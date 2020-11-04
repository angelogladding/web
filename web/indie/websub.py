"""WebSub hub and subscriber apps."""

import web


pub = web.application("WebSubPublisher", mount_prefix="hub")
sub = web.application("WebSubSubscriber", mount_prefix="subscriptions")


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
