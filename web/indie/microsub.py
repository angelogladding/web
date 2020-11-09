"""Microsub client and server apps."""

import web


client = web.application("MicrosubClient", mount_prefix="reader")
server = web.application("MicrosubServer", mount_prefix="microsub")


@server.route(r"")
class Reader:
    """."""

    def _get(self):
        return "reader.."


@server.route(r"")
class MicrosubServer:
    """."""

    def _get(self):
        return "microsub server.."
