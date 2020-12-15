"""Micropub server app and editor helper."""

import json
import requests

import web
from web import tx


server = web.application("Micropub", mount_prefix="micropub")


def insert_references(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(syndication="""destination JSON NOT NULL""")
    yield
    if tx.request.uri.path == "":
        doc = web.parse(tx.response.body)
        try:
            head = doc.select("head")[0]
        except IndexError:
            print("COULDN'T INSERT MICROPUB ENDPOINT")
        else:
            head.append("<link rel=micropub_endpoint href=/micropub>")
            tx.response.body = doc.html
        web.header("Link", f'</micropub>; rel="micropub_endpoint"', add=True)


def send_request(payload):
    """Send a Micropub request to a Micropub server."""
    print(json.dumps(payload))
    response = requests.post(tx.user.session["micropub_endpoint"],
                             json=json.dumps(payload))
    print()
    print(response)
    print(dir(response))
    print(response)
    print()
    return response.location, response.links


@server.route(r"")
class MicropubEndpoint:
    """."""

    def _get(self):
        print(tx.request)
        form = web.form("q")
        syndication_endpoints = []
        if form.q == "config":
            return {"q": ["category", "contact", "source", "syndicate-to"],
                    "media-endpoint": "/micropub/media",
                    "syndicate-to": syndication_endpoints}

    def _post(self):
        print("GOT TO THE ENDPOINT POST!")
        permalink = "/foobar"
        web.header("Link", f'</blat>; rel="shortlink"', add=True)
        web.header("Link", f'<https://twitter.com/angelogladding/status/'
                           f'30493490238590234>; rel="syndication"',
                   add=True)
        raise web.Created(permalink)


@server.route(r"syndication")
class Syndication:
    """."""

    def _get(self):
        return """<form method=post>
                  Twitter<br>
                  <input name=twitter_username placeholder=username><br>
                  <input name=twitter_password placeholder=password><br>
                  GitHub<br>
                  <input name=github_username placeholder=username><br>
                  <input name=github_token placeholder=token><br>
                  <button>Save</button>
                  </form>"""

    def _post(self):
        destinations = web.form()
        if "twitter_username" in destinations:
            un = destinations.twitter_username
            # TODO pw = destinations.twitter_password
            # TODO sign in
            user_photo = ""  # TODO doc.qS(f"a[href=/{un}/photo] img").src
            destination = {"uid": f"//twitter.com/{un}",
                           "name": f"{un} on Twitter",
                           "service": {"name": "Twitter",
                                       "url": "//twitter.com",
                                       "photo": "//abs.twimg.com/favicons/"
                                                "twitter.ico"},
                           "user": {"name": un, "url": f"//twitter.com/{un}",
                                    "photo": user_photo}}
            tx.db.insert("syndication", destination=destination)
        if "github_username" in destinations:
            un = destinations.github_username
            # TODO token = destinations.github_token
            # TODO check the token
            user_photo = ""  # TODO doc.qS("img.avatar-user.width-full").src
            destination = {"uid": f"//github.com/{un}",
                           "name": f"{un} on GitHub",
                           "service": {"name": "GitHub",
                                       "url": "//github.com",
                                       "photo": "//github.githubassets.com/"
                                                "favicons/favicon.png"},
                           "user": {"name": un, "url": f"//github.com/{un}",
                                    "photo": user_photo}}
            tx.db.insert("syndication", destination=destination)


@server.route(r"media")
class MediaEndpoint:
    """."""

    def _get(self):
        return "media endpoint.."
