from main import *
import utils

sample_hand = [
    Card(Card.Color[color], Card.Number[num])
    for color, num in [("RED", "TWO"), ("BLUE", "FIVE"), ("WHITE", "ONE"), ("BLUE", "ONE")]
]

def test_play_cards():
    board = Board()
    assert(board.play_card(Card(Card.Color.RED, Card.Number.ONE)))
    assert(board.play_card(Card(Card.Color.RED, Card.Number.TWO)))
    assert(board.play_card(Card(Card.Color.RED, Card.Number.THREE)))

def test_playable_cards():
    board = Board()
    board.play_card(Card(Card.Color.RED, Card.Number.ONE))

    playable_cards =  utils.playable_cards(board)

    assert(len(playable_cards) == 5)

    board.play_card(Card(Card.Color.RED, Card.Number.TWO))
    board.play_card(Card(Card.Color.RED, Card.Number.THREE))
    board.play_card(Card(Card.Color.RED, Card.Number.FOUR))
    board.play_card(Card(Card.Color.RED, Card.Number.FIVE))

    playable_cards =  utils.playable_cards(board)
    assert(len(playable_cards) == 4)

def test_unambiguous_hints():
    other_hands : other_hands = []
    assert(utils.unambiguous_hints(other_hands) == [])

    other_hands = [(1, [(card, Card.Knowledge()) for card in sample_hand])]
    assert(utils.unambiguous_hints(other_hands).sort()\
           == [(1, [ColorHint(Card.Color.RED), NumberHint(Card.Number.TWO), NumberHint(Card.Number.FIVE), ColorHint(Card.Color.WHITE)])].sort())
