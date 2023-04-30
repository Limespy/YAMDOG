"""API module

Handles"""
#══════════════════════════════════════════════════════════════════════════════
# IMPORT
import itertools as _itertools
import re as _re
import sys
from collections import defaultdict as _defaultdict
from collections.abc import Collection as _Collection
from collections.abc import Iterable as _Iterable
from collections.abc import Sequence as _Sequence
from enum import Enum as _Enum
from functools import partial as _partial
from string import punctuation as _punctuation
from typing import Any as _Any
from typing import Generator as _Generator
from typing import Optional as _Optional
from typing import Union as _Union

from .dataclass_validate import dataclass as _dataclass
from .dataclass_validate import field as _field
#══════════════════════════════════════════════════════════════════════════════
# AUXILIARIES
# To skip using slots on python 3.9
_maybeslots = {} if sys.version_info[1] <= 9 else {'slots': True}

_INDENT = ' ' * 4
class Alignment(_Enum):
    # _EnumDict __setitem__ detect lambdas as descriptors,
    # because they have __get__ attribute,
    # so they need to wrapped with a functools.partial
    LEFT = _partial(lambda width: ':'+ (width - 1) * '-')
    CENTER = _partial(lambda width: ':'+ (width - 2) * '-' + ':')
    RIGHT = _partial(lambda width: (width - 1) * '-' + ':')

LEFT, CENTER, RIGHT = Alignment

class ListingStyle(_Enum):
                # prefixes, prefix_length
    ORDERED = (lambda : (f'{n}. ' for n in _itertools.count(1, 1)), 3)
    UNORDERED = (lambda : _itertools.repeat('- '), 2)
    DEFINITION = (lambda : _itertools.repeat(': '), 2)

ORDERED, UNORDERED, DEFINITION = ListingStyle

class TextStyle(_Enum):
    BOLD = '**'
    ITALIC = '*'
    STRIKETHROUGH = '~~'
    HIGHLIGHT = '=='

BOLD, ITALIC, STRIKETHROUGH, HIGHLIGHT = TextStyle
class TextLevel(_Enum):
    SUBSCRIPT = '~'
    NORMAL = ''
    SUPERSCRIPT = '^'

SUBSCRIPT, NORMAL, SUPERSCRIPT = TextLevel

class Flavour(_Enum):
    BASIC = 1
    EXTENDED = 2
    GITHUB = 3
    GITLAB = 4
    PYPI = 5

BASIC, EXTENDED, GITHUB, GITLAB, PYPI = Flavour

_re_begin = _re.compile(r'^\s*\n\s*')
_re_middle = _re.compile(r'\s*\n\s*')
_re_end = _re.compile(r'\s*\n\s*$')
def _sanitise_str(text: str):
    return _re_middle.sub(' ', _re_end.sub('', _re_begin.sub('', text)))
#══════════════════════════════════════════════════════════════════════════════
def _is_collectable(obj) -> bool:
    return hasattr(obj, '_collect') and isinstance(obj, Element)
#══════════════════════════════════════════════════════════════════════════════
def _collect_iter(items: _Iterable) -> tuple[dict, dict]:
    '''Doing ordered set union thing

    Parameters
    ----------
    items : _Iterable
        items to be checked

    Returns
    -------
    tuple[dict, dict]
        list of unique items
    '''
    output: tuple[dict[Link, None], dict[Footnote, None]] = ({}, {})
    for item in items:
        if _is_collectable(item):
            for old, new in zip(output, item._collect()):
                old |= new
    return output
#══════════════════════════════════════════════════════════════════════════════
# ELEMENTS BASE CLASSES
@_dataclass(**_maybeslots)
class Element:
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, other):
        return Document([self, other]) # type: ignore
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class ContainerElement(Element):
    #─────────────────────────────────────────────────────────────────────────
    def __getattr__(self, attr: str) -> _Any:
        return getattr(self.content, attr)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return (self.content._collect() # type: ignore
                if _is_collectable(self.content) else ({}, {})) # type: ignore
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class IterableElement(ContainerElement):
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return _collect_iter(self.content)   # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def __iter__(self):
        return iter(self.content)   # type: ignore
#══════════════════════════════════════════════════════════════════════════════
@_dataclass
class InlineElement(Element):
    """A marker class to whether element can be treated as inline"""
    ...
#══════════════════════════════════════════════════════════════════════════════
# BASIC ELEMENTS
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
    content: list[_Any] = _field(default_factory = list)
    separator: str = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return self.separator.join(_sanitise_str(item) if isinstance(item, str)
                                   else str(item) for item in self.content)
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, other):
        if isinstance(other, InlineElement):
            self.content.append(other)
            return self
        elif isinstance(other, Paragraph):
            self.content += other.content
            return self
        else:
            raise TypeError(f"+= has not been implemented for Paragraph with object {repr(other)} type '{type(other).__name__}'")
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Text(ContainerElement, InlineElement):
    '''Stylised text

    Parameters
    ----------
    text : has method str
        text to be containes
    style: set[str]
        style of the text, options are: bold, italic, strikethrough, emphasis
    level: TextLevel
        NORMAL, SUBSCRIPT or SUPERSCRIPT
    '''
    content: _Any
    style: set[TextStyle] = _field(default_factory = set)
    level: TextLevel = NORMAL
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        # superscipt and subcript have to be the innermost
        marker = self.level.value
        text = f'{marker}{self.content}{marker}'

        for substyle in self.style:
            marker = substyle.value
            text = f'{marker}{text}{marker}'
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
    def strike(self):
        '''Adds strikethrough'''
        self.style.add(STRIKETHROUGH)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unstrike(self):
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
    def clear(self):
        '''Removes all formatting'''
        self.style = set()
        return self
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Listing(IterableElement):
    '''List of items

    Parameters
    ----------
    style: ListingStyle
        ORDERED, UNORDERED or DEFINITION
    content: Iterable
        Content of the listing
    '''
    style: ListingStyle
    content: _Iterable[_Any]
    #─────────────────────────────────────────────────────────────────────────
    def __getattr__(self, attr: str) -> _Any:
        return getattr(self.content, attr)
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        prefixes, prefix_length = self.style.value
        output = []
        for item, prefix in zip(self.content, prefixes()):
            if (isinstance(item, tuple)
                and len(item) == 2
                and isinstance(item[1], Listing)):
                output.append(prefix + str(item[0]))
                output.append(_INDENT
                              + str(item[1]).replace('\n', '\n'+ _INDENT))
            else:
                output.append(prefix
                              + str(item).replace('\n',
                                                  '\n'+ ' '* prefix_length))
        return '\n'.join(output)
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Checkbox(ContainerElement):
    '''[x] Checkbox

    Parameters
    ----------
    checked: bool
        Whether the checkbox is checked or not
    content: Any
        content coming after the checkbox, e.g. [x] content
    '''
    checked: bool
    content: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __bool__(self) -> bool:
        return self.checked
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        content = (_sanitise_str(self.content)
                  if isinstance(self.content, str)
                  else self.content)
        return (f'[{"x" if self else " "}] {content}')
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, other):
        raise TypeError(f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'")
#══════════════════════════════════════════════════════════════════════════════
def make_checklist(items: _Iterable[tuple[bool, _Any]]):
    '''Assembles a Listing of checkboxes from iterable

    Parameters
    ----------
    items: Iterable[tuple[bool, Any]]
        Wheteher the checkbox is checked and the content of the checkbox
    Returns
    -------
    Listing
        Unorderd listing containing checkboxes'''
    return Listing(UNORDERED,
                   (Checkbox(*item) for item in items)) # type: ignore
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Heading(ContainerElement):
    level: int
    content: _Any
    alt_style: bool = False # Underline ----- instead of #
    in_TOC: bool = True
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        if self.level <= 0:
            raise ValueError(f'Level must be greater that 0, not {self.level}')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content)
        toccomment = '' if self.in_TOC else ' <!-- omit in toc -->'
        if self.alt_style and self.level in (1, 2):
            return (text + toccomment +'\n'
                    + ('=' if self.level == 1 else '-') * len(text))
        return self.level * "#" + ' ' + text + toccomment
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Code(InlineElement):
    '''Inline monospace text

    Parameters
    ----------
    content: Any
        Content to be turned into inline monospace text
    '''
    content: _Any
    def __str__(self) -> str:
        return f'`{self.content}`'
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class CodeBlock(Element):
    content: _Any
    language: _Any = ''
    _tics: int = _field(init = False, default = 3)
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content)
        language = _sanitise_str(str(self.language))
        if isinstance(self.content, CodeBlock):
            self._tics = self.content._tics + 1
        return f'{"`" * self._tics}{language}\n{text}\n{"`" * self._tics}'
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Address(InlineElement):
    content: _Any
    def __str__(self) -> str:
        return f'<{self.content}>'
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Link(InlineElement):
    '''Link with to a target. Can be a reference in a document

    Parameters
    ----------
    content: Any
        Content to be displayed
    target: Any
        address where link points to. E.g. an URL
    title: Any, default None
        If set, transforms link to a reference in a document.
    '''
    content: _Any
    target: _Any
    title: _Any = None
    _index: int = _field(init = False, default = 0)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return ({} if self.title is None else {self: None},
                self.content._collect()[1] if _is_collectable(self.content) else {})
    #─────────────────────────────────────────────────────────────────────────
    def __hash__(self) -> int:
        return (hash(str(self.target))
                + hash(str(self.title))
                + hash(str(self.content)))
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return (f'[{self.content}][{self._index}]' if self._index
                else f'[{self.content}]({self.target})')
#══════════════════════════════════════════════════════════════════════════════
# Table
def _pad(items: _Iterable[str],
         widths: _Iterable[int],
         alignments: _Iterable[Alignment]
         ) -> _Generator[str, None, None]:
    '''Generator that pads text based on alignments given

    Parameters
    ----------
    items : Iterable[str]
        _description_
    widths : Iterable[int]
        _description_
    alignments : Iterable[Alignment]
        Text alignment tags

    Returns
    -------
    Generator[str, None, None]
        _description_

    Yields
    ------
    str
        padded text

    Raises
    ------
    ValueError
        if Alignment is not recognised
    '''
    for alignment, item, width in zip(alignments, items, widths):
        if alignment == LEFT:
            yield f'{item:<{width}}'
        elif alignment == CENTER:
            yield f'{item:^{width}}'
        elif alignment == RIGHT:
            yield f'{item:>{width}}'
        else:
            raise ValueError(f'alignment {alignment} not recognised')
#─────────────────────────────────────────────────────────────────────────────
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Table(IterableElement):
    '''Table of

    Parameters
    ----------
    header: Iterable
        Header of the table. Will be padded to table width
    content: list[Collection]
        Main body of the table
    alignment: Union[Alignment, Collection[Alingment]]
        Alignment of the columns. LEFT, CENTER, RIGHT
        If just Alignment, the all columns are aligned with that.
        If iterable, then each item corresponds to one column and
        rest are padded. If empty, and alignment_pad is None, then
        padding is LEFT.
    compact: bool, default False
        When converting to str, is the table compact or padded
    alignment_pad: Optional[Alignmetn], default None
        By default missing alignments are padded with the alignment of
        the last alignment in the iterable, but this can be overridden here.
    '''
    header: _Iterable
    content: list[_Collection] = _field(default_factory = list)
    alignment: _Union[Alignment,
                      _Iterable[Alignment]] = _field(default_factory = list)  # type: ignore
    compact: bool = False
    alignment_pad: _Optional[Alignment] = None
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        output = _collect_iter(self.header)
        for row in self.content:
            for old, new in zip(output, _collect_iter(row)):
                old |= new
        return output
    #─────────────────────────────────────────────────────────────────────────
    def append(self, row: _Collection) -> None:
        if isinstance(row, _Iterable):
            self.content.append(row)
        else:
            raise TypeError(f"'{type(row)}' is not iterable")
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        header = [str(item) for item in self.header]
        headerlen = len(header)

        max_rowlen = headerlen
        for row in self.content:
            if len(row) > max_rowlen:
                max_rowlen = len(row)
        header += ['']*(max_rowlen - len(header))

        if isinstance(self.alignment, Alignment):
            alignment = [self.Alignment] * max_rowlen
        else:
            alignment = list(self.alignment)
            alignment_pad = ((alignment[-1] if alignment else LEFT)
                             if self.alignment_pad is None
                             else self.alignment_pad)
            alignment.extend([alignment_pad] * (max_rowlen - len(alignment)))

        content = [[str(item) for item in row] for row in self.content]

        if self.compact: # Compact table
            output = [header, (item.value(3) for item in alignment)]
            for row in content:
                row.extend([''] * (max_rowlen - len(row)))
                output.append((str(item) for item in row))
            return '\n'.join(('|'.join(row) for row in output))
        else: # Pretty table
            # maximum cell widths
            max_widths = ([max(len(item), 3) for item in header]
                          + (max_rowlen - headerlen) * [3])
            # content = [[str(item) for item in row] for row in self.content]
            for row in content:
                for i, cell in enumerate(row):
                    if len(cell) > max_widths[i]:
                        max_widths[i] = len(cell)

            output = [_pad(header, max_widths, alignment)]
            # Alignments and paddings
            alignment_row: list[str] = [item.value(width) for item, width
                                        in zip(alignment, max_widths)]

            output.append((item for item in alignment_row))
            for row in content:
                row.extend([''] * (max_rowlen - len(row)))
                output.append(_pad(row, max_widths, alignment))
            return '\n'.join('| ' + ' | '.join(row) + ' |' for row in output)
#══════════════════════════════════════════════════════════════════════════════
# EXTENDED ELEMENTS
@_dataclass(**_maybeslots)
class Footnote(ContainerElement, InlineElement):
    '''Make a numbered note with text in the bottom

    Parameters
    ----------
    content: Any
        Content to be displayed as the note text
    '''
    content: _Any
    _index: int = _field(init = False, default = 0)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:

        links, footnotes = (self.content._collect()
                            if _is_collectable(self.content)
                            else ({}, {}))
        own = {self: None}
        own |= footnotes
        return links, own
    #─────────────────────────────────────────────────────────────────────────
    def __hash__(self) -> int:
        return hash(str(self.content))
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[^{self._index}]'
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Math(InlineElement):
    text: _Any
    flavour: Flavour = GITHUB
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        if self.flavour == GITHUB:
            return f'${self.text}$'
        elif self.flavour == GITLAB:
            return f'$`{self.text}`$'
        raise ValueError(f'Flavour {self.flavour} not recognised')
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class MathBlock(Element):
    '''_summary_

    Parameters
    ----------
    text : Any
        Text to be displayed in the block
    flavour: Flavour
        Markdown flavour to be be used
    '''
    text: _Any
    flavour: Flavour = GITHUB
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        if self.flavour == GITHUB:
            return f'$$\n{self.text}\n$$'
        elif self.flavour == GITLAB:
            return f'```math\n{self.text}\n```'
        raise ValueError(f'Flavour {self.flavour} not suppoted')
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class QuoteBlock(ContainerElement):
    content: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return '> ' + str(self.content).replace('\n', '\n> ')
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class HRule(Element):
    '''Simple a horizontal line'''
    def __str__(self) -> str:
        return '---'
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Image(Element):
    path: _Any
    alt_text: _Any = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'![{self.alt_text}]({self.path})'
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Emoji(InlineElement):
    """https://www.webfx.com/tools/emoji-cheat-sheet/"""
    code: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f':{self.code}:'
#══════════════════════════════════════════════════════════════════════════════
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
#══════════════════════════════════════════════════════════════════════════════
def _preprocess_document(content: _Iterable
                ) -> tuple[list,
                           dict[int, list[TOC]],
                           int,
                           list[Heading],
                           dict[Link, None],
                           dict[Footnote, None]]:
    '''Iterates through document tree and collects
        - TOCs
        - headers
        - references
        - footnotes
    and sanitises string objects'''
    collectables: tuple[dict[Link, None],
                        dict[Footnote, None]] = ({}, {})
    new_content: list[str] = []
    TOCs: dict[int, list[TOC]] = _defaultdict(list)
    top_level = 0
    headings: list[Heading] = []
    for item in content:
        if isinstance(item, str):
            new_content.append(_sanitise_str(item).strip())
        else:
            new_content.append(item)
            if isinstance(item, TOC):
                TOCs[item.level].append(item)
            else:
                if isinstance(item, Heading) and item.in_TOC:
                    headings.append(item)
                    if item.level < top_level or not top_level:
                        top_level = item.level
                if _is_collectable(item):
                    for old, new in zip(collectables, item._collect()):
                        old |= new
    return new_content, TOCs, top_level, headings, *collectables
#══════════════════════════════════════════════════════════════════════════════
def _process_footnotes(footnotes: dict[Footnote, None]) -> str:
    '''Makes footone list text from collected footnotes and updates
    their indices'''
    for index, footnote in enumerate(footnotes, start = 1):
        footnote._index = index
    return '\n'.join(f'[^{footnote._index}]: {footnote.content}'
                     for footnote in footnotes)
#══════════════════════════════════════════════════════════════════════════════
def _process_references(references: dict[Link, None]) -> str:
    '''Makes reference list text from collected link references and updates
    and their indices'''
    reftargets: dict[str, list[Link]] = _defaultdict(list)
    for link in references: # matching links to references
        reftargets[f'<{link.target}> "{link.title}"'].append(link)
    reflines = []
    for index, (reftext, links) in enumerate(reftargets.items(), start = 1):
        for link in links: # Adding indices to links and reftext
            link._index = index
        reflines.append(f'[{index}]: {reftext}')
    return '\n'.join(reflines)
#══════════════════════════════════════════════════════════════════════════════
def _process_header(language: _Any, content: _Any) -> str:
    language = str(language).strip().lower()
    if language == 'yaml':
        return f'---\n{content}\n---'
    if language == 'toml':
        return f'+++\n{content}\n+++'
    if language == 'json':
        return f';;;\n{content}\n;;;'
    return f'---{language}\n{content}\n---'
#══════════════════════════════════════════════════════════════════════════════
def _heading_ref_texts(text: str) -> tuple[str, str]:
    '''Generates visible link text and internal link target'''
    return (text.translate(''.maketrans('', '', '[]')),
            '#' + text.translate(''.maketrans(' ', '-', _punctuation)).lower())
#══════════════════════════════════════════════════════════════════════════════
def _process_TOC(TOCs: dict[int, list[TOC]],
                 headings: _Iterable[Heading],
                 top_level: int
                 ) -> None:
    '''Generates table of content string and sets it to correct TOCs'''
    refcounts: dict[str, int] = _defaultdict(lambda: -1) # {reference: index}
    TOCtexts: dict[int, list[str]] = _defaultdict(list) # {level: texts}
    for heading in headings:
        text, ref = _heading_ref_texts(str(heading.content))
        refcounts[ref] += 1

        if n_duplicates := refcounts[ref]: # Handling multiple same refs
            ref += str(n_duplicates)

        line = f'{(heading.level - top_level) * _INDENT}- [{text}]({ref})'
        for TOClevel in TOCs:
            if heading.level <= TOClevel:
                TOCtexts[TOClevel].append(line)

    for level, toclist in TOCs.items(): # Adding appropriate texts
        text = '\n'.join(TOCtexts[level])
        for toc in toclist:
            toc._text = text
#══════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Document(IterableElement):
    content: list[_Any] = _field(default_factory = list)
    header_language_and_text: _Union[tuple[()],
                                    tuple[_Any, _Any]] = _field(
                                        default_factory = tuple) # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, item: _Any):
        return self.__iadd__(item)
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, item: _Any):
        if isinstance(item, self.__class__):
            self.content += item.content
        else:
            self.content.append(item)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self)  -> str:
        content, TOCs, top_level, headings, refs, footnotes = _preprocess_document(self.content)

        if self.header_language_and_text: # Making heading
            content.insert(0, _process_header(*self.header_language_and_text))

        if footnotes: # Handling footnotes
            content.append(_process_footnotes(footnotes))

        if refs: # Handling link references
            content.append(_process_references(refs))

        if TOCs and headings: # Creating TOC
            _process_TOC(TOCs, headings, top_level)

        return '\n\n'.join(str(item) for item in content)
