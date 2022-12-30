'''Unittests for limesqueezer'''
#%%═════════════════════════════════════════════════════════════════════
# IMPORT

import os
import pathlib
import unittest

PATH_TESTS = pathlib.Path(__file__).parent
PATH_REPO = PATH_TESTS.parent
# First item in src should be the package
PATH_SRC = next((PATH_REPO / 'src').glob('*'))
#%%═════════════════════════════════════════════════════════════════════
# TEST CASES
class Unittests(unittest.TestCase):
    #═══════════════════════════════════════════════════════════════════
    def test_does_it_import(self):
        import yamdog as yg
#═══════════════════════════════════════════════════════════════════════
def unittests(verbosity: int = 2) -> unittest.TestResult:
    return unittest.TextTestRunner(verbosity = verbosity).run(unittest.makeSuite(Unittests))
#═══════════════════════════════════════════════════════════════════════
def typing(shell: bool = False) -> tuple[str, str, int]:
    args = [str(PATH_SRC), '--config-file', str(PATH_TESTS / "mypy.ini")]
    if shell:
        os.system(f'mypy {" ".join(args)}')
    else:
        from mypy import api as mypy
        return mypy.run(args)