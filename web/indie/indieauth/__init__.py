"""IndieAuth client and server apps and sign-in helper."""

import base64
import hashlib

import web
from web import tx


server = web.application("IndieAuthServer", mount_prefix="auth",
                         client_id=r"[\w/]+")
client = web.application("IndieAuthClient", mount_prefix="user")
templates = web.templates(__name__)


def wrap_server(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(auths="""initiated DATETIME NOT NULL DEFAULT
                              CURRENT_TIMESTAMP, revoked DATETIME,
                          code TEXT, client_id TEXT, redirect_uri TEXT,
                          code_challenge TEXT, code_challenge_method TEXT,
                          response JSON""")
    yield
    if tx.request.uri.path == "":
        doc = web.parse(tx.response.body)
        try:
            head = doc.select("head")[0]
        except IndexError:
            pass
        else:
            head.append("<link rel=authorization_endpoint href=/auth>",
                        "<link rel=token_endpoint href=/auth/token>")
            tx.response.body = doc.html
        web.header("Link", f'</auth>; rel="authorization_endpoint"', add=True)
        web.header("Link", f'</auth/token>; rel="token_endpoint"', add=True)


def wrap_client(handler, app):
    """Ensure client database contains user table."""
    tx.db.define(users="""account_created DATETIME NOT NULL DEFAULT
                              CURRENT_TIMESTAMP, url TEXT, name TEXT,
                          email TEXT, access_token TEXT""")
    yield


def get_client(client_id):
    """Return the client name and author if provided."""
    # FIXME unapply_dns was here..
    client = {"name": None, "url": web.uri(client_id).normalized}
    author = None
    if client["url"].startswith("https://addons.mozilla.org"):
        try:
            heading = web.get(client_id).dom.select("h1.AddonTitle")[0]
        except IndexError:
            pass
        else:
            client["name"] = heading.text.partition(" by ")[0]
            author_link = heading.select("a")[0]
            author_id = author_link.href.rstrip('/').rpartition('/')[2]
            author = {"name": author_link.text,
                      "url": f"https://addons.mozilla.org/user/{author_id}"}
    else:
        mfs = web.mf.parse(url=client["url"])
        for item in mfs["items"]:
            if "h-app" in item["type"]:
                client = {"name": item["properties"]["name"][0],
                          "url": "https://todo.example"}
                break
            author = {"name": "NAME", "url": "URL"}  # TODO
    return client, author


@server.route(r"")
class AuthorizationEndpoint:
    """IndieAuth server `authorization endpoint`."""

    def _get(self):
        try:
            form = web.form("response_type", "client_id", "redirect_uri",
                            "state", "code_challenge", "code_challenge_method",
                            scope="")
        except web.BadRequest:
            active = tx.db.select("auths", where="revoked is null")
            revoked = tx.db.select("auths", where="revoked not null")
            return templates.authorizations(active, revoked)
        client, developer = get_client(form.client_id)
        tx.user.session["client_id"] = form.client_id
        tx.user.session["redirect_uri"] = form.redirect_uri
        tx.user.session["state"] = form.state
        tx.user.session["code_challenge"] = form.code_challenge
        tx.user.session["code_challenge_method"] = form.code_challenge_method
        supported_scopes = ["create", "draft", "update", "delete",
                            "media", "profile", "email"]
        scopes = [s for s in form.scope.split() if s in supported_scopes]
        return templates.signin(client, developer, scopes)

    def _post(self):
        form = web.form("action", scopes=[])
        redirect_uri = web.uri(tx.user.session["redirect_uri"])
        if form.action == "cancel":
            raise web.Found(redirect_uri)
        code = web.nbrandom(32)
        s = tx.user.session
        decoded_code_challenge = base64.b64decode(s["code_challenge"]).decode()
        tx.db.insert("auths", code=code, code_challenge=decoded_code_challenge,
                     client_id=s["client_id"], redirect_uri=s["redirect_uri"],
                     code_challenge_method=s["code_challenge_method"],
                     response={"scope": " ".join(form.scopes)})
        redirect_uri["code"] = code
        redirect_uri["state"] = tx.user.session["state"]
        raise web.Found(redirect_uri)


@server.route(r"token")
class TokenEndpoint:
    """IndieAuth server `token endpoint`."""

    def _post(self):
        try:
            form = web.form("action", "token")
            if form.action == "revoke":
                tx.db.update("auths", revoked=web.utcnow(), vals=[form.token],
                             where="""json_extract(response,
                                                   '$.access_token') = ?""")
                raise web.OK("")
        except web.BadRequest:
            pass
        form = web.form("grant_type", "code", "client_id",
                        "redirect_uri", "code_verifier")
        if form.grant_type != "authorization_code":
            raise web.Forbidden("only grant_type=authorization_code supported")
        auth = tx.db.select("auths", where="code = ?", vals=[form.code])[0]
        computed_code_challenge = \
            hashlib.sha256(form.code_verifier.encode("ascii")).hexdigest()
        if auth["code_challenge"] != computed_code_challenge:
            raise web.Forbidden("code mismatch")
        response = auth["response"]
        scope = response["scope"].split()
        if "profile" in scope:
            profile = {"name": "NAME"}  # TODO
            if "email" in scope:
                profile["email"] = "EMAIL"  # TODO
            response["profile"] = profile
        if scope and self.is_token_request(scope):
            response.update(access_token=web.nbrandom(12),
                            token_type="Bearer")
        response["me"] = f"https://{tx.request.uri.host}"
        tx.db.update("auths", response=response,
                     where="code = ?", vals=[auth["code"]])
        web.header("Content-Type", "application/json")
        return response

    def is_token_request(self, scope):
        """Determine whether the list of scopes dictates a token reuqest."""
        return bool(len([s for s in scope if s not in ("profile", "email")]))


@server.route(r"clients")
class Clients:
    """IndieAuth server authorized clients."""

    def _get(self):
        clients = tx.db.select("auths", what="DISTINCT client_id")
        return templates.clients(clients)


@server.route(r"clients/{client_id}")
class Client:
    """IndieAuth server authorized client."""

    def _get(self):
        client = tx.db.select("auths", where="client_id = ?",
                              vals=[self.client_id])
        return templates.client(client)


@client.route(r"sign-in")
class SignIn:
    """IndieAuth client sign in."""

    def _get(self):
        try:
            form = web.form("me", return_to="/")
        except web.BadRequest:
            return templates.identify(tx.host.name)
        try:
            rels = web.get(form.me).mf2json["rels"]
        except web.ConnectionError:
            return f"can't reach https://{form.me}"
        auth_endpoint = web.uri(rels["authorization_endpoint"][0])
        token_endpoint = web.uri(rels["token_endpoint"][0])
        micropub_endpoint = web.uri(rels["micropub"][0])
        tx.user.session["auth_endpoint"] = str(auth_endpoint)
        tx.user.session["token_endpoint"] = str(token_endpoint)
        tx.user.session["micropub_endpoint"] = str(micropub_endpoint)
        client_id = web.uri(f"http://{tx.host.name}:{tx.host.port}")
        auth_endpoint["me"] = form.me
        auth_endpoint["client_id"] = tx.user.session["client_id"] = client_id
        auth_endpoint["redirect_uri"] = tx.user.session["redirect_uri"] = \
            client_id / "user/sign-in/auth"
        auth_endpoint["response_type"] = "code"
        auth_endpoint["state"] = tx.user.session["state"] = web.nbrandom(16)
        code_verifier = tx.user.session["code_verifier"] = web.nbrandom(64)
        code_challenge = \
            hashlib.sha256(code_verifier.encode("ascii")).hexdigest()
        auth_endpoint["code_challenge"] = \
            base64.b64encode(code_challenge.encode("ascii"))
        auth_endpoint["code_challenge_method"] = "S256"
        auth_endpoint["scope"] = "create draft update delete profile email"
        tx.user.session["return_to"] = form.return_to
        raise web.SeeOther(auth_endpoint)


@client.route(r"sign-in/auth")
class Authorize:
    """IndieAuth client authorization."""

    def _get(self):
        form = web.form("state", "code")
        if form.state != tx.user.session["state"]:
            raise web.BadRequest("bad state")
        payload = {"grant_type": "authorization_code",
                   "code": form.code,
                   "client_id": tx.user.session["client_id"],
                   "redirect_uri": tx.user.session["redirect_uri"],
                   "code_verifier": tx.user.session["code_verifier"]}
        response = web.post(tx.user.session["token_endpoint"],
                            headers={"Accept": "application/json"},
                            data=payload).json
        profile = response.get("profile", {})
        tx.db.insert("users", url=response["me"], name=profile.get("name"),
                     email=profile.get("email"),
                     access_token=response["access_token"])
        tx.user.session["me"] = response["me"]
        raise web.SeeOther(tx.user.session["return_to"])


@client.route(r"sign-out")
class SignOut:
    """IndieAuth client sign out."""

    def _post(self):
        tx.user.session = None
        raise web.SeeOther("/")


def sign_in(user_url):
    """Initiate an IndieAuth sign-in (eg. micropub client)."""
