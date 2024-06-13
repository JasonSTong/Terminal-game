import uuid
from typing import Optional

from base import cm, rm
from domain.server_client import Client
from domain.texas_holdem_game import TexasHoldemGame


class GameManager:
    def __init__(self, ):
        self.game_process_list: dict[str, Optional[TexasHoldemGame]] = {}

    def create_game(self, clients: list[Client], game_uuid: str = str(uuid.uuid4())):
        game = TexasHoldemGame(clients)
        self.game_process_list[game_uuid] = game
        return game_uuid

    def get_game(self, game_uuid):
        return self.game_process_list.get(game_uuid)

    def remove_game(self, game_uuid):
        self.game_process_list.pop(game_uuid, None)

    def check_client_permission(self, game_uuid, client_id):
        game = self.get_game(game_uuid)
        if game:
            return game.client_permission(client_id)
        else:
            return -1, "错误: 游戏不存在。"

    def get_game_uuid_by_client_id(self, client_id):
        client = cm.get_client(client_id)
        if client:
            room = rm.get_room(client.room_id)
            if room:
                game_state = room.game_state
                if game_state:
                    return 0, game_state.game_uuid
        return -1, "错误: 未加入任何游戏"

