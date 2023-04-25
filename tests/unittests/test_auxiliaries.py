import pytest
import yamdog._API as md

#══════════════════════════════════════════════════════════════════════════════
# clean_string
@pytest.mark.parametrize("string, expected", [
    ('test', 'test'),
    (' test', ' test'),
    ('test ', 'test '),
    ('test\t', 'test\t'),
    ('''test
        text''',  'test text')])
def test_string_sanitisation(string, expected):
    assert md._sanitise_str(string) == expected
#══════════════════════════════════════════════════════════════════════════════
# Element
#──────────────────────────────────────────────────────────────────────────────
def test_element_add():
    element1 = md.Heading(1, 'test')
    element2 = md.Link('test', 'case')
    assert element1 + element2 == md.Document([element1, element2])
    assert element2 + element1 == md.Document([element2, element1])
#══════════════════════════════════════════════════════════════════════════════
# _collect_iter
def test_collect_iter():
    link_collect1 = md.Link('link-collect1', 'link-collect1', 'link-collect1')
    link_collect2 = md.Link('link-collect2', 'link-collect2', 'link-collect2')
    link_collect3 = md.Link('link-collect3', 'link-collect3', 'link-collect3')
    footnote1 = md.Footnote('footnote1')
    footnote2 = md.Footnote('footnote2')
    output = md._collect_iter([
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
    assert output == ({link_collect1: None,
                       link_collect2: None,
                       link_collect3: None},
                      {footnote1: None,
                       footnote2: None})
#══════════════════════════════════════════════════════════════════════════════
# Header
@pytest.mark.parametrize("args,expected", [
    (('yaml', 'test'),  '---\ntest\n---'),
    (('toml', 'test'),  '+++\ntest\n+++'),
    (('json', 'test'),  ';;;\ntest\n;;;'),
    (('php', 'test'),   '---php\ntest\n---')])
def test_header_str(args, expected):
    assert str(md._process_header(*args)) == expected
#══════════════════════════════════════════════════════════════════════════════
# _pad
def test_pad_raises_valueerror():
    with pytest.raises(ValueError):
        list(md._pad(['a', 'b'], [3, 3], [md.LEFT, 'left'])) # type: ignore
#══════════════════════════════════════════════════════════════════════════════
# _markers
def test_markers():
    for style in md.TextStyle:
        assert style in md._markers
