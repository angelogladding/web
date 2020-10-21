"""Micropub server app and editor helper."""

import web


server = web.application("Micropub", mount_prefix="micropub")


def send_request():
    """Send a Micropub request to a Micropub server."""


@server.route(r"")
class MicropubEndpoint:
    """."""

    def _get(self):
        form = web.form("q")
        if form.q == "config":
            return {"media-endpoint": "/micropub/media",
                    "q": ["category", "contact", "source", "syndicate-to"]}
        # url = store_post()
        # return url


@server.route(r"media")
class MediaEndpoint:
    """."""

    def _get(self):
        return "media endpoint.."
