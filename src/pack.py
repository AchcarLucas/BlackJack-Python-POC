
from .card import Card
from .deck import Deck

class Pack:
    """
        A class representing a pack of multiple decks of cards. 
        It allows drawing cards from the top of the first non-empty deck.
    """
    def __init__(self, num_decks: int = 8, shuffle: bool = True):
        self.__decks = [Deck(shuffle=shuffle) for _ in range(num_decks)]

    # Remove and return the top card from the first non-empty deck
    def pop(self) -> Card:
        for deck in self.__decks:
            if len(deck) > 0:
                return deck.pop()

        raise IndexError("No more cards in the pack")
    
    def __len__(self) -> int:
        return sum(len(deck) for deck in self.__decks)