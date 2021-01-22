"""Microsub client and server apps."""

import web
from web import tx


server = web.application("MicrosubServer", mount_prefix="sub")
reader = web.application("MicrosubReader", mount_prefix="reader")


def wrap_server(handler, app):
    """Ensure server links are in head of root document."""
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


@server.route(r"")
class MicrosubServer:
    """."""

    def _get(self):
        return "microsub server.."


@reader.route(r"")
class Reader:
    """."""

    def _get(self):
        return "reader.."
