# [`web`][1] Copyright 2020- @[Angelo Gladding][2]
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
# [1]: //angelogladding.com/code/web
# [2]: //angelogladding.com
# [3]: //gnu.org
# [4]: //gnu.org/licenses/agpl
# [5]: //fsf.org

"""Install tools for a metamodern web environment."""

from setuptools import setup

setup(requires=["acme_tiny", "BeautifulSoup4", "cssselect", "gevent",
                "html5lib", "httpagentparser", "lxml", "mf2py", "mf2util",
                "mm", "pendulum", "pycrypto", "python_mimeparse",
                "pyvirtualdisplay", "PySocks", "regex", "requests",
                "selenium", "stem", "unidecode", "uri", "uwsgi", "watchdog"],
      provides={"pygments.styles": ["Lunar = solarized:Lunar",
                                    "Solar = solarized:Solar"],
                "term.apps": ["mf = mf.__main__:main",
                              "mkdn = mkdn.__main__:main",
                              "mm = mm.__main__:main",
                              "web = web.__main__:main"]},
      discover=__file__)
