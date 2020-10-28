# web
tools for metamodern web development

## Bootstrap a host

1) Create a new Debian 10 machine (at your host)
2) Run `ssh -tt root@IP.ADDRESS.OF.MACHINE "wget https://raw.githubusercontent.com/angelogladding/web/main/host.py -qO host.py && python3 host.py"` in your terminal and copy the resulting token
3) Navigate to `http://IP.ADDRESS.OF.MACHINE:5555` in your browser and paste the token

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
