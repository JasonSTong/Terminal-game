
# 牌型权值（从低到高）
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

class Deck:
    def __init__(self):
        self.cards = [r + s for r in '23456789TJQKA' for s in 'HDCS']
        random.shuffle(self.cards)

    def deal(self, num):
        return [self.cards.pop() for _ in range(num)]


class PokerHand:
    def __init__(self, cards):
        self.cards = cards
        self.rank, self.high_card = self.evaluate_hand()

    def evaluate_hand(self):
        values = '23456789TJQKA'
        suits = 'HDCS'
        value_counts = Counter(card[0] for card in self.cards)
        suit_counts = Counter(card[1] for card in self.cards)
        is_flush = any(count == 5 for count in suit_counts.values())
        sorted_values = sorted((values.index(v), v) for v in value_counts.keys())
        is_straight = len(sorted_values) == 5 and sorted_values[-1][0] - sorted_values[0][0] == 4
        if is_straight and is_flush:
            return ('straight_flush', sorted_values[-1][1])
        if 4 in value_counts.values():
            return ('four_of_a_kind', max(value_counts, key=value_counts.get))
        if sorted(value_counts.values()) == [2, 3]:
            return ('full_house', max(value_counts, key=value_counts.get))
        if is_flush:
            return ('flush', sorted_values[-1][1])
        if is_straight:
            return ('straight', sorted_values[-1][1])
        if 3 in value_counts.values():
            return ('three_of_a_kind', max(value_counts, key=value_counts.get))
        if list(value_counts.values()).count(2) == 2:
            return ('two_pair', max(value_counts, key=value_counts.get))
        if 2 in value_counts.values():
            return ('pair', max(value_counts, key=value_counts.get))
        return ('high_card', sorted_values[-1][1])



class PokerGame:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.pot = 0
        self.community_cards = []
        self.current_bet = 0
        self.player_bets = {player: 0 for player in players}

    def deal_hole_cards(self):
        for player in self.players:
            player.hand = self.deck.deal(2)

    def deal_community_cards(self, num):
        self.community_cards.extend(self.deck.deal(num))

    async def betting_round(self):
        for player in self.players:
            await self.prompt_player_action(player)

    async def prompt_player_action(self, player):
        await player.send_message({"action": "your_turn"})
        response = await player.websocket.recv()
        action = json.loads(response)
        if action['type'] == 'bet':
            amount = action['amount']
            self.player_bets[player] += amount
            self.pot += amount
            self.current_bet = max(self.current_bet, self.player_bets[player])

    async def showdown(self):
        hands = {player: PokerHand(player.hand + self.community_cards) for player in self.players}
        best_player = max(self.players, key=lambda p: (hand_ranks[hands[p].rank], hands[p].high_card))
        return f"赢家是 {best_player.get_username()}， 他们的手牌是 {hands[best_player].cards}"


class GameState:
    WAITING_FOR_PLAYERS = 'waiting_for_players'
    PRE_FLOP = 'pre_flop'
    FLOP = 'flop'
    TURN = 'turn'
    RIVER = 'river'
    SHOWDOWN = 'showdown'
# Function: ('', '__init__')
