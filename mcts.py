from spades import *

def children(player, hand, table, bids, history, spades_broken):
    #Build state from information
    #Use probability to create state
    hands = []
    probable_state = GameState.from_(
        bids,
        hands,
        table,
        player,
        history,
        spades_broken
    )

class Node:
    def __init__(self):
        pass