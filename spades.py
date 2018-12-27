import numpy as np
from deck import *

TRUMP_SUIT = "spades"

class OOPGame:
    """An OOP Game"""

    def __init__(self, deck, player_names=("Aaron", "Chris", "David", "Max"), verbose=True):
        p1 = Player(player_names[0])
        p2 = Player(player_names[1])
        p3 = Player(player_names[2], p1)
        p4 = Player(player_names[3], p2)
        p2.partner = p4
        p1.partner = p3
        p1.next_player = p2
        p2.next_player = p3
        p3.next_player = p4
        p4.next_player = p1
        self.spades_broken = False
        self.players = (p1, p2, p3, p4)
        self.teams = ((p1, p3), (p2, p4))
        self.past_tricks = []
        self.verbose = verbose
        deck.deal(self.players)
    
    def log(self, text):
        if self.verbose:
            print(text)
       
    def play(self):
        if self.players[0].hand_size <= 0:
            return
        self.make_bids()
        winner = self.players[0]
        while self.players[0].hand_size > 0:
            plays, winner, self.spades_broken = self.trick(winner, self.past_tricks, self.spades_broken)
            self.past_tricks.append(plays)
            winner.win_trick()
            self.log("")

    def make_bids(self):
        self.bids = [player.bid for player in self.players]
        for player in self.players:
            player.make_bid(self.bids)
            self.bids = [player.bid for player in self.players]

    def trick(self, winner, past_tricks, spades_broken):
        plays = []
        plays.append((winner, winner.throw_card(past_tricks, plays, spades_broken, True)))
        player = winner.next_player
        while player is not winner:
            card = player.throw_card(past_tricks, plays, spades_broken)
            if card.value == TRUMP_SUIT:
                spades_broken = True
            plays.append((player, card))
            player = player.next_player
        current_suit = plays[0][1].suit
        max_play = plays[0]
        for player, card in plays:
            if card.suit in (TRUMP_SUIT, current_suit):
                if ((card.suit == max_play[1].suit != TRUMP_SUIT) and card.value > max_play[1].value) or (card.suit == TRUMP_SUIT and max_play[1].suit != TRUMP_SUIT):
                    max_play = (player, card)
        return plays, max_play[0], spades_broken

NO_CARD = np.array(Card.null_card())
PARTNERS = (2, 3, 0, 1)
TWO_CLUBS = np.array([0, 0, 0, 1, 2])

def card_value(vec):
    return Card.values[vec[4]]

def card_suit(vec):
    return np.where(vec==1)[0][0]

def show_card(vec):
    if vec is None or is_no_card(vec):
        return None
    return str(Card.from_(vec))

def is_trump(vec):
    return card_suit(vec) == 1

def is_no_card(vec):
    return all(vec == NO_CARD)

def vec_to_player(vec):
    return np.where(vec==1)[0][0]

def player_to_hot(i):
    hot = np.zeros((4,), dtype='int32')
    hot[i] = 1
    return hot

def pad_name(name):
    pad_len = 8
    return name + (" " * (pad_len - len(name)))

def loop_add_one(x):
    if x >= 3: return 0
    return x+1

def play_card(vector, offset, target):
    """Put the card starting at OFFSET into target"""
    vector[target:target+5] = vector[offset:offset+5]
    vector[offset:offset+5] = np.zeros((5,), dtype='int32')   

p1 = 8 + 5*13*4 #Hands
p2 = p1 + 5*4 #Table

class GameState:

    @staticmethod
    def from_(bids, hands, play_on_board, whose_turn, history, spades_broken=False, player_names=("Aaron", "Chris", "David", "Max")):
        arr = []
        for bid in bids:
            if bid is None:
                arr.append(-1)
            else:
                arr.append(bid)
        one_hot = [0, 0, 0, 0]
        one_hot[whose_turn] = 1
        arr.extend(one_hot)
        for hand in hands:
            for card in hand:
                arr.extend(card.vectorize())
        for card in play_on_board:
            if card is None:
                arr.extend(Card.null_card())
            else:
                arr.extend(card.vectorize())
        arr.append(1 if spades_broken else 0)
        for play, winner, last in history:
            res = []
            for card in play:
                res.extend(card.vectorize())
            one_hot = [0, 0, 0, 0]
            one_hot[winner] = 1
            res.extend(one_hot)
            one_hot = [0, 0, 0, 0]
            one_hot[last] = 1
            res.extend(one_hot)
            arr.extend(res)
        vec = np.zeros((653,), dtype='int32')
        arr = np.array(arr)
        vec[:arr.shape[0]] = arr
        return GameState(vec, len(history))

    def __init__(self, state_vector, hands_played, player_names=("Aaron", "Chris", "David", "Max")):
        self.vec = state_vector
        self.hands_played = hands_played
        self.bids = state_vector[0:4]
        self.active_player = vec_to_player(state_vector[4:8])
        self.hands = np.array([np.split(arr, 13) for arr in np.split(state_vector[8:p1], 4)])
        self.table = np.split(state_vector[p1:p2], 4)
        self.spades_broken = state_vector[p2]
        p3 = p2 + 1 + hands_played*(28)
        if hands_played > 0:
            self.history = [(np.split(arr[0:20], 4), arr[20:24], arr[24:28]) for arr in np.split(state_vector[p2+1:p3], hands_played)]
        else:
            self.history = []
        self.names = player_names

    def label(self):
        for i, bid in enumerate(self.bids):
            if bid < 0:
                if i-1 < 0:
                    return "Game has begun"
                return "{0} bids {1}".format(pad_name(self.names[i-1]), self.bids[i-1])
        if len(self.history) == 0 and all(is_no_card(card) for card in self.table):
            return "{0} bids {1}".format(pad_name(self.names[3]), self.bids[3])
        is_empty = True
        for card_vec in self.table:
            if not is_no_card(card_vec):
                is_empty = False
        empty_message = ""
        if is_empty:
            k = vec_to_player(self.history[-1][2])
            last_card = self.history[-1][0][k]
            empty_message = "\n{0} wins\n".format(self.names[vec_to_player(self.history[-1][1])])
        else:
            k = self.active_player - 1
            if k < 0:
                k = 3
            last_card = self.table[k]
        
        return "{0} plays {1}".format(pad_name(self.names[k]), Card.from_(last_card).prettify()) + empty_message
        
    def debug(self):
        print(self.vec)
        print("Shape:", self.vec.shape)
        print("Bids:", self.bids)
        print("Turn:", self.names[self.active_player])
        print("Hands:", [[show_card(card) for card in hand] for hand in self.hands])
        print("Table:", [show_card(card) for card in self.table])
        print("History:", [self.names[vec_to_player(winner)] + " won " + ' '.join([show_card(card) for card in cards]) for cards, winner, last in self.history])
        print(self.label())
    
    def score(self, player):
        pass

    def children(self):
        for i, bid in enumerate(self.bids):
            if bid < 0:
                player_with_2_clubs = 0
                for y, hand in enumerate(self.hands):
                    for card in hand:
                        if all(card == np.array([0, 0, 0, 1, 2])):
                            player_with_2_clubs = y
                            break
                self.vec[4:8] = player_to_hot(player_with_2_clubs)
                for b in range(14):
                    cpy = np.copy(self.vec)
                    cpy[i] = b
                    yield GameState(cpy, 0, self.names)
                return
        if self.hands_played == 0 and all(is_no_card(card) for card in self.table):
            #Yield state where 2clubs has been played and it is next player's turn
            cpy = np.copy(self.vec)
            offset = None
            player_with_2_clubs = 0
            for i, hand in enumerate(self.hands):
                for k, card in enumerate(hand):
                    if all(card == TWO_CLUBS):
                        offset = i*13*5 + k*5 + 8
                        player_with_2_clubs = i
                        break
                if offset is not None:
                    break
            cpy[4:8] = player_to_hot(loop_add_one(player_with_2_clubs))
            indice = p1 + 5*player_with_2_clubs
            cpy[indice:indice+5] = cpy[offset:offset+5]
            cpy[offset:offset+5] = np.zeros((5,), dtype='int32')    
            yield GameState(cpy, 0, self.names)
            return
        active_player = vec_to_player(self.vec[4:8])
        next_player = player_to_hot(loop_add_one(active_player))
        target = p1 + 5*active_player
        table_count = sum(1 if is_no_card(card) else 0 for card in self.table)
        opener_index = 0
        if table_count < 4: #ONE NULL CARD, THREE CARDS
            while not is_no_card(self.table[opener_index]):
                opener_index = loop_add_one(opener_index)
            while is_no_card(self.table[opener_index]):
                opener_index = loop_add_one(opener_index)
        for k, card in enumerate(self.hands[active_player]):
            offset = active_player*13*5 + k*5 + 8
            cpy = np.copy(self.vec)
            cpy[4:8] = next_player
            if not is_no_card(cpy[offset:offset+5]):
                #if spade, update spades_broken
                play_card(cpy, offset, target)
                #Update history if last
                history_i = self.hands_played
                if table_count == 1:
                    #insert at history_i
                    cards = np.split(cpy[p1:p2], 4)
                    winner = opener_index
                    strongest_card = cards[opener_index]
                    for i, card_vec in enumerate(cards):
                        if (card_vec[4] > strongest_card[4] \
                            and card_suit(card_vec) == card_suit(strongest_card)) \
                            or (is_trump(card_vec) and not is_trump(strongest_card)):
                            strongest_card = card_vec
                            winner = i
                    hot_winner = player_to_hot(winner)
                    arr = np.zeros((28,), dtype='int32')
                    arr[0:20] = cpy[p1:p2]
                    arr[20:24] = hot_winner #Winner
                    cpy[4:8] = hot_winner
                    arr[24:28] = player_to_hot(active_player) #Last player
                    offset = p2 + 1 + 28*history_i
                    cpy[offset:offset+28] = arr
                    cpy[p1:p2] = np.zeros((20,), dtype='int32') #Zero out table
                    history_i += 1
                t = GameState(cpy, history_i, self.names)
                yield t

    
def test():
    test_state = GameState.from_([3, 3, 3, None], Deck().deal_array(), [None, None, None, Card("spades", 4)], 0, [
        ([Card("diamonds", 3), Card("clubs", 3), Card("hearts", 3), Card("spades", 3)], 3, 3)
    ])
    start_state = GameState.from_([None, None, None, None], Deck().deal_array(), [None, None, None, None], 0, [])
    print(start_state.label())
    d1 = start_state
    for i in range(14*4):
        d1 = list(d1.children())
        random_child = random.choice(d1)
        print(random_child.label())
        d1 = random_child

test()