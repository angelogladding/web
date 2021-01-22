"""WebSub hub and subscriber apps."""

import web
from web import tx


pub = web.application("WebSubPublisher", mount_prefix="hub")
sub = web.application("WebSubSubscriber", mount_prefix="subscriptions")


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


@pub.route(r"")
class Hub:
    """."""

    def _get(self):
        return "hub.."


@sub.route(r"")
class Subscriptions:
    """."""

    def _get(self):
        return "subscriptions.."
