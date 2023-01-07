import yamdog as md

from dataclasses import dataclass
import pytest
import typing

def test_string_cleaning():
    output = md.clean_string('''
            test text
            to check\tstring 
            cleaning.
            ''')
    assert output == 'test text to check string cleaning.'

@pytest.mark.parametrize("index,value", [
    (i, value) for i, value in enumerate(('s', 1, [], (1,), 1, 1.5))])
def test_validation(index, value):
    @dataclass
    class Cls(md.Element):
        Int: int
        Float: float
        Tuple: tuple
        Tuple2: tuple[int, int]
        Iterable: typing.Iterable
        Optional: typing.Optional[int]
        Any: typing.Any
    args = [1, 1.2, (1, 2), (1,2), [1,2,3], None, 's']
    args[index] = value
    with pytest.raises(TypeError):
        Cls(*args)


