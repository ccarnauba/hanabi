from main import *
import random
import utils

class Unambiguous_Hinting_Player(Player):
    """A player that will:

    1. If they know nothing about their hand, and there are hints to give they will:

    1.1 If there is a visible card that is playable and has an unabmiguous
    hint, hint at that card

    1.2 If there aren't any visible playable cards, discard a knowledge-free card at random.

    2. If they know something, assume that card is playable.
    3. If there are no hints to give, discard at random.

    """
    @staticmethod
    def round_policy_exn(hints_remaining : int,\
                         errors_remaining : int,\
                         other_hands : other_hands,\
                         discard_pile: Discard_pile,\
                         board : Board,\
                         hand_knowledge: list[Card.Knowledge],
                         cards_remaining_in_deck: int) -> PlayerAction:

        cards_we_know_about = [ index for (index, knowledge)\
                                in enumerate(hand_knowledge) if
                                not knowledge.is_fully_unknown() ]

        playable_cards = utils.playable_cards_by_player(board, other_hands)

        playable_cards = set([card for (_, cards)\
                              in playable_cards for (_, card) in cards])

        unambiguous_hints = utils.unambiguous_hints(other_hands)
        unambiguous_hints = [(index, hint) for index, hints in unambiguous_hints for hint in hints]

        cards_touched_by_unambiguous_hints =\
            [ (player, hint,
               utils.cards_and_knowledge_touched_by_hint(utils.cards_held_by_player(other_hands, player), hint)) for
              (player, hint) in unambiguous_hints
             ]

        playable_cards_touched_by_unambiguous_hints =\
            [ (player, hint, card) for (player, hint, cards)\
              in cards_touched_by_unambiguous_hints\
              for (card, _) in cards\
              if card in playable_cards]


        match cards_we_know_about:
            # If we know nothing, then either give a hint, or discard a card.
            case []:
                match hints_remaining:
                    case 0:
                        return DiscardAction(0)
                    case _:
                        match playable_cards_touched_by_unambiguous_hints:
                            case []:
                                return DiscardAction(0)
                            case cards:
                                return HintAction(cards[0][0], cards[0][1])

            # If we know anything, then play that card.
            case cards:
                return PlayAction(cards[0])
