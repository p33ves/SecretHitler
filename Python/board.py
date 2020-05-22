import random
from enum import Enum
from typing import Type

import discord
from discord import Embed, File

from players import Player
from static_data import colours


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

    def generateAndSendRoles(self):
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
                p.rolePic = f"./images/Role_{p.role}{random.randint(0, 5)}.png"
            elif reqdRoles[i] == "F":
                p.role = "Facist"
                p.rolePic = f"./images/Role_{p.role}{random.randint(0, 2)}.png"
                self.__facists[p.id] = p.name
            else:
                p.role = "Hitler"
                p.rolePic = f"./images/Role_{p.role}.png"
                self.__hitler = {p.id: p.name}
        self.__gameBoard = f"./images/Board{self.boardType.value}.png"
        self.__sendRoles()

    def __sendRoles(self):
        for player in self.__players:
            if player.role == "Liberal":
                desc = "For justice, liberty and equality!"
                col = "BLUE"
            elif player.role == "Facist":
                col = "ORANGE"
                if self.__boardType == BoardType.FiveToSix:
                    desc = (
                        f"Hitler is ***{list(self.hitler.values())[0]}***"
                    )
                elif self.__boardType == BoardType.SevenToEight:
                    desc = f"Your fellow facist is *{[val for key, val in self.facists.items() if key != player.id]}*, Hitler is ***{list(self.hitler.values())[0]}***"
                else:
                    desc = f"Your fellow facists are *{[val for key, val in self.facists.items() if key != player.id]}*, Hitler is ***{list(self.hitler.values())[0]}***"
            else:
                col = "RED"
                if self.__boardType == BoardType.SevenToEight:
                    desc = (
                        f"*{list(self.facists.values())[0]}* is the facist"
                    )
                else:
                    desc = "You don't know who the other facists are!"
            roleEmbed = Embed(
                title=f"You are the ***{player.role}***",
                colour=colours[col],
                description=desc,
            )
            file_embed = File(
                f"{player.rolePic}", filename="role.png"
            )
            roleEmbed.set_author(name=player.name, icon_url=player.avatar_url)
            roleEmbed.set_image(url="attachment://role.png")
            player.send(file_embed, roleEmbed)

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
        if self.roundType == RoundType.Nomination:
            # Remove spaces in below tags when using n bots
            desc = f"<@! {self.president.id} >, please pick the chancellor by typing *sh!p @<candidate name>*"
            col = "PURPLE"
        elif self.roundType == RoundType.Election:
            # Remove spaces in below tags when using n bots
            desc = f"All players, please enter *sh!v ja* -> to vote **YES** and *sh!v nein* -> to vote **NO**"
            col = "GREY"
        tableEmbed = discord.Embed(
            title=f"***\t {self.roundType} Stage***",
            description=desc,
            colour=colours[col],
        )
        file_embed = discord.File(self.gameBoard, filename="board.png")
        """
        Commented due to presence of bots
        tableEmbed.set_author(
            name=game.president.name, icon_url=game.president.avatar
        )
        """
        for p in self.getPlayers():
            if p.id == self.president.id:
                val = "Current President"
            elif p.id == self.chancellor.id:
                val = "Current Chancellor"
            elif p.id == self.prevChancellorID:
                val = "Previous Chancellor"
            elif p.id == self.prevPresidentID:
                val = "Previous President"
            elif self.roundType == RoundType.Nomination:
                val = "Waiting for chancellor nomination"
            elif self.roundType == RoundType.Election:
                val = "Yet to vote"
            tableEmbed.add_field(name=p.name, value=val)
        tableEmbed.set_image(url="attachment://board.png")
        return tableEmbed, file_embed


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
    def state(self, newState: Type[BoardState]):
        # TODO define exception
        self.__state = newState

    @roundType.setter
    def roundType(self, newInput: int):
        self.__roundType = newInput

    @messageToEdit.setter
    def messageToEdit(self, message):
        self.__messageToEdit = message
