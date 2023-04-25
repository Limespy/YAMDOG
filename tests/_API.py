'''Unittests for limesqueezer'''
#%%═════════════════════════════════════════════════════════════════════
# IMPORT
import os
import pathlib
import sys
from typing import Callable
from typing import NoReturn
from typing import Optional
from typing import Union

PATH_TESTS = pathlib.Path(__file__).parent
PATH_UNITTESTS = PATH_TESTS / 'unittests'
PATH_LINTCONFIG = PATH_TESTS / '.pylintrc'
PATH_REPO = PATH_TESTS.parent
# First item in src should be the package
PATH_SRC = next((PATH_REPO / 'src').glob('*'))
#%%═════════════════════════════════════════════════════════════════════
# TEST CASES

#══════════════════════════════════════════════════════════════════════════════
def unittests() -> None:
    import pytest
    CWD = pathlib.Path.cwd()
    os.chdir(str(PATH_UNITTESTS))
    pytest.main([])
    os.chdir(str(CWD))
    return None
#══════════════════════════════════════════════════════════════════════════════
def typing(shell: bool = True) -> Optional[tuple[str, str, int]]:
    args = [str(PATH_SRC), '--config-file', str(PATH_TESTS / "mypy.ini")]
    if shell:
        from mypy.main import main
        main(args = args)
    else:
        from mypy import api
        return api.run(args)
#══════════════════════════════════════════════════════════════════════════════
def lint() -> None:
    from pylint import lint
    lint.Run([str(PATH_SRC),
              f'--rcfile={str(PATH_LINTCONFIG)}',
              '--output-format=colorized',
              '--msg-template="{path}:{line}:{column}:{msg_id}:{symbol}\n'
                              '    {msg}"'])
#══════════════════════════════════════════════════════════════════════════════
def compare() -> None:
    import compare as _compare
    _compare.main()
#══════════════════════════════════════════════════════════════════════════════
def performance():
    import yamdog as md
    from yamdog._API import _sanitise_str

    from pydantic import BaseModel
    from pympler.asizeof import asizeof # type: ignore

    import sys
    from timeit import timeit

    Paragraph_dc = md.Paragraph

    class ElementPyd(BaseModel):
        def __add__(self, other):
            return md.Document([self, other])
    class IterableElementPyd(ElementPyd):
        #─────────────────────────────────────────────────────────────────────
        def _collect(self) -> tuple[dict, dict]:
            return _collect_iter(self.content)   # type: ignore
        #─────────────────────────────────────────────────────────────────────
        def __iter__(self):
            return iter(self.content)   # type: ignore
    class Paragraph_pyd(IterableElementPyd):
        content: list = []
        separator: str = ''
        #─────────────────────────────────────────────────────────────────────────
        def __str__(self) -> str:
            return self.separator.join(_sanitise_str(item) if isinstance(item, str)
                                    else str(item) for item in self.content)
        #─────────────────────────────────────────────────────────────────────────
        def __iadd__(self, other):
            if isinstance(other, md.InlineElement):
                self.content.append(other)
                return self
            elif isinstance(other, md.Paragraph):
                self.content += other.content
                return self
            else:
                raise TypeError(f"+= has not been implemented for Paragraph with object {repr(other)} type '{type(other).__name__}'")

    kwargs = {'content': ['a','b','c'],
              'separator': '_'}
    Paragraph_dc([], separator = '_')
    paragraph_dc = Paragraph_dc(**kwargs) # type: ignore
    paragraph_pyd = Paragraph_pyd(**kwargs) # type: ignore
    print(sys.getsizeof(paragraph_dc))
    print(sys.getsizeof(paragraph_pyd))
    print(asizeof(paragraph_dc))
    print(asizeof(paragraph_pyd))
    print(repr(paragraph_dc))
    print(repr(paragraph_pyd))
    time_dc = timeit("paragraph_dc(**kwargs)", setup = "import yamdog as md; paragraph_dc = md.Paragraph;kwargs = {'content': ['a','b','c'], 'separator': '_'}")
    print(time_dc)
    time_pyd = timeit("ParagraphPyd(**kwargs)", setup = '''

from pydantic import BaseModel
import yamdog as md

class ElementPyd(BaseModel):
    def __add__(self, other):
        return md.Document([self, other])
class IterableElementPyd(ElementPyd):
    #─────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return _collect_iter(self.content)   # type: ignore
    #─────────────────────────────────────────────────────────────────────
    def __iter__(self):
        return iter(self.content)   # type: ignore
class ParagraphPyd(IterableElementPyd):
    content: list = []
    separator: str = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return self.separator.join(_clean_string(item) if isinstance(item, str)
                                else str(item) for item in self.content)
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, other):
        if isinstance(other, md.InlineElement):
            self.content.append(other)
            return self
        elif isinstance(other, md.Paragraph):
            self.content += other.content
            return self
        else:
            raise TypeError(f"+= has not been implemented for Paragraph with object {repr(other)} type '{type(other).__name__}'")
kwargs = {'content': ['a','b','c'], 'separator': '_'}
''')
    print(time_pyd)
    time_dc = timeit("paragraph_dc(**kwargs)", setup = "import yamdog as md; paragraph_dc = md.Paragraph;kwargs = {'content': ['a','b','c'], 'separator': '_'}")
    print(time_dc)
#══════════════════════════════════════════════════════════════════════════════
TESTS: dict[str, Callable] = {function.__name__: function # type: ignore
                              for function in
                              (lint, unittests, compare, typing)}
def main(args: list[str] = sys.argv[1:]) -> Union[list, None, NoReturn]:
    if not args:
        return None
    if args[0] == '--all':
        return [test() for test in TESTS.values()]
    return [TESTS[arg[2:]]() for arg in args if arg.startswith('--')]
#══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    main()
