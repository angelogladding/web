"""Host administration app."""

import mm
import sh

from .framework import application


hostapp = application("HostAdmin")
views = mm.templates(__name__)


@hostapp.route(r"")
class Main:
    """Host admin interface."""

    def _get(self):
        with open("/home/webhost/system/etc/supervisor-hostadmin.conf") as fp:
            config = fp.read()
        status = sh.sudo("supervisorctl", "status")
        return views.main(config, status)
