import asyncio
import logging

from enum import Enum

from .hand import HandResult
from .player import Player, PlayerState, PlayerAction

from .ia_player import IAPlayer
from .human_player import HumanPlayer
from .dealer_player import DealerPlayer

from .pack import Pack

from .color_text import ColorText

class GameState(Enum):
    WAITING_PLAYERS = 0
    START_TURN = 1
    WAITING_DEALING = 2
    DEALING_CARDS = 3
    PLAYER_TURN = 4
    DEALER_TURN = 5
    END_TURN = 6

class BlackJack():
    def __init__(self, num_decks=3, num_players=2):
        self.__num_decks = num_decks
        self.__num_players = num_players
        self.__pack : Pack = None
        self.__game_state: GameState = GameState.WAITING_PLAYERS
        
        self.__players : list[Player] = []

        self.__dealer = DealerPlayer('dealer', credits=0, dealer=True)
        self.__players.insert(-1, HumanPlayer('HUMAN', credits=100))
        self.__players.insert(-1, IAPlayer('I.A', credits=1000))

    def _set_game_state(self, state: GameState):
        self.__game_state = state

    def _get_game_state(self) -> GameState:
        return self.__game_state

    # Método para criar um novo pacote de cargas quando necessário
    async def new_pack(self):
        # se existir menos que um pacote de cartas, criamos um novo pacote
        if self.__pack is None or len(self.__pack) < 52:
            logging.info(f" - New {self.__num_decks} card's pack with created")
            self.__pack = Pack(self.__num_decks)

    # Method to start a new turn, it will reset the state of the dealer and players to NEW_TURN
    async def new_turn(self):
        await self.__dealer.run(PlayerState.HANDING)

        for player in self.__players:
            await player.run(PlayerState.HANDING)

    # Method to set the state of the dealer and players to WAITING, it will be called after the new turn is started and before the dealing of cards
    async def waiting_players(self):
        await self.__dealer.run(PlayerState.WAITING)

        for player in self.__players:
            await player.run(PlayerState.WAITING)

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.START_TURN)

    async def start_turn(self):
        await self.new_pack()
        await self.new_turn()

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.WAITING_DEALING)

    async def waiting_dealing(self):
        # WAITING_DEALING It can be synchronized with all players. When all players are ready, we can start dealing the cards.
        # For now, we will just wait for a short time to simulate the waiting time for players to be ready.
        for player in self.__players:
            await player.run(PlayerState.DEALING)

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.DEALING_CARDS)

    async def dealing_cards(self):
        self.__dealer.receive_card(card=self.__pack.pop(), hide=True)
        self.__dealer.receive_card(card=self.__pack.pop(), hide=False)

        dealer_hand = self.__dealer.get_current_hand()

        logging.info(f" - Dealer {self.__dealer.name} with hand: {dealer_hand} - SUM: {dealer_hand.sum_cards()} (Hidden Ignored)")

        for player in self.__players:
            player_hand = player.get_current_hand()

            # Ignora jogador sem mão ativa
            if player_hand is None:
                continue

            player.receive_card(card=self.__pack.pop())
            player.receive_card(card=self.__pack.pop())

            logging.info(f"Player {player.name} hand: {player.get_current_hand()}")

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.PLAYER_TURN)

    async def player_turn(self):
        for player in self.__players:
            player_hand = player.get_current_hand()

            # Ignora jogador sem mão ativa
            if player_hand is None:
                continue

            # Se o player já tiver em STAND, apenas passamos a vez dele
            if  player_hand is not None and \
                not player_hand.can_play():
                continue

            logging.info(f"Player {player.name} turn...")
            logging.info(f" - Player {player.name} with hand: {player_hand} - SUM: {player_hand.sum_cards()}")
            action = await player.run(PlayerState.PLAYING)
            if action == PlayerAction.STAND:
                logging.info(f" - Player {player.name} STAND with hand: {player_hand} - SUM: {player_hand.sum_cards()}")
            elif action == PlayerAction.HIT:
                # Receive a card from the pack and add it to the player's hand, then print the new hand of the player
                player.receive_card(card=self.__pack.pop(), hide=False)
                logging.info(f" - Player {player.name} HIT with hand: {player_hand} - SUM: {player_hand.sum_cards()}")
            elif action == PlayerAction.DOUBLE:
                player.receive_card(card=self.__pack.pop(), hide=False)
                logging.info(f" - Player {player.name} DOUBLE down with hand: {player_hand} - SUM: {player_hand.sum_cards()}")
            elif action == PlayerAction.SPLIT:
                logging.info(f" - Player {player.name} SPLIT with hand: {player_hand} - SUM: {player_hand.sum_cards()}")

        # Verifica se algum jogador ainda pode jogar, se sim, volta para o estado de 'player_turn'
        for player in self.__players:
             player_hand = player.get_current_hand()
             if player_hand is not None and \
                player_hand.can_play():
                 self._set_game_state(GameState.PLAYER_TURN)
                 return

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.DEALER_TURN)

    async def dealer_turn(self):
        dealer_hand = self.__dealer.get_current_hand()

        # Revela todas as cartas
        dealer_hand.turn_all_cards()

        logging.info(f" - Dealer {self.__dealer.name} with hand: {dealer_hand} - SUM: {dealer_hand.sum_cards()} (Open Hidden)")

        # Faz a jogada do dealer considerando sua lógica interna
        while True:
            result = await self.__dealer.run(PlayerState.PLAYING)
            if result is PlayerAction.STAND:
                logging.info(f" - Dealer {self.__dealer.name} STAND with hand: {dealer_hand} - SUM: {dealer_hand.sum_cards()}")
                logging.info("Dealer STAND")
                break
            elif result is PlayerAction.HIT:
                self.__dealer.receive_card(card=self.__pack.pop(), hide=False)
                logging.info(f" - Dealer {self.__dealer.name} HIT with hand: {dealer_hand} - SUM: {dealer_hand.sum_cards()}")
                logging.info("Dealer HIT")
                continue

        # Valida os players e todas as suas mãos conforme o resultado do dealer
        for player in self.__players:
            hand_result: list[HandResult] = player.play(self.__dealer.get_current_hand())
            # obter ganho e adicionar como crédito
            player.add_credits(player.get_gain())
            logging.info(f"{ColorText.AMARELO}Player: {player.name} - Hand: {hand_result}{ColorText.RESET}")
        
        await asyncio.sleep(0.25)
        self._set_game_state(GameState.END_TURN)

    async def end_turn(self):
        await asyncio.sleep(0.25)
        self._set_game_state(GameState.WAITING_PLAYERS)

    async def play(self):
        while True:
            match self._get_game_state():
                case GameState.WAITING_PLAYERS:
                    logging.info("Waiting for players to be ready...")
                    await self.waiting_players()
                case GameState.START_TURN:
                    logging.info("Starting new turn...")
                    await self.start_turn()
                case GameState.WAITING_DEALING:
                    logging.info("Starting dealing...")
                    await self.waiting_dealing()
                case GameState.DEALING_CARDS:
                    logging.info("Dealing cards for players and dealer...")
                    await self.dealing_cards()
                case GameState.PLAYER_TURN:
                    logging.info("Starting player's turn...")
                    await self.player_turn()
                case GameState.DEALER_TURN:
                    logging.info("Starting dealer's turn...")
                    await self.dealer_turn()
                case GameState.END_TURN:
                    logging.info("Round ended, calculating results...")
                    await self.end_turn()   
        

        
