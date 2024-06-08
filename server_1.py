import asyncio
import json
from urllib.parse import parse_qs, urlparse

import websockets

from base import cm, rm
from domain.server_client import Client
from handler.client_handler import ClientHandler
from handler.room_handler import RoomHandler
from states.client_state import ClientSystem
from states.room_state import RoomSystem


class WebSocketServer:
    def __init__(self):
        self.room_system_list: dict[str, RoomSystem] = {}
        self.room_handler = RoomHandler(self.room_system_list, rm, cm)
        self.client_system_list: dict[str, ClientSystem] = {}
        self.client_handler = ClientHandler(self.client_system_list, rm, cm)

    async def handle_message(self, websocket, path):
        uri = websocket.path
        parsed_uri = urlparse(uri)
        params_dict = parse_qs(parsed_uri.query)
        account = params_dict.get('account')[0]
        password = params_dict.get('password')[0]
        client_id = account

        if client_id in cm.clients:
            await cm.get_client(client_id).other_login(websocket)
        else:
            client = Client(client_id, websocket, account, None, password)
            cm.add_client(client)

        print(f"Client connected: {client_id}, username: {cm.get_client(client_id).get_username()}")
        await websocket.send(json.dumps({'action': 'connected', 'client_id': client_id}))

        async for message in websocket:
            await self.dispatch_message(websocket, message, client_id)

    async def dispatch_message(self, websocket, message, client_id):
        message = json.loads(message)
        await self.room_handler.handle(message, client_id)
        await self.client_handler.handle(message, client_id)
        # state_handlers = {
        #     'Login': login,
        #     'RoomList': room_list,
        #     'InRoom': in_room,
        #     'Playing': playing,
        #     'GameOver': game_over
        # }
        # current_state = self.game_system.state
        # handler = state_handlers.get(current_state)
        # if handler:
        #     await handler.handle(self.game_system, websocket, message)
        # else:
        #     await websocket.send("Unknown states.")


async def main():
    server = WebSocketServer()
    async with websockets.serve(server.handle_message, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())