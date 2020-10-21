"""

"""

import uri


def test_netloc():
    """"""
    cases = {"example.org": "http://example.org/",
             "example.org./": "http://example.org/",
             "example.org:80/foo": "http://example.org/foo",
             "example.org:080/foo": "http://example.org/foo",
             "example.org:8000/foo": "http://example.org:8000/foo",
             "example.org./foo/bar.html": "http://example.org/foo/bar.html",
             "example.org.:81/foo": "http://example.org:81/foo",
             "USER:@example.org": "http://USER@example.org/",
             "USER:pass@Example.ORG/": "http://USER:pass@example.org/"}
    for orig, expected in cases.items():
        normalized = uri.parse(orig).normalized
        assert expected == normalized
        # "{} normalized to {} not {}".format(orig, normalized, expected)


{
    # path
    "/%7ebar": "/~bar",
    "/%7Ebar": "/~bar",
    "/foo/bar/.": "/foo/bar/",
    "/foo/bar/./": "/foo/bar/",
    "/foo/bar/..": "/foo/",
    "/foo/bar/../": "/foo/",
    "/foo/bar/../baz": "/foo/baz",
    "/foo/bar/../..": "/",
    "/foo/bar/../../": "/",
    "/foo/bar/../../baz": "/baz",
    "/foo/bar/../../../baz": "/baz",
    "/foo/bar/../../../../baz": "/baz",
    "/./foo": "/foo",
    "/../foo": "/foo",
    "/foo.": "/foo.",
    "/.foo": "/.foo",
    "/foo..": "/foo..",
    "/..foo": "/..foo",
    "/./../foo": "/foo",
    "/./foo/.": "/foo/",
    "/foo/./bar": "/foo/bar",
    "/foo/../bar": "/bar",
    "/foo//": "/foo/",
    "/foo///bar//": "/foo/bar/",

    # query
    "/?q=%5c": "/?q=%5C",
    "/?q=%5C": "/?q=%5C",
    # "/?foo=bar": "/?foo=bar",
    # "/?q=%C7": "/?q=%EF%BF%BD",
    # "/?q=C%CC%A7": "/?q=C%CC%A7",
    # "/?q=%C3%87": "/?q=%C3%87",
    # "/?q=%E2%85%A0": "/?q=%E2%85%A0",

    # fragment
    "/#": "/",

    # miscellaneous
    "/#!foo": "/?_escaped_fragment_=foo",
    "пример.испытание/Служебная:foo/bar": "http://xn--e1afmkfd.xn--80akhbykn"
    "j4f/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:foo/bar"
}
