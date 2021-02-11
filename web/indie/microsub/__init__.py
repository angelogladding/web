"""Microsub client and server apps."""

import web
from web import tx


server = web.application("MicrosubServer", mount_prefix="sub")
templates = web.templates(__name__)


def wrap_server(handler, app):
    """Ensure server links are in head of root document."""
    tx.db.define(following="""url TEXT, added DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP""")
    tx.sub = LocalClient()
    yield
    if tx.request.uri.path == "":
        doc = web.parse(tx.response.body)
        try:
            head = doc.select("head")[0]
        except IndexError:
            pass
        else:
            head.append("<link rel=microsub href=/sub>")
            tx.response.body = doc.html
        web.header("Link", f'</sub>; rel="microsub"', add=True)


class LocalClient:
    """."""

    def get_following(self):
        return {"items": [{"type": "feed", "url": f["url"]}
                          for f in tx.db.select("following")]}

    def follow(self, url):
        tx.db.insert("following", url=url)


@server.route(r"")
class MicrosubServer:
    """."""

    def _get(self):
        try:
            form = web.form("action", channel="default")
        except web.BadRequest:
            following = tx.sub.get_following()["items"]
            return templates.activity(following)
        if form.action == "follow":
            response = tx.sub.get_following()
        web.header("Content-Type", "application/json")
        return response

    def _post(self):
        form = web.form("action", "url", channel="default")
        if form.action == "follow":
            tx.sub.follow(form.url)
            response = tx.sub.get_following()
        web.header("Content-Type", "application/json")
        return response
