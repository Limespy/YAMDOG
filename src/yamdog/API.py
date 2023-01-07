
#══════════════════════════════════════════════════════════════════════════════
# IMPORT
from abc import abstractmethod, ABC
from collections.abc import Sequence
from collections import defaultdict
from dataclasses import dataclass, field
import enum
import itertools
import pathlib
import re
import string
from typing import Union as U
from typing import Any, Generator, Iterable, Optional, _SpecialForm, _UnionGenericAlias, _AnyMeta # type: ignore
#══════════════════════════════════════════════════════════════════════════════
# AUXILIARIES
_INDENT = '    '

class Alignment(enum.Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

LEFT = Alignment.LEFT
CENTER = Alignment.CENTER
RIGHT = Alignment.RIGHT

class ListingStyle(enum.Enum):
    ORDERED = 1
    UNORDERED = 2
    DEFINITION = 3

ORDERED = ListingStyle.ORDERED
UNORDERED = ListingStyle.UNORDERED
DEFINITION = ListingStyle.DEFINITION

class TextStyle(enum.Enum):
    BOLD = 1
    ITALIC = 2
    STRIKETHROUGH = 3
    SUPERSCRIPT = 4
    SUBSCRIPT = 5
    HIGHLIGHT = 6

BOLD = TextStyle.BOLD
ITALIC = TextStyle.ITALIC
STRIKETHROUGH = TextStyle.STRIKETHROUGH
SUPERSCRIPT = TextStyle.SUPERSCRIPT
SUBSCRIPT = TextStyle.SUBSCRIPT
HIGHLIGHT = TextStyle.HIGHLIGHT

@dataclass(frozen = True, slots = True)
class Flavour(set):
    name: str

BASIC = Flavour('Basic')

GITHUB = Flavour('GitHub')
GITLAB = Flavour('GitLab')

_re_whitespaces = re.compile('\s\s*')
def clean_string(text: str):
    return _re_whitespaces.sub(' ', text).strip()
#══════════════════════════════════════════════════════════════════════════════
def _collect_iter(items: Iterable) -> tuple[dict, dict]:
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
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        self._validate_fields()
    #─────────────────────────────────────────────────────────────────────────
    def _validate_fields(self) -> None:
         for field_name, field_def in self.__dataclass_fields__.items():
            if isinstance(field_def.type, (_SpecialForm, _AnyMeta)):
                continue # type: ignore
            elif field_def.type is Iterable:
                field_value = getattr(self, field_name)
                if not hasattr(field_value, '__iter__'):
                    raise TypeError(f"'{type(field_value)}' object is not iterable")
                continue
            elif isinstance(field_def.type, _UnionGenericAlias):
                field_value = getattr(self, field_name) # type: ignore
                field_types = field_def.type.__args__
                for field_type in field_types:
                    if isinstance(field_value, field_type):
                        break
                else:
                    raise TypeError(f'{type(field_value)} not in {field_types}')
                # TODO
                continue
            field_type = (field_def.type.__origin__ 
                          if hasattr(field_def.type, '__origin__')
                          else field_def.type)
            field_value = getattr(self, field_name)
            if not isinstance(field_value, field_type):
                raise TypeError(f'Parameter {field_name} must be instance of type {field_type}, not {type(field_value)}')
    #─────────────────────────────────────────────────────────────────────────
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
        return _collect_iter(self.content)   # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def __iter__(self):
        return iter(self.content)   # type: ignore
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class InlineElement(Element):
    pass
#══════════════════════════════════════════════════════════════════════════════
# BASIC ELEMENTS
@dataclass(slots = True)
class TOC(Element):
    level: int = 4
    _text: str = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return self._text
#══════════════════════════════════════════════════════════════════════════════
def _translate(text, *args):
    return str(text).translate(''.maketrans(*args))
#══════════════════════════════════════════════════════════════════════════════
def _header_ref_texts(text: str) -> tuple[str, str]:
    return (_translate(text, '', '', '[]'),
            '#' + _translate(text, ' ', '-', string.punctuation).lower())
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Header(Element):
    language: str
    text: str
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        language = str(self.language).strip().lower()
        if language == 'yaml':
            return f'---\n{self.text}\n---'
        elif language == 'toml':
            return f'+++\n{self.text}\n+++'
        elif language == 'json':
            return f';;;\n{self.text}\n;;;'
        else:
            return f'---{self.language}\n{self.text}\n---'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Document(IterableElement):
    content: list = field(default_factory = list) # attribute name important
    header_language_and_text: tuple[Any, Any] = field(default_factory = tuple) # type: ignore
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self)  -> None:
        self._validate_fields()
        if len(self.header_language_and_text) not in (0, 2):
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
        if self.header_language_and_text:
            content.insert(0, Header(*self.header_language_and_text))

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
        # Creating TOC
        headings = []
        TOCs: dict[int, list[TOC]] = defaultdict(list)
        top_level = 9
        for item in self.content:
            if isinstance(item, Heading) and item.in_TOC:
                headings.append(item)
                if item.level < top_level:
                    top_level = item.level
            elif isinstance(item, TOC):
                TOCs[item.level] += [item]

        if TOCs and headings:
            refs: dict[str, int] = {}
            TOCtexts: dict[int, list[str]] = defaultdict(list)
            for heading in headings:
                text, ref = _header_ref_texts(heading.text)

                if ref in refs: # Handling multiple same refs
                    refs[ref] += 1
                    ref += str(refs[ref]) 
                else:
                    refs[ref] = 0

                line = '- '.join(((heading.level - top_level) * _INDENT,
                                  f'[{text}]({ref})'))

                for level in TOCs:
                    if heading.level <= level:
                        TOCtexts[level] += [line]

            for level, toclist in TOCs.items():
                text = '\n'.join(TOCtexts[level])
                for toc in toclist:
                    toc._text = text

        return '\n\n'.join(clean_string(item) if isinstance(item, str)
                           else str(item) for item in content)
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
        return self.separator.join(clean_string(item) if isinstance(item, str)
                                   else str(item) for item in self.content)
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, other):
        if isinstance(other, InlineElement):
            self.content.append(other)
            return self
        elif isinstance(other, Paragraph):
            self.content + other.content
            return self
        else:
            raise NotImplementedError(f'+= has not been implemented for Paragraph with object {repr(other)} type{type(other)}')
#══════════════════════════════════════════════════════════════════════════════
notations = {BOLD:          '**',
             ITALIC:        '*',
             STRIKETHROUGH: '~~',
             SUBSCRIPT:     '~',
             SUPERSCRIPT:   '^',
             HIGHLIGHT:     '=='}
@dataclass(slots = True)
class Text(ContainerElement, InlineElement):
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
    style: set[TextStyle] = field(default_factory = set)
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self):
        self._validate_fields()
        if incorrect_substyles := [substyle for substyle in self.style
                                   if substyle not in notations]:
            raise ValueError(f'Style options {incorrect_substyles} invalid')

        if SUBSCRIPT and SUPERSCRIPT in self.style:
            raise ValueError('Text cannot be both superscript and subscript')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content)
        for substyle in self.style:
            marker = notations[substyle]
            text = f'{marker}{text}{marker}'
        return text
    #─────────────────────────────────────────────────────────────────────────
    def bold(self):
        self.style.add(BOLD)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unbold(self):
        self.style.discard(BOLD)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def italicize(self):
        self.style.add(ITALIC)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unitalicize(self):
        self.style.discard(ITALIC)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def strike(self):
        self.style.add(STRIKETHROUGH)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unstrike(self):
        self.style.discard(STRIKETHROUGH)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def superscipt(self):
        self.style.discard(SUBSCRIPT)
        self.style.add(SUPERSCRIPT)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unsuperscribe(self):
        self.style.discard(SUPERSCRIPT)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def subscribe(self):
        self.style.discard(SUPERSCRIPT)
        self.style.add(SUBSCRIPT)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unsubscript(self):
        self.style.discard(SUBSCRIPT)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def highlight(self):
        self.style.add(HIGHLIGHT)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def unhighlight(self):
        self.style.discard(HIGHLIGHT)
        return self
#══════════════════════════════════════════════════════════════════════════════
markers = {UNORDERED: (lambda : itertools.repeat('- '), 2),
           ORDERED: (lambda : (f'{n}. ' for n in itertools.count(1, 1)), 3),
           DEFINITION: (lambda : itertools.repeat(': '), 2)}
@dataclass(slots = True)
class Listing(IterableElement):
    listingtype: ListingStyle
    content: Iterable
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        self._validate_fields()
        if self.listingtype not in markers:
            raise ValueError(f'{self.listingtype} not in recognised')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        prefixes, prefix_length = markers[self.listingtype]
        output = []
        for item, prefix in zip(self.content, prefixes()):
            if (isinstance(item, tuple)
                and len(item) == 2
                and isinstance(item[1], Listing)):
                output.append(prefix + str(item[0]))
                output.append(_INDENT + str(item[1]).replace('\n', '\n'+ _INDENT))
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
    def __bool__(self) -> bool:
        return self.checked
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[{"x" if self else " "}] {self.content}'
#══════════════════════════════════════════════════════════════════════════════
def make_checklist(items: Iterable[tuple[bool, Any]]):
    return Listing(UNORDERED, (Checkbox(*item) for item in items))
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Heading(Element):
    level: int
    text: Any
    alt_style: bool = False
    in_TOC: bool = True
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        self._validate_fields()
        if self.level <= 0:
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
class CodeBlock(InlineElement):
    content: Any
    language: Any = ''
    _tics: int = 3
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.content)
        self._tics = (self.content._tics + 1
                      if isinstance(self.content, CodeBlock)
                      else self._tics)
        return f'{"`" * self._tics}{self.language}\n{text}\n{"`" * self._tics}'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Address(InlineElement):
    text: Any
    def __str__(self) -> str:
        return f'<{self.text}>'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Code(InlineElement):
    text: Any
    def __str__(self) -> str:
        return f'`{self.text}`'
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Link(InlineElement):
    """Do not change `_index`"""
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
def pad(items: Iterable[str],
        widths: Iterable[int],
        alignments: Iterable[Alignment]
         ) -> Generator[str, None, None]:
    for alignment, item, width in zip(alignments, items, widths):
        if alignment == LEFT:
            yield f'{item}{(width - len(item)) * " "}'
        elif alignment == CENTER:
            item += ((width - len(item))//2) * ' '
            yield f'{(width - len(item)) * " "}{item}'
        elif alignment == RIGHT:
            yield f'{(width - len(item)) * " "}{item}'
        else:
            raise ValueError(f'alignment {alignment} not recognised')
#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Table(IterableElement):
    header: Iterable
    content: list[Sequence] = field(default_factory = list)
    alignment: list[Alignment] = field(default_factory = list)
    compact: bool = False
    #─────────────────────────────────────────────────────────────────────────
    def _collect(self) -> tuple[dict, dict]:
        output = _collect_iter(self.header)
        for row in self.content:
            for old, new in zip(output, _collect_iter(row)):
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

        alignment = self.alignment + [LEFT] * (max_rowlen - len(self.alignment))
        alignment_row: list[str] = []
        if self.compact:
            output = ['|'.join(header)]
            # Alignments
            
            for i, item in enumerate(alignment):
                if item == LEFT:
                    alignment_row.append(':--')
                elif item == CENTER:
                    alignment_row.append(':-:')
                elif item == RIGHT:
                    alignment_row.append('--:')
            output.append('|'.join(alignment_row))
            for row in self.content:
                output.append('|'.join(str(item) for item in row))
        else:
            # maximum cell widths
            max_widths = [max(len(item), 3) for item in header] + (max_rowlen - headerlen) * [3]
            content = [[str(item) for item in row] for row in self.content]
            for row in content:
                for i, cell in enumerate(row):
                    celllen = len(cell)
                    if celllen > max_widths[i]:
                        max_widths[i] = celllen

            output = [self._str_row_sparse(pad(header, max_widths, alignment))]
            # Alignments and paddings
            for item, width in zip(alignment, max_widths):
                if item == LEFT:
                    alignment_row.append(':'+ (width - 1) * '-')
                elif item == CENTER:
                    alignment_row.append(':'+ (width - 2) * '-' + ':')
                elif item == RIGHT:
                    alignment_row.append((width - 1) * '-' + ':')
            output.append(self._str_row_sparse(item for item in alignment_row))
            for row in content:
                output.append(self._str_row_sparse(pad(row, max_widths, alignment)))
        return '\n'.join(output)
#══════════════════════════════════════════════════════════════════════════════
# EXTENDED ELEMENTS


#══════════════════════════════════════════════════════════════════════════════
@dataclass(slots = True)
class Footnote(InlineElement):
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
class Math(InlineElement):
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
class Emoji(InlineElement):
    """https://www.webfx.com/tools/emoji-cheat-sheet/"""
    code: Any
    def __str__(self) -> str:
        return f':{self.code}:'
#══════════════════════════════════════════════════════════════════════════════