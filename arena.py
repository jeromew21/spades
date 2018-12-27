from spades import *
from jeromeai import jerome_ai
from jacob_ai import play_turn

#from jacob_ai import jacob_ai

NAMES = ("Jerome", "Jacob")

def fight(a1, a2, names=NAMES):
    coin = random.choice((0, 1))
    if coin:
        turns = (a1, a2, a1, a2)
        p_names = (names[0] + "1", names[1] + "2", names[0] + "1", names[1] + "2")
    else:
        turns = (a2, a1, a2, a1)
        p_names = (names[1] + "1", names[0] + "2", names[1] + "1", names[0] + "2")
    start_state = GameState.from_([random.randint(1, 3) for _ in range(4)], Deck().deal_array(), [None, None, None, None], 0, player_names=p_names)
    state = start_state.children()[0]
    print(state.label())
    while state.hands_played < 13:
        ai_func = turns[state.active_player]
        state = hook(ai_func, state)
        print(state.label())
    if state.score(0) > state.score(1):
        return turns[0]
    elif state.score(0) < state.score(1):
        return turns[1]
    else:
        return None

def match():
    record = [0, 0]
    errors = 0
    for i in range(100):
        try:
            winner = fight(jerome_ai, play_turn)
        except:
            winner = None
            errors += 1
        if winner == jerome_ai:
            record[0] += 1
        elif winner == play_turn:
            record[1] += 1
    print("Jerome wins", record[0])
    print("Jacob wins", record[1])
    print("Jacob errors", errors)