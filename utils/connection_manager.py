from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections : List[WebSocket] = []

    async def connect(self, websocket:WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket:WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_msg(self,msg:str, websocket:WebSocket):
        await websocket.send_text(msg)

    async def broadcast(self, message:str):
        for connection in self.active_connections:
            await connection.send_text(message)


# manager = ConnectionManager()
#
# @app.websocket("/ws/{client_id}")
# async def web_socket_endpoint(client_id:int,websocket: WebSocket):
#     await manager.connect(websocket)
#     try :
#         data = await websocket.receive_text()
#         await manager.send_personal_msg(f"vous:{data}", websocket)
#         await manager.broadcast(f"- {client_id} : {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"{client_id} a quitter la dicussion")
