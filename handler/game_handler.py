class PokerGameHandler:
    def __init__(self, game):
        self.game = game

    def handle_action(self, player, action):
        if action == 'bet':
            self.handle_bet(player)
        elif action == 'fold':
            self.handle_fold(player)
        elif action == 'check':
            self.handle_check(player)
        # Add more actions as needed
        elif action == 'raise':
            pass
        elif action == '':
            pass

    def handle_bet(self, player):
        # Handle player betting
        pass

    def handle_fold(self, player):
        # Handle player folding
        pass

    def handle_check(self, player):
        # Handle player checking
        pass