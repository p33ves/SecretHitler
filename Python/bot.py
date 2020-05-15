import json

import discord
from discord.ext import commands

with open("auth.json", "r") as authFile:
    token = json.load(authFile)["token"]

with open("images/colors.json", "r") as colourFile:
    colours = json.load(colourFile)


class Game:
    def __init__(self):
        self.active = False

    def open(self, channel, gameOwner, openMessage):
        self.channel = channel
        self.gameOwner = gameOwner
        self.active = True
        self.openMessage = openMessage
        self.players = set()


client = discord.Client()
bot = commands.Bot(command_prefix="sh!")


@bot.event
async def on_ready():
    print("Time to fight fascism")


@bot.command()
async def test(ctx):
    welcome_embed = discord.Embed(
        title="***\t Welcome to Secret Hitler! ***", colour=colours["BLUE"]
    )
    file_embed = discord.File(
        "images/WelcomeToSecretHitler.png", filename="welcome.png"
    )
    welcome_embed.set_image(url="attachment://welcome.png")
    welcome_embed.set_footer(text=f"Ping: {round(bot.latency * 1000)}ms")
    await ctx.send(file=file_embed, embed=welcome_embed)


@bot.command()
async def open(ctx):
    author = ctx.author
    channel = ctx.channel
    playersEmbed = discord.Embed(
        title="**\t Player List **",
        description=f"A board has been opened. Please type sh!join if you wish to join the game.",
        colour=colours["AQUA"],
    )
    playersEmbed.set_author(name=author.name, icon_url=ctx.author.avatar_url)
    openMessage = await ctx.send(embed=playersEmbed)
    game.open(channel, author, openMessage)


@bot.command()
async def join(ctx):
    if game.active == False:
        await ctx.send(
            "Board has not been opened yet. Please type sh!open to a game first."
        )
    elif ctx.author not in game.players:
        game.players.add(ctx.author)
        newEmbed = game.openMessage.embeds[-1]
        newEmbed.add_field(name=str(len(game.players) + 1), value=ctx.author.name)
        await game.openMessage.edit(embed=newEmbed)


@bot.command()
async def begin(ctx):
    await ctx.send(
        """
        *The year is 1932. The place is pre-WWII Germany. In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler.*"""
    )


game = Game()
bot.run(token)
