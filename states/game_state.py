from enum import Enum

from transitions import Machine

class TexasHoldemEnum(Enum):
    WAITING = 'Waiting'
    DEALING = 'Dealing'
    BETTING = 'Betting'
    FLOP = 'Flop'
    TURN = 'Turn'
    RIVER = 'River'
    SHOWDOWN = 'Showdown'


class TexasHoldem:
    states = [state.value for state in TexasHoldemEnum]

    def __init__(self):
        self.machine = Machine(model=self, states=TexasHoldem.states, initial=TexasHoldemEnum.WAITING)
        self.machine.add_transition(trigger='dealing', source=TexasHoldemEnum.WAITING, dest=TexasHoldemEnum.DEALING,
                                    before='on_enter_dealing')
        self.machine.add_transition(trigger='betting', source=TexasHoldemEnum.DEALING, dest=TexasHoldemEnum.BETTING,
                                    before='on_enter_betting')
        self.machine.add_transition(trigger='flop', source=TexasHoldemEnum.BETTING, dest=TexasHoldemEnum.FLOP,
                                    before='on_enter_flop')
        self.machine.add_transition(trigger='turn', source=TexasHoldemEnum.FLOP, dest=TexasHoldemEnum.TURN,
                                    before='on_enter_turn')
        self.machine.add_transition(trigger='river', source=TexasHoldemEnum.TURN, dest=TexasHoldemEnum.RIVER,
                                    before='on_enter_river')
        self.machine.add_transition(trigger='showdown', source=TexasHoldemEnum.RIVER, dest=TexasHoldemEnum.SHOWDOWN,
                                    before='on_enter_showdown')

        self.state_trigger_map = {
            TexasHoldemEnum.DEALING: self.dealing,
            TexasHoldemEnum.BETTING: self.betting,
            TexasHoldemEnum.FLOP: self.flop,
            TexasHoldemEnum.TURN: self.turn,
            TexasHoldemEnum.RIVER: self.river,
            TexasHoldemEnum.SHOWDOWN: self.showdown
        }


    def on_enter_login(self):
        print("Entering Login states")

    def on_enter_room_list(self):
        print("Entering RoomList states")

    def on_enter_in_room(self):
        print("Entering InRoom states")

    def on_enter_playing(self):
        print("Entering Playing states")

    def on_enter_game_over(self):
        print("Entering GameOver states")
