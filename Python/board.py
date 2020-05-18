import random
from enum import Enum
from typing import Type

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
    def players(self):
        return self.__players

    @property
    def openMessage(self):
        return self.__openMessage

    @property
    def type(self):
        return self.__type

    @state.setter
    def state(self, newState: Type[BoardState]):
        # TODO define exception
        self.__state = newState

    def checkPlayerCount(self) -> bool:
        return len(self.__players) > 4 and len(self.__players) < 11

    @property
    def facists(self):
        return set(p for p in self.__players if p.id in self.__facists)

    @property
    def hitler(self):
        return (p for p in self.__players if p.id == self.__hitler)

    def generateRoles(self):
        rolesList = ["H", "L", "L", "L", "F", "L", "F", "L", "F", "L"]
        reqdRoles = rolesList[: len(self.__players)]
        if len(self.__players) < 7:
            self.__type = 1
        elif len(self.__players) < 9:
            self.__type = 2
        else:
            self.__type = 3
        random.shuffle(self.__players)
        random.shuffle(reqdRoles)
        self.__facists = set()
        for i, p in enumerate(self.__players):
            if reqdRoles[i] == "L":
                p.role = "Liberal"
                p.rolePic = f"./images/Role_{p.role}{random.randint(0, 5)}.png"
            elif reqdRoles[i] == "F":
                p.role = "Facist"
                p.rolePic = f"./images/Role_{p.role}{random.randint(0, 2)}.png"
                self.__facists.add(p.id)
            else:
                p.role = "Hitler"
                p.rolePic = f"./images/Role_{p.role}.png"
                self.__hitler = p.id
