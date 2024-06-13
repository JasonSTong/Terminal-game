from enum import Enum
from typing import Optional

from transitions import Machine

from base import cm
from domain.server_client import Client
from domain.texas_holdem_game import TexasHoldemGame


class TexasHoldemEnum(Enum):
    WAITING = 'Waiting'
    BIG_BLIND = 'Big_Blind'
    SMALL_BLIND = 'Small_Blind'
    HOLE_CARDS = 'Hole_Cards'
    BETTING_1 = 'Betting_1'
    FLOP = 'Flop'
    BETTING_2 = 'Betting_2'
    TURN = 'Turn'
    BETTING_3 = 'Betting_3'
    RIVER = 'River'
    BETTING_4 = 'Betting_4'
    SHOWDOWN = 'Showdown'


class TexasHoldemSystem:

    def __init__(self, clients: list[Client]):
        self.clients = clients
        self.states = [state.value for state in TexasHoldemEnum]
        self.machine = self._create_state_machine()
        self.game: Optional[TexasHoldemGame] = None

    def _create_state_machine(self):
        self.machine = Machine(model=self, states=self.states, initial=TexasHoldemEnum.WAITING)
        # big_blind -> small_blind -> Hole Cards -> betting1 -> flop -> betting2 -> turn -> betting3 -> river -> betting4 -> showdown
        self.machine.add_transition(trigger='big_blind', source=TexasHoldemEnum.WAITING, dest=TexasHoldemEnum.BIG_BLIND,
                                    before='on_enter_big_blind')
        self.machine.add_transition(trigger='small_blind', source=TexasHoldemEnum.BIG_BLIND,
                                    dest=TexasHoldemEnum.SMALL_BLIND,
                                    before='on_enter_small_blind')
        self.machine.add_transition(trigger='hole_cards', source=TexasHoldemEnum.SMALL_BLIND,
                                    dest=TexasHoldemEnum.HOLE_CARDS,
                                    before='on_enter_hole_cards')

        self.machine.add_transition(trigger='betting1', source=TexasHoldemEnum.HOLE_CARDS,
                                    dest=TexasHoldemEnum.BETTING_1,
                                    before='on_enter_betting1')
        self.machine.add_transition(trigger='flop', source=TexasHoldemEnum.BETTING_1, dest=TexasHoldemEnum.FLOP,
                                    before='on_enter_flop')

        self.machine.add_transition(trigger='betting2', source=TexasHoldemEnum.FLOP, dest=TexasHoldemEnum.BETTING_2,
                                    before='on_enter_betting')
        self.machine.add_transition(trigger='turn', source=TexasHoldemEnum.BETTING_2, dest=TexasHoldemEnum.TURN,
                                    before='on_enter_turn')

        self.machine.add_transition(trigger='betting3', source=TexasHoldemEnum.TURN, dest=TexasHoldemEnum.BETTING_3,
                                    before='on_enter_betting')
        self.machine.add_transition(trigger='river', source=TexasHoldemEnum.TURN, dest=TexasHoldemEnum.RIVER,
                                    before='on_enter_river')

        self.machine.add_transition(trigger='betting4', source=TexasHoldemEnum.RIVER, dest=TexasHoldemEnum.BETTING_4,
                                    before='on_enter_betting')
        self.machine.add_transition(trigger='showdown', source=TexasHoldemEnum.RIVER, dest=TexasHoldemEnum.SHOWDOWN,
                                    before='on_enter_showdown')

        self.state_trigger_map = {
            TexasHoldemEnum.DEALING: self.dealing,
            TexasHoldemEnum.BETTING_1: self.betting1,
            TexasHoldemEnum.FLOP: self.flop,
            TexasHoldemEnum.BETTING_2: self.betting2,
            TexasHoldemEnum.TURN: self.turn,
            TexasHoldemEnum.BETTING_3: self.betting3,
            TexasHoldemEnum.RIVER: self.river,
            TexasHoldemEnum.BETTING_4: self.betting4,
            TexasHoldemEnum.SHOWDOWN: self.showdown
        }

    def on_enter_big_blind(self):
        self.game = TexasHoldemGame(self.clients)
        self.game.init_player_seats()
        big_blind_client_id = self.game.next_player()
        cm.send_message(big_blind_client_id, "info: 请下大盲注 指令: bet <amount>")

    def on_enter_small_blind(self):
        small_blind_client_id = self.game.next_player()
        cm.send_message(small_blind_client_id, "info: 请下小盲注 指令: bet <amount>")

    def on_enter_hole_cards(self):
        self.game.deal_hole_cards()

    def on_enter_betting1(self):
        cm.send_message(self.game.current_player, "info: 请下注 指令: bet <amount>")

    def on_enter_flop(self):
        self.game.deal_community_cards(3)

    def on_enter_betting2(self):
        cm.send_message(self.game.current_player, "info: 请下注 指令: bet <amount>")

    def on_enter_turn(self):
        self.game.deal_community_cards(1)

    def on_enter_betting3(self):
        cm.send_message(self.game.current_player, "info: 请下注 指令: bet <amount>")

    def on_enter_river(self):
        self.game.deal_community_cards(1)

    def on_enter_betting4(self):
        cm.send_message(self.game.current_player, "info: 请下注 指令: bet <amount>")

    def on_enter_showdown(self):
        cm.send_message(self.game.current_player, "info: 比牌")
        cm.send_message(self.game.current_player, self.game.showdown())
