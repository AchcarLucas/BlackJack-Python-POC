import logging

from .player import Player, PlayerState, PlayerAction

from .color_text import ColorText

class HumanPlayer(Player):
    async def logic(self, state : PlayerState) -> PlayerAction:
        if state is PlayerState.HANDING:
            if self.can_deal():
                self.reset_hands()
                self.new_hand()
            return None
        elif state is PlayerState.WAITING:
            return None
        elif state is PlayerState.DEALING:
            if not self.can_deal():
                logging.info(f" - Player {self.name} is {ColorText.VERMELHO}broker{ColorText.RESET}")
                return PlayerAction.BROKE

            deal = int(input(f"Press Enter to make a deal <1, {self.credits}>: "))
            self.deal(deal)

            logging.info(f" - Player {self.name} dealing with {ColorText.AMARELO}{deal}{ColorText.RESET} - credits {ColorText.VERDE}{self.credits}{ColorText.RESET}")

            return PlayerAction.DEAL
        elif state is PlayerState.PLAYING:
            while True:
                if self.get_current_hand() is None:
                    return None

                action = input("Choose an action: [H]it, [S]tand, [P]Split or [D]ouble: ").upper()
                if action == "H":
                    if self.can_hit():
                        self.hit()
                    return PlayerAction.HIT
                elif action == "S":
                    self.stand()
                    return PlayerAction.STAND
                elif action == "P":
                    if self.can_split():
                        self.split()
                        return PlayerAction.SPLIT
                    else:
                        logging.info("You cannot split your hand. Please choose another action.")
                elif action == "D":
                    if self.can_double():
                        self.double()
                        logging.info(f" - Player {self.name} - credits {ColorText.VERDE}{self.credits}{ColorText.RESET}")
                        return PlayerAction.DOUBLE
                    else:
                        logging.info("You cannot double your deal. Please choose another action.")
                else:
                    logging.info("Invalid action. Please choose H, S, P, or D.")
    
    async def run(self, state : PlayerState) -> PlayerAction:
        if state is None:
            raise Exception("PlayerState cannot be None.")
         
        self._set_state(state)

        return await self.logic(state)
