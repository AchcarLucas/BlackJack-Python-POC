import logging
import random

from .player import Player, PlayerState, PlayerAction

from .color_text import ColorText

class IAPlayer(Player):
    async def logic(self, state : PlayerState) -> PlayerAction:
        self._set_state(state)

        if state is PlayerState.WAITING:
            return None
        elif state is PlayerState.HANDING:
            if self.can_deal():
                self.reset_hands()
                self.new_hand()
            return None
        elif state is PlayerState.DEALING:
            deal = 0

            if not self.can_deal():
                logging.info(f" - Player {self.name} is {ColorText.VERMELHO}broker{ColorText.RESET}")
                return PlayerAction.BROKE
            elif self.credits >= 500:
                deal = self.credits * random.uniform(0.25, 0.5)
            elif self.credits >= 100 and self.credits < 500:
                deal = self.credits * random.uniform(0.1, 0.25)
            else:
                deal = self.credits
            
            deal = int(deal)

            self.deal(deal)
            
            logging.info(f" - Player {self.name} dealing with {ColorText.AMARELO}{deal}{ColorText.RESET} - credits {ColorText.AZUL}{self.credits}{ColorText.RESET}")

            return PlayerAction.DEAL
        elif state is PlayerState.PLAYING:
            # Simple Strategy: if hand value is less than 17, hit; otherwise, stand.
            hand_value = self.get_current_hand().sum_cards()
            if hand_value < 17:
                self.hit()
                return PlayerAction.HIT
            else:
                self.stand()
                return PlayerAction.STAND

    async def run(self, state : PlayerState) -> PlayerAction:
        if state is None:
            raise Exception("PlayerState cannot be None.")

        self._set_state(state)

        return await self.logic(state)
