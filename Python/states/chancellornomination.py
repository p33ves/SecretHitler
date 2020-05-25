from discord.ext.commands import Context

from states.election import Election
from states.gamestate import GameState


class ChancellorNomination(GameState):

    async def join(self, ctx: Context, board) -> 'GameState':
        await ctx.send("The game is in progress you cannot join now")
        return self

    async def start(self, ctx: Context, board) -> 'GameState':
        await ctx.send("The game is already in progress")
        return self

    async def pick(self, ctx: Context, board) -> 'GameState':
        if ctx.author.id != board.president.id:
            await ctx.send(f"Sorry {ctx.author.name}, you are not the President!")
            return self
        else:
            args = ctx.message.content.split()[1:]
            chancellorTag = args[0]
            if (
                    len(args) > 1
                    or chancellorTag[:3] != "<@!"
                    or not board.checkPlayerID(int(chancellorTag[3:-1]))
                    or chancellorTag[3:-1] == board.prevChancellorID
                    or chancellorTag[3:-1] == board.president.id
            ):
                await ctx.send(f"Invalid nomination, please retry!")
                return self
            else:
                chancellorID = args[0][3:-1]
                board.setChancellor(chancellorID)
                await board.channel.send(f"{args[0]} has been nominated as the chancellor")
                voteMessage = await showBoard(board, board.channel)
                board.messageToEdit = voteMessage
        return Election()

    async def vote(self, ctx: Context, board) -> 'GameState':
        await ctx.send("Chancellor Nomination is in progress you cannot vote")
        return self

async def showBoard(board, channel):
    tableEmbed, file_embed = board.getTableEmbed()
    tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
    return await channel.send(file=file_embed, embed=tableEmbed)