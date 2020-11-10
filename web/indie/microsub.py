"""Microsub client and server apps."""

import web


reader = web.application("MicrosubReader", mount_prefix="reader")
server = web.application("MicrosubServer", mount_prefix="microsub")


@reader.route(r"")
class Reader:
    """."""

    def _get(self):
        return "reader.."


@server.route(r"")
class MicrosubServer:
    """."""

    def _get(self):
        return "microsub server.."
