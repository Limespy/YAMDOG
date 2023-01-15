import API
import sys

args = sys.argv[1:]
if not args or '--typing' in args:
    API.typing(shell = True)
if not args or '--unittests' in args:
    API.unittests(verbosity = 2)
if not args or '--performance' in args:
    API.performance()
