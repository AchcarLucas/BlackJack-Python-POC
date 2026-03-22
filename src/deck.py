import random

from .card import SUIT, RANK, Card

class Deck:
    """
        A class representing a standard deck of 52 playing cards. 
        It can be shuffled and allows drawing cards from the top.
    """
    def __init__(self, shuffle: bool = True):
        self.__cards : list[Card] = [Card(suit, rank) for suit in SUIT for rank in RANK]

        if shuffle:
            self.shuffle()

    # Shuffle the cards in the deck
    def shuffle(self):
        random.shuffle(self.__cards)

    # Return the number of cards remaining in the deck
    def __len__(self) -> int:
        return len(self.__cards)

    # Remove and return the top card of the deck
    def pop(self) -> Card:
        if not self.__cards:
            raise IndexError("No more cards in the deck")

        return self.__cards.pop()