class Player:
    def __init__(self, user):
        self.__user = user
        self.__role = None
        self.__rolePic = None
        self.__vote = None
        self.__isDead = False

    def __str__(self):
        return vars(self)

    @property
    def id(self) -> str:
        return self.__user.id

    @property
    def name(self) -> str:
        return self.__user.name

    @property
    def avatar(self) -> str:
        return self.__user.avatar_url

    @property
    def role(self) -> str:
        return self.__role

    @property
    def rolePic(self) -> str:
        return self.__rolePic

    @property
    def dmChannelID(self) -> int:
        return self.__user.dm_channel.id

    @role.setter
    def role(self, role: str):
        self.__role = role

    @rolePic.setter
    def rolePic(self, rolePic: str):
        self.__rolePic = rolePic

    def kill(self):
        self.__isDead = True

    @property
    def isDead(self):
        return self.__isDead

    async def send(self, fileObj, embedObj):
        await self.__user.send(file=fileObj, embed=embedObj)
