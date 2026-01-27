from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ControlSignal(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    unknown: _ClassVar[ControlSignal]
    interrupt: _ClassVar[ControlSignal]
    rollback: _ClassVar[ControlSignal]
    done: _ClassVar[ControlSignal]
unknown: ControlSignal
interrupt: ControlSignal
rollback: ControlSignal
done: ControlSignal
