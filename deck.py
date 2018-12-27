import random
import numpy as np
from colorama import Fore, Back, Style

class Card:
    suits = ("hearts", "spades", "diamonds", "clubs")
    values = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
    suit_displays = ['🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂽🂾🂱', '🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂭🂮🂡', '🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃍🃎🃁', '🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃝🃞🃑']
    
    @staticmethod
    def from_(vec):
        if isinstance(vec, int):
            return Card(Card.suits(vec//13), Card.values(vec%13))
        if all(vec == np.array(Card.null_card())):
            return None
        return Card(Card.suits[np.where(vec==1)[0][0]], vec[4]) 
    
    def encode(self):
        return self.suit_index * 13 + self.value_index

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.suit_index = Card.suits.index(suit)
        self.value_index = self.value - 2
        self.display = Card.suit_displays[self.suit_index][Card.values.index(value)]
    
    def vectorize(self):
        arr = [0, 0, 0, 0, self.value]
        arr[self.suit_index] = 1
        return arr
        
    @staticmethod
    def null_card():
        return [0, 0, 0, 0, 0]
    
    def prettify(self):
        if self.suit in ("hearts", "diamonds"):
            return Fore.RED + Back.WHITE + self.display + ' ' + Style.RESET_ALL
        return Fore.BLACK + Back.WHITE + self.display + ' ' + Style.RESET_ALL
    
    def __str__(self):
        return self.display

    def __repr__(self):
        return "<" + self.display + " >"

class Deck:
    def __init__(self):
        self.cards = []
        for suit in Card.suits:
            for val in Card.values:
                self.cards.append(Card(suit, val))
        assert len(self.cards) == 52
        random.shuffle(self.cards)
    
    def pop(self):
        return self.cards.pop()
    
    def deal_array(self):
        result = ([], [], [], [])
        while self.cards:
            for i in result:
                i.append(self.cards.pop())
        return result

    def deal(self, players):
        while self.cards:
            for p in players:
                p.give_card(self.cards.pop())

class Player:
    def __init__(self, name, partner=None, verbose=True):
        self.hand = []
        self.partner = partner
        self._name = name
        self.verbose = verbose
        self.hand_capacity = len(self.hand)
        self.bid = None
        self.team_bid = 0
        self.score = 0
        self.next_player = None
        self.tricks_won = 0
    
    @property
    def name(self):
        pad_len = 10
        return self._name + (" " * (pad_len - len(self._name)))

    def log(self, text):
        if self.verbose:
            print(text)
    
    def win_trick(self):
        self.log("{0} won the trick.".format(self.name))
        self.tricks_won += 1
        self.partner.tricks_won += 1

    def make_bid(self, bids):
        assert self.hand_size == self.hand_capacity
        bid = 3
        self.log("{0} bids {1}".format(self.name, bid))
        self.bid = bid
        if self.partner.bid is not None:
            self.team_bid = self.bid + self.partner.bid
            self.partner.team_bid = self.team_bid
    
    def throw_card(self, past_tricks, current_play, spades_broken, opener=False):
        card = self.hand.pop()
        self.log("{0} plays {1}".format(self.name, card))
        return card

    def give_card(self, card):
        self.hand.append(card)
        self.hand_capacity = len(self.hand)        
    
    @property
    def hand_size(self):
        return len(self.hand)
    
    def __repr__(self):
        return self.name

def pretty_print_hand(hand):
    print(' '.join(c.prettify() for c in hand))

def sort_hand(hand):
    suits = [
        [], [], [], []
    ]
    for card in hand:
        suits[Card.suits.index(card.suit)].append(card)
    suits.insert(1, suits.pop(3))
    suits.append(suits.pop(2))
    result = []
    for group in suits:
        result.extend(sorted(group, key=lambda card: card.value))
    return result