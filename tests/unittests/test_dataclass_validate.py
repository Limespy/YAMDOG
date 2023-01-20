from yamdog.dataclass_validate import dataclass

import pytest
import typing
from collections import abc

#══════════════════════════════════════════════════════════════════════════════
def _check(cls, args, index, value):
    args = args.copy()
    args[index] = value
    with pytest.raises(TypeError):
        cls(*args)
#──────────────────────────────────────────────────────────────────────────────
def _index_value(args):
    return ((i, value) for i, value in enumerate(args))
#══════════════════════════════════════════════════════════════════════════════
# _dict
dict_args = [{}, {1: 1, 2: 2}, {1: {1: 2}}]

@dataclass(validate = 'middle')
class DictClass:
    dict1: dict
    dict2: dict[int, int]
    dict3: dict[int, dict[int, int]]
#──────────────────────────────────────────────────────────────────────────────
def test_type_validation_dict_valid():
    DictClass(*dict_args)
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("index,value", _index_value((1,
                                                     {1: '2'},
                                                     {1: {1: '2'}})))
def test_type_validation_dict_invalid(index, value):
    _check(DictClass, dict_args, index, value)
#══════════════════════════════════════════════════════════════════════════════
# _iterable

iterable_args = [[], [1, 2]]

@dataclass(validate = 'middle')
class IterableClass:
    iterable1: abc.Iterable
    iterable2: abc.Iterable[int]
#──────────────────────────────────────────────────────────────────────────────
def test_type_validation_iterable_valid():
    IterableClass(*iterable_args)
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("index,value", _index_value((1,)))
def test_type_validation_iterable_invalid(index, value):
    _check(IterableClass, iterable_args, index, value)
#══════════════════════════════════════════════════════════════════════════════
# _union

union_args = [None, {1: 2}]

@dataclass(validate = 'middle')
class UnionClass:
    union1: typing.Union[int, None]
    union2: typing.Union[dict[int, int], int]
#──────────────────────────────────────────────────────────────────────────────
def test_type_validation_union_valid():
    UnionClass(*union_args)
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("index,value", _index_value(('1', {1: '2'})))
def test_type_validation_union_invalid(index, value):
    _check(UnionClass, union_args, index, value)
#══════════════════════════════════════════════════════════════════════════════
# _iterate

iterate_args = [[], [], {1, 2}]

@dataclass(validate = 'middle')
class IterateClass:
    iterate1: list
    iterate2: list[int]
    iterate3: set[int]
#──────────────────────────────────────────────────────────────────────────────
def test_type_validation_iterate_valid():
    IterateClass(*iterate_args)
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("index,value", _index_value((1, {1: 2}, {1, 2, '3'})))
def test_type_validation_iterate_invalid(index, value):
    _check(IterateClass, iterate_args, index, value)
#══════════════════════════════════════════════════════════════════════════════
# _tuple

tuple_args = [tuple(), tuple(), (1,2), (1,2), (1, (1, 2))]

@dataclass(validate = 'middle', frozen = True)
class TupleClass:
    tuple1: tuple
    tuple2: tuple[()]
    tuple3: tuple[int, ...]
    tuple4: tuple[int, int]
    tuple5: tuple[int, tuple[int,int]]
#──────────────────────────────────────────────────────────────────────────────
def test_type_validation_tuple_valid():
    TupleClass(*tuple_args)
#──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("index,value", _index_value((1,
                                                     (1,),
                                                     (1, '2'),
                                                     (1, '2'),
                                                     (1, (1, '2')))))
def test_type_validation_tuple_invalid(index, value):
    _check(TupleClass, tuple_args, index, value)
#══════════════════════════════════════════════════════════════════════════════
# invalid argument
def test_dataclass_invalid_keyword():

    with pytest.raises(ValueError):
        @dataclass(validate = True)
        class Invalid:
            ...