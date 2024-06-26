import uuid
from enum import Enum

from base import cm
from domain.poker_game import Deck, PokerGame
from domain.server_client import Client
from states.client_state import ClientGameBaseState

hand_ranks = {
    "high_card": 1,
    "pair": 2,
    "two_pair": 3,
    "three_of_a_kind": 4,
    "straight": 5,
    "flush": 6,
    "full_house": 7,
    "four_of_a_kind": 8,
    "straight_flush": 9,
    "royal_flush": 10,
}
# TODO game需要一个Interface, 用于定义游戏的基本操作(交由Manager控制), 游戏特有流程交由各个handler控制
# TODO Interface 1. init_game操作 2. pot增加和玩家积分扣减 3. 积分结算

class TexasHoldemGame:
    def __init__(self, clients: list[Client], game_uuid: str = str(uuid.uuid4())):
        self.game_uuid = game_uuid
        self.game_type = "Texas Hold'em"
        self.players = clients
        self.deck = Deck()
        self.pot = 0
        self.community_cards = []
        self.current_bet = 0
        self.player_seats: list[dict] = self.init_player_seats()
        self.round = 0
        self.current_player = None
        self.is_operating = False

    def init_player_seats(self):
        sits = []
        for player in self.players:
            if player.is_owner:
                player.game_base_state = ClientGameBaseState.ACTIVE
                self.current_player = player.client_id
            sits.append({"player_id": player.get_client_id(), "state": player.game_base_state})
        return sits

    def next_player(self) -> str:
        """
        Get the next player to play
        :return: player_id
        """
        for i, player_site in enumerate(self.player_seats):
            if player_site["state"].play_state == ClientGameBaseState.ACTIVE:
                player_site["state"].player_state = ClientGameBaseState.WAITING
                cm.get_client(player_site["player_id"]).game_base_state = ClientGameBaseState.WAITING
                if len(self.player_seats) > i + 1:
                    next_player = self.player_seats[i + 1]
                else:
                    next_player = self.player_seats[0]

                client_id = next_player['player_id']
                cm.get_client(client_id).game_base_state = ClientGameBaseState.ACTIVE
                self.current_player = client_id

                return client_id

    # TODO implement the game logic, 1. player bet 2. limit the bet amount 3. deal the community cards 4. showdown
    # TODO overall process of the game
    #  1. init seat (在状态机内传入 game_uuid 进行初始化, room中需要新增game_uuid, room操作创建销毁游戏)
    #  2. deal hole cards ( 初始化后调用状态机, 状态机应该操作 game_handler 控制)
    #  3. betting round
    #  4. deal community cards
    #  5. betting round
    #  6. showdown

    def deal_hole_cards(self):
        """
        Deal 2 cards to each player
        :return:
        """
        for player in self.players:
            player.hand = self.deck.deal(2)

    def deal_community_cards(self, num):
        """
        Deal community cards
        :param num: number of cards to deal
        :return:
        """
        self.community_cards.extend(self.deck.deal(num))

    async def betting_round(self, player, amount):
        """
        Player makes a bet
        :param player:
        :param amount:
        :return:
        """
        await self.process_betting_amount(player, amount)

    async def process_betting_amount(self, player, amount):
        """
        Process the amount bet by the player
        :param player:
        :param amount:
        :return:
        """
        self.player_bets[player] += amount
        self.pot += amount
        self.current_bet = max(self.current_bet, self.player_bets[player])

    async def showdown(self):
        hands = {player: PokerHand(player.hand + self.community_cards) for player in self.players}
        best_player = max(self.players, key=lambda p: (hand_ranks[hands[p].rank], hands[p].high_card))
        return f"赢家是 {best_player.get_username()}， 他们的手牌是 {hands[best_player].cards}"

    def client_permission(self, client_id):
        """
        Check if the client has permission to play the game
        :param client_id:
        :return:
        """
        if self.current_player == client_id and self.is_operating:
            return 0, "ok"
        name = cm.get_id_or_name(client_id)
        err_msg = f"error: 当前玩家为: {name} .请等待你的回合"
        return -1, err_msg
