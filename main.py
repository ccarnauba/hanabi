from enum import Enum, auto
from collections import deque
import random

class Color(Enum):
    BLUE   = "blue"
    GREEN  = "green"
    RED    = "red"
    WHITE  = "white"
    YELLOW = "yellow"


class Number(Enum):
    ONE   = auto()
    TWO   = auto()
    THREE = auto()
    FOUR  = auto()
    FIVE  = auto()

    def frequency(self) -> int:
        match self:
            case Number.ONE:
                return 3
            case (Number.TWO | Number.THREE | Number.FOUR):
                return 2
            case Number.FIVE:
                return 1


class Card:
    def __init__(self, color : Color, number : Number):
        self.color = color
        self.number = number


class Deck:
    @staticmethod
    def __create_deck():
        deck = deque()
        for color in list(Color):
            for number in list(Number):
                for _ in range(number.frequency()):
                    card = Card(color, number)
                    deck.append(card)
        return deck

    def __init__(self):
        deck = Deck.__create_deck()
        random.shuffle(deck)
        self.deck = deck

    def draw_card(self):
        return self.deck.pop()

class Discard_pile:
    def __init__(self):
        self.pile = dict()

    def add_card(self, card: Card):


# class Board:

# class Player:
