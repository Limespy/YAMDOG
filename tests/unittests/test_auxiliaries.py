from pprint import pprint

import pytest
import yamdog as md
from yamdog import _API
#══════════════════════════════════════════════════════════════════════════════
# _INDENT
def test_INDENT_is_4_spaces():
    assert _API._INDENT == ' '*4
#══════════════════════════════════════════════════════════════════════════════
# _sanitise_str
@pytest.mark.parametrize("string, expected", [
    ('test', 'test'),
    (' test', ' test'),
    ('test ', 'test '),
    ('test\t', 'test\t'),
    ('''test
        text''',  'test text')])
def test_string_sanitisation(string, expected):
    assert _API._sanitise_str(string) == expected
#══════════════════════════════════════════════════════════════════════════════
# _collect_iter
def test_collect_iter():
    link_collect1 = md.Link('target', 'content', 'title')
    link_collect2 = md.Link('target', 'content', 'title')
    link_collect3 = md.Link('target3', 'content3', 'title3')
    footnote1 = md.Footnote('footnote1')
    footnote2 = md.Footnote('footnote2')
    output = _API._collect_iter([
        'test-no-collect',
        md.Text('test-no-collect1', {md.BOLD}),
        md.Text(link_collect3, {md.ITALIC}),
        md.Link('test-no-collect', 'test-no-collect'),
        link_collect1,
        md.Paragraph([link_collect2,
                      md.Text('test-no-collect2', {md.BOLD}),
                      link_collect1]),
        md.QuoteBlock(footnote1),
        md.Table([1,2], [['a', footnote2]]),
    ])
    links, footnotes = output
    assert dict(links) == {('target', 'title'): {id(link_collect1): link_collect1,
                                       id(link_collect2): link_collect2},
                       ('target3', 'title3'): {id(link_collect3): link_collect3}}
    assert dict(footnotes) == {footnote1: {id(footnote1): footnote1},
                               footnote2: {id(footnote2): footnote2}}
#══════════════════════════════════════════════════════════════════════════════
# Header
@pytest.mark.parametrize("args,expected", [
    (('yaml', 'test'),  '---\ntest\n---'),
    (('toml', 'test'),  '+++\ntest\n+++'),
    (('json', 'test'),  ';;;\ntest\n;;;'),
    (('php', 'test'),   '---php\ntest\n---')])
def test_header_str(args, expected):
    assert str(_API._process_header(*args)) == expected
#══════════════════════════════════════════════════════════════════════════════
# _pad
def test_pad_raises_ValueError_with_incorrect_alignment():
    with pytest.raises(ValueError):
        list(_API._pad(['a', 'b'], [3, 3], [md.LEFT, 'left'])) # type: ignore
