import asyncio
import logging

# Configuração básica de logging para facilitar o debug
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

from .test import all_test

from .blackjack import BlackJack

if __name__ == "__main__":
    all_test()
    
    blackjack = BlackJack(num_decks=3, num_players=2)

    logging.info("Starting BlackJack...")
    asyncio.run(blackjack.play())
    logging.info("Game finished!")