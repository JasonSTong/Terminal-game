from enum import Enum

from transitions import Machine


class ClientSystemEnum(Enum):
    HALL = 'Hall'
    IN_ROOM = 'InRoom'
    PLAYING = 'Playing'
    GAME_OVER = 'GameOver'
    EXIT = 'Exit'


class ClientSystem:
    # 登录 -> 大厅 -> 房间 -> 游戏 -> 结算积分 -> 大厅
    states = [state.value for state in ClientSystemEnum]

    def __init__(self):
        self.machine = Machine(model=self, states=ClientSystem.states, initial='Hall')
        self.machine.add_transition(trigger='enter_room', source='Hall', dest='InRoom', before='on_enter_in_room')
        self.machine.add_transition(trigger='start_game', source='InRoom', dest='Playing', before='on_enter_playing')
        self.machine.add_transition(trigger='game_over', source='GameOver', dest='RoomList',
                                    before='on_enter_game_over')
        self.machine.add_transition(trigger='exit', source='*', dest='Hall', before='on_enter_exit')

        # 映射状态到触发器方法
        self.state_trigger_map = {
            ClientSystemEnum.IN_ROOM: self.enter_room,
            ClientSystemEnum.PLAYING: self.start_game,
            ClientSystemEnum.GAME_OVER: self.game_over,
            ClientSystemEnum.EXIT: self.exit
        }

    def on_enter_login(self):
        print("Entering Login states")

    def on_enter_in_room(self):
        print("Entering InRoom states")

    def on_enter_playing(self):
        print("Entering Playing states")

    def on_enter_game_over(self):
        print("Entering GameOver states")

    def on_enter_exit(self):
        print("Entering Exit")

    def change_state(self, new_state: ClientSystemEnum):
        trigger = self.state_trigger_map.get(new_state)
        if trigger:
            trigger()
        else:
            print(f"Unknown state: {new_state}")
# Class: ClientSystemEnum
# Function: ('', '__init__')
# Function: ('', 'on_enter_login')
# Function: ('', 'on_enter_in_room')
