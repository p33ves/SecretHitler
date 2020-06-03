from enum import Enum


class Vote(Enum):
    NEIN = 0
    JA = 1


class BallotBox:
    def __init__(self):
        self.__votedJa = []
        self.__votedNein = []

    def vote(self, playerId, vote: Vote):
        if not playerId in self.__votedJa and not playerId in self.__votedNein:
            if vote == Vote.NEIN:
                self.__votedNein.append(playerId)
            elif vote == Vote.JA:
                self.__votedJa.append(playerId)

    def getTotalVoteCount(self) -> int:
        return len(self.__votedJa) + len(self.__votedNein)

    def getVoteSplit(self) -> tuple():
        return len(self.__votedJa), len(self.__votedNein)

    def result(self) -> Vote:
        if len(self.__votedJa) > len(self.__votedNein):
            return Vote.JA
        else:
            return Vote.NEIN

    def getVote(self, id):
        if id in self.__votedJa:
            return Vote.JA
        elif id in self.__votedNein:
            return Vote.NEIN
        else:
            return None
