"""
render Python powered string templates

>   But you're right, it is "yet another template language". And I'm not
>   going to apologize for it.

--- Aaron Swartz

Syntax
------

*   secure Python via [Templetor]
*   a strict superset dialect of [Markdown]
*   literate programming aided by [reStructuredText]
*   mathematical formulae a la [LaTeX]

Features
--------

*   spell check based upon GNU's Aspell (91 countries)
*   style conformance according to:

    *   [The Elements of Style]
    *   [The Elements of Typographic Style]

The following example demonstrates headings, block quotation, paragraphs,
ellipses, em dash, smart quotes, Microformats (hCard), lowercased figures,
title case, auto-reference and spell check.

(217 characters to 450+ including X codes.)

    >>> mana('''
    ... On nonsnse in prose  {nonsense}
    ... ===============================
    ...
    ... > ...
    ... > Beware the Jubjub bird, and shun
    ... > The frumious Bandersnatch!
    ... > ...
    ...
    ... --- @[Lewis Carroll], "Through the Looking-Glass,
    ...                        and What Alice Found There" 1872
    ... ''', stage='proof')  #doctest: +NORMALIZE_WHITESPACE
    '<h1 id=nonsense><a href=#nonsense>On <span class=x-spelling><span
    class=x-error>Nonsnse</span> (<span class=x-suggestions>Nonsense,
    Nonsenses, Nansen's, Nonsense's, Ninon's, Jonson's</span>)</span> in
    Prose</a></h1><blockquote><p>&#x; Be&shy;ware the Jub&shy;jub bird,
    and shun<br>The frumious Bandersnatch!&nbsp;&#x;</p></blockquote><p>&#x;
    <span class=h-card>Lew&shy;is Carroll</span>, &#x;Through the
    Look&shy;ing-Glass, and What Al&shy;ice Found There&#x;&nbsp;<span
    class=>1872</span></p>'

"""

from .templating import templates, build, Template, TemplatePackage

__all__ = ["templates", "build", "Template", "TemplatePackage"]
