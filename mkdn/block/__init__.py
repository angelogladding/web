"""

"""

# TODO remove clean_indent in favor of dedent

from inspect import cleandoc as clean_indent
import re
from textwrap import dedent

import lxml.html
import lxml.html.builder as E
import pygments
import pygments.formatters
import pygments.lexers

from .titlecase import titlecase

__all__ = ["HTML", "Pre", "HashHeading", "ReSTHeading", "HorizontalRule",
           "OrderedList", "UnorderedList", "DefinitionList",
           "Blockquote", "Paragraph"]


class Block:

    """
    a generic block

    """

    def __init__(self, parser):
        self.parser = parser


class HTML(Block):

    """
    a block of raw HyperText

    """

    pattern = r"^<"

    def parse(self, block):
        """"""
        # if re.match(r"^</?[a-z0-9 =-]+>$", block):
        #     return E.PRE(block)  # TODO begin/end tags in blocks
        # XXX print(len(block))
        # XXX print(block)
        # XXX print()
        # XXX print()
        # XXX print()
        try:
            element = lxml.html.fromstring(block)
        except lxml.etree.ParserError:
            element = None
        return element
        # return lxml.html.fromstring(to_lga(block))


class Heading:

    """
    a generic heading

    """

    def process_heading(self, level, lines):
        """
        automatically titlecase so long as text doesn't end with " &"

        """
        sections = []
        for line in lines:
            if line.endswith("  "):
                line = line[:-2] + " <br>"
            sections.append(line)
        text = " ".join(sections)
        id_match = re.match(r".*\{(?P<id>\w[\w\d-]*[\w\d])\}$", text)
        if id_match:
            text = text.rpartition(" {")[0]
            id = id_match.group("id")
        else:
            id = text.lower().replace(" <br> ", "-").replace(" ", "-")
        text = text.rstrip()
        if text.endswith("&"):
            text = text.rstrip(" &")
            id = id.rstrip("-&")
        else:
            text = titlecase(text)
        html = "<h{0} id={1}>{2}</h{0}>"
        element = lxml.html.fromstring(html.format(level, id, text))
        # element= lxml.html.fromstring("<h{0}>{1}</h{0}>".format(level, text))
        # self.parser.toc.append((int(level), str(element.text_content()), id))
        return element


class HashHeading(Block, Heading):

    """
    a hash heading

    """

    pattern = r"^[#]{1,6}"

    def parse(self, block):
        """"""
        level = len(block.partition(" ")[0])
        lines = [line.lstrip("# ") for line in block.splitlines()]
        return self.process_heading(level, lines)


class ReSTHeading(Block, Heading):

    """
    a ReStructuredText (setext) heading

    """

    pattern = r"^(?s).*\n(=|-)+$"

    def parse(self, block):
        """"""
        level = "1" if block[-1] == "=" else "2"
        lines = block.splitlines()[:-1]
        return self.process_heading(level, lines)


class HorizontalRule(Block):

    """
    a horizontal rule

    """

    pattern = r"^\s*((\*|-|_|:)\s*){3,}$"

    def parse(self, block):
        """"""
        return E.HR()


class List:

    """
    a generic list

    """

    def parse(self, block):
        """"""
        list = self.list_type()
        for inner_block in re.split(self.list_pattern, block)[1:]:
            item = E.LI()
            self.parser.process_blocks(item, clean_indent(inner_block))
            list.append(item)
        return list


class OrderedList(Block, List):

    """
    an ordered list

    """

    pattern = r"^([\w#][.\)]\s{2}|\w{2}[.\)]\s)\S"
    list_pattern = r"(?m)^\w{1,2}\.\s+"
    list_type = E.OL


class UnorderedList(Block, List):

    """
    an unordered list

    """

    pattern = r"^(\*|\-|\+)[ ]{3}\S"
    list_pattern = r"(?m)^[\*\-\+][ ]{3}"
    list_type = E.UL


class DefinitionList(Block):

    """
    a definition list

    """

    pattern = r"^[\w\s]+\n:\s{3}\S"

    def parse(self, block):
        """"""
        list = E.DL()
        for inner_block in re.split(r"(?m)\n    \n(?=\w)", block):
            term_block, _, definition_block = inner_block.partition("\n:   ")
            for term in term_block.splitlines():
                list.append(E.DT(term))
            for def_block in definition_block.split("\n:   "):
                definition = E.DD()
                self.parser.process_blocks(definition,
                                           clean_indent(def_block))
                list.append(definition)
        return list


class Pre(Block):

    """
    a block of preformatted text

    """

    pattern = r"^[ ]{4}"

    def parse(self, block):
        """"""
        text = dedent(block)
        if text.startswith(">>> "):
            lexer = pygments.lexers.PythonConsoleLexer()
            lexer.add_filter("codetagify")
            formatter = pygments.formatters.HtmlFormatter(cssclass="doctest")
            code = pygments.highlight(text, lexer, formatter)
            html = lxml.html.fromstring(code)
        else:
            html = E.PRE(text)
        return html


class Blockquote(Block):

    """
    a block quotation

    The block quotation is used to denote a passage significant enough to
    stand alone.

        >   when & where?
        >
        >   >   Joe's @ Noon

        >>> blockquote = Blockquote('''
        ... >   when & where?
        ... >
        ... >   >   Joe's @ Noon''')
        >>> print(blockquote)
        <blockquote>
            <p>when &amp; where?</p>
            <blockquote>
                <p>Joe's @ Noon</p>
            </blockquote>
        </blockquote>

    """

    pattern = r"^>"

    def parse(self, block):
        """"""
        inner_blocks = "\n".join(l[2:] for l in block.splitlines())
        tree = E.BLOCKQUOTE()
        self.parser.process_blocks(tree, inner_blocks)
        return tree


class Paragraph(Block):

    """
    a paragraph

    The paragraph is the simplest block type as well as the fallback.

        Lorem ipsum dolor sit amet.

    Lorem ipsum dolor sit amet.

        >>> paragraph = Paragraph('''Lorem ipsum dolor sit amet.''')
        >>> print(paragraph)
        <p>Lorem ipsum dolor sit amet.</p>

    """

    pattern = r".*"

    def parse(self, block):
        """"""
        lines = []
        for line in block.splitlines():
            if line.endswith("  "):
                lines.append(line[:-2])
                lines.append(E.BR())
            else:
                lines.append(line + " ")
        return E.P(*lines)
