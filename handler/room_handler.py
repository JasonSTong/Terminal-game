from game.states.room_state import RoomSystem


class RoomHandler:
    def __init__(self, room_system_list: dict[str, RoomSystem], room_manager, client_manager):
        self.room_system_list = room_system_list
        self.room_manager = room_manager
        self.client_manager = client_manager

    async def initialize(self):
        print("Initializing Room state")

    async def enter(self):
        print("Entering Room state")

    async def exit(self):
        print("Exiting Room state")

    async def handle(self, message, client_id):
        action = message.get("action","")
        if action == "create_room":
            await self.room_manager.create_room(client_id, message.get("room_name"), message.get("max_players"))

        elif action == "join_room":
            await self.room_manager.join_room(message.get("room_id"), client_id)

        elif action == "leave_room":
            await self.room_manager.leave_room(client_id)

        elif action == "list_rooms":
            await self.room_manager.list_rooms(client_id)

        elif action == "room_info":
            room_id = message.get('room_id')
            if room_id is None:
                await self.client_manager.send_message(client_id, "错误: 当前不在房间内。")
            else:
                await self.room_manager.notify_room_status(room_id, client_id)
        elif action == "chat_message":
            await self.room_manager.chat_message(client_id, message.get("message"))
# Function: ('', '__init__')
