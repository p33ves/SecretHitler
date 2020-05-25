from abc import ABC, abstractmethod

from discord.ext.commands import Context


class GameState(ABC):

    @abstractmethod
    async def join(self, ctx: Context, board) -> 'GameState':
        pass

    @abstractmethod
    async def start(self, ctx: Context, board) -> 'GameState':
        pass

    @abstractmethod
    async def pick(self, ctx: Context, board) -> 'GameState':
        pass

    @abstractmethod
    async def vote(self, ctx: Context, board) -> 'GameState':
        pass
