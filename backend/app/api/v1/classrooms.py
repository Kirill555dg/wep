"""
Classroom management endpoints
"""

import asyncio
import time
import uuid

import fastapi
from fastapi import status as http_status
import pydantic
import starlette.websockets as starlette_websockets
from sqlalchemy.ext import asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import pagination as api_pagination
from app.db import session as db_session
from app.domain import errors as domain_errors
from app.core import config as core_config
from app.models import users as user_models
from app.realtime import auth as realtime_auth
from app.realtime import presence as realtime_presence
from app.schemas import communication as communication_schemas
from app.schemas import classrooms as classroom_schemas
from app.schemas import pagination as pagination_schemas
from app.services import chat as chat_service_module
from app.services import classroom as classroom_service_module

router = fastapi.APIRouter()


@router.post(
    "",
    response_model=classroom_schemas.ClassroomResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_classroom(
    classroom_data: classroom_schemas.ClassroomCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    classroom_service: classroom_service_module.ClassroomService = fastapi.Depends(
        deps.get_classroom_service
    ),
):
    """
    Create new classroom (teachers only)

    - **name**: Classroom name
    - **subject**: Subject (e.g., Mathematics, Physics)
    - **grade_level**: Grade level (1-12)
    - **description**: Optional description
    """
    return await classroom_service.create_classroom(classroom_data, current_user.id)


@router.get("", response_model=pagination_schemas.Page[classroom_schemas.ClassroomResponse])
async def get_my_classrooms(
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    classroom_service: classroom_service_module.ClassroomService = fastapi.Depends(
        deps.get_classroom_service
    ),
):
    """
    Get classrooms for current user

    - Teachers: classrooms they created
    - Students: classrooms they joined
    """
    if current_user.role == "teacher":
        items = await classroom_service.get_teacher_classrooms(current_user.id, pagination.skip, pagination.limit)
        total = await classroom_service.count_teacher_classrooms(current_user.id)
    else:
        items = await classroom_service.get_student_classrooms(current_user.id, pagination.skip, pagination.limit)
        total = await classroom_service.count_student_classrooms(current_user.id)

    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/{classroom_id}", response_model=classroom_schemas.ClassroomResponse)
async def get_classroom(
    classroom_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    classroom_service: classroom_service_module.ClassroomService = fastapi.Depends(
        deps.get_classroom_service
    ),
):
    """
    Get classroom details by ID
    """
    return await classroom_service.get_classroom(classroom_id)


@router.patch("/{classroom_id}", response_model=classroom_schemas.ClassroomResponse)
async def update_classroom(
    classroom_id: int,
    classroom_data: classroom_schemas.ClassroomUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    classroom_service: classroom_service_module.ClassroomService = fastapi.Depends(
        deps.get_classroom_service
    ),
):
    """
    Update classroom (teachers only, owner only)
    """
    return await classroom_service.update_classroom(classroom_id, classroom_data, current_user.id)


@router.post("/join", response_model=classroom_schemas.ClassroomResponse)
async def join_classroom(
    join_data: classroom_schemas.JoinClassroomRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_student),
    classroom_service: classroom_service_module.ClassroomService = fastapi.Depends(
        deps.get_classroom_service
    ),
):
    """
    Join classroom via invite code (students only)

    - **invite_code**: Unique invite code from teacher
    """
    return await classroom_service.join_classroom(join_data, current_user.id)


@router.get(
    "/{classroom_id}/students",
    response_model=pagination_schemas.Page[classroom_schemas.ClassroomStudentResponse],
)
async def get_classroom_students(
    classroom_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    classroom_service: classroom_service_module.ClassroomService = fastapi.Depends(
        deps.get_classroom_service
    ),
):
    """
    Get list of students in classroom (teachers only)

    Returns student information with enrollment dates
    """
    items = await classroom_service.get_classroom_students(
        classroom_id, current_user.id, pagination.skip, pagination.limit
    )
    total = await classroom_service.count_classroom_students(classroom_id, current_user.id)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get(
    "/{classroom_id}/chat/messages",
    response_model=pagination_schemas.Page[communication_schemas.MessageResponse],
)
async def list_chat_messages(
    classroom_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    before_id: int | None = fastapi.Query(default=None, gt=0),
    tail: bool = fastapi.Query(default=False),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    chat_service: chat_service_module.ChatService = fastapi.Depends(deps.get_chat_service),
):
    items = await chat_service.list_messages(
        classroom_id,
        user=current_user,
        skip=pagination.skip,
        limit=pagination.limit,
        before_id=before_id,
        tail=tail,
    )
    total = await chat_service.count_messages(classroom_id, user=current_user)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.post(
    "/{classroom_id}/chat/messages",
    response_model=communication_schemas.MessageResponse,
)
async def post_chat_message(
    classroom_id: int,
    payload: communication_schemas.MessageCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    chat_service: chat_service_module.ChatService = fastapi.Depends(deps.get_chat_service),
):
    return await chat_service.post_message(classroom_id, user=current_user, payload=payload)


@router.websocket("/{classroom_id}/chat/ws")
async def classroom_chat_ws(
    websocket: fastapi.WebSocket,
    classroom_id: int,
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
):
    """
    Realtime classroom chat via WebSocket.

    Auth: `?token=<jwt>` query param or `Authorization: Bearer <jwt>` header.
    """
    ws_request_id = uuid.uuid4().hex

    async def _send_ws_error(
        *,
        code: str,
        message: str,
        meta: dict[str, object] | None = None,
    ) -> None:
        error: dict[str, object] = {"code": code, "message": message, "meta": meta or {}}
        await websocket.send_json({"type": "error", "error": error, "request_id": ws_request_id})

    manager = getattr(websocket.app.state, "chat_connection_manager", None)
    broker = getattr(websocket.app.state, "chat_broker", None)
    redis_client = getattr(websocket.app.state, "redis", None)

    if manager is None or broker is None or redis_client is None:
        await websocket.accept()
        await _send_ws_error(code="realtime_not_configured", message="Realtime broker is not configured")
        await websocket.close(code=1011)
        return

    try:
        user = await realtime_auth.require_current_user(websocket, db)
        chat_service = chat_service_module.ChatService(db)
        await chat_service.require_access(classroom_id, user=user)
    except domain_errors.DomainError as e:
        await websocket.accept()
        await _send_ws_error(code=e.code or "unauthorized", message=e.message, meta=e.meta or None)
        await websocket.close(code=1008)
        return

    store = realtime_presence.ChatEphemeralStore(
        redis_client,
        presence_ttl_seconds=core_config.settings.CHAT_PRESENCE_TTL_SECONDS,
        typing_ttl_seconds=core_config.settings.CHAT_TYPING_TTL_SECONDS,
    )

    await websocket.accept()
    await manager.connect(classroom_id, websocket)
    await broker.ensure_subscription(classroom_id)

    await store.set_online(classroom_id, user.id)

    online_user_ids = await store.list_online(classroom_id)
    typing_user_ids = await store.list_typing(classroom_id)

    await websocket.send_json(
        {
            "type": "ready",
            "classroom_id": classroom_id,
            "presence": {"online_user_ids": online_user_ids},
            "typing": {"user_ids": typing_user_ids},
            "request_id": ws_request_id,
        }
    )

    await broker.publish(
        classroom_id,
        {"type": "presence", "payload": {"user_id": user.id, "status": "online"}},
    )

    keepalive_task: asyncio.Task[None] | None = None

    async def _keepalive() -> None:
        while True:
            await asyncio.sleep(core_config.settings.CHAT_PRESENCE_REFRESH_SECONDS)
            await store.touch_online(classroom_id, user.id)

    keepalive_task = asyncio.create_task(_keepalive())

    last_typing_sent = 0.0

    try:
        while True:
            data = await websocket.receive_json()
            if not isinstance(data, dict):
                await _send_ws_error(code="bad_request", message="Invalid payload")
                continue

            msg_type = data.get("type")
            if msg_type == "ping":
                await store.touch_online(classroom_id, user.id)
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type == "typing":
                now = time.monotonic()
                if now - last_typing_sent < 0.2:
                    continue
                last_typing_sent = now

                is_typing_raw = data.get("is_typing")
                is_typing = bool(is_typing_raw)
                await store.touch_online(classroom_id, user.id)
                if is_typing:
                    await store.start_typing(classroom_id, user.id)
                else:
                    await store.stop_typing(classroom_id, user.id)

                await broker.publish(
                    classroom_id,
                    {"type": "typing", "payload": {"user_id": user.id, "is_typing": is_typing}},
                )
                continue

            if msg_type != "message":
                await _send_ws_error(code="bad_request", message="Unknown message type")
                continue

            try:
                create_payload = communication_schemas.MessageCreate(content=str(data.get("content", "")))
            except pydantic.ValidationError as e:
                await _send_ws_error(
                    code="validation_error",
                    message="Invalid message",
                    meta={"errors": e.errors()},
                )
                continue

            await store.touch_online(classroom_id, user.id)
            await store.stop_typing(classroom_id, user.id)
            message = await chat_service.post_message(classroom_id, user=user, payload=create_payload)
            event = {"type": "message", "payload": message.model_dump(mode="json")}
            await broker.publish(classroom_id, event)
    except starlette_websockets.WebSocketDisconnect:
        pass
    finally:
        if keepalive_task is not None:
            keepalive_task.cancel()
            try:
                await keepalive_task
            except asyncio.CancelledError:
                pass

        await store.set_offline(classroom_id, user.id)
        await broker.publish(
            classroom_id,
            {"type": "presence", "payload": {"user_id": user.id, "status": "offline"}},
        )
        await broker.release_subscription(classroom_id)
        await manager.disconnect(classroom_id, websocket)
