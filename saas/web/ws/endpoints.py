import asyncio

from fastapi import APIRouter, WebSocket
from websockets.exceptions import ConnectionClosedError

websocket_router = APIRouter()


@websocket_router.websocket('/timer')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    timer = 0
    try:
        while timer := timer + 1:
            await asyncio.sleep(1)
            await websocket.send_text(str(timer))
    except ConnectionClosedError:
        await websocket.close()
