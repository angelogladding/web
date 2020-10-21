"""
encode/decode formatted plaintext to and from HTML

Plaintext to HTML that strives to use concise, human-readable textual anno-
tations to build rich documents of various size and purpose including sta-
tus updates, scholarly works, screenwriting, literate programming, etc.

The guiding philosophy of both the syntax and features is to allow the
user as much freedom as possible to convey a message while automatically
handling the distracting, repetitive details commonly involved with pub-
lishing for the web.

    >>> text = "foo bar"
    >>> html = "<p>foo bar</p>"
    >>> encode(text) == decode(html)
    True

>   The idea was to make writing simple web pages ... as easy as writing
>   an email, by allowing you to use much the same syntax and converting
>   it automatically into HTML ... [and] back into Markdown.

--- Aaron Swartz, [Markdown][1] -- March 19, 2004

[1]: http://www.aaronsw.com/weblog/001189

"""

# TODO lettered-list
# TODO talk about typesetting
# TODO bibtex??
# TODO mathtex??
# TODO font-families
# TODO microformats
# TODO code[, var, kbd, ..](`), sub(_), sup(^), em(*), strong(**)
# TODO a, footnote[^abba] (w/ \u21A9), abbr, cite[@Angelo], q (w/ @cite)
# TODO table
# TODO img, figure (w/ figcaption), audio, video
# TODO smart quotes, dashes, ellipses
# TODO widont
# TODO syntax highlight
# TODO table of contents, reheader (# > h2), index, bibliography
# TODO papaya pilcrows
# TODO emoticons
# TODO l10n (charset)
# TODO math
# TODO timestamp
# TODO [tl;dr] as Abstract
# TODO formulae to formul\u00E6
# TODO slidy/S5

from .parse import Parser as render

__all__ = ["render"]


# def render(plaintext, inline=False):
#     """
#     return HTML representing the rendered plaintext
#
#     """
#     parser = parse.Parser(plaintext)
#     html = str(parser)
#     if html.startswith("<p></p>"):
#         html = html[8:]
#     if inline:
#         html = html[html.find(">")+1:html.rfind("<")]
#     data = {"tags": parser.tags, "mentions": parser.mentions}
#     return parser
