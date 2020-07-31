from enum import Enum

import discord


class State(Enum):
    GameOver = None
    Inactive = 0
    Nomination = 1
    Election = 2
    Legislation = 3
    Execution = 4

    def checkActive(self) -> bool:
        try:
            return bool(self.value)
        except AttributeError:
            return False

    @classmethod
    def launch(cls, currentState) -> Enum:
        if not cls.checkActive(currentState):
            return cls.Inactive
        else:
            raise Exception

    async def check(self, other, channel: discord.channel, user: discord.User) -> bool:
        if self is other:
            return True
        else:
            await channel.send(
                f"Sorry {user.name}, that's an invalid command at the moment"
            )

    """
    Create decorator for next state progression
    """
