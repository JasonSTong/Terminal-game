from typing import Optional

from base import cm
from domain.server_client import Client
from domain.texas_holdem_game import TexasHoldemGame
from states.room_state import RoomSystem, RoomSystemEnum


class Room:
    def __init__(self, id, name, max_players, clients: list[Client], owner):
        self.id = id
        self.name = name
        self.max_players = max_players
        self.clients = clients
        self.owner = owner
        self.room_state = RoomSystem()
        self.game_info: Optional[TexasHoldemGame] = None

    def remove_client(self, client_id):
        self.clients.remove(client_id)
        if self.clients:
            if client_id == self.owner:
                new_client_id = cm.get_max_score_by_client_ids(self.clients)
                self.owner = new_client_id
                return 0, new_client_id
            else:
                return 0, ""
        else:
            self.destroy()
            return -1, f"房间 {self.name} 已解散。"

    async def add_client(self, client_id):
        client = cm.get_client(client_id)
        if len(self.clients) < self.max_players:
            self.clients.append(client_id)
            return 0, f"信息: {client.get_id_or_name()} 加入房间。"
        elif len(self.clients) >= self.max_players:
            return -1, f"错误: 房间 {self.name} 已满员。"

    def is_owner(self, client_id):
        if self.owner == client_id:
            return 0, ""
        else:
            return -1, f"当前用户:{cm.get_client(client_id).get_id_or_name()} 非房主"

    def get_info(self):
        return {
            'id': self.id,
            'name': self.name,
            'max_players': self.max_players,
            'clients': len(self.clients),
            'owner': self.owner
        }

    def get_room_clients_info(self):
        return cm.get_clients_info()

    def destroy(self):
        self.room_state.change_state(RoomSystemEnum.DESTROY_ROOM)
        return f"房间 {self.name} 已解散。"

    async def notify_room_status(self):
        status = self.room_status()
        for client_id in self.clients:
            await cm.get_client(client_id).send_message(status, "room_status")

    def get_clients(self):
        return self.clients

    def room_status(self):
        players = []
        for client in self.clients:
            players.append(
                {'id': client.get_id_or_name(),
                 'score': client.score,
                 'is_owner': client.is_owner,
                 'game_status': client.game_state
                 }
            )
        return {
            'room_id': self.id,
            'players': players
        }

    def start_game(self, game_info: Optional[TexasHoldemGame]):
        self.game_info = game_info
        self.room_state.change_state(RoomSystemEnum.PLAYING)
        return f"游戏开始"