"""Micropub server app and editor helper."""

import pathlib

import sh
import web
from web import tx


server = web.application("MicropubServer", mount_prefix="pub",
                         filename=rf"{web.nb60_re}{{4}}.\w{{1,10}}")
templates = web.templates(__name__)


def wrap_server(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(resources="""resource JSON, url TEXT, modified DATETIME""",
                 files="""fid TEXT, sha256 TEXT UNIQUE, size INTEGER""",
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
    elif "like-of" in properties:
        post_type = "like"
    elif "follow-of" in properties:
        post_type = "follow"
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
        return tx.db.select("resources", order="modified DESC")

    def recent_entries(self, limit=20):
        """Return a list of recent entries."""
        return tx.db.select("""resources""", order="modified DESC",
                            where="""json_extract(resources.resource,
                                                  '$.type[0]') == 'h-entry'""")

    def create(self, *types, visibility="public", **properties):
        """Write a resource and return its permalink."""
        now = web.utcnow()
        url = f"https://{tx.host.name}"
        if "h-card" in types:
            if properties["uid"] == str(web.uri(tx.host.name)):
                pass
        elif "h-entry" in types:
            post_type = discover_post_type(properties)
            timeslug = web.timeslug(now)
            if post_type == "note":
                textslug = properties["content"]
            elif post_type == "bookmark":
                textslug = properties["bookmark-of"][0]["properties"]["name"]
            elif post_type == "like":
                textslug = properties["like-of"][0]["properties"]["name"]
            elif post_type == "follow":
                props = properties["follow-of"][0]["properties"]
                tx.sub.follow(props["url"])
                textslug = props["name"]
            url += f"/{timeslug}/{web.textslug(textslug)}"
            author = {"type": ["h-card"],
                      "properties": self.read("")["resource"]["properties"]}
            properties.update(published=now, url=url, author=author)
        tx.db.insert("resources", url=url, modified=now,
                     resource={"type": types, "visibility": visibility,
                               "properties": properties})
        # TODO send_webmentions() using tx.cache[]
        return url

    def search(self, query):
        return tx.db.select("resources", vals=[query, query],
                            where="""json_extract(resources.resource,
                                     '$.properties.bookmark-of[0].properties.url') == ? OR
                                     json_extract(resources.resource,
                                     '$.properties.like-of[0].properties.url') == ?""")

    def get_files(self):
        """Return list of media files."""
        try:
            files = list(pathlib.Path(tx.host.name).iterdir())
        except FileNotFoundError:
            files = []
        return files

    def get_file(self, filename):
        """Return a media file."""
        return pathlib.Path(tx.host.name) / filename


@server.route(r"")
class MicropubEndpoint:
    """."""

    def _get(self):
        try:
            form = web.form("q")
        except web.BadRequest:
            local_client = LocalClient()
            resources = local_client.read_all()
            files = local_client.get_files()
            return templates.activity(resources, files)
        syndication_endpoints = []
        if form.q == "config":
            response = {"q": ["category", "contact", "source", "syndicate-to"],
                        "media-endpoint": f"https://{tx.host.name}/pub/media",
                        "syndicate-to": syndication_endpoints,
                        "visibility": ["public", "unlisted", "private"]}
        elif form.q == "source":
            response = {}
            if "search" in form:
                response = {"items": [{"url": [r["resource"]["properties"]["url"]]} for r in
                                      LocalClient().search(form.search)]}
        else:
            raise web.BadRequest("unsupported query. check `q=config` for support.")
        web.header("Content-Type", "application/json")
        return response

    def _post(self):
        resource = tx.request.body._data
        permalink = LocalClient().create(*resource["type"], visibility=resource["visibility"],
                                         **resource["properties"])
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
        return templates.media(LocalClient().get_files())

    def _post(self):
        media_dir = pathlib.Path(tx.host.name)
        media_dir.mkdir(exist_ok=True, parents=True)
        while True:
            fid = web.nbrandom(4)
            filename = media_dir / fid
            if not filename.exists():
                filename = web.form("file").file.save(filename)
                break
        sha256 = str(sh.sha256sum(filename)).split()[0]
        try:
            tx.db.insert("files", fid=fid, sha256=sha256,
                         size=filename.stat().st_size)
        except tx.db.IntegrityError:
            fid = tx.db.select("files", where="sha256 = ?",
                               vals=[sha256])[0]["fid"]
            filename.unlink()
        path = f"/pub/media/{fid}"
        raise web.Created(f"File can be found at <a href={path}>{path}</a>",
                          location=path)


@server.route(r"media/{filename}")
class MediaFile:
    """."""

    def _get(self):
        content_types = {(".jpg", ".jpeg"): "image/jpg",
                         ".png": "image/png",
                         ".mp3": "audio/mpeg",
                         ".mp4": "video/mp4"}
        for suffix, content_type in content_types.items():
            if self.filename.endswith(suffix):
                web.header("Content-Type", content_type)
                break
        web.header("X-Accel-Redirect", f"/X/{tx.host.name}/{self.filename}")

    def _delete(self):
        filepath = LocalClient().get_file(self.filename)
        tx.db.delete("files", where="fid = ?", vals=[filepath.stem])
        filepath.unlink()
        return "deleted"
