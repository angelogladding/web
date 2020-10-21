"""
interpret

"""

import zlib  # TODO more useful hash?

import lxml.html
import lxml.html.builder as E
try:
    import regex as re
except ImportError:
    import re

from . import block
from . import inline

__all__ = ["from_lga", "to_lga", "obfuscate_references", "Parser"]


_LT = "%!lt!%"
_GT = "%!gt!%"
_LTS = "%!lts!%"
_GTS = "%!gts!%"
_AMP = "%!amp!%"

reference_pattern = re.compile(r"\s*\[([\w\s-]+)\]:\s+(.{2,})")
abbreviation_pattern = re.compile(r"\s*\*\[([\w\s-]+)\]:\s+(.{2,})")


def from_lga(text):
    """"""
    text = str(text)
    text = text.replace(_LT, "<")
    text = text.replace(_GT, ">")
    text = text.replace(_AMP, "&")
    return text


def to_lga(text):
    """"""
    text = text.replace("<", _LT)
    text = text.replace(">", _GT)
    text = text.replace("&lt;", _LTS)
    text = text.replace("&gt;", _GTS)
    text = text.replace("&", _AMP)
    return text


def preprocess_script_style_pre_textarea(mahna):
    def esc(m):
        return m.group(0).replace("\n", "%!nl!%")
    mahna = re.sub(r"(?s)<script.*?>(.*?)</script>", esc, mahna)
    mahna = re.sub(r"(?s)<style.*?>(.*?)</style>", esc, mahna)
    mahna = re.sub(r"(?s)<pre.*?>(.*?)</pre>", esc, mahna)
    mahna = re.sub(r"(?s)<textarea.*?>(.*?)</textarea>", esc, mahna)
    return mahna


def preprocess_inline_code(mahna):
    # TODO !!! escape from inside <pre></pre>
    return mahna
    # TODO handle "an inline code block, `\`<div>\``, preprocessor"

    def escape_match_handler(m):
        return "<code>{0}</code>".format(to_lga(m.group(0).strip("`")))
    return re.sub(r"`(.*?)`", escape_match_handler, mahna)


def preprocess_hyphens(mahna):
    new_lines = []
    queue = []
    for line in mahna.splitlines():
        if line != "-" and not line.endswith("--") and line.endswith("-"):
            queue.append(line[:-1])
            continue
        queued = ""
        if len(queue) > 0:
            queued += queue[0]
            line = line.lstrip(" >")
        if len(queue) > 1:
            queued += "".join(l.strip(" >") for l in queue[1:])
        new_lines.append(queued + line)
        queue = []
    return "\n".join(new_lines)


def postprocess_script_style_pre_textarea_code(html):
    html = html.replace("%!nl!%", "\n")
    html = html.replace("%!lts!%", "&lt;")
    html = html.replace("%!gts!%", "&gt;")
    return html


def obfuscate_references(mahna):
    """"""
    references = {}
    for chunk in re.split(r"\n{2,}", mahna):
        reference_match = reference_pattern.match(chunk)
        if reference_match:
            for id, uri in reference_pattern.findall(chunk):
                references.update({id + "---" + str(zlib.adler32(uri)): uri})
            continue
    for id in references.keys():
        before = "[{}]".format(id.partition("---")[0])
        after = "[{}]".format(id)
        mahna = mahna.replace(before, after)
    return mahna


class Parser:

    """

    """

    def __init__(self, text, context=None):
        self.abbrs = {}
        self.refs = {}
        self.toc = []
        self.tags = []
        self.at_mentions = []
        self.mentioned_urls = []
        self.context = context
        self.process(text)

    def process(self, mahna):  # , options=None):
        # document = render(mahna)  # TODO prerender?
        # document = "<meta charset=utf-8>\n" + mahna
        mahna = "\n\n" + str(mahna).strip()
        mahna = preprocess_script_style_pre_textarea(mahna)
        mahna = preprocess_inline_code(mahna)
        mahna = preprocess_hyphens(mahna)

        body = E.DIV()
        self.process_blocks(body, mahna)
        output = lxml.html.tostring(body, encoding="utf-8").decode("utf-8")

        output = output.replace("<p>" + _LT, "<")
        output = output.replace(_GT + "</p>", ">")
        output = from_lga(output)

        dom = lxml.html.fromstring(output)
        dom = E.BODY(dom)
        dom[0].drop_tag()

        for handler_name in inline.__all__:
            handler = getattr(inline, handler_name)()
            self.proc_inlines(handler, dom)
            output = lxml.html.tostring(dom, encoding="utf-8").decode("utf-8")
            output = from_lga(output)
            dom = lxml.html.fromstring(output)

        # self.process_inlines(0, dom)
        # output = lxml.html.tostring(dom, encoding="utf-8").decode("utf-8")
        # output = from_lga(output)
        # dom = lxml.html.fromstring(output)

        dom = E.BODY(dom)

        # TODO repeat setup and teardown for each inline handler as hacked
        #      below for hyphenation -- isolate link creation as root cause?

        # self.process_inlines(1, dom)
        # output = lxml.html.tostring(dom, encoding="utf-8").decode("utf-8")
        # output = from_lga(output)
        # dom = lxml.html.fromstring(output)

        self.process_abbreviations(dom)

        output = lxml.html.tostring(dom, pretty_print=True,
                                    encoding="utf-8").decode("utf-8")
        output = lxml.html.tostring(dom, pretty_print=True).decode("utf-8")

        output = from_lga(output)
        output = postprocess_script_style_pre_textarea_code(output)

        # XXX here be dragons -- skips jumps in hierarchy (e.g. h5 follows h3)
        top_heading_level = 1

        def tocify(_toc, curr):
            section = E.OL()
            i = 0
            for level, text, id in _toc:
                i += 1
                if level == top_heading_level:
                    continue
                if level < curr:
                    return section
                if level == curr:
                    section.append(E.LI(E.A(text, href="#" + id),
                                        tocify(_toc[i:], curr + 1)))
            return section

        toc = tocify(self.toc, top_heading_level + 1)
        toc.set("id", "toc")  # toc["id"] = "toc"
        for ol in toc.cssselect("ol"):    # XXX two words, rhymes with bucket
            if ol.getparent() is not None and not len(ol):
                ol.drop_tag()
        output = output.replace("<p>[Contents] </p>",
                                str(lxml.html.tostring(toc)))

        # if options and options.document:
        #     try:
        #         title = document.title
        #     except AttributeError:
        #         title = body.cssselect("h1")[0].text_content()
        #     self.stylesheet = "<style>{0}</style>".format(self.stylesheet)
        #     try:
        #         style = self.stylesheet + document.stylesheet
        #     except AttributeError:
        #         style = self.stylesheet
        #     output = html.template(options.language, title, style, output)
        # XXX sometimes `lxml` wraps with a <div> .. sometimes it doesn't
        # XXX probably something to do with fromstring/tostring    fffuuuuuu
        # elif output.startswith("<div>"):
        output = output.strip()
        if output.startswith("<body>"):
            output = output[6:-7]
        output = output.strip()
        if output.startswith("<div>"):
            output = output[5:-6]
        output = output.strip()
        if output.startswith("<p></p>"):
            output = output[8:]
        # XXX if inline:
        # XXX     html = html[html.find(">")+1:html.rfind("<")]
        self.html = output

    def process_blocks(self, parent, mahna):
        for chunk in re.split(r"\n{2,}", mahna):
            reference_match = reference_pattern.match(chunk)
            if reference_match:
                self.refs.update(reference_pattern.findall(chunk))
                continue
            abbreviation_match = abbreviation_pattern.match(chunk)
            if abbreviation_match:
                self.abbrs.update(abbreviation_pattern.findall(chunk))
                continue
            for name in block.__all__:
                handler = getattr(block, name)(self)
                match = re.match(handler.pattern, chunk)
                if match:
                    # XXX try:
                    # XXX     encoded_chunk = chunk.decode("utf-8")
                    # XXX except UnicodeEncodeError:
                    # XXX     encoded_chunk = chunk
                    encoded_chunk = chunk

                    # try:
                    element = handler.parse(encoded_chunk)
                    if element is not None:
                        parent.append(element)
                    # except ValueError:
                    #     chunk = "".join(c if ord(c) < 128 else
                    #                     c+"!?" for c in chunk)
                    #     print("Found non Unicode or ASCII char in chunk:",
                    #                 chunk, sep="\n\n", file=sys.stderr)
                    #     sys.exit(1)
                    break

    def proc_inlines(self, handler, parent):
        for child in parent:
            if child.tag in ("script", "style", "pre", "code", "textarea"):
                continue
            handler.parser = self
            self.child = child
            if child.text:
                child.text = re.sub(handler.pattern, handler.parse, child.text)
            if child.tail:
                child.tail = re.sub(handler.pattern, handler.parse, child.tail)
            if child.text:
                child.text = to_lga(child.text)
            if child.tail:
                child.tail = to_lga(child.tail)
            self.proc_inlines(handler, child)

    # def process_inlines(self, stage, parent):
    #     for child in parent:
    #         if child.tag in ("script", "style", "pre", "code", "textarea"):
    #             continue
    #         handler_names = inline.__all__ if stage == 0 else ["Hyphenate"]
    #         for handler_name in handler_names:
    #             handler = getattr(inline, handler_name)()
    #             handler.parser = self
    #             # XXX self.child = child
    #             # XXX self.parent = parent

    #             if child.text:
    #                 while True:
    #                     found = re.split(f"({handler.split_pattern})",
    #                                      child.text)
    #                     print()
    #                     print(handler_name, child.text)
    #                     # print(handler.pattern)
    #                     # print(child.text)
    #                     print(found)
    #                     if len(found) < 3:
    #                         break
    #                     before = "".join(found[:-2])
    #                     matched_text, after = found[-2:]
    #                     child.text = before
    #                     match = re.match(handler.pattern, matched_text)
    #                     replacement = handler.parse(match)
    #                     # if isinstance(replacement, lxml.html.HtmlElement):
    #                     replacement.tail = after
    #                     child.insert(0, replacement)
    #                     # print(lxml.html.tostring(replacement))
    #                     # else:
    #                     #     child.text += replacement + after
    #                     # print(child.text)
    #                     # print(lxml.html.tostring(child))

    #             # if child.text:
    #             #     child.text = re.sub(handler.pattern, handler.parse,
    #             #                         child.text)

    #             # if child.tail:
    #             #     child.tail = re.sub(handler.pattern, handler.parse,
    #             #                         child.tail)
    #         if child.text:
    #             child.text = to_lga(child.text)
    #         if child.tail:
    #             child.tail = to_lga(child.tail)
    #         self.process_inlines(stage, child)

    def process_abbreviations(self, parent):
        for child in parent:
            if child.tag in ("script", "style", "pre", "code", "textarea"):
                continue
            for abbr, full in self.abbrs.items():
                html = '<abbr title="{}">{}</abbr>'.format(full, abbr)
                if child.text:
                    child.text = to_lga(child.text.replace(abbr, html))
                if child.tail:
                    child.tail = to_lga(child.tail.replace(abbr, html))
            self.process_abbreviations(child)

    def __str__(self):
        return self.html
