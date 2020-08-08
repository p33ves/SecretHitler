import random
from collections import namedtuple
from enum import Enum

import discord
from discord.ext.commands import Context

from vote_ballot import BallotBox, Vote
from role_player import Role, Player
from static_data import colours, images


class Players:
    def __init__(self):
        self.__playerList = list()
        self.__fascists = dict()
        self.__hitler = None
        self.__presidentElectIndex = 0
        self.__prevElectionWin = False
        self.__chancellorElectID = None
        self.__prevPresidentID = None
        self.__prevChancellorID = None
        self.__ballotBox = BallotBox()

    @property
    def count(self) -> int:
        return len(self.__playerList)

    @property
    def ballotBox(self) -> BallotBox:
        return self.__ballotBox

    @property
    def hitler(self) -> namedtuple:
        return self.__hitler

    @property
    def prevPresidentID(self) -> str:
        return self.__prevPresidentID

    @property
    def prevChancellorID(self) -> str:
        return self.__prevChancellorID

    @property
    def playersAlive(self) -> list:
        alive = list()
        for player in self.__playerList:
            if not player.isDead:
                alive.append(player)
        return alive

    @property
    def president(self) -> Player:
        return self.__playerList[self.__presidentElectIndex]

    @property
    def chancellor(self) -> Player:
        if self.__chancellorElectID:
            for player in self.__playerList:
                if player.id == self.__chancellorElectID:
                    return player

    def getPlayers(self) -> list:
        return self.__playerList

    def clearBallot(self):
        self.__ballotBox = BallotBox()

    def checkPlayerID(self, id: int) -> bool:
        for player in self.playersAlive:
            if id == player.id:
                return True
        return False

    async def generateRoles(self) -> int:
        rolesList = ["H", "L", "L", "L", "F", "L", "F", "L", "F", "L"]
        reqdRoles = rolesList[: self.count]
        random.shuffle(self.__playerList)
        random.shuffle(reqdRoles)
        for index, player in enumerate(self.__playerList):
            if reqdRoles[index] == "L":
                player.setRole(Role.Liberal)
            elif reqdRoles[index] == "F":
                player.setRole(Role.Fascist)
                self.__fascists[player.id] = player.name
            else:
                player.setRole(Role.Hitler)
                hitler = namedtuple("hitler", "id name")
                self.__hitler = hitler(player.id, player.name)
        for player in self.__playerList:
            await player.sendRole(self.count, self.__fascists, self.__hitler)

    def votingComplete(self) -> bool:
        return len(self.playersAlive) == self.__ballotBox.getTotalVoteCount()

    def freezePrevious(self):
        self.__prevPresidentID = self.president.id
        self.__prevChancellorID = self.chancellor.id

    def nextPresident(self, newIndex=None):
        if newIndex is None:
            newIndex = self.__presidentElectIndex + 1
            while self.__playerList[newIndex].isDead:
                if newIndex + 1 >= self.count:
                    newIndex = 0
                else:
                    newIndex += 1
        elif newIndex >= self.count:
            raise Exception("New president index greater than player count")
        self.__presidentElectIndex = newIndex
        self.__chancellorElectID = None

    async def addPlayer(self, channel: discord.channel, user: discord.User) -> bool:
        if self.count > 9:
            await channel.send(
                f"Sorry {user.name}, the current game has reached maximum player limit"
            )
            return False
        else:
            self.__playerList.append(Player(user))
            return True

    async def beginGame(self, channel: discord.channel, user: discord.User) -> bool:
        if self.count < 5:
            await channel.send(
                f"Sorry {user.name}, the game requires minimum 5 players"
            )
            return False
        return True

    async def pickChancellor(self, ctx: Context, arg: str) -> bool:
        if ctx.author.id != self.president.id:
            await ctx.send(f"Sorry {ctx.author.name}, you are not the president!")
        elif (
            arg[:3] != "<@!"
            or not self.checkPlayerID(int(arg[3:-1]))
            or int(arg[3:-1]) == self.__prevChancellorID
            or int(arg[3:-1]) == self.president.id
        ):
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid nomination, please retry!"
            )
        elif self.count > 6 and int(arg[3:-1]) == self.__prevPresidentID:
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid nomination, please retry!"
            )
        else:
            self.__chancellorElectID = int(arg[3:-1])
            return True
        return False

    async def markVote(self, ctx: Context, vote: str) -> bool:
        if not self.checkPlayerID(ctx.author.id):
            await ctx.send(f"Sorry {ctx.author.name}, you cannot vote")
        elif vote.upper() not in ("JA", "NEIN"):
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid vote, please retry!"
            )
        else:
            self.__ballotBox.vote(ctx.author.id, Vote[vote.upper()])
            return True
        return False

    async def assassinate(self, channel: discord.channel, playerID: int):
        for player in self.__playerList:
            if player.id == playerID:
                player.kill()
                await channel.send(
                    f"{player.name} has been assassinated by President {self.president.name}. RIP"
                )
                return

    async def inspect(self, channel: discord.channel, playerID: int):
        for player in self.__playerList:
            if player.id == playerID:
                await player.revealParty(self.president)
                await channel.send(
                    f"President {self.president.name} has inspected {player.name}'s party membership"
                )
                return

    async def chooseSuccessor(self, channel: discord.channel, playerID: int):
        index = None
        for ind, player in enumerate(self.getPlayers()):
            if player.id == playerID:
                index = ind
                break
        if index is None:
            raise Exception("Next chosen President ID not found ")
        self.nextPresident(index)
