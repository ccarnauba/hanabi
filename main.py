import abc
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum, IntEnum
import random
import sys
from typing import TypeAlias, assert_never

STARTING_HINT_COUNT      = 8
STARTING_ERROR_ALLOWANCE = 3

PlayerIndex: TypeAlias = int
HandIndex  : TypeAlias = int

@dataclass(eq=True, frozen=True)
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

        def next_number(self) -> Card.Number | None:
            match self:
                case Card.Number.ONE:
                    return Card.Number.TWO

                case Card.Number.TWO:
                    return Card.Number.THREE

                case Card.Number.THREE:
                    return Card.Number.FOUR

                case Card.Number.FOUR:
                    return Card.Number.FIVE

                case Card.Number.FIVE:
                    return None


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

        def is_fully_unknown(self) -> bool:
            return not self.known_color and not self.known_number

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

type other_hands = list[tuple[PlayerIndex, list[tuple[Card, Card.Knowledge]]]]

class Deck:
    @staticmethod
    def _create_deck() -> deque[Card]:
        deck : deque[Card] = deque()
        for color in list(Card.Color):
            for number in list(Card.Number):
                for _ in range(number.frequency()):
                    card = Card(color, number)
                    deck.append(card)
        return deck

    def __init__(self):
        deck = Deck._create_deck()
        random.shuffle(deck)
        self.deck : deque[Card] = deck

    def draw_card(self) -> None | Card:
        if not self.deck:
            return None

        return self.deck.pop()


class Discard_pile:
    def __init__(self):
        pile : defaultdict[Card.Color, deque[Card]] = defaultdict()

        for color in list(Card.Color):
            pile.setdefault(color, deque())

        self.pile = pile

    def add_card(self, card: Card) -> None:
        self.pile[card.color].append(card)

    def peek(self) -> defaultdict[Card.Color, deque[Card]]:
        return self.pile

class Board:
    def __init__(self) -> None:
        board : dict[Card.Color, list[Card]] = {c: [] for c in Card.Color}
        self.board :dict[Card.Color, list[Card]] = board

    def is_won(self) -> bool:
        for cards in self.board.values():
            if len(cards) != 5:
                return False

        return True

    def score(self) -> int:
        count = 0

        for cards in self.board.values():
            count += len(cards)

        return count


    def play_card(self, card : Card) -> bool:
        """Returns false if card was not played due to breaking the rules of
        the game
        """
        if (not self.board[card.color]):
            if(card.number == Card.Number.ONE):
                self.board[card.color].append(card)
                return True
            else:
                return False
        else:
            if self.board[card.color][-1].number != (card.number - 1):
                return False
            else:
                self.board[card.color].append(card)
                return True


    def peek(self) -> dict[Card.Color, list[Card]]:
        return self.board

class Player(abc.ABC):
    def __init__(self):
        self.hand: list[tuple[Card, Card.Knowledge]] = list()

    def add_card_to_hand(self, new_card : Card):
        self.hand.append((new_card, Card.Knowledge()))

    def pop_card(self, index : HandIndex) -> Card:
        (card, _) = self.hand.pop(index)
        return card

    # Static method to avoid leaking player hand to policy.
    @staticmethod
    @abc.abstractmethod
    def round_policy_exn(hints_remaining : int,\
                         errors_remaining : int,\
                         other_hands : other_hands,\
                         discard_pile: Discard_pile,\
                         board : Board,\
                         hand_knowledge: list[Card.Knowledge],\
                         cards_remaining_in_deck: int) -> PlayerAction:
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

@dataclass
class GameInfo:
    score       : int
    game_length : int

class Game:
    def __init__(self, player_list : list[Player], verbose : bool = False, log_file: str | None= None):
        match log_file:
            case None:
                self.log_file = sys.stdout
            case log_file:
                self.log_file = open(log_file, 'w')

        # WLOG start at player zero
        self.player_index              = 0
        self.game_length               = 0
        self.player_list               = player_list
        self.hints_remaining           = STARTING_HINT_COUNT
        self.error_allowance_remaining = STARTING_ERROR_ALLOWANCE
        self.discard_pile              = Discard_pile()
        self.board                     = Board()
        self.deck                      = Deck()
        self.player_to_draw_last_card  = None
        self.verbose                   = verbose

    def _describe_round(self, player_action : PlayerAction) -> None:
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

    def _draw_card(self, player : Player) -> None:
        new_card = self.deck.draw_card()

        if not self.player_to_draw_last_card and not new_card:
            self.player_to_draw_last_card = self.player_index

        if new_card:
            player.add_card_to_hand(new_card)

    def _discard(self, discard_index : HandIndex):
        player = self.player_list[self.player_index]
        self.hints_remaining = max(self.hints_remaining + 1, STARTING_HINT_COUNT)
        discarded_card = player.pop_card(discard_index)
        self._draw_card(player)
        self.discard_pile.add_card(discarded_card)

    def _play(self, play_index : HandIndex) -> None:
        player = self.player_list[self.player_index]
        card_to_play = player.pop_card(play_index)
        self._draw_card(player)

        if not self.board.play_card(card_to_play):
            self.discard_pile.add_card(card_to_play)
            self.error_allowance_remaining -= 1
        else:
            # If play is valid and completes a set, players get another hint back!
            if card_to_play.number == Card.Number.FIVE:
                self.hints_remaining = (self.hints_remaining + 1) % STARTING_HINT_COUNT


    def _hint(self, player_index: int, hint_type: HintType):
        hand_to_hint = self.player_list[player_index].hand

        match hint_type:
            case ColorHint(color):
                for (card, card_info) in hand_to_hint:
                    if card.color == color:
                        card_info.__setattr__("known_color", color)

            case NumberHint(num):
                for (card, card_info) in hand_to_hint:
                    if card.number == num:
                        card_info.__setattr__("known_number", num)

    def _handle_player_action(self, player_action : PlayerAction) -> None:
        match player_action:
            case DiscardAction(i):
                self._discard(i)
            case PlayAction(i):
                self._play(i)
            case HintAction(i, hint):
                self._hint(i, hint)

            case _:
                assert_never(player_action)

    def _get_other_hands(self) ->  list[tuple[PlayerIndex, list[tuple[Card, Card.Knowledge]]]]:
        return [(index, player.hand ) for (index, player)\
                in enumerate(self.player_list)\
                if index != self.player_index]


    def _initialize_players(self):
        num_players = len(self.player_list)
        assert(num_players >= 2)
        cards_per_player = 4 if num_players > 3 else 5

        for player in self.player_list:
            for _ in range(cards_per_player):
                new_card = self.deck.draw_card()
                match new_card:
                    case None:
                        raise ValueError("Unexpected deck smaller than starting hand")
                    case card:
                        player.add_card_to_hand(card)

    def play(self) -> GameInfo:
        self._initialize_players()
        while(self.error_allowance_remaining > 0 and not self.board.is_won()):

            if self.player_index == self.player_to_draw_last_card:
                break

            curr_player    = self.player_list[self.player_index]
            other_hands    = self._get_other_hands()

            hand_knowledge = [ knowledge for (_, knowledge) in curr_player.hand ]

            player_action = curr_player.round_policy_exn(self.hints_remaining,\
                                                          self.error_allowance_remaining,\
                                                          other_hands,\
                                                          self.discard_pile,\
                                                          self.board,\
                                                          hand_knowledge, \
                                                          len(self.deck.deck))
            if self.verbose:
                self._describe_round(player_action)

            self._handle_player_action(player_action)

            self.player_index = (self.player_index + 1) % len(self.player_list)
            self.game_length += 1

        return GameInfo(self.board.score(), self.game_length)
