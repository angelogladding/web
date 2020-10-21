import term

import mm


main = term.application("mm", __doc__)


@main.register()
class Main:

    def setup(self, parser):
        add = parser.add_argument
        add("args", nargs="*", help="argument(s) passed to template")
        add("-w", "--wrap", nargs="+", dest="wrappers", type=open,
            help="wrap in given template(s)")

    def run(self, args, stdin):
        document = mm.Template(stdin)(*args.args)
        for wrapper in args.wrappers:
            document = mm.Template(wrapper)(document)
        print(document)
        return 0
