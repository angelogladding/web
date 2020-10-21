"""WebSub hub and subscriber apps."""

import web


hub = web.application("WebSubHub", mount_prefix="hub")
subscriptions = web.application("WebSubSubscriptions",
                                mount_prefix="subscriptions")


@hub.route(r"")
class Hub:
    """."""

    def _get(self):
        return "hub.."


@subscriptions.route(r"")
class Subscriptions:
    """."""

    def _get(self):
        return "subscriptions.."
