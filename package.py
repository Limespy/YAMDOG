#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#%%═════════════════════════════════════════════════════════════════════
# IMPORT

import tomli_w
import pathlib
from build import __main__ as build
import tomllib

import sys

if '--print' in sys.argv:
    sys.argv.pop(sys.argv.index('--print'))
    is_verbose = True
else:
    is_verbose = False

if '--tests' in sys.argv or is_verbose:
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
BASE_DIR = pathlib.Path(__file__).parent
PYTHON_VERSION = '>=3.9'
PATH_LICENCE = next(BASE_DIR.glob('LICENSE*'))
PATH_SRC = BASE_DIR / 'src'
PATH_INIT = next(PATH_SRC.rglob('__init__.py'))
PATH_README = BASE_DIR / 'README.md'
PATH_PYPROJECT = BASE_DIR / 'pyproject.toml'
#%%═════════════════════════════════════════════════════════════════════
# Run tests first
if '--tests' in sys.argv:
    import tests
    print('Running typing checks')
    typing_test_result = tests.typing(shell = False)
    failed = not typing_test_result[0].startswith('Success')
    failed |= bool(typing_test_result[1])
    print(f'{RED if failed else GREEN}{typing_test_result[0]}{RESET}')
    if typing_test_result[1]:
        print(typing_test_result[1])

    print('Running unit tests')
    unit_test_result = tests.unittests(verbosity = 1)
    failed |= bool(unit_test_result.errors)
    failed |= bool(unit_test_result.failures)
    if failed:
        raise Exception('Tests did not pass, read above')
    sys.argv.pop(sys.argv.index('--tests'))
#%%═════════════════════════════════════════════════════════════════════
# SETUP FUNCTIONS
def header(text: str, linechar = '─', endchar = '┐', headerwidth  =  60):
    titlewidth = headerwidth // 2
    textlen = len(text)
    l_len = ((titlewidth - textlen) // 2 - 1)
    lpad = linechar*l_len
    rpad = f'{(headerwidth - l_len - textlen - 3)*linechar}'
    return f'{lpad} {GREEN}{text}{RESET} {rpad}{endchar}'
#───────────────────────────────────────────────────────────────────────
# For classifiers
def c(*args):
    out = f'{args[0]} :: {args[1]}'
    for arg in args[2:]:
        out += f' :: {arg}'
    return out
#───────────────────────────────────────────────────────────────────────
def cset(key, *values):
    out = []
    if isinstance(key, str):
        key = (key, )
    for value in values:
        if isinstance(value, tuple):
            out.append(c(*key, *value))
        else:
            out.append(c(*key, value))
    return out
#%%═════════════════════════════════════════════════════════════════════
# BUILD INFO

# Loading the pyproject TOML file
pyproject = tomllib.loads(PATH_PYPROJECT.read_text())
build_info = pyproject['project']

if is_verbose:
    print(f'\n{header("Starting packaging setup", "=", "=")}\n')
build_info = {}
# Getting package name
build_info['name'] = PATH_INIT.parent.stem
#───────────────────────────────────────────────────────────────────────
# Version
with open(PATH_INIT, 'r', encoding = 'utf8') as f:
    while not (line := f.readline().lstrip()).startswith('__version__'):
        pass
    build_info['version'] = line.split('=')[-1].strip().strip("'")
#───────────────────────────────────────────────────────────────────────
# Licence
with open(PATH_LICENCE, 'r', encoding = 'utf8') as f:
    LICENSE_NAME = f'{f.readline().strip()}'
build_info['license'] = {'text': LICENSE_NAME}
#───────────────────────────────────────────────────────────────────────
# Author
build_info['authors'] = [{'name': 'Limespy'}]
#───────────────────────────────────────────────────────────────────────
# URL
URL = f'https://github.com/{build_info["authors"][0]["name"]}/{build_info["name"]}'
GITHUB_MAIN_URL = f'{URL}/blob/main/'
#───────────────────────────────────────────────────────────────────────
# Description
with open(PATH_README, 'r', encoding = 'utf8') as f:
    # The short description is in the README after badges
    while (description := f.readline().lstrip(' ')).startswith(('#', '\n', '[')):
        pass
    while not (line := f.readline().lstrip(' ')).startswith('\n'):
        description += line

build_info['description'] = description[:-1] # Removing trailing linebreak
#───────────────────────────────────────────────────────────────────────
# Long Description
long_description = PATH_README.read_text().replace('./', GITHUB_MAIN_URL)
#───────────────────────────────────────────────────────────────────────
# Classifiers
# complete classifier list:
#   http://pypi.python.org/pypi?%3Aaction=list_classifiers
build_info['classifiers']   = [
    c('Development Status', '3 - Alpha'),
    c('License', 'OSI Approved', LICENSE_NAME),
    *cset('Operating System', 'Unix', 'POSIX', ('Microsoft', 'Windows')),
    *cset(('Programming Language', 'Python'),
          '3', ('3', 'Only'), '3.9', '3.10', '3.11')]
#───────────────────────────────────────────────────────────────────────
# Project URLs
build_info['urls'] = {
    'Changelog': f'{GITHUB_MAIN_URL}{PATH_README.name}#Changelog',
    'Issue Tracker': f'{URL}/issues'}
#───────────────────────────────────────────────────────────────────────
# Keywords
# build_info['keywords'] = ['markdown']
#───────────────────────────────────────────────────────────────────────
# Python requires
build_info['requires-python']  = PYTHON_VERSION
#───────────────────────────────────────────────────────────────────────
# Install requires
with open(BASE_DIR / 'dependencies.txt', encoding = 'utf8') as f:
    build_info['dependencies'] = [line.rstrip() for line in f.readlines()]
#───────────────────────────────────────────────────────────────────────
# Extras require
with open(BASE_DIR / 'dependencies_dev.txt', encoding = 'utf8') as f:
    build_info['optional-dependencies'] = {'dev':
                                    [line.rstrip() for line in f.readlines()]}
# ───────────────────────────────────────────────────────────────────────
# Entry points
#%%═════════════════════════════════════════════════════════════════════
# PRINTING SETUP INFO
if is_verbose:
    for key, value in build_info.items():
        print(f'\n{header(key)}\n')
        if isinstance(value, list):
            print('[', end = '')
            if value:
                print(value.pop(0), end = '')
                for item in value:
                    print(f',\n {item}', end = '')
            print(']')
        elif isinstance(value, dict):
            print('{', end = '')
            if value:
                items = iter(value.items())
                key2, value2 = next(items)
                print(f'{key2}: {value2}', end = '')
                for key2, value2 in items:
                    print(f',\n {key2}: {value2}', end = '')
            print('}')
        else:
            print(value)
#%%═════════════════════════════════════════════════════════════════════
# RUNNING THE BUILD
pyproject['project'] = build_info
PATH_PYPROJECT.write_text(tomli_w.dumps(pyproject))
for path in (BASE_DIR / 'dist').glob('*'):
    path.unlink()
if is_verbose:
    print(f'\n{header("Replacing README", "=", "=")}\n')
PATH_LOCAL_README = PATH_README.rename(PATH_README.parent /'.README.md')
PATH_README.write_text(long_description)
if is_verbose:
    print(f'\n{header("Calling build", "=", "=")}\n')
build.main([])
if is_verbose:
    print(f'\n{header("Returning README", "=", "=")}\n')
PATH_README.unlink()
PATH_LOCAL_README.rename(PATH_README.parent / 'README.md')