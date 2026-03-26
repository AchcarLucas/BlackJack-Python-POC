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

        self.__players.insert(-1, HumanPlayer('HUMAN', credits=1000))

        self.__players.insert(-1, IAPlayer('I.A (1)', credits=1000))
        self.__players.insert(-1, IAPlayer('I.A (2)', credits=1000))
        self.__players.insert(-1, IAPlayer('I.A (3)', credits=1000))
        self.__players.insert(-1, IAPlayer('I.A (4)', credits=1000))

    def _set_game_state(self, state: GameState):
        self.__game_state = state

    def _get_game_state(self) -> GameState:
        return self.__game_state

    # Method for creating a new card pack when needed.
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

    # State machine to start turn, create pack e initial turn configuration
    async def start_turn(self):
        await self.new_pack()
        await self.new_turn()

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.WAITING_DEALING)

    # State machine to waiting dealing
    async def waiting_dealing(self):
        # WAITING_DEALING It can be synchronized with all players. When all players are ready, we can start dealing the cards.
        # For now, we will just wait for a short time to simulate the waiting time for players to be ready.
        for player in self.__players:
            await player.run(PlayerState.DEALING)

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.DEALING_CARDS)

    # State machine to dealing card
    async def dealing_cards(self):
        self.__dealer.receive_card(card=self.__pack.pop(), hide=True)
        self.__dealer.receive_card(card=self.__pack.pop(), hide=False)

        dealer_hand = self.__dealer.get_current_hand()

        logging.info(f" - Dealer {self.__dealer.name} with hand: {dealer_hand} - SUM: {dealer_hand.sum_cards()} (Hidden Ignored)")

        for player in self.__players:
            player_hand = player.get_current_hand()

            # Ignore player without active hand.
            if player_hand is None:
                continue

            player.receive_card(card=self.__pack.pop())
            player.receive_card(card=self.__pack.pop())

            logging.info(f"Player {player.name} hand({id(player_hand)}): {player_hand}")

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.PLAYER_TURN)

    # State machine for player moves
    async def player_turn(self):
        for player in self.__players:
            player_hand = player.get_current_hand()

            # Ignore player without active hand.
            if player_hand is None:
                continue

            # If the player is already in STAND mode, we simply pass their turn.
            if  player_hand is not None and \
                not player_hand.can_play():
                continue

            logging.info(f"Player {player.name} turn...")
            logging.info(f" - Player {player.name} with hand({id(player_hand)}): {player_hand} - SUM: {player_hand.sum_cards()}")
            action = await player.run(PlayerState.PLAYING)
            if action == PlayerAction.STAND:
                logging.info(f" - Player {player.name} STAND with hand({id(player_hand)}): {player_hand} - SUM: {player_hand.sum_cards()}")
            elif action == PlayerAction.HIT:
                # Receive a card from the pack and add it to the player's hand, then print the new hand of the player
                player.receive_card(card=self.__pack.pop(), hide=False)
                logging.info(f" - Player {player.name} HIT with hand({id(player_hand)}): {player_hand} - SUM: {player_hand.sum_cards()}")
            elif action == PlayerAction.DOUBLE:
                # Receive a card from the pack and add it to the player's hand, then print the new hand of the player
                player.receive_card(card=self.__pack.pop(), hide=False)
                logging.info(f" - Player {player.name} DOUBLE down with hand({id(player_hand)}): {player_hand} - SUM: {player_hand.sum_cards()}")
            elif action == PlayerAction.SPLIT:
                logging.info(f" - Player {player.name} SPLIT with hand({id(player_hand)}): {player_hand} - SUM: {player_hand.sum_cards()}")

        # Checks if any player can still play, if so, returns to the 'player_turn' state.
        for player in self.__players:
             player_hand = player.get_current_hand()
             if player_hand is not None and \
                player_hand.can_play():
                 self._set_game_state(GameState.PLAYER_TURN)
                 return

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.DEALER_TURN)

    # State machine to dealer turn
    async def dealer_turn(self):
        dealer_hand = self.__dealer.get_current_hand()

        # Reveal all the cards
        dealer_hand.turn_all_cards()

        logging.info(f" - Dealer {self.__dealer.name} with hand: {dealer_hand} - SUM: {dealer_hand.sum_cards()} (Open Hidden)")

        # Make the dealer's move considering your internal logic.
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

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.END_TURN)

    # State machine to End Turn
    async def end_turn(self):
         # Validates the players and all their hands according to the dealer's result.
        for player in self.__players:
            hand_result: list[HandResult] = player.play(self.__dealer.get_current_hand())
            # Earn money win and add it as credit.
            player.add_credits(player.get_gain())

            logging.info(f"{ColorText.VERDE if player.get_gain() > 0 else ColorText.VERMELHO}Player: {player.name} - Hand: {hand_result}{ColorText.RESET}")

        await asyncio.sleep(0.25)
        self._set_game_state(GameState.WAITING_PLAYERS)

    async def play(self):
        while True:
            match self._get_game_state():
                case GameState.WAITING_PLAYERS:
                    logging.info(f"{ColorText.BG_AMARELO}Waiting for players to be ready...{ColorText.RESET}")
                    await self.waiting_players()
                case GameState.START_TURN:
                    logging.info(f"{ColorText.BG_AMARELO}Starting new turn...{ColorText.RESET}")
                    await self.start_turn()
                case GameState.WAITING_DEALING:
                    logging.info(f"{ColorText.BG_AMARELO}Starting dealing...{ColorText.RESET}")
                    await self.waiting_dealing()
                case GameState.DEALING_CARDS:
                    logging.info(f"{ColorText.BG_AMARELO}Dealing cards for players and dealer...{ColorText.RESET}")
                    await self.dealing_cards()
                case GameState.PLAYER_TURN:
                    logging.info(f"{ColorText.BG_AMARELO}Starting player's turn...{ColorText.RESET}")
                    await self.player_turn()
                case GameState.DEALER_TURN:
                    logging.info(f"{ColorText.BG_AMARELO}Starting dealer's turn...{ColorText.RESET}")
                    await self.dealer_turn()
                case GameState.END_TURN:
                    logging.info(f"{ColorText.BG_AMARELO}Round ended, calculating results...{ColorText.RESET}")
                    await self.end_turn()   
        

        
