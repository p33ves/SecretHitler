import random
from enum import Enum
from typing import Type, List


class Policy(Enum):
    fascist = 1
    liberal = 2


class PolicyPile:
    def __init__(self):
        # TODO: reabalance deck
        self.__drawPile = []  # 11 F, 6 L
        self.__discardPile = []
        self.__cardsInPlay = []
        self.__initDrawPile()

    def __initDrawPile(self):
        for _ in range(1, 12):
            self.__drawPile.append(Policy.fascist)
        for _ in range(1, 7):
            self.__drawPile.append(Policy.liberal)
        self.__shuffle()

    def __shuffle(self):
        self.__drawPile.extend(self.__discardPile)
        self.__discardPile.clear()
        random.shuffle(self.__drawPile)

    def peekTop3(self):  # returns the top three cards on the deck
        return self.__drawPile[0:3]

    def draw(self) -> bool:
        # TODO: define Exception
        shuffled = False
        if len(self.__cardsInPlay) != 0:
            raise Exception
        if len(self.__drawPile) < 3:
            self.__shuffle()
            shuffled = True
        for i in range(0, 3):
            self.__cardsInPlay.append(self.__drawPile.pop(0))
        return shuffled

    def peekCardsInPlay(self) -> List[Policy]:
        return self.__cardsInPlay.copy()

    def discardPolicy(self, policy: Type[Policy]):
        # TODO: define exception
        if self.__cardsInPlay.count(policy) == 0 or len(self.__cardsInPlay) != 3:
            raise Exception
        self.__cardsInPlay.remove(policy)
        self.__discardPile.append(policy)

    def acceptPolicy(self, policy: Type[Policy]):
        # TODO: define exception
        if self.__cardsInPlay.count(policy) != 2 or len(self.__cardsInPlay) != 2:
            raise Exception
        self.__cardsInPlay.remove(policy)
        self.__discardPile.append(self.__cardsInPlay)
        self.__cardsInPlay.clear()
