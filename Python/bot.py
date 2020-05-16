import json
import random

import discord
from discord.ext import commands

with open("./auth.json", "r") as _authFile:
    token = json.load(_authFile)["token"]

with open("./images/colors.json", "r") as _colourFile:
    colours = json.load(_colourFile)


class Game:
    def __init__(self):
        self.active = False

    def open(self, channel, gameOwner, openMessage):
        self.channel = channel
        self.gameOwner = gameOwner
        self.openMessage = openMessage
        self.active = True
        self.players = list()

    def checkPlayerCount(self):
        return len(self.players) > 4 and len(self.players) < 11

    def generateRoles(self):
        rolesList = ["H", "L", "L", "L", "F", "L", "F", "L", "F", "L"]
        reqdRoles = rolesList[: len(self.players)]
        if len(self.players) < 7:
            self.boardType = 1
        elif len(self.players) < 9:
            self.boardType = 2
        else:
            self.boardType = 3
        random.shuffle(self.players)
        random.shuffle(reqdRoles)
        self.facists = set()
        for i, p in enumerate(self.players):
            if reqdRoles[i] == "L":
                p.role = "Liberal"
                p.rolePic = f"./images/Role_{p.role}{random.randint(0, 5)}.png"
            elif reqdRoles[i] == "F":
                p.role = "Facist"
                p.rolePic = f"./images/Role_{p.role}{random.randint(0, 2)}.png"
                self.facists.add(p.name)
            else:
                p.role = "Hitler"
                p.rolePic = f"./images/Role_{p.role}.png"
                self.hitler = p.name


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


client = discord.Client()
bot = commands.Bot(command_prefix="sh!")


@bot.event
async def on_ready():
    print("Time to fight fascism")


@bot.command()
async def test(ctx):
    welcome_embed = discord.Embed(
        title="***\t\t\t\t\t\t\t Welcome to Secret Hitler! ***", colour=colours["BLUE"]
    )
    file_embed = discord.File(
        "./images/WelcomeToSecretHitler.jpg", filename="welcome.jpg"
    )
    welcome_embed.set_image(url="attachment://welcome.jpg")
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
    file_embed = discord.File(
        "./images/SecretHitler_Thumbnail.png", filename="thumbnail.jpg"
    )
    playersEmbed.set_author(name=author.name, icon_url=author.avatar_url)
    playersEmbed.set_thumbnail(url="attachment://thumbnail.jpg")
    openMessage = await ctx.send(file=file_embed, embed=playersEmbed)
    game.open(channel, Player.from_Discord(author), openMessage)


@bot.command()
async def join(ctx):
    if game.active == False:
        await ctx.send(
            "Board has not been opened yet. Please type sh!open to a game first."
        )
    elif ctx.author.id not in [p.id for p in game.players]:
        game.players.append(Player.from_Discord(ctx.author))
        newEmbed = game.openMessage.embeds[0]
        newEmbed.add_field(name=str(len(game.players)), value=ctx.author.name)
        await game.openMessage.edit(embed=newEmbed)


@bot.command()
async def begin(ctx):
    if game.active == False:
        await ctx.send(
            "Board has not been opened yet. Please type sh!open to a game first."
        )
    elif game.checkPlayerCount() == False:
        await ctx.send("Sorry, the game requires player count to be 5-10")
        for i in range(5):
            game.players.append(Player(f"Bot{i}", 11110000 + i, None, True))
    else:
        await ctx.send(
            "*The year is 1932. The place is pre-WWII Germany. "
            "In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. "
            "Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler. "
            "Your roles will be sent to you as a Private Message. The future of the world depends on you."
            "So play wisely and remember, trust* ***no one.***"
        )
        game.generateRoles()
        for player in game.players:
            if player.isbot == False:
                user = bot.get_user(player.id)
                if player.role == "Liberal":
                    desc = "Hope you stand for the principles of liberty, justice and equality before the law."
                    col = "BLUE"
                elif player.role == "Facist":
                    col = "ORANGE"
                    if game.boardType == 1:
                        desc = f"Hitler is {game.hitler}"
                    elif game.boardType == 2:
                        desc = f"Your fellow facist is {game.facists.difference(set([player.name]))}, Hitler is {game.hitler}"
                    else:
                        desc = f"Your fellow facists are {game.facists.difference(set([player.name]))}, Hitler is {game.hitler}"
                else:
                    col = "RED"
                    if game.boardType == 1:
                        desc = f"{game.facists} is the facist"
                    else:
                        desc = "You don't know who the other facists are!"
                roleEmbed = discord.Embed(
                    title=f"You are the ***{player.role}***",
                    colour=colours[col],
                    description=desc,
                )
                file_embed = discord.File(f"{player.rolePic}", filename="role.png")
                roleEmbed.set_author(name=user.name, icon_url=user.avatar_url)
                roleEmbed.set_image(url="attachment://role.png")
                await user.send(file=file_embed, embed=roleEmbed)


game = Game()
bot.run(token)
