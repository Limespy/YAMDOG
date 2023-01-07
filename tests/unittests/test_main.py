import yamdog as md

import pytest

@pytest.mark.parametrize("args,expected", [
    (('',),                 ''),
    (('test',{md.BOLD}), '**test**')
])
def test_text(args, expected):
    assert str(md.Text(*args)) == expected

@pytest.mark.parametrize("args,expected", [
    (tuple(),                       ''),
    (([],),                         ''),
    ((['test'],),                   'test'),
    ((['test', 'item'],),           'test\n\nitem'),
    ((['test\n', 'item'],),         'test\n\nitem'),
    ((['test\n', '    item'],),     'test\n\nitem'),
    ((['test'], ('yaml', 'test')),  '---\ntest\n---\n\ntest'),
    ((['test'], ('toml', 'test')),  '+++\ntest\n+++\n\ntest'),
    ((['test'], ('json', 'test')),  ';;;\ntest\n;;;\n\ntest'),
    ((['test'], ('php', 'test')),   '---php\ntest\n---\n\ntest')
])
def test_initialising_document(args, expected):
    assert str(md.Document(*args)) == expected

@pytest.mark.parametrize("args,expected", [
    (tuple(),                   ''),
    (([],),                    ''),
    (([],''),                   ''),
    ((['test'],),                   'test'),
    ((['test', 'item'],),           'testitem'),
    ((['test'],' '),                'test'),
    ((['test', 'item'],' '),        'test item'),
])
def test_initialising_paragraph(args, expected):
    assert str(md.Paragraph(*args)) == expected