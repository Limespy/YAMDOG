"""API module

Handles"""
#═════════════════════════════════════════════════════════════════════════════
# IMPORT
import csv as _csv
import itertools as _itertools
import pathlib as _pathlib
import re as _re
import sys as _sys
from collections import defaultdict as _defaultdict
from collections.abc import Collection as _Collection
from collections.abc import Iterable as _Iterable
from collections.abc import Sequence as _Sequence
from enum import Enum as _Enum
from functools import partial as _partial
from io import IOBase as _IOBase
from string import punctuation as _punctuation
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Generator as _Generator
from typing import Optional as _Optional
from typing import TextIO as _TextIO
from typing import Union as _Union

from .dataclass_validate import dataclass as _dataclass
from .dataclass_validate import field as _field
#═════════════════════════════════════════════════════════════════════════════
# AUXILIARIES
# To skip using slots on python 3.9
_maybeslots = {} if _sys.version_info[1] <= 9 else {'slots': True}
#─────────────────────────────────────────────────────────────────────────────
_INDENT = ' ' * 4
#─────────────────────────────────────────────────────────────────────────────
class Align(_Enum):
    '''Alingment codes used by Table'''
    # _EnumDict __setitem__ detect lambdas as descriptors,
    # because they have __get__ attribute,
    # so they need to wrapped with a functools.partial
    LEFT = _partial(lambda width: f':{(width - 1) * "-"}')
    CENTER = _partial(lambda width: f':{"-" * (width - 2)}:')
    RIGHT = _partial(lambda width: f'{(width - 1) * "-"}:')

LEFT, CENTER, RIGHT = Align
#─────────────────────────────────────────────────────────────────────────────
class Flavour(_Enum):
    '''Variations of the Markdown syntax'''
    BASIC = 1
    EXTENDED = 2
    GITHUB = 3
    GITLAB = 4
    PYPI = 5

BASIC, EXTENDED, GITHUB, GITLAB, PYPI = Flavour
#─────────────────────────────────────────────────────────────────────────────
class ListingStyle(_Enum):
    '''Styles of listing'''
                # prefixes, prefix_length
    ORDERED = _partial(lambda : (f'{n}. ' for n in _itertools.count(1, 1)))
    UNORDERED = _partial(_itertools.repeat, '- ')
    DEFINITION = _partial(_itertools.repeat, ': ')

ORDERED, UNORDERED, DEFINITION = ListingStyle
#─────────────────────────────────────────────────────────────────────────────
class TextLevel(_Enum):
    '''Text "scipt" levels'''
    SUBSCRIPT = '~'
    NORMAL = ''
    SUPERSCRIPT = '^'

SUBSCRIPT, NORMAL, SUPERSCRIPT = TextLevel
#─────────────────────────────────────────────────────────────────────────────
class TextStyle(_Enum):
    '''Text styling options'''
    BOLD = '**', '**'
    ITALIC = '*', '*'
    STRIKETHROUGH = '~~', '~~'
    HIGHLIGHT = '==', '=='
    UNDERLINE = '<ins>', '</ins>'

BOLD, ITALIC, STRIKETHROUGH, HIGHLIGHT, UNDERLINE = TextStyle
#─────────────────────────────────────────────────────────────────────────────
INDENT = '&nbsp;&nbsp;&nbsp;&nbsp;'
#─────────────────────────────────────────────────────────────────────────────
_ListDict = _partial(_defaultdict, list)
_empty_collected = lambda: (_ListDict(), _ListDict())
_Collected = tuple[_defaultdict, _defaultdict] # Type alias for collected items
#═════════════════════════════════════════════════════════════════════════════
_re_ends = _re.compile(r'^\s*\n\s*|\s*\n\s*$')
_re_middle = _re.compile(r'\s*\n\s*')
_translation_mdchars =  str.maketrans({c: '\\' + c for c in r'\*_~^[]`'})
def _sanitise(text: str) -> str:
    return _re_middle.sub(' ', _re_ends.sub('', text)
                          ).translate(_translation_mdchars)
def _sanitise_str(content: _Any) -> str:
    return _sanitise(content) if isinstance(content, str) else str(content)
#─────────────────────────────────────────────────────────────────────────────
def _collect(item: _Any, visited: set[int], collected: _Collected
             ) -> tuple[set[int], _Collected]:
    '''Checks if item has collectibles and it has not been visited yet

    Parameters
    ----------
    item : _Any
        Item to be maybe collected from
    visited : set[int]
        All ids of already collected objects. To prevent infinite loops
    collected : _Collected
        previously collected items

    Returns
    -------
    tuple[set[int], _Collected]
        updated visisted and collected
    '''
    if (hasattr(item, '_collect')
        and isinstance(item, Element)
        and (item_id := id(item)) not in visited):
        visited.add(item_id)
        visited, new_collected = item._collect(visited) # type: ignore
        for old, new in zip(collected, new_collected):
            for key, sublist in new.items():
                old[key].extend(sublist)
    return visited, collected
#─────────────────────────────────────────────────────────────────────────────
def _collect_iter(items: _Iterable, visited: set[int], collected: _Collected
                  ) -> tuple[set[int], _Collected]:
    '''Doing ordered set union thing

    Parameters
    ----------
    items : Iterable
        Items to be checked
    visited: set[int]
        Objectes already visited. To prevent infinite recursion

    Returns
    -------
    tuple[dict, dict]
        unique items
    '''
    for item in items:
        visited, collected = _collect(item, visited, collected)
    return visited, collected
#═════════════════════════════════════════════════════════════════════════════
# ELEMENTS BASE CLASSES
@_dataclass(**_maybeslots)
class Element:
    '''Base class for all YAMDOG elements'''
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, other):
        return Document([self, other]) # type: ignore
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class ContainerElement(Element):
    '''Base class for elements with content that may be other elements'''
    content: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __bool__(self) -> bool:
        return bool(self.content)
    #─────────────────────────────────────────────────────────────────────────
    def __getattr__(self, attr: str) -> _Any:
        return getattr(self.content, attr)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self, visited: set[int]) -> tuple[set[int], _Collected]:
        return _collect(self.content, visited, _empty_collected())
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class IterableElement(ContainerElement):
    '''Base class for elements that have iterable content'''
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self, visited: set[int]) -> tuple[set[int], _Collected]:
        return _collect_iter(self.content, visited, _empty_collected())
    #─────────────────────────────────────────────────────────────────────────
    def __iter__(self):
        return iter(self.content)
#═════════════════════════════════════════════════════════════════════════════
@_dataclass
class InlineElement(Element):
    """A marker class to whether element can be treated as inline"""
    ...
#═════════════════════════════════════════════════════════════════════════════
#═════════════════════════════════════════════════════════════════════════════
# Checkbox
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Checkbox(ContainerElement):
    '''[x] Checkbox

    Parameters
    ----------
    content: Any
        content coming after the checkbox, e.g. [x] content
    checked: bool
        Whether the checkbox is checked or not
    '''
    checked: bool = False
    #─────────────────────────────────────────────────────────────────────────
    def __bool__(self) -> bool:
        return self.checked
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return (f'[{"x" if self else " "}] {_sanitise_str(self.content)}')
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, other):
        raise TypeError(f"unsupported operand type(s) for +: "
                        f"'{type(self).__name__}' and '{type(other).__name__}'")
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Code(InlineElement):
    '''Inline monospace text

    Parameters
    ----------
    text: Any
        Content to be turned into inline monospace text
    '''
    text: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'`{self.text}`'
#─────────────────────────────────────────────────────────────────────────────
_re_tics = _re.compile(r'(?:`)+')
@_dataclass(**_maybeslots)
class CodeBlock(Element):
    '''Multiline monospace text. Nesting CodeBlocks is possible

    Parameters
    ----------
    text: Any
        Text to be displayed in the code block
    language: Any, default ''
        language name to be placed on the code block beginning
    '''
    text: _Any
    language: _Any = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        # Forces potential ` characters to be resolved and undoes unnecessary sanitisation
        text = str(self.text).replace(r'\`', '`')
        mark = ('`' * (n + 1) if (tics := _re_tics.findall(text))
                                  and (n := len(max(tics))) > 2
                else '```')
        return f'{mark}{_sanitise(str(self.language))}\n{text}\n{mark}'
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Comment(Element):
    '''Text visible only in the markdown text and not HTML generated from it.

    Parameters
    ----------
    text: Any
        Contents of the comment
    '''
    text: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[{self.text}]::'
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Emoji(InlineElement):
    '''https://www.webfx.com/tools/emoji-cheat-sheet/

    Parameters
    ----------
    code: Any
        Code for the emoji
    '''
    code: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f':{self.code}:'
#═════════════════════════════════════════════════════════════════════════════
# Footnote
@_dataclass(**_maybeslots)
class Footnote(ContainerElement, InlineElement):
    '''Make a numbered note with text in the bottom

    Parameters
    ----------
    content: Any
        Content to be displayed as the note text
    '''
    _index: int = _field(init = False, default = 0)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self, visited: set[int]) -> tuple[set[int], _Collected]:
        return _collect(self.content, visited,
                        (_ListDict(), _ListDict({str(self.content): [self]})))
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[^{self._index}]'
#═════════════════════════════════════════════════════════════════════════════
# Heading
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Heading(ContainerElement):
    '''One line of text to separate sections from each other

    Parameters
    ----------
    content: Any
        Content to be displayed as the heading
    level: int
        Level of the heading, from 1 to 6
    in_TOC:
        Flag to Document whether the heading should be added to Table of  Contents
    alt_style: bool
        Using alternate heading style with ==== or ---- instead of # or ##

    Raises
    ------
    ValueError
        If level not in in range [1, 6]
    '''
    level: int
    in_TOC: bool = True
    alt_style: bool = False # Underline ----- instead of #
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        if self.level < 1 or self.level > 6:
            raise ValueError(f'Level must be greater that 0, not {self.level}')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content)
        toccomment = '' if self.in_TOC else ' <!-- omit in toc -->'

        if self.alt_style and self.level in (1, 2):
            return (text + toccomment +'\n'
                    + ('=' if self.level == 1 else '-') * len(text))
        return self.level * "#" + ' ' + text + toccomment
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class HRule(Element):
    '''Simple a horizontal line'''
    def __str__(self) -> str:
        return '---'
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Image(Element):
    '''

    Parameters
    ----------
    path: Any
        path to the image
    alt_text: Any, default 'image'
        Text that is displayed if the image cannot be shown
    '''
    path: _Any
    alt_text: _Any = 'image'
    caption: _Any = None
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return (f'![{self.alt_text}]({self.path})' if self.caption is None else
                f'![{self.alt_text}]({self.path})\n{self.caption}')
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Link(InlineElement):
    '''Link with to a target. Can be a reference in a document

    Parameters
    ----------
    target: Any
        address where link points to. E.g. an URL
    content: Any, default None
        Content to be displayed. If None, angle bracket <link> is created
    title: Any, default None
        If set, transforms link to a reference in a document.
    '''
    target: _Any
    content: _Any = None
    title: _Any = None
    _index: int = _field(init = False, default = 0)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self, visited: set[int]) -> tuple[set[int], _Collected]:
        link = (_ListDict() if self.title is None
                else _ListDict({(str(self.target), str(self.title)): [self]}))
        return _collect(self.content, visited, (link, _ListDict()))
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return (f'<{self.target}>' if self.content is None else
                (f'[{self.content}][{self._index}]' if self._index else
                 f'[{self.content}]({self.target})'))
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Listing(IterableElement):
    '''List of items

    Parameters
    ----------
    content: Iterable
        Content of the listing
    style: ListingStyle
        ORDERED, UNORDERED or DEFINITION
    '''
    content: _Iterable[_Any]
    style: ListingStyle = UNORDERED
    #─────────────────────────────────────────────────────────────────────────
    def __getattr__(self, attr: str) -> _Any:
        return getattr(self.content, attr)
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        output = []
        for item, prefix in zip(self.content, self.style.value()):
            if (isinstance(item, tuple)
                and len(item) == 2
                and isinstance(item[1], Listing)):
                output.append(prefix + str(item[0]))
                output.append(_INDENT
                              + str(item[1]).replace('\n', '\n'+ _INDENT))
            else:
                output.append(prefix
                              + str(item).replace('\n', '\n'+ ' '* len(prefix)))
        return '\n'.join(output)
#─────────────────────────────────────────────────────────────────────────────
def make_checklist(items: _Iterable[tuple[_Any, bool]]) -> Listing:
    '''Assembles a Listing of checkboxes from iterable

    Parameters
    ----------
    items: Iterable[tuple[bool, Any]]
        Wheteher the checkbox is checked and the content of the checkbox
    Returns
    -------
    Listing
        Unorderd listing containing checkboxes'''
    return Listing([Checkbox(*item) for item in items], UNORDERED)
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Math(InlineElement):
    '''Inline KaTeX math notation

    Parameters
    ----------
    text : Any
        Text to be displayed in the block
    flavour: Flavour, default GITHUB
        Markdown flavour to be be used
    '''
    text: _Any
    flavour: Flavour = GITHUB
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        if self.flavour == GITHUB:
            return f'${self.text}$'
        if self.flavour == GITLAB:
            return f'$`{self.text}`$'
        raise ValueError(f'Flavour {self.flavour} not recognised')
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class MathBlock(Element):
    '''KaTeX math notation in a block

    Parameters
    ----------
    text : Any
        Text to be displayed in the block
    flavour: Flavour, default GITHUB
        Markdown flavour to be be used
    '''
    text: _Any
    flavour: Flavour = GITHUB
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        if self.flavour == GITHUB:
            return f'$$\n{self.text}\n$$'
        if self.flavour == GITLAB:
            return f'```math\n{self.text}\n```'
        raise ValueError(f'Flavour {self.flavour} not suppoted')
#═════════════════════════════════════════════════════════════════════════════
# Paragraph
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Paragraph(IterableElement):
    '''Section of text

    Parameters
    ----------
    content: list[Any]
        contents of the paragraph. You can add more wih +=
    separator: str, default ''
        separator string to be used when combining the content into string
    '''
    content: list[_Any]
    separator: str = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return self.separator.join(map(_sanitise_str, self.content))
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, other):
        if isinstance(other, InlineElement):
            self.content.append(other)
            return self
        if isinstance(other, Paragraph):
            self.content += other.content
            return self
        raise TypeError(f"+= has not been implemented for Paragraph with object"
                        f" {repr(other)} type '{type(other).__name__}'")
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class PDF(Image):
    '''PDF view using HTML

    Parameters
    ----------
    path: Any
        path to the pdf
    alt_text: Any, default 'image'
        Text that is displayed if the image cannot be shown
    caption: Any, default None
        Caption text under thie image
    '''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        path = str(self.path)
        image = (f'<object data="{path}" type="application/pdf">'
                 f'<embed src="{path}"></embed></object>')
        return image if self.caption is None else image + f'\n{self.caption}'
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Quote(ContainerElement):
    '''Block of text that gets emphasized. Can be

    Parameters
    ----------
    content: Any
        Content to be wrapped in a quote block
    '''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return '> ' + str(self.content).replace('\n', '\n> ')
#─────────────────────────────────────────────────────────────────────────────
QuoteBlock = Quote # some backwards compatibility
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Raw(InlineElement):
    '''Unsanitised text. Can be used for e.g. inserting HTML

    Parameters
    ----------
    content: Any
    '''
    content: _Any
    def __str__(self) -> str:
        return str(self.content)
#═════════════════════════════════════════════════════════════════════════════
# Table
def _pad(items: _Iterable[str],
         widths: _Iterable[int],
         alignments: _Iterable[Align]
         ) -> _Generator[str, None, None]:
    '''Generator that pads text based on alignments given

    Parameters
    ----------
    items : Iterable[str]
        items to be turned to strings and padded
    widths : Iterable[int]
        widths to which pad to
    alignments : Iterable[Align]
        Text align tags

    Returns
    -------
    Generator[str, None, None]
        _description_

    Yields
    ------
    str
        padded text

    '''
    for align, item, width in zip(alignments, items, widths):
        yield (f'{item:^{width}}' if align == CENTER else
               (f'{item:>{width}}' if align == RIGHT else
                (f'{item:<{width}}')))
#─────────────────────────────────────────────────────────────────────────────
_table_translation = str.maketrans({'|': '&#124;',
                                    '\n': '<br><br>'})
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Table(IterableElement):
    '''Table of

    Parameters
    ----------
    content: Iterable[Iterable]
        Main body of the table
    header: Iterable
        Header of the table. Will be padded to table width
    align: Align | Iterable[Alingment]
        Alignment of the columns. LEFT, CENTER, RIGHT
        If just Align, the all columns are aligned with that.
        If iterable, then each item corresponds to one column and
        rest are padded. If empty, and alignment_pad is None, then
        padding is LEFT.
    compact: bool, default False
        When converting to str, is the table compact or padded
    alignment_pad: Optional[Align], default None
        By default missing alignments are padded with the align of
        the last align in the iterable, but this can be overridden here.
    '''
    content: _Iterable[_Iterable]
    header: _Iterable
    align: _Union[Align,
                  _Iterable[Align]] = _field(default_factory = list)  # type: ignore
    compact: bool = False
    align_pad: _Optional[Align] = None
    #─────────────────────────────────────────────────────────────────────────
    @classmethod
    def from_dict(cls,
                  data: dict[_Any, _Iterable],
                  align: _Union[Align, _Iterable[Align], None] = None,
                  compact: bool = False,
                  align_pad: _Optional[Align] = None):
        '''Assembles Table from dictionary

        Parameters
        ----------
        data : dict[_Any, _Iterable]
            _description_
        align : _Union[Align, _Iterable[Align], None], optional
            _description_, by default None
        compact : bool, optional
            _description_, by default False
        align_pad : _Optional[Align], optional
            _description_, by default None
        '''
        header = data.keys()
        content = list(_itertools.zip_longest(*data.values(), fillvalue = ''))
        if align is None:
            align = []

        return cls(content, header, align, compact, align_pad)
    #─────────────────────────────────────────────────────────────────────────
    @classmethod
    def from_csv(cls,
                 path_or_file: _Union[_pathlib.Path, _TextIO],
                 header: _Union[bool, _Iterable] = True,
                 align: _Union[Align, _Iterable[Align], None] = None,
                 compact: bool = False,
                 align_pad: _Optional[Align] = None,
                 *,
                 encoding = 'utf8',
                 **csvkwargs: _Any):
        '''Assembles Table from pathlike to csv or file object

        Parameters
        ----------
        path : _type_, optional
            _description_, by default None
        header : _Union[bool, _Iterable, None], optional
            _description_, by default None
        align : _Union[Align, _Iterable[Align], None], optional
            _description_, by default None
        compact : bool, optional
            _description_, by default False
        align_pad : _Optional[Align], optional
            _description_, by default None
        file : _type_, optional
            _description_, by default None
        csvkwargs : _Optional[dict[str, _Any]], optional
            _description_, by default None
        '''

        if isinstance(path_or_file, _IOBase):
            content = list(_csv.reader(path_or_file, **csvkwargs)) # type: ignore
        else:
            with open(path_or_file, 'r', # type: ignore
                      encoding = encoding, newline = '') as file:
                content = list(_csv.reader(file, **csvkwargs))

        if header is True:
            header = content.pop(0)
        elif header is False:
            header = []

        if align is None:
            align = []

        return cls(content, header, align, compact, align_pad)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self, visited: set[int]) -> tuple[set[int], _Collected]:
        visited, collected = _collect_iter(self.header, visited,
                                           _empty_collected())
        for row in self.content:
            visited, collected = _collect_iter(row, visited, collected)
        return visited, collected
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        header = [str(cell) for cell in self.header]
        headerlen = len(header)

        # Conversion to str and escaping |
        content = [[str(cell).translate(_table_translation) for cell in row]
                   for row in self.content]

        max_rowlen = headerlen
        for row in content:
            if len(row) > max_rowlen:
                max_rowlen = len(row)
        # Pad header with empty cells
        header.extend(['']*(max_rowlen - len(header)))

        # Pad rows to with empty cells
        for row in content:
            row.extend([''] * (max_rowlen - len(row)))

        # Pad align with Align
        if isinstance(self.align, Align):
            align = [self.align] * max_rowlen
        else:
            align = list(self.align)

            align.extend([(align[-1] if align else LEFT)
                          if self.align_pad is None else self.align_pad
                          ] * (max_rowlen - len(align)))

        # Build the table
        if self.compact: # Compact table
            output = [header, (alignment.value(3) for alignment in align)]
            output.extend(content)
            return '\n'.join('|'.join(row) for row in output)
        else: # Pretty table
            # maximum cell widths
            max_widths = ([max(len(cell), 3) for cell in header]
                          + (max_rowlen - headerlen) * [3])
            for row in content:
                for i, cell in enumerate(row):
                    if len(cell) > max_widths[i]:
                        max_widths[i] = len(cell)

            output = [_pad(header, max_widths, align),
                      (alignment.value(width) for alignment, width
                       in zip(align, max_widths))]
            output.extend(_pad(row, max_widths, align) for row in content)
            return '\n'.join('| ' + ' | '.join(row) + ' |' for row in output)
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Text(ContainerElement, InlineElement):
    '''Stylised text

    Parameters
    ----------
    content : has method str
        Content to be stylised
    style: set[str]
        Style of the text, options are: bold, italic, strikethrough, emphasis
    level: TextLevel
        NORMAL, SUBSCRIPT or SUPERSCRIPT
    colour: Any
        Uses HTML tags to make colour
    '''
    style: set[TextStyle] = _field(default_factory = set)
    level: TextLevel = NORMAL
    colour: _Any = None
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        # superscipt and subcript have to be the innermost
        marker = self.level.value
        text = f'{marker}{self.content}{marker}'

        if self.colour is not None:
            text = f'<font color="{self.colour}">{text}</font>'

        for substyle in self.style:
            left, right = substyle.value
            text = f'{left}{text}{right}'
        return text
    #─────────────────────────────────────────────────────────────────────────
    def bold(self):
        '''Makes bolded'''
        self.style.add(BOLD)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unbold(self):
        '''Removes bolding'''
        self.style.discard(BOLD)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def italicize(self):
        '''Makes italics'''
        self.style.add(ITALIC)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unitalicize(self):
        '''Removes italics'''
        self.style.discard(ITALIC)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def strikethrough(self):
        '''Adds strikethrough'''
        self.style.add(STRIKETHROUGH)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unstrikethrough(self):
        '''Removes strikethrough'''
        self.style.discard(STRIKETHROUGH)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def highlight(self):
        '''Adds highlighting'''
        self.style.add(HIGHLIGHT)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unhighlight(self):
        '''Removes highlighting'''
        self.style.discard(HIGHLIGHT)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def underline(self):
        '''Adds underlining'''
        self.style.add(UNDERLINE)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def ununderline(self):
        '''Removes underlining'''
        self.style.discard(UNDERLINE)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def superscribe(self):
        '''Makes text superscript'''
        self.level = SUPERSCRIPT
        return self
    #─────────────────────────────────────────────────────────────────────────
    def subscribe(self):
        '''Makes text subscript'''
        self.level = SUBSCRIPT
        return self
    #─────────────────────────────────────────────────────────────────────────
    def normalise(self):
        '''Removes superscript or subscript'''
        self.level = NORMAL
        return self
    #─────────────────────────────────────────────────────────────────────────
    def destyle(self):
        '''Removes all styling, but not level'''
        self.style = set()
        return self
    #─────────────────────────────────────────────────────────────────────────
    def reset(self):
        '''Removes all formatting'''
        self.style = set()
        self.level = NORMAL
        return self
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class TOC(Element):
    '''Marker where table of contents will be placed.
    Also during conversion to text the text for table of contents
    is stored here.'''
    level: int = 4
    _text: str = _field(init = False, default = '')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return self._text
#═════════════════════════════════════════════════════════════════════════════
#═════════════════════════════════════════════════════════════════════════════
# Document
def _preprocess_document(content: _Iterable[_Any]
                         ) -> tuple[list[_Any],
                                    dict[int, list[TOC]],
                                    int,
                                    list[Heading],
                                    dict[tuple[str, str], list[Link]],
                                    dict[str, list[Footnote]]]:
    '''Iterates through document tree and collects
        - TOCs
        - headers
        - references
        - footnotes
    and sanitises string objects'''
    new_content: list[str] = []
    TOCs: dict[int, list[TOC]] = _defaultdict(list)
    top_level = 0
    headings: list[Heading] = []
    collected: _Collected = (_ListDict(), _ListDict())
    visited: set[int] = set()

    for item in content:

        if isinstance(item, str):
            new_content.append(_sanitise(item).strip())
        else:
            new_content.append(item)
            if isinstance(item, TOC):
                TOCs[item.level].append(item)
            else:
                visited, collected = _collect(item, visited, collected)
                if isinstance(item, Heading) and item.in_TOC:
                    headings.append(item)
                    if item.level < top_level or not top_level:
                        top_level = item.level
    return new_content, TOCs, top_level, headings, *collected
#═════════════════════════════════════════════════════════════════════════════
def _process_footnotes(footnotes: dict[str, list[Footnote]]) -> str:
    '''Makes footone list text from collected footnotes and updates
    their indices'''
    info = []
    for index, footnote_list in enumerate(footnotes.values(), start = 1):
        # Adding same index to all footnotes with same text
        for footnote in footnote_list:
            footnote._index = index
        info.append((index, footnote.content)) # Same content in previous loop
    return '\n'.join(f'[^{index}]: {content}' for index, content in info)
#═════════════════════════════════════════════════════════════════════════════
def _process_references(references: dict[tuple[str, str], list[Link]]) -> str:
    '''Makes reference list text from collected link references and updates
    and their indices'''
    reflines = []
    for index, ((target, title), links) in enumerate(references.items(),
                                                        start = 1):
        reflines.append(f'[{index}]: <{target}> "{title}"')
        # Adding same index to all links with same text
        for link in links:
            link._index = index
    return '\n'.join(reflines)
#═════════════════════════════════════════════════════════════════════════════
def _process_header(language: _Any, content: _Any) -> str:
    language = str(language).strip().lower()
    return (f'---\n{content}\n---' if language == 'yaml' else
            (f'+++\n{content}\n+++' if language == 'toml' else
             (f';;;\n{content}\n;;;' if language == 'json' else
              f'---{language}\n{content}\n---')))
#═════════════════════════════════════════════════════════════════════════════
_punctuation_translation = str.maketrans(' ', '-', _punctuation)
#═════════════════════════════════════════════════════════════════════════════
def _process_TOC(TOCs: dict[int, list[TOC]],
                 headings: _Iterable[Heading],
                 top_level: int
                 ) -> None:
    '''Generates table of content string and sets it to correct TOCs'''
    refcounts: dict[str, int] = _defaultdict(lambda: -1) # {reference: index}
    TOCtexts: dict[int, list[str]] = _defaultdict(list) # {level: texts}
    TOC_maxlevel = max(TOCs.keys()) # Highest heading level to be included
    for heading in headings:
        content = _sanitise_str(heading.content)
        ref = '#' + content.translate(_punctuation_translation).lower()
        refcounts[ref] += 1

        if heading.level > TOC_maxlevel: # Short circuit
            continue

        if n_duplicates := refcounts[ref]: # Handling multiple same refs
            ref += f'-{n_duplicates}'

        line = (f'{(heading.level - top_level) * _INDENT}'
                f'- [{content}]({ref})')
        for TOClevel in TOCs:
            if heading.level <= TOClevel:
                TOCtexts[TOClevel].append(line)

    for level, toclist in TOCs.items(): # Adding appropriate texts
        text = '\n'.join(TOCtexts[level])
        for toc in toclist:
            toc._text = text
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Document(IterableElement):
    '''Highest level collection of elements.
    Each piece is separated by empty line

    Parameters
    ----------
    content: list[Any]
        Content of the document. Can be made of anything convertible to strings
    header_language_and_text: tuple[()] | tuple[Any, Any]
        Header language and text. If you want a header written in
        e.g. yaml, then ("yaml", yaml_string)
    '''
    content: list[_Any]
    header: _Union[tuple[()], tuple[_Any, _Any]] = _field(
                                        default_factory = tuple) # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, other: _Any):
        if isinstance(other, self.__class__):
            return self.__class__(self.content + other.content, self.header)
        else:
            content = self.content.copy()
            content.append(other)
            return self.__class__(content, self.header)
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, other: _Any):
        if isinstance(other, self.__class__):
            self.content += other.content
        else:
            self.content.append(other)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        (content,
         TOCs,
         top_level,
         headings,
         links,
         footnotes) = _preprocess_document(self.content)
        if self.header: # Making header
            content.insert(0, _process_header(*self.header))

        if footnotes: # Handling footnotes
            content.append(_process_footnotes(footnotes))

        if links: # Handling link references
            content.append(_process_references(links))

        if TOCs and headings: # Creating TOC
            _process_TOC(TOCs, headings, top_level)

        return '\n\n'.join(str(item) for item in content)
