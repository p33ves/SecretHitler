import json

import discord
from discord.ext import commands

from board import Board, BoardState
from players import Player

with open("./images/colors.json", "r") as _colourFile:
    colours = json.load(_colourFile)

bot = commands.Bot(command_prefix="sh!")
board = Board()


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
    welcome_embed.set_footer(
        text=f"@{ctx.author.name}, your Ping is: {round(bot.latency * 1000)}ms"
    )
    await ctx.send(file=file_embed, embed=welcome_embed)
    # await ctx.send(f"<@!{ctx.message.author.id}> Hiiiiii")


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
        file_embed = discord.File(
            "./images/SecretHitler_Thumbnail.png", filename="thumbnail.png"
        )
        playersEmbed.set_author(name=author.name, icon_url=author.avatar_url)
        playersEmbed.set_thumbnail(url="attachment://thumbnail.png")
        openMessage = await ctx.send(file=file_embed, embed=playersEmbed)
        board.open(channel, Player.from_Discord(author), openMessage)


@bot.command()
async def join(ctx):
    if board.channel.id != ctx.channel.id:
        await ctx.send(
            f"Board has not been opened on this channel. Please ask {board.owner.name} for directions"
        )
    else:
        if board.state == BoardState.Inactive:
            await ctx.send(
                "Board has not been opened yet. Please enter sh!open to a game first."
            )
        elif board.state != BoardState.Open:
            await ctx.send(
                f"You cannot join right now because the game is {board.state}"
            )
        elif ctx.author.id not in [p.id for p in board.players]:
            board.players.append(Player.from_Discord(ctx.author))
            newEmbed = board.openMessage.embeds[0]
            newEmbed.add_field(name=str(len(board.players)), value=ctx.author.name)
            await board.openMessage.edit(embed=newEmbed)


@bot.command()
async def begin(ctx):
    if board.channel.id != ctx.channel.id:
        await ctx.send(
            f"Board has not been opened on this channel. Please ask {board.owner.name} for directions"
        )
    else:
        if board.state == BoardState.Inactive:
            await ctx.send(
                "Board has not been opened yet. Please enter sh!open to a game first."
            )
        elif board.state != BoardState.Open:
            await ctx.send(
                f"You cannot begin right now because the game is {board.state}"
            )
        else:
            args = ctx.message.content.split()[1:]
            errorFlag = False
            if len(args):
                noOfBots = 0
                if args[0] == "-autobot":
                    try:
                        if int(args[1]) > 0:
                            noOfBots = int(args[1])
                    except IndexError:
                        errorFlag = True
                else:
                    errorFlag = True
                if errorFlag:
                    await ctx.send("Invalid argument!")
                else:
                    for i in range(noOfBots):
                        board.addPlayer(
                            Player(str(11110000 + i), f"Bot{i}", None, True)
                        )
            if not board.hasEnoughPlayers():
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
                board.generateRoles()
                for player in board.getPlayers():
                    if player.isbot == False:
                        user = bot.get_user(player.id)
                        if player.role == "Liberal":
                            desc = "For justice, liberty and equality!"
                            col = "BLUE"
                        elif player.role == "Facist":
                            col = "ORANGE"
                            if board.boardType == 1:
                                desc = (
                                    f"Hitler is ***{list(board.hitler.values())[0]}***"
                                )
                            elif board.boardType == 2:
                                desc = f"Your fellow facist is *{[val for key, val in board.facists.items() if key != player.id]}*, Hitler is ***{list(board.hitler.values())[0]}***"
                            else:
                                desc = f"Your fellow facists are *{[val for key, val in board.facists.items() if key != player.id]}*, Hitler is ***{list(board.hitler.values())[0]}***"
                        else:
                            col = "RED"
                            if board.boardType == 1:
                                desc = (
                                    f"*{list(board.facists.values())[0]}* is the facist"
                                )
                            else:
                                desc = "You don't know who the other facists are!"
                        roleEmbed = discord.Embed(
                            title=f"You are the ***{player.role}***",
                            colour=colours[col],
                            description=desc,
                        )
                        file_embed = discord.File(
                            f"{player.rolePic}", filename="role.png"
                        )
                        roleEmbed.set_author(name=user.name, icon_url=user.avatar_url)
                        roleEmbed.set_image(url="attachment://role.png")
                        await user.send(file=file_embed, embed=roleEmbed)
                tableEmbed, file_embed = showTable()
                await ctx.send(file=file_embed, embed=tableEmbed)


@bot.command()
async def table(ctx):
    if board.channel.id != ctx.channel.id:
        await ctx.send(
            f"Board has not been opened on this channel. Please ask {board.owner.name} for directions"
        )
    elif board.state != BoardState.Active:
        await ctx.send(
            "Board is not been active on this channel. Please retry after activating the game"
        )
    else:
        tableEmbed, file_embed = showTable()
        await ctx.send(file=file_embed, embed=tableEmbed)


@bot.command()
async def t(ctx):
    if board.channel.id != ctx.channel.id:
        await ctx.send(
            f"Board has not been opened on this channel. Please ask {board.owner.name} for directions"
        )
    elif board.state != BoardState.Active:
        await ctx.send(
            "Board is not been active on this channel. Please retry after activating the game"
        )
    else:
        tableEmbed, file_embed = showTable()
        await ctx.send(file=file_embed, embed=tableEmbed)


def showTable():
    tableEmbed = discord.Embed(
        title=f"**\t President: {board.president.name}  **",
        # Remove spaces in below tags when using n bots
        description=f"<@! {board.president.id} >, please pick the chancellor by typing sh!p @<candidate name>",
        colour=colours["PURPLE"],
    )
    file_embed = discord.File(board.gameBoard, filename="board.png")
    """
    Commented due to presence of bots
    tableEmbed.set_author(
        name=game.president.name, icon_url=game.president.avatar
    )
    """
    for p in board.getPlayers():
        if p.id == board.president.id:
            val = "Current President"
        elif p.id == board.prevChancellorID:
            val = "Previous Chancellor"
        elif p.id == board.prevPresidentID:
            val = "Previous President"
        elif board.roundType == 0:
            val = "Waiting for chancellor nomination"
        tableEmbed.add_field(name=p.name, value=val)
    tableEmbed.set_image(url="attachment://board.png")
    return (tableEmbed, file_embed)
    # game.open(channel, Player.from_Discord(author), openMessage)


def main():
    with open("./auth.json", "r") as _authFile:
        token = json.load(_authFile)["token"]

    bot.run(token)


if __name__ == "__main__":
    main()
