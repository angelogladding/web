"""

"""

try:
    import regex as re
except ImportError:
    import re  # noqa


class Status(Exception):

    """

    """

    def __init__(self, body):
        super(Status, self).__init__(body)
        self.body = body

    @property
    def code(self):
        return self.__doc__.split()[0]

    @property
    def reason(self):
        return re.sub("([A-Z])", r" \1", self.__class__.__name__).lstrip()

    def __str__(self):
        return "{} {}".format(self.code, self.reason)
