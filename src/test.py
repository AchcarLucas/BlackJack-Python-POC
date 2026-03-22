import logging

from .deck import Deck
from .card import SUIT, RANK, Card
from .pack import Pack
from .hand import Hand
    
TEST = False

def test_card():
    logging.info("-" * 30)
    logging.info("Testing Card class...")
    logging.info("-" * 30)
    card = Card(SUIT.HEARTS, RANK.ACE)
    logging.info(f"Created card: {card} - Blackjack value: {card.value()}")

def test_deck():
    logging.info("-" * 30)
    logging.info("Testing Deck class...")
    logging.info("-" * 30)
    deck = Deck(shuffle=True)
    logging.info(f"Total cards in the deck: {len(deck)}")
    try:
        while True:
            card : Card = deck.pop()
            logging.info(f"Drew card: {card} - Cards left in deck: {len(deck)}")
    except IndexError as e:
        logging.error(str(e))

def test_pack():
    logging.info("-" * 30)
    logging.info("Testing Pack class...")
    logging.info("-" * 30)
    pack = Pack(shuffle=True)
    logging.info(f"Total cards in the pack: {len(pack)}")
    try:
        while True:
            card : Card = pack.pop()
            logging.info(f"Drew card: {card} - Cards left in pack: {len(pack)}")
    except IndexError as e:
        logging.error(str(e))

def test_hand():
    logging.info("-" * 30)
    logging.info("Testing Hand class...")
    logging.info("-" * 30)

    logging.info("Testing hand value calculation with Aces without hidden cards...")
    try:
        hand = Hand()
        hand.add_card(Card(SUIT.HEARTS, RANK.ACE))
        hand.add_card(Card(SUIT.SPADES, RANK.KING))
        logging.info(f"Hand value with Ace and King: {hand.sum_cards()}")

        hand.add_card(Card(SUIT.DIAMONDS, RANK.FIVE))
        logging.info(f"Hand value with Ace, King, and Five: {hand.sum_cards()}")

        logging.info(f"Hand: {hand}")
    except Exception as e:
        logging.error(str(e))

    logging.info("\nTesting hand value calculation with hidden cards...")
    try:
        hand = Hand()
        hand.add_card(Card(SUIT.HEARTS, RANK.ACE))
        hand.add_card(Card(SUIT.SPADES, RANK.EIGHT), True) # Simulate hidden card
        logging.info(f"Hand value with Ace and Eight (Hidden): {hand.sum_cards()}")

        hand.add_card(Card(SUIT.DIAMONDS, RANK.FIVE))
        logging.info(f"Hand value with Ace, Eight (Hidden), and Five: {hand.sum_cards()}")

        logging.info(f"Hand: {hand}")

        logging.info("Revealing hidden card...")
        hand.turn_all_cards()
        logging.info(f"Hand value with Ace, Eight, and Five: {hand.sum_cards()}")

        logging.info(f"Hand: {hand}")
    except Exception as e:
        logging.error(str(e))

    # Test splitting a hand with two Aces (should be allowed)
    logging.info("\nTesting hand splitting with two Aces...")
    try:
        hand = Hand()
        hand.add_card(Card(SUIT.HEARTS, RANK.ACE))
        hand.add_card(Card(SUIT.SPADES, RANK.ACE))

        logging.info(f"Original hand before split: {hand}")

        split_hand = hand.split()

        logging.info(f"Original hand after split: {hand}")
        logging.info(f"New hand after split: {split_hand}")
    except Exception as e:
        logging.error(str(e))

    # Test splitting a hand with different ranks (should raise an error)
    logging.info("\nTesting hand splitting with different ranks...")
    try:
        hand = Hand()
        hand.add_card(Card(SUIT.HEARTS, RANK.ACE))
        hand.add_card(Card(SUIT.SPADES, RANK.FOUR))

        logging.info(f"Original hand before split: {hand}")

        split_hand = hand.split()
    except Exception as e:
        logging.error(str(e))

    # Test splitting a hand with more than two cards (should raise an error)
    logging.info("\nTesting hand splitting with more than two cards...")
    try:
        hand = Hand()
        hand.add_card(Card(SUIT.HEARTS, RANK.ACE))
        hand.add_card(Card(SUIT.SPADES, RANK.FOUR))
        hand.add_card(Card (SUIT.DIAMONDS, RANK.FOUR))

        logging.info(f"Original hand before split: {hand}")

        split_hand = hand.split()
    except Exception as e:
        logging.error(str(e))

def all_test():
    if not TEST:
        return

    logging.info("Iniciando testes...")

    test_card()
    test_deck()
    test_pack()
    test_hand()

    logging.info("Todos os testes foram concluídos com sucesso!")