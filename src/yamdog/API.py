
from dataclasses import dataclass, field
from abc import abstractmethod

import itertools
import pathlib

from collections.abc import Sequence
from typing import Union as U
from typing import Any, Generator, Iterable, Optional

INDENT = '    '

#══════════════════════════════════════════════════════════════════════════════
@dataclass
class ElementBase:
    def __add__(self, other):
        return Document([self, other])
    #─────────────────────────────────────────────────────────────────────────
    @abstractmethod
    def __str__(self) -> str:
        pass
#══════════════════════════════════════════════════════════════════════════════
def list_diff(list1, list2):
    return [item for item in list1 if item not in set(list2)]
#══════════════════════════════════════════════════════════════════════════════
def collect_references_iter(items: Iterable) -> list:
    '''Doing ordered set union thing

    Parameters
    ----------
    items : Iterable
        items to be checked

    Returns
    -------
    list
        list of unique items
    '''
    output: list[Link] = []
    for item in items:
        if hasattr(item, '_collect_references'):
            output += list_diff(item._collect_references(), output)
    return output
#══════════════════════════════════════════════════════════════════════════════
notations = {'bold': '**',
             'italic': '*',
             'strikethrough': '~~',
             'subscript': '~',
             'superscript': '^',
             'emphasis': '=='}
@dataclass
class StylisedText(ElementBase):
    '''Inline text

    Parameters
    ----------
    text : has method str 
        text to be containes
    style: set
        style of the text, options are: bold, italic, strikethrough, subscript, superscript, emphasis

    Raises
    ------
    ValueError
        for invalid style attributes
    '''
    text: str
    style: set[str] = field(default_factory = set)
    def __post_init__(self):
        if incorrect_substyles := [substyle for substyle in self.style
                                   if substyle not in notations]:
            raise ValueError(f'Style options {incorrect_substyles} invalid')

        if 'subscript' and 'superscipt' in self.style:
            raise ValueError('Text cannot be both superscript and subscript')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        text = str(self.text)
        for substyle in self.style:
            marker = notations[substyle]
            text = f'{marker}{text}{marker}'
        return text
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Address(ElementBase):
    text: str
    def __str__(self) -> str:
        return f'<{self.text}>'
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Monospace(ElementBase):
    text: str
    def __str__(self) -> str:
        return f'`{self.text}`'
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Paragraph(ElementBase):
    content: list = field(default_factory = list)
    #─────────────────────────────────────────────────────────────────────────
    def _collect_references(self) -> list:
        return collect_references_iter(self.content)
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return ''.join(str(item) for item in self.content)
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Link(ElementBase):
    text: U[str, ElementBase]
    url: U[str, pathlib.Path]
    title: Optional[str] = None
    _index: int = 0
    _hash: Optional[int] = None
    #─────────────────────────────────────────────────────────────────────────
    def _collect_references(self) -> list:
        if self.title is not None:
            return [self]
        return []
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
listingprefixes = {'unordered': (itertools.repeat('- '), 2),
                   'ordered': ((f'{n}. ' for n in itertools.count(start = 1, step = 1)), 3),
                   'checkbox': (itertools.repeat('- [ ] '), 6),
                   'checkbox': (itertools.repeat('- [x] '), 6),
                   'definition': (itertools.repeat(': '), 2)}
@dataclass
class Listing(ElementBase):
    listingtype: str
    content: list
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self):
        if self.listingtype not in listingprefixes:
            raise ValueError(f'{self.listingtype} not in listingprefixes')
        if isinstance(self.content[0], Listing):
            raise ValueError(f'First item cannot be sublist')
    #─────────────────────────────────────────────────────────────────────────
    def _collect_references(self) -> list:
        return collect_references_iter(self.content)
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
@dataclass
class InlineMath(ElementBase):
    text: U[str, ElementBase]
    def __str__(self) -> str:
        return f'${self.text}$'
#══════════════════════════════════════════════════════════════════════════════
def padd(items: Iterable[str], widths: Iterable[int]
         ) -> Generator[str, None, None]:
    for item, width in zip(items, widths):
        item += ((width - len(item))//2) * ' '
        yield (width - len(item)) * ' ' + item
@dataclass
class Table(ElementBase):
    header: Iterable
    alignment: list[str]
    content: list[Sequence] = field(default_factory = list)
    compact: bool = False
    #─────────────────────────────────────────────────────────────────────────
    def _collect_references(self):
        output = collect_references_iter(self.header)
        for row in self.content:
            output += list_diff(collect_references_iter(row), output)
        return output
    #─────────────────────────────────────────────────────────────────────────
    def append(self, row: Sequence) -> None:
        if hasattr(row, '__iter__'):
            self.content.append(row)
        else:
            raise TypeError(f"'{type(row)}' object is not iterable")
    #─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _str_row_sparse(row: Iterable):
        return '| ' + ' | '.join(row) + ' |\n'
    #─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _str_row_compact(row: Iterable):
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
                alignment[i] = ' :'+ (max_widths[i] - 1) * '-'
                continue
            if item == 'center':
                alignment[i] = ' :'+ (max_widths[i] - 2) * '-' + ':'
                continue
            if item == 'right':
                alignment[i] = (max_widths[i] - 1) * '-' + ':'
        output += self._str_row_sparse(item for item in alignment)
        for row in content:
            output += self._str_row_sparse(padd(row, max_widths))
        return output[:-1]
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class QuoteBlock(ElementBase):
    content: ElementBase
    #─────────────────────────────────────────────────────────────────────────
    def _collect_references(self) -> list:
        if hasattr(self.content, '_collect_references'):
            return self.content._collect_references()
        return []
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        content = '> ' + str(self.content).replace('\n', '\n> ')
        return content
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Heading(ElementBase):
    level: int
    text: str
    include_in_TOC: bool = True
    def __str__(self) -> str:
        return f'{self.level * "#"} {self.text}' + ('' if self.include_in_TOC
                                                    else " <!-- omit in toc -->")
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Block(ElementBase):
    language: str
    content: str
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'```{self.language}\n{self.content}\n```'
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Image(ElementBase):
    path: U[str, pathlib.Path]
    alt_text: str = ''
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self):
        return f'![{self.alt_text}]({self.path})'
#══════════════════════════════════════════════════════════════════════════════
@dataclass
class Document:
    content: list = field(default_factory = list)
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, item):
        self.content.append(item)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, item):
        if isinstance(item, Document):
            self.content + item.content
            return self
        else:
            self.content.append(item)
            return self
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self)  -> str:
        # Collecting references
        references = collect_references_iter(self.content)
        for index, link in enumerate(references, start = 1):
            link._index = index
        reftext = '\n'+'\n'.join(f'[{link._index}]: <{link.url}> "{link.title}"'
                                 for link in references) + '\n'
        return '\n\n'.join(str(item) for item in self.content) + '\n' + reftext
    #─────────────────────────────────────────────────────────────────────────
    def to_file(self,
                filepath: pathlib.Path = pathlib.Path.cwd() / 'document.md'
                ) -> None:
        with open(filepath, 'w+', encoding  = 'utf8') as f:
            f.write(str(self))
