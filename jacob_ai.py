import numpy as np
import time
from deck import *
from spades import *
from copy import copy

empty_card = np.array([0,0,0,0,0])

def play_turn(player, hand, table, bids, history, spades):
	#returns a card from hand
	table = np.array(table)
	my_bid = bids[player]
	our_bid = my_bid+bids[(player+2)%4]
	opp_bid = bids[(player+1)%4]+bids[(player+3)%4]

	if len(history)>0:
		winner = vec_to_player(history[-1][1])
	else:
		for i,row in enumerate(table):
			if row[4]==2 and row[3]==1:
				winner = i
	trick_winners = tuple(vec_to_player(winner) for cards, winner, _ in history)
	tricks_won = len([k for k in trick_winners if k in (player,(player+2)%4)])
	tricks_won_opp = len([k for k in trick_winners if not k in (player,(player+2)%4)])

	table_high = max(table[:,4])
	table_high_player = np.argmax(table[:,4])
	if winner != player:
		suit = min(np.where(table[winner]==1)[0])
	else:
		suit = 0
	# high_card = 

	#if it is advantageous to win the trick
	if table_high_player!=(player+2)%4:
		if tricks_won<our_bid or opp_bid<tricks_won_opp:
			hand_high = 0
			have_suit = False
			for card in hand:
				if len(np.where(card==1)[0])>0 and min(np.where(card==1)[0])==suit:
					have_suit = True
				if len(np.where(card==1)[0])>0 and min(np.where(card==1)[0])==suit and card[4]>table_high and card[4]<hand_high:
					hand_high = card[4]

			#if you can play high card in suit				
			if hand_high>0:
				card = copy(empty_card)
				card[suit] = 1
				card[4] = hand_high
				return card

			#try to play a spade instead
			if hand_high==0 and have_suit==False:
				spade_low = 100
				for card in hand:
					if len(np.where(card==1)[0])>0 and min(np.where(card==1)[0])==1 and card[4]<spade_low:
						spade_low = card[4]
				if spade_low<100:
					card = copy(empty_card)
					card[1] = 1
					card[4] = spade_low
					return card

	#otherwise play lowest card in suit
	hand_low = 100
	for card in hand:
		if len(np.where(card==1)[0])>0 and min(np.where(card==1)[0])==suit and card[4]<hand_low:
			hand_low = card[4]
	if hand_low<100:
		card = copy(empty_card)
		card[suit] = 1
		card[4] = hand_low
		return card

	#if no card in suit play lowest non-trump
	for card in hand:
		if card[1]!=1 and card[4]<hand_low and card[4]>0:
			hand_low = card[4]
			hand_low_suit = min(np.where(card==1)[0])
	if hand_low<100:
		card = copy(empty_card)
		card[hand_low_suit] = 1
		card[4] = hand_low
		return card

	#play lowest trump
	for card in hand:
		if card[4]<hand_low and card[4]>0:
			hand_low = card[4]
	card = copy(empty_card)
	card[1] = 1
	card[4] = hand_low
	return card

def test_ai():
	start_state = GameState.from_([3, 3, 3, 3], Deck().deal_array(), [None, None, None, None], 0)
	state = start_state.children()[0]
	print(state.label())
	while state.hands_played < 13:
		print(play_turn)
		state = hook(play_turn, state)
		print(state.label())

if __name__ == "__main__":
	for i in range(1):
		test_ai()