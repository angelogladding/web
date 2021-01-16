"""Micropub server app and editor helper."""

import web
from web import tx


server = web.application("MicropubServer", mount_prefix="pub")
templates = web.templates(__name__)


def insert_references(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(resources="""resource JSON,
                              published TEXT AS (json_extract(resource,
                                  '$.published')) STORED,
                              url TEXT AS (json_extract(resource,
                                  '$.url')) STORED""",
                 syndication="""destination JSON NOT NULL""")
    tx.pub = LocalClient()
    yield
    if tx.request.uri.path == "":
        doc = web.parse(tx.response.body)
        try:
            head = doc.select("head")[0]
        except IndexError:
            pass
        else:
            head.append("<link rel=micropub href=/pub>")
            tx.response.body = doc.html
        web.header("Link", f'</pub>; rel="micropub"', add=True)


def send_request(payload):
    """Send a Micropub request to a Micropub server."""
    # TODO FIXME what's in the session?
    response = web.post(tx.user.session["micropub_endpoint"], json=payload)
    return response.location, response.links


class LocalClient:
    """A localized interface to the endpoint's backend."""

    def read(self, url):
        """Return a resource with its metadata."""
        return tx.db.select("resources", where="url = ?", vals=["/" + url],
                            order="published DESC", limit=1)[0]["resource"]

    def read_all(self, limit=20):
        """Return a list of all resources."""
        return tx.db.select("""resources, json_tree(resources.resource,
                                                    '$.name')""",
                            where="json_tree.type == 'text'",
                            order="published desc")

    def create(self, url, resource):
        """Write a resource and return its permalink."""
        now = web.utcnow()
        url = "/" + url.format(dtslug=web.timeslug(now),
                               nameslug=web.textslug(resource.get("name", "")))
        try:
            author = self.read("about")
        except IndexError:  # TODO bootstrap first post with first post
            author = dict(resource)
        author.pop("type")
        tx.db.insert("resources", resource=dict(**resource, published=now,
                                                url=url, author=author))
        # TODO tx.db.snapshot()
        return url


@server.route(r"")
class MicropubEndpoint:
    """."""

    def _get(self):
        try:
            form = web.form("q")
        except web.BadRequest:
            clients = tx.db.select("auths", what="DISTINCT client_id")
            posts = LocalClient().read_all()
            return templates.activity(clients, posts)
        syndication_endpoints = []
        if form.q == "config":
            return {"q": ["category", "contact", "source", "syndicate-to"],
                    "media-endpoint": "/pub/media",
                    "syndicate-to": syndication_endpoints}
        return "unsupported `q` command"

    def _post(self):
        print(tx.request.body)
        permalink = "/foobar"
        web.header("Link", f'</blat>; rel="shortlink"', add=True)
        web.header("Link", f'<https://twitter.com/angelogladding/status/'
                           f'30493490238590234>; rel="syndication"',
                   add=True)
        raise web.Created("post created", location=permalink)


@server.route(r"syndication")
class Syndication:
    """."""

    def _get(self):
        return templates.syndication()

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
