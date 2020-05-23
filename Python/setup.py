
from enum import Enum

from PIL import Image

from static_data import colours, images


class SetupType(Enum):
    FiveToSix = 1
    SevenToEight = 2
    NineToTen = 3


class Setup:
    def __init__(self, numOfPlayers: int):
        if numOfPlayers < 7:
            self.__setupType = SetupType.FiveToSix
        elif numOfPlayers < 9:
            self.__setupType = SetupType.SevenToEight
        else:
            self.__setupType = SetupType.NineToTen
        self.__failedElection = 0
        self.__liberalPolicies = 0
        self.__facistPolicies = 0
        self.__setupBase = images["baseboard.png"][self.__setupType.name]

    @property
    def setupType(self):
        return self.__setupType

    @property
    def failedElection(self):
        return self.__failedElection

    @property
    def liberalPolicies(self):
        return self.__liberalPolicies

    @property
    def facistPolicies(self):
        return self.__facistPolicies

    @property
    def gameBoard(self):
        return self.__setupBase
