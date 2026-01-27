from google.protobuf import empty_pb2 as _empty_pb2
from . import engine_common_pb2 as _engine_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PutRequest(_message.Message):
    __slots__ = ("config", "checkpoint", "metadata", "new_versions")
    class NewVersionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NEW_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    config: _engine_common_pb2.EngineRunnableConfig
    checkpoint: _engine_common_pb2.Checkpoint
    metadata: _engine_common_pb2.CheckpointMetadata
    new_versions: _containers.ScalarMap[str, str]
    def __init__(self, config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., checkpoint: _Optional[_Union[_engine_common_pb2.Checkpoint, _Mapping]] = ..., metadata: _Optional[_Union[_engine_common_pb2.CheckpointMetadata, _Mapping]] = ..., new_versions: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PutWritesRequest(_message.Message):
    __slots__ = ("config", "writes", "task_id", "task_path")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    WRITES_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_PATH_FIELD_NUMBER: _ClassVar[int]
    config: _engine_common_pb2.EngineRunnableConfig
    writes: _containers.RepeatedCompositeFieldContainer[_engine_common_pb2.Write]
    task_id: str
    task_path: str
    def __init__(self, config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., writes: _Optional[_Iterable[_Union[_engine_common_pb2.Write, _Mapping]]] = ..., task_id: _Optional[str] = ..., task_path: _Optional[str] = ...) -> None: ...

class Capabilities(_message.Message):
    __slots__ = ("supports_delete_thread", "supports_prune", "supports_delete_for_runs", "supports_copy_thread")
    SUPPORTS_DELETE_THREAD_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_PRUNE_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_DELETE_FOR_RUNS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_COPY_THREAD_FIELD_NUMBER: _ClassVar[int]
    supports_delete_thread: bool
    supports_prune: bool
    supports_delete_for_runs: bool
    supports_copy_thread: bool
    def __init__(self, supports_delete_thread: bool = ..., supports_prune: bool = ..., supports_delete_for_runs: bool = ..., supports_copy_thread: bool = ...) -> None: ...

class ListRequest(_message.Message):
    __slots__ = ("config", "filter_json", "before", "limit")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    FILTER_JSON_FIELD_NUMBER: _ClassVar[int]
    BEFORE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    config: _engine_common_pb2.EngineRunnableConfig
    filter_json: bytes
    before: _engine_common_pb2.EngineRunnableConfig
    limit: int
    def __init__(self, config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., filter_json: _Optional[bytes] = ..., before: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., limit: _Optional[int] = ...) -> None: ...

class DeleteThreadRequest(_message.Message):
    __slots__ = ("thread_id",)
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    thread_id: str
    def __init__(self, thread_id: _Optional[str] = ...) -> None: ...

class DeleteForRunsRequest(_message.Message):
    __slots__ = ("run_ids",)
    RUN_IDS_FIELD_NUMBER: _ClassVar[int]
    run_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, run_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class CopyThreadRequest(_message.Message):
    __slots__ = ("from_thread_id", "to_thread_id")
    FROM_THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    TO_THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    from_thread_id: str
    to_thread_id: str
    def __init__(self, from_thread_id: _Optional[str] = ..., to_thread_id: _Optional[str] = ...) -> None: ...

class PruneRequest(_message.Message):
    __slots__ = ("thread_ids", "strategy")
    class PruneStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[PruneRequest.PruneStrategy]
        KEEP_LATEST: _ClassVar[PruneRequest.PruneStrategy]
        DELETE_ALL: _ClassVar[PruneRequest.PruneStrategy]
    UNSPECIFIED: PruneRequest.PruneStrategy
    KEEP_LATEST: PruneRequest.PruneStrategy
    DELETE_ALL: PruneRequest.PruneStrategy
    THREAD_IDS_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    thread_ids: _containers.RepeatedScalarFieldContainer[str]
    strategy: PruneRequest.PruneStrategy
    def __init__(self, thread_ids: _Optional[_Iterable[str]] = ..., strategy: _Optional[_Union[PruneRequest.PruneStrategy, str]] = ...) -> None: ...

class GetTupleRequest(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: _engine_common_pb2.EngineRunnableConfig
    def __init__(self, config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ("next_config",)
    NEXT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    next_config: _engine_common_pb2.EngineRunnableConfig
    def __init__(self, next_config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ...) -> None: ...

class ListResponse(_message.Message):
    __slots__ = ("checkpoint_tuples",)
    CHECKPOINT_TUPLES_FIELD_NUMBER: _ClassVar[int]
    checkpoint_tuples: _containers.RepeatedCompositeFieldContainer[_engine_common_pb2.CheckpointTuple]
    def __init__(self, checkpoint_tuples: _Optional[_Iterable[_Union[_engine_common_pb2.CheckpointTuple, _Mapping]]] = ...) -> None: ...

class GetTupleResponse(_message.Message):
    __slots__ = ("checkpoint_tuple",)
    CHECKPOINT_TUPLE_FIELD_NUMBER: _ClassVar[int]
    checkpoint_tuple: _engine_common_pb2.CheckpointTuple
    def __init__(self, checkpoint_tuple: _Optional[_Union[_engine_common_pb2.CheckpointTuple, _Mapping]] = ...) -> None: ...
