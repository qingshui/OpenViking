# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0
"""Observer endpoints for OpenViking HTTP Server.

Provides observability API for monitoring component status.
Mirrors the SDK's client.observer API:
- /api/v1/observer/queue - Queue status
- /api/v1/observer/vikingdb - VikingDB status
- /api/v1/observer/vlm - VLM status
- /api/v1/observer/system - System overall status
"""

from fastapi import APIRouter, Depends

from openviking.server.auth import get_request_context
from openviking.server.dependencies import get_service
from openviking.server.identity import RequestContext
from openviking.server.models import Response
from openviking.service.debug_service import ComponentStatus, SystemStatus
from openviking.storage.queuefs.queue_manager import get_queue_manager
from openviking.storage.observers.queue_observer import QueueObserver
from openviking_cli.utils import run_async

router = APIRouter(prefix="/api/v1/observer", tags=["observer"])


def _component_to_dict(component: ComponentStatus) -> dict:
    """Convert ComponentStatus to dict."""
    return {
        "name": component.name,
        "is_healthy": component.is_healthy,
        "has_errors": component.has_errors,
        "status": component.status,
    }


def _system_to_dict(status: SystemStatus) -> dict:
    """Convert SystemStatus to dict."""
    return {
        "is_healthy": status.is_healthy,
        "errors": status.errors,
        "components": {
            name: _component_to_dict(component) for name, component in status.components.items()
        },
    }


def _queue_to_dict() -> dict:
    """Get queue status as structured dict."""
    try:
        qm = get_queue_manager()
    except Exception:
        return {
            "name": "queue",
            "is_healthy": False,
            "has_errors": True,
            "status": "Queue manager not initialized",
            "queues": {},
            "services": {
                "semantic": {"status": "error", "pending": 0, "processing": 0, "completed": 0, "failed": 0},
                "embedding": {"status": "error", "pending": 0, "processing": 0, "completed": 0, "failed": 0}
            }
        }

    observer = QueueObserver(qm)
    statuses = run_async(observer._queue_manager.check_status())

    queues = {}
    for queue_name, status in statuses.items():
        queues[queue_name] = {
            "pending": status.pending,
            "in_progress": status.in_progress,
            "processed": status.processed,
            "error_count": status.error_count,
        }

    # Build services status
    semantic_status = statuses.get("semantic")
    embedding_status = statuses.get("embedding")

    return {
        "name": "queue",
        "is_healthy": not observer.has_errors(),
        "has_errors": observer.has_errors(),
        "status": observer.get_status_table(),
        "queues": queues,
        "services": {
            "semantic": {
                "status": "running" if not observer.has_errors() else "error",
                "pending": semantic_status.pending if semantic_status else 0,
                "processing": semantic_status.in_progress if semantic_status else 0,
                "completed": semantic_status.processed if semantic_status else 0,
                "failed": semantic_status.error_count if semantic_status else 0
            },
            "embedding": {
                "status": "running" if not observer.has_errors() else "error",
                "pending": embedding_status.pending if embedding_status else 0,
                "processing": embedding_status.in_progress if embedding_status else 0,
                "completed": embedding_status.processed if embedding_status else 0,
                "failed": embedding_status.error_count if embedding_status else 0
            }
        }
    }


@router.get("/queue")
async def observer_queue(
    _ctx: RequestContext = Depends(get_request_context),
):
    """Get queue system status."""
    result = _queue_to_dict()
    return Response(status="ok", result=result)


@router.get("/vikingdb")
async def observer_vikingdb(
    _ctx: RequestContext = Depends(get_request_context),
):
    """Get VikingDB status."""
    service = get_service()
    component = service.debug.observer.vikingdb
    return Response(status="ok", result=_component_to_dict(component))


@router.get("/vlm")
async def observer_vlm(
    _ctx: RequestContext = Depends(get_request_context),
):
    """Get VLM (Vision Language Model) token usage status."""
    service = get_service()
    component = service.debug.observer.vlm
    return Response(status="ok", result=_component_to_dict(component))


@router.get("/transaction")
async def observer_transaction(
    _ctx: RequestContext = Depends(get_request_context),
):
    """Get transaction system status."""
    service = get_service()
    component = service.debug.observer.transaction
    return Response(status="ok", result=_component_to_dict(component))


@router.get("/system")
async def observer_system(
    _ctx: RequestContext = Depends(get_request_context),
):
    """Get system overall status (includes all components)."""
    service = get_service()
    status = service.debug.observer.system
    return Response(status="ok", result=_system_to_dict(status))
