from time import perf_counter
from typing import Any

docname = 'Comparison'

heading1 = 'Comparing YANDOG and SnakeMD'

paragraph1 = '''
    This document is built one YAMDOG and on SnakeMD.
    Aim is to compare interface and performance.
    YAMDOG is based on'''

list1 = [
   'YAMDOG is based on use of small abjects',
   'SnakeMD'
] 

heading2 = 'Similarities'

link1 = ('YAMDOG', 'https://github.com/Limespy/YAMDOG')
link2 = ('SnakeMD', 'https://snakemd.therenegadecoder.com')

table1_header = ['first', 'second', 'third']
table1_body = [[1,2,3],
               [4,5,6]]

def build_yamdog_doc():
    import yamdog as md
    doc = md.Document()
    doc += md.Heading(1, heading1)
    doc += paragraph1
    doc += md.Listing(md.UNORDERED, list1)
    doc += md.Listing(md.ORDERED, [md.Link(*link1), md.Link(*link2)])
    doc += md.Table(table1_header, table1_body)
    doc += md.Table(table1_header, table1_body, (md.LEFT, md.CENTER, md.RIGHT))
    return doc

def build_snakemd_doc():
    import snakemd as md

    doc = md.Document(docname)

    doc.add_header(heading1)
    doc.add_paragraph(paragraph1)
    doc.add_unordered_list(list1)
    doc.add_element(md.MDList([md.InlineText(*link1),
                               md.InlineText(*link2)],
                              ordered = True))
    doc.add_table(table1_header, table1_body)
    doc.add_table(table1_header, table1_body, (md.Table.Align.LEFT,
                                               md.Table.Align.CENTER,
                                               md.Table.Align.RIGHT))
    return doc

def massive_table_yamdog():
    import yamdog as md



def timed(function, *args) -> tuple[Any, float]:
    t0 = perf_counter()
    output = function(*args)
    time_difference = perf_counter() - t0
    return output, time_difference

def main():
    snakemd_doc, t_snakemd = timed(build_snakemd_doc)
    yamdog_doc, t_yamdog = timed(build_yamdog_doc)

    print(t_yamdog)
    print(t_snakemd)
    t0 = perf_counter()
    str_yamdog = str(yamdog_doc)
    t_yamdog = perf_counter() - t0
    t0 = perf_counter()
    str_snakemd = str(snakemd_doc)
    t_snakemd = perf_counter() - t0
    t0 = perf_counter()
    str_yamdog = str(yamdog_doc)
    t_yamdog = perf_counter() - t0
    print(t_yamdog)
    print(t_snakemd)
    is_same = str_yamdog == str_snakemd
    print(is_same)
    print(str_yamdog)
    if not is_same:
        print('-'*60)
        print(str_snakemd)