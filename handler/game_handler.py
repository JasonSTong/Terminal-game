from base import cm
from manager.game_manager import GameManager


class PokerGameHandler:
    def __init__(self, room_manager, client_manager, game_manager:GameManager):
        self.room_manager = room_manager
        self.client_manager = client_manager
        self.game_manager = game_manager

    def handle_action(self, action, client, msg):
        self.game_manager.check_client_permission()
        if action == 'bet':
            self.handle_bet(client, msg)
        elif action == 'fold':
            self.handle_fold(player)
        elif action == 'check':
            self.handle_check(player)
        # Add more actions as needed
        elif action == 'raise':
            pass
        elif action == '':
            pass

    def convert_amount(self, client, amount):
        all = client.score
        if amount == 'all_in' or amount == 'all' or amount == 'allin' or amount == 'all-in':
            return 0, all
        elif amount == 'half' or amount == 'half_pot' or amount == 'half-pot' or amount == 'half pot' or amount == 'halfpot':
            return 0, all // 2
        else:
            try:
                spend = int(amount)
                if spend > all:
                    return -1, "error: 金额超过剩余筹码, 请重新下注"
                return 0, spend
            except ValueError:
                return -1, "error: 请输入有效的下注金额"

    def handle_bet(self, client, msg):
        err, err_msg = self.game_manager.get_game_uuid_by_client_id(client.client_id)
        if err != 0:
            await self.client_manager.send_message(client.client_id, err_msg)
        game_uuid = err_msg
        err, err_msg = self.convert_amount(client, msg)

        # TODO 只做了扣减用户分数的操作，缺失游戏对局积分增加
        if err == 0:
            amount = err_msg
            client.spend_score(amount)


    def handle_fold(self, player):
        # Handle player folding
        pass

    def handle_check(self, player):
        # Handle player checking
        pass
