"""

"""

from collections import namedtuple
from inspect import cleandoc

from nose.tools import raises

from web.templates import Template


def test_definitions():
    _("1", {}, "1")
    _("$def with ()\n1", {}, "1")
    _("$def with ()\n1", {}, "1")
    _("$def with (a)\n$a", {}, "1", "1")
    _("$def with (a=0)\n$a", {}, "0")
    _("$def with (a=0)\n$a", {}, "1", 1)
    _("$def with (a=0)\n$a", {}, "1", a=1)


def test_complicated_expressions():
    _("$def with (x)\n$x.upper()", {}, "HELLO", "hello")
    _("$(2 * 3 + 4 * 5)", {}, "26")
    _("${2 * 3 + 4 * 5}", {}, "26")
    _("$def with (limit)\nkeep $(limit)ing.", {}, "keep going.", "go")
    _("$def with (a)\n$a.b[0]", {}, "1", namedtuple("_", "b")(b=[1]))


def test_looping():
    _("$if 1: 1", {}, "1")
    _("$if 1:\n    1", {}, "1")
    _("$if 1:\n    1\\", {}, "1")
    _("$if 0: 0\n$elif 1: 1", {}, "1")
    _("$if 0: 0\n$elif None: 0\n$else: 1", {}, "1")
    _("$if 0 < 1 and 1 < 2: 1", {}, "1")
    _("$for x in [1, 2, 3]: $x", {}, "1\n2\n3")
    _("$def with (d)\n$for k, v in d.items(): $k", {}, "1", {1: 1})
    _("$for x in [1, 2, 3]:\n    $x", {}, "1\n2\n3")
    _("$def with (a)\n$while a and a.pop(): 1", {}, "1\n1\n1", [1, 2, 3])


def test_loop_details():
    _("$for i in range(5):\n    $loop.index, $loop.parity", {},
      "1, odd\n2, even\n3, odd\n4, even\n5, odd")
    _("$for i in range(2):\n    $for j in range(2): "
      "$loop.parent.parity, $loop.parity", {},
      "odd, odd\nodd, even\neven, odd\neven, even")


def test_space_after_colon():
    _("$if True: foo", {}, "foo")


def test_assignment():
    _("$ a = 1\n$a", {}, "1")
    _("$ a = [1]\n$a[0]", {}, "1")
    _("$ a = {1: 1}\n$list(a.keys())[0]", {}, "1")
    _("$ a = []\n$if not a: 1", {}, "1")
    _("$ a = {}\n$if not a: 1", {}, "1")
    _("$ a = -1\n$a", {}, "-1")
    _("$ a = '1'\n$a", {}, "1")


def test_comments():
    _("$# 0", {}, "")
    _("hello$# comment1\nhello$# comment2", {}, "hello\nhello")
    _("$# comment0\nhi$# comment1\nhi$#comment2", {}, "\nhi\nhi")


def test_unicode():
    _("$def with (a)\n$a", {}, "\u203d", "\u203d")
    _("$def with (a)\n$a $:a", {}, "\u203d \u203d", "\u203d")
    _("$def with ()\nfoo", {}, "foo")
    _("$def with (f)\n$:f('x')", {}, "x", lambda x: x)


def test_dollar_escaping():
    _("$$money", {}, "$money")


def test_space_sensitivity():
    _("$def with (x)\n$x", {}, "1", 1)
    _("$def with(x ,y)\n$x", {}, "1", 1, 1)
    _("$(1 + 2 * 3 + 4)", {}, "11")


@raises(NameError)
def test_global_not_defined():
    Template("$x")()


@raises(UnboundLocalError)
def test_global_override():
    Template("$ x = x + 1\n$x", globals={"x": 1})()


def test_globals():
    _("$x", {"x": 1}, "1")
    _("$ x = 2\n$x", {"x": 1}, "2")


def test_builtins():
    _("$min(1, 2)", {}, "1")


@raises(NameError)
def test_override_builtins():
    Template("$min(1, 2)", builtins={})()


def test_vars():
    tests = {"$var x: 1": "1",
             "$var x = 1": 1}
             # TODO "$var x:\n    foo\n    bar": "foo\nbar"
    for template, expected in tests.items():
        actual = Template(template)()["x"]
        assert actual == expected, "\n\n".join((template, expected, actual))


def test_bom_chars():
    _("\xef\xbb\xbf$def with(x)\n$x", {}, "foo", "foo")


def test_weird_for():
    _("$for i in range(10)[1:5]:\n    $i", {}, "1\n2\n3\n4")
    _("$for k, v in {'a': 1, 'b': 2}.items():\n    $k $v", {}, "a 1\nb 2")


@raises(SyntaxError)
def test_invalid_syntax():
    Template("$for k, v in ({'a': 1, 'b': 2}.items():\n    $k $v")()


def _(template, globals, expected, *args, **kwargs):
    actual = str(Template(template, globals=globals)(*args, **kwargs)).rstrip()
    msg = cleandoc("""actual output does not match expected..

                      TEMPLATE:

                      {}

                      GLOBALS, ARGS, KWARGS:

                      {}
                      {}
                      {}

                      EXPECTED:

                      {}

                      ACTUAL:

                      {}""")
    assert actual == expected, msg.format(template, globals, args, kwargs,
                                          expected, actual)
