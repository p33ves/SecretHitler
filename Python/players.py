class Player:
    def __init__(self, name, id, avatar, isbot):
        self.id = id
        self.name = name
        self.avatar = avatar
        self.isbot = isbot

    def __str__(self):
        return vars(self)

    @classmethod
    def from_Discord(cls, user):
        return cls(user.name, user.id, user.avatar_url, user.bot)
