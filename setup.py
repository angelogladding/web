# [`web`][1] Copyright @[Angelo Gladding][2] 2020-
#
# This program is free software: it is distributed in the hope that it
# will be useful, but *without any warranty*; without even the implied
# warranty of merchantability or fitness for a particular purpose. You
# can redistribute it and/or modify it under the terms of the @@[GNU's
# Not Unix][3] %[Affero General Public License][4] as published by the
# @@[Free Software Foundation][5], either version 3 of the License, or
# any later version.
#
# *[GNU]: GNU's Not Unix
#
# [1]: https://github.com/angelogladding/web
# [2]: https://angelogladding.com
# [3]: https://gnu.org
# [4]: https://gnu.org/licenses/agpl
# [5]: https://fsf.org

"""Tools for metamodern web development."""

from setuptools import setup

setup(requires=["acme_tiny", "BeautifulSoup4", "cssselect", "dnspython",
                "gevent", "html5lib", "httpagentparser", "lxml", "mf2py",
                "mf2util", "networkx", "pendulum", "pillow", "pycrypto",
                "pyparsing", "pyscreenshot", "PySocks", "python_mimeparse",
                "pyvirtualdisplay", "regex", "requests", "selenium", "stem",
                "unidecode", "uwsgi", "watchdog"],
      provides={"pygments.styles": ["Lunar = solarized:Lunar",
                                    "Solar = solarized:Solar"],
                "term.apps": ["mf = mf.__main__:main",
                              "mkdn = mkdn.__main__:main",
                              "mm = mm.__main__:main",
                              "web = web.__main__:main"],
                "web.apps": ["indieauth-client = web.indie.indieauth:client",
                             "indieauth-server = web.indie.indieauth:server",
                             "micropub-server = web.indie.micropub:server",
                             "microsub-reader = web.indie.microsub:reader",
                             "microsub-server = web.indie.microsub:server",
                             "webmention = web.indie.webmention:receiver",
                             "websub-pub = web.indie.websub:pub",
                             "websub-sub = web.indie.websub:sub"]},
      discover=__file__)
