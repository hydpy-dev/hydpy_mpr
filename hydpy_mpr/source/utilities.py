from __future__ import annotations

from hydpy_mpr.source.typing_ import *

Orig = TypeVar("Orig")
New = TypeVar("New")


class NewTypeDataclassDescriptor(Generic[Orig, New]):

    id2data: dict[int, New]

    def __init__(self) -> None:
        self.id2data = {}

    @overload
    def __get__(self, obj: None, owner: type[object], /) -> Self: ...
    @overload
    def __get__(self, obj: object, owner: type[object], /) -> New: ...

    def __get__(self, obj: object | None, owner: type[object], /) -> New | Self:
        if obj is None:
            return self
        return self.id2data[id(obj)]

    def __set__(self, obj: object, value: New | Orig) -> None:
        self.id2data[id(obj)] = cast(New, value)
