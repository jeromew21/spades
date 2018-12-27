import sqlite3
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from jeromeai import *

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
    inner_size = 30
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
            state = start_state.children()[0]
            while state.hands_played < 13:
                state = hook(jerome_ai, state)
                #print(state.label())   
            score = state.score(0)
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

def best_hands():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    query = "SELECT hand from bids WHERE best_bid = '7'"
    c.execute(query)
    for t in c.fetchall():
        hand = [Card.from_(i) for i, k in enumerate(json.loads(t[0])) if k == 1]
        pretty_print_hand(hand)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    query = "SELECT hand, best_bid from bids"
    c.execute(query)
    fetch = c.fetchall()
    X = np.array([np.array(json.loads(t[0])) for t in fetch])
    Y = np.array([int(t[1]) for t in fetch])

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.25)

    linear = Ridge()
    linear.fit(X_train, y_train)

    y_train_pred = linear.predict(X_train)
    y_test_pred = linear.predict(X_test)

    # print accuracies
    print('train acc: ', accuracy_score(np.rint(y_train_pred), y_train))
    print('test acc: ', accuracy_score(np.rint(y_test_pred), y_test))

    print('test loss', np.mean(np.square(y_test_pred - y_test)))

    conn.commit()
    conn.close()