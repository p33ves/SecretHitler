
import json

import discord
from discord.ext import commands

from board import Board, BoardState, RoundType
from players import Player, Vote
from static_data import colours, images

bot = commands.Bot(command_prefix="sh!")
board = Board()


@bot.event
async def on_ready():
    print("Time to fight fascism")


@bot.command()
async def test(ctx):
    welcome_embed = discord.Embed(
        title="***\t Welcome to Secret Hitler! ***", colour=colours["BLUE"]
    )
    file_embed = discord.File(images["welcome.png"], filename="welcome.png")
    welcome_embed.set_image(url="attachment://welcome.png")
    welcome_embed.set_footer(
        text=f"@{ctx.author.name}, your Ping is: {round(bot.latency * 1000)}ms"
    )
    await ctx.send(file=file_embed, embed=welcome_embed)


@bot.command()
async def reset(ctx):
    global board
    board = Board()


@bot.command()
async def launch(ctx):
    if board.state != BoardState.Inactive:
        await ctx.send(
            f"A game opened by {board.owner.name} is already in {board.state} state. Please try to join that or try again later."
        )
    else:
        author = ctx.author
        channel = ctx.channel
        playersEmbed = discord.Embed(
            title="**\t Player List **",
            description="A board has been opened. Please enter sh!join if you wish to join the game.",
            colour=colours["AQUA"],
        )
        file_embed = discord.File(images["banner.jpg"], filename="banner.jpg")
        playersEmbed.set_author(name=author.name, icon_url=author.avatar_url)
        playersEmbed.set_image(url="attachment://banner.jpg")
        playersEmbed.set_footer(text="Player limit: 5-10")
        openMessage = await ctx.send(file=file_embed, embed=playersEmbed)
        board.open(channel, Player(author), openMessage)


@bot.command()
async def join(ctx):
    if not inChannel(ctx):
        return
    else:
        if board.state == BoardState.Inactive:
            await ctx.send(
                "Board has not been opened yet. Please enter *sh!launch* to a game first."
            )
        elif board.state != BoardState.Open:
            await ctx.send(
                f"You cannot join right now because the game is {board.state}"
            )
        elif not board.checkPlayerID(ctx.author.id):
            board.addPlayer(Player(ctx.author))
            newEmbed = board.messageToEdit.embeds[0].copy()
            newEmbed.set_image(url="attachment://banner.jpg")
            newEmbed.add_field(name=board.getPlayerCount(), value=ctx.author.name)
            newEmbed.set_footer(text=f"{board.getPlayerCount()}/10 players joined")
            await board.messageToEdit.edit(embed=newEmbed)


@bot.command()
async def begin(ctx):
    if not inChannel(ctx):
        return
    elif board.state == BoardState.Inactive:
        await ctx.send(
            "Board has not been opened yet. Please enter sh!open to a game first."
        )
    elif board.state != BoardState.Open:
        await ctx.send(
            f"You cannot begin right now because the game is {board.state}"
        )
    elif not board.hasEnoughPlayers():
            await ctx.send("Sorry, the game requires player count to be 5-10")
    else:
        await ctx.send(
            "*The year is 1932. The place is pre-WWII Germany. "
            "In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. "
            "Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler. "
            "Your roles will be sent to you as a Private Message. The future of the world depends on you."
            "So play wisely and remember, trust* ***no one.***"
        )
        board.state = BoardState.Active
        board.messageToEdit = None
        await board.generateAndSendRoles()
        tableEmbed, file_embed = board.getTableEmbed()
        tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
        await ctx.send(file=file_embed, embed=tableEmbed)


@bot.command()
async def table(ctx):
    if not inChannel(ctx):
        return
    elif not activeBoard(ctx):
        return
    else:
        tableEmbed, file_embed = board.getTableEmbed()
        tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
        await ctx.send(file=file_embed, embed=tableEmbed)


@bot.command()
async def t(ctx):
    if not inChannel(ctx):
        return
    elif not activeBoard(ctx):
        return
    else:
        tableEmbed, file_embed = board.getTableEmbed()
        tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
        await ctx.send(file=file_embed, embed=tableEmbed)


@bot.command()
async def p(ctx):
    if not validSource(ctx):
        return
    elif not activeBoard(ctx):
        return
    else:
        if ctx.author.id != board.president.id:
            await ctx.send(f"Sorry {ctx.author.name}, you are not the President!")   
        else:
            args = ctx.message.content.split()[1:]
            if board.roundType == RoundType.Nomination:
                chancellorTag = args[0]
                if (
                    len(args) > 1
                    or chancellorTag[:3] != "<@!"
                    or not board.checkPlayerID(int(chancellorTag[3:-1]))
                    or chancellorTag[3:-1] == board.prevChancellorID
                    or chancellorTag[3:-1] == board.president.id
                ):
                    await ctx.send(f"Invalid nomination, please retry!")
                else:
                    chancellorID = args[0][3:-1]
                    board.setChancellor(chancellorID)
                    await ctx.send(f"{args[0]} has been nominated as the chancellor")
                    board.roundType = RoundType.Election
                    tableEmbed, file_embed = board.getTableEmbed()
                    tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
                    voteMessage = await ctx.send(file=file_embed, embed=tableEmbed)
                    board.messageToEdit = voteMessage

@bot.command()
async def v(ctx):
    if not validSource(ctx):
        return
    elif not activeBoard(ctx):
        return
    elif not playerInGame(ctx):
        return
    elif board.roundType != RoundType.Election:
        await ctx.send(
            f"Sorry {ctx.author.name}, this isn't election phase!"
        )
    else:
        args = ctx.message.content.split()[1:]
        vote = args[0]
        if len(args) > 1 or vote not in [name for name, value in vars(Vote).items()]:
            await ctx.send(f"Sorry {ctx.author.name}, that seems to be an invalid entry")
        else:
            allVoted = board.setPlayerVote(ctx.author.id, Vote[vote])
            tableEmbed, file_embed = board.getTableEmbed()
            tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
            await board.messageToEdit.edit(embed=tableEmbed)
            if allVoted:
                result, jaCount, neinCount = board.countVotes()
                if result:
                    resultTitle = "\t Election *Passed*"
                    col = "DARK_GOLD"
                    img = images["vote.png"]["Ja"]
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
                await ctx.send(file=file_embed, embed=result_embed)
                board.roundType = RoundType.Legislation


async def inChannel(ctx) -> bool:
    if board.channel.id != ctx.channel.id:
        await ctx.send(
            f"Board has not been opened on this channel. Please ask {board.owner.name} for directions"
        )
        return False
    return True


async def validSource(ctx) -> bool:
    if board.channel.id != ctx.channel.id and ctx.channel.id not in board.getDMChannelIDs().values():
        await ctx.send(
            f"Board has not been opened on this channel. Please ask {board.owner.name} for directions"
        )
        return False
    return True


async def activeBoard(ctx) -> bool:
    if board.state != BoardState.Active:
        await ctx.send(
            "Board is not been active on this channel. Please retry after activating the game"
        )
        return False
    return True


async def playerInGame(ctx) -> bool:
    if not board.checkPlayerID(ctx.author.id):
        await ctx.send(
            f"Sorry {ctx.author.name}, you don't seem to have joined this game"
        )
        return False
    return True

def main():
    with open("./auth.json", "r") as _authFile:
        token = json.load(_authFile)["token"]

    bot.run(token)


if __name__ == "__main__":
    main()
