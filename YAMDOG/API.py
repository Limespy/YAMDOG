
from dataclasses import dataclass
from abc import abstractmethod


BOLD = '*'


@dataclass
class ElementBase:

    @abstractmethod
    def __str__(self):
        pass


class Paragraph(ElementBase):
    text: str

    def __str__(self):





@dataclass
class Header(ElementBase):
    level: int
