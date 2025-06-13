from uuid import UUID

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.core.config import project_settings
from src.services.ws_service import ChatService, get_chat_service

from fastapi import APIRouter, Depends, Form, Request, WebSocket

router = APIRouter()
templates = Jinja2Templates(directory=project_settings.templates_path)


@router.websocket("/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: UUID, user_id: UUID, chat_service: ChatService = Depends(get_chat_service)
):
    await chat_service.handle_websocket_connection(websocket, room_id, user_id)


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.post("/join_chat_api")
async def join_chat_api(
    username: str = Form(...),
    room_id: UUID = Form(...),
    role: str = Form("user"),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.join_chat(username, room_id, role)


@router.post("/create_room_api")
async def create_room_api(
    username: str = Form(...), name: str = Form(...), chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.create_room(username, name)


@router.get("/get_rooms")
async def get_rooms(chat_service: ChatService = Depends(get_chat_service)):
    return await chat_service.get_rooms()


@router.get("/{room_id}/{user_id}", response_class=HTMLResponse)
async def get_chat_page(request: Request, room_id: UUID, user_id: UUID, username: str, role: str = "user"):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "room_id": room_id,
            "username": username,
            "user_id": user_id,
            "role": role,
            "websocket_url": f"/ws/v1/chat/{room_id}/{user_id}",
        },
    )


@router.post("/switch_room")
async def switch_room_api(
    user_id: UUID = Form(...),
    old_room_id: UUID = Form(...),
    new_room_id: UUID = Form(...),
    username: str = Form(...),
    role: str = Form("user"),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.switch_room(user_id, old_room_id, new_room_id, username, role)
