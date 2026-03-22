from __future__ import annotations

from typing import Optional
from enum import Enum
from abc import abstractmethod

from .card import RANK, Card

# Enum representa o resultado da mão do jogador no final de uma rodada
class HandResult(Enum):
    PUSH = 'push'
    WON = 'win'
    LOST = 'lost'
    BLACKJACK = 'blackjack'

class Hand:
    """
        A class representing a player's or dealer's hand, containing the cards in hand, the bet amount (deal), 
        the hand's outcome, and flags to indicate whether the hand is sealed or split.
    """
    def __init__(self):
        self.hand_cards = []
        self._deal = 0
        self._result : Optional[HandResult] = None

        # A flag indicating that the hand is sealed (the play has already been made).
        self.__is_sealed = False

        # Flag indicating that the hand is in stand mode.
        self.__is_stand = False

        # flag to indicate if the hand has been split (used for players who split their hand into two separate hands)
        self.__is_split = False

    # For user-friendly display of the hand, we want to show each card, indicating if it's hidden
    def __str__(self):
        return ", ".join(f"{card['card']} (Hidden)" if card['hide'] else str(card['card']) for card in self.hand_cards)
    
    @property
    def is_sealed(self) -> bool:
        return self.__is_sealed
    
    @property
    def is_stand(self) -> bool:
        return self.__is_stand
    
    @property
    def is_split(self) -> bool:
        return self.__is_split
    
    @property
    def deal(self) -> int:
        return self._deal
    
    @property
    def result(self) -> Optional[HandResult]:
        return self._result
    
    """
        This method seals the hand, indicating that the player has decided to keep their current hand 
        and will not receive any more cards, setting the sealed hand flag to True.
    """
    def do_stand(self):
        self.__is_stand = True

    def do_sealed(self):
        self.__is_sealed = True

    # Method to check if it's possible to play with the hand
    def can_play(self) -> bool:
        # A hand can be played if it is not sealed and the total value of the hand is less than 21.
        return  not self.is_sealed and \
                not self.is_stand and \
                self.sum_cards() < 21 and \
                self.result is None
    
    """
        Check if the hand can be split, which is only possible if there are exactly 
        two cards and both are of the same value, and the hand has not yet been split or sealed.
    """
    def can_split(self) -> bool:
        if self.can_play() is False or (len(self.hand_cards) != 2) or (self.is_split):
            return False

        return self.hand_cards[0]['card'].rank == self.hand_cards[1]['card'].rank


    """
        A method for playing a hand, comparing the value of the player's hand with the value of the 
        dealer's hand to determine the outcome (win, lose, tie, or blackjack), and defining the hand's 
        result according to the rules of the game
    """
    def play(self, dealer_hand_value : int):
        if self.is_sealed is False:
            raise Exception("Cannot play a hand that is not sealed.")
        
        if self.result is not None:
            raise Exception("Cannot play a hand that already has a result.")

        your_hand_value = self.sum_cards()

        if your_hand_value > 21:
            self._result = HandResult.LOST
        elif your_hand_value == 21 and len(self.hand_cards) == 2:
            self._result = HandResult.BLACKJACK
        elif dealer_hand_value > 21 or your_hand_value > dealer_hand_value:
            self._result = HandResult.WON
        elif your_hand_value == dealer_hand_value:
            self._result = HandResult.PUSH
        else:
            self._result = HandResult.LOST

    # Method for calculating hand winnings based on the result.
    def get_gain(self) -> int:
        if self.is_sealed is False:
            raise Exception("Cannot calculate gain for a hand that is not sealed.")
        
        if self.result is None:
            raise Exception("Cannot calculate gain for a hand that does not have a result.")

        if self.result is HandResult.BLACKJACK:
            return self.deal * 2.5
        elif self.result is HandResult.WON:
            return self.deal * 2
        elif self.result is HandResult.PUSH:
            return self.deal
        elif self.result is HandResult.LOST:
            return 0

    # Method for determining the deal value for a hand.
    def set_deal(self, deal: int):
        if self.result is not None:
            raise Exception("Cannot make a deal on a hand that already has a result.")
        if deal <= 0:
            raise ValueError("Deal must be greater than zero.")

        self._deal = deal
        return self._deal

    # Method for adding value to the current bet (deal)
    def add_deal(self, deal: int):
        return self.set_deal(self._deal + deal)

    """
        Adds a card to the hand, checking that the hand is not play to allow the addition of cards, 
        and storing the card along with information on whether it is face down or not.
    """
    def add_card(self, card: Card, hide: bool = False):
        if self.can_play() is False:
            raise ValueError("Cannot add cards to a hand, you cannot play this hand.")

        self.hand_cards.append({'card': card, 'hide': hide})

    # Reveals a specific card in hand by setting the card's 'hide' attribute to False, to show the value of the hidden card.
    def turn_card(self, index: int):
        if index < 0 or index >= len(self.hand_cards):
            raise IndexError("Card index out of range")

        self.hand_cards[index]['hide'] = False

    # Reveals all cards in hand by setting each card's 'hide' attribute to False, to show the value of all cards in hand.
    def turn_all_cards(self):
        for hand_card in self.hand_cards:
            hand_card['hide'] = False

    # This method involves splitting the hand into two separate hands, moving one of the cards to the new hand, and marking the original hand as split.
    def split(self) -> Hand:
        if self.can_split() is False:
            raise Exception("Can only split with exactly two cards or if the hand has already been split")
        
        self.__is_split = True

        # Remove a card from the original hand to create the new hand.
        hand_card = self.hand_cards.pop()

        # Creates a new hand for the split, adding the card removed from the original hand to the new hand.
        new_hand = Hand()
        new_hand.add_card(hand_card.get('card'), hide=hand_card.get('hide'))

        return new_hand
    
    """
        It calculates the total value of the hand, not taking into account hidden cards and Aces,
        which can be worth 1 or 11 points depending on the total hand value.
    """
    @abstractmethod
    def sum_cards(self) -> int:
        sum : int = 0
        aces : int = 0

        for card, hide in (e.values() for e in self.hand_cards):
            # If the card is face down, do not count it towards the hand total.
            if not hide:
                sum += card.value()
                # If the card is an Ace, count how many Aces you have to adjust the hand value.
                if card.rank == RANK.ACE:
                    aces += 1

        # Adjust the hand value to count Aces as 1 point instead of 11 if the total exceeds 21.
        while sum > 21 and aces > 0:
            sum -= 10  # Count an Ace as 1 point instead of 11.
            aces -= 1

        return sum