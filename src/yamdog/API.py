
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


#══════════════════════════════════════════════════════════════════════════════
# AUXILIARIES
INDENT = '    '

@dataclass(frozen = True, slots = True)
class Flavour:
    name: str

BASIC = Flavour('Basic')

GITHUB = Flavour('GitHub')
GITLAB = Flavour('GitLab')
#══════════════════════════════════════════════════════════════════════════════
def collect_iter(items: Iterable) -> tuple[dict, dict]:
    '''Doing ordered set union thing

    Parameters
    ----------
    items : Iterable
        items to be checked

    Returns
    -------
    tuple[dict, dict]
        list of unique items
    '''
    output: tuple[dict[Link, None], dict[Footnote, None]] = ({}, {})
    for item in items:
        if hasattr(item, '_collect'):
            for old, new in zip(output, item._collect()):
                old |= new
    return output
#══════════════════════════════════════════════════════════════════════════════
# ELEMENTS BASE CLASSES
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
# BASIC ELEMENTS
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
        if isinstance(item, self.__class__):
            self.content += item.content
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

        if footnotes:# Handling footnotes
            for index, footnote in enumerate(footnotes, start = 1):
                footnote._index = index
            content.append('\n'.join(f'[^{footnote._index}]: {footnote.content}'
                                    for footnote in footnotes))

        # Handling references
        if references:
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
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Paragraph(IterableElement):
    content: list = field(default_factory = list)
    separator: str = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return self.separator.join(str(item) for item in self.content)
#══════════════════════════════════════════════════════════════════════════════
notations = {'bold': '**',
             'italic': '*',
             'strikethrough': '~~',
             'subscript': '~',
             'superscript': '^',
             'emphasis': '=='}
@dataclass(slots = True)
class Text(ContainerElement):
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
listingprefixes = {'unordered': (lambda : itertools.repeat('- '), 2),
                   'ordered': (lambda : (f'{n}. ' for n in itertools.count(start = 1, step = 1)), 3),
                   'definition': (lambda : itertools.repeat(': '), 2)}
@dataclass(slots = True)
class Listing(IterableElement):
    listingtype: str
    content: Iterable
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        if self.listingtype not in listingprefixes:
            raise ValueError(f'{self.listingtype} not in listingprefixes')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        prefixes, prefix_length = listingprefixes[self.listingtype]
        output = []
        for item, prefix in zip(self.content, prefixes()):
            if isinstance(item, tuple):
                output.append(prefix + str(item[0]))
                output.append(INDENT + str(item[1]).replace('\n', '\n'+ INDENT))
            else:
                output.append(prefix + str(item).replace('\n',
                                                         '\n'+ ' '* prefix_length))
        return '\n'.join(output)
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Checkbox(ContainerElement):
    checked: bool
    content: Any
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        if not isinstance(self.checked, bool):
            raise TypeError(f'Check value {self.checked} must be a bool, not {type(self.level)}')
    #─────────────────────────────────────────────────────────────────────────
    def __bool__(self) -> bool:
        return self.checked
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[{"x" if self else " "}] {self.content}'
#══════════════════════════════════════════════════════════════════════════════
def make_checklist(items: Iterable[tuple[bool, Any]]):
    return Listing('unordered',
                   (Checkbox(*item) for item in items))
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Heading(Element):
    level: int
    text: Any
    alt_style: bool = False
    in_TOC: bool = True
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        if not isinstance(self.level, int):
            raise TypeError(f'Level {self.level} type must be int, not {type(self.level)}')
        if not 0 < self.level:
            raise ValueError(f'Level must be greater that 0, not {self.level}')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.text)
        toccomment = '' if self.in_TOC else ' <!-- omit in toc -->'
        if self.alt_style and (self.level == 1 or self.level == 2):
            return ''.join((text, toccomment, '\n',
                            ('=', '-')[self.level - 1] * len(text)))
        else: # The normal style with #
            return ''.join((self.level * "#", ' ', text, toccomment))
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class CodeBlock(Element):
    content: Any
    language: Any = ''
    _tics: int = 3
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content)
        self._tics = (self.content._tics + 1 if isinstance(self.content, CodeBlock)
                else self._tics)
        return f'{"`" * self._tics}{self.language}\n{text}\n{"`" * self._tics}'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Address(Element):
    text: Any
    def __str__(self) -> str:
        return f'<{self.text}>'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Code(Element):
    text: Any
    def __str__(self) -> str:
        return f'`{self.text}`'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Link(Element):
    """Do not change `_index` or `_hash`"""
    text: Any
    url: Any
    title: Any = None
    _index: int = 0
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        if self.title is None:
            return {}, {}
        return {self: None}, {}
    #─────────────────────────────────────────────────────────────────────────
    def __hash__(self) -> int:
        return hash(str(self.url)) + hash(str(self.title))
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        if self._index:
            return f'[{self.text}][{self._index}]'
        return f'[{self.text}]({self.url})'
#══════════════════════════════════════════════════════════════════════════════
def pad(items: Iterable[str], widths: Iterable[int], alignments: Iterable[str]
         ) -> Generator[str, None, None]:
    for alignment, item, width in zip(alignments, items, widths):
        if alignment == 'left':
            yield f'{item}{(width - len(item)) * " "}'
        elif alignment == 'center':
            item += ((width - len(item))//2) * ' '
            yield f'{(width - len(item)) * " "}{item}'
        elif alignment == 'right':
            yield f'{(width - len(item)) * " "}{item}'
        else:
            raise ValueError(f'alignment {alignment} not recognised')
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
            raise TypeError(f"'{type(row)}' is not iterable")
    #─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _str_row_sparse(row: Iterable[str]):
        return '| ' + ' | '.join(row) + ' |'
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
            output = ['|'.join(header)]
            # Alignments
            for i, item in enumerate(alignment):
                if item == 'left':
                    alignment[i] = ':--'
                elif item == 'center':
                    alignment[i] = ':-:'
                elif item == 'right':
                    alignment[i] = '--:'
            output.append('|'.join(alignment))
            for row in self.content:
                output.append('|'.join(str(item) for item in row))
        else:
            # maximum cell widths
            max_widths = [max(len(item), 3) for item in header] + (max_rowlen - headerlen) * [3]
            content = [[str(item) for item in row] for row in self.content]
            for row in content:
                for i, item in enumerate(row):
                    itemlen = len(item)
                    if itemlen > max_widths[i]:
                        max_widths[i] = itemlen

            output = [self._str_row_sparse(pad(header, max_widths, alignment))]
            # Alignments and paddings
            alignment_row = []
            for item, width in zip(alignment, max_widths):
                if item == 'left':
                    alignment_row.append(':'+ (width - 1) * '-')
                elif item == 'center':
                    alignment_row.append(':'+ (width - 2) * '-' + ':')
                elif item == 'right':
                    alignment_row.append((width - 1) * '-' + ':')
            output.append(self._str_row_sparse(item for item in alignment_row))
            for row in content:
                output.append(self._str_row_sparse(pad(row, max_widths, alignment)))
        return '\n'.join(output)
#══════════════════════════════════════════════════════════════════════════════
# EXTENDED ELEMENTS


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
@dataclass(slots = True)
class Math(Element):
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

__all__ = ['Element', 'make_checklist']
__all__ += list({cls.__name__ for cls in Element.__subclasses__()})
__all__ += list({cls.__name__ for cls in IterableElement.__subclasses__()})
__all__ += list({cls.__name__ for cls in ContainerElement.__subclasses__()})
