'''Unittests for public interface of the package.
Classes are sorted alphabetically and related functions'''
import itertools
from pprint import pprint

import pytest
import yamdog as md
from yamdog import _API
#═════════════════════════════════════════════════════════════════════════════
class Test_Checkbox:
    @pytest.mark.parametrize("args,expected", [
        ((True, 'test'), '[x] test'),
        ((False, 'test'), '[ ] test')
    ])
    def test_str(self, args, expected):
        assert str(md.Checkbox(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_add_raises_type_error(self):
        with pytest.raises(TypeError):
            md.Checkbox(True, 'test') + md.Checkbox(False, 'test')
#═════════════════════════════════════════════════════════════════════════════
# Code
@pytest.mark.parametrize("args,expected", [
    (('',),                  '``'),
    (('test',),              '`test`')
])
def test_Code_str(args, expected):
    assert str(md.Code(*args)) == expected
#═════════════════════════════════════════════════════════════════════════════
class Test_CodeBlock:
    @pytest.mark.parametrize("args,expected", [
        (('',),             '```\n\n```'),
        (('',),             '```\n\n```'),
        (('a=1','py'),      '```py\na=1\n```'),
        (('```','py'),      '````py\n```\n````'),
        ((md.CodeBlock('a=1', 'py'), 'py'), ('````py\n'
                                              '```py\n'
                                              'a=1\n'
                                              '```\n'
                                              '````')),
        ((md.CodeBlock('```', 'py'), 'py'), ('`````py\n'
                                             '````py\n'
                                             '```\n'
                                             '````\n'
                                             '`````')),
        ((md.Paragraph(['```',
                       md.CodeBlock('```', 'py')],
                       '\n'), 'py'), ('`````py\n'
                                                           '```\n'
                                                           '````py\n'
                                                           '```\n'
                                                           '````\n'
                                                           '`````'))
    ])
    def test_str(self, args, expected):
        assert str(md.CodeBlock(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_tics_init_raises(self):
        with pytest.raises(TypeError):
            md.CodeBlock('python', 'a = 1', 1) # type: ignore
#═════════════════════════════════════════════════════════════════════════════
class Test_Document:

    def test_str_no_args(self):
        assert str(md.Document()) == ''
    #─────────────────────────────────────────────────────────────────────────
    def test_str_no_empty_list(self):
        assert str(md.Document([])) == ''
    #─────────────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("args", [(['test'],),
                                      (['test', 'item'],),
                                      (['test\n', 'item'],),
                                      (['test\n', '    item'],)])
    def test_str_simple(self, args):
        expected = [_API._sanitise_str(item).strip()
                    if isinstance(item, str) else str(item)
                    for item in args[0]]
        assert str(md.Document(*args)) == '\n\n'.join(expected)
    #─────────────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("args", [(['test'], ('yaml', 'test')),
                                    (['test'], ('toml', 'test')),
                                    (['test'], ('json', 'test')),
                                    (['test'], ('php', 'test'))])
    def test_str_header(self, args):

        expected = [_API._process_header(*args[1])]
        expected.extend(_API._sanitise_str(item) if isinstance(item, str)
                        else str(item) for item in args[0])

        assert str(md.Document(*args)) == '\n\n'.join(expected)
    #─────────────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("args", [([], ('yaml',)),
                                    ([], ('toml', 'test', 'test'))])
    def test_header_invalid(self, args):
        with pytest.raises(TypeError):
            md.Document(*args)
    #─────────────────────────────────────────────────────────────────────────
    def test_with_TOC_and_non_str_Heading_valid(self):
        str(md.Document([md.TOC(), md.Heading(1, 1)]))
    #─────────────────────────────────────────────────────────────────────────
    footnote = md.Footnote('footnote')
    #─────────────────────────────────────────────────────────────────────────
    def test_str_footnote(self):
        assert str(md.Document([self.footnote])) == ('[^1]\n'
                                                               '\n'
                                                               '[^1]: footnote')
    #─────────────────────────────────────────────────────────────────────────
    def test_str_footnotes(self):
        footnote2 = md.Footnote('b')
        doc = md.Document([self.footnote, footnote2, self.footnote])
        assert str(doc) == ('[^1]\n'
                            '\n'
                            '[^2]\n'
                            '\n'
                            '[^1]\n'
                            '\n'
                            f'[^1]: {self.footnote.content}\n'
                            f'[^2]: {footnote2.content}')
    #─────────────────────────────────────────────────────────────────────────
    def test_nested_footnotes(self):
        nested_footnote = md.Footnote(self.footnote)
        assert str(md.Document([nested_footnote])) == ('[^1]\n'
                                                       '\n'
                                                       '[^1]: [^2]\n'
                                                       '[^2]: footnote')
    #─────────────────────────────────────────────────────────────────────────
    def test_self_referencing_footnote(self):
        footnote = md.Footnote('dummy')
        footnote.content = md.Paragraph(['See ', footnote])
        assert str(md.Document([footnote])) == ('[^1]\n'
                                                '\n'
                                                '[^1]: See [^1]')
    #─────────────────────────────────────────────────────────────────────────
    def test_footnote_index_init_raises_TypeError(self):
        with pytest.raises(TypeError):
            md.Footnote('test', 1) # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def test_str_references(self):
        link0 = md.Link('no', 'no')
        link1 = md.Link('url1', 'content', 'title1')
        # Same text in two different objects
        link2 = md.Link('url1', 'content', 'title1')
        link3 = md.Link('url2', 'content', 'title2')
        link4 = md.Link('url1', 'different text', 'title1')
        doc = md.Document([link0, link1, link2, link3, link4])
        expected = [str(link0),
                    f'[{link1.content}][1]',
                    f'[{link2.content}][1]',
                    f'[{link3.content}][2]',
                    f'[{link4.content}][1]']
        expected.append(f'[1]: <{link1.target}> "{link1.title}"\n'
                        f'[2]: <{link3.target}> "{link3.title}"')
        expected_str = '\n\n'.join(expected)
        pprint(expected_str)
        doc_str = str(doc)
        pprint(doc_str)
        assert link1.target == link4.target
        assert link1.title == link4.title
        assert doc_str == expected_str
    #─────────────────────────────────────────────────────────────────────────
    def test_a_reference_in_a_footnote(self):
        link = md.Link('target', 'content', 'title')
        footnote = md.Footnote(link)
        assert str(md.Document([footnote])) == ('[^1]\n'
                                                '\n'
                                                '[^1]: [content](target)\n'
                                                '\n'
                                                '[1]: <target> "title"')
    #─────────────────────────────────────────────────────────────────────────
    # Not supported by markdown viewers
    # def test_footnote_in_paragraph_in_reference(self):
    #     paragraph = md.Paragraph(['text', self.footnote])
    #     link = md.Link(, 'target', 'title')

    #     assert str(md.Document([link])) == ('[[^1]](target)\n'
    #                                         '\n'
    #                                         '[^1]: footnote\n'
    #                                         '\n'
    #                                         '[1]: <target> "title"')
    #─────────────────────────────────────────────────────────────────────────
    def test_TOC(self):
        headings = [md.Heading(f'h{i}', i) for i in range(1,6,1)]
        # creating example
        reftext, ref = _API._heading_ref_texts(headings[3].content) # level up to 4

        listing = md.Listing(md.UNORDERED, [md.Link(ref, reftext)])
        for heading in reversed(headings[:3]):
            reftext, ref = _API._heading_ref_texts(heading.content)
            listing = md.Listing(md.UNORDERED, [(md.Link(ref, reftext), listing)])
        # Testing duplicate headers
        reftext, ref = _API._heading_ref_texts(headings[0].content)
        listing.append(md.Link(ref + '1', reftext)) # type: ignore
        headings.append(headings[0])
        assert str(md.Document([md.TOC()] + headings)).startswith(str(listing))
    #─────────────────────────────────────────────────────────────────────────
    def test_iadd_element(self):
        document = md.Document(['test'])
        text = md.Text('case', {md.BOLD})
        document += text
        assert document == md.Document(['test', text])
    #─────────────────────────────────────────────────────────────────────────
    def test_iadd_document(self):
        document1 = md.Document(['test'])
        document2 = md.Document(['case'])
        document1 += document2
        assert document1 == md.Document(['test', 'case'])
#══════════════════════════════════════════════════════════════════════════════
# Element
@pytest.mark.parametrize('element1, element2',
                         itertools.permutations((md.Heading('test', 1),
                                                 md.Link('test', 'case'),
                                                 md.Quote('quote'),
                                                 md.Image('path'),
                                                 md.CodeBlock('code', 'python'),
                                                 md.HRule(),
                                                 md.MathBlock('a = b^2')), 2))
def test_Element_add(element1, element2):
    assert element1 + element2 == md.Document([element1, element2])
#═════════════════════════════════════════════════════════════════════════════
# Emoji
def test_Emoji_str():
    assert str(md.Emoji('test')) == ':test:'
#═════════════════════════════════════════════════════════════════════════════
class Test_Heading:
    @pytest.mark.parametrize("args, expected", [
        (('', 1),                   '# '),
        (('test', 2),               '## test'),
        (('test', 1, False),        '# test <!-- omit in toc -->'),
        (('test', 1, True),         '# test'),
        (('test', 1, True, True),   'test\n===='),
        (('test', 2, True, True),   'test\n----'),
        (('test', 3, True, True),   '### test'),
        (('test', 1, True, False),  '# test'),
        (('test', 1, False, False), '# test <!-- omit in toc -->'),
        (('test', 1, False, True),  'test <!-- omit in toc -->\n====')
    ])
    def test_str(self, args, expected):
        assert str(md.Heading(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_level_0_raises_ValueError(self):
        with pytest.raises(ValueError):
            md.Heading('test', 0)
    #─────────────────────────────────────────────────────────────────────────
    def test_level_7_raises_ValueError(self):
        with pytest.raises(ValueError):
            md.Heading('test', 7)
#═════════════════════════════════════════════════════════════════════════════
# HRule
def test_hrule_str():
    assert str(md.HRule()) == '---'
#═════════════════════════════════════════════════════════════════════════════
# Image
@pytest.mark.parametrize("args,expected", [(('',),   '![image]()'),
                                           (('',''), '![]()'),
                                           (('path',''), '![](path)'),
                                           ((2,1),   '![1](2)'),])
def test_Image_str(args, expected):
    assert str(md.Image(*args)) == expected
#═════════════════════════════════════════════════════════════════════════════
class Test_Link:
    def test_target_only(self):
        assert str(md.Link('target')) == '<target>'
    #─────────────────────────────────────────────────────────────────────────
    def test_target_and_content(self):
        assert str(md.Link('target', 'content')) == '[content](target)'
    #─────────────────────────────────────────────────────────────────────────
    def test_index_init_raises(self):
        with pytest.raises(TypeError):
            md.Link('Text', 'doge.png', 'Title', 1) # type: ignore
#═════════════════════════════════════════════════════════════════════════════
class Test_Listing:
    @pytest.mark.parametrize("args, expected", [
        ((md.ORDERED, [1, 2]), '1. 1\n2. 2'),
        ((md.UNORDERED, [1, 2]), '- 1\n- 2'),
        ((md.DEFINITION, [1, 2]), ': 1\n: 2'),
    ])
    def test_str(self, args, expected):
        assert str(md.Listing(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_multiline_str(self):
        assert str(md.Listing(md.ORDERED, ['a\nb'])) == ('1. a\n'
                                                         '   b')
    #─────────────────────────────────────────────────────────────────────────
    def test_nested(self):
        inner_listing = md.Listing(md.UNORDERED, ('a', 'b'))
        listing = md.Listing(md.ORDERED, (1, 2, (3, inner_listing)))
        assert str(listing) == ('1. 1\n'
                                '2. 2\n'
                                '3. 3\n'
                                f'{_API._INDENT}- a\n'
                                f'{_API._INDENT}- b')
#═════════════════════════════════════════════════════════════════════════════
class Test_make_checklist:
    arg = [(True, 'testtrue'), (False, 'testfalse')]
    @pytest.fixture
    def checklist(self) -> md.Listing:
        return md.make_checklist(self.arg)
    #─────────────────────────────────────────────────────────────────────────
    def test_return_listing(self, checklist):
        assert isinstance(checklist, md.Listing)
    #─────────────────────────────────────────────────────────────────────────
    def test_return_correct_listing_style(self, checklist):
        assert checklist.style == md.UNORDERED
    #─────────────────────────────────────────────────────────────────────────
    def test_return_correct_listing_style_with_multiple(self, checklist):
        assert list(checklist) == [md.Checkbox(*args) for args in self.arg]
#═════════════════════════════════════════════════════════════════════════════
class Test_Math:
    @pytest.mark.parametrize("args,expected", [
        (('',),                  '$$'),
        (('test',),              '$test$'),
        (('test',md.GITHUB),     '$test$'),
        (('test',md.GITLAB),     '$`test`$')
    ])
    def test_str(self, args, expected):
        assert str(md.Math(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_invalid_flavour(self):
        with pytest.raises(ValueError):
            str(md.Math('test', md.PYPI))
#═════════════════════════════════════════════════════════════════════════════
class Test_MathBlock:
    @pytest.mark.parametrize("args,expected", [
        (('',),                  '$$\n\n$$'),
        (('test',),              '$$\ntest\n$$'),
        (('test',md.GITHUB),     '$$\ntest\n$$'),
        (('test',md.GITLAB),     '```math\ntest\n```')
    ])
    def test_str(self, args, expected):
        assert str(md.MathBlock(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_invalid_flavour(self):
        with pytest.raises(ValueError):
            str(md.MathBlock('test', md.PYPI))
#═════════════════════════════════════════════════════════════════════════════
class Test_Paragraph:
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
    def test_str(self, args, expected):
        assert str(md.Paragraph(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_iadd_inline(self):
        paragraph = md.Paragraph()
        text = md.Text('test', {md.BOLD})
        paragraph += text
        assert paragraph.content[0] == text
    #─────────────────────────────────────────────────────────────────────────
    def test_iadd_paragraph(self):
        paragraph1 = md.Paragraph(['test'])
        paragraph2 = md.Paragraph(['case'])
        paragraph1 += paragraph2
        assert paragraph1 == md.Paragraph(['test', 'case'])
    #─────────────────────────────────────────────────────────────────────────
    def test_iadd_with_not_InlineElement_or_Paragraph_raises_TypeError(self):
        with pytest.raises(TypeError):
            paragraph = md.Paragraph(['test'])
            paragraph += 'test'
#═════════════════════════════════════════════════════════════════════════════
# Quote
@pytest.mark.parametrize("args, expected", [
    (('',),             '> '),
    (('1',), '> 1'),
    (('1\n2',), '> 1\n> 2')
])
def test_Quote_str(args, expected):
    assert str(md.Quote(*args)) == expected
#═════════════════════════════════════════════════════════════════════════════
class Test_Text:
    @pytest.mark.parametrize("args, expected", [
        (('',),                 ''),
        (('test',{md.BOLD}), '**test**'),
        (('test',{md.ITALIC}), '*test*'),
        (('test',{md.STRIKETHROUGH}), '~~test~~'),
        (('test',set(), md.SUPERSCRIPT), '^test^'),
        (('test',set(), md.SUBSCRIPT), '~test~'),
        (('test',{md.HIGHLIGHT}), '==test=='),
        (('test',{md.BOLD, md.ITALIC}), '***test***')
    ])
    def test_str(self, args, expected):
        assert str(md.Text(*args)) == expected
    #─────────────────────────────────────────────────────────────────────────
    def test_invalid_style(self):
        with pytest.raises(TypeError):
            md.Text('test', {'test'}) # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def test_superscrip_subscipt_not_TextLevel_raises(self):
        with pytest.raises(TypeError):
            md.Text('test', set(), 'subscript') # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def test_style_edit(self):
        text = md.Text('test')
        assert not text.style
        assert md.BOLD in text.bold().style
        assert md.BOLD not in text.unbold().style
        assert not text.style
        assert md.ITALIC in text.italicize().style
        assert md.ITALIC not in text.unitalicize().style
        assert not text.style
        assert md.STRIKETHROUGH in text.strikethrough().style
        assert md.STRIKETHROUGH not in text.unstrikethrough().style
        assert not text.style
        assert md.HIGHLIGHT in text.highlight().style
        assert md.HIGHLIGHT not in text.unhighlight().style
        assert not text.style
        text.superscribe()
        assert text.subscribe().level == md.SUBSCRIPT
        assert text.superscribe().level == md.SUPERSCRIPT
        assert text.normalise().level == md.NORMAL
        text.bold().italicize().highlight()
        assert not text.reset().style
#═════════════════════════════════════════════════════════════════════════════
class Test_Table:
    @pytest.mark.parametrize("args,expected_pretty,expected_compact", [
        ((['a', 'b', 'c'],
          [[1, 2, 3333],
           (4, 5, 6, 7)],
          [md.LEFT, md.CENTER, md.RIGHT]),
        '| a   |  b  |    c |     |\n'
        '| :-- | :-: | ---: | --: |\n'
        '| 1   |  2  | 3333 |     |\n'
        '| 4   |  5  |    6 |   7 |',
        'a|b|c|\n'
        ':--|:-:|--:|--:\n'
        '1|2|3333|\n'
        '4|5|6|7'),
    ])
    def test_str(self,args, expected_pretty, expected_compact):
        assert str(md.Table(*args)) == expected_pretty
        assert str(md.Table(*args, compact = True)) == expected_compact # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def test_alignment_fill(self):
        assert str(md.Table(['a', 'b'], [[1, 2]])) == ('| a   | b   |\n'
                                                       '| :-- | :-- |\n'
                                                       '| 1   | 2   |')
    #─────────────────────────────────────────────────────────────────────────
    def test_append(self):
        table = md.Table(['a', 'b'], [[1, 2]])
        table.append([3, 4])
        assert table.content == [[1,2], [3,4]]
        with pytest.raises(TypeError):
            table.append(1) # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def test_from_dict(self):
        dictionary = {'a': (1,2),
                      'b': (1,2,3)}
        assert str(md.Table.from_dict(dictionary)) == ('| a   | b   |\n' # type: ignore
                                                       '| :-- | :-- |\n'
                                                       '| 1   | 1   |\n'
                                                       '| 2   | 2   |\n'
                                                       '|     | 3   |')
