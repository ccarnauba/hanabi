from collections import deque, defaultdict
from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import TypeAlias, assert_never

import abc
import random
import sys

STARTING_HINT_COUNT      = 8
STARTING_ERROR_ALLOWANCE = 4

PlayerIndex: TypeAlias = int
HandIndex  : TypeAlias = int

@dataclass
class Card:
    class Color(Enum):
        BLUE   = "blue"
        GREEN  = "green"
        RED    = "red"
        WHITE  = "white"
        YELLOW = "yellow"

    class Number(IntEnum):
        ONE   = 1
        TWO   = 2
        THREE = 3
        FOUR  = 4
        FIVE  = 5

        def frequency(self) -> int:
            match self:
                case Card.Number.ONE:
                    return 3
                case (Card.Number.TWO | Card.Number.THREE | Card.Number.FOUR):
                    return 2
                case Card.Number.FIVE:
                    return 1

    @dataclass
    class Knowledge:
        known_color  : Card.Color  | None = None
        known_number : Card.Number | None = None

    color  : Card.Color
    number : Card.Number

@dataclass
class ColorHint:
    color: Card.Color

@dataclass
class NumberHint:
    number: Card.Number

@dataclass
class DiscardAction:
    index: HandIndex

@dataclass
class PlayAction:
    index: HandIndex

type HintType =  ColorHint | NumberHint

@dataclass
class HintAction:
    hint_to_player:PlayerIndex
    hint_type : HintType

type PlayerAction =  DiscardAction | PlayAction | HintAction

class Deck:
    @staticmethod
    def __create_deck():
        deck = deque()
        for color in list(Card.Color):
            for number in list(Card.Number):
                for _ in range(number.frequency()):
                    card = Card(color, number)
                    deck.append(card)
        return deck

    def __init__(self):
        deck = Deck.__create_deck()
        random.shuffle(deck)
        self.deck = deck

    def __draw_card(self):
        return self.deck.pop()


class Discard_pile:
    def __init__(self):
        pile : defaultdict[Card.Color, deque[Card]] = defaultdict()

        for color in list(Card.Color):
            pile.setdefault(color, deque())

        self.pile = pile

    def __add_card(self, card: Card) -> None:
        self.pile[card.color].append(card)

    def peek(self) -> defaultdict[Card.Color, deque[Card]]:
        return self.pile

class Board:
    def __init__(self) -> None:
        board : defaultdict[Card.Color, deque[Card]] = defaultdict()
        self.board = board

    def __is_won(self) -> bool:
        for cards in self.board.values():
            if len(cards) != 5:
                return False

        return True

    def __score(self) -> int:
        count = 0

        for cards in self.board.values():
            count += len(cards)

        return count


    def __play_card(self, card : Card) -> bool:
        """Returns false if card was not played due to breaking the rules of
        the game
        """
        if (not self.board[card.color]) and card.number != Card.Number.ONE:
            return False

        if self.board[card.color][-1].Number != (card.number - 1):
            return False

        self.board[card.color].append(card)
        return True

    def peek(self) -> defaultdict[Card.Color, deque[Card]]:
        return self.board

class Player:
    def __init__(self):
        self.__hand: list[tuple[Card, Card.Knowledge]] = list()

    def __draw_card(self, deck):
        new_card = deck.__draw_card()
        self.__hand.append((new_card, Card.Knowledge()))

    def __pop_card(self, index : HandIndex):
        (card, _) = self.__hand.pop(index)
        return card

    # Static method to avoid leaking player hand to policy.
    @staticmethod
    @abc.abstractmethod
    def round_policy_exn(hints_remaining : int,\
                         errors_remaining : int,\
                         other_hands : list[tuple[PlayerIndex, list[tuple[Card, Card.Knowledge]]]],\
                         discard_pile: Discard_pile,\
                         board : Board,\
                         hand_knowledge: list[Card.Knowledge]) -> PlayerAction:
        """- hints_remaining: How many hints do the players have collectively?
        - errors_remaining: How many errors are remaining?
        - other_hands: a list of player hands and what they know about their
          hands, indexed by player. Note that one index will be missing since a
          player can't see their own hand :p.
        - discard_pile: Can be used to peek at what cards have been discarded
        - board: Can be used to peek at what cards have been played
        - hand_knowledge: An encoding of what this player


        What does this player do per round?
        Note that if the player decides to break the rules of the game, the
        game crashes. That's not a fun way to play the game :'(.

        """

class Game:
    def __init__(self, player_list : list[Player], verbose = False, log_file = None):
        match log_file:
            case None:
                self.log_file = sys.stdout
            case log_file:
                self.log_file = open(log_file, 'w')

        # WLOG start at player zero
        self.player_index              = 0
        self.player_list               = player_list
        self.hints_remaining           = STARTING_HINT_COUNT
        self.error_allowance_remaining = STARTING_ERROR_ALLOWANCE
        self.discard_pile              = Discard_pile()
        self.board                     = Board()
        self.deck                      = Deck()
        self.verbose                   = verbose

    def __describe_round(self, player_action : PlayerAction) -> None:
        log_line = None
        match player_action:
            case DiscardAction(i):
                log_line = f"Player {self.player_index} discarded card {i}"
            case PlayAction(i):
                log_line = f"Player {self.player_index} discarded card {i}"
            case HintAction(i, hint):

                match hint:
                    case ColorHint(color):
                        log_line = f"Player {self.player_index} hinted player {i} about the color {color}"
                    case NumberHint(num):
                        log_line = f"Player {self.player_index} hinted player {i} about the number {num}"

        self.log_file.write(log_line)

    def __discard(self, discard_index):
        player = self.player_list[self.player_index]
        self.hints_remaining = max(self.hints_remaining + 1, STARTING_HINT_COUNT)
        discarded_card = player.__pop_card(discard_index)
        self.discard_pile.__add_card(discarded_card)
        player.__draw_card(self.deck)

    def __play(self, play_index):
        player = self.player_list[self.player_index]
        card_to_play = player.__pop_card(play_index)
        player.__draw_card(self.deck)

        if not self.board.__play_card(play_index):
            self.discard_pile.__add_card(card_to_play)
            self.error_allowance_remaining -= 1


    def __hint(self, player_index: int, hint_type: HintType):
        hand_to_hint = self.player_list[player_index].__hand

        match hint_type:
            case ColorHint(color):
                for (i, (card, card_info)) in enumerate(hand_to_hint):
                    if card.Color == color:
                        card_info.__setattr__("known_color", color)

            case NumberHint(num):
                for (i, (card, card_info)) in enumerate(hand_to_hint):
                    if card.Number == num:
                        card_info.__setattr__("known_number", num)

    def __handle_player_action(self, player_action : PlayerAction) -> None:
        match player_action:
            case DiscardAction(i):
                self.__discard(i)
            case PlayAction(i):
                self.__play(i)

            case HintAction(i, hint):
                self.__hint(i, hint)

            case _:
                assert_never(player_action)

    def __get_other_hands(self) ->  list[tuple[PlayerIndex, list[tuple[Card, Card.Knowledge]]]]:
        return [(index, player.__hand) for (index, player)\
                in enumerate(self.player_list)\
                if index != self.player_index]

    def __initialize_players(self):
        num_players = len(self.player_list)
        assert(num_players >= 2)
        cards_per_player = 4 if num_players > 3 else 5

        for player in self.player_list:
            for _ in range(cards_per_player):
                player.__draw_card(self.deck)

    def play(self) -> int:
        while(self.error_allowance_remaining or not self.board.__is_won()):
            curr_player    = self.player_list[self.player_index]
            other_hands    = self.__get_other_hands()

            hand_knowledge = [ knowledge for (_, knowledge) in curr_player.__hand ]

            player_action = curr_player.round_policy_exn(self.hints_remaining,\
                                                          self.error_allowance_remaining,\
                                                          other_hands,\
                                                          self.discard_pile,\
                                                          self.board,\
                                                          hand_knowledge)
            if self.verbose:
                self.__describe_round(player_action)

            self.__handle_player_action(player_action)
            self.player_index = (self.player_index + 1) % len(self.player_list)

        return self.board.__score()
