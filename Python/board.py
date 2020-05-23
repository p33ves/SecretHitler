
import random
from enum import Enum

import discord
from discord import Embed, File

from ballot_box import BallotBox, Vote
from players import Player
from setup import Setup, SetupType
from static_data import colours, images


# from PIL import Image


class BoardState(Enum):
    Inactive = 0
    Open = 1
    Active = 2

    def __str__(self):
        return self.name


class RoundType(Enum):
    Nomination = 0
    Election = 1
    Legislation = 2
    Execution = 3

    def __str__(self):
        return self.name


class Board:
    def __init__(self):
        self.__channel = None
        self.__owner = None
        self.__state = BoardState.Inactive
        self.__messageToEdit = None
        self.__players = list()
        self.__presidentIndex = 0
        self.__chancellor = None
        self.__prevPresidentID = None
        self.__prevChancellorID = None
        self.__roundType = RoundType.Nomination
        self.__ballotBox = BallotBox()

    def open(self, channel, boardOwner, messageToEdit):
        self.__channel = channel
        self.__owner = boardOwner
        self.__messageToEdit = messageToEdit
        self.__state = BoardState.Open

    def addPlayer(self, player: Player):
        if len(self.__players) > 9:
            raise Exception
        self.__players.append(player)

    def hasEnoughPlayers(self) -> bool:
        return len(self.__players) > 4

    def getPlayers(self):
        return self.__players.copy()

    def getPlayerCount(self) -> int:
        return len(self.__players)

    def checkPlayerID(self, id: int) -> bool:
        return id in [p.id for p in self.getPlayers()]

    def getDMChannelIDs(self):
        dm_channelID = dict()
        for player in self.__players:
            dm_channelID[player.id] = player.dmChannelID
        return dm_channelID


    async def generateAndSendRoles(self):
        rolesList = ["H", "L", "L", "L", "F", "L", "F", "L", "F", "L"]
        reqdRoles = rolesList[: self.getPlayerCount()]
        self.__setup = Setup(self.getPlayerCount())
        random.shuffle(self.__players)
        random.shuffle(reqdRoles)
        self.__fascists = dict()
        for i, p in enumerate(self.__players):
            if reqdRoles[i] == "L":
                p.role = "Liberal"
                p.rolePic = random.choice(images["role.png"]["Liberal"])
            elif reqdRoles[i] == "F":
                p.role = "Fascist"
                p.rolePic = random.choice(images["role.png"]["Fascist"])
                self.__fascists[p.id] = p.name
            else:
                p.role = "Hitler"
                p.rolePic = images["role.png"]["Hitler"]
                self.__hitler = {p.id: p.name}
        await self.__sendRoles()

    async def __sendRoles(self):
        for player in self.__players:
            if player.role == "Liberal":
                desc = "For justice, liberty and equality!"
                col = "BLUE"
            elif player.role == "Fascist":
                col = "ORANGE"
                if self.setup.setupType == SetupType.FiveToSix:
                    desc = f"Hitler is ***{list(self.hitler.values())[0]}***"
                elif self.setup.setupType == SetupType.SevenToEight:
                    desc = f"Your fellow fascist is *{[val for key, val in self.fascists.items() if key != player.id]}*, Hitler is ***{list(self.hitler.values())[0]}***"
                else:
                    desc = f"Your fellow fascists are *{[val for key, val in self.fascists.items() if key != player.id]}*, Hitler is ***{list(self.hitler.values())[0]}***"
            else:
                col = "RED"
                if self.setup.setupType == SetupType.FiveToSix:
                    desc = f"*{list(self.fascists.values())[0]}* is the fascist"
                else:
                    desc = "You don't know who the other fascists are!"
            roleEmbed = Embed(
                title=f"You are ***{player.role}***",
                colour=colours[col],
                description=desc,
            )
            file_embed = File(f"{player.rolePic}", filename="role.png")
            roleEmbed.set_author(name=player.name, icon_url=player.avatar)
            roleEmbed.set_image(url="attachment://role.png")
            await player.send(file_embed, roleEmbed)

    def nextPresident(self, newIndex=None):
        if newIndex is None:
            newIndex = self.__presidentIndex + 1
        self.__prevPresidentID = self.president.id
        self.__presidentIndex = newIndex
        if self.__chancellor:
            self.__prevChancellorID = self.__chancellor.id
            self.__chancellor = None

    def setChancellor(self, chancellorID):
        for p in self.__players:
            if p.id == chancellorID:
                self.__chancellor = p

    def getTableEmbed(self):
        if self.__roundType == RoundType.Nomination:
            desc = f"<@!{self.president.id}>, please pick the chancellor by typing *sh!p @<candidate name>*"
            col = "PURPLE"
        elif self.__roundType == RoundType.Election:
            desc = "All players, please enter *sh!v ja* -> to vote **YES** and *sh!v nein* -> to vote **NO**"
            col = "GREY"
        tableEmbed = discord.Embed(
            title=f"***\t {self.__roundType} Stage***",
            description=desc,
            colour=colours[col],
        )
        file_embed = discord.File(self.setup.gameBoard, filename="board.png")
        tableEmbed.set_author(
            name=self.president.name, icon_url=self.president.avatar
        )
        for p in self.getPlayers():
            if self.__roundType == RoundType.Nomination:
                if p.id == self.president.id:
                    val = "Current President"
                elif p.id == self.__prevChancellorID:
                    val = "Previous Chancellor"
                elif p.id == self.__prevPresidentID:
                    val = "Previous President"
                else:
                    val = "Waiting for chancellor nomination"
            elif self.__roundType == RoundType.Election:
                playerVote = self.__ballotBox.getVote(p.id)
                if playerVote is None:
                    val = "Yet to vote"
                else:
                    val = f"Voted {playerVote}"
            elif self.roundType == RoundType.Election:
                if p.id == self.__chancellor.id:
                    val = "Current Chancellor"
                else:
                    val = "Yet to vote"
            tableEmbed.add_field(name=p.name, value=val)
        return tableEmbed, file_embed

    def vote(self, playerID, vote: Vote):
        self.__ballotBox.vote(playerID, vote)

    def clearVotes(self):
        self.__ballotBox.clear()

    def votingComplete(self) -> bool:
        return len(self.__players) == self.__ballotBox.getTotalVoteCount()

    def getVoteSplit(self) -> (int, int):
        return self.__ballotBox.getVoteSplit()

    def electionResult(self) -> Vote:
        if self.__ballotBox.result() == Vote.nein:
            self.setup.failedElection += 1
        return self.__ballotBox.result()

    @property
    def channel(self):
        return self.__channel

    @property
    def owner(self):
        return self.__owner

    @property
    def state(self) -> BoardState:
        return self.__state

    @property
    def messageToEdit(self):
        return self.__messageToEdit

    @property
    def setup(self):
        return self.__setup

    @property
    def fascists(self):
        return self.__fascists

    @property
    def hitler(self):
        return self.__hitler

    @property
    def president(self):
        return self.__players[self.__presidentIndex]

    @property
    def prevPresidentID(self):
        return self.__prevPresidentID

    @property
    def prevChancellorID(self):
        return self.__prevChancellorID

    @property
    def roundType(self):
        return self.__roundType

    @property
    def chancellor(self):
        return self.__chancellor

    @state.setter
    def state(self, newState: BoardState):
        # TODO define exception
        self.__state = newState

    @roundType.setter
    def roundType(self, newInput: int):
        self.__roundType = newInput

    @messageToEdit.setter
    def messageToEdit(self, message):
        self.__messageToEdit = message