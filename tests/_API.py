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
    import _compare
    return _compare.main()
#══════════════════════════════════════════════════════════════════════════════
def performance():
    import _performance
    return _performance.main()
#══════════════════════════════════════════════════════════════════════════════
TESTS: dict[str, Callable] = {function.__name__: function # type: ignore
                              for function in
                              (lint, unittests, compare, typing, performance)}
def main(args: list[str] = sys.argv[1:]) -> Union[list, None, NoReturn]:
    if not args:
        return None
    if args[0] == '--all':
        return [test() for test in TESTS.values()]
    return [TESTS[arg[2:]]() for arg in args if arg.startswith('--')]
#══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    main()
