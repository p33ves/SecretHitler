
import random
from enum import Enum
from typing import Type

import discord
from discord import Embed, File

from players import Player, Vote
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


class BoardType(Enum):
    FiveToSix = 1
    SevenToEight = 2
    NineToTen = 3


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
        self.__gameBoard = None
        self.__roundType = RoundType.Nomination

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
        reqdRoles = rolesList[: len(self.__players)]
        if len(self.__players) < 7:
            self.__boardType = BoardType.FiveToSix
        elif len(self.__players) < 9:
            self.__boardType = BoardType.SevenToEight
        else:
            self.__boardType = BoardType.NineToTen
        random.shuffle(self.__players)
        random.shuffle(reqdRoles)
        self.__facists = dict()
        for i, p in enumerate(self.__players):
            if reqdRoles[i] == "L":
                p.role = "Liberal"
                p.rolePic = random.choice(images["role.png"]["Liberal"])
            elif reqdRoles[i] == "F":
                p.role = "Facist"
                p.rolePic = random.choice(images["role.png"]["Facist"])
                self.__facists[p.id] = p.name
            else:
                p.role = "Hitler"
                p.rolePic = images["role.png"]["Hitler"]
                self.__hitler = {p.id: p.name}
        self.__gameBoard = images["baseboard.png"][self.__boardType.name]
        await self.__sendRoles()

    async def __sendRoles(self):
        for player in self.__players:
            if player.role == "Liberal":
                desc = "For justice, liberty and equality!"
                col = "BLUE"
            elif player.role == "Facist":
                col = "ORANGE"
                if self.__boardType == BoardType.FiveToSix:
                    desc = f"Hitler is ***{list(self.hitler.values())[0]}***"
                elif self.__boardType == BoardType.SevenToEight:
                    desc = f"Your fellow facist is *{[val for key, val in self.facists.items() if key != player.id]}*, Hitler is ***{list(self.hitler.values())[0]}***"
                else:
                    desc = f"Your fellow facists are *{[val for key, val in self.facists.items() if key != player.id]}*, Hitler is ***{list(self.hitler.values())[0]}***"
            else:
                col = "RED"
                if self.__boardType == BoardType.FiveToSix:
                    desc = f"*{list(self.facists.values())[0]}* is the facist"
                else:
                    desc = "You don't know who the other facists are!"
            roleEmbed = Embed(
                title=f"You are the ***{player.role}***",
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
        self.__prevChancellorID = self.__chancellor.id
        self.__chancellor = None

    def setChancellor(self, chancellorID):
        for p in self.__players:
            if p.id == chancellorID:
                self.__chancellor = p

    def getTableEmbed(self):
        if self.__roundType == RoundType.Nomination:
            # Remove spaces in below tags when using n bots
            desc = f"<@! {self.president.id} >, please pick the chancellor by typing *sh!p @<candidate name>*"
            col = "PURPLE"
        elif self.__roundType == RoundType.Election:
            # Remove spaces in below tags when using n bots
            desc = "All players, please enter *sh!v ja* -> to vote **YES** and *sh!v nein* -> to vote **NO**"
            col = "GREY"
        tableEmbed = discord.Embed(
            title=f"***\t {self.__roundType} Stage***",
            description=desc,
            colour=colours[col],
        )
        file_embed = discord.File(self.__gameBoard, filename="board.png")
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
                if p.vote is None:
                    val = "Yet to vote"
                else:
                    val = f"Voted {p.vote}"
            elif self.roundType == RoundType.Election:
                if p.id == self.__chancellor.id:
                    val = "Current Chancellor"
                else:
                    val = "Yet to vote"
            tableEmbed.add_field(name=p.name, value=val)
        return tableEmbed, file_embed

    def setPlayerVote(self, playerID, vote : Vote) -> bool:
        check = True
        for player in self.__players:
            if player.id == playerID and player.vote is None:
                player.vote = vote
            if not player.vote:
                check = False
        return check
            
    def clearVotes(self):
        for player in self.__players:
                player.vote = None

    def countVotes(self) -> (bool, int, int):
        jc, nc = 0, 0
        for player in self.__players:
            if player.vote == Vote.ja:
                jc +=1
            elif player.vote == Vote.nein:
                nc +=1
        return jc > nc, jc, nc

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
    def boardType(self):
        return self.__boardType

    @property
    def facists(self):
        return self.__facists

    @property
    def hitler(self):
        return self.__hitler

    @property
    def president(self):
        return self.__players[self.__presidentIndex]

    @property
    def gameBoard(self):
        return self.__gameBoard

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