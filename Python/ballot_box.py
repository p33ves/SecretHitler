from enum import Enum


class Vote(Enum):
    nein = 0
    ja = 1

    def __str__(self):
        return self.name


class BallotBox:

    def __init__(self):
        self.__votedJa = []
        self.__votedNein = []

    def vote(self, playerId, vote: Vote):
        if not playerId in self.__votedJa and not playerId in self.__votedNein:
            if vote == Vote.nein:
                self.__votedNein.append(playerId)
            elif vote == Vote.ja:
                self.__votedJa.append(playerId)

    def getTotalVoteCount(self) -> int:
        return len(self.__votedJa) + len(self.__votedNein)

    def getVoteSplit(self) -> ():
        return len(self.__votedJa), len(self.__votedNein)

    def result(self) -> Vote:
        if len(self.__votedJa) > len(self.__votedNein):
            return Vote.ja
        else:
            return Vote.nein

    def clear(self):
        self.__votedJa.clear()
        self.__votedNein.clear()

    def getVote(self, id):
        if id in self.__votedJa:
            return Vote.ja
        elif id in self.__votedNein:
            return Vote.nein
        else:
            return None
