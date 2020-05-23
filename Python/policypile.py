import random
from enum import Enum
from typing import Type, List

from static_data import images


class Policy(Enum):
    Fascist = 1
    Liberal = 2

    def getImageUrl(self) -> str:
        imageUrls = {
            1: images["policy.png"]["Facist"],
            2: images["policy.png"]["Liberal"],
        }
        return imageUrls.get(self.value)


class PolicyPile:
    def __init__(self):
        # TODO: reabalance deck
        self.__drawPile = []  # 11 F, 6 L
        self.__discardPile = []
        self.__cardsInPlay = []
        self.__initDrawPile()

    def __initDrawPile(self):
        for _ in range(1, 12):
            self.__drawPile.append(Policy.Fascist)
        for _ in range(1, 7):
            self.__drawPile.append(Policy.Liberal)
        self.__shuffle()

    def __shuffle(self):
        self.__drawPile.extend(self.__discardPile)
        self.__discardPile.clear()
        random.shuffle(self.__drawPile)

    def draw(self) -> bool:
        # TODO: define Exception
        shuffled = False
        if len(self.__cardsInPlay) != 0:
            raise Exception
        if len(self.__drawPile) < 3:
            self.__shuffle()
            shuffled = True
        self.__cardsInPlay.extend(self.__drawPile[0:3])
        self.__drawPile = self.__drawPile[3:]
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

    def peekTop3(self):  # returns the top three cards on the deck
        return self.__drawPile[0:3]
