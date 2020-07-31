from enum import Enum

from static_data import images


class Power(Enum):
    getParty = 1
    peekTop3 = 2
    nextPresident = 3
    kill = 4
    killVeto = 5


class BoardType(Enum):
    FiveToSix = 1
    SevenToEight = 2
    NineToTen = 3

    def getBaseBoard(self) -> str:
        return images["baseboard.png"][self.name]

    def getPowers(self, cardIndex: int) -> Power:
        powers = {4: Power.kill, 5: Power.killVeto}
        if self.value == 3:
            powers[1] = Power.getParty
        if self.value > 1:
            powers[3] = Power.nextPresident
            powers[2] = Power.getParty
        elif self.value == 1:
            powers[3] = Power.peekTop3
        else:
            raise Exception
        if cardIndex in powers.keys():
            return powers[cardIndex]
        return None
