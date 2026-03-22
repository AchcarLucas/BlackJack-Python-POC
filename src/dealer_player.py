from .player import Player, PlayerState, PlayerAction

class DealerPlayer(Player):
    async def logic(self, state : PlayerState) -> PlayerAction:
        self._set_state(state)

        if state is PlayerState.WAITING:
            return None
        elif state is PlayerState.HANDING:
            self.reset_hands()
            self.new_hand()
            return None
        elif state is PlayerState.DEALING:
            return PlayerAction.DEAL
        elif state is PlayerState.PLAYING:
            # Regra do dealer
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
