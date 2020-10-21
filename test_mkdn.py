from mkdn import render


def t(mkdn, html):
    assert str(render(mkdn)) == str(render(html))


def test_link():
    t("a [basic](//basic) link",
      "<p>a <a href=https://basic>basic</a> link </p>")


def test_auto_link():
    t("an https://auto link",
      "<p>an <a href=https://auto>auto</a> link </p>")


def test_wiki_link():
    t("a [[wiki]] link",
      "<p>a <a href=/pages/wiki>wiki</a> link </p>")
    t("a [[wiki/subpage]] link",
      "<p>a <a href=/pages/wiki/subpage>wiki/subpage</a> link </p>")


def test_mention():
    t("@jane went to town",
      "<p><a class=h-card href=/people/jane>jane</a> "
      "went to town </p>")


def test_tag():
    t("they discussed #ProgressiveEnhancement over dinner",
      "<p>they discussed <a class=p-category "
      "href=/tags/ProgressiveEnhancement>ProgressiveEnhancement</a> "
      "over dinner </p>")


# def test_dates():
#     _test([("1440-80's",
#             '<p>1440-80<span class="rsquo"><span>\'</span></span>s </p>'),
#            # ("1440-'80s", "1440-&#8216;80s"),
#            # ("1440---'80s", "1440&#8211;&#8216;80s"),
#            # ("1960s", "1960s"),
#            # ("1960's", "1960&#8217;s"),
#            # ("one two '60s", "one two &#8216;60s"),
#            ("'60s",
#             '<p><span class="lsquo"><span>\'</span></span>60s </p>')])


# def test_comments():
#     _test([("--", "&#8212;"),
#            ("-->", "&#8212;>"),
#            ("<!-- comment -->", "<!-- comment -->"),
#            ("<!-- <li>Fee-fi-of-fum</li> -->",
#             "<!-- <li>Fee-fi-of-fum</li> -->")])


# def test_ordinal_numbers():
#     _test([("21st century", "21st century"),
#            ("3rd", "3rd")])


# def test_educated_quotes():
#     _test([('''"Isn't this fun?"''',
#             '''&#8220;Isn&#8217;t this fun?&#8221;''')])
