from enum import Enum

class SUIT(Enum):
    HEARTS = "HEARTS"
    DIAMONDS = "DIAMONDS"
    CLUBS = "CLUBS"
    SPADES = "SPADES"

class RANK(Enum):
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"

class Card:
    """
        A class representing a single playing card, with a suit and rank.
        The card's value is determined by its rank, following Blackjack rules.
    """
    def __init__(self, suit: SUIT, rank: RANK):
        self.__suit = suit
        self.__rank = rank

    @property
    def suit(self) -> SUIT:
        return self.__suit
    
    @property
    def rank(self) -> RANK:
        return self.__rank

    # For user-friendly display of the card, we want to show its rank and suit, along with its Blackjack value
    def __str__(self):
        return f"{self.rank.value} of {self.suit.value} {self.__value()}"
    
    # For debugging purposes, we want a more detailed representation of the card
    def __repr__(self):
        return f"Card(suit={self.__suit}, rank={self.__rank}, value={self.__value()})"
    
    # Two cards are equal if they have the same suit and rank
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False

    # Return the Blackjack value of the card
    def value(self) -> int:
        if self.rank in {RANK.JACK, RANK.QUEEN, RANK.KING}:
            return 10
        elif self.rank == RANK.ACE:
            return 11
        else:
            return int(self.rank.value)

    # Modifies the returned value for display purposes only.
    def __value(self):
        value = self.value()
        return f"({value})" if value != 11 else f"({value}, 1)"
