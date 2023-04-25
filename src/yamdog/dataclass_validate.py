from dataclasses import *
from dataclasses import dataclass as _dataclass_std
from typing import _UnionGenericAlias # type: ignore
from typing import Any as _Any
from typing import Callable as _Callable
from typing import GenericAlias as _GenericAlias # type: ignore
from typing import Protocol as _Protocol
del dataclass # type: ignore
#──────────────────────────────────────────────────────────────────────────────
class _DataclassWrapped(_Protocol):
    __dataclass_fields__: dict[str, Field]
#──────────────────────────────────────────────────────────────────────────────
def _basic(fieldtype, value: str) -> list[str]:
    return ([] if isinstance(value, fieldtype) else
            [f"{value!r} is type '{type(value).__qualname__}',"
             f" not '{fieldtype.__qualname__}'"])
#──────────────────────────────────────────────────────────────────────────────
def _tuple(fieldtypes, values: str) -> list[str]:
    if not fieldtypes and not values:
        return []
    if len(fieldtypes) == 2 and fieldtypes[-1] is Ellipsis:
        return _iterate(fieldtypes[0], values)
    if len(fieldtypes) != len(values):
        return [f'Length of the tuple {values!r} not {len(fieldtypes)}']
    errormessages = []
    for _type, subvalue in zip(fieldtypes, values):
        errormessages += _validate(_type, subvalue)
    return errormessages
#──────────────────────────────────────────────────────────────────────────────
def _iterate(fieldtype, values: str) -> list[str]:
    errormessages = []
    for item in values:
        errormessages += _validate(fieldtype, item)
    return errormessages
#──────────────────────────────────────────────────────────────────────────────
def _dict(fieldtypes, values) -> list[str]:
    return (_iterate(fieldtypes[0], values.keys())
            + _iterate(fieldtypes[1], values.values()))
#──────────────────────────────────────────────────────────────────────────────
def _generic_alias(fieldtype, value: str) -> list[str]:
    basetype = fieldtype.__origin__
    if errormessage := _basic(basetype, value):
        return errormessage
    if basetype is tuple:
        return _tuple(fieldtype.__args__, value)
    if (basetype is set or basetype is list) and value:
        return _iterate(fieldtype.__args__[0], value)
    if basetype is dict and value:
        return _dict(fieldtype.__args__, value)
    return []
#──────────────────────────────────────────────────────────────────────────────
def _union(fieldtypes: tuple[type, ...], value: str) -> list[str]:
    errormessages = []
    for _type in fieldtypes:
        if not (errormessage := _validate(_type, value)):
            return []
        errormessages += errormessage
    return errormessages
#──────────────────────────────────────────────────────────────────────────────
def _validate(fieldtype, value: str) -> list[str]:
    if fieldtype == _Any:
        return []
    if isinstance(fieldtype, _UnionGenericAlias):
        return _union(fieldtype.__args__, value)
    if isinstance(fieldtype, _GenericAlias):
        return _generic_alias(fieldtype, value)
    return _basic(fieldtype, value)
#──────────────────────────────────────────────────────────────────────────────
def _validate_fields(obj: _DataclassWrapped, ExceptionType = TypeError) -> None:
    '''Checks types of the attributes of the class
    '''
    errormessages = []
    for name, field in obj.__dataclass_fields__.items():
        if messages := _validate(field.type, getattr(obj, name)):
            errormessages.append(f'{name}: {" ".join(messages)}')
    if errormessages:
        errormessages.insert(0, f'{obj.__class__.__qualname__} parameters not matching types')
        raise ExceptionType('\n    - '.join(errormessages))
#──────────────────────────────────────────────────────────────────────────────
def validate(cls: type):
    '''Validate after 'init', 'post_init' or not at all (`None`)
    '''
    #─────────────────────────────────────────────────────────────────────────
    # Creating a new wrapper to wrap the original dataclass wrapper
    # to wrap init or post_init
    method_name = '__init__'
    original_method = getattr(cls, method_name)
    #─────────────────────────────────────────────────────────────────────
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
