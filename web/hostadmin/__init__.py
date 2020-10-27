"""Host administration app."""

import mm
import pathlib
import sh

from ..framework import application, get_apps, form, SeeOther


hostapp = application("HostAdmin")
views = mm.templates(__name__)


@hostapp.route(r"")
class Main:
    """Host admin interface."""

    def _get(self):
        hostname = sh.hostname("--fqdn")
        ip = sh.hostname("-I").split()[0]
        uptime = sh.uptime()
        configs = []
        for config in pathlib.Path("/etc/supervisor/conf.d").glob("*.conf"):
            with config.open() as fp:
                configs.append((config.name, fp.read()))
        status = sh.sudo("supervisorctl", "status")
        apps = get_apps()
        return views.main(hostname, ip, uptime, status, configs, apps)


@hostapp.route(r"apps")
class Apps:
    """Installed web applications."""

    def _post(self):
        app = form("app").app
        owner, _, name = app.partition("/")
        sh.sh("runinenv", "system/env", "pip", "install", "-e",
              f"git+https://github.com/{owner}/{name}.git#egg={name}")
        sh.sudo("supervisorctl", "restart", "hostadmin")
        raise SeeOther("/")
