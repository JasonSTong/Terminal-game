from enum import Enum

from transitions import Machine

class TexasHoldemEnum(Enum):
    pass

class TexasHoldem:
    states = ['Init', 'Pre-Flop', 'InRoom', 'Playing', 'GameOver']

    def __init__(self):
        self.machine = Machine(model=self, states=TexasHoldem.states, initial='Login')

        self.machine.add_transition(trigger='login', source='Login', dest='RoomList', before='on_enter_room_list')
        self.machine.add_transition(trigger='view_rooms', source='RoomList', dest='InRoom', before='on_enter_in_room')
        self.machine.add_transition(trigger='enter_room', source='InRoom', dest='Playing', before='on_enter_playing')
        self.machine.add_transition(trigger='start_game', source='Playing', dest='GameOver',
                                    before='on_enter_game_over')
        self.machine.add_transition(trigger='game_over', source='GameOver', dest='RoomList',
                                    before='on_enter_room_list')
        self.machine.add_transition(trigger='exit', source='*', dest='Login', before='on_enter_login')

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
# Class: TexasHoldemEnum
# Function: ('', '__init__')
# Function: ('', 'on_enter_login')
