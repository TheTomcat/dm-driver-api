import anyio
from fastapi import Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from starlette.templating import Jinja2Templates

from core.broadcast import broadcast, make_channel

router = APIRouter(prefix="/live")
templates = Jinja2Templates(directory="templates")

# make_channel = lambda x: "chatroom"


@router.get("/", response_class=HTMLResponse, tags=["live"])
async def index(request: Request):
    template = "chat.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


@router.websocket("/socket/{session_id}")  # /{client_id}")
async def join_ws(websocket: WebSocket, session_id: int):  # , client_id: int):
    print("Client joining room", session_id)
    await websocket.accept()

    async with anyio.create_task_group() as task_group:

        async def run_chatroom_ws_receiver(session_id) -> None:
            print(f"Something at {session_id}")
            await chatroom_ws_receiver(websocket=websocket, session_id=session_id)
            task_group.cancel_scope.cancel()

        task_group.start_soon(run_chatroom_ws_receiver, session_id)
        await chatroom_ws_sender(websocket, session_id)


async def chatroom_ws_receiver(websocket: WebSocket, session_id: int):
    async for message in websocket.iter_json():
        print("Rec: ", message, session_id)

        await broadcast.publish(channel=make_channel(session_id), message=message)


async def chatroom_ws_sender(websocket: WebSocket, session_id: int):
    async with broadcast.subscribe(channel=make_channel(session_id)) as subscriber:
        async for event in subscriber:
            print("send", event)
            # await websocket.send_json(event)
            await websocket.send_json(event.message)


# @router.websocket("/socket")  # /{client_id}")
# async def chatroom_ws(websocket: WebSocket):
#     await websocket.accept()

#     async with anyio.create_task_group() as task_group:
#         # run until first is complete
#         async def run_chatroom_ws_receiver() -> None:
#             await chatroom_ws_receiver(websocket=websocket)
#             task_group.cancel_scope.cancel()

#         task_group.start_soon(run_chatroom_ws_receiver)
#         await chatroom_ws_sender(websocket)


# async def chatroom_ws_receiver(websocket):
#     async for message in websocket.iter_text():
#         print("Rec: ", message)
#         await broadcast.publish(channel="chatroom", message=message)


# async def chatroom_ws_sender(websocket):
#     async with broadcast.subscribe(channel="chatroom") as subscriber:
#         async for event in subscriber:
#             await websocket.send_text(event.message)
