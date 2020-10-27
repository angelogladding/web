"""Host administration app."""

import mm
import pathlib
import sh

from ..framework import application, get_apps, form


hostapp = application("HostAdmin")
views = mm.templates(__name__)


@hostapp.route(r"")
class Main:
    """Host admin interface."""

    def _get(self):
        configs = []
        for config in pathlib.Path("/etc/supervisor/conf.d").glob("*.conf"):
            with config.open() as fp:
                configs.append((config.name, fp.read()))
        status = sh.sudo("supervisorctl", "status")
        apps = get_apps()
        return views.main(configs, status, apps)


@hostapp.route(r"apps")
class Apps:
    """Installed web applications."""

    def _post(self):
        app = form("app").app
        sh.pip("install", "-e", f"git+https://github.com/{app}.git")
        return "done"
