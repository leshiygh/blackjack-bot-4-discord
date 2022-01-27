"""Файл колоды для игры"""

from itertools import product
from random import shuffle

from black_jack_core.config import RANKS, SUITS, PRINTED


class Card:
    """Класс карты"""
    def __init__(self, suit, rank, picture, points):
        self.suit = suit
        self.rank = rank
        self.picture = picture
        self.points = points


class Deck:
    """Класс колоды"""
    def __init__(self):
        self.cards = self.generate_deck()
        shuffle(self.cards)

    @staticmethod
    def generate_deck():
        """
        Генератор колоды
        :return: cards -- колода
        """
        cards = []
        for suit, rank in product(SUITS, RANKS):
            if rank == 'ace':
                points = 11
            elif rank.isdigit():
                points = int(rank)
            else:
                points = 10

            picture = PRINTED.get(f'{rank}_{suit}')
            card = Card(suit=suit, rank=rank, points=points, picture=picture)
            cards.append(card)

        return cards

    def get_card(self):
        """
        Выдача карты из колоды
        :return: card -- карта из колоды
        """
        return self.cards.pop()

    def __len__(self):
        """
        Длина колоды
        :return: len(self.cards)
        """
        return len(self.cards)
