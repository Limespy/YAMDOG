import pathlib
import sys
import timeit
from dataclasses import dataclass
from dataclasses import field
from math import floor
from math import log10

import yamdog as md
from pydantic import BaseModel
from pympler.asizeof import asizeof # type: ignore
from yamdog._API import _sanitise_str
# ======================================================================
_maybeslots = {} if sys.version_info[1] <= 9 else {'slots': True}

@dataclass(**_maybeslots)
class ElementDC:
    def __add__(self, other):
        return md.Document([self, other])
@dataclass(**_maybeslots)
class IterableElementDC(ElementDC):
    # ------------------------------------------------------------------
    def _collect(self) -> tuple[dict, dict]:
        return _collect_iter(self.content)   # type: ignore
    # ------------------------------------------------------------------
    def __iter__(self):
        return iter(self.content)   # type: ignore
@dataclass(**_maybeslots)
class ParagraphDC(IterableElementDC):
    content: list = field(default_factory = list)
    separator: str = ''
    # ------------------------------------------------------------------────
    def __str__(self) -> str:
        return self.separator.join(_sanitise_str(item) if isinstance(item, str)
                                else str(item) for item in self.content)
    # ------------------------------------------------------------------────
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
#%% Setup 1

Paragraph = md.Paragraph
kwargs = {'content': ['a','b','c'], 'separator': '_'}
#%% Setup 2

class ElementPyd(BaseModel):
    def __add__(self, other):
        return md.Document([self, other])

class IterableElementPyd(ElementPyd):
    # ------------------------------------------------------------------
    def _collect(self) -> tuple[dict, dict]:
        return _collect_iter(self.content)   # type: ignore
    # ------------------------------------------------------------------
    def __iter__(self):
        return iter(self.content)   # type: ignore

class ParagraphPyd(IterableElementPyd):
    content: list = []
    separator: str = ''
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return self.separator.join(_sanitise_str(item) if isinstance(item, str)
                                else str(item) for item in self.content)
    # ------------------------------------------------------------------
    def __iadd__(self, other):
        if isinstance(other, md.InlineElement):
            self.content.append(other)
            return self
        elif isinstance(other, md.Paragraph):
            self.content += other.content
            return self
        else:
            raise TypeError(f"+= has not been implemented for Paragraph with object {repr(other)} type '{type(other).__name__}'")
# ======================================================================
def _time(function, /, *args, **kwargs):
    """Self-adjusting timing.

    Minimum two runs
    """
    _globals = {'function': function,
                'args': args,
                'kwargs': kwargs}
    t_min_s = 0.5
    n = 2
    args_expanded = ''.join(f'a{n}, ' for n in range(len(args)))
    kwargs_expanded = ', '.join(f'{k} = {k}' for k in kwargs)
    call = f'function({args_expanded}{kwargs_expanded})'

    args_setup = f'{args_expanded} = args\n'
    kwargs_setup = '\n'.join((f'{k} = kwargs["{k}"]' for k in kwargs))
    setup = f'{args_setup if args else ""}\n{kwargs_setup}'

    while (t := timeit.timeit(call, setup,
                              globals = _globals, number = n)) < t_min_s:
        n *= 2 * int(t_min_s / t)
    return  t / float(n)

PATH_BASE = pathlib.Path(__file__).parent
# ----------------------------------------------------------------------
def _sigfig_round(value: float, n_sigfig: int) -> float:
    n_decimals = max(0, n_sigfig - floor(log10(value)) - 1)
    return round(value, n_decimals)
# ======================================================================
def main() -> tuple[str, dict[str, dict[str, float]]]:
    classes = (('Dataclass', ParagraphDC),
               ('Validated DC', md.Paragraph),
               ('Pydantic', ParagraphPyd))
    results = {}
    for name, cls  in classes:
        results[name] = {'size [B]': asizeof(cls(**kwargs)),
                         'time [us]': _sigfig_round(_time(cls,
                                           content = ['a','b','c'],
                                           separator = '_')*1e6, 3)}
    return md.__version__, results
