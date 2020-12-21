"""
Tools for a metamodern web environment.

## User agent tools

Simple interface, simple automate.

## Web application framework

Simple interface, simple deploy.

"""

# TODO clean these up
from hstspreload import in_hsts_preload
import mf
from mkdn import render as mkdn
import mm
from mm import Template as template  # noqa
from mm import templates  # noqa
import pendulum  # TODO XXX
from requests.exceptions import ConnectionError
from uri import parse as uri

from . import agent
from .agent import *  # noqa
from . import framework
from .framework import *  # noqa
from .indie import *  # noqa
from .response import (Status,  # noqa
                       OK, Created, Accepted, NoContent, MultiStatus,
                       Found, SeeOther, PermanentRedirect,
                       BadRequest, Unauthorized, Forbidden, NotFound,
                         MethodNotAllowed, Conflict, Gone)
from .tasks import run_queue

__all__ = ["in_hsts_preload", "mf", "mkdn", "mm", "template", "templates",
           "pendulum", "indieauth", "micropub", "microsub", "webmention",
           "websub", "run_queue", "uri", "Created", "ConnectionError"]
__all__ += agent.__all__ + framework.__all__
