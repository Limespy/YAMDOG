'''Unittests for limesqueezer'''
#%%═════════════════════════════════════════════════════════════════════
# IMPORT
import os
import pathlib

PATH_TESTS = pathlib.Path(__file__).parent
PATH_REPO = PATH_TESTS.parent
# First item in src should be the package
PATH_SRC = next((PATH_REPO / 'src').glob('*'))
#%%═════════════════════════════════════════════════════════════════════
# TEST CASES

#══════════════════════════════════════════════════════════════════════════════
def unittests(verbosity: int = 2) -> None:
    os.system(f'pytest')
#══════════════════════════════════════════════════════════════════════════════
def typing(shell: bool = False) -> tuple[str, str, int]:
    args = [str(PATH_SRC), '--config-file', str(PATH_TESTS / "mypy.ini")]
    if shell:
        os.system(f'mypy {" ".join(args)}')
    else:
        from mypy import api as mypy
        return mypy.run(args)