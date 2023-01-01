
#══════════════════════════════════════════════════════════════════════════════
# IMPORT
from dataclasses import dataclass, field
from abc import abstractmethod, ABC

import itertools
import pathlib

import enum
from collections.abc import Sequence
from typing import Union as U
from typing import Any, Generator, Iterable, Optional

INDENT = '    '
HLine = '---'

class Flavour(enum.Enum):
    GITHUB = enum.auto
    GITLAB = enum.auto

GITHUB = Flavour.GITHUB
GITLAB = Flavour.GITLAB

#══════════════════════════════════════════════════════════════════════════════
def padd(items: Iterable[str], widths: Iterable[int]
         ) -> Generator[str, None, None]:
    for item, width in zip(items, widths):
        item += ((width - len(item))//2) * ' '
        yield (width - len(item)) * ' ' + item
#══════════════════════════════════════════════════════════════════════════════
def collect_iter(items: Iterable) -> tuple[dict, dict]:
    '''Doing ordered set union thing

    Parameters
    ----------
    items : Iterable
        items to be checked

    Returns
    -------
    dict[Link]
        list of unique items
    '''
    output: tuple[dict[Link, None], dict[Footnote, None]] = ({}, {})
    for item in items:
        if hasattr(item, '_collect'):
            for old, new in zip(output, item._collect()):
                old |= new
    return output
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Element(ABC):
    def __add__(self, other):
        return Document([self, other])
    #─────────────────────────────────────────────────────────────────────────
    @abstractmethod
    def __str__(self) -> str:
        pass
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class ContainerElement(Element):
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        if hasattr(self.content, '_collect'): # type: ignore
            return self.content._collect()  # type: ignore
        return {}, {}
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class IterableElement(Element):
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return collect_iter(self.content)   # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def __iter__(self):
        return iter(self.content)   # type: ignore
#══════════════════════════════════════════════════════════════════════════════
notations = {'bold': '**',
             'italic': '*',
             'strikethrough': '~~',
             'subscript': '~',
             'superscript': '^',
             'emphasis': '=='}
@dataclass(slots = True)
class StylisedText(ContainerElement):
    '''Stylised text

    Parameters
    ----------
    text : has method str 
        text to be containes
    style: set[str]
        style of the text, options are: bold, italic, strikethrough, subscript, superscript, emphasis

    Raises
    ------
    ValueError
        for invalid style attributes
    '''
    content: Any
    style: Iterable[str] = field(default_factory = set)
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self):
        if not isinstance(self.style, set):
            self.style = set(self.style)
        if incorrect_substyles := [substyle for substyle in self.style
                                   if substyle not in notations]:
            raise ValueError(f'Style options {incorrect_substyles} invalid')

        if 'subscript' and 'superscipt' in self.style:
            raise ValueError('Text cannot be both superscript and subscript')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content)
        for substyle in self.style:
            marker = notations[substyle]
            text = f'{marker}{text}{marker}'
        return text
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Address(Element):
    text: Any
    def __str__(self) -> str:
        return f'<{self.text}>'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Monospace(Element):
    text: Any
    def __str__(self) -> str:
        return f'`{self.text}`'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Paragraph(IterableElement):
    content: list = field(default_factory = list)
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return ' '.join(str(item) for item in self.content)
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Link(Element):
    """Do not change `_index` or `_hash`"""
    text: Any
    url: Any
    title: Any = None
    _index: int = 0
    _hash: Optional[int] = None
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        if self.title is None:
            return {}, {}
        return {self: None}, {}
    #─────────────────────────────────────────────────────────────────────────
    def __hash__(self) -> int:
        if self._hash is None:
            return hash(str(self.text)) + hash(str(self.url)) + hash(str(self.title))
        return self._hash
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        if self._index:
            return f'[{self.text}][{self._index}]'
        return f'[{self.text}]({self.url})'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Footnote(Element):
    """Do not change `_index`"""
    content: Any
    _index: int = 0 # TODO something with `field` to prevent assignment at init
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return {}, {self: None}
    #─────────────────────────────────────────────────────────────────────────
    def __hash__(self) -> int:
        return hash(str(self.content))
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[^{self._index}]'
#══════════════════════════════════════════════════════════════════════════════
listingprefixes = {'unordered': (itertools.repeat('- '), 2),
                   'ordered': ((f'{n}. ' for n in itertools.count(start = 1, step = 1)), 3),
                   'checkbox': (itertools.repeat('- [ ] '), 6),
                   'checkbox': (itertools.repeat('- [x] '), 6),
                   'definition': (itertools.repeat(': '), 2)}
@dataclass(slots = True)
class Listing(IterableElement):
    listingtype: str
    content: list
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self):
        if self.listingtype not in listingprefixes:
            raise ValueError(f'{self.listingtype} not in listingprefixes')
        if isinstance(self.content[0], Listing):
            raise ValueError(f'First item cannot be sublist')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        prefix, prefix_length = listingprefixes[self.listingtype]
        output = ''
        for item in self.content:
            if isinstance(item, tuple):
                output += next(prefix) + str(item[0]) + '\n'
                output += INDENT + str(item[1]).replace('\n', '\n'+ INDENT
                                                     ).removesuffix(INDENT) + '\n'
            else:
                output += next(prefix) + str(item).replace('\n', '\n'+ ' '* prefix_length) + '\n'
        return output[:-1]
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class InlineMath(Element):
    text: Any
    flavour: Flavour = GITHUB
    def __str__(self) -> str:
        if self.flavour == GITHUB:
            return f'${self.text}$'
        elif self.flavour == GITLAB:
            return f'$`{self.text}`$'
        raise ValueError(f'Flavour {self.flavour} not recognised')
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class MathBlock(Element):
    text: Any
    flavour: Flavour = GITHUB
    def __str__(self) -> str:
        if self.flavour == GITHUB:
            return f'$$\n{self.text}\n$$'
        elif self.flavour == GITLAB:
            return f'```math\n{self.text}\n```'
        raise ValueError(f'Flavour {self.flavour} not recognised')
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Table(IterableElement):
    header: Iterable
    alignment: list[str]
    content: list[Sequence] = field(default_factory = list)
    compact: bool = False
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        output = collect_iter(self.header)
        for row in self.content:
            for old, new in zip(output, collect_iter(row)):
                old |= new
        return output
    #─────────────────────────────────────────────────────────────────────────
    def append(self, row: Sequence) -> None:
        if hasattr(row, '__iter__'):
            self.content.append(row)
        else:
            raise TypeError(f"'{type(row)}' object is not iterable")
    #─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _str_row_sparse(row: Iterable[str]):
        return '| ' + ' | '.join(row) + ' |\n'
    #─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _str_row_compact(row: Iterable[str]):
        return '|' + '|'.join(row) + '|\n'
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        header = [str(item) for item in self.header]
        headerlen = len(header)
        max_rowlen = headerlen

        for row in self.content:
            if len(row) > max_rowlen:
                max_rowlen = len(row)
        alignment = self.alignment + ['left'] * (max_rowlen - len(self.alignment))
        if self.compact:
            output = self._str_row_compact(header) + '|\n'
            # Alignments
            for i, item in enumerate(alignment):
                if item == 'left':
                    alignment[i] = ' :-- '
                    continue
                if item == 'center':
                    alignment[i] = ' :-: '
                    continue
                if item == 'right':
                    alignment[i] = ' --: '
            output += self._str_row_compact(item for item in alignment)
            for row in self.content:
                output += self._str_row_compact(str(item) for item in row)
            return output[:-1] # Removing the last \n

        # pretty
        max_widths = [max(len(item), 3) for item in header] + (max_rowlen - headerlen) * [3]
        content = [[str(item) for item in row] for row in self.content]
        for row in content:
            for i, item in enumerate(row):
                itemlen = len(item)
                if itemlen > max_widths[i]:
                    max_widths[i] = itemlen
        output = self._str_row_sparse(padd(header, max_widths))
        # Alignments
        for i, item in enumerate(alignment):
            if item == 'left':
                alignment[i] = ':'+ (max_widths[i] - 1) * '-'
                continue
            if item == 'center':
                alignment[i] = ':'+ (max_widths[i] - 2) * '-' + ':'
                continue
            if item == 'right':
                alignment[i] = (max_widths[i] - 1) * '-' + ':'
        output += self._str_row_sparse(item for item in alignment)
        for row in content:
            output += self._str_row_sparse(padd(row, max_widths))
        return output[:-1]
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class QuoteBlock(ContainerElement):
    content: Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return '> ' + str(self.content).replace('\n', '\n> ')
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class HRule(Element):
    def __str__(self) -> str:
        return '---'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Heading(Element):
    level: int
    text: Any
    alt_style: bool = False
    in_TOC: bool = True
    def __str__(self) -> str:
        text = str(self.text)
        toccomment = '' if self.in_TOC else ' <!-- omit in toc -->'
        if self.alt_style and (self.level == 1 or self.level == 2):
            return ''.join((text, toccomment, '\n',
                            ('=', '-')[self.level - 1] * len(text)))
        else: # The normal style with #
            return ''.join((self.level * "#", text, toccomment))
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class CodeBlock(Element):
    language: Any
    content: Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'```{self.language}\n{self.content}\n```'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Image(Element):
    path: U[str, pathlib.Path]
    alt_text: Any = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'![{self.alt_text}]({self.path})'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Emoji(Element):
    """https://www.webfx.com/tools/emoji-cheat-sheet/"""
    code: Any
    def __str__(self) -> str:
        return f':{self.code}:'
#══════════════════════════════════════════════════════════════════════════════
# def parse_headings(headings):
#     for heading in headings:
#         text = str(heading.text).strip()
#         (heading.level, Link(text, f'#{text}'))

@dataclass(slots = True)
class Document(IterableElement):
    content: list = field(default_factory = list) # attribute name important
    header_text: Any = None
    header_language: Any = None
    # TOC: bool = True
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self)  -> None:
        if (self.header_text is None) ^ (self.header_language is None):
            raise ValueError('Header and language must be specified together')
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, item):
        if isinstance(item, Document):
            self.content + item.content
        else:
            self.content.append(item)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, item):
        return self.__add__(item)
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self)  -> str:
        content = list(self.content)
        # Making heading
        if self.header_text is not None and self.header_language is not None:
            language = str(self.header_language).strip().lower()
            if language == 'yaml':
                header = f'---\n{self.header_text}\n---'
            elif language == 'toml':
                header = f'+++\n{self.header_text}\n+++'
            elif language == 'json':
                header = f';;;\n{self.header_text}\n;;;'
            else:
                header = f'---{language}\n{self.header_text}\n---'
            content.insert(0, header)

        references, footnotes = self._collect()

        if footnotes: # Handling footnotes
            for index, footnote in enumerate(footnotes, start = 1):
                footnote._index = index
            content.append('\n'.join(f'[^{footnote._index}]: {footnote.content}'
                                    for footnote in footnotes))

        if references: # Handling references
            for index, link in enumerate(references, start = 1):
                link._index = index
            content.append('\n'.join(f'[{link._index}]: <{link.url}> "{link.title}"'
                                    for link in references))

        # # Creating TOC
        # if self.TOC:
        #     headings = [item for item in self.content
        #                 if isinstance(item, Heading) and item.include_in_TOC]

        return '\n\n'.join(str(item) for item in content)
    #─────────────────────────────────────────────────────────────────────────
    def to_file(self,
                filepath: pathlib.Path = pathlib.Path.cwd() / 'document.md'
                ) -> None:
        with open(filepath, 'w+', encoding  = 'utf8') as f:
            f.write(str(self))
