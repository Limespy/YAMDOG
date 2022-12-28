'''Unittests for limesqueezer'''
#%%═════════════════════════════════════════════════════════════════════
# IMPORT

import os
import pathlib
import time
import unittest


PATH_TESTS = pathlib.Path(__file__).parent
PATH_REPO = PATH_TESTS.parent
# First item in src should be the package
PATH_SRC = next((PATH_REPO / 'src').glob('*'))

#%%═════════════════════════════════════════════════════════════════════
# AUXILIARIES
def f2zero_100(n: int) -> float:
    '''returns < 0 for values 0 to 100 and >0 for values > 100'''
    if round(n) != n: raise ValueError('Not whole number')
    if n < 0: raise ValueError('Input must be >= 0')
    return np.sqrt(n) - 10.01, True
#%%═════════════════════════════════════════════════════════════════════
def compressionaxis(x: np.ndarray, y: np.ndarray) -> int:
    if y.ndim == 1:
        return 0
    if y.shape[0] == len(x):
        return 0
    if y.shape[0] == len(x):
        return 1
#%%═════════════════════════════════════════════════════════════════════
# TEST CASES
class Unittests(unittest.TestCase):
    #═══════════════════════════════════════════════════════════════════
    def test_does_it_import(self):
        import yamdog
#═══════════════════════════════════════════════════════════════════════
def unittests(verbosity: int = 2) -> unittest.TestResult:
    return unittest.TextTestRunner(verbosity = verbosity).run(unittest.makeSuite(Unittests))
#═══════════════════════════════════════════════════════════════════════
def typing(shell: bool = False) -> None | tuple[str, str, int]:
    args = [str(PATH_SRC), '--config-file', str(PATH_TESTS / "mypy.ini")]
    if shell:
        os.system(f'mypy {" ".join(args)}')
    else:
        from mypy import api as mypy
        return mypy.run(args)