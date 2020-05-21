import random
from enum import Enum
from typing import boardType

from players import Player

# from PIL import Image


class BoardState(Enum):
    Inactive = 0
    Open = 1
    Active = 2

    def __str__(self):
        return self.name


class Board:
    def __init__(self):
        self.__channel = None
        self.__owner = None
        self.__state = BoardState.Inactive

    def open(self, channel, boardOwner, openMessage):
        self.__channel = channel
        self.__owner = boardOwner
        self.__openMessage = openMessage
        self.__state = BoardState.Open
        self.__players = list()

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

    def generateRoles(self):
        rolesList = ["H", "L", "L", "L", "F", "L", "F", "L", "F", "L"]
        reqdRoles = rolesList[: len(self.__players)]
        if len(self.__players) < 7:
            self.__boardType = 1
        elif len(self.__players) < 9:
            self.__boardType = 2
        else:
            self.__boardType = 3
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
        self.__presidentIndex = 0
        self.__chancellor = None
        self.__prevPresidentID = None
        self.__prevChancellorID = None
        self.__gameBoard = f"./images/Board{self.__boardType}.png"
        self.__roundType = 0

    def nextPresident(self, newIndex=None):
        if newIndex is None:
            newIndex = self.__presidentIndex + 1
        self.__prevPresidentID = self.president.id
        self.__presidentIndex = newIndex

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
    def openMessage(self):
        return self.__openMessage

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

    @state.setter
    def state(self, newState: boardType[BoardState]):
        # TODO define exception
        self.__state = newState

    @roundType.setter
    def roundType(self, newInput: int):
        self.__roundType = newInput
