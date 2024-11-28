from __future__ import annotations

from hydpy_mpr.source.typing_ import *

Orig = TypeVar("Orig")
New = TypeVar("New")


class NewTypeDataclassDescriptor(Generic[Orig, New]):

    mangled_name: str

    def __set_name__(self, owner: object, name: str) -> None:
        self.mangled_name = f"__newtype_dataclass_descriptor__{name}__"

    @overload
    def __get__(self, obj: None, owner: type[object], /) -> Self: ...
    @overload
    def __get__(self, obj: object, owner: type[object], /) -> New: ...

    def __get__(self, obj: object | None, owner: type[object], /) -> New | Self:
        if obj is None:
            return self
        return cast(New, getattr(obj, self.mangled_name))

    def __set__(self, obj: object, value: New | Orig) -> None:
        setattr(obj, self.mangled_name, value)
