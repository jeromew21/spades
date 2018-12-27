from spades import *

def rate_card(card):
    score = 0
    if not is_no_card and is_trump(card):
        score += 14
    score += card[4]
    return score

def jerome_ai(player, hand, table, bids, history, spades_broken):
    #Assume is player's turn to play
    #Return a card object to be played
    table_count = sum(1 if is_no_card(card) else 0 for card in table)
    opener_index = 0
    has_suit = False
    has_non_spade = False
    active_suit = None
    if table_count < 4:
        while not is_no_card(table[opener_index]):
            opener_index = loop_add_one(opener_index)
        while is_no_card(table[opener_index]):
            opener_index = loop_add_one(opener_index)
        active_suit = card_suit(table[opener_index])
        for card in hand:
            if not is_no_card(card) and card_suit(card) == card_suit(table[opener_index]):
                has_suit = True
            if not is_no_card(card) and not is_trump(card):
                has_non_spade = True
    else: #Four nulls mean we always have the suit
        has_suit = True
        for card in hand:
            if not is_no_card(card) and not is_trump(card):
                has_non_spade = True
    
    card_scores = ((i, rate_card(card), card) for i, card in enumerate(hand))
    card_scores = [
        (i, score, card) for i, score, card in card_scores if
        #Play a card of suit
        not is_no_card(card) and (
            (card_suit(card) == active_suit and has_suit) or \
            #Counter with a card of different suit
            (table_count < 4 and not has_suit) or \
            #Start with a spade
            (table_count == 4 and (is_trump(card) and (not has_non_spade or spades_broken))) or \
            (table_count == 4 and not is_trump(card))
        )
    ]
    table_scores = (
        (i, rate_card(card), card) for i, card in enumerate(table)
    )
    best_on_table = max(table_scores, key=lambda x: x[1])
    strongest_play = max(card_scores, key=lambda x: x[1])
    weakest_play = min(card_scores, key=lambda x: x[1])

    if best_on_table[1] >= strongest_play[1]:
        return weakest_play[2]
    
    trick_winners = tuple(vec_to_player(winner) for cards, winner, _ in history)
    tricks_won = len([k for k in trick_winners if k in (player, PARTNERS[player])])
    total_bid = bids[player] + bids[PARTNERS[player]]
    if tricks_won >= total_bid: #We have gone over
        return weakest_play[2]
    #Take best play better than strongest play
    return strongest_play[2]

def test_ai():
    start_state = GameState.from_([3, 3, 3, 3], Deck().deal_array(), [None, None, None, None], 0)
    state = start_state.children()[0]
    print(state.label())
    while state.hands_played < 13:
        state = hook(jerome_ai, state)
        print(state.label())
        