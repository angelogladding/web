"""Micropub server app and editor helper."""

import pathlib

import sh
import web
from web import tx


server = web.application("MicropubServer", mount_prefix="pub")
templates = web.templates(__name__)


def insert_references(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(resources="""url TEXT, modified DATETIME, types TEXT,
                              properties JSON""",
                 files="""fid TEXT, sha256 TEXT, size INTEGER""",
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


def discover_post_type(properties):
    """Return the discovered post type."""
    if "bookmark-of" in properties:
        post_type = "bookmark"
    else:
        post_type = "note"
    return post_type


def send_request(payload):
    """Send a Micropub request to a Micropub server."""
    # TODO FIXME what's in the session?
    response = web.post(tx.user.session["micropub_endpoint"], json=payload)
    return response.location, response.links


class LocalClient:
    """A localized interface to the endpoint's backend."""

    def read(self, url):
        """Return a resource with its metadata."""
        url = f"https://{tx.host.name}/{url}".rstrip("/")
        return tx.db.select("resources", where="url = ?", vals=[url])[0]

    def read_all(self, limit=20):
        """Return a list of all resources."""
        return tx.db.select("resources", order="url ASC")

    def recent_entries(self, limit=20):
        """Return a list of recent entries."""
        return tx.db.select("""resources""",
                            where="types == 'h-entry'",
                            order="""json_extract(resources.properties,
                                     '$.published') DESC""")

    def create(self, types, properties):
        """Write a resource and return its permalink."""
        now = web.utcnow()
        url = f"https://{tx.host.name}"
        if types == "h-card":
            if properties["uid"] == str(web.uri(tx.host.name)):
                pass
        elif types == "h-entry":
            post_type = discover_post_type(properties)
            timeslug = web.timeslug(now)
            if post_type == "note":
                textslug = properties["content"]
            elif post_type == "bookmark":
                textslug = properties["bookmark-of"][0]["properties"]["name"]
            url += f"/{timeslug}/{web.textslug(textslug)}"
            author = {"type": ["h-card"],
                      "properties": self.read("")["properties"]}
            properties.update(published=now, url=url, author=author)
        tx.db.insert("resources", url=url, modified=now, types=types,
                     properties=properties)
        return url


@server.route(r"")
class MicropubEndpoint:
    """."""

    def _get(self):
        try:
            form = web.form("q")
        except web.BadRequest:
            clients = tx.db.select("auths", what="DISTINCT client_id")
            local_client = LocalClient()
            resources = local_client.read_all()
            files = local_client.get_files()
            return templates.activity(clients, resources, files)
        syndication_endpoints = []
        if form.q == "config":
            web.header("Content-Type", "application/json")
            return {"q": ["category", "contact", "source", "syndicate-to"],
                    "media-endpoint": f"https://{tx.host.name}/pub/media",
                    "syndicate-to": syndication_endpoints}
        return "unsupported `q` command"

    def _post(self):
        resource = tx.request.body._data
        permalink = LocalClient().create(" ".join(resource["type"]),
                                         resource["properties"])
        web.header("Link", f'</blat>; rel="shortlink"', add=True)
        web.header("Link", f'<https://twitter.com/angelogladding/status/'
                           f'30493490238590234>; rel="syndication"', add=True)
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
        return list(pathlib.Path(tx.host.name).iterdir())

    def _post(self):
        media_dir = pathlib.Path(tx.host.name)
        media_dir.mkdir(exist_ok=True, parents=True)
        while True:
            fid = web.nbrandom(4)
            filename = media_dir / fid
            if not filename.exists():
                web.form("file").file.save(filename)
                break
        sha256 = str(sh.sha256sum(filename)).split()[0]
        tx.db.insert("files", fid=fid, sha256=sha256,
                     size=filename.stat().st_size)
        raise web.Created("file created", location=f"/pub/media/{fid}")


@server.route(r"media/{fid}")
class MediaFile:
    """."""

    def _get(self):
        return f"config NGINX for an X-Redirect to {self.fid}"
