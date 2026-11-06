from main import *

def playable_cards(board: Board) -> set[Card]:
    """
    Given the board, what set of cards should be played to progress the game?
    """
    board_list  = board.peek()
    playable_cards : set[Card] = set()

    for (color, cards) in board_list.items():
        if not cards:
            playable_cards.add(Card(color, Card.Number.ONE))

        top_card = cards[-1]
        match top_card.number.next_number():
            case None:
                continue
            case number:
                playable_cards.add(Card(color, number))

    return playable_cards


def unknown_card_indicies(hand_knowledge : list[Card.Knowledge]) -> list[int]:
    """
    Given a player's knowledge about their hand, which cards are fully unknown?
    """
    return [ index for (index, knowledge)\
             in enumerate(hand_knowledge)\
             if knowledge.is_fully_unknown() ]


def playable_cards_by_player(board : Board, other_hands : list[tuple[PlayerIndex, list[tuple[Card, Card.Knowledge]]]])\
        -> list[tuple[PlayerIndex, list[tuple[HandIndex, Card]]]]:
    playable_card_set = playable_cards(board)

    return \
        [(player_index,
          [(hand_index, card) for (hand_index, (card, _))
           in enumerate(cards_and_knowledge)
           if card in playable_card_set])
         for (player_index, cards_and_knowledge) in other_hands]
