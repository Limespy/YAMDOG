
from dataclasses import dataclass, field
from abc import abstractmethod

import itertools
import pathlib

from typing import Union as U

BOLD = '*'
INLINEMATH = '$'
INDENT = '    '


@dataclass
class ElementBase:

    def __add__(self, other) -> None:
        return Document([self, other])
    @abstractmethod
    def __str__(self) -> str:
        pass



#═══════════════════════════════════════════════════════════════════════
class Paragraph(ElementBase):
    def __init__(self, *items) -> str:
        self.items = items
    def __str__(self) -> str:
        output = ''
        for item in self.items:
            output += str(item)
        return output
#═══════════════════════════════════════════════════════════════════════
@dataclass
class Link(ElementBase):
    text: U[str, ElementBase]
    url: U[str, pathlib.Path]
    validate: bool = False
    #─────────────────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        if self.validate:
            raise NotImplementedError('This has not yet been implemented')
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'[{self.text}]({self.url})'
#═══════════════════════════════════════════════════════════════════════

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

@dataclass
class InlineMath(ElementBase):
    text: U[str, ElementBase]
    def __str__(self) -> str:
        return f'${self.text}$'


def padd(item: str, width: int) -> str:
    item += ((width - len(item))//2) * ' '
    return (width - len(item)) * ' ' + item

@dataclass
class Table(ElementBase):
    header: list
    alignment: list[str]
    content: list[list]
    compact: bool = False
    #─────────────────────────────────────────────────────────────────────────
    def append(self, row: list):
        if hasattr(row, '__iter__'):
            self.content.append(row)
        else:
            raise TypeError(f"'{type(row)}' object is not iterable")
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        header = [str(item) for item in self.header]
        headerlen = len(header)
        max_rowlen = headerlen

        for row in self.content:
            if len(row) > max_rowlen:
                max_rowlen = len(row)
        if self.compact:
            output = '|' + '|'.join(header) + '|\n'
            alignment = self.alignment + ['left'] * (max_rowlen - len(self.alignment))
            # Alignments
            for i, item in enumerate(alignment):
                if item == 'left':
                    alignment[i] = ':--'
                    continue
                if item == 'center':
                    alignment[i] = ':-:'
                    continue
                if item == 'right':
                    alignment[i] = '--:'
            output += '|' + '|'.join(item for item in alignment) + '|\n'
            for row in self.content:
                output += '|' + '|'.join(str(item) for item in row) + '|\n'
            return output[:-1] # Removing the last \n

        # pretty
        max_widths = [max(len(item), 3) for item in header] + (max_rowlen - headerlen) * [3]
        content = [[str(item) for item in row] for row in self.content]
        for row in content:
            for i, item in enumerate(row):
                itemlen = len(item)
                if itemlen > max_widths[i]:
                    max_widths[i] = itemlen
        output = '| ' + ' | '.join(padd(item, max_width) for item, max_width in zip(header, max_widths)) + ' |\n'
        alignment = self.alignment + ['left'] * (max_rowlen - len(self.alignment))
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
        output += '| ' + ' | '.join(item for item in alignment) + ' |\n'
        for row in content:
            output += '| ' + ' | '.join(padd(item, max_width) for item, max_width in zip(row, max_widths)) + ' |\n'
        return output[:-1]


@dataclass
class QuoteBlock(ElementBase):
    content: ElementBase
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        content = '> ' + str(self.content).replace('\n', '\n> ')
        return content


@dataclass
class Heading(ElementBase):
    level: int
    text: str
    include_in_TOC: bool = True
    def __str__(self) -> str:
        return f'{self.level * "#"} {self.text}' + ('' if self.include_in_TOC
                                                    else " <!-- omit in toc -->")

@dataclass
class Block(ElementBase):
    language: str
    content: str
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self) -> str:
        return f'```{self.language}\n{self.content}\n```'


@dataclass
class Document:
    content: list = field(default_factory = list)
    #─────────────────────────────────────────────────────────────────────────
    def __iadd__(self, item) -> None:
        print(item)
        self.content.append(item)
        return self
    #─────────────────────────────────────────────────────────────────────────
    def __add__(self, item) -> None:
        if isinstance(item, Document):
            self.content + item.content
            return self
        else:
            self.content.append(item)
            return self
    #─────────────────────────────────────────────────────────────────────────
    def __str__(self)  -> str:
        return '\n\n'.join(str(item) for item in self.content) + '\n'
    #─────────────────────────────────────────────────────────────────────────
    def to_file(self,
                filepath: pathlib.Path = pathlib.Path.cwd() / 'document.md'
                ) -> None:
        with open(filepath, 'w+', encoding  = 'utf8') as f:
            f.write(str(self))
