from game.domain.server_client import Client
from game.states.client_state import ClientSystemEnum


class ClientManager:
    def __init__(self, ):
        self.clients: dict[str, Client] = {}
        self.client_id_increment = 0

    def incr_client_id(self):
        self.client_id_increment += 1
        return str(self.client_id_increment)

    def create_client(self, websocket, account, username, password):
        client = Client(self.incr_client_id(), websocket, account, username, password)
        self.add_client(client)
        return client

    def get_id_or_name(self, client_id):
        return self.clients[client_id].get_id_or_name()

    def add_client(self, client):
        self.clients[client.client_id] = client

    def get_client(self, client_id):
        return self.clients.get(client_id)

    def remove_client(self, client_id):
        self.clients.pop(client_id, None)

    def get_clients_info(self):
        return {client_id: self.clients[client_id].parse_json() for client_id in self.clients}

    def get_clients_score(self, client_id_list):
        return {client_id: self.clients[client_id].score for client_id in client_id_list}

    def get_max_score_by_client_ids(self, client_id_list):
        return max([self.clients[client_id].score for client_id in client_id_list])

    def set_owner(self, client_id, is_owner):
        self.clients[client_id].set_owner(is_owner)

    def set_room_id(self, client_id, room_id):
        self.clients[client_id].room_id = room_id

    def change_state(self, client_id, state: ClientSystemEnum):
        self.clients[client_id].change_state(state)

    def change_username(self, client_id, new_username):
        self.clients[client_id].change_username(new_username)
        self.send_client_info(client_id)

    async def send_message(self, client_id, info, action=None):
        client = self.get_client(client_id)
        if client:
            await client.send_message(info, action)
            return 0, f"info: 发送成功 [action:{action}, message: {info} ]"
        else:
            return -1, f"error: 客户端 {client_id} 不存在。"

    async def send_client_info(self, client_id):
        client = self.get_client(client_id)
        if client:
            await client.send_message(client.client_info(), "player_info")
            return 0, f"info: 发送成功 [action: message, message: {client.parse_json()}]"
        else:
            await self.send_message(client_id, "error: 客户端不存在。")
            return -1, f"error: 客户端 {client_id} 不存在。"

    async def logout(self, client_id):
        client = self.get_client(client_id)
        if client:
            await client.logout()
            return 0, f"info: 客户端 {client_id} 已退出。"
        else:
            return -1, f"error: 客户端 {client_id} 不存在。"# Function: ('', '__init__')
# Function: ('', 'incr_client_id')
# Function: ('', 'create_client')
# Function: ('', 'get_id_or_name')
