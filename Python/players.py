from enum import Enum


class Vote(Enum):
    nein = 0
    ja = 1

    def __str__(self):
        return self.name


class Player:
    def __init__(self, id: str, name: str, avatar: str, isbot: bool, user=None):
        self.__id = id
        self.__name = name
        self.__avatar = avatar
        self.__isbot = isbot
        self.__user = user
        self.__role = None
        self.__rolePic = None
        self.__vote = None

    def __str__(self):
        return vars(self)

    @classmethod
    def from_Discord(cls, user):
        return cls(user.id, user.name, user.avatar_url, user.bot, user)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def avatar(self) -> str:
        return self.__avatar

    @property
    def isbot(self) -> bool:
        return self.__isbot

    @property
    def role(self) -> str:
        return self.__role

    @property
    def rolePic(self) -> str:
        return self.__rolePic

    @property
    def vote(self) -> Vote:
        return self.__vote

    @property
    def dmChannelID(self) -> int:
        return self.__user.dm_channel.id

    @role.setter
    def role(self, role: str):
        self.__role = role

    @rolePic.setter
    def rolePic(self, rolePic: str):
        self.__rolePic = rolePic

    @vote.setter
    def vote(self, newVote: Vote):
        self.__vote = newVote

    async def send(self, fileObj, embedObj):
        if self.__user:
            await self.__user.send(file=fileObj, embed=embedObj)
