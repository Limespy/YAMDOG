'''Unittests for limesqueezer'''
#%%═════════════════════════════════════════════════════════════════════
# IMPORT
import os
import pathlib

PATH_TESTS = pathlib.Path(__file__).parent
PATH_UNITTESTS = PATH_TESTS / 'unittests'
PATH_REPO = PATH_TESTS.parent
# First item in src should be the package
PATH_SRC = next((PATH_REPO / 'src').glob('*'))
#%%═════════════════════════════════════════════════════════════════════
# TEST CASES

#══════════════════════════════════════════════════════════════════════════════
def unittests(verbosity: int = 2) -> None:
    import pytest
    CWD = pathlib.Path.cwd()
    os.chdir(str(PATH_UNITTESTS))
    output = pytest.main([])
    os.chdir(str(CWD))
    return output
#══════════════════════════════════════════════════════════════════════════════
def typing(shell: bool = False) -> tuple[str, str, int]:
    args = [str(PATH_SRC), '--config-file', str(PATH_TESTS / "mypy.ini")]
    if shell:
        os.system(f'mypy {" ".join(args)}')
    else:
        from mypy import api as mypy
        return mypy.run(args)
#══════════════════════════════════════════════════════════════════════════════
def comparison():
    import compare
    compare.main()
#══════════════════════════════════════════════════════════════════════════════
def performance():
    import yamdog as md
    from yamdog.API import _sanitise_str

    from pydantic import BaseModel
    from pympler.asizeof import asizeof

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
    paragraph_dc = Paragraph_dc(**kwargs)
    paragraph_pyd = Paragraph_pyd(**kwargs)
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