from collections.abc import Collection as _Collection
from collections.abc import Mapping as _Mapping
from dataclasses import *
from dataclasses import dataclass as _dataclass_std
from functools import wraps
from typing import _UnionGenericAlias # type: ignore
from typing import Any as _Any
from typing import Callable as _Callable
from typing import GenericAlias as _GenericAlias # type: ignore
from typing import Iterable as _Iterable
from typing import Protocol as _Protocol
del dataclass # type: ignore
#──────────────────────────────────────────────────────────────────────────────
class _DataclassWrapped(_Protocol):
    __dataclass_fields__: dict[str, Field]
#──────────────────────────────────────────────────────────────────────────────
def _basic(fieldtype, value: _Any) -> list[str]:
    return ([] if isinstance(value, fieldtype) else
            [f"{value!r} is type '{type(value).__qualname__}',"
             f" not '{fieldtype.__qualname__}'"])
#──────────────────────────────────────────────────────────────────────────────
def _tuple(fieldtypes, values: _Any) -> list[str]:
    if not fieldtypes and not values:
        return []
    if len(fieldtypes) == 2 and fieldtypes[-1] is Ellipsis:
        return _iterate(fieldtypes[0], values)
    if len(fieldtypes) != len(values):
        return [f'Length of the tuple {values!r} not {len(fieldtypes)}']
    errormessages = []
    for fieldtype, subvalue in zip(fieldtypes, values):
        errormessages.extend(_validate(fieldtype, subvalue))
    return errormessages
#──────────────────────────────────────────────────────────────────────────────
def _iterate(fieldtype: type, values: _Iterable[_Any]) -> list[str]:
    errormessages = []
    for item in values:
        errormessages.extend(_validate(fieldtype, item))
    return errormessages
#──────────────────────────────────────────────────────────────────────────────
def _generic_alias(fieldtype, value: _Any) -> list[str]:
    basetype = fieldtype.__origin__
    if errormessage := _basic(basetype, value):
        return errormessage
    if issubclass(basetype, tuple):
        return _tuple(fieldtype.__args__, value)
    if issubclass(basetype, dict) and value:
        keytype, valuetype = fieldtype.__args__
        return (_iterate(keytype, value.keys())
                + _iterate(valuetype, value.values()))
    if issubclass(basetype, _Collection) and value:
        return _iterate(fieldtype.__args__[0], value)
    return []
#──────────────────────────────────────────────────────────────────────────────
def _union(fieldtypes: tuple[type, ...], value: _Any) -> list[str]:
    '''If one of the types in the union matches'''
    errormessages = []
    for _type in fieldtypes:
        if not (errormessage := _validate(_type, value)):
            return []
        errormessages.extend(errormessage)
    return errormessages
#──────────────────────────────────────────────────────────────────────────────
def _validate(fieldtype: type, value: _Any) -> list[str]:
    if fieldtype == _Any:
        return []
    if isinstance(fieldtype, _UnionGenericAlias):
        return _union(fieldtype.__args__, value)
    if isinstance(fieldtype, _GenericAlias):
        return _generic_alias(fieldtype, value)
    return _basic(fieldtype, value)
#──────────────────────────────────────────────────────────────────────────────
def _validate_fields(obj: _DataclassWrapped) -> None:
    '''Checks types of the attributes of the class
    '''
    errormessages = []
    for name, field in obj.__dataclass_fields__.items():
        try:
            attribute = getattr(obj, name)
        except AttributeError:
            continue
        if messages := _validate(field.type, attribute):
            errormessages.append(f'{name}: {" ".join(messages)}')
    if errormessages:
        errormessages.insert(0,
                             f'{obj.__class__.__qualname__} '
                             'parameters not matching types')
        raise TypeError('\n    '.join(errormessages))
#──────────────────────────────────────────────────────────────────────────────
def validate(cls: type):
    '''Validate after 'init', 'post_init' or not at all (`None`)
    '''
    #─────────────────────────────────────────────────────────────────────────
    # Creating a new wrapper to wrap the original dataclass wrapper
    # to wrap init or post_init

    if hasattr(cls, '__post_init__'):
        method_name = '__post_init__'
        original_method = getattr(cls, method_name)
        @wraps(original_method)
        def validation_wrap(self, *args, **kwargs) -> None:
            _validate_fields(self)
            original_method(self, *args, **kwargs)
    else:
        method_name = '__init__'
        original_method = getattr(cls, method_name)
        @wraps(original_method)
        def validation_wrap(self, *args, **kwargs) -> None:
            original_method(self, *args, **kwargs)
            _validate_fields(self)
    #─────────────────────────────────────────────────────────────────────
    setattr(cls, method_name, validation_wrap)
    return cls
_validation_function = validate
#──────────────────────────────────────────────────────────────────────────────
def dataclass(cls = None, /, *, validate: bool = False, **kwargs # type: ignore
              ) -> _Callable:
    '''Validate after 'init', 'post_init' or not at all (`None`)
    '''
    if not validate:
        return _dataclass_std(cls, **kwargs)
    # cls is None
    dataclass_wrapper = _dataclass_std(cls, **kwargs)

    return lambda cls: _validation_function(dataclass_wrapper(cls))
