from base import cm
from game.domain.room import Room
from game.states.client_state import ClientSystemEnum


class RoomManager:
    """
        所有方法都应该有返回值, 以便于日后扩展/抽取。
    """

    def __init__(self):
        self.rooms: dict[str, Room] = {}
        self.room_id_increment = 0

    def incr_room_id(self):
        self.room_id_increment += 1
        return str(self.room_id_increment)

    async def create_room(self, client_id, room_name, max_players):
        client = cm.get_client(client_id)
        if client.room_id:
            await cm.send_message(client_id, "错误: 请先离开当前房间。")
            return f"错误: 玩家 {cm.get_id_or_name(client_id)} 已在房间内。"
        room_id = self.incr_room_id()
        room = Room(room_id, room_name, max_players, [client_id], client_id)
        self.rooms[room_id] = room
        client.room_id = room_id
        cm.set_owner(client_id, True)
        await cm.send_message(client_id,
                              f"信息: 玩家: {cm.get_id_or_name(client_id)} 加入房间。")
        await self.notify_room_status(room_id, client_id)
        cm.change_state(client_id, ClientSystemEnum.IN_ROOM)
        return room

    def get_room(self, room_id):
        return self.rooms.get(room_id)

    async def delete_room(self, room_id, client_id):
        """
        删除房间
        :param room_id:
        :param client_id:
        :return:
        """
        room = self.rooms.get(room_id)
        if room:
            err, res = room.is_owner(client_id)
            if err == 0:
                self.rooms.pop(room_id, None)
                res = room.destroy()
                for client_id in room.clients:
                    await cm.get_client(client_id).send_message(res)
            else:
                await cm.get_client(client_id).send_message(res)
        else:
            res = "错误: 房间不存在。"
            await cm.get_client(client_id).send_message(res)
        return res

    async def list_rooms(self, client_id):
        """
        获取所有房间信息
        :return:
        """
        # {'rooms':[]}
        list_info = {
            'rooms': [room.get_info() for room in self.rooms.values()]
        }
        await cm.send_message(client_id, list_info, "room_list")
        return list_info

    async def notify_room_status(self, room_id, client_id):
        """
        通知玩家房间状态
        :param room_id:
        :param client_id:
        :return:
        """
        room = self.get_room(room_id)
        status = room.room_status()
        await cm.send_message(client_id, status, "room_status")

    async def broadcast_to_room(self, room_id, message, action="message"):
        room = self.get_room(room_id)
        if room:
            for client_id in room.get_clients():
                await cm.send_message(client_id, message, action)

    async def notify_all_client_room_status(self, room_id):
        """
        通知房间内所有玩家房间状态
        :param room_id:
        :return:
        """
        room = self.get_room(room_id)
        if room:
            status = room.room_status()
            await self.broadcast_to_room(room_id, status, "room_status")

    async def join_room(self, room_id, client_id):
        """
        加入房间
        :param room_id:
        :param client_id:
        :return:
        """
        room = self.get_room(room_id)
        if room:
            err, res = await room.add_client(client_id)
            if err == 0:
                cm.set_room_id(client_id, room_id)
                # status = room.room_status()
                # await cm.send_message(client_id, status, "room_status")
                await self.notify_all_client_room_status(room_id)
                cm.change_state(client_id, ClientSystemEnum.IN_ROOM)
            return res
        else:
            return f"错误: 房间不存在。"

    async def leave_room(self, client_id):
        """
        离开房间
        :param room_id:
        :param client_id:
        :return:
        """
        client = cm.get_client(client_id)
        room = self.get_room(client.room_id)
        if room:
            err, res = room.remove_client(client_id)
            cm.set_room_id(client_id, None)
            if err == 0:
                if res.len() == 0:
                    await self.broadcast_to_room(room.id, f"{cm.get_id_or_name(client_id)} 离开房间。")
                else:
                    cm.set_owner(res, True)
                    await cm.send_message(res,
                                          f"房主: {cm.get_id_or_name(client_id)} 离开房间。 {cm.get_id_or_name(res)} 已成为新房主。")
            cm.change_state(client_id, ClientSystemEnum.EXIT)
            await cm.send_message(client_id, f"成功离开房间: {room.name}")
            return 0, ""
        else:
            return -1, f"错误: 房间不存在。"

    async def chat_message(self, sender_id, message):
        room_id = cm.get_client(sender_id).room_id
        sender_name = cm.get_id_or_name(sender_id)
        if room_id:
            room = self.get_room(room_id)
            for receiver_id in room.get_clients():
                receiver = cm.get_client(receiver_id)
                await receiver.send_message({'action': 'message', 'message': f"{sender_name}: {message}"})
# Function: ('', '__init__')
# Function: ('', 'incr_room_id')
# Function: ('async ', 'create_room')
# Function: ('', 'get_room')
# Function: ('async ', 'delete_room')
# Function: ('async ', 'list_rooms')
