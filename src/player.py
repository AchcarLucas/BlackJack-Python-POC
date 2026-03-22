from abc import abstractmethod
from typing import Optional
from enum import Enum

from .card import Card
from .hand import Hand, HandResult

# Enums to represent the state of the player's
class PlayerState(Enum):
    HANDING = 'handing'
    DEALING = 'dealing'
    WAITING = 'waiting'
    PLAYING = 'playing'

class PlayerAction(Enum):
    BROKE = 'broke'
    DEAL = 'deal'
    STAND = 'stand'
    SEALED = 'sealed'
    HIT = 'hit'
    DOUBLE = 'double'
    SPLIT = 'split'

class Player:
    """
        Represents a player in the blackjack game, which can be either a regular player or the dealer.
        Each player has a unique identifier, a name, a certain amount of credits for betting,
        and a list of hands.
    """
    def __init__(self, name: str, credits: int = 1000, dealer: bool = False):
        # Unique identifier for the player instance
        self.__uuid = id(self)
        # Player's name for identification
        self.__name = name
        # Whether the player is the dealer
        self.__is_dealer = dealer
        # Créditos do usuário
        self.__credits = 0
        # O player esta quebrando, por enquanto
        self.__is_broken = True

        # adiciona crédito
        self.add_credits(credits)

        # Variables to track the current and last state and action of the player for decision-making purposes
        self.__current_state : Optional[PlayerState] = None
        self.__last_state : Optional[PlayerState] = None

        # The current action the player has decided to take based on the game state, and the last action taken
        self.__current_action : Optional[PlayerAction] = None
        self.__last_action : Optional[PlayerAction] = None

        # Each player can have multiple hands (main hand and split hand)
        self.__hand_list: list[Hand] = []

    @property
    def current_state(self) -> Optional[PlayerState]:
        return self.__current_state
    
    @property
    def last_state(self) -> Optional[PlayerState]:
        return self.__last_state
    
    @property
    def current_action(self) -> Optional[PlayerAction]:
        return self.__current_action
    
    @property
    def last_action(self) -> Optional[PlayerAction]:
        return self.__last_action

    @property
    def uuid(self) -> int:
        return self.__uuid

    @property
    def name(self) -> str:
        return self.__name

    @property    
    def credits(self) -> int:
        return self.__credits

    @property
    def is_dealer(self) -> bool:
        return self.__is_dealer
    
    @property
    def is_broken(self) -> bool:
        return self.__is_broken
    
    # Adiciona créditos ao jogador
    def add_credits(self, credits):
        self.__credits += credits

        if self.credits > 0:
            self.__is_broken = False

    def sub_credits(self, credits):
        self.__credits -= credits

        if self.__credits <= 0:
            self.__credits = 0
            self.__is_broken = True
        elif self.credits > 0:
            self.__is_broken = False
    
    # Método responsável por manter o último action e atual
    def _set_action(self, action: PlayerAction):
         self.__last_action = self.__current_action
         self.__current_action = action

    # Método responsável por manter o último state e o atual
    def _set_state(self, state: PlayerState):
        self.__last_state = self.__current_state
        self.__current_state = state

    # Método responsável por obter a primeira mão ativa da lista de mãos
    def get_current_hand(self) -> Optional[Hand]:
        for hand in self.__hand_list:
            if not hand.is_sealed:
                return hand

        return None
    
    # Método responsável por validar todas as mãos com base na mão do dealer
    def play(self, dealer_hand : Hand) -> list[HandResult]:
        hand_result: list[HandResult] = []
        dealer_hand_value = dealer_hand.sum_cards()

        for hand in self.__hand_list:
            if not hand.is_sealed:
              hand.do_sealed()
              hand.play(dealer_hand_value)
              hand_result.append({'result': hand.result, 'gain' : hand.get_gain()})

        return hand_result
    
    # Método para validar se um jogador pode fazer deal
    def can_deal(self):
        return self.credits > 0

    # Método para validar se o jogador pode retirar mais uma carta na mão ativa
    def can_hit(self):
        current_hand = self.get_current_hand()
        return current_hand is not None and current_hand.can_play()
    
    # Método para validar se o jogador pode fazer double na mão ativa
    def can_double(self):
        current_hand = self.get_current_hand()
        return current_hand is not None and current_hand.can_play() and self.credits >= current_hand.deal

    # Método para validar se o jogador pode fazer split na mão ativa
    def can_split(self):
        current_hand = self.get_current_hand()
        return current_hand is not None and current_hand.can_play() and current_hand.can_split() and self.credits >= current_hand.deal

    # Método para fazer uma aposta, garantindo que o jogador tenha créditos suficientes 
    # e que ele possa jogar (ou seja, tenha uma mão ativa que não esteja selada)
    def make_deal(self, amount):
        current_hand = self.get_current_hand()
        if current_hand is None:
            raise Exception(f"Player {self.name} cannot make a deal because they have no active hand that can play.")
        
        if self.credits < amount:
            raise Exception(f"Player {self.name} does not have enough credits to make a deal of {amount}. Current credits: {self.credits}")

        self.sub_credits(amount)
        current_hand.set_deal(amount)

    # Método para fazer uma aposta de double deak, garantindo que o jogador tenha 
    # créditos suficientes e que ele possa jogar (ou seja, tenha uma mão ativa que não esteja selada)
    def make_double_deal(self):
        current_hand = self.get_current_hand()
        if current_hand is None:
            raise Exception(f"Player {self.name} cannot make a double deal because they have no active hand that can play.")

        self.make_deal(current_hand.deal)

    # Método para resetar o estado do jogador para o início de uma nova rodada, limpando as mãos e preparando para receber novas cartas
    def reset_hands(self):
        self.__hand_list: list[Hand] = []

    # Método para criar uma nova mão, garantindo que o jogador não tenha mais de duas mãos (mão principal e mão dividida)
    def new_hand(self):
        new_hand = Hand()
        self.__hand_list.append(new_hand)

        return new_hand
    
    # Método responsável por obter o ganho de todas as mãos
    def get_gain(self) -> int:
        gain = 0
        for hand in self.__hand_list:
            gain += hand.get_gain()
        return gain

    # Method to receive a card and add it to the appropriate hand
    def receive_card(self, card : Card, hide=False):
        self.get_current_hand().add_card(card, hide=hide)

    # Método responsável por fazer o deal da carta
    def deal(self, deal: int):
        if not self.can_deal():
            raise Exception(f"Player {self.name} cannot deal your hand")
         
        self.make_deal(deal)

        self._set_action(PlayerAction.DEAL)

    # Método responsável por dar STAND na mão ativa atual
    def stand(self) -> bool:
        self.get_current_hand().do_stand()

        self._set_action(PlayerAction.STAND)

    # Método responsável por dar SELATED na mão ativa atual
    def sealed(self) -> bool:
        self.get_current_hand().do_sealed()

        self._set_action(PlayerAction.SEALED)

    # Método responsável por dar HIT na mão ativa atual
    def hit(self):        
        if not self.can_hit():
            raise Exception(f"Player {self.name} cannot hit your hand")

        self._set_action(PlayerAction.HIT)

    # Método responsável por dar DOUBLE na mão ativa atual
    def double(self):
        if not self.can_double():
            raise Exception(f"Player {self.name} cannot double your hand")
        
        self.make_double_deal()

        self._set_action(PlayerAction.DOUBLE)

    # Método responsável por fazer o SPLIT da mão ativa atual
    def split(self) -> bool:
        if not self.can_split():
            raise Exception(f"Player {self.name} cannot split your hand")
        
        current_hand = self.get_current_hand()
        self.sub_credits(current_hand.deal)

        new_hand = current_hand.split()
        new_hand.set_deal(current_hand.deal)

        self.__hand_list.append(new_hand)

        self._set_action(PlayerAction.SPLIT)
        
    @abstractmethod
    async def run(self, state : PlayerState) -> PlayerAction:
        """ 
            Method to get the player's action based on the current state of the game. 
            This method should be implemented by subclasses to define how the player decides their actions 
            (e.g., hit, stand, split, double down) based on the game state and their hand. 
        """
        pass
        