"""
Tools for a metamodern web environment.

## User agent tools

Simple interface, simple automate.

## Web application framework

Simple interface, simple deploy.

"""

# TODO clean these up
import mf
import mm
from mm import Template as template  # noqa
import pendulum  # TODO XXX

from . import agent
from .agent import *  # noqa
from . import framework
from .framework import *  # noqa
# XXX from .framework.indieweb import indieauth
# XXX from .framework.indieweb import micropub
# XXX from .framework.indieweb import webmention
# XXX from .framework.indieweb import websub
from .response import (Status,  # noqa
                       OK, Created, Accepted, NoContent, MultiStatus,
                       Found, SeeOther, PermanentRedirect,
                       BadRequest, Unauthorized, Forbidden, NotFound,
                         MethodNotAllowed, Conflict, Gone)
from .tasks import run_queue

__all__ = ["mf", "mm", "template", "pendulum", "indieauth", "micropub",
           "webmention", "websub", "run_queue", "hostapp", "Created"]
__all__ += agent.__all__ + framework.__all__
