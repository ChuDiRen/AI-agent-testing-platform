import datetime

from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import engine_common_pb2 as _engine_common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OnConflictBehavior(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RAISE: _ClassVar[OnConflictBehavior]
    DO_NOTHING: _ClassVar[OnConflictBehavior]

class SortOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DESC: _ClassVar[SortOrder]
    ASC: _ClassVar[SortOrder]

class AssistantsSortBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[AssistantsSortBy]
    ASSISTANT_ID: _ClassVar[AssistantsSortBy]
    GRAPH_ID: _ClassVar[AssistantsSortBy]
    NAME: _ClassVar[AssistantsSortBy]
    CREATED_AT: _ClassVar[AssistantsSortBy]
    UPDATED_AT: _ClassVar[AssistantsSortBy]

class ThreadStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    THREAD_STATUS_IDLE: _ClassVar[ThreadStatus]
    THREAD_STATUS_BUSY: _ClassVar[ThreadStatus]
    THREAD_STATUS_INTERRUPTED: _ClassVar[ThreadStatus]
    THREAD_STATUS_ERROR: _ClassVar[ThreadStatus]

class ThreadTTLStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    THREAD_TTL_STRATEGY_DELETE: _ClassVar[ThreadTTLStrategy]

class CheckpointSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHECKPOINT_SOURCE_UNSPECIFIED: _ClassVar[CheckpointSource]
    CHECKPOINT_SOURCE_INPUT: _ClassVar[CheckpointSource]
    CHECKPOINT_SOURCE_LOOP: _ClassVar[CheckpointSource]
    CHECKPOINT_SOURCE_UPDATE: _ClassVar[CheckpointSource]
    CHECKPOINT_SOURCE_FORK: _ClassVar[CheckpointSource]

class ThreadsSortBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    THREADS_SORT_BY_UNSPECIFIED: _ClassVar[ThreadsSortBy]
    THREADS_SORT_BY_THREAD_ID: _ClassVar[ThreadsSortBy]
    THREADS_SORT_BY_CREATED_AT: _ClassVar[ThreadsSortBy]
    THREADS_SORT_BY_UPDATED_AT: _ClassVar[ThreadsSortBy]
    THREADS_SORT_BY_STATUS: _ClassVar[ThreadsSortBy]

class RunStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RUN_STATUS_PENDING: _ClassVar[RunStatus]
    RUN_STATUS_RUNNING: _ClassVar[RunStatus]
    RUN_STATUS_ERROR: _ClassVar[RunStatus]
    RUN_STATUS_SUCCESS: _ClassVar[RunStatus]
    RUN_STATUS_TIMEOUT: _ClassVar[RunStatus]
    RUN_STATUS_INTERRUPTED: _ClassVar[RunStatus]

class MultitaskStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MULTITASK_STRATEGY_UNSPECIFIED: _ClassVar[MultitaskStrategy]
    MULTITASK_STRATEGY_REJECT: _ClassVar[MultitaskStrategy]
    MULTITASK_STRATEGY_ROLLBACK: _ClassVar[MultitaskStrategy]
    MULTITASK_STRATEGY_INTERRUPT: _ClassVar[MultitaskStrategy]
    MULTITASK_STRATEGY_ENQUEUE: _ClassVar[MultitaskStrategy]

class StreamMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STREAM_MODE_UNSPECIFIED: _ClassVar[StreamMode]
    STREAM_MODE_VALUES: _ClassVar[StreamMode]
    STREAM_MODE_MESSAGES: _ClassVar[StreamMode]
    STREAM_MODE_UPDATES: _ClassVar[StreamMode]
    STREAM_MODE_EVENTS: _ClassVar[StreamMode]
    STREAM_MODE_DEBUG: _ClassVar[StreamMode]
    STREAM_MODE_TASKS: _ClassVar[StreamMode]
    STREAM_MODE_CHECKPOINTS: _ClassVar[StreamMode]
    STREAM_MODE_CUSTOM: _ClassVar[StreamMode]

class CreateRunBehavior(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REJECT_RUN_IF_THREAD_NOT_EXISTS: _ClassVar[CreateRunBehavior]
    CREATE_THREAD_IF_THREAD_NOT_EXISTS: _ClassVar[CreateRunBehavior]

class CancelRunAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CANCEL_RUN_ACTION_INTERRUPT: _ClassVar[CancelRunAction]
    CANCEL_RUN_ACTION_ROLLBACK: _ClassVar[CancelRunAction]

class CancelRunStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CANCEL_RUN_STATUS_PENDING: _ClassVar[CancelRunStatus]
    CANCEL_RUN_STATUS_RUNNING: _ClassVar[CancelRunStatus]
    CANCEL_RUN_STATUS_ALL: _ClassVar[CancelRunStatus]
RAISE: OnConflictBehavior
DO_NOTHING: OnConflictBehavior
DESC: SortOrder
ASC: SortOrder
UNSPECIFIED: AssistantsSortBy
ASSISTANT_ID: AssistantsSortBy
GRAPH_ID: AssistantsSortBy
NAME: AssistantsSortBy
CREATED_AT: AssistantsSortBy
UPDATED_AT: AssistantsSortBy
THREAD_STATUS_IDLE: ThreadStatus
THREAD_STATUS_BUSY: ThreadStatus
THREAD_STATUS_INTERRUPTED: ThreadStatus
THREAD_STATUS_ERROR: ThreadStatus
THREAD_TTL_STRATEGY_DELETE: ThreadTTLStrategy
CHECKPOINT_SOURCE_UNSPECIFIED: CheckpointSource
CHECKPOINT_SOURCE_INPUT: CheckpointSource
CHECKPOINT_SOURCE_LOOP: CheckpointSource
CHECKPOINT_SOURCE_UPDATE: CheckpointSource
CHECKPOINT_SOURCE_FORK: CheckpointSource
THREADS_SORT_BY_UNSPECIFIED: ThreadsSortBy
THREADS_SORT_BY_THREAD_ID: ThreadsSortBy
THREADS_SORT_BY_CREATED_AT: ThreadsSortBy
THREADS_SORT_BY_UPDATED_AT: ThreadsSortBy
THREADS_SORT_BY_STATUS: ThreadsSortBy
RUN_STATUS_PENDING: RunStatus
RUN_STATUS_RUNNING: RunStatus
RUN_STATUS_ERROR: RunStatus
RUN_STATUS_SUCCESS: RunStatus
RUN_STATUS_TIMEOUT: RunStatus
RUN_STATUS_INTERRUPTED: RunStatus
MULTITASK_STRATEGY_UNSPECIFIED: MultitaskStrategy
MULTITASK_STRATEGY_REJECT: MultitaskStrategy
MULTITASK_STRATEGY_ROLLBACK: MultitaskStrategy
MULTITASK_STRATEGY_INTERRUPT: MultitaskStrategy
MULTITASK_STRATEGY_ENQUEUE: MultitaskStrategy
STREAM_MODE_UNSPECIFIED: StreamMode
STREAM_MODE_VALUES: StreamMode
STREAM_MODE_MESSAGES: StreamMode
STREAM_MODE_UPDATES: StreamMode
STREAM_MODE_EVENTS: StreamMode
STREAM_MODE_DEBUG: StreamMode
STREAM_MODE_TASKS: StreamMode
STREAM_MODE_CHECKPOINTS: StreamMode
STREAM_MODE_CUSTOM: StreamMode
REJECT_RUN_IF_THREAD_NOT_EXISTS: CreateRunBehavior
CREATE_THREAD_IF_THREAD_NOT_EXISTS: CreateRunBehavior
CANCEL_RUN_ACTION_INTERRUPT: CancelRunAction
CANCEL_RUN_ACTION_ROLLBACK: CancelRunAction
CANCEL_RUN_STATUS_PENDING: CancelRunStatus
CANCEL_RUN_STATUS_RUNNING: CancelRunStatus
CANCEL_RUN_STATUS_ALL: CancelRunStatus

class Tags(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class EqAuthFilter(_message.Message):
    __slots__ = ("match",)
    MATCH_FIELD_NUMBER: _ClassVar[int]
    match: str
    def __init__(self, match: _Optional[str] = ...) -> None: ...

class ContainsAuthFilter(_message.Message):
    __slots__ = ("matches",)
    MATCHES_FIELD_NUMBER: _ClassVar[int]
    matches: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Value]
    def __init__(self, matches: _Optional[_Iterable[_Union[_struct_pb2.Value, _Mapping]]] = ...) -> None: ...

class AuthFilter(_message.Message):
    __slots__ = ("eq", "contains")
    EQ_FIELD_NUMBER: _ClassVar[int]
    CONTAINS_FIELD_NUMBER: _ClassVar[int]
    eq: EqAuthFilter
    contains: ContainsAuthFilter
    def __init__(self, eq: _Optional[_Union[EqAuthFilter, _Mapping]] = ..., contains: _Optional[_Union[ContainsAuthFilter, _Mapping]] = ...) -> None: ...

class UUID(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class CountResponse(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class Assistant(_message.Message):
    __slots__ = ("assistant_id", "graph_id", "version", "created_at", "updated_at", "config", "context", "metadata", "name", "description")
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    graph_id: str
    version: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    config: _engine_common_pb2.EngineRunnableConfig
    context: _struct_pb2.Struct
    metadata: _struct_pb2.Struct
    name: str
    description: str
    def __init__(self, assistant_id: _Optional[str] = ..., graph_id: _Optional[str] = ..., version: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class AssistantVersion(_message.Message):
    __slots__ = ("assistant_id", "graph_id", "version", "created_at", "config", "context", "metadata", "name", "description")
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    graph_id: str
    version: int
    created_at: _timestamp_pb2.Timestamp
    config: _engine_common_pb2.EngineRunnableConfig
    context: _struct_pb2.Struct
    metadata: _struct_pb2.Struct
    name: str
    description: str
    def __init__(self, assistant_id: _Optional[str] = ..., graph_id: _Optional[str] = ..., version: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class CreateAssistantRequest(_message.Message):
    __slots__ = ("assistant_id", "graph_id", "filters", "if_exists", "config", "context", "name", "description", "metadata")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    IF_EXISTS_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    graph_id: str
    filters: _containers.MessageMap[str, AuthFilter]
    if_exists: OnConflictBehavior
    config: _engine_common_pb2.EngineRunnableConfig
    context: _struct_pb2.Struct
    name: str
    description: str
    metadata: _struct_pb2.Struct
    def __init__(self, assistant_id: _Optional[str] = ..., graph_id: _Optional[str] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ..., if_exists: _Optional[_Union[OnConflictBehavior, str]] = ..., config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetAssistantRequest(_message.Message):
    __slots__ = ("assistant_id", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, assistant_id: _Optional[str] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class PatchAssistantRequest(_message.Message):
    __slots__ = ("assistant_id", "filters", "graph_id", "config", "context", "name", "description", "metadata")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    filters: _containers.MessageMap[str, AuthFilter]
    graph_id: str
    config: _engine_common_pb2.EngineRunnableConfig
    context: _struct_pb2.Struct
    name: str
    description: str
    metadata: _struct_pb2.Struct
    def __init__(self, assistant_id: _Optional[str] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ..., graph_id: _Optional[str] = ..., config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class DeleteAssistantRequest(_message.Message):
    __slots__ = ("assistant_id", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, assistant_id: _Optional[str] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class DeleteAssistantsResponse(_message.Message):
    __slots__ = ("assistant_ids",)
    ASSISTANT_IDS_FIELD_NUMBER: _ClassVar[int]
    assistant_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, assistant_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class SetLatestAssistantRequest(_message.Message):
    __slots__ = ("assistant_id", "version", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    version: int
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, assistant_id: _Optional[str] = ..., version: _Optional[int] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class SearchAssistantsRequest(_message.Message):
    __slots__ = ("filters", "graph_id", "metadata", "limit", "offset", "sort_by", "sort_order", "select")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SELECT_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.MessageMap[str, AuthFilter]
    graph_id: str
    metadata: _struct_pb2.Struct
    limit: int
    offset: int
    sort_by: AssistantsSortBy
    sort_order: SortOrder
    select: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, filters: _Optional[_Mapping[str, AuthFilter]] = ..., graph_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., sort_by: _Optional[_Union[AssistantsSortBy, str]] = ..., sort_order: _Optional[_Union[SortOrder, str]] = ..., select: _Optional[_Iterable[str]] = ...) -> None: ...

class SearchAssistantsResponse(_message.Message):
    __slots__ = ("assistants",)
    ASSISTANTS_FIELD_NUMBER: _ClassVar[int]
    assistants: _containers.RepeatedCompositeFieldContainer[Assistant]
    def __init__(self, assistants: _Optional[_Iterable[_Union[Assistant, _Mapping]]] = ...) -> None: ...

class GetAssistantVersionsRequest(_message.Message):
    __slots__ = ("assistant_id", "filters", "metadata", "limit", "offset")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    assistant_id: str
    filters: _containers.MessageMap[str, AuthFilter]
    metadata: _struct_pb2.Struct
    limit: int
    offset: int
    def __init__(self, assistant_id: _Optional[str] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetAssistantVersionsResponse(_message.Message):
    __slots__ = ("versions",)
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedCompositeFieldContainer[AssistantVersion]
    def __init__(self, versions: _Optional[_Iterable[_Union[AssistantVersion, _Mapping]]] = ...) -> None: ...

class CountAssistantsRequest(_message.Message):
    __slots__ = ("filters", "graph_id", "metadata")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.MessageMap[str, AuthFilter]
    graph_id: str
    metadata: _struct_pb2.Struct
    def __init__(self, filters: _Optional[_Mapping[str, AuthFilter]] = ..., graph_id: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class TruncateRequest(_message.Message):
    __slots__ = ("runs", "threads", "assistants", "checkpointer", "store")
    RUNS_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    ASSISTANTS_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINTER_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    runs: bool
    threads: bool
    assistants: bool
    checkpointer: bool
    store: bool
    def __init__(self, runs: bool = ..., threads: bool = ..., assistants: bool = ..., checkpointer: bool = ..., store: bool = ...) -> None: ...

class ThreadTTLConfig(_message.Message):
    __slots__ = ("strategy", "default_ttl", "sweep_interval_minutes")
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_TTL_FIELD_NUMBER: _ClassVar[int]
    SWEEP_INTERVAL_MINUTES_FIELD_NUMBER: _ClassVar[int]
    strategy: ThreadTTLStrategy
    default_ttl: float
    sweep_interval_minutes: int
    def __init__(self, strategy: _Optional[_Union[ThreadTTLStrategy, str]] = ..., default_ttl: _Optional[float] = ..., sweep_interval_minutes: _Optional[int] = ...) -> None: ...

class Fragment(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    def __init__(self, value: _Optional[bytes] = ...) -> None: ...

class CheckpointTask(_message.Message):
    __slots__ = ("id", "name", "error", "interrupts", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    error: str
    interrupts: _containers.RepeatedCompositeFieldContainer[_struct_pb2.Struct]
    state: _struct_pb2.Struct
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., error: _Optional[str] = ..., interrupts: _Optional[_Iterable[_Union[_struct_pb2.Struct, _Mapping]]] = ..., state: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CheckpointMetadata(_message.Message):
    __slots__ = ("source", "step", "parents")
    class ParentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    PARENTS_FIELD_NUMBER: _ClassVar[int]
    source: CheckpointSource
    step: int
    parents: _containers.ScalarMap[str, str]
    def __init__(self, source: _Optional[_Union[CheckpointSource, str]] = ..., step: _Optional[int] = ..., parents: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CheckpointPayload(_message.Message):
    __slots__ = ("config", "metadata", "values", "next", "parent_config", "tasks")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    PARENT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    config: _engine_common_pb2.EngineRunnableConfig
    metadata: CheckpointMetadata
    values: _struct_pb2.Struct
    next: _containers.RepeatedScalarFieldContainer[str]
    parent_config: _engine_common_pb2.EngineRunnableConfig
    tasks: _containers.RepeatedCompositeFieldContainer[CheckpointTask]
    def __init__(self, config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., metadata: _Optional[_Union[CheckpointMetadata, _Mapping]] = ..., values: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., next: _Optional[_Iterable[str]] = ..., parent_config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., tasks: _Optional[_Iterable[_Union[CheckpointTask, _Mapping]]] = ...) -> None: ...

class Interrupt(_message.Message):
    __slots__ = ("id", "value", "when", "resumable", "ns")
    ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    RESUMABLE_FIELD_NUMBER: _ClassVar[int]
    NS_FIELD_NUMBER: _ClassVar[int]
    id: str
    value: bytes
    when: str
    resumable: bool
    ns: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., value: _Optional[bytes] = ..., when: _Optional[str] = ..., resumable: bool = ..., ns: _Optional[_Iterable[str]] = ...) -> None: ...

class Interrupts(_message.Message):
    __slots__ = ("interrupts",)
    INTERRUPTS_FIELD_NUMBER: _ClassVar[int]
    interrupts: _containers.RepeatedCompositeFieldContainer[Interrupt]
    def __init__(self, interrupts: _Optional[_Iterable[_Union[Interrupt, _Mapping]]] = ...) -> None: ...

class Thread(_message.Message):
    __slots__ = ("thread_id", "created_at", "updated_at", "metadata", "config", "status", "values", "interrupts", "error")
    class InterruptsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Interrupts
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Interrupts, _Mapping]] = ...) -> None: ...
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    INTERRUPTS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    metadata: Fragment
    config: Fragment
    status: ThreadStatus
    values: Fragment
    interrupts: _containers.MessageMap[str, Interrupts]
    error: Fragment
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., metadata: _Optional[_Union[Fragment, _Mapping]] = ..., config: _Optional[_Union[Fragment, _Mapping]] = ..., status: _Optional[_Union[ThreadStatus, str]] = ..., values: _Optional[_Union[Fragment, _Mapping]] = ..., interrupts: _Optional[_Mapping[str, Interrupts]] = ..., error: _Optional[_Union[Fragment, _Mapping]] = ...) -> None: ...

class CreateThreadRequest(_message.Message):
    __slots__ = ("thread_id", "filters", "if_exists", "metadata", "ttl")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    IF_EXISTS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TTL_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    if_exists: OnConflictBehavior
    metadata: _struct_pb2.Struct
    ttl: ThreadTTLConfig
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ..., if_exists: _Optional[_Union[OnConflictBehavior, str]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., ttl: _Optional[_Union[ThreadTTLConfig, _Mapping]] = ...) -> None: ...

class GetThreadRequest(_message.Message):
    __slots__ = ("thread_id", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class PatchThreadRequest(_message.Message):
    __slots__ = ("thread_id", "filters", "metadata", "ttl")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TTL_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    metadata: _struct_pb2.Struct
    ttl: ThreadTTLConfig
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., ttl: _Optional[_Union[ThreadTTLConfig, _Mapping]] = ...) -> None: ...

class DeleteThreadRequest(_message.Message):
    __slots__ = ("thread_id", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class CopyThreadRequest(_message.Message):
    __slots__ = ("thread_id", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class SearchThreadsRequest(_message.Message):
    __slots__ = ("filters", "metadata", "values", "status", "limit", "offset", "sort_by", "sort_order", "select")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SELECT_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.MessageMap[str, AuthFilter]
    metadata: _struct_pb2.Struct
    values: _struct_pb2.Struct
    status: ThreadStatus
    limit: int
    offset: int
    sort_by: ThreadsSortBy
    sort_order: SortOrder
    select: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, filters: _Optional[_Mapping[str, AuthFilter]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., values: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., status: _Optional[_Union[ThreadStatus, str]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., sort_by: _Optional[_Union[ThreadsSortBy, str]] = ..., sort_order: _Optional[_Union[SortOrder, str]] = ..., select: _Optional[_Iterable[str]] = ...) -> None: ...

class SearchThreadsResponse(_message.Message):
    __slots__ = ("threads",)
    THREADS_FIELD_NUMBER: _ClassVar[int]
    threads: _containers.RepeatedCompositeFieldContainer[Thread]
    def __init__(self, threads: _Optional[_Iterable[_Union[Thread, _Mapping]]] = ...) -> None: ...

class CountThreadsRequest(_message.Message):
    __slots__ = ("filters", "metadata", "values", "status")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.MessageMap[str, AuthFilter]
    metadata: _struct_pb2.Struct
    values: _struct_pb2.Struct
    status: ThreadStatus
    def __init__(self, filters: _Optional[_Mapping[str, AuthFilter]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., values: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., status: _Optional[_Union[ThreadStatus, str]] = ...) -> None: ...

class SweepThreadsTTLResponse(_message.Message):
    __slots__ = ("expired", "deleted")
    EXPIRED_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    expired: int
    deleted: int
    def __init__(self, expired: _Optional[int] = ..., deleted: _Optional[int] = ...) -> None: ...

class SweepThreadsTTLRequest(_message.Message):
    __slots__ = ("batch_size", "limit")
    BATCH_SIZE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    batch_size: int
    limit: int
    def __init__(self, batch_size: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class SetThreadStatusRequest(_message.Message):
    __slots__ = ("thread_id", "status", "checkpoint", "exception", "expected_status")
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_STATUS_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    status: ThreadStatus
    checkpoint: CheckpointPayload
    exception: _struct_pb2.Struct
    expected_status: _containers.RepeatedScalarFieldContainer[ThreadStatus]
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., status: _Optional[_Union[ThreadStatus, str]] = ..., checkpoint: _Optional[_Union[CheckpointPayload, _Mapping]] = ..., exception: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., expected_status: _Optional[_Iterable[_Union[ThreadStatus, str]]] = ...) -> None: ...

class SetThreadJointStatusRequest(_message.Message):
    __slots__ = ("thread_id", "run_id", "run_status", "graph_id", "checkpoint", "exception")
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_STATUS_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    run_id: UUID
    run_status: str
    graph_id: str
    checkpoint: CheckpointPayload
    exception: _struct_pb2.Struct
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., run_id: _Optional[_Union[UUID, _Mapping]] = ..., run_status: _Optional[str] = ..., graph_id: _Optional[str] = ..., checkpoint: _Optional[_Union[CheckpointPayload, _Mapping]] = ..., exception: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class JointRollbackRequest(_message.Message):
    __slots__ = ("thread_id", "run_id", "graph_id", "checkpoint", "exception")
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    run_id: UUID
    graph_id: str
    checkpoint: CheckpointPayload
    exception: _struct_pb2.Struct
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., run_id: _Optional[_Union[UUID, _Mapping]] = ..., graph_id: _Optional[str] = ..., checkpoint: _Optional[_Union[CheckpointPayload, _Mapping]] = ..., exception: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class RunKwargs(_message.Message):
    __slots__ = ("config", "context", "input", "command", "stream_mode", "interrupt_before", "interrupt_after", "webhook", "feedback_keys", "temporary", "subgraphs", "resumable", "checkpoint_during", "durability")
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    STREAM_MODE_FIELD_NUMBER: _ClassVar[int]
    INTERRUPT_BEFORE_FIELD_NUMBER: _ClassVar[int]
    INTERRUPT_AFTER_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_KEYS_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_FIELD_NUMBER: _ClassVar[int]
    SUBGRAPHS_FIELD_NUMBER: _ClassVar[int]
    RESUMABLE_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINT_DURING_FIELD_NUMBER: _ClassVar[int]
    DURABILITY_FIELD_NUMBER: _ClassVar[int]
    config: _engine_common_pb2.EngineRunnableConfig
    context: _struct_pb2.Struct
    input: _struct_pb2.Struct
    command: _struct_pb2.Struct
    stream_mode: StreamMode
    interrupt_before: _containers.RepeatedScalarFieldContainer[str]
    interrupt_after: _containers.RepeatedScalarFieldContainer[str]
    webhook: str
    feedback_keys: _containers.RepeatedScalarFieldContainer[str]
    temporary: bool
    subgraphs: bool
    resumable: bool
    checkpoint_during: bool
    durability: str
    def __init__(self, config: _Optional[_Union[_engine_common_pb2.EngineRunnableConfig, _Mapping]] = ..., context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., command: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., stream_mode: _Optional[_Union[StreamMode, str]] = ..., interrupt_before: _Optional[_Iterable[str]] = ..., interrupt_after: _Optional[_Iterable[str]] = ..., webhook: _Optional[str] = ..., feedback_keys: _Optional[_Iterable[str]] = ..., temporary: bool = ..., subgraphs: bool = ..., resumable: bool = ..., checkpoint_during: bool = ..., durability: _Optional[str] = ...) -> None: ...

class Run(_message.Message):
    __slots__ = ("run_id", "thread_id", "assistant_id", "created_at", "updated_at", "status", "metadata", "kwargs", "multitask_strategy")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    MULTITASK_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    run_id: UUID
    thread_id: UUID
    assistant_id: UUID
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    status: RunStatus
    metadata: Fragment
    kwargs: RunKwargs
    multitask_strategy: MultitaskStrategy
    def __init__(self, run_id: _Optional[_Union[UUID, _Mapping]] = ..., thread_id: _Optional[_Union[UUID, _Mapping]] = ..., assistant_id: _Optional[_Union[UUID, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[RunStatus, str]] = ..., metadata: _Optional[_Union[Fragment, _Mapping]] = ..., kwargs: _Optional[_Union[RunKwargs, _Mapping]] = ..., multitask_strategy: _Optional[_Union[MultitaskStrategy, str]] = ...) -> None: ...

class QueueStats(_message.Message):
    __slots__ = ("n_pending", "n_running", "pending_runs_wait_time_max_secs", "pending_runs_wait_time_med_secs")
    N_PENDING_FIELD_NUMBER: _ClassVar[int]
    N_RUNNING_FIELD_NUMBER: _ClassVar[int]
    PENDING_RUNS_WAIT_TIME_MAX_SECS_FIELD_NUMBER: _ClassVar[int]
    PENDING_RUNS_WAIT_TIME_MED_SECS_FIELD_NUMBER: _ClassVar[int]
    n_pending: int
    n_running: int
    pending_runs_wait_time_max_secs: float
    pending_runs_wait_time_med_secs: float
    def __init__(self, n_pending: _Optional[int] = ..., n_running: _Optional[int] = ..., pending_runs_wait_time_max_secs: _Optional[float] = ..., pending_runs_wait_time_med_secs: _Optional[float] = ...) -> None: ...

class NextRunRequest(_message.Message):
    __slots__ = ("wait", "limit")
    WAIT_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    wait: bool
    limit: int
    def __init__(self, wait: bool = ..., limit: _Optional[int] = ...) -> None: ...

class RunWithAttempt(_message.Message):
    __slots__ = ("run", "attempt")
    RUN_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    run: Run
    attempt: int
    def __init__(self, run: _Optional[_Union[Run, _Mapping]] = ..., attempt: _Optional[int] = ...) -> None: ...

class NextRunResponse(_message.Message):
    __slots__ = ("runs",)
    RUNS_FIELD_NUMBER: _ClassVar[int]
    runs: _containers.RepeatedCompositeFieldContainer[RunWithAttempt]
    def __init__(self, runs: _Optional[_Iterable[_Union[RunWithAttempt, _Mapping]]] = ...) -> None: ...

class CreateRunRequest(_message.Message):
    __slots__ = ("assistant_id", "kwargs", "filters", "thread_id", "user_id", "run_id", "status", "metadata", "prevent_insert_if_inflight", "multitask_strategy", "if_not_exists", "after_seconds")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    KWARGS_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PREVENT_INSERT_IF_INFLIGHT_FIELD_NUMBER: _ClassVar[int]
    MULTITASK_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    IF_NOT_EXISTS_FIELD_NUMBER: _ClassVar[int]
    AFTER_SECONDS_FIELD_NUMBER: _ClassVar[int]
    assistant_id: UUID
    kwargs: _struct_pb2.Struct
    filters: _containers.MessageMap[str, AuthFilter]
    thread_id: UUID
    user_id: str
    run_id: UUID
    status: RunStatus
    metadata: _struct_pb2.Struct
    prevent_insert_if_inflight: bool
    multitask_strategy: MultitaskStrategy
    if_not_exists: CreateRunBehavior
    after_seconds: int
    def __init__(self, assistant_id: _Optional[_Union[UUID, _Mapping]] = ..., kwargs: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ..., thread_id: _Optional[_Union[UUID, _Mapping]] = ..., user_id: _Optional[str] = ..., run_id: _Optional[_Union[UUID, _Mapping]] = ..., status: _Optional[_Union[RunStatus, str]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., prevent_insert_if_inflight: bool = ..., multitask_strategy: _Optional[_Union[MultitaskStrategy, str]] = ..., if_not_exists: _Optional[_Union[CreateRunBehavior, str]] = ..., after_seconds: _Optional[int] = ...) -> None: ...

class GetRunRequest(_message.Message):
    __slots__ = ("run_id", "thread_id", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    run_id: UUID
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, run_id: _Optional[_Union[UUID, _Mapping]] = ..., thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class DeleteRunRequest(_message.Message):
    __slots__ = ("run_id", "thread_id", "filters")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    run_id: UUID
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    def __init__(self, run_id: _Optional[_Union[UUID, _Mapping]] = ..., thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ...) -> None: ...

class CancelRunIdsTarget(_message.Message):
    __slots__ = ("thread_id", "run_ids")
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_IDS_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    run_ids: _containers.RepeatedCompositeFieldContainer[UUID]
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., run_ids: _Optional[_Iterable[_Union[UUID, _Mapping]]] = ...) -> None: ...

class CancelStatusTarget(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: CancelRunStatus
    def __init__(self, status: _Optional[_Union[CancelRunStatus, str]] = ...) -> None: ...

class CancelRunRequest(_message.Message):
    __slots__ = ("filters", "run_ids", "status", "action")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    RUN_IDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.MessageMap[str, AuthFilter]
    run_ids: CancelRunIdsTarget
    status: CancelStatusTarget
    action: CancelRunAction
    def __init__(self, filters: _Optional[_Mapping[str, AuthFilter]] = ..., run_ids: _Optional[_Union[CancelRunIdsTarget, _Mapping]] = ..., status: _Optional[_Union[CancelStatusTarget, _Mapping]] = ..., action: _Optional[_Union[CancelRunAction, str]] = ...) -> None: ...

class SearchRunsRequest(_message.Message):
    __slots__ = ("thread_id", "filters", "limit", "offset", "status", "select")
    class FiltersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AuthFilter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AuthFilter, _Mapping]] = ...) -> None: ...
    THREAD_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SELECT_FIELD_NUMBER: _ClassVar[int]
    thread_id: UUID
    filters: _containers.MessageMap[str, AuthFilter]
    limit: int
    offset: int
    status: RunStatus
    select: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, thread_id: _Optional[_Union[UUID, _Mapping]] = ..., filters: _Optional[_Mapping[str, AuthFilter]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., status: _Optional[_Union[RunStatus, str]] = ..., select: _Optional[_Iterable[str]] = ...) -> None: ...

class SearchRunsResponse(_message.Message):
    __slots__ = ("runs",)
    RUNS_FIELD_NUMBER: _ClassVar[int]
    runs: _containers.RepeatedCompositeFieldContainer[Run]
    def __init__(self, runs: _Optional[_Iterable[_Union[Run, _Mapping]]] = ...) -> None: ...

class SetRunStatusRequest(_message.Message):
    __slots__ = ("run_id", "status")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    run_id: UUID
    status: RunStatus
    def __init__(self, run_id: _Optional[_Union[UUID, _Mapping]] = ..., status: _Optional[_Union[RunStatus, str]] = ...) -> None: ...

class SweepRunsResponse(_message.Message):
    __slots__ = ("run_ids",)
    RUN_IDS_FIELD_NUMBER: _ClassVar[int]
    run_ids: _containers.RepeatedCompositeFieldContainer[UUID]
    def __init__(self, run_ids: _Optional[_Iterable[_Union[UUID, _Mapping]]] = ...) -> None: ...
