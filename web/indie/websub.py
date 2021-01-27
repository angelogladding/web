"""WebSub hub and subscriber apps."""

import web
from web import tx


hub = web.application("WebSubHub", mount_prefix="hub")
subs = web.application("WebSubSubs", mount_prefix="subs")


def wrap_hub(handler, app):
    """Ensure server links are in head of root document."""
    yield
    if tx.request.uri.path == "":
        doc = web.parse(tx.response.body)
        try:
            head = doc.select("head")[0]
        except IndexError:
            pass
        else:
            head.append("<link rel=self href=/>")
            head.append("<link rel=hub href=/hub>")
            tx.response.body = doc.html
        web.header("Link", f'</>; rel="self"', add=True)
        web.header("Link", f'</hub>; rel="hub"', add=True)


@hub.route(r"")
class Hub:
    """."""

    def _get(self):
        return "hub.."


@subs.route(r"")
class Subscriptions:
    """."""

    def _get(self):
        return "subscriptions.."
