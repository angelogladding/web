# web
tools for metamodern web development

    import web

## A web browser

    browser = web.browser()
    browser.go("en.wikipedia.org/wiki/Pasta")
    browser.shot("wikipedia-pasta.png")

## A web cache

    cache = web.cache()
    cache["indieweb.org/note"].entry["summary"]
    cache["indieweb.org/note"].entry["summary"]  # served from caceh

## A simple application

In `hello.py`:

    import web

    app = web.application("HelloWorld")

    @app.route(r"")
    class HelloWorld:
        def _get(self):
            return "Hello World!"

In `setup.py`:

    ...
    setup(requires=["web"],
          entry_points={"web.apps": ["hello:app"]},
          ...)
