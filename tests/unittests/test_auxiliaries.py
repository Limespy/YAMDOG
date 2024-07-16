import pytest
import yamdog as md
from yamdog import _API
# ======================================================================
# _INDENT
def test_RAW_INDENT_is_4_spaces():
    assert _API._RAW_INDENT == ' '*4
# ======================================================================
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
# ======================================================================
class Test_collect_iter:
    def test_collect_iter_single(self):
        ref = md.Link('target', 'content', 'title')
        footnote = md.Footnote('footnote')
        visited, output = _API._collect_iter([ref, footnote],
                                             set(),
                                             _API._empty_collected())
        links, footnotes = output
        assert visited == {id(ref), id(footnote)}
        assert dict(links) == {('target', 'title'): [ref]}
        assert dict(footnotes) == {str(footnote.content): [footnote]}
    #─────────────────────────────────────────────────────────────────────────
    def test_collect_iter_multiple(self):
        ref1 = md.Link('target', 'content', 'title')
        ref2 = md.Link('target', 'content', 'title')
        ref3 = md.Link('target3', 'content3', 'title3')
        footnote1 = md.Footnote('footnote1')
        footnote2 = md.Footnote('footnote2')
        visited, output = _API._collect_iter([
            'test-no-collect',
            md.Text('test-no-collect1', {md.BOLD}),
            md.Text(ref3, {md.ITALIC}),
            md.Link('test-no-collect', 'test-no-collect'),
            ref1,
            md.Paragraph([ref2,
                        md.Text('test-no-collect2', {md.BOLD}),
                        ref1]),
            md.QuoteBlock(footnote1),
            md.Table([['a', footnote2]], [1,2]),
        ], set(), _API._empty_collected())
        links, footnotes = output
        expected_ln = {('target', 'title'): [ref1, ref2],
                       ('target3', 'title3'): [ref3]}
        print(dict(links))
        print(expected_ln)
        assert dict(links) == expected_ln
        expected_fn = {str(footnote1.content): [footnote1],
                       str(footnote2.content): [footnote2]}
        assert dict(footnotes) == expected_fn
# ======================================================================
# Header
@pytest.mark.parametrize("args,expected", [
    (('yaml', 'test'),  '---\ntest\n---'),
    (('toml', 'test'),  '+++\ntest\n+++'),
    (('json', 'test'),  ';;;\ntest\n;;;'),
    (('php', 'test'),   '---php\ntest\n---')])
def test_header_str(args, expected):
    assert str(_API._process_header(*args)) == expected
