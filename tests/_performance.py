import pathlib
import re
from timeit import timeit

import yamdog as md
from _performance_setup import ParagraphDC
from _performance_setup import ParagraphPyd
from pympler.asizeof import asizeof # type: ignore

PATH_BASE = pathlib.Path(__file__).parent
PATH_SETUP = PATH_BASE / '_performance_setup.py'
SETUP = re.split(r'#%%.+\n', PATH_SETUP.read_text('utf8'))[1:]

def main():
    kwargs = {'content': ['a','b','c'],
                'separator': '_'}
    n_runs = 1000
    classes = {'Dataclass': ParagraphDC,
               'Validated DC': md.Paragraph,
               'Pydantic': ParagraphPyd}
    table = []
    for setup, (name, cls)  in zip(SETUP, classes.items()):
        table.append((name,
                      asizeof(cls(**kwargs)),
                      timeit(f"{cls.__name__}(**kwargs)",
                             setup = setup, number = n_runs)*1e6 / n_runs))


    table = [[row[0], str(row[1]), f'{row[2]:.2f}'] for row in table]

    widths = [0] * len(table[0])
    for row in table:
        for index, cell in enumerate(row):
            if (cell_len := len(cell)) > widths[index]:
                widths[index] = cell_len
    print('\t\tsize\tcreation time [us]')
    for row in table:
        print(f'{row[0]:<{widths[0]}}\t{row[1]:<{widths[1]}}\t{row[2]:<{widths[2]}}')
