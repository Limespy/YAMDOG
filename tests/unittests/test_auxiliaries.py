import yamdog.API as md

from dataclasses import dataclass
import pytest
import typing

#══════════════════════════════════════════════════════════════════════════════
# clean_string
def test_string_cleaning():
    output = md._clean_string('''
            test text
            to check\tstring 
            cleaning.
            ''')
    assert output == 'test text to check string cleaning.'
#══════════════════════════════════════════════════════════════════════════════
# Element
@pytest.mark.parametrize("index,value", [
    (i, value) for i, value in enumerate(('s', 1, [], (1,), (1, 1.5), {1: 'a'}, 1, 1.5, 1.5))])
def test_element_validation(index, value):
    @dataclass
    class Cls(md.Element):
        Int: int
        Float: float
        Tuple: tuple
        Tuple2: tuple[int,int]
        Tuple3: tuple[int, int]
        Dict: dict[str, int]
        Iterable: typing.Iterable
        Optional: typing.Optional[int]
        Union: typing.Union[int, str]
        Any: typing.Any
        def __str__(self) -> str:
            return ''
    args = [1, 1.2, (1, 2), (1,2), (1,2), {'a', 1}, [1], None, 's', 's']
    args[index] = value
    with pytest.raises(TypeError):
        Cls(*args)
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
    assert str(md._Header(*args)) == expected
#══════════════════════════════════════════════════════════════════════════════
# _pad
def test_pad_raises_valueerror():
    with pytest.raises(ValueError):
        list(md._pad(['a', 'b'], [3, 3], [md.LEFT, 'left']))
#══════════════════════════════════════════════════════════════════════════════
# _markers
def test_markers():
    for style in md.TextStyle:
        assert style in md._markers

