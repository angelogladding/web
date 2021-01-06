"""IndieAuth client and server apps and sign-in helper."""

import json

import web
from web import tx


server = web.application("IndieAuthServer", mount_prefix="auth")
client = web.application("IndieAuthClient", mount_prefix="user")
templates = web.templates(__name__)


def insert_references(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(auths="""initiated DATETIME NOT NULL DEFAULT
                              CURRENT_TIMESTAMP,
                          code TEXT, client_id TEXT, redirect_uri TEXT,
                          code_challenge TEXT, code_challenge_method TEXT,
                          scope TEXT""")
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
            author = {"name": "TODO", "url": "https://todo.example"}
    return client, author


def handle_auth_response(handler=None):
    """
    Handle the second leg of authorization.

    This takes place before returning profile URL or access token.

    """
    form = web.form("grant_type", "code", "client_id",
                    "redirect_uri", "code_verifier")
    if form["grant_type"] != "authorization_code":
        raise web.Forbidden("this endpoint only supports the "
                            "`grant_type=authorization_code`.")
    if form.code != tx.db.select("auths"):  # TODO FIXME
        raise web.Forbidden("`code` mismatch")
    scope = []  # TODO FIXME
    payload = {"me": f"https://{tx.request.uri.host}"}
    if "profile" in scope:
        profile = {"name": "TODO NAME"}
        if "email" in scope:
            profile["email"] = "TODO EMAIL"
        payload["profile"] = profile
    if handler:
        payload.update(**handler())
    web.header("Content-Type", "application/json")
    raise web.OK(json.dumps(payload))


@server.route(r"")
class AuthorizationEndpoint:
    """IndieAuth server `authorization endpoint`."""

    def _get(self):
        form = web.form("response_type", "client_id", "redirect_uri", "state",
                        "code_challenge", "code_challenge_method", scope="")
        client, developer = get_client(form.client_id)
        tx.user.session["redirect_uri"] = form.redirect_uri
        tx.user.session["state"] = form.state
        tx.user.session["code_challenge"] = form.code_challenge
        tx.db.insert("auths", client_id=form.client_id,
                     redirect_uri=form.redirect_uri,
                     code_challenge=form.code_challenge,
                     code_challenge_method=form.code_challenge_method)
        supported_scopes = ["create", "draft", "update", "delete",
                            "media", "profile", "email"]
        scopes = [s for s in form.scope.split() if s in supported_scopes]
        return templates.signin(client, developer, scopes)

    def _post(self):
        try:
            handle_auth_response()
        except web.BadRequest:
            pass
        form = web.form("action", scopes=[])
        redirect_uri = web.uri(tx.user.session["redirect_uri"])
        if form.action == "cancel":
            raise web.Found(redirect_uri)
        code = web.nbrandom(32)
        tx.db.update("auths", code=code, where="code_challenge = ?",
                     vals=[tx.user.session["code_challenge"]])
        redirect_uri["code"] = code
        redirect_uri["state"] = tx.user.session["state"]
        raise web.Found(redirect_uri)


@server.route(r"token")
class TokenEndpoint:
    """IndieAuth server `token endpoint`."""

    def _post(self):
        def handle_access_token_flow():
            """Access Token response payload."""
            token = web.nbrandom(16)
            scopes = " ".join([])
            return {"access_token": token, "token_type": "Bearer",
                    "scope": scopes}
        handle_auth_response(handle_access_token_flow)


@client.route(r"sign-in")
class SignIn:
    """IndieAuth client sign in."""

    def _get(self):
        try:
            user_url = web.form("me").me
        except web.BadRequest:
            return templates.identify(tx.host.name)
        # if not user_url.startswith("https://"):
        #     user_url = "https://" + user_url
        try:
            rels = web.get(user_url).mf2json["rels"]
        except web.ConnectionError:
            return f"can't reach https://{user_url}"
        auth_endpoint = web.uri(rels["authorization_endpoint"][0])
        token_endpoint = web.uri(rels["token_endpoint"][0])
        micropub_endpoint = web.uri(rels["micropub_endpoint"][0])
        tx.user.session["auth_endpoint"] = str(auth_endpoint)
        tx.user.session["token_endpoint"] = str(token_endpoint)
        tx.user.session["micropub_endpoint"] = str(micropub_endpoint)
        client_id = web.uri(f"http://{tx.host.name}:{tx.host.port}")
        auth_endpoint["me"] = user_url
        auth_endpoint["client_id"] = client_id
        # TODO don't hardcode the following
        auth_endpoint["redirect_uri"] = client_id / "user/sign-in/auth"
        auth_endpoint["response_type"] = "code"
        auth_endpoint["state"] = web.nbrandom(10)
        auth_endpoint["scope"] = "draft"
        raise web.SeeOther(auth_endpoint)


@client.route(r"sign-in/auth")
class Authorize:
    """IndieAuth client authorization."""

    def _get(self):
        # form = web.form("state", "code")
        # verify state
        # request token from token_endpoint using `code`
        tx.user.session["me"] = "http://alice.example"
        # TODO return_to="/"
        raise web.SeeOther("/")


@client.route(r"sign-out")
class SignOut:
    """IndieAuth client sign out."""

    def _post(self):
        tx.user.session = None
        raise web.SeeOther("/")


def sign_in(user_url):
    """Initiate an IndieAuth sign-in (eg. micropub client)."""
