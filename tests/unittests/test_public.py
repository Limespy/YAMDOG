import pytest
import yamdog as md
from yamdog import _API
#══════════════════════════════════════════════════════════════════════════════
# Text
@pytest.mark.parametrize("args,expected", [
    (('',),                 ''),
    (('test',{md.BOLD}), '**test**'),
    (('test',{md.ITALIC}), '*test*'),
    (('test',{md.STRIKETHROUGH}), '~~test~~'),
    (('test',set(), md.SUPERSCRIPT), '^test^'),
    (('test',set(), md.SUBSCRIPT), '~test~'),
    (('test',{md.HIGHLIGHT}), '==test=='),
    (('test',{md.BOLD, md.ITALIC}), '***test***')
])
def test_text_str(args, expected):
    assert str(md.Text(*args)) == expected
#──────────────────────────────────────────────────────────────────────────────
def test_text_invalid_style():
    with pytest.raises(TypeError):
        md.Text('test', {'test'}) # type: ignore
#──────────────────────────────────────────────────────────────────────────────
def test_text_superscrip_subscipt_not_TextLevel_raises():
    with pytest.raises(TypeError):
        md.Text('test', set(), 'subscript') # type: ignore
#──────────────────────────────────────────────────────────────────────────────
def test_text_style_edit():
    text = md.Text('test')
    assert not text.style
    assert md.BOLD in text.bold().style
    assert md.BOLD not in text.unbold().style
    assert not text.style
    assert md.ITALIC in text.italicize().style
    assert md.ITALIC not in text.unitalicize().style
    assert not text.style
    assert md.STRIKETHROUGH in text.strike().style
    assert md.STRIKETHROUGH not in text.unstrike().style
    assert not text.style
    assert md.HIGHLIGHT in text.highlight().style
    assert md.HIGHLIGHT not in text.unhighlight().style
    assert not text.style
    text.superscribe()
    assert text.subscribe().level == md.SUBSCRIPT
    assert text.superscribe().level == md.SUPERSCRIPT
    assert text.normalise().level == md.NORMAL
    text.bold().italicize().highlight()
    assert not text.clear().style
#══════════════════════════════════════════════════════════════════════════════
# Paragraph
@pytest.mark.parametrize("args,expected", [
    (tuple(),                ''),
    (([],),                  ''),
    (([],''),                ''),
    ((['test'],),            'test'),
    ((['test', 'item'],),    'testitem'),
    ((['test'],' '),         'test'),
    ((['test', 'item'],' '), 'test item'),
    (([' test'],), ' test'),
    ((['''
          test
       '''],), 'test')
])
def test_paragraph_str(args, expected):
    assert str(md.Paragraph(*args)) == expected
#──────────────────────────────────────────────────────────────────────────────
def test_paragraph_iadd_inline():
    paragraph = md.Paragraph()
    text = md.Text('test', {md.BOLD})
    paragraph += text
    assert paragraph.content[0] == text
#──────────────────────────────────────────────────────────────────────────────
def test_paragraph_iadd_paragraph():
    paragraph1 = md.Paragraph(['test'])
    paragraph2 = md.Paragraph(['case'])
    paragraph1 += paragraph2
    assert paragraph1 == md.Paragraph(['test', 'case'])
#──────────────────────────────────────────────────────────────────────────────
def test_paragraph_iadd_with_not_InlineElement_or_Paragraph_raises_TypeError():
    with pytest.raises(TypeError):
        paragraph = md.Paragraph(['test'])
        paragraph += 'test'
#══════════════════════════════════════════════════════════════════════════════
# Heading
@pytest.mark.parametrize("args,expected", [
    ((1, ''),                  '# '),
    ((2, 'test'),              '## test'),
    ((1,'test', False),        '# test'),
    ((1,'test', True),         'test\n===='),
    ((2,'test', True),         'test\n----'),
    ((3,'test', True),         '### test'),
    ((1,'test', False, True),  '# test'),
    ((1,'test', False, False), '# test <!-- omit in toc -->'),
    ((1,'test', True, False),  'test <!-- omit in toc -->\n====')
])
def test_heading_str(args, expected):
    assert str(md.Heading(*args)) == expected
#──────────────────────────────────────────────────────────────────────────────
def test_heading_level_0_raises_valueerror():
    with pytest.raises(ValueError):
        md.Heading(0, 'test')
#══════════════════════════════════════════════════════════════════════════════
# Link
@pytest.mark.parametrize('args1,args2',
                         (((1, 2), (1, 2)),
                          ((1, 2), ('1', 2)),
                          ((1, 2, 3), (1, 2, 3))))
def test_Link_same_hash(args1, args2):
    assert hash(md.Link(*args1)) == hash(md.Link(*args2))
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize('args1,args2',
                         (((1, 1), (1, 2)),
                          ((1, 2, 1), (1, 2, 3))))
def test_Link_different_hash(args1, args2):
    assert hash(md.Link(*args1)) != hash(md.Link(*args2))
#──────────────────────────────────────────────────────────────────────────────
def test_Link_index_init_raises():
    with pytest.raises(TypeError):
        md.Link('Text', 'doge.png', 'Title', 1) # type: ignore
#══════════════════════════════════════════════════════════════════════════════
# Listing
@pytest.mark.parametrize("args,expected", [
    ((md.ORDERED, [1, 2]), '1. 1\n2. 2'),
    ((md.UNORDERED, [1, 2]), '- 1\n- 2'),
    ((md.DEFINITION, [1, 2]), ': 1\n: 2'),
])
def test_Listing_str(args, expected):
    assert str(md.Listing(*args)) == expected
#══════════════════════════════════════════════════════════════════════════════
# Checkbox
@pytest.mark.parametrize("args,expected", [
    ((True, 'test'), '[x] test'),
    ((False, 'test'), '[ ] test')
])
def test_Checkbox_str(args, expected):
    assert str(md.Checkbox(*args)) == expected
#──────────────────────────────────────────────────────────────────────────────
def test_Checkbox_add_raises_type_error():
    with pytest.raises(TypeError):
        md.Checkbox(True, 'test') + md.Checkbox(False, 'test')
#══════════════════════════════════════════════════════════════════════════════
# make_checklist
def test_make_cheklist_return_listing():
    assert isinstance(md.make_checklist([(True, 'test')]), md.Listing)
#──────────────────────────────────────────────────────────────────────────────
def test_make_checklist_return_correct_listing_style():
    assert md.make_checklist([(True, 'test')]).style == md.UNORDERED
#──────────────────────────────────────────────────────────────────────────────
def test_make_checklist_return_correct_listing_style_with_multiple():
    data = [(True, 'test'), (False, 'test')]
    assert list(md.make_checklist(data)) == [md.Checkbox(*args) for args in data]
#══════════════════════════════════════════════════════════════════════════════
# Table
@pytest.mark.parametrize("args,expected_pretty,expected_compact", [
    ((['a', 'b', 'c'], [[1, 2, 3333],(4, 5, 6, 7)], [md.LEFT, md.CENTER, md.RIGHT]),
     '''
| a   |  b  |    c |     |
| :-- | :-: | ---: | --: |
| 1   |  2  | 3333 |     |
| 4   |  5  |    6 |   7 |''',
     '''
a|b|c|
:--|:-:|--:|--:
1|2|3333|
4|5|6|7'''),
])
def test_Table_str(args, expected_pretty, expected_compact):
    assert str(md.Table(*args)) == expected_pretty.strip()
    assert str(md.Table(*args, compact = True)) == expected_compact.strip() # type: ignore
#──────────────────────────────────────────────────────────────────────────────
def test_Table_alignment_fill():
    assert str(md.Table(['a', 'b'], [[1, 2]])) == '| a   | b   |\n| :-- | :-- |\n| 1   | 2   |'
#──────────────────────────────────────────────────────────────────────────────
def test_Table_append():
    table = md.Table(['a', 'b'], [[1, 2]])
    table.append([3, 4])
    assert table.content == [[1,2], [3,4]]
    with pytest.raises(TypeError):
        table.append(1) # type: ignore
#══════════════════════════════════════════════════════════════════════════════
# Address
def test_Address_str():
    assert str(md.Address('test')) == '<test>'
#══════════════════════════════════════════════════════════════════════════════
# Emoji
def test_Emoji_str():
    assert str(md.Emoji('test')) == ':test:'
#══════════════════════════════════════════════════════════════════════════════
# Math
@pytest.mark.parametrize("args,expected", [
    (('',),                  '$$'),
    (('test',),              '$test$'),
    (('test',md.GITHUB),     '$test$'),
    (('test',md.GITLAB),     '$`test`$')
])
def test_Math_str(args, expected):
    assert str(md.Math(*args)) == expected
#──────────────────────────────────────────────────────────────────────────────
def test_Math_invalid_flavour():
    with pytest.raises(ValueError):
        str(md.Math('test', md.PYPI))
#══════════════════════════════════════════════════════════════════════════════
# MathBlock
@pytest.mark.parametrize("args,expected", [
    (('',),                  '$$\n\n$$'),
    (('test',),              '$$\ntest\n$$'),
    (('test',md.GITHUB),     '$$\ntest\n$$'),
    (('test',md.GITLAB),     '```math\ntest\n```')
])
def test_MathBlock_str(args, expected):
    assert str(md.MathBlock(*args)) == expected
#──────────────────────────────────────────────────────────────────────────────
def test_mathblock_invalid_flavour():
    with pytest.raises(ValueError):
        str(md.MathBlock('test', md.PYPI))
#══════════════════════════════════════════════════════════════════════════════
# HRule
def test_hrule_str():
    assert str(md.HRule()) == '---'
#══════════════════════════════════════════════════════════════════════════════
# Code
@pytest.mark.parametrize("args,expected", [
    (('',),                  '``'),
    (('test',),              '`test`')
])
def test_code_str(args, expected):
    assert str(md.Code(*args)) == expected
#══════════════════════════════════════════════════════════════════════════════
# CodeBlock
@pytest.mark.parametrize("args,expected", [
    (('',),             '```\n\n```'),
    (('',),             '```\n\n```'),
    (('test','py'), '```py\ntest\n```'),
    ((md.CodeBlock('test', 'py'), 'py'), '````py\n```py\ntest\n```\n````')
])
def test_codeblock_str(args, expected):
    assert str(md.CodeBlock(*args)) == expected
#──────────────────────────────────────────────────────────────────────────────
def test_CodeBlock_tics_init_raises():
    with pytest.raises(TypeError):
        md.CodeBlock('python', 'a = 1', 1) # type: ignore
#══════════════════════════════════════════════════════════════════════════════
# QuoteBlock
@pytest.mark.parametrize("args,expected", [
    (('',),             '> '),
    (('1',), '> 1'),
    (('1\n2',), '> 1\n> 2')
])
def test_QuoteBlock_str(args, expected):
    assert str(md.QuoteBlock(*args)) == expected
#══════════════════════════════════════════════════════════════════════════════
# Image
@pytest.mark.parametrize("args,expected", [(('',),   '![]()'),
                                           (('',''), '![]()'),
                                           (('',''), '![]()'),
                                           ((2,1),   '![1](2)'),])
def test_Image_str(args, expected):
    assert str(md.Image(*args)) == expected
#══════════════════════════════════════════════════════════════════════════════
# Document
@pytest.mark.parametrize("args", [tuple(),
                                  ([],),
                                  (['test'],),
                                  (['test', 'item'],),
                                  (['test\n', 'item'],),
                                  (['test\n', '    item'],)])
def test_Document_str_simple(args):
    if len(args) == 0:
        expected = []
    elif len(args) >= 1:
        expected = [_API._sanitise_str(item).strip()
                    if isinstance(item, str) else str(item)
                    for item in args[0]]
    if len(args) == 2:
        expected.insert(0, _API._process_header(*args[1]))

    assert str(md.Document(*args)) == '\n\n'.join(expected)
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("args", [(['test'], ('yaml', 'test')),
                                  (['test'], ('toml', 'test')),
                                  (['test'], ('json', 'test')),
                                  (['test'], ('php', 'test'))])
def test_Document_str_header(args):

    expected = [_API._process_header(*args[1])]
    expected += [_API._sanitise_str(item) if isinstance(item, str) else str(item)
                    for item in args[0]]

    assert str(md.Document(*args)) == '\n\n'.join(expected)
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("args", [([], ('yaml',)),
                                  ([], ('toml', 'test', 'test'))])
def test_Document_header_invalid(args):
    with pytest.raises(TypeError):
        md.Document(*args)
#──────────────────────────────────────────────────────────────────────────────
def test_Document_with_TOC_and_non_str_Heading_valid():
    str(md.Document([md.TOC(), md.Heading(1, 1)]))
#──────────────────────────────────────────────────────────────────────────────
def test_Document_str_footnotes():
    footnote1 = md.Footnote('a')
    footnote2 = md.Footnote('b')
    doc = md.Document([footnote1, footnote2, footnote1])
    expected = [f'[^1]', f'[^2]', f'[^1]']
    expected += [f'[^1]: {footnote1.content}\n[^2]: {footnote2.content}']
    assert str(doc) == '\n\n'.join(expected)
#──────────────────────────────────────────────────────────────────────────────
def test_Document_footnote_index_init_raises():
    with pytest.raises(TypeError):
        md.Footnote('test', 1) # type: ignore
#──────────────────────────────────────────────────────────────────────────────
def test_Document_str_references():
    link0 = md.Link('no', 'no')
    link1 = md.Link('simple', 'url1', 'title1')
    link2 = md.Link('simple', 'url2', 'title2')
    link3 = md.Link('different text', 'url1', 'title1')
    doc = md.Document([link0, link1, link2, link3])
    expected = [str(link0),
                f'[{link1.content}][1]',
                f'[{link2.content}][2]',
                f'[{link3.content}][1]']
    expected += [f'[1]: <{link1.target}> "{link1.title}"\n[2]: <{link2.target}> "{link2.title}"']
    assert link1.target == link3.target and link1.title == link3.title
    assert str(doc) == '\n\n'.join(expected)
#──────────────────────────────────────────────────────────────────────────────
def test_Document_toc():
    headings = [md.Heading(i, f'h{i}') for i in range(1,6,1)]
    # creating example
    reftext, ref = _API._heading_ref_texts(headings[3].content) # level up to 4

    listing = md.Listing(md.UNORDERED, [md.Link(reftext, ref)])
    for heading in reversed(headings[:3]):
        reftext, ref = _API._heading_ref_texts(heading.content)
        listing = md.Listing(md.UNORDERED, [(md.Link(reftext, ref), listing)])
    # Testing duplicate headers
    reftext, ref = _API._heading_ref_texts(headings[0].content)
    listing.append(md.Link(reftext, ref + '1')) # type: ignore
    headings.append(headings[0])
    assert str(md.Document([md.TOC()] + headings)).startswith(str(listing))
#──────────────────────────────────────────────────────────────────────────────
def test_Document_iadd_element():
    document = md.Document(['test'])
    text = md.Text('case', {md.BOLD})
    document += text
    assert document == md.Document(['test', text])
#──────────────────────────────────────────────────────────────────────────────
def test_Document_iadd_document():
    document1 = md.Document(['test'])
    document2 = md.Document(['case'])
    document1 += document2
    assert document1 == md.Document(['test', 'case'])
