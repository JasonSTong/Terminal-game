from game.manager.client_manager import ClientManager
from game.manager.room_manager import RoomManager
from game.states.client_state import ClientSystem


class ClientHandler:
    def __init__(self, client_handler: dict[str, ClientSystem], room_manager:RoomManager, client_manager:ClientManager):
        self.client_handler = client_handler
        self.room_manager = room_manager
        self.client_manager = client_manager

    async def initialize(self):
        print("Initializing Room state")

    async def enter(self):
        print("Entering Room state")

    async def exit(self):
        print("Exiting Room state")

    async def handle(self, message, client_id):
        action = message.get("action", "")
        if action == "player_info":
            await self.client_manager.send_client_info(client_id)
        elif action == "change_username":
            self.client_manager.get_client(client_id).change_username(message.get("username"))
            print(f"客户端 {client_id} 更改用户名为: {message.get('username')}")
        elif action == "logout":
            print(await self.client_manager.get_client(client_id).logout())
            client = self.client_manager.get_client(client_id)
            if client.room_id:
                room = self.room_manager.get_room(client.room_id)
                if room:
                    await self.room_manager.leave_room(client_id)

# Function: ('', '__init__')
# Function: ('async ', 'initialize')
