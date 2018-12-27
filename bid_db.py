import sqlite3
import json
from spades import *

DB = "bidding.sqlite3"

def create_table():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    query = """CREATE TABLE bids (
        id integer PRIMARY KEY,
        hand text NOT NULL,
        best_bid text NOT NULL
    )"""
    c.execute(query)
    conn.commit()
    conn.close()

def generate_row():
    deck = Deck()
    hand = sort_hand([deck.pop() for _ in range(13)])
    rest = [deck.pop() for _ in range(13*3)]
    inner_size = 50
    means = []
    for bid in range(8): #We rarely, rarely see bids over 7.
        samples = []
        for _ in range(inner_size):
            random.shuffle(rest)
            starting_hands = [
                hand,
                rest[0:13],
                rest[13:26],
                rest[26:39],
            ]
            start_state = GameState.from_([bid, 2, 2, 2], starting_hands, [None, None, None, None])
            d1 = start_state
            for _ in range(14*4):
                children = tuple(d1.children())
                if not children:
                    break
                random_child = random.choice(children)
                #print(random_child.label())
                d1 = random_child
            score = d1.score(0)
            #print("{0}/{1}".format(k, inner_size), diff)
            samples.append(score)
        mean = sum(samples) / len(samples)
        means.append((bid, mean))
    result = max(means, key=lambda x: x[1])[0]
    print("Mean for")
    pretty_print_hand(hand)
    print("is", result)
    hand_serialized = [0 for _ in range(52)]
    for card in hand:
        hand_serialized[card.encode()] = 1
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    query = "INSERT INTO bids (hand, best_bid) VALUES (?, ?)"
    c.execute(query, (json.dumps(hand_serialized), str(result)))
    conn.commit()
    conn.close()