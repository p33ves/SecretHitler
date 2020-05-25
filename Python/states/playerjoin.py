from discord.ext.commands import Context

from players import Player
from states.gamestate import GameState
from states.chancellornomination import ChancellorNomination


class PlayerJoin(GameState):
    async def join(self, ctx: Context, board) -> 'GameState':
        if board.getPlayerCount() == 10:
            await ctx.send("The game is full please join a different game")
            return self
        board.addPlayer(Player(ctx.author))
        newEmbed = board.messageToEdit.embeds[0].copy()
        newEmbed.set_image(url="attachment://banner.jpg")
        newEmbed.add_field(name=board.getPlayerCount(), value=ctx.author.name)
        newEmbed.set_footer(text=f"{board.getPlayerCount()}/10 players joined")
        await board.messageToEdit.edit(embed=newEmbed)
        return self

    async def start(self,ctx: Context, board) -> 'GameState':
        count = board.getPlayerCount()
        if not (4 < count < 11):
            await ctx.send("Sorry, the game requires player count to be 5-10")
            return self
        else:
            await ctx.send(
                "*The year is 1932. The place is pre-WWII Germany. "
                "In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. "
                "Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler. "
                "Your roles will be sent to you as a Private Message. The future of the world depends on you."
                "So play wisely and remember, trust* ***no one.***"
            )
        board.messageToEdit = None
        await board.generateAndSendRoles()
        await showBoard(board, ctx.channel)
        return ChancellorNomination()

    async def pick(self, ctx: Context, board) -> 'GameState':
        await ctx.send("Waiting for game to start you cannot pick now")
        return self

    async def vote(self, ctx: Context, board) -> 'GameState':
        await ctx.send("Waiting for game to start you cannot vote now")
        return self


async def showBoard(board, channel):
    tableEmbed, file_embed = board.getTableEmbed()
    tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
    return await channel.send(file=file_embed, embed=tableEmbed)