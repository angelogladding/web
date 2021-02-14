# web
tools for metamodern web development

    >>> import web

## Browser

uses Firefox via Selenium

    >>> browser = web.browser()
    >>> browser.go("en.wikipedia.org/wiki/Pasta")
    >>> browser.shot("wikipedia-pasta.png")

## Cache

uses SQLite

    >>> cache = web.cache()
    >>> cache["indieweb.org/note"].entry["summary"]
    "A note is a post that is typically short unstructured* plain text, written & posted quickly, that has its own permalink page."
    >>> cache["indieweb.org/note"].entry["summary"]  # served from cache
    "A note is a post that is typically short unstructured* plain text, written & posted quickly, that has its own permalink page."

## Application

WSGI-compatible

In `hello.py`:

    import web

    app = web.application("HelloWorld")

    @app.route(r"")
    class HelloWorld:
        def _get(self):
            return "Hello World!"

In `setup.py`:

    ...
    setup(install_requires=["web"],
          entry_points={"web.apps": ["hello:app"]},
          ...)

## Templating

Full Python inside string templates.

    >>> web.template("$def with (name)\n$name")("Alice")
    "Alice"

## Markdown

Strict syntax subset (there should be one and only one way).

Picoformat support eg. @person, @@org, #tag, %license

    >>> str(web.mkdn("*lorem* ipsum."))
    "<p><em>lorem</em> ipsum. </p>"

## URL parsing

Defaults to safe-mode and raises DangerousURL eagerly. Up-to-date public suffix and HSTS support.

    >>> url = web.uri("example.cnpy.gdn/foo/bar?id=38")
    >>> url.host
    "example.cnpy.gdn"
    >>> url.suffix
    "cnpy.gdn"
    >>> url.is_hsts()
    True

## IndieWeb

Supported: IndieAuth client/server, Micropub client/server, Microsub :construction:, WebSub :construction:, Webmention :construction:

    >>> app.mount(web.indieauth.server)
    >>> app.mount(web.micropub.server)

### Microformats

Parse `mf2` from HTML. Analyze vocabularies for stability/interoperability.
