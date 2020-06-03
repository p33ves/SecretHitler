import random
from enum import Enum
from typing import List

import discord

from role_player import Player
from static_data import images, colours


class Policy(Enum):
    Fascist = 1
    Liberal = 2

    def getImageUrl(self) -> str:
        imageUrls = {
            1: images["policy.png"]["Fascist"],
            2: images["policy.png"]["Liberal"],
        }
        return imageUrls[self.value]

    @staticmethod
    def getEnum(policy: str):
        policy = policy.lower()
        if policy == "fascist" or policy == "red" or policy == "r":
            return Policy.Fascist
        elif policy == "liberal" or policy == "blue" or policy == "b":
            return Policy.Liberal
        else:
            return None


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

    @property
    def noOfCardsInDeck(self) -> int:
        return len(self.__drawPile)

    @property
    def cardsInPlay(self) -> List[Policy]:
        return self.__cardsInPlay

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

    def discardPolicy(self, policy: Policy):
        # TODO: define exception
        if self.__cardsInPlay.count(policy) == 0 or len(self.__cardsInPlay) != 3:
            raise Exception
        self.__cardsInPlay.remove(policy)
        self.__discardPile.append(policy)

    def acceptPolicy(self, policy: Policy):
        # TODO: define exception
        if self.__cardsInPlay.count(policy) == 0 or len(self.__cardsInPlay) != 2:
            raise Exception
        self.__cardsInPlay.remove(policy)
        self.__discardPile.append(self.__cardsInPlay)
        self.__cardsInPlay.clear()

    def peekTop3(self):  # returns the top three cards on the deck
        return self.__drawPile[0:3]

    def placeTopPolicy(self) -> Policy:
        return self.__drawPile.pop(0)

    async def presidentTurn(self, channel, president: Player):
        shuffled = self.draw()
        if shuffled:
            await channel.send(
                f"The deck has been reshuffled and there are {self.noOfCardsInDeck}"
            )
        file_embed = discord.File(
            images["presidentdeck.png"][self.cardsInPlay.count(Policy.Fascist)],
            filename="policydeck.png",
        )
        cardsEmbed = discord.Embed(
            title=f"\t **Discard** one Policy",
            description="Type *sh!p <color/name>* of the card that you wish to discard from the 3 given below: ",
            colour=colours["DARK_AQUA"],
        )
        cardsEmbed.set_image(url="attachment://policydeck.png")
        await president.send(fileObj=file_embed, embedObj=cardsEmbed)

    async def chancellorTurn(self, chancellor: Player, discarded: Policy):
        self.discardPolicy(discarded)
        file_embed = discord.File(
            images["chancellordeck.png"][self.cardsInPlay.count(Policy.Fascist)],
            filename="policydeck.png",
        )
        cardsEmbed = discord.Embed(
            title=f"\t **Pick** one Policy",
            description="Type *sh!p <color/name>* of the card that you wish to enact from the 2 given below: ",
            colour=colours["GOLD"],
        )
        cardsEmbed.set_image(url="attachment://policydeck.png")
        await chancellor.send(fileObj=file_embed, embedObj=cardsEmbed)

    async def executeTop3(self, president: Player):
        top3 = self.peekTop3()
        file_embed = discord.File(
            images["presidentdeck.png"][top3.count(Policy.Fascist)],
            filename="policydeck.png",
        )
        cardsEmbed = discord.Embed(
            title="\t Next cards in the draw pile", colour=colours["DARK_AQUA"],
        )
        cardsEmbed.set_image(url="attachment://policydeck.png")
        await president.send(fileObj=file_embed, embedObj=cardsEmbed)
