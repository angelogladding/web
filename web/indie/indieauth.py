"""IndieAuth client and server apps and sign-in helper."""

import json

import web
from web.agent import unapply_dns


server = web.application("IndieAuthServer", mount_prefix="auth")
client = web.application("IndieAuthClient", mount_prefix="sign-in")


# @server.wrap  # TODO include subapp wrappers
def insert_references(handler, app):
    """Ensure server links are in head of root document."""
    web.tx.db.define(auths="""received DATETIME NOT NULL DEFAULT
                                CURRENT_TIMESTAMP,
                              mention_id TEXT, data JSON,
                              source_url TEXT, target_url TEXT""")
    yield
    if web.tx.request.uri.path == "":
        doc = web.parse(web.tx.response.body)
        try:
            head = doc.select("head")[0]
        except IndexError:
            pass
        else:
            head.append("<link rel=authorization_endpoint href=/auth>",
                        "<link rel=token_endpoint href=/auth/token>")
            web.tx.response.body = doc.html


def get_client(client_id):
    """."""


@server.route(r"")
class AuthenticationEndpoint:
    """An IndieAuth server's `authentication endpoint`."""

    template = web.template("""$def with (name, identifier, scope)
                               $var title: Sign in to $name?

                               <form method=post>
                               <p>Sign in to $name at $identifier with
                               $scope scope?</p>
                               <button>Sign In</button>
                               <button>Block</button>
                               </form>""")

    def _get(self):
        form = web.form("me", "client_id", "redirect_uri", "state", scope=None)
        client_url = web.uri.parse(form.client_id)
        # TODO use cache[url].app instead of raw mf.parse
        mfs = web.mf.parse(url=client_url)
        for item in mfs["items"]:
            if "h-app" in item["type"]:
                name = item["properties"]["name"][0]
                break
        else:
            name = "Unknown"
        identifier = web.uri.parse(unapply_dns(client_url)).minimized
        # XXX web.tx.user.session["client_id"] = form.client_id
        web.tx.user.session["redirect_uri"] = form.redirect_uri
        web.tx.user.session["state"] = form.state
        return self.template(name, identifier, form.scope)

    def _post(self):
        callback = web.uri.parse(web.tx.user.session["redirect_uri"])
        # XXX callback["client_id"] = web.tx.user.session["client_id"]
        # XXX callback["redirect_uri"] = web.tx.user.session["redirect_uri"]
        callback["state"] = web.tx.user.session["state"]
        code = web.nbrandom(10)
        callback["code"] = code
        # TODO use sql
        # XXX web.tx.kv["codes"][web.tx.user.session["client_id"]] = code
        raise web.Found(callback)


@server.route(r"token")
class TokenEndpoint:
    """An IndieAuth server's `token endpoint`."""

    def _post(self):
        form = web.form("me", "code", "grant_type",
                        "client_id", "redirect_uri")
        if form.code != web.tx.kv["codes"][form.client_id]:
            return "nope"
        token = web.nbrandom(10)
        web.header("Content-Type", "application/json")
        return json.dumps({"access_token": token, "scope": "draft",
                           "me": "https://{}".format(web.tx.host.name)})


# Client


@client.route(r"")
class SignIn:
    """An IndieAuth client's `sign-in form`."""

    template = web.template("""$def with (host)
                               <!doctype html>
                               <title>Sign in to $host</title>
                               <body>
                               <form>
                               <input name=me>
                               <button>Sign In</button>
                               </form>""")

    def _get(self):
        try:
            user_url = web.form("me").me
        except web.BadRequest:
            return self.template(web.tx.host.name)
        try:
            rels = web.get(user_url).mf2json["rels"]
        except web.ConnectionError:
            return f"can't reach https://{user_url}"
        auth = web.uri.parse(rels["authorization_endpoint"][0])
        web.tx.user.session["auth_endpoint"] = str(auth)
        client_id = web.uri.parse(f"http://{web.tx.host.name}"
                                  f":{web.tx.host.port}")
        auth["me"] = user_url
        auth["client_id"] = client_id
        auth["redirect_uri"] = client_id / "sign-in/auth"
        auth["response_type"] = "code"
        auth["state"] = web.nbrandom(10)
        auth["scope"] = "draft"
        raise web.SeeOther(auth)


@client.route(r"auth")
class Authorize:
    """An IndieAuth client's authorization."""

    def _get(self):
        # form = web.form("state", "code")
        # verify state
        # request token from token_endpoint using `code`
        web.tx.user.session["me"] = "http://alice.example"
        # TODO return_to="/"
        raise web.SeeOther("/")


def sign_in(user_url):
    """Initiate an IndieAuth sign-in (eg. micropub client)."""
