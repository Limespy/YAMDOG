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
    results: dict[str, list] = {'header': ['Dataclass', 'Validated DC', 'Pydantic'],
                                'size': [],
                                'creation time': []}
    kwargs = {'content': ['a','b','c'],
                'separator': '_'}
    n_runs = 1000
    for setup_index, cls in enumerate((ParagraphDC,
                                       md.Paragraph,
                                       ParagraphPyd)):
        results['size'].append(asizeof(cls(**kwargs)))
        results['creation time'].append(timeit(f"{cls.__name__}(**kwargs)",
                                               setup = SETUP[setup_index],
                                               number = n_runs))

    print('\t\t\t' + '\t'.join(results["header"]))
    print('size [bytes]\t\t' + '\t\t'.join(str(s) for s in results["size"]))
    print('creation time [μs]\t' + '\t\t'.join(f'{s*1e6 / n_runs:.2f}' for s in results["creation time"]))
