class Player:
    def __init__(self, id: str, name: str, avatar: str, isbot: bool):
        self.__id = id
        self.__name = name
        self.__avatar = avatar
        self.__isbot = isbot

    def __str__(self):
        return vars(self)

    @classmethod
    def from_Discord(cls, user):
        return cls(user.name, user.id, user.avatar_url, user.bot)

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
