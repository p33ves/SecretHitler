import random
import typing
from enum import Enum

import discord
from discord.ext.commands import Context

from ballot_box import BallotBox, Vote
from board import Board, Power
from players import Player, Role
from policypile import Policy, PolicyPile
from static_data import colours, images


class GameStage(Enum):
    Undefined = 0
    Nomination = 1
    Election = 2
    Legislation = 3
    Execution = 4
    Completed = 5


class Game:
    def __init__(self, channel, user):
        self.__channel = channel
        self.__owner = user
        self.__board = Board()
        self.__players = list()
        self.__fascists = dict()
        self.__hitler = None
        self.__stage = GameStage.Undefined
        self.__presidentElectIndex = 0
        self.__chancellorElectID = None
        self.__prevPresidentID = None
        self.__prevChancellorID = None
        self.__cardsInPlay = list()
        self.__power = None
        self.__threeFascists = False

    @property
    def president(self) -> Player:
        return self.__players[self.__presidentElectIndex]

    @property
    def chancellor(self) -> Player:
        if self.__chancellorElectID:
            for player in self.__players:
                if player.id == self.__chancellorElectID:
                    return player
        return None

    async def launch(self):
        await self.__board.openBoard(self.__channel, self.__owner)

    async def join(self, user) -> bool:
        if len(self.__players) > 9:
            await self.__channel.send(
                f"Sorry {user.name}, the current game has reached maximum player limit"
            )
        elif await self.__board.joinBoard(
            self.__channel, user.name, len(self.__players)
        ):
            self.__players.append(Player(user))
            return True
        return False

    async def begin(self, user):
        if len(self.__players) < 5:
            await self.__channel.send(
                f"Sorry {user.name}, the game requires minimum 5 players"
            )
        elif await self.__board.beginBoard(self.__channel, user.name):
            self.__generateRoles()
            await self.__sendRoles()
            self.__stage = GameStage.Nomination
            await self.__board.showBoard(
                self.__channel,
                self.__stage.name,
                self.__players,
                self.president,
                self.chancellor,
                self.__prevPresidentID,
                self.__prevChancellorID,
                self.__power,
            )

    async def pick(self, ctx: Context):
        if not self.__stage.value or self.__stage == GameStage.Election:
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid command at the moment"
            )
        elif self.__stage == GameStage.Nomination:
            if ctx.author.id != self.president.id:
                await ctx.send(f"Sorry {ctx.author.name}, you are not the president!")
            else:
                args = ctx.message.content.split()[1:]
                chancellorTag = args[0]
                if (
                    len(args) > 1
                    or chancellorTag[:3] != "<@!"
                    or not self.__checkPlayerID(int(chancellorTag[3:-1]))
                    or int(chancellorTag[3:-1]) == self.__prevChancellorID
                    or int(chancellorTag[3:-1]) == self.president.id
                ):
                    await ctx.send(
                        f"Sorry {ctx.author.name}, thats an invalid nomination, please retry!"
                    )
                elif (
                    self.__board.type.name != "FiveToSix"
                    and int(chancellorTag[3:-1]) == self.__prevPresidentID
                ):
                    await ctx.send(
                        f"Sorry {ctx.author.name}, thats an invalid nomination, please retry!"
                    )
                else:
                    chancellorID = int(args[0][3:-1])
                    if self.__checkDead(chancellorID):
                        await ctx.send(
                            f"Sorry {ctx.author.name}, the nominee is dead, please retry!"
                        )
                    else:
                        self.__chancellorElectID = chancellorID
                        await self.__channel.send(
                            f"<@!{self.chancellor.id}> has been nominated as the chancellor by {self.president.name}"
                        )
                        self.__stage = GameStage.Election
                        self.__board.clearEdit()
                        await self.__board.showBoard(
                            self.__channel,
                            self.__stage.name,
                            self.__players,
                            self.president,
                            self.chancellor,
                            self.__prevPresidentID,
                            self.__prevChancellorID,
                            self.__power,
                        )
        elif self.__stage == GameStage.Legislation:
            args = ctx.message.content.split()[1:]
            if len(args) > 1 or not Policy.getEnum(args[0]):
                await ctx.send(
                    f"Sorry {ctx.author.name}, thats an invalid selection. Please retry!"
                )
            elif len(self.__cardsInPlay) == 3 and ctx.author.id == self.president.id:
                discardedPolicy = Policy.getEnum(args[0])
                await ctx.send(
                    f"You discarded {discardedPolicy.name}. Sending the rest to {self.chancellor.name} now."
                )
                self.__cardsInPlay = await self.__board.chancellorTurn(
                    self.chancellor, discardedPolicy
                )
            elif len(self.__cardsInPlay) == 2 and ctx.author.id == self.chancellor.id:
                pickedPolicy = Policy.getEnum(args[0])
                await ctx.send(
                    f"You picked {pickedPolicy.name}. Enacting it on the board now."
                )
                self.__cardsInPlay = list()
                await self.__channel.send(
                    f"A ***{pickedPolicy.name}*** policy has been placed on the board"
                )
                (
                    self.__power,
                    fascistPolicies,
                    liberalPolicies,
                ) = self.__board.endLegislation(pickedPolicy)
                await self.checkWin(fascistPolicies, liberalPolicies)
                if fascistPolicies <= 3:
                    self.__threeFascists = True
                self.__board.clearEdit()
                if self.__power:
                    self.__stage = GameStage.Execution
                else:
                    self.__nextPresident()
                    self.__stage = GameStage.Nomination
                await self.__board.showBoard(
                    self.__channel,
                    self.__stage.name,
                    self.__players,
                    self.president,
                    self.chancellor,
                    self.__prevPresidentID,
                    self.__prevChancellorID,
                    self.__power,
                )
            else:
                await ctx.send(
                    f"Sorry {ctx.author.name}, thats an invalid command at the moment"
                )
        elif self.__stage == GameStage.Execution:
            if ctx.author.id != self.president.id:
                await ctx.send(
                    f"Sorry {ctx.author.name}, you are not the current President"
                )
            else:
                args = ctx.message.content.split()[1:]
                playerTag = args[0]
                if (
                    len(args) > 1
                    or playerTag[:3] != "<@!"
                    or not self.__checkPlayerID(int(playerTag[3:-1]))
                    or int(playerTag[3:-1]) == self.president.id
                ):
                    await ctx.send(
                        f"Sorry {ctx.author.name}, that's an invalid selection, please retry!"
                    )
                elif (
                    self.__power == Power.getParty
                    or self.__power == Power.kill
                    or self.__power == Power.killVeto
                ):
                    player = None
                    for p in self.__players:
                        if int(playerTag[3:-1]) == p.id:
                            player = p
                            break
                        elif self.__checkDead(int(playerTag[3:-1])):
                            await ctx.send(
                                f"Sorry {ctx.author.name}, {player.name} is dead. Please check someone else!"
                            )
                            return
                    if not player:
                        raise Exception
                    elif self.__power == Power.getParty:
                        await player.revealParty(self.president)
                        await self.__channel.send(
                            f"{self.president.name} has viewed {player.name}'s party membership'"
                        )
                    else:
                        if player.isDead:
                            await ctx.send(
                                f"Sorry {ctx.author.name}, that's an invalid selection, {player.name} is already dead!"
                            )
                        else:
                            player.kill()
                            self.__board.playerCount -= 1
                            await self.checkWin()
                            self.__threeFascists = True
                            await self.__channel.send(
                                f"{player.name} has been assassinated. RIP."
                            )
                    self.__nextPresident()
                    self.__stage = GameStage.Nomination
                    self.__board.clearEdit()
                    self.__power = None
                    await self.__board.showBoard(
                        self.__channel,
                        self.__stage.name,
                        self.__players,
                        self.president,
                        self.chancellor,
                        self.__prevPresidentID,
                        self.__prevChancellorID,
                        self.__power,
                    )
                elif self.__power == Power.nextPresident:
                    index = None
                    for i, p in enumerate(self.__players):
                        if int(playerTag[3:-1]) == p.id:
                            index = i
                            break
                    if not index:
                        raise Exception
                    elif self.__players[index].isDead:
                        await ctx.send(
                            f"Sorry {ctx.author.name}, this player is dead, please choose someone alive!"
                        )
                    else:
                        await self.__channel.send(
                            f"{self.__players[index].name} has been chosen as the next president by {self.president.name}"
                        )
                        self.__nextPresident(index)
                        self.__power = None
                        self.__stage = GameStage.Nomination
                        self.__board.clearEdit()
                        await self.__board.showBoard(
                            self.__channel,
                            self.__stage.name,
                            self.__players,
                            self.president,
                            self.chancellor,
                            self.__prevPresidentID,
                            self.__prevChancellorID,
                            self.__power,
                        )

    async def vote(self, ctx: Context):
        if not self.__stage.value or self.__stage != GameStage.Election:
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid command at the moment"
            )
        elif self.__checkDead(ctx.author.id):
            await ctx.send(
                f"Sorry {ctx.author.name}, you cannot vote because you are dead."
            )
        else:
            args = ctx.message.content.split()[1:]
            if len(args) > 1 or args[0] not in [
                name for name, value in vars(Vote).items()
            ]:
                await ctx.send(
                    f"Sorry {ctx.author.name}, thats an invalid selection. Please retry!"
                )
            else:
                votingComplete = self.__board.markVote(ctx.author.id, args[0])
                await self.__board.showBoard(
                    self.__channel,
                    self.__stage.name,
                    self.__players,
                    self.president,
                    self.chancellor,
                    self.__prevPresidentID,
                    self.__prevChancellorID,
                    self.__power,
                )
                if votingComplete:
                    (
                        result,
                        (jaCount, neinCount),
                        failCount,
                    ) = self.__board.electionResult()
                    if result == Vote.ja:
                        resultTitle = "\t Election *Passed*"
                        col = "DARK_GOLD"
                        img = images["vote.png"]["Ja"]
                        desc = "Democracy prevails"
                        self.__freezePrevious(self.president.id, self.chancellor.id)
                        self.__stage = GameStage.Legislation
                    else:
                        if failCount == 3:
                            desc = f"The top policy will be drawn and placed"
                        else:
                            desc = f"Failed election marker moves forward"
                        resultTitle = "\t Election *Failed*"
                        col = "DARK_RED"
                        img = images["vote.png"]["Nein"]
                        self.__stage = GameStage.Nomination
                    self.__board.clearEdit()
                    result_embed = discord.Embed(
                        title=resultTitle, description=desc, colour=colours[col]
                    )
                    file_embed = discord.File(img, filename="vote.png")
                    result_embed.set_image(url="attachment://vote.png")
                    result_embed.set_footer(
                        text=f"with splits of {jaCount} - {neinCount}"
                    )
                    if failCount == 3:
                        (
                            fascistsCount,
                            liberalCount,
                        ) = await self.__board.failedElectionReset(self.__channel)
                        if fascistsCount <= 3:
                            self.__threeFascists = True
                        await self.checkWin(fascistsCount, liberalCount)
                    await self.__channel.send(file=file_embed, embed=result_embed)
                    if self.__stage == GameStage.Nomination:
                        self.__nextPresident()
                        self.__board.clearEdit()
                        await self.__board.showBoard(
                            self.__channel,
                            self.__stage.name,
                            self.__players,
                            self.president,
                            self.chancellor,
                            self.__prevPresidentID,
                            self.__prevChancellorID,
                            self.__power,
                        )
                    else:
                        await self.__startLegislation()

    async def see(self, ctx: Context):
        if (
            self.__stage != GameStage.Execution
            or self.__power != Power.peekTop3
            or self.president.id != ctx.author.id
        ):
            await ctx.send(
                f"Sorry {ctx.author.name}, this seems to be an invalid command"
            )
        else:
            await self.__board.executeTop3(self.president)
            self.__power = None
            self.__nextPresident()
            self.__stage = GameStage.Nomination
            self.__board.clearEdit()
            await self.__channel.send(
                f"President {ctx.author.name} has peeked the next set of Policies"
            )
            await self.__board.showBoard(
                self.__channel,
                self.__stage.name,
                self.__players,
                self.president,
                self.chancellor,
                self.__prevPresidentID,
                self.__prevChancellorID,
                self.__power,
            )

    async def veto(self, ctx: Context):
        if self.__power != Power.killVeto or self.president.id != ctx.author.id:
            await self.__channel.send(
                f"Sorry {ctx.author.name}, you don't have the power to veto!"
            )

    async def checkWin(self, fascistPolicies=0, liberalPolicies=0):
        if self.__threeFascists and list(self.__hitler.keys())[0] == self.chancellor.id:
            await self.__channel.send("Facists win! Hitler has been made Chancellor")
            self.__stage = GameStage.Completed
        elif fascistPolicies == 6:
            await self.__channel.send(
                "Facists win! 6 Fascist policies have been passed"
            )
            self.__stage = GameStage.Completed
        elif liberalPolicies == 5:
            await self.__channel.send(
                "Liberals win! 5 Liberal policies have been passed"
            )
            self.__stage = GameStage.Completed
        else:
            for player in self.__players:
                if player.id == list(self.__hitler.keys())[0] and player.isDead:
                    await self.__channel.send(
                        "Liberals win! Hitler has been assassinated"
                    )
                    self.__stage = GameStage.Completed

    def __generateRoles(self):
        rolesList = ["H", "L", "L", "L", "F", "L", "F", "L", "F", "L"]
        reqdRoles = rolesList[: len(self.__players)]
        self.__board.setType(len(self.__players))
        random.shuffle(self.__players)
        random.shuffle(reqdRoles)
        for index, player in enumerate(self.__players):
            if reqdRoles[index] == "L":
                player.setRole(Role.Liberal)
            elif reqdRoles[index] == "F":
                player.setRole(Role.Fascist)
                self.__fascists[player.id] = player.name
            else:
                player.setRole(Role.Hitler)
                self.__hitler = {player.id: player.name}

    def __checkPlayerID(self, id: int) -> bool:
        for player in self.__players:
            if id == player.id:
                return True
        return False

    def __nextPresident(self, newIndex=None):
        if newIndex is None:
            newIndex = self.__presidentElectIndex + 1
            while self.__players[newIndex].isDead:
                newIndex += 1
        self.__presidentElectIndex = newIndex
        self.__chancellorElectID = None

    def __freezePrevious(self, presidentID, chancellorID):
        self.__prevPresidentID = presidentID
        self.__prevChancellorID = chancellorID

    def __checkDead(self, id: int) -> bool:
        for player in self.__players:
            if player.id == id:
                return player.isDead

    async def __sendRoles(self):
        for player in self.__players:
            await player.sendRole(
                self.__board.type.name, self.__fascists, self.__hitler
            )

    async def __startLegislation(self):
        self.__cardsInPlay = await self.__board.presidentTurn(
            self.__channel, self.president
        )
