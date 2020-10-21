import term

import web

__all__ = ["main"]


main = term.application("web", web.__doc__)


@main.register()
class Serve:

    def setup(self, add_arg):
        add_arg("app", help="name of web application")

    def run(self, stdin, log):
        __import__(self.app + ".__web__")
        web.serve(self.app)
        return 0
