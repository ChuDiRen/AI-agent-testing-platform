"""gRPC-based operations for LangGraph API."""

from __future__ import annotations

import asyncio
import functools
from collections.abc import AsyncIterator
from datetime import UTC
from http import HTTPStatus
from typing import Any, overload
from uuid import UUID

import orjson
import structlog
from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct  # type: ignore[import]
from grpc import StatusCode
from grpc.aio import AioRpcError
from langgraph_sdk.schema import Config
from starlette.exceptions import HTTPException

from langgraph_api.grpc import config_conversion
from langgraph_api.schema import (
    Assistant,
    AssistantSelectField,
    Context,
    MetadataInput,
    OnConflictBehavior,
    Thread,
    ThreadSelectField,
    ThreadStatus,
)
from langgraph_api.serde import json_dumpb, json_loads

from .client import get_shared_client
from .generated import core_api_pb2 as pb

GRPC_STATUS_TO_HTTP_STATUS = {
    StatusCode.NOT_FOUND: HTTPStatus.NOT_FOUND,
    StatusCode.ALREADY_EXISTS: HTTPStatus.CONFLICT,
    StatusCode.INVALID_ARGUMENT: HTTPStatus.UNPROCESSABLE_ENTITY,
}

logger = structlog.stdlib.get_logger(__name__)


def map_if_exists(if_exists: str) -> pb.OnConflictBehavior:
    if if_exists == "do_nothing":
        return pb.OnConflictBehavior.DO_NOTHING
    return pb.OnConflictBehavior.RAISE


@overload
def consolidate_config_and_context(
    config: Config | None, context: None
) -> tuple[Config, None]: ...


@overload
def consolidate_config_and_context(
    config: Config | None, context: Context
) -> tuple[Config, Context]: ...


def consolidate_config_and_context(
    config: Config | None, context: Context | None
) -> tuple[Config, Context | None]:
    """Return a new (config, context) with consistent configurable/context.

    Does not mutate the passed-in objects. If both configurable and context
    are provided, raises 400. If only one is provided, mirrors it to the other.
    """
    cfg: Config = Config(config or {})
    ctx: Context | None = dict(context) if context is not None else None
    configurable = cfg.get("configurable")

    if configurable and ctx:
        raise HTTPException(
            status_code=400,
            detail="Cannot specify both configurable and context. Prefer setting context alone."
            " Context was introduced in LangGraph 0.6.0 and "
            "is the long term planned replacement for configurable.",
        )

    if configurable:
        ctx = configurable
    elif ctx is not None:
        cfg["configurable"] = ctx

    return cfg, ctx


def dict_to_struct(data: dict[str, Any]) -> Struct:
    """Convert a dictionary to a protobuf Struct."""
    struct = Struct()
    if data:
        struct.update(data)
    return struct


def struct_to_dict(struct: Struct) -> dict[str, Any]:
    """Convert a protobuf Struct to a dictionary."""
    return MessageToDict(struct) if struct else {}


def proto_to_assistant(proto_assistant: pb.Assistant) -> Assistant:
    """Convert protobuf Assistant to dictionary format."""
    # Preserve None for optional scalar fields by checking presence via HasField
    description = (
        proto_assistant.description if proto_assistant.HasField("description") else None
    )
    return {
        "assistant_id": proto_assistant.assistant_id,
        "graph_id": proto_assistant.graph_id,
        "version": proto_assistant.version,
        "created_at": proto_assistant.created_at.ToDatetime(tzinfo=UTC),
        "updated_at": proto_assistant.updated_at.ToDatetime(tzinfo=UTC),
        "config": config_conversion.config_from_proto(proto_assistant.config),
        "context": struct_to_dict(proto_assistant.context),
        "metadata": struct_to_dict(proto_assistant.metadata),
        "name": proto_assistant.name,
        "description": description,
    }


THREAD_STATUS_TO_PB = {
    "idle": pb.ThreadStatus.THREAD_STATUS_IDLE,
    "busy": pb.ThreadStatus.THREAD_STATUS_BUSY,
    "interrupted": pb.ThreadStatus.THREAD_STATUS_INTERRUPTED,
    "error": pb.ThreadStatus.THREAD_STATUS_ERROR,
}

THREAD_STATUS_FROM_PB = {
    pb.ThreadStatus.THREAD_STATUS_IDLE: "idle",
    pb.ThreadStatus.THREAD_STATUS_BUSY: "busy",
    pb.ThreadStatus.THREAD_STATUS_INTERRUPTED: "interrupted",
    pb.ThreadStatus.THREAD_STATUS_ERROR: "error",
}

THREAD_SORT_BY_MAP = {
    "thread_id": pb.ThreadsSortBy.THREADS_SORT_BY_THREAD_ID,
    "created_at": pb.ThreadsSortBy.THREADS_SORT_BY_CREATED_AT,
    "updated_at": pb.ThreadsSortBy.THREADS_SORT_BY_UPDATED_AT,
    "status": pb.ThreadsSortBy.THREADS_SORT_BY_STATUS,
}

THREAD_TTL_STRATEGY_MAP = {"delete": pb.ThreadTTLStrategy.THREAD_TTL_STRATEGY_DELETE}


def _map_thread_status(status: ThreadStatus | None) -> pb.ThreadStatus | None:
    if status is None:
        return None
    return THREAD_STATUS_TO_PB.get(status)


def _map_threads_sort_by(sort_by: str | None) -> pb.ThreadsSortBy:
    if not sort_by:
        return pb.ThreadsSortBy.THREADS_SORT_BY_CREATED_AT
    return THREAD_SORT_BY_MAP.get(
        sort_by.lower(), pb.ThreadsSortBy.THREADS_SORT_BY_CREATED_AT
    )


def _map_thread_ttl(ttl: dict[str, Any] | None) -> pb.ThreadTTLConfig | None:
    if not ttl:
        return None

    config = pb.ThreadTTLConfig()
    strategy = ttl.get("strategy")
    if strategy:
        mapped_strategy = THREAD_TTL_STRATEGY_MAP.get(str(strategy).lower())
        if mapped_strategy is None:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f"Invalid thread TTL strategy: {strategy}. Expected one of ['delete']",
            )
        config.strategy = mapped_strategy

    ttl_value = ttl.get("ttl", ttl.get("default_ttl"))
    if ttl_value is not None:
        config.default_ttl = float(ttl_value)

    sweep_interval = ttl.get("sweep_interval_minutes")
    if sweep_interval is not None:
        config.sweep_interval_minutes = int(sweep_interval)

    return config


def fragment_to_value(fragment: pb.Fragment | None) -> Any:
    if fragment is None or not fragment.value:
        return {}
    try:
        return json_loads(fragment.value)
    except orjson.JSONDecodeError:
        logger.warning("Failed to decode fragment", fragment=fragment.value)
        return {}


def _proto_interrupts_to_dict(
    interrupts_map: dict[str, pb.Interrupts],
) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for key, interrupts in interrupts_map.items():
        entries: list[dict[str, Any]] = []
        for interrupt in interrupts.interrupts:
            entry: dict[str, Any] = {
                "id": interrupt.id or None,
                "value": json_loads(interrupt.value),
            }
            if interrupt.when:
                entry["when"] = interrupt.when
            if interrupt.resumable:
                entry["resumable"] = interrupt.resumable
            if interrupt.ns:
                entry["ns"] = list(interrupt.ns)
            entries.append(entry)
        out[key] = entries
    return out


def proto_to_thread(proto_thread: pb.Thread) -> Thread:
    """Convert protobuf Thread to API dictionary format."""
    thread_id = (
        UUID(proto_thread.thread_id.value)
        if proto_thread.HasField("thread_id")
        else None
    )
    if thread_id is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Thread response missing thread_id",
        )
    created_at = (
        proto_thread.created_at.ToDatetime(tzinfo=UTC)
        if proto_thread.HasField("created_at")
        else None
    )
    updated_at = (
        proto_thread.updated_at.ToDatetime(tzinfo=UTC)
        if proto_thread.HasField("updated_at")
        else None
    )
    status = THREAD_STATUS_FROM_PB.get(proto_thread.status, "idle")

    return {
        "thread_id": thread_id,
        "created_at": created_at,
        "updated_at": updated_at,
        "metadata": fragment_to_value(proto_thread.metadata),
        "config": fragment_to_value(proto_thread.config),
        "error": fragment_to_value(proto_thread.error),
        "status": status,  # type: ignore[typeddict-item]
        "values": fragment_to_value(proto_thread.values),
        "interrupts": _proto_interrupts_to_dict(dict(proto_thread.interrupts)),
    }


def exception_to_struct(exception: BaseException | None) -> Struct | None:
    if exception is None:
        return None
    try:
        payload = orjson.loads(json_dumpb(exception))
    except orjson.JSONDecodeError:
        payload = {"error": type(exception).__name__, "message": str(exception)}
    return dict_to_struct(payload)


def _filter_thread_fields(
    thread: Thread, select: list[ThreadSelectField] | None
) -> dict[str, Any]:
    if not select:
        return dict(thread)
    return {field: thread[field] for field in select if field in thread}


def _normalize_uuid(value: UUID | str) -> str:
    return str(value) if isinstance(value, UUID) else str(UUID(str(value)))


def _map_sort_by(sort_by: str | None) -> pb.AssistantsSortBy:
    """Map string sort_by to protobuf enum."""
    if not sort_by:
        return pb.AssistantsSortBy.CREATED_AT

    sort_by_lower = sort_by.lower()
    mapping = {
        "assistant_id": pb.AssistantsSortBy.ASSISTANT_ID,
        "graph_id": pb.AssistantsSortBy.GRAPH_ID,
        "name": pb.AssistantsSortBy.NAME,
        "created_at": pb.AssistantsSortBy.CREATED_AT,
        "updated_at": pb.AssistantsSortBy.UPDATED_AT,
    }
    return mapping.get(sort_by_lower, pb.AssistantsSortBy.CREATED_AT)


def _map_sort_order(sort_order: str | None) -> pb.SortOrder:
    """Map string sort_order to protobuf enum."""
    if sort_order and sort_order.upper() == "ASC":
        return pb.SortOrder.ASC
    return pb.SortOrder.DESC


def _handle_grpc_error(error: AioRpcError) -> None:
    """Handle gRPC errors and convert to appropriate exceptions."""
    raise HTTPException(
        status_code=GRPC_STATUS_TO_HTTP_STATUS.get(
            error.code(), HTTPStatus.INTERNAL_SERVER_ERROR
        ),
        detail=str(error.details()),
    )


class Authenticated:
    """Base class for authenticated operations (matches storage_postgres interface)."""

    resource: str = "assistants"

    @classmethod
    async def handle_event(
        cls,
        ctx: Any,  # Auth context
        action: str,
        value: Any,
    ) -> dict[str, Any] | None:
        """Handle authentication event - stub implementation for now."""
        # TODO: Implement proper auth handling that converts auth context
        # to gRPC AuthFilter format when needed
        return None


def grpc_error_guard(cls):
    """Class decorator to wrap async methods and handle gRPC errors uniformly."""
    for name, attr in list(cls.__dict__.items()):
        func = None
        wrapper_type = None
        if isinstance(attr, staticmethod):
            func = attr.__func__
            wrapper_type = staticmethod
        elif isinstance(attr, classmethod):
            func = attr.__func__
            wrapper_type = classmethod
        elif callable(attr):
            func = attr

        if func and asyncio.iscoroutinefunction(func):

            def make_wrapper(f):
                @functools.wraps(f)
                async def wrapped(*args, **kwargs):
                    try:
                        return await f(*args, **kwargs)
                    except AioRpcError as e:
                        _handle_grpc_error(e)

                return wrapped  # noqa: B023

            wrapped = make_wrapper(func)
            if wrapper_type is staticmethod:
                setattr(cls, name, staticmethod(wrapped))
            elif wrapper_type is classmethod:
                setattr(cls, name, classmethod(wrapped))
            else:
                setattr(cls, name, wrapped)
    return cls


@grpc_error_guard
class Assistants(Authenticated):
    """gRPC-based assistants operations."""

    resource = "assistants"

    @staticmethod
    async def search(
        conn,  # Not used in gRPC implementation
        *,
        graph_id: str | None,
        metadata: MetadataInput,
        limit: int,
        offset: int,
        sort_by: str | None = None,
        sort_order: str | None = None,
        select: list[AssistantSelectField] | None = None,
        ctx: Any = None,
    ) -> tuple[AsyncIterator[Assistant], int | None]:  # type: ignore[return-value]
        """Search assistants via gRPC."""
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx,
            "search",
            {
                "graph_id": graph_id,
                "metadata": metadata,
                "limit": limit,
                "offset": offset,
            },
        )

        # Build the gRPC request
        request = pb.SearchAssistantsRequest(
            filters=auth_filters,
            graph_id=graph_id,
            metadata=dict_to_struct(metadata or {}),
            limit=limit,
            offset=offset,
            sort_by=_map_sort_by(sort_by),
            sort_order=_map_sort_order(sort_order),
            select=select,
        )

        client = await get_shared_client()
        response = await client.assistants.Search(request)

        # Convert response to expected format
        assistants = [
            proto_to_assistant(assistant) for assistant in response.assistants
        ]

        # Determine if there are more results
        # Note: gRPC doesn't return cursor info, so we estimate based on result count
        cursor = offset + limit if len(assistants) == limit else None

        async def generate_results():
            for assistant in assistants:
                yield {
                    k: v for k, v in assistant.items() if select is None or k in select
                }

        return generate_results(), cursor

    @staticmethod
    async def get(
        conn,  # Not used in gRPC implementation
        assistant_id: UUID | str,
        ctx: Any = None,
    ) -> AsyncIterator[Assistant]:  # type: ignore[return-value]
        """Get assistant by ID via gRPC."""
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx, "read", {"assistant_id": str(assistant_id)}
        )

        # Build the gRPC request
        request = pb.GetAssistantRequest(
            assistant_id=str(assistant_id),
            filters=auth_filters or {},
        )

        client = await get_shared_client()
        response = await client.assistants.Get(request)

        # Convert and yield the result
        assistant = proto_to_assistant(response)

        async def generate_result():
            yield assistant

        return generate_result()

    @staticmethod
    async def put(
        conn,  # Not used in gRPC implementation
        assistant_id: UUID | str,
        *,
        graph_id: str,
        config: Config,
        context: Context,
        metadata: MetadataInput,
        if_exists: OnConflictBehavior,
        name: str,
        description: str | None = None,
        ctx: Any = None,
    ) -> AsyncIterator[Assistant]:  # type: ignore[return-value]
        """Create/update assistant via gRPC."""
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx,
            "create",
            {
                "assistant_id": str(assistant_id),
                "graph_id": graph_id,
                "config": config,
                "context": context,
                "metadata": metadata,
                "name": name,
                "description": description,
            },
        )

        config, context = consolidate_config_and_context(config, context)

        on_conflict = map_if_exists(if_exists)

        # Build the gRPC request
        request = pb.CreateAssistantRequest(
            assistant_id=str(assistant_id),
            graph_id=graph_id,
            filters=auth_filters or {},
            if_exists=on_conflict,
            config=config_conversion.config_to_proto(config),
            context=dict_to_struct(context or {}),
            name=name,
            description=description,
            metadata=dict_to_struct(metadata or {}),
        )

        client = await get_shared_client()
        response = await client.assistants.Create(request)

        # Convert and yield the result
        assistant = proto_to_assistant(response)

        async def generate_result():
            yield assistant

        return generate_result()

    @staticmethod
    async def patch(
        conn,  # Not used in gRPC implementation
        assistant_id: UUID | str,
        *,
        config: Config | None = None,
        context: Context | None = None,
        graph_id: str | None = None,
        metadata: MetadataInput | None = None,
        name: str | None = None,
        description: str | None = None,
        ctx: Any = None,
    ) -> AsyncIterator[Assistant]:  # type: ignore[return-value]
        """Update assistant via gRPC."""
        metadata = metadata if metadata is not None else {}
        config = config if config is not None else Config()
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx,
            "update",
            {
                "assistant_id": str(assistant_id),
                "graph_id": graph_id,
                "config": config,
                "context": context,
                "metadata": metadata,
                "name": name,
                "description": description,
            },
        )

        config, context = consolidate_config_and_context(config, context)

        # Build the gRPC request
        request = pb.PatchAssistantRequest(
            assistant_id=str(assistant_id),
            filters=auth_filters or {},
            graph_id=graph_id,
            name=name,
            description=description,
            metadata=dict_to_struct(metadata or {}),
        )

        # Add optional config if provided
        if config:
            request.config.CopyFrom(config_conversion.config_to_proto(config))

        # Add optional context if provided
        if context:
            request.context.CopyFrom(dict_to_struct(context))

        client = await get_shared_client()
        response = await client.assistants.Patch(request)

        # Convert and yield the result
        assistant = proto_to_assistant(response)

        async def generate_result():
            yield assistant

        return generate_result()

    @staticmethod
    async def delete(
        conn,  # Not used in gRPC implementation
        assistant_id: UUID | str,
        ctx: Any = None,
    ) -> AsyncIterator[UUID]:  # type: ignore[return-value]
        """Delete assistant via gRPC."""
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx, "delete", {"assistant_id": str(assistant_id)}
        )

        # Build the gRPC request
        request = pb.DeleteAssistantRequest(
            assistant_id=str(assistant_id),
            filters=auth_filters or {},
        )

        client = await get_shared_client()
        await client.assistants.Delete(request)

        # Return the deleted ID
        async def generate_result():
            yield UUID(str(assistant_id))

        return generate_result()

    @staticmethod
    async def set_latest(
        conn,  # Not used in gRPC implementation
        assistant_id: UUID | str,
        version: int,
        ctx: Any = None,
    ) -> AsyncIterator[Assistant]:  # type: ignore[return-value]
        """Set latest version of assistant via gRPC."""
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx,
            "update",
            {
                "assistant_id": str(assistant_id),
                "version": version,
            },
        )

        # Build the gRPC request
        request = pb.SetLatestAssistantRequest(
            assistant_id=str(assistant_id),
            version=version,
            filters=auth_filters or {},
        )

        client = await get_shared_client()
        response = await client.assistants.SetLatest(request)

        # Convert and yield the result
        assistant = proto_to_assistant(response)

        async def generate_result():
            yield assistant

        return generate_result()

    @staticmethod
    async def get_versions(
        conn,  # Not used in gRPC implementation
        assistant_id: UUID | str,
        metadata: MetadataInput,
        limit: int,
        offset: int,
        ctx: Any = None,
    ) -> AsyncIterator[Assistant]:  # type: ignore[return-value]
        """Get all versions of assistant via gRPC."""
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx,
            "search",
            {"assistant_id": str(assistant_id), "metadata": metadata},
        )

        # Build the gRPC request
        request = pb.GetAssistantVersionsRequest(
            assistant_id=str(assistant_id),
            filters=auth_filters or {},
            metadata=dict_to_struct(metadata or {}),
            limit=limit,
            offset=offset,
        )

        client = await get_shared_client()
        response = await client.assistants.GetVersions(request)

        # Convert and yield the results
        async def generate_results():
            for version in response.versions:
                # Preserve None for optional scalar fields by checking presence
                version_description = (
                    version.description if version.HasField("description") else None
                )
                yield {
                    "assistant_id": version.assistant_id,
                    "graph_id": version.graph_id,
                    "version": version.version,
                    "created_at": version.created_at.ToDatetime(tzinfo=UTC),
                    "config": config_conversion.config_from_proto(version.config),
                    "context": struct_to_dict(version.context),
                    "metadata": struct_to_dict(version.metadata),
                    "name": version.name,
                    "description": version_description,
                }

        return generate_results()

    @staticmethod
    async def count(
        conn,  # Not used in gRPC implementation
        *,
        graph_id: str | None = None,
        metadata: MetadataInput = None,
        ctx: Any = None,
    ) -> int:  # type: ignore[return-value]
        """Count assistants via gRPC."""
        # Handle auth filters
        auth_filters = await Assistants.handle_event(
            ctx, "search", {"graph_id": graph_id, "metadata": metadata}
        )

        # Build the gRPC request
        request = pb.CountAssistantsRequest(
            filters=auth_filters or {},
            graph_id=graph_id,
            metadata=dict_to_struct(metadata or {}),
        )

        client = await get_shared_client()
        response = await client.assistants.Count(request)

        return int(response.count)


def _json_contains(container: Any, subset: dict[str, Any]) -> bool:
    if not subset:
        return True
    if not isinstance(container, dict):
        return False
    for key, value in subset.items():
        if key not in container:
            return False
        candidate = container[key]
        if isinstance(value, dict):
            if not _json_contains(candidate, value):
                return False
        else:
            if candidate != value:
                return False
    return True


@grpc_error_guard
class Threads(Authenticated):
    """gRPC-based threads operations."""

    resource = "threads"

    @staticmethod
    async def search(
        conn,  # Not used in gRPC implementation
        *,
        ids: list[str] | list[UUID] | None = None,
        metadata: MetadataInput,
        values: MetadataInput,
        status: ThreadStatus | None,
        limit: int,
        offset: int,
        sort_by: str | None = None,
        sort_order: str | None = None,
        select: list[ThreadSelectField] | None = None,
        ctx: Any = None,
    ) -> tuple[AsyncIterator[Thread], int | None]:  # type: ignore[return-value]
        metadata = metadata or {}
        values = values or {}

        auth_filters = await Threads.handle_event(
            ctx,
            "search",
            {
                "metadata": metadata,
                "values": values,
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )

        if ids:
            normalized_ids = [_normalize_uuid(thread_id) for thread_id in ids]
            threads: list[Thread] = []
            client = await get_shared_client()
            for thread_id in normalized_ids:
                request = pb.GetThreadRequest(
                    thread_id=pb.UUID(value=_normalize_uuid(thread_id)),
                    filters=auth_filters or {},
                )
                response = await client.threads.Get(request)
                thread = proto_to_thread(response)

                if status and thread["status"] != status:
                    continue
                if metadata and not _json_contains(thread["metadata"], metadata):
                    continue
                if values and not _json_contains(thread.get("values") or {}, values):
                    continue
                threads.append(thread)

            total = len(threads)
            paginated = threads[offset : offset + limit]
            cursor = offset + limit if total > offset + limit else None

            async def generate_results():
                for thread in paginated:
                    yield _filter_thread_fields(thread, select)

            return generate_results(), cursor

        request_kwargs: dict[str, Any] = {
            "filters": auth_filters or {},
            "metadata": dict_to_struct(metadata),
            "values": dict_to_struct(values),
            "limit": limit,
            "offset": offset,
            "sort_by": _map_threads_sort_by(sort_by),
            "sort_order": _map_sort_order(sort_order),
        }

        if status:
            mapped_status = _map_thread_status(status)
            if mapped_status is None:
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail=f"Invalid thread status: {status}",
                )
            request_kwargs["status"] = mapped_status

        if select:
            request_kwargs["select"] = select

        client = await get_shared_client()
        response = await client.threads.Search(
            pb.SearchThreadsRequest(**request_kwargs)
        )

        threads = [proto_to_thread(thread) for thread in response.threads]
        cursor = offset + limit if len(threads) == limit else None

        async def generate_results():
            for thread in threads:
                yield _filter_thread_fields(thread, select)

        return generate_results(), cursor

    @staticmethod
    async def count(
        conn,  # Not used
        *,
        metadata: MetadataInput,
        values: MetadataInput,
        status: ThreadStatus | None,
        ctx: Any = None,
    ) -> int:  # type: ignore[override]
        metadata = metadata or {}
        values = values or {}

        auth_filters = await Threads.handle_event(
            ctx,
            "search",
            {
                "metadata": metadata,
                "values": values,
                "status": status,
            },
        )

        request_kwargs: dict[str, Any] = {
            "filters": auth_filters or {},
            "metadata": dict_to_struct(metadata),
            "values": dict_to_struct(values),
        }
        if status:
            mapped_status = _map_thread_status(status)
            if mapped_status is None:
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail=f"Invalid thread status: {status}",
                )
            request_kwargs["status"] = mapped_status

        client = await get_shared_client()
        response = await client.threads.Count(pb.CountThreadsRequest(**request_kwargs))

        return int(response.count)

    @staticmethod
    async def get(
        conn,  # Not used
        thread_id: UUID | str,
        ctx: Any = None,
    ) -> AsyncIterator[Thread]:  # type: ignore[return-value]
        auth_filters = await Threads.handle_event(
            ctx, "read", {"thread_id": str(thread_id)}
        )

        request = pb.GetThreadRequest(
            thread_id=pb.UUID(value=_normalize_uuid(thread_id)),
            filters=auth_filters or {},
        )
        client = await get_shared_client()
        response = await client.threads.Get(request)

        thread = proto_to_thread(response)

        async def generate_result():
            yield thread

        return generate_result()

    @staticmethod
    async def put(
        conn,  # Not used
        thread_id: UUID | str,
        *,
        metadata: MetadataInput,
        if_exists: OnConflictBehavior,
        ttl: dict[str, Any] | None = None,
        ctx: Any = None,
    ) -> AsyncIterator[Thread]:  # type: ignore[return-value]
        metadata = metadata or {}

        auth_filters = await Threads.handle_event(
            ctx,
            "create",
            {
                "thread_id": str(thread_id),
                "metadata": metadata,
                "if_exists": if_exists,
            },
        )

        request = pb.CreateThreadRequest(
            thread_id=pb.UUID(value=_normalize_uuid(thread_id)),
            filters=auth_filters or {},
            if_exists=map_if_exists(if_exists),
            metadata=dict_to_struct(metadata),
        )
        ttl_config = _map_thread_ttl(ttl)
        if ttl_config is not None:
            request.ttl.CopyFrom(ttl_config)

        client = await get_shared_client()
        response = await client.threads.Create(request)
        thread = proto_to_thread(response)

        async def generate_result():
            yield thread

        return generate_result()

    @staticmethod
    async def patch(
        conn,  # Not used
        thread_id: UUID | str,
        *,
        metadata: MetadataInput,
        ttl: dict[str, Any] | None = None,
        ctx: Any = None,
    ) -> AsyncIterator[Thread]:  # type: ignore[return-value]
        metadata = metadata or {}

        auth_filters = await Threads.handle_event(
            ctx,
            "update",
            {
                "thread_id": str(thread_id),
                "metadata": metadata,
            },
        )

        request = pb.PatchThreadRequest(
            thread_id=pb.UUID(value=_normalize_uuid(thread_id)),
            filters=auth_filters or {},
        )

        if metadata:
            request.metadata.CopyFrom(dict_to_struct(metadata))

        ttl_config = _map_thread_ttl(ttl)
        if ttl_config is not None:
            request.ttl.CopyFrom(ttl_config)

        client = await get_shared_client()
        response = await client.threads.Patch(request)

        thread = proto_to_thread(response)

        async def generate_result():
            yield thread

        return generate_result()

    @staticmethod
    async def delete(
        conn,  # Not used
        thread_id: UUID | str,
        ctx: Any = None,
    ) -> AsyncIterator[UUID]:  # type: ignore[return-value]
        auth_filters = await Threads.handle_event(
            ctx,
            "delete",
            {
                "thread_id": str(thread_id),
            },
        )

        request = pb.DeleteThreadRequest(
            thread_id=pb.UUID(value=_normalize_uuid(thread_id)),
            filters=auth_filters or {},
        )

        client = await get_shared_client()
        response = await client.threads.Delete(request)

        deleted_id = UUID(response.value)

        async def generate_result():
            yield deleted_id

        return generate_result()

    @staticmethod
    async def copy(
        conn,  # Not used
        thread_id: UUID | str,
        ctx: Any = None,
    ) -> AsyncIterator[Thread]:  # type: ignore[return-value]
        auth_filters = await Threads.handle_event(
            ctx,
            "read",
            {
                "thread_id": str(thread_id),
            },
        )

        request = pb.CopyThreadRequest(
            thread_id=pb.UUID(value=_normalize_uuid(thread_id)),
            filters=auth_filters or {},
        )

        client = await get_shared_client()
        response = await client.threads.Copy(request)

        thread = proto_to_thread(response)

        async def generate_result():
            yield thread

        return generate_result()
