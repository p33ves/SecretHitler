import enum
import json
import random

import discord
from discord.ext import commands

import board
from players import Player

game = None
colours = None
bot = None
game = board.Board()
state = board.BoardState()


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
async def table(ctx):
    if game.state != state.Inactive:
        await ctx.send(
            f"A game opened by {game.owner.name} is already in {game.state} state. Please try to join that or try again later."
        )
    else:
        author = ctx.author
        channel = ctx.channel
        playersEmbed = discord.Embed(
            title="**\t Player List **",
            description=f"A board has been opened. Please type sh!join if you wish to join the game.",
            colour=colours["AQUA"],
        )
        file_embed = discord.File(
            "./images/SecretHitler_Thumbnail.png", filename="thumbnail.png"
        )
        playersEmbed.set_author(name=author.name, icon_url=author.avatar_url)
        playersEmbed.set_thumbnail(url="attachment://thumbnail.png")
        openMessage = await ctx.send(file=file_embed, embed=playersEmbed)
        game.open(channel, Player.from_Discord(author), openMessage)


@bot.command()
async def join(ctx):
    if game.state == state.Inactive:
        await ctx.send(
            "Board has not been opened yet. Please type sh!open to a game first."
        )
    elif game.state != state.Open:
        await ctx.send(f"You cannot join right now because the game is {game.state}")
    elif ctx.author.id not in [p.id for p in game.players]:
        game.players.append(Player.from_Discord(ctx.author))
        newEmbed = game.openMessage.embeds[0]
        newEmbed.add_field(name=str(len(game.players)), value=ctx.author.name)
        await game.openMessage.edit(embed=newEmbed)


@bot.command()
async def begin(ctx):
    if game.state == state.Inactive:
        await ctx.send(
            "Board has not been opened yet. Please type sh!open to a game first."
        )
    elif game.state == state.Open:
        args = ctx.message.content.split()[1:]
        errorFlag = False
        if len(args):
            noOfBots = 0
            if args[0] == "-autobot":
                try:
                    if int(args[1]) > 0:
                        noOfBots = int(args[1])
                except:
                    errorFlag = True
            else:
                errorFlag = True
            if errorFlag:
                await ctx.send("Invalid argument!")
            else:
                for i in range(noOfBots):
                    game.players.append(Player(f"Bot{i}", 11110000 + i, None, True))
        if game.checkPlayerCount() == False:
            await ctx.send("Sorry, the game requires player count to be 5-10")
        else:
            await ctx.send(
                "*The year is 1932. The place is pre-WWII Germany. "
                "In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. "
                "Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler. "
                "Your roles will be sent to you as a Private Message. The future of the world depends on you."
                "So play wisely and remember, trust* ***no one.***"
            )
            game.state = state.Active
            game.generateRoles()
            for player in game.players:
                if player.isbot == False:
                    user = bot.get_user(player.id)
                    if player.role == "Liberal":
                        desc = "Hope you stand for the principles of liberty, justice and equality before the law."
                        col = "BLUE"
                    elif player.role == "Facist":
                        col = "ORANGE"
                        if game.type == 1:
                            desc = f"Hitler is {game.hitler}"
                        elif game.type == 2:
                            desc = f"Your fellow facist is {game.facists.difference(set([player.name]))}, Hitler is {game.hitler}"
                        else:
                            desc = f"Your fellow facists are {game.facists.difference(set([player.name]))}, Hitler is {game.hitler}"
                    else:
                        col = "RED"
                        if game.type == 1:
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
    else:
        await ctx.send(f"You cannot begin right now because the game is {game.state}")


def main():
    global colours
    global game
    global bot

    with open("./auth.json", "r") as _authFile:
        token = json.load(_authFile)["token"]

    with open("./images/colors.json", "r") as _colourFile:
        colours = json.load(_colourFile)

    bot = commands.Bot(command_prefix="sh!")
    bot.run(token)


if __name__ == "__main__":
    main()
