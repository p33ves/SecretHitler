import discord
from discord.ext.commands import Context

from ballot_box import Vote
from board import Board
from players import Role
from states.gamestate import GameState
from static_data import images, colours


class Election(GameState):
    async def join(self, ctx: Context, board) -> 'GameState':
        await ctx.send("The game is in progress you cannot join now")
        return self

    async def start(self, ctx: Context, board) -> 'GameState':
        await ctx.send("The game is already in progress")
        return self

    async def pick(self, ctx: Context, board) -> 'GameState':
        await ctx.send("The election is in progress you cannot pick now")
        return self

    async def vote(self, ctx: Context, board) -> 'GameState':
        args = ctx.message.content.split()[1:]
        vote = args[0]
        voteEnum = Vote.getEnum(vote)
        if len(args) > 1 or not voteEnum:
            await ctx.send(f"Sorry {ctx.author.name}, that seems to be an invalid entry")
        else:
            board.vote(ctx.author.id, Vote[vote])
            votingComplete = board.votingComplete()
            tableEmbed, file_embed = board.getTableEmbed()
            tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
            await board.messageToEdit.edit(embed=tableEmbed)
            if votingComplete:
                jaCount, neinCount = board.getVoteSplit()
                result = board.electionResult()
                if result == Vote.ja:
                    resultTitle = "\t Election *Passed*"
                    col = "DARK_GOLD"
                    img = images["vote.png"]["Ja"]
                    board.startLegislation()
                else:
                    resultTitle = "\t Election *Failed*"
                    col = "DARK_RED"
                    img = images["vote.png"]["Nein"]
                result_embed = discord.Embed(
                    title=resultTitle, colour=colours[col]
                )
                file_embed = discord.File(img, filename="vote.png")
                result_embed.set_image(url="attachment://vote.png")
                result_embed.set_footer(text=f"with splits of {jaCount} - {neinCount}")
                await board.channel.send(file=file_embed, embed=result_embed)
                if(result == Vote.nein)

        pass

async def checkIfFascWinByElection(ctx: Context, board: Board) -> bool:
    if board.chancellor.role == Role.Hitler and board.getFascistPolicyCount >= 3:
        await ctx.send("Fascists have won")
        return True
    return False
