#!/usr/bin/env python
# type: ignore
#%%═════════════════════════════════════════════════════════════════════
# IMPORT
import pathlib
import re
import sys

import tomli_w

import readme
from build import __main__ as build

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

PATH_BASE = pathlib.Path(__file__).parent
PATH_LICENCE = next(PATH_BASE.glob('LICENSE*'))
PATH_README = PATH_BASE / 'README.md'
PATH_PYPROJECT = PATH_BASE / 'pyproject.toml'
VERSION = re.search(r"(?<=__version__ = ').*(?=')",
                    next((PATH_BASE / 'src').rglob('__init__.py')).read_text()
                    )[0]

def main(args = sys.argv[1:]):
    if '--print' in args:
        import pprint
        args.pop(args.index('--print'))
        is_verbose = True
    else:
        is_verbose = False

    if not '--notests' in args or is_verbose:
        import colorama as col
        RESET = col.Style.RESET_ALL
        BLACK = col.Fore.BLACK
        BLUE = col.Fore.BLUE
        CYAN = col.Fore.CYAN
        GREEN = col.Fore.GREEN
        MAGENTA = col.Fore.MAGENTA
        RED = col.Fore.RED
        YELLOW = col.Fore.YELLOW
        WHITE = col.Fore.WHITE
        WHITE_BG = col.Back.WHITE
    #%%═════════════════════════════════════════════════════════════════════
    # SETUP GLOBALS

    #%%═════════════════════════════════════════════════════════════════════
    # Run tests first
    if '--notests' in args:
        args.pop(args.index('--notests'))
    else:
        import tests
        print('Running typing checks')
        typing_test_result = tests.typing(shell = False)
        failed = not typing_test_result[0].startswith('Success')
        failed |= bool(typing_test_result[1])
        print(f'{RED if failed else GREEN}{typing_test_result[0]}{RESET}')
        if typing_test_result[1]:
            print(typing_test_result[1])

        print('Running unit tests')
        from tox import run
        failed |= bool(run.main([]))
        if failed:
            raise Exception('Tests did not pass, read above')
    #%%═════════════════════════════════════════════════════════════════════
    # SETUP FUNCTIONS
    def header(text: str, linechar = '─', endchar = '┐', headerwidth  =  60):
        titlewidth = headerwidth // 2
        textlen = len(text)
        l_len = ((titlewidth - textlen) // 2 - 1)
        lpad = linechar*l_len
        rpad = f'{(headerwidth - l_len - textlen - 3)*linechar}'
        return f'{lpad} {GREEN}{text}{RESET} {rpad}{endchar}'
    #%%═════════════════════════════════════════════════════════════════════
    # BUILD INFO

    # Loading the pyproject TOML file
    pyproject = tomllib.loads(PATH_PYPROJECT.read_text())
    master_info = pyproject['master-info']
    build_info = pyproject['project']

    if is_verbose:
        print(f'\n{header("Starting packaging setup", "=", "=")}\n')

    build_info['version'] = VERSION
    package_name = master_info["package_name"]
    full_name = master_info.get("full_name",
                                package_name.replace('-', ' ').capitalize())
    description = master_info['description']

    build_info["name"] = package_name
    build_info['description'] = description
    #───────────────────────────────────────────────────────────────────────
    # URL
    URL = f'{master_info["organisation"]}/{package_name}'
    GITHUB_MAIN_URL = f'{URL}/blob/main/'
    #───────────────────────────────────────────────────────────────────────
    # Long Description
    readme_text = str(readme.make(full_name, package_name, description)) + '\n'
    readme_text_pypi = readme_text.replace('./', GITHUB_MAIN_URL)
    #───────────────────────────────────────────────────────────────────────
    # Classifiers
    # complete classifier list:
    #   http://pypi.python.org/pypi?%3Aaction=list_classifiers
    #───────────────────────────────────────────────────────────────────────
    # Project URLs
    build_info['urls'] = {
        'Homepage': URL,
        'Changelog': f'{GITHUB_MAIN_URL}{PATH_README.name}#Changelog',
        'Issue Tracker': f'{URL}/issues'}
    #%%═════════════════════════════════════════════════════════════════════
    # PRINTING SETUP INFO
    if is_verbose:
        for key, value in build_info.items():
            print(f'\n{header(key)}\n')
            pprint.pprint(value)
    #%%═════════════════════════════════════════════════════════════════════
    # RUNNING THE BUILD
    pyproject['project'] = build_info
    pyproject['master-info'] = master_info
    PATH_PYPROJECT.write_text(tomli_w.dumps(pyproject))

    for path in (PATH_BASE / 'dist').glob('*'):
        path.unlink()

    if is_verbose:
        print(f'\n{header("Replacing README", "=", "=")}\n')
    PATH_README.write_text(readme_text_pypi)
    if is_verbose:
        print(f'\n{header("Calling build", "=", "=")}\n')
    if not '--no-build' in args:
        master_info['build-number'] += 1
        build.main([f'--config-setting=--tag-build={master_info["build-number"]}'])
    if is_verbose:
        print(f'\n{header("Returning README", "=", "=")}\n')
    PATH_README.write_text(readme_text)

if __name__ =='__main__':
    raise SystemExit(main())
