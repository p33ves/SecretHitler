
from enum import Enum

from PIL import Image

from policypile import Policy
from static_data import colours, images, coordinates


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
        self.__fascistPolicies = 0
        self.__base = images["baseboard.png"][self.__setupType.name]

    def sendImage(self) -> str:
        baseImg = Image.open(self.__base)
        dot = Image.open(images["dot.png"])
        new = baseImg.copy()
        new.paste(dot, coordinates["failedElection"][self.failedElection] , dot)
        new.save(images["currentboard.png"],"PNG")
        return images["currentboard.png"]

    def placePolicy(self, card: Policy):
        baseImg = Image.open(self.__base)
        new = baseImg.copy()
        if card == Policy.Fascist:
            cardImg = Image.open(card.getImageUrl())
            new.paste(cardImg, coordinates[card.name][self.__fascistPolicies])
            self.__fascistPolicies += 1           
        elif card == Policy.Liberal:
            cardImg = Image.open(card.getImageUrl())
            new.paste(cardImg, coordinates[card.name][self.__liberalPolicies])
            self.__liberalPolicies += 1
        new.save(images["newbase.png"],"PNG")
        self.__base = images["newbase.png"]
        
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
    def fascistPolicies(self):
        return self.__fascistPolicies

    @property
    def gameBoard(self) -> str:
        return self.sendImage()


    @failedElection.setter
    def failedElection(self, newInput: int):
        self.__failedElection = newInput

