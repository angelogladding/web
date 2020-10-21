"""

"""

# import os
import re

import lxml.html
# from lxml.html import builder as E
import pkg.licensing

# from . import hyphenator
import uri

__all__ = [  # "SmartQuotes",
           # # "SmallCapitals",
           # # "LicenseLink", "LicenseReference", "LicenseAutoReference",
           # # "OrgLink", "OrgReference", "OrgAutoReference",
           # # "PersonLink", "PersonReference", "PersonAutoReference",
           # "ImageLink", "ImageReference", "ImageAutoReference",
           # "WikiLink",
           # "Reference", "AutoReference",
           # "AutoMagnet",
           # "Section", "Widow",
           "StrongEm", "Strong", "Em", "Small", "Code",

           "Link", "AutoLink", "WikiLink",
           "Mention", "Tag",

           # "Ampersand", "Copyright", "Ellipsis", "LigatureAE", "Heart",
           # "QuotationDash", "DblEmDash",
           # "InnerEmDash",
           "EmDash",
           # "InnerEnDash",
           "EnDash",
           # # "Hyphenate",
           ]


# STAGES = (__all__[:], __all__[:])
LINK_CONTAINER_RE = r"\[(?P<text>.+?)\]"


class Inline:

    """"""

    # def __init__(self, text):
    #     self.text = text

    # def str(self):
    #     return self.template.format(**self.parse(re.match(self.pattern,
    #                                                       self.text)))


class Link(Inline):

    """

        >>> link = Link("[Example](http://example.org/)")
        >>> str(link)
        u'<a href=""></a>'

    """

    split_pattern = r"\[.+?\]\(.+?\)"
    pattern = LINK_CONTAINER_RE + r"(?P<uri>\(.+?\))"

    def parse(self, match):
        given_url = match.group("uri")
        if given_url.startswith(("(#", "(/")):
            url = given_url[1:-1]
        else:
            if given_url.endswith(' "wikilink")'):
                url = uri.parse(self.parser.context)
                url.path = given_url[1:-12]
            else:
                url = uri.parse(given_url[1:-1])
            url = url.normalized
        text = match.group("text")
        return f'<a href="{url}">{text}</a>'
        # return E.A(text, href=url.normalized)


class AutoLink(Inline):

    """

    """

    split_pattern = r"https?://\S+"
    pattern = r"(?P<uri>https?://\S+)"

    def parse(self, match):
        url = uri.parse(match.group("uri"))
        self.parser.mentioned_urls.append(url)
        return f"<a href={url.normalized}>{url.minimized}</a>"
        # return E.A(url.minimized, href=url.normalized)


class WikiLink(Inline):

    """

    """

    pattern = r"\[\[(?P<page>.+?)\]\]"

    def parse(self, match):
        # TODO define wiki prefix in renderer config
        page = match.group("page")
        path = page.replace(" ", "")  # TODO CamelCase
        return f"<a href=/pages/{path}>{page}</a>"


class Mention(Inline):

    """

    """

    split_pattern = r"@[A-Za-z0-9.]+"
    pattern = r"@(?P<person>[A-Za-z0-9.]+)"

    def parse(self, match):
        if self.parser.child.tag == "a":
            self.parser.child.attrib["class"] = "h-card"
            return f"@{match.groups()[0]}"
        # TODO rel=tag for "entry" context
        person = match.group("person")
        self.parser.at_mentions.append(person)
        return f"<a class=h-card href=/people/{person}>{person}</a>"
        # return E.A(person, E.CLASS("h-card"), href=f"/people/{person}")


class Tag(Inline):

    """

    """

    split_pattern = r"#[A-Za-z0-9]+"
    pattern = r"#(?P<tag>[A-Za-z0-9]+)"

    def parse(self, match):
        # TODO rel=tag for "entry" context
        tag = match.group("tag")
        self.parser.tags.append(tag)
        return f"<a class=p-category href=/tags/{tag}>{tag}</a>"
        # return E.A(tag, E.CLASS("p-category"), href=f"/tags/{tag}")


# ----------------------------------------------------------------------


class SmartQuotes:

    """"""

    pattern = r".*"

    def parse(self, match):
        punct = r"""[!"#\$\%'()*+,-.\/:;<=>?\@\[\\\]\^_`{|}~]"""
        text = match.group(0)

        # Special case if the very first character is a quote followed by
        # punctuation at a non-word-break. Close the quotes by brute force:
        text = re.sub(r"""^'(?=%s\\B)""" % (punct,), r"""&#8217;""", text)
        text = re.sub(r"""^"(?=%s\\B)""" % (punct,), r"""&#8221;""", text)

        # Special case for double sets of quotes, e.g.:
        #   <p>He said, "'Quoted' words in a larger quote."</p>
        text = re.sub(r""""'(?=\w)""", """&#8220;&#8216;""", text)
        text = re.sub(r"""'"(?=\w)""", """&#8216;&#8220;""", text)

        # Special case for decade abbreviations (the '80s):
        text = re.sub(r"""\b'(?=\d{2}s)""", r"""&#8217;""", text)

        close_class = r"""[^\ \t\r\n\[\{\(\-]"""
        dec_dashes = r"""&#8211;|&#8212;"""

        # Get most opening single quotes:
        opening_single_quotes_regex = re.compile(r"""
                (
                    \s          |   # a whitespace char, or
                    &nbsp;      |   # a non-breaking space entity, or
                    --          |   # dashes, or
                    &[mn]dash;  |   # named dash entities
                    %s          |   # or decimal entities
                    &\#x201[34];    # or hex
                )
                '                 # the quote
                (?=\w)            # followed by a word character
                """ % (dec_dashes,), re.VERBOSE)
        text = opening_single_quotes_regex.sub(r"""\1&#8216;""", text)

        closing_single_quotes_regex = re.compile(r"""
                (%s)
                '
                (?!\s | s\b | \d)
                """ % (close_class,), re.VERBOSE)
        text = closing_single_quotes_regex.sub(r"""\1&#8217;""", text)

        closing_single_quotes_regex = re.compile(r"""
                (%s)
                '
                (\s | s\b)
                """ % (close_class,), re.VERBOSE)
        text = closing_single_quotes_regex.sub(r"""\1&#8217;\2""", text)

        # Any remaining single quotes should be opening ones:
        text = re.sub(r"""'""", r"""&#8216;""", text)

        # Get most opening double quotes:
        opening_double_quotes_regex = re.compile(r"""
                (
                    \s          |  # a whitespace char, or
                    &nbsp;      |  # a non-breaking space entity, or
                    --          |  # dashes, or
                    &[mn]dash;  |  # named dash entities
                    %s          |  # or decimal entities
                    &\#x201[34];   # or hex
                )
                "                  # the quote
                (?=\w)             # followed by a word character
                """ % (dec_dashes,), re.VERBOSE)
        text = opening_double_quotes_regex.sub(r"""\1&#8220;""", text)

        # Double closing quotes:
        closing_double_quotes_regex = re.compile(r"""
                #(%s)?  # character that indicates the quote should be closing
                "
                (?=\s)
                """ % (close_class,), re.VERBOSE)
        text = closing_double_quotes_regex.sub(r"""&#8221;""", text)

        closing_double_quotes_regex = re.compile(r"""
                (%s)   # character that indicates the quote should be closing
                "
                """ % (close_class,), re.VERBOSE)
        text = closing_double_quotes_regex.sub(r"""\1&#8221;""", text)

        # Any remaining quotes should be opening ones.
        text = re.sub(r'"', r"""&#8220;""", text)

        lsquo = r"""<span class="lsquo"><span>'</span></span>"""
        rsquo = r"""<span class="rsquo"><span>'</span></span>"""
        ldquo = r"""<span class="ldquo"><span>"</span></span>"""
        rdquo = r"""<span class="rdquo"><span>"</span></span>"""

        text = text.replace("&#8216;", lsquo)
        text = text.replace("&#8217;", rsquo)
        text = text.replace("&#8220;", ldquo)
        text = text.replace("&#8221;", rdquo)

        return text


class AutoMagnet(Inline):

    """

    """

    pattern = r"(?P<uri>magnet:.+?)"

    def parse(self, match):
        uri = match.group("uri")
        return '<a href="{0}">{0}</a>'.format(uri)


class Reference(Inline):

    """

        >>> reference = Reference("[Example][1]")
        >>> str(reference)
        u'<a href=""></a>'

    """

    pattern = LINK_CONTAINER_RE + r"\[(?P<reference_id>.+?)\]"
    template = '<a href="{uri}">{text}</a>'

    def parse(self, match):
        text = match.group("text")
        reference_id = match.group("reference_id")
        try:
            uri = self.parser.refs[reference_id]
        except KeyError:
            uri = ""  # XXX catch in parser and store as warning
            # raise ReferenceError("no reference for " + reference_id)
        return self.template.format(uri=uri, text=text)


class AutoReference:

    """

    """

    pattern = LINK_CONTAINER_RE
    template = '<a href="{uri}">{text}</a>'

    def parse(self, match):
        text = match.group("text")
        # XXX reference = lxml.html.fromstring(from_lga(text)).text_content()
        reference = lxml.html.fromstring(text).text_content()
        try:
            uri = self.parser.refs[reference]
        except KeyError:
            return match.group(0)
        return self.template.format(uri=uri, text=text)


class ImageLink(Link):

    """"""

    pattern = "!" + Link.pattern

    def parse(self, match):
        """"""
        text = match.group("text")
        uri = match.group("uri").strip("()")
        try:
            return '<img src="{0}" alt="{1}">'.format(uri, text)
        except KeyError:
            return match.group(0)


class ImageReference(Reference):

    """"""

    pattern = "!" + Reference.pattern

    def parse(self, match):
        text = match.group("text")
        reference_id = match.group("reference_id")
        try:
            uri = self.parser.refs[reference_id]
        except KeyError:
            return text
        return '<img src="{0}" alt="{1}">'.format(uri, text)


class ImageAutoReference(AutoReference):

    """"""

    pattern = "!" + AutoReference.pattern

    def parse(self, match):
        text = match.group("text")
        try:
            uri = self.parser.refs[text]
        except KeyError:
            return ""
        return '<img src="{0}" alt="{1}">'.format(uri, text)


# class LicenseLink(Link):
#
#     """"""


# class LicenseReference(Reference):
#
#     """"""


class LicenseAutoReference(AutoReference):

    """"""

    pattern = "%" + AutoReference.pattern

    def parse(self, match):
        alias = match.group(1)
        try:
            uri, name, version = pkg.licensing.get_license(alias)
        except pkg.licensing.LookupError:
            return alias
        anchor_template = '<a href="http://{}" rel=license>{} License</a>'
        return anchor_template.format(uri, name)


# class OrgLink(Link):
#
#     """"""
#
#     template = """"""


# class OrgReference(Reference):
#
#     """"""
#
#     template = '<span class="vcard h-card"><a class="fn p-fn '
#                'org h-org url u-url" href="{0}">{1}</a></span>'


# class OrgAutoReference(AutoReference):
#
#     """"""
#
#     pattern = "@@" + AutoReference.pattern
#     template = """<span class=h-card>{0}</span>"""
#
#     def parse(self, match):
#         text = match.group(1)
#         wrapper = '<span class="vcard h-card">{0}</span>'
#         try:
#             uri = self.parser.refs[text]
#         except KeyError:
#             return self.template.format('<span class="fn '
#                                         'org">{0}</span>'.format(text))
#         return wrapper.format('<a class="fn org url" '
#                               'href="{0}">{1}</a>'.format(uri, text))


# class PersonLink(Link):
#
#     """
#
#     """
#
#     pattern = "@" + Link.pattern
#     format_string = """<span class="vcard h-card">
#                        <a class="fn p-fn org h-org url u-url"
#                        href="{uri}">{text}</a>
#                        </span>"""


# class PersonReference(Reference):
#
#     """"""
#
#     template = """<span class="vcard h-card"><a class="fn """
#                """p-fn url u-url" href="{0}">{1}</a></span>"""


# class PersonAutoReference(AutoReference):
#
#     """"""
#
#     def parse(self, match):
#         """"""
#         text = match.group(1)
#         wrapper = u'<span class="vcard h-card">{0}</span>'
#         try:
#             uri = self.parser.refs[text]
#         except KeyError:
#             if "{" in text:
#                 text = text.replace("}", "</span>")
#                 z = re.compile(r"\{(?P<semantics>[\w,-]+):")
#
#                 def y(m):
#                     semantics = m.group("semantics").split(",")
#                     classes = " ".join(pr[2:] + " " + pr for pr in semantics)
#                     return u'<span class="{0}">'.format(classes)
#
#                 return wrapper.format(z.sub(y, text))
#             return wrapper.format(u'<span class="fn '
#                                   u'p-fn">{0}</span>'.format(text))
#         return wrapper.format(u'<a class="fn p-fn url u-url" '
#                               u'href="{0}">{1}</a>'.format(uri, text))


class Section:

    """"""

    pattern = r"(?P<symbol>SS?)\s+(?P<section>[\d.]+)"

    def parse(self, match):
        symbol = match.group("symbol")
        section = match.group("section")
        html = '<span class="x-section"><span>S</span></span>'
        return "&nbsp;".join((" ".join([html] * len(symbol)), section))


class Widow:

    """"""

    pattern = r"(?P<before>[\w\[\]]+)\s(?P<after>[\w'\[\]]+[\.,)]*\s*)$"

    def parse(self, match):
        return "&nbsp;".join((match.group("before"), match.group("after")))


# class SmallCapitals:
#
#     pattern = r"""
#         (?x)
#         \b
#         (?P<acronym>
#             AT&T | Q&A |
#             [A-Z\d][A-Z\d\./]{2,} |
#             [A-Z]{2,}
#         )
#         \b
#     """
#
#     def parse(self, match):
#         html = "<span class=x-small-caps>{0}</span>"
#         acronym = match.group("acronym")
#         # if self.roman_numeral_pattern.match(acronym).group("numeral"):
#         #     # html = "<span class=x-suggest-caps>{0}</span>"
#         #     return acronym
#         #     # if self.config["stage"] == "publish":
#         #     #     if acronym not in self.config["proofed"]:
#         #     #         return acronym
#         #     # else:
#         #     #     html = "<span class=x-suggest-caps>{0}</span>"
#         return html.format(acronym)
#
#     # Copyright (c) 2009, Mark Pilgrim, BSD License
#     roman_numeral_pattern = re.compile(r"""(?x)
#                                            (?P<numeral>
#                                                M{0,4}            # thousands
#                                                (CM|CD|D?C{0,3})  # hundreds
#                                                (XC|XL|L?X{0,3})  # tens
#                                                (IX|IV|V?I{0,3})  # ones
#                                            )""")


class StrongEm(Inline):

    # pattern = r"""\*{3}([\w\s\-.,'"]+)\*{3}"""
    pattern = r"""\*{3}(.+?)\*{3}"""

    def parse(self, match):
        text = match.group(1)
        return "<strong><em>{0}</em></strong>".format(text)


class Strong(Inline):

    # pattern = r"""\*{2}([\w\s\-.,'"]+)\*{2}"""
    pattern = r"""\*{2}(.+?)\*{2}"""

    def parse(self, match):
        text = match.group(1)
        return '<strong>{0}</strong>'.format(text)


class Em(Inline):

    # pattern = r"""\*([\w\s\-.,'"]+)\*"""
    pattern = r"""\*(.+?)\*"""

    def parse(self, match):
        text = match.group(1)
        return "<em>{0}</em>".format(text)


class Small(Inline):

    # pattern = r"""~([\w\s\-/<>%!.,'"]+)~"""
    pattern = r"""(?s)~(.+?)~"""

    def parse(self, match):
        text = match.group(1)
        return "<small>{0}</small>".format(text)


class Code(Inline):

    pattern = r"""(?s)`(.+?)`"""

    def parse(self, match):
        text = match.group(1)
        return "<code>{0}</code>".format(text)


class Ampersand(Inline):

    pattern = r" %!amp!% "

    def parse(self, match):
        return " <span class=x-amp>%!amp!%</span> "


class Copyright(Inline):

    pattern = r" \(c\) "

    def parse(self, match):
        return " &copy; "


class Ellipsis(Inline):

    pattern = r"\.\.\."

    def parse(self, match):
        # return "<span class=ellipsis><span>...</span></span>"
        return "&hellip;"


class QuotationDash(Inline):

    pattern = r"^---"

    def parse(self, match):
        return "<span class=quotation-dash><span>---</span></span>"


class DblEmDash(Inline):

    pattern = r"----"

    def parse(self, match):
        # return "<span class=em-dash><span>--</span></span>" * 2
        return "&emdash;" * 2


class EmDash(Inline):

    pattern = r"---"

    def parse(self, match):
        return "<span class=em-dash><span>&#x2014;</span></span>"


class InnerEmDash(Inline):

    pattern = r" --- "

    def parse(self, match):
        # return '<span class="em-dash inner"><span> --- </span></span>'
        return '&thinsp;&#x2014;&thinsp;'


class EnDash(Inline):

    pattern = r"--"

    def parse(self, match):
        return "<span class=en-dash><span>&#x2013;</span></span>"


class InnerEnDash(Inline):

    pattern = r" -- "

    def parse(self, match):
        # return '<span class="en-dash inner"><span>--</span></span>'
        return "&thinsp;&#x2013;&thinsp;"


class LigatureAE(Inline):

    pattern = r"(?i)(ae)"

    def parse(self, match):
        html = '<span class="x-ligature-ae x-{0}"><span>{1}</span></span>'
        cases = {"ae": "lower", "AE": "upper", "Ae": "upper"}
        m = match.group(1)
        return html.format(cases[m], m)


class Heart(Inline):

    pattern = r" <3 "

    def parse(self, match):
        return " &#x2764; "


# class Hyphenate(Inline):
#
#     # pattern = r"(?<!%!amp!%nbsp;)(?P<word>\w{4,}[\., \n])"
#     pattern = r"(?P<word>\w{4,}[\., \n])"
#
#     def parse(self, match):
#         hyphen_dict = os.path.dirname(__file__) + "/hyph_en_US.dic"
#         hyphenate = hyphenator.Hyphenator(hyphen_dict)
#         word = match.group("word")
#         sections = []
#         for section in word.split("-"):
#             sections.append(hyphenate.inserted(section).replace("-",
#                                                                 "&shy;"))
#         hyphenated = "-".join(sections)
#         start, _, final = hyphenated.rpartition("&shy;")
#         if len(final.strip()) < 3:  # or (final.endswith(".") and
#                                     # len(final.strip()) < 4):  # an-oth-er.
#             hyphenated = start + final
#         return hyphenated
