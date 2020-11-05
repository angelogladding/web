# web
tools for metamodern web development

## A simple application

In `hello.py`:

    import web

    app = web.application("HelloWorld")

    @app.route(r"")
    class HelloWorld:
        def _get(self):
            return "Hello World!"

In `setup.py` (requires [`angelogladding/src`](https://github.com/angelogladding/src)):

    ...
    setup(requires=["web"],
          provides={"web.apps": ["hello:app"]},
          discover=__file__)
