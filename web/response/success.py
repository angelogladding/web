"""

"""

from .util import Status

__all__ = ["Success", "OK", "Created", "Accepted",
           "NonAuthoritativeInformation", "NoContent",
           "ResetContent", "PartialContent", "MultiStatus"]


class Success(Status):

    """2xx -- the action was successfully received, understood, & accepted"""


class OK(Success):

    """
    200

    """

    def __init__(self, body):
        super(Success, self).__init__(body)


class Created(Success):

    """
    201

    """

    def __init__(self, body, location):
        self.location = location
        super(Created, self).__init__(body)


class Accepted(Success):

    """
    202

    """


class NonAuthoritativeInformation(Success):

    """
    203

    """


class NoContent(Success):

    """
    204

    """


class ResetContent(Success):

    """
    205

    """


class PartialContent(Success):

    """
    206

    """


class MultiStatus(Success):

    """
    207

    """
