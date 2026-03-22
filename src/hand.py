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
        Classe que representa a mão de um jogador ou do dealer, contendo os cartões na mão, o valor da aposta (deal), 
        o resultado da mão e flags para indicar se a mão está selada ou dividida.
    """
    def __init__(self):
        self.hand_cards = []
        self._deal = 0
        self._result : Optional[HandResult] = None

        # Flag que indica que a mão esta selada (já fez a jogada)
        self.__is_sealed = False

        # Flag que indica que a mão esta em estado stand
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
    
    # Método responsável por selar a mão, indicando que o jogador decidiu ficar com a mão atual e não 
    # receberá mais cartas, definindo a flag de mão selada como True
    def do_stand(self):
        self.__is_stand = True

    def do_sealed(self):
        self.__is_sealed = True

    # Método para verificar se é possível jogar com a mão
    def can_play(self) -> bool:
        # Uma mão pode jogar se ela não estiver selada e o valor total da mão for menor que 21
        return not self.is_sealed and not self.__is_stand and self.sum_cards() < 21 and self.result is None
    
    # Verifica se a mão pode ser dividida, o que é possível apenas se houver exatamente dois cartões 
    # e ambos forem do mesmo valor, e a mão ainda não tiver sido dividida ou selada
    def can_split(self) -> bool:
        if self.can_play() is False or (len(self.hand_cards) != 2) or (self.is_split):
            return False

        return self.hand_cards[0]['card'].rank == self.hand_cards[1]['card'].rank

    # Método para jogar a mão, comparando o valor da mão do jogador com o valor da mão do dealer para 
    # determinar o resultado (ganhou, perdeu, empate ou blackjack), e definindo o resultado da 
    # mão de acordo com as regras do jogo
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

    # Método para calcular o ganho da mão com base no resultado
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

    # Método para definir o valor da aposta (deal) para a mão
    def set_deal(self, deal: int):
        if self.result is not None:
            raise Exception("Cannot make a deal on a hand that already has a result.")
        if deal <= 0:
            raise ValueError("Deal must be greater than zero.")

        self._deal = deal
        return self._deal

    # Método para adicionar um valor à aposta (deal) atual
    def add_deal(self, deal: int):
        return self.set_deal(self._deal + deal)

    # Adiciona uma carta à mão, verificando se a mão não está selada para permitir a adição de cartas, e armazenando a carta junto com a informação de se ela está oculta ou não
    def add_card(self, card: Card, hide: bool = False):
        if self.can_play() is False:
            raise ValueError("Cannot add cards to a hand, you cannot play this hand.")

        self.hand_cards.append({'card': card, 'hide': hide})

    # Revela uma carta específica na mão, definindo o atributo 'hide' da carta como False, para mostrar o valor da carta oculta
    def turn_card(self, index: int):
        if index < 0 or index >= len(self.hand_cards):
            raise IndexError("Card index out of range")

        self.hand_cards[index]['hide'] = False

    # Revela todas as cartas da mão, definindo o atributo 'hide' de cada carta como False, para mostrar o valor de todas as cartas na mão
    def turn_all_cards(self):
        for hand_card in self.hand_cards:
            hand_card['hide'] = False

    # Método responsável por dividir a mão em duas mãos separadas, movendo um dos cartões para a nova mão e marcando a mão original como dividida
    def split(self) -> Hand:
        if self.can_split() is False:
            raise Exception("Can only split with exactly two cards or if the hand has already been split")
        
        self.__is_split = True

        # Remove um cartão da mão original para criar a nova mão
        hand_card = self.hand_cards.pop()

        # Cria uma mão nova para a divisão, adicionando o cartão removido da mão original para a nova mão
        new_hand = Hand()
        new_hand.add_card(hand_card.get('card'), hide=hand_card.get('hide'))

        return new_hand
    
    # Calculula o valor total da mão, não em consideração as cartas ocultas e os Aces, que podem valer 1 ou 11 pontos dependendo do total da mão
    @abstractmethod
    def sum_cards(self) -> int:
        sum : int = 0
        aces : int = 0

        for card, hide in (e.values() for e in self.hand_cards):
            # Se a carta estiver oculta, não a conte para o total da mão
            if not hide:
                sum += card.value()
                # Se a carta for um Ace, conte quantos Aces temos para ajustar o valor da mão
                if card.rank == RANK.ACE:
                    aces += 1

        # Ajusta o valor da mão para contar os Aces como 1 ponto em vez de 11 se o total ultrapassar 21
        while sum > 21 and aces > 0:
            sum -= 10  # Conta um Ace como 1 ponto em vez de 11
            aces -= 1

        return sum