"""."""

import datetime
import json
import re
import sh
import time

import lxml.html
import mf
import networkx as nx
import pyscreenshot
import pyvirtualdisplay
import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import solarized
import sql
import uri

__all__ = ["get", "post", "parse", "browser", "cache", "discover_link"]

displays = []
browsers = []

tor_proxies = {"http": "socks5h://localhost:9050",
               "https": "socks5h://localhost:9050"}


def discover_link(target, name):
    # TODO head = request("HEAD", target)
    # TODO if head.status_code == 200:
    # TODO     try:
    # TODO         endpoint = get_header_link(head.headers, name)[0]
    # TODO     except IndexError:
    # TODO         pass
    # TODO     else:
    # TODO         if endpoint:
    # TODO             return endpoint
    response = get(target)
    try:
        endpoint = get_header_link(response.headers, name)[0]
    except IndexError:
        rels = mf.parse(response.text, url=target)["rels"]
        try:
            endpoint = rels.get(name, [])[0]
        except IndexError:
            endpoint = None
    return endpoint


def get_header_link(headers: dict, search_rel: str):
    """

    """
    try:
        header = headers["Link"]
    except KeyError:
        return []
    links = []
    for link in header.split(","):
        resource, _, rel = link.partition(";")
        match = re.match("""rel=['"](.+)['"]""", rel.strip())
        if match and match.groups()[0] == search_rel:
            links.append(resource.strip(" <>"))
    return links


def download(url, filepath, chunk_size=1024):
    """

    """
    response = request("GET", url, stream=True)
    with filepath.open("wb") as fp:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                fp.write(chunk)
    return response


def request(method, url, **kwargs):
    """
    return the response to dereferencing given `url` using given `method`

    Attempts to use HTTPS when accessing non-onion domains. Proxies
    through Tor when accessing onion services. Optionally pass typical
    `requests.Request` arguments as `kwargs`.

    """
    url = uri.parse(url)
    preferred = "https"
    if url.suffix == "onion":
        kwargs["proxies"] = tor_proxies
        preferred = "http"
    try:
        response = requests.request(method, f"{preferred}://{url.minimized}",
                                    **kwargs)
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        if url.suffix != "onion":
            try:
                response = requests.request(method, f"http://{url.minimized}",
                                            **kwargs)
            except (requests.exceptions.SSLError,
                    requests.exceptions.ConnectionError):
                raise RequestFailed()
    return response


class RequestFailed(Exception):

    """"""


def get(url, **kwargs):
    """Get from the web."""
    return Transaction(url, **kwargs)


def post(url, **kwargs):
    """Post to the web."""
    return Transaction(url, "post", **kwargs)


class Cache:

    def __init__(self, domain=None, db=None):
        self.cache = {}
        if domain:
            self.domain = domain
        if db:
            self.db = sql.db(db)
            self.db.define(resources="""url TEXT UNIQUE, html TEXT,
                                        data JSON""")

    def format_url(self, url):
        try:
            url = f"{self.domain}/{url}"
        except AttributeError:
            url = url
        return url

    def add(self, *resource_urls):
        for resource_url in resource_urls:
            url = self.format_url(resource_url)
            resource = get(url)
            self.cache[resource_url] = resource
            try:
                self.db.insert("resources", url=url, html=resource.text,
                               data=resource.mf2json.data)
            except AttributeError:
                pass

    def __getitem__(self, resource_url):
        try:
            resource = self.cache[resource_url]
        except KeyError:
            try:
                url = self.format_url(resource_url)
                resource_data = self.db.select("resources", where="url = ?",
                                               vals=[url])[0]
                resource = Transaction(url, fetch=False)
                resource.text = resource_data["html"]
            except (AttributeError, IndexError):
                self.add(resource_url)
                resource = self.cache[resource_url]
        return resource

    @property
    def graph(self):
        network = nx.DiGraph()
        for url, resource in self.cache.items():
            # print(resource.links)
            network.add_node(url)
        return nx.draw(network, with_labels=True)


cache = Cache


class Transaction:
    """."""

    def __init__(self, url, method="get", fetch=True, **kwargs):
        self.url = str(uri.parse(str(url)))
        if fetch:
            handler = getattr(requests, method)
            self.response = handler(apply_dns(self.url), **kwargs)
            print()
            print(self.response)
            print(dir(self.response))
            print(self.response.headers)
            print()
            self.text = self.response.text
            self.headers = self.response.headers

    @property
    def location(self):
        print(self.headers)
        return self.response.url

    @property
    def links(self):
        return self.headers["Link"]

    @property
    def dom(self):
        return parse(self.text)

    @property
    def mf2json(self):
        return Semantics(mf.parse(self.text, self.url))

    @property
    def links(self):
        return []

    @property
    def card(self):
        return Semantics(mf.representative_hcard(self.mf2json.data,
                                                 source_url=self.url))

    @property
    def entry(self):
        return Semantics(mf.interpret_entry(self.mf2json.data,
                                            source_url=self.url))

    @property
    def event(self):
        return Semantics(mf.interpret_event(self.mf2json.data,
                                            source_url=self.url))

    @property
    def jf2(self):
        return Semantics(mf.interpret_feed(self.mf2json.data,
                                           source_url=self.url))

    def mention(self, *target_urls):
        return Semantics(mf.interpret_comment(self.mf2json.data,
                                              self.url, target_urls))


class Semantics:

    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    def __repr__(self):
        return JSONEncoder(indent=2).encode(self.data)  # , indent=2)
        # XXX return json.dumps(self.data, indent=2)

    def _repr_html_(self):
        return solarized.highlight(JSONEncoder(indent=2).encode(self.data), ".json")
        # XXX return solarized.highlight(json.dumps(self.data, indent=2),
        # ".json")


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, uri.URI):
            return str(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def parse(html):
    """Return a document object for given html."""
    return Document(html)


def apply_dns(url):
    if url.startswith("/"):
        return url
    url = uri.parse(url)
    if url.host == "alice.example":
        url = str(url).replace("http://alice.example",
                               "http://127.0.0.1:8080")
    elif url.host == "bob.example":
        url = str(url).replace("http://bob.example",
                               "http://127.0.0.1:8081")
    elif url.host == "hello.example":
        url = str(url).replace("http://hello.example",
                               "http://127.0.0.1:8082")
    else:
        url = str(url)
    return url


def unapply_dns(url):
    url = uri.parse(url)
    if url.host == "127.0.0.1":
        if url.port == 8080:
            url = str(url).replace("http://127.0.0.1:8080",
                                   "http://alice.example")
        elif url.port == 8081:
            url = str(url).replace("http://127.0.0.1:8081",
                                   "http://bob.example")
        elif url.port == 8082:
            url = str(url).replace("http://127.0.0.1:8082",
                                   "http://hello.example")
    else:
        url = str(url)
    return url


class Document:

    # TODO with html as dom: -- manipulate dom -- on exit html is modified

    def __init__(self, html):
        self.doc = lxml.html.fromstring(str(html))

    def select(self, selector):
        els = []
        for el in self.doc.cssselect(selector):
            els.append(Element(el))
        return els

    @property
    def children(self):
        return self.doc.getchildren()

    @property
    def html(self):
        return lxml.html.tostring(self.doc).decode()


class Element:

    def __init__(self, element):
        self.element = element

    def append(self, *html):
        for _html in html:
            self.element.append(_make_element(_html))

    def replace(self, html):
        self.element.getparent().replace(self.element, _make_element(html))

    @property
    def text(self):
        return self.element.text_content()


def _make_element(html):
    el = lxml.html.fromstring(f"<DOUGIE>{html}</DOUGIE>")
    return el.cssselect("DOUGIE")[0].getchildren()[0]


class Browser:
    """Firefox via Selenium."""

    By = By
    EC = expected_conditions

    def __init__(self, name=None, width=1024, height=768):
        if not len(displays):
            display = pyvirtualdisplay.Display(visible=False, size=(2048, 768))
            display.start()
            displays.append(display)
        profile = webdriver.FirefoxProfile()
        profile.add_extension(extension="/home/gaea/canopy/var/identities/"
                                        "6c189616-4fe1-4f3f-84dc-c4a13ee9b155/"
                                        "asteria/asteria-dev.xpi")
        binary = "/home/gaea/firefox/firefox-bin"
        self.browser = webdriver.Firefox(firefox_profile=profile,
                                         firefox_binary=binary)
        count = len(browsers)
        browsers.append(self)
        self._top = 0
        self._left = count * 1024
        self._width = width
        self._height = height
        self._update_window()
        self.name = name
        self.shot_id = 0

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._update_window()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self._update_window()

    def _update_window(self):
        self.browser.set_window_rect(self._left, self._top,
                                     self._width, self._height)

    def go(self, *args, wait=0):
        if len(args) == 1:
            url = args[0]
        elif len(args) == 2:
            url = "/".join(args)
        url = apply_dns(url)
        self.browser.get(url)
        if wait:
            time.sleep(wait)
        return self
        # XXX self.browser.get(str(uri.parse(url)))

    def wait(self, *conditions, duration=20):
        for condition in conditions:
            time.sleep(.1)
            wait = WebDriverWait(self.browser, duration)
            wait.until(condition)

    def wait_until_url_contains(self, url):
        self.wait(self.EC.url_contains(apply_dns(url)))

    def select(self, selector):
        return self.browser.find_elements_by_css_selector(selector)

    def select_first(self, selector):
        return self.browser.find_element_by_css_selector(selector)

    def action(self):
        return ActionChains(self.browser)

    def shot(self, path):
        # TODO take in pieces & stitch together -- using way too much memory
        # self._height = self.browser.execute_script("return document.body."
        #                                            "scrollHeight;") + 100
        # self._update_window()
        self.browser.get_screenshot_as_file(str(path) + ".png")

    # XXX def shot_url(self):
    # XXX     base64 = self.browser.get_screenshot_as_base64()
    # XXX     return f"data:image/png;BASE64,{base64}"

    def twitter_login(self, handle, passphrase):
        self.go("https://twitter.com/login")
        time.sleep(2)
        username = self.select_first("input[type=text]")
        username.send_keys(handle)
        password = self.select_first("input[type=password]")
        password.send_keys(passphrase)
        password.submit()
        time.sleep(3)

    def twitter_syndicate_post(self, post, post_url, in_reply_to=None):
        """syndicate a post to Twitter and return the syndication url"""
        if in_reply_to:
            start_url = in_reply_to
            button = "Reply"
            y_offset = 320
            article_index = 1
        else:
            start_url = "https://twitter.com/home"
            button = "Tweet"
            y_offset = 220
            article_index = 0
        self.go(start_url)
        time.sleep(2)
        self.select_first(f"*[aria-label={button}]").click()
        time.sleep(2)
        padding = browsers.index(self) * 1024
        sh.xdotool("mousemove", padding + 330, y_offset, "click", 1,
                   "type", post + f" \u2014 {post_url}")
        self.select_first("*[data-testid=tweetButton]").click()
        time.sleep(2)
        js = f"""return document.querySelectorAll("article")[{article_index}]
                 .querySelectorAll("div[data-testid=tweet] a")[2].href"""
        return self.execute_script(js)

    def twitter_backfeed_post(self, syndication_url):
        self.go(syndication_url)
        time.sleep(2)
        urls = []
        for article in self.select("article"):
            links = []
            for a in article.find_elements_by_css_selector("a"):
                suffixes = ("/retweets", "/retweets/with_comments", "/likes")
                if a.get_property("target") == "_blank" or \
                   a.text.startswith("@") or \
                   a.get_property("href").endswith(suffixes):
                    continue
                links.append(a)
            url = links[{3: 2, 4: 2, 5: 3}[len(links)]].get_property("href")
            urls.append(url)
        post = {"url": syndication_url}
        if urls[0] == syndication_url:  # a note
            article_index = 0
            child_index = 0
            post["comment"] = urls[1:]
        elif urls[1] == syndication_url:  # a reply
            post["in-reply-to"] = urls[0]
            post["comment"] = urls[2:]
            article_index = 1
            child_index = 1
        js = f"""return document.querySelectorAll("article")[{article_index}]
                 .querySelector("div[data-testid=tweet] + div")
                 .childNodes[{child_index}].childNodes[0].childNodes[0]
                 .innerHTML"""
        doc = Document(self.execute_script(js)).doc
        children = doc.getchildren()
        if children:
            parts = []
            for child in children:
                grandchildren = child.getchildren()
                if child.tag == "a":
                    url = child.attrib["title"]
                    part = f'<a href="{url}">{url}</a>'
                elif grandchildren:
                    grandchild_text = grandchildren[0].text_content()
                    if grandchild_text.startswith("@"):  # @-mention
                        part = (f'<a class=h-card href="https://twitter.com/'
                                f'{grandchild_text}">{grandchild_text}</a>')
                    else:  # emoji
                        part = grandchildren[0].attrib["aria-label"]
                else:
                    part = child.text_content().replace("\n", "<br>")
                parts.append(part)
            content = "".join(parts)
        else:
            content = doc.text_content()
        post["content"] = content
        return post

    def shot_url(self):
        # XXX grab = pyscreenshot.grab(bbox=(0, 0, 920, 920)).tobytes()
        # XXX base64png = b"".join(base64.encodebytes(grab).splitlines())
        self.shot_id += 1
        filename = f"{self.name}-{self.shot_id}.png"
        placement = browsers.index(self)
        coords = (1024 * placement, 0,
                  1024 * (placement + 1), 768)
        # import sh
        # sh.Command("import")("-screen", "-window", "root", filename)
        # time.sleep(2)
        # sh.Command("import")("-window", "root", filename)
        # sh.convert(sh.xwd("-root", "-screen"), "xwd:-", f"png:{filename}")
        pyscreenshot.grab(bbox=coords).save(filename)
        return f"/IndieWeb/{filename}"

    def quit(self):
        try:
            self.browser.quit()
        except selenium.common.exceptions.WebDriverException:
            pass
        if displays:
            try:
                displays[0].stop()
            except KeyError:  # raising during multi-user testing
                pass

    def __getattr__(self, attr):
        return getattr(self.browser, attr)

    def _repr_html_(self):
        return f"<img class=screen src={self.shot_url()}>"
        # url = unapply_dns(self.current_url)
        # site_character = url.partition("//")[2].partition(".")[0]
        # TODO FIXME remove hard-coded IndieWeb..
        # return (f"<div class=screenshot>"
        #         f"<div class=browser><small>{self.name}'s "
        #         f"Browser</small></div>"
        #         f"<div class=tab><img src=/IndieWeb/{site_character}16.png>"
        #         f" {self.title}</div>"
        #         f"<div class=address><small><code>{url}</code></small></div>"
        #         f"<img class=screen src={self.shot_url()}></div>")


browser = Browser


# def shot(name, description):  # XXX , *browsers):
#     test_case = inspect.stack()[1].function
#     global shot_counter
#     shot_id = "{:03}".format(shot_counter)
#     dashed_name = name.replace(" ", "-")
#     for user, browser in sorted(browsers.items()):
#         shot_filename = "{}-{}-{}.png".format(shot_id, user, dashed_name)
#         height = browser.execute_script("return document.body.scrollHeight;")
#         browser.set_window_size(browser_width, height + 100)
#         browser.get_screenshot_as_file(str(build_dir / "features" /
#                                            shot_filename))
#     features.append((test_case, shot_id, dashed_name, name, description))
#     # XXX , shot_filename, [user for u in browsers.keys()]))
#     shot_counter += 1
