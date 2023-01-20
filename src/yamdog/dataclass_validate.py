
from dataclasses import *
_dataclass = dataclass
del dataclass
import typing as _typing

def _basic(fieldtype, value: str) -> list[str]:
    # print(f'{fieldtype!r}, {value!r}')
    return ([] if isinstance(value, fieldtype) else 
            [f"{value!r} is not type '{fieldtype.__name__}',"
             f" but '{type(value).__name__}'."])
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
    if fieldtype == _typing.Any:
        return []
    if isinstance(fieldtype, _typing._UnionGenericAlias): # type: ignore
        return _union(fieldtype.__args__, value)
    if isinstance(fieldtype, _typing.GenericAlias): # type: ignore
        return _generic_alias(fieldtype, value)
    return _basic(fieldtype, value)
#──────────────────────────────────────────────────────────────────────────────
def _validate_fields(obj, ExceptionType = TypeError) -> None:
    '''Checks types of the attributes of the class
    '''
    errormessages = []
    for name, field in obj.__dataclass_fields__.items():
        if messages := _validate(field.type, getattr(obj, name)):
            errormessages.append(f'{name}: {" ".join(messages)}')
    if errormessages:
        raise ExceptionType('\n'.join(errormessages))
#──────────────────────────────────────────────────────────────────────────────
def dataclass(cls=None, /, *, validate: _typing.Optional[str] = None, **kwargs): # type: ignore
    '''Validate after 'init', 'post_init' or not at all (`None`)
    '''

    if validate is None:
        return _dataclass(cls, **kwargs)
    if not (validate == 'middle' or validate == 'last'):
        raise ValueError(f'validate was {repr(validate)}')
    # cls is None
    dataclass_wrapper = _dataclass(cls, **kwargs)
    #─────────────────────────────────────────────────────────────────────────
    # Creating a new wrapper to wrap the original dataclass wrapper
    # to wrap init or post_init 
    def decoratorwrap(cls):
        cls = dataclass_wrapper(cls)
        method_name = ('__post_init__'
                       if validate == 'last' and hasattr(cls, '__post_init__')
                       else '__init__')

        original_method = getattr(cls, method_name)
        #─────────────────────────────────────────────────────────────────────
        def validation_wrap(self, *args, **kwargs) -> None:
            original_method(self, *args, **kwargs)
            _validate_fields(self)
        #─────────────────────────────────────────────────────────────────────
        setattr(cls, method_name, validation_wrap)

        return cls
    #─────────────────────────────────────────────────────────────────────────
    return decoratorwrap
