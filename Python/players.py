import random
from enum import Enum

import discord
from discord import Embed, File

from static_data import images, colours


class Role(Enum):
    Hidden = None
    Hitler = 1
    Fascist = 2
    Liberal = 3

    def getRolePic(self):
        rolePics = {
            1: images["role.png"]["Hitler"],
            2: random.choice(images["role.png"]["Fascist"]),
            3: random.choice(images["role.png"]["Liberal"]),
        }
        return rolePics[self.value]

    def getParty(self) -> tuple():
        if self == Role.Liberal:
            return (self.name, images["party.png"]["Liberal"], "DARK_BLUE")
        else:
            return (Role.Fascist.name, images["party.png"]["Fascist"], "RED")


class Player:
    def __init__(self, user):
        self.__user = user
        self.__role = Role.Hidden
        self.__isDead = False

    @property
    def id(self) -> str:
        return self.__user.id

    @property
    def name(self) -> str:
        # If same palyer names join the same game, need to change this into full_name
        return self.__user.name

    @property
    def avatar_url(self) -> str:
        return self.__user.avatar_url

    @property
    def dmChannelID(self) -> int:
        return self.__user.dm_channel.id

    @property
    def isDead(self):
        return self.__isDead

    def kill(self):
        self.__isDead = True

    def setRole(self, role: Role):
        self.__role = Role

    async def sendRole(self, boardType, fascists=None, hitler=None):
        if self.__role == Role.Liberal:
            desc = "For justice, liberty and equality!"
            col = "BLUE"
        elif self.__role == Role.Fascist:
            col = "ORANGE"
            if boardType == "FiveToSix":
                desc = f"Hitler is ***{hitler.values()[0]}***"
            elif boardType == "SevenToEight":
                desc = f"Your fellow fascist is *{[val for key, val in fascists.items() if key != self.id]}*, Hitler is ***{hitler.values()[0]}***"
            else:
                desc = f"Your fellow fascists are *{[val for key, val in fascists.items() if key != self.id]}*, Hitler is ***{hitler.values()[0]}***"
        else:
            col = "DARK_ORANGE"
            if boardType == "FiveToSix":
                desc = f"*{fascists.values()[0]}* is the fascist"
            else:
                desc = "You don't know who the other fascists are!"
        roleEmbed = Embed(
            title=f"You are ***{self.__role.name}***",
            colour=colours[col],
            description=desc,
        )
        file_embed = File(self.__role.getRolePic(), filename="role.png")
        roleEmbed.set_author(name=self.name, icon_url=self.avatar_url)
        roleEmbed.set_image(url="attachment://role.png")
        await self.__send(file_embed, roleEmbed)

    async def revealParty(self, president):
        partyName, partyPic, colour = self.__role.getParty()
        partyEmbed = Embed(
            title=f"{self.name} is from ***{partyName}*** party",
            colour=colours[colour],
        )
        file_embed = File(partyPic, filename="party.png")
        partyEmbed.set_author(name=self.name, icon_url=self.avatar_url)
        partyEmbed.set_image(url="attachment://party.png")
        await president.send(file_embed, partyEmbed)

    async def __send(self, fileObj, embedObj):
        await self.__user.send(file=fileObj, embed=embedObj)
