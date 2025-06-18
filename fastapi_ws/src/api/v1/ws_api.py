import json
from uuid import UUID

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.core.config import project_settings
from src.db.superuser_auth import get_superuser
from src.schemas.user_schema import SuperuserResponse
from src.services.ws_service import ChatService, get_chat_service

from fastapi import APIRouter, Depends, Form, HTTPException, Request, WebSocket, status

router = APIRouter()
templates = Jinja2Templates(directory=project_settings.templates_path)


@router.post("/admin_login")
async def admin_login(
    name: str = Form(...),
    api_key: str = Form(...),
    chat_service: ChatService = Depends(get_chat_service),
    superuser: SuperuserResponse = Depends(get_superuser),
):
    """Авторизация на страницу администратора."""
    if superuser.name != name or superuser.api_key != api_key:
        raise HTTPException(status_code=403, detail="Неверные данные администратора")
    room = await chat_service.create_room(f"Комната администратора {name}")
    redirect_url = f"/ws/v1/chat/{room.id}/{superuser.id}?username={name}&role=admin&email={superuser.email}"
    return {"success": True, "redirect_url": redirect_url, "user_id": str(superuser.id)}


@router.websocket("/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: UUID, user_id: UUID, chat_service: ChatService = Depends(get_chat_service)
):
    """ "Авторизация в комнату Вебсокет."""
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        if data.get("type") != "auth":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        email = data.get("email")
        username = data.get("username", email.split("@")[0] if email else "user")
        role = data.get("role", "user")
        await chat_service.handle_websocket_connection(
            websocket, room_id, user_id, username=username, email=email, role=role
        )
    except json.JSONDecodeError:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Главная страница чата."""
    return templates.TemplateResponse("home.html", {"request": request})


@router.post("/join_chat")
async def join_chat(email: str = Form(...), chat_service: ChatService = Depends(get_chat_service)):
    """Авторизация пользователя по почте."""
    try:
        room = await chat_service.get_or_create_personal_room(email)
        user = await chat_service.get_user_by_email(email)

        if not user:
            return {"success": False, "error": "Пользователь не найден"}

        redirect_url = f"/ws/v1/chat/{room.id}/{user.id}?username={user.name}&email={email}&role=user"
        return {"success": True, "redirect_url": redirect_url, "user_id": str(user.id)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/create_room")
async def create_room(
    name: str = Form(...),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Создание комнаты администратором."""
    return await chat_service.create_room(name)


@router.get("/rooms")
async def get_rooms(chat_service: ChatService = Depends(get_chat_service)):
    """Получение всех комнат."""
    return await chat_service.get_all_rooms()


@router.get("/{room_id}/{user_id}", response_class=HTMLResponse)
async def get_chat_page(request: Request, room_id: UUID, user_id: UUID, username: str, email: str, role: str = "user"):
    """Страница комнаты."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room_id": room_id,
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "room_name": f"Комната пользователя {username}",
        },
    )


@router.post("/switch_room")
async def switch_room(
    user_id: UUID = Form(...),
    new_room_id: UUID = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form("user"),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Переключение между комнат администратором."""
    return await chat_service.switch_room(user_id, new_room_id, username, email, role)


@router.get("/user_rooms")
async def get_user_rooms(user_id: UUID, chat_service: ChatService = Depends(get_chat_service)):
    """Получение всех комнаты пользователя."""
    return await chat_service.get_user_rooms(user_id)


@router.post("/add_user_to_room")
async def add_user_to_room(
    room_id: UUID = Form(...),
    email: str = Form(...),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Добавления пользователя в комнату администратором."""
    return await chat_service.add_user_to_room(room_id, email)


@router.post("/remove_user_from_room")
async def remove_user_from_room(
    room_id: UUID = Form(...),
    email: str = Form(...),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Удаление пользователя в комнату администратором."""
    return await chat_service.remove_user_from_room(room_id, email)


@router.post("/delete_room")
async def delete_room(
    room_id: UUID = Form(...),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Удаление комнаты администратором."""
    return await chat_service.delete_room(room_id)


@router.get("/users")
async def get_all_users(chat_service: ChatService = Depends(get_chat_service)):
    """Получение всех пользователей."""
    return await chat_service.get_all_users()
