from main import *
from functools import cache

def playable_cards(board: Board) -> set[Card]:
    """
    Given the board, returns the set of cards which progress the game
    """
    board_list  = board.peek()
    playable_cards : set[Card] = set()

    for (color, cards) in board_list.items():
        if not cards:
            playable_cards.add(Card(color, Card.Number.ONE))
            continue

        top_card = cards[-1]
        match top_card.number.next_number():
            case None:
                continue
            case number:
                playable_cards.add(Card(color, number))

    return playable_cards

def unknown_card_indicies(hand_knowledge : list[Card.Knowledge]) -> list[int]:
    """
    Given a list of knowledge, returns a list of indices of fully unknown cards.
    """
    return [ index for (index, knowledge)\
             in enumerate(hand_knowledge)\
             if knowledge.is_fully_unknown() ]

def playable_cards_by_player(board : Board, other_hands : other_hands)\
        -> list[tuple[PlayerIndex, list[tuple[HandIndex, Card]]]]:
    playable_card_set = playable_cards(board)

    return \
        [(player_index,
          [(hand_index, card) for (hand_index, (card, _))
           in enumerate(cards_and_knowledge)
           if card in playable_card_set])
         for (player_index, cards_and_knowledge) in other_hands]


def fully_unknown_cards_by_player(other_hands : other_hands)\
        -> list[tuple[PlayerIndex, list[tuple[HandIndex, Card]]]]:

    return \
        [(player_index,
          [(hand_index, card) for (hand_index, (card, knowledge))
           in enumerate(cards_and_knowledge)
           if knowledge.is_fully_unknown()])
         for (player_index, cards_and_knowledge) in other_hands]


def cards_revealed_by_hint(cards : list[Card], hint_type : HintType) -> list[Card]:
    match hint_type:
        case ColorHint(color):
            return [card for card in cards if card.color == color]
        case NumberHint(number):
            return [card for card in cards if card.number == number]

def cards_and_knowledge_touched_by_hint(cards_and_knowledge : list[tuple[Card, Card.Knowledge]], hint_type : HintType)\
        -> list[tuple[Card, Card.Knowledge]]:
    match hint_type:
        case ColorHint(color):
            return\
                [(card, knowledge) for (card, knowledge)\
                 in cards_and_knowledge if card.color == color]
        case NumberHint(number):
            return\
                [(card, knowledge) for (card, knowledge)\
                 in cards_and_knowledge if card.number == number]

@cache
def all_hints() -> list[HintType]:
    color_hints = [ColorHint(color) for color in Card.Color]
    number_hints = [NumberHint(number) for number in Card.Number]

    return color_hints + number_hints


def unambiguous_hints(other_hands : other_hands) -> list[tuple[PlayerIndex, list[HintType]]]:

    all_possible_hints = all_hints()

    other_hands_knowlege_free = [(player_index,
                                  [card for (card, _) in cards_and_knowlege])
                                 for (player_index, cards_and_knowlege) in other_hands]
    return\
        [(player_index,
          [hint for hint
           in all_possible_hints
           if len(cards_revealed_by_hint(cards, hint)) == 1])
         for (player_index, cards) in other_hands_knowlege_free]

def cards_held_by_player(other_hands : other_hands, player : PlayerIndex)\
        -> list[tuple[Card, Card.Knowledge]]:

    for (player_index, cards_and_knowledge) in other_hands:
        if player_index == player:
            return cards_and_knowledge

    return []

def does_hint_reveal_new_info(other_hands : other_hands, player : PlayerIndex, hint : HintType) -> bool:

    cards_for_player = cards_held_by_player(other_hands, player)
    cards_touched = cards_and_knowledge_touched_by_hint(cards_for_player, hint)

    return all([(knowledge.is_fully_unknown() for (_, knowledge) in cards_touched)])
