"""IndieAuth client and server apps and sign-in helper."""

import json

import web
from web import tx
from web.agent import unapply_dns


server = web.application("IndieAuthServer", mount_prefix="auth")
client = web.application("IndieAuthClient", mount_prefix="user")


def insert_references(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(auths="""received DATETIME NOT NULL DEFAULT
                              CURRENT_TIMESTAMP,
                          mention_id TEXT, data JSON,
                          source_url TEXT, target_url TEXT""")
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
    """."""


@server.route(r"")
class AuthenticationEndpoint:
    """An IndieAuth server's `authentication endpoint`."""

    template = web.template("""$def with (name, identifier, scope, path)
                               $var title: Sign in to $name?

                               <form method=post action=/$path>
                               <p>Sign in to $name at $identifier?</p>
                               $if scope:
                                   <p>Scope: $scope</p>
                               <button>Sign In</button>
                               <button>Block & Report</button>
                               </form>""")

    def _get(self):
        form = web.form("me", "client_id", "redirect_uri", "state", scope=None)
        client_url = web.uri(form.client_id)
        # TODO use cache[url].app instead of raw mf.parse
        mfs = web.mf.parse(url=client_url)
        for item in mfs["items"]:
            if "h-app" in item["type"]:
                name = item["properties"]["name"][0]
                break
        else:
            name = "Unknown"
        identifier = web.uri(unapply_dns(client_url)).minimized
        # XXX tx.user.session["client_id"] = form.client_id
        tx.user.session["redirect_uri"] = form.redirect_uri
        tx.user.session["state"] = form.state
        return self.template(name, identifier, form.scope, tx.request.uri.path)

    def _post(self):
        try:
            web.form("code", "client_id", "redirect_uri", "code_verifier")
        except web.BadRequest:
            pass
        else:
            # TODO https://indieauth.spec.indieweb.org/#profile-url-response
            web.header("Content-Type", "application/json")
            return json.dumps({"me": f"https://{tx.request.uri.host}"})
        callback = web.uri(tx.user.session["redirect_uri"])
        # XXX callback["client_id"] = form["client_id"]
        # XXX callback["redirect_uri"] = form["redirect_uri"]

        # NOTE put this back!
        # TODO XXX callback["state"] = tx.user.session["state"]

        code = web.nbrandom(10)
        callback["code"] = code
        # TODO use sql
        # XXX tx.kv["codes"][tx.user.session["client_id"]] = code
        raise web.Found(callback)


@server.route(r"token")
class TokenEndpoint:
    """An IndieAuth server's `token endpoint`."""

    def _post(self):
        form = web.form("me", "code", "grant_type",
                        "client_id", "redirect_uri")
        if form.code != tx.kv["codes"][form.client_id]:
            return "nope"
        token = web.nbrandom(10)
        web.header("Content-Type", "application/json")
        return json.dumps({"access_token": token, "scope": "draft",
                           "me": "https://{}".format(tx.host.name)})


# Client


@client.route(r"sign-in")
class SignIn:
    """An IndieAuth client's `sign-in form`."""

    template = web.template("""$def with (host)
                               $var title: Sign in to $host

                               <form>
                               <input name=me>
                               <button>Sign In</button>
                               </form>""")

    def _get(self):
        try:
            user_url = web.form("me").me
        except web.BadRequest:
            return self.template(tx.host.name)
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
    """An IndieAuth client's authorization."""

    def _get(self):
        # form = web.form("state", "code")
        # verify state
        # request token from token_endpoint using `code`
        tx.user.session["me"] = "http://alice.example"
        # TODO return_to="/"
        raise web.SeeOther("/")


@client.route(r"sign-out")
class SignOut:
    """An IndieAuth client's authorization."""

    def _post(self):
        tx.user.session = None
        raise web.SeeOther("/")


def sign_in(user_url):
    """Initiate an IndieAuth sign-in (eg. micropub client)."""
