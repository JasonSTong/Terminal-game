from enum import Enum

from transitions import Machine


class RoomSystemEnum(Enum):
    WAITING = 'Waiting'
    PLAYING = 'Playing'
    GAME_OVER = 'GameOver'
    DESTROY_ROOM = 'DestroyRoom'


class RoomSystem:
    # 等待 -> 游戏中 -> 结算 -> 销毁房间
    states = [state.value for state in RoomSystemEnum]

    def __init__(self):
        self.machine = Machine(model=self, states=RoomSystem.states, initial='Waiting')

        self.machine.add_transition(trigger='playing', source='Waiting', dest='Playing', before='on_enter_playing')
        self.machine.add_transition(trigger='game_over', source='Playing', dest='Waiting', before='on_enter_game_over')
        self.machine.add_transition(trigger='destroy', source='*', dest='DestroyRoom',
                                    before='on_enter_destroy_room')
        self.state_trigger_map = {
            RoomSystemEnum.PLAYING: self.playing,
            RoomSystemEnum.GAME_OVER: self.game_over,
            RoomSystemEnum.DESTROY_ROOM: self.destroy
        }

    def on_playing(self):
        print("Entering Login states")

    def on_enter_game_over(self):
        print("Entering RoomList states")

    def on_enter_destroy_room(self):
        print("Entering InRoom states")

    def change_state(self, new_state: RoomSystemEnum):
        trigger = self.state_trigger_map.get(new_state)
        if trigger:
            trigger()
        else:
            print(f"Unknown state: {new_state}")