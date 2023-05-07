#%% Setup 0
import sys
from dataclasses import dataclass
from dataclasses import field
_maybeslots = {} if sys.version_info[1] <= 9 else {'slots': True}
@dataclass(**_maybeslots)
class ElementDC:
    def __add__(self, other):
        return md.Document([self, other])
@dataclass(**_maybeslots)
class IterableElementDC(ElementDC):
    #─────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return _collect_iter(self.content)   # type: ignore
    #─────────────────────────────────────────────────────────────────────
    def __iter__(self):
        return iter(self.content)   # type: ignore
@dataclass(**_maybeslots)
class ParagraphDC(IterableElementDC):
    content: list = field(default_factory = list)
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
kwargs = {'content': ['a','b','c'], 'separator': '_'}
#%% Setup 1
import yamdog as md
Paragraph = md.Paragraph
kwargs = {'content': ['a','b','c'], 'separator': '_'}
#%% Setup 2
from pydantic import BaseModel
import yamdog as md
from yamdog._API import _sanitise_str

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
kwargs = {'content': ['a','b','c'], 'separator': '_'}
