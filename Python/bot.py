import json

import discord
from discord.ext import commands
from discord.ext.commands import Context

from game import Game
from static_data import colours, images


bot = commands.Bot(command_prefix="sh!")
currentGames = dict()
currentUsers = dict()


@bot.event
async def on_ready():
    print("Time to fight fascism")


@bot.command()
async def test(ctx: Context):
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
    # TODO Allow reset only by owners/ autoreset after a timeout
    if ctx.channel.id in currentGames.keys():
        del currentGames[ctx.channel.id]
    if ctx.channel.id in currentUsers.keys():
        del currentUsers[ctx.channel.id]
    await ctx.send(f"Game has been reset on #{ctx.channel.name}")


@bot.command()
async def launch(ctx: Context):
    if not ctx.guild:
        await ctx.send(
            f"Sorry {ctx.author.name}, the game can only be started sever text channel"
        )
    elif checkGames(ctx.channel.id):
        await ctx.send(
            f"Sorry {ctx.author.name}, a game is currently in-progress in this channel"
        )
    else:
        currentGames[ctx.channel.id] = Game(ctx.channel, ctx.author)
        currentUsers[ctx.channel.id] = dict()
        await currentGames[ctx.channel.id].launch()


@bot.command()
async def join(ctx: Context):
    if not await inGameChannel(ctx):
        return
    elif checkActiveUser(ctx.author.id):
        await ctx.send(
            f"Sorry {ctx.author.name}, you already seem to be active in a game"
        )
    elif await currentGames[ctx.channel.id].join(ctx.author):
        if not ctx.author.dm_channel:
            await ctx.author.create_dm()
        currentUsers[ctx.channel.id][ctx.author.id] = ctx.author.dm_channel.id


@bot.command()
async def begin(ctx: Context):
    if not await inGameChannel(ctx):
        return
    await currentGames[ctx.channel.id].begin(ctx.author)


@bot.command()
async def p(ctx: Context):
    if await validSourceChannel(ctx) and getGame(ctx.author.id):
        gameChannel = getGame(ctx.author.id)
        await currentGames[gameChannel].pick(ctx)


@bot.command()
async def v(ctx: Context):
    if await validSourceChannel(ctx) and getGame(ctx.author.id):
        gameChannel = getGame(ctx.author.id)
        await currentGames[gameChannel].vote(ctx)


@bot.command()
async def see(ctx: Context):
    if await validSourceChannel(ctx) and getGame(ctx.author.id):
        gameChannel = getGame(ctx.author.id)
        await currentGames[gameChannel].see(ctx)


@bot.command()
async def veto(ctx: Context):
    if await validSourceChannel(ctx) and getGame(ctx.author.id):
        gameChannel = getGame(ctx.author.id)
        await currentGames[gameChannel].veto(ctx)


def checkGames(channelID: int) -> bool:
    return channelID in currentGames.keys()


def checkActiveUser(userID: int) -> bool:
    for users in currentUsers.values():
        if userID in users.keys():
            return True
    return False


def getGame(userID: int) -> int:
    for channelID, users in currentUsers.items():
        if userID in users.keys():
            return channelID
    return 0


async def inGameChannel(ctx):
    if not ctx.guild:
        await ctx.send(
            f"Sorry {ctx.author.name}, this game action can only be performed via a valid sever text channel"
        )
    elif not checkGames(ctx.channel.id):
        await ctx.send(f"Sorry {ctx.author.name}, no active game in this channel")
    else:
        return True
    return False


async def validSourceChannel(ctx) -> bool:
    validUser = False
    for channelID, users in currentUsers.items():
        if ctx.author.id in users.keys() and channelID in currentGames.keys():
            validUser = True
            if ctx.channel.id == channelID or ctx.channel.id == users[ctx.author.id]:
                return True
    if validUser:
        await ctx.send(
            f"Sorry {ctx.author.name}, correspondence through this channel is not allowed"
        )
    else:
        await ctx.send(f"Sorry {ctx.author.name}, you don't seem to be in a game")
    return False


def main():
    with open("./auth.json", "r") as _authFile:
        token = json.load(_authFile)["token"]

    bot.run(token)


if __name__ == "__main__":
    main()
