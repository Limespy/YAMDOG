"""API module

Handles"""
#═════════════════════════════════════════════════════════════════════════════
# IMPORT
import itertools as _itertools
import re as _re
import sys as _sys
from collections import defaultdict as _defaultdict
from collections.abc import Collection as _Collection
from collections.abc import Iterable as _Iterable
from collections.abc import Sequence as _Sequence
from enum import Enum as _Enum
from functools import partial as _partial
from string import punctuation as _punctuation
from typing import Any as _Any
from typing import Callable as _Callable
from typing import Generator as _Generator
from typing import Optional as _Optional
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
    BOLD = '**'
    ITALIC = '*'
    STRIKETHROUGH = '~~'
    HIGHLIGHT = '=='

BOLD, ITALIC, STRIKETHROUGH, HIGHLIGHT = TextStyle
#─────────────────────────────────────────────────────────────────────────────
_dict_dict: _Callable[[], dict] = lambda: _defaultdict(dict)
#═════════════════════════════════════════════════════════════════════════════
_re_begin = _re.compile(r'^\s*\n\s*')
_re_middle = _re.compile(r'\s*\n\s*')
_re_end = _re.compile(r'\s*\n\s*$')
def _sanitise_str(text: str):
    return _re_middle.sub(' ', _re_end.sub('', _re_begin.sub('', text)))
#═════════════════════════════════════════════════════════════════════════════
def _is_collectable(obj) -> bool:
    return hasattr(obj, '_collect') and isinstance(obj, Element)
#─────────────────────────────────────────────────────────────────────────────
def _update_collected(olds: tuple, news: tuple):
    for old, new in zip(olds, news):
        for key, value in new.items():
            old[key].update(value)
#─────────────────────────────────────────────────────────────────────────────
def _collect_iter(items: _Iterable) -> tuple[dict, dict]:
    '''Doing ordered set union thing

    Parameters
    ----------
    items : Iterable
        items to be checked

    Returns
    -------
    tuple[dict, dict]
        unique items
    '''
    output: tuple[_CollectedLinks,
                  _CollectedFootnotes] = (_dict_dict(),  _dict_dict())
    for item in items:
        if _is_collectable(item):
            _update_collected(output, item._collect())
    return output
#═════════════════════════════════════════════════════════════════════════════
# ELEMENTS BASE CLASSES
@_dataclass(**_maybeslots)
class Element:
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, other):
        return Document([self, other]) # type: ignore
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class ContainerElement(Element):
    #─────────────────────────────────────────────────────────────────────────
    def __getattr__(self, attr: str) -> _Any:
        return getattr(self.content, attr)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return (self.content._collect() # type: ignore
                if _is_collectable(self.content) # type: ignore
                else (_dict_dict(), _dict_dict()))
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class IterableElement(ContainerElement):
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        return _collect_iter(self.content)   # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def __iter__(self):
        return iter(self.content)   # type: ignore
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
#═════════════════════════════════════════════════════════════════════════════
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
#─────────────────────────────────────────────────────────────────────────────
_re_tics = _re.compile(r'(?:`)+')
@_dataclass(**_maybeslots)
class CodeBlock(Element):
    '''Multiline monospace text. Nesting CodeBlocks is possible

    Parameters
    ----------
    content: Any
        Text to be displayed in the code block
    language: Any, default ''
        language name to be placed on the code block beginning
    '''
    content: _Any
    language: _Any = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content) # Forces potential ` characters to be resolved
        tics = ('`' * (n_tics + 1)
                if ((tics := sorted(_re_tics.findall(text), reverse = True))
                    and (n_tics := len(tics[0])) > 2)
                else '```')
        return f'{tics}{_sanitise_str(str(self.language))}\n{text}\n{tics}'
#═════════════════════════════════════════════════════════════════════════════
# Emoji
@_dataclass(**_maybeslots)
class Emoji(InlineElement):
    """https://www.webfx.com/tools/emoji-cheat-sheet/"""
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
    content: _Any
    _index: int = _field(init = False, default = 0)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:

        links, footnotes = (self.content._collect()
                            if _is_collectable(self.content)
                            else (_dict_dict(), _dict_dict()))
        own = _dict_dict()
        own.update({self: {id(self): self}})
        own.update(footnotes)
        return links, own
    #─────────────────────────────────────────────────────────────────────────
    def __hash__(self) -> int:
        return hash(str(self.content))
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[^{self._index}]'
#─────────────────────────────────────────────────────────────────────────────
_CollectedFootnotes = dict[Footnote, dict[int, Footnote]]
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
        Using alternate heading style with ==== or ----

    Raises
    ------
    ValueError
        If level not in in range [1, 6]
    '''
    content: _Any
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
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'![{self.alt_text}]({self.path})'
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
    def _collect(self) -> tuple[dict, dict]:
        links = _dict_dict()
        if self.title is not None:
            links.update({(str(self.target), str(self.title)):
                         {id(self): self}})
        return (links,
                self.content._collect()[1] if _is_collectable(self.content)
                else _dict_dict())
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        if self.content is None:
            return f'<{self.target}>'
        if self._index:
            return f'[{self.content}][{self._index}]'
        return f'[{self.content}]({self.target})'
#─────────────────────────────────────────────────────────────────────────────
_CollectedLinks = dict[tuple[str, str], dict[int, Link]]
#═════════════════════════════════════════════════════════════════════════════
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
def make_checklist(items: _Iterable[tuple[bool, _Any]]) -> Listing:
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
        elif self.flavour == GITLAB:
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
        elif self.flavour == GITLAB:
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
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(**_maybeslots)
class Quote(ContainerElement):
    '''Block of text that gets emphasized. Can be

    Parameters
    ----------
    content: Any
        Content to be wrapped in a quote block
    '''
    content: _Any
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return '> ' + str(self.content).replace('\n', '\n> ')
#─────────────────────────────────────────────────────────────────────────────
QuoteBlock = Quote # some backwards compatibility
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
        _description_
    widths : Iterable[int]
        _description_
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

    Raises
    ------
    ValueError
        if Align is not recognised
    '''
    for align, item, width in zip(alignments, items, widths):
        if align == LEFT:
            yield f'{item:<{width}}'
        elif align == CENTER:
            yield f'{item:^{width}}'
        elif align == RIGHT:
            yield f'{item:>{width}}'
        else:
            raise ValueError(f'align {align} not recognised')
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
    header: _Iterable
    content: list[_Iterable] = _field(default_factory = list)
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
        header = data.keys()
        content = [row for row in _itertools.zip_longest(*data.values(),
                                                         fillvalue = '')]
        if align is None:
            align = []

        return cls(header, content, align, compact, align_pad)
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[_CollectedLinks, _CollectedFootnotes]:
        output = _collect_iter(self.header)
        for row in self.content:
            _update_collected(output, _collect_iter(row))
        return output
    #─────────────────────────────────────────────────────────────────────────
    def append(self, row: _Collection) -> None:
        '''Appends to content, but checks whe

        Parameters
        ----------
        row : _Collection
            Content to be added as a row

        Raises
        ------
        TypeError
            if row to be appended is not iterable
        '''
        if isinstance(row, _Iterable):
            self.content.append(row)
        else:
            raise TypeError(f"'{type(row)}' is not iterable")
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        header = [str(cell) for cell in self.header]
        headerlen = len(header)

        content = [[str(cell) for cell in row] for row in self.content]

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
            align = [self.Align] * max_rowlen
        else:
            align = list(self.align)

            align.extend([(align[-1] if align else LEFT)
                          if self.align_pad is None else self.align_pad
                          ] * (max_rowlen - len(align)))

        # Build the table
        if self.compact: # Compact table
            output = [header, (alignment.value(3) for alignment in align)]
            output.extend(content)
            return '\n'.join(('|'.join(row) for row in output))
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
# TOC
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
def _preprocess_document(content: _Iterable
                ) -> tuple[list,
                           int,
                           dict[int, list[TOC]],
                           int,
                           list[Heading],
                           _CollectedLinks,
                           _CollectedFootnotes]:
    '''Iterates through document tree and collects
        - TOCs
        - headers
        - references
        - footnotes
    and sanitises string objects'''
    collectables: tuple[_CollectedLinks,
                        _CollectedFootnotes] = (_dict_dict(), _dict_dict())
    new_content: list[str] = []
    TOC_bottomlevel = 0
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
                if item.level > TOC_bottomlevel:
                    TOC_bottomlevel = item.level
            else:
                if isinstance(item, Heading) and item.in_TOC:
                    headings.append(item)
                    if item.level < top_level or not top_level:
                        top_level = item.level
                if _is_collectable(item):
                    _update_collected(collectables, item._collect())
    return (new_content,
            TOC_bottomlevel,
            TOCs,
            top_level,
            headings,
            *collectables)
#═════════════════════════════════════════════════════════════════════════════
def _process_footnotes(footnotes: _CollectedFootnotes) -> str:
    '''Makes footone list text from collected footnotes and updates
    their indices'''
    for index, footnote_dict in enumerate(footnotes.values(), start = 1):
        # Adding same index to all footnotes with same text
        for footnote in footnote_dict.values():
            footnote._index = index
    return '\n'.join(f'[^{footnote._index}]: {footnote.content}'
                     for footnote in footnotes)
#═════════════════════════════════════════════════════════════════════════════
def _process_references(references: _CollectedLinks) -> str:
    '''Makes reference list text from collected link references and updates
    and their indices'''
    reflines = []
    for index, ((target, title), links) in enumerate(references.items(),
                                                        start = 1):
        reflines.append(f'[{index}]: <{target}> "{title}"')
        # Adding same index to all links with same text
        for link in links.values():
            link._index = index
    return '\n'.join(reflines)
#═════════════════════════════════════════════════════════════════════════════
def _process_header(language: _Any, content: _Any) -> str:
    language = str(language).strip().lower()
    if language == 'yaml':
        return f'---\n{content}\n---'
    if language == 'toml':
        return f'+++\n{content}\n+++'
    if language == 'json':
        return f';;;\n{content}\n;;;'
    return f'---{language}\n{content}\n---'
#═════════════════════════════════════════════════════════════════════════════
_square_bracket_translation = ''.maketrans('', '', '[]')
_punctuation_translation = ''.maketrans(' ', '-', _punctuation)
def _heading_ref_texts(text: str) -> tuple[str, str]:
    '''Generates visible link text and internal link target'''
    return (text.translate(_square_bracket_translation),
            '#' + text.translate(_punctuation_translation).lower())
#═════════════════════════════════════════════════════════════════════════════
def _process_TOC(TOC_bottomlevel: int,
                 TOCs: dict[int, list[TOC]],
                 headings: _Iterable[Heading],
                 top_level: int
                 ) -> None:
    '''Generates table of content string and sets it to correct TOCs'''
    refcounts: dict[str, int] = _defaultdict(lambda: -1) # {reference: index}
    TOCtexts: dict[int, list[str]] = _defaultdict(list) # {level: texts}
    for heading in headings:
        text, ref = _heading_ref_texts(str(heading.content))
        refcounts[ref] += 1

        if heading.level > TOC_bottomlevel:
            continue

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
#═════════════════════════════════════════════════════════════════════════════
@_dataclass(validate = True, **_maybeslots) # type: ignore
class Document(IterableElement):
    '''Collection of elements

    Parameters
    ----------
    content: list[Any]
        Content of the document. Can be made of anything convertible to strings
    header_language_and_text: tuple[()] | tuple[Any, Any]
        If you want a header written in e.g. yaml, then ("yaml", yaml_string)
    '''
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
        (content,
         TOC_bottomlevel,
         TOCs,
         top_level,
         headings,
         refs,
         footnotes) = _preprocess_document(self.content)

        if self.header_language_and_text: # Making heading
            content.insert(0, _process_header(*self.header_language_and_text))

        if footnotes: # Handling footnotes
            content.append(_process_footnotes(footnotes))

        if refs: # Handling link references
            content.append(_process_references(refs))

        if TOCs and headings: # Creating TOC
            _process_TOC(TOC_bottomlevel, TOCs, headings, top_level)

        return '\n\n'.join(str(item) for item in content)
