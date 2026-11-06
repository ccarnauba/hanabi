from main import *
import random

class RandomPlayer(Player):

    @staticmethod
    def round_policy_exn(hints_remaining : int,\
                         errors_remaining : int,\
                         other_hands : list[tuple[PlayerIndex, list[tuple[Card, Card.Knowledge]]]],\
                         discard_pile: Discard_pile,\
                         board : Board,\
                         hand_knowledge: list[Card.Knowledge]) -> PlayerAction:

        num_of_cards = len(hand_knowledge)
        rand_card = random.randrange(0, num_of_cards, 1)

        return PlayAction(rand_card)


class RandomDiscarder(Player):

    @staticmethod
    def round_policy_exn(hints_remaining : int,\
                         errors_remaining : int,\
                         other_hands : list[tuple[PlayerIndex, list[tuple[Card, Card.Knowledge]]]],\
                         discard_pile: Discard_pile,\
                         board : Board,\
                         hand_knowledge: list[Card.Knowledge]) -> PlayerAction:

        num_of_cards = len(hand_knowledge)
        rand_card = random.randrange(0, num_of_cards, 1)

        return DiscardAction(rand_card)
