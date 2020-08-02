from enum import Enum

import discord
from discord.ext.commands import Context
from PIL import Image

from vote_ballot import Vote
from board_powers import BoardType, Power
from game_state import State
from role_player import Player
from players_manager import Players
from policy_pile import Policy, PolicyPile
from static_data import colours, coordinates, images


class Board:
    def __init__(self):
        self.__messageToEdit = None
        self.__type = None
        self.__playerCount = 0
        self.__base = ""
        self.__policyPile = PolicyPile()
        self.__failedElection = 0
        self.__fascistPolicies = 0
        self.__liberalPolicies = 0

    def __getImage(self, id: int) -> str:
        baseImg = Image.open(self.__base)
        dot = Image.open(images["dot.png"])
        new = baseImg.copy()
        new.paste(dot, coordinates["failedElection"]
                  [self.__failedElection], dot)
        new.save(images["currentboard.png"].replace(
            "<channelID>", f"{id}"), "PNG")
        return images["currentboard.png"].replace("<channelID>", f"{id}")

    def __placePolicy(self, card: Policy, id: int) -> Power:
        baseImg = Image.open(self.__base)
        new = baseImg.copy()
        power = None
        if card == Policy.Fascist:
            cardImg = Image.open(card.getImageUrl())
            new.paste(cardImg, coordinates[card.name][self.__fascistPolicies])
            self.__fascistPolicies += 1
            power = self.__type.getPowers(self.__fascistPolicies)
        elif card == Policy.Liberal:
            cardImg = Image.open(card.getImageUrl())
            new.paste(cardImg, coordinates[card.name][self.__liberalPolicies])
            self.__liberalPolicies += 1
        new.save(images["newbase.png"].replace("<channelID>", f"{id}"), "PNG")
        self.__base = images["newbase.png"].replace("<channelID>", f"{id}")
        return power

    @property
    def policyPile(self) -> PolicyPile:
        return self.__policyPile

    def setType(self, numOfPlayers: int):
        if numOfPlayers < 7:
            self.__type = BoardType.FiveToSix
        elif numOfPlayers < 9:
            self.__type = BoardType.SevenToEight
        else:
            self.__type = BoardType.NineToTen
        self.__playerCount = numOfPlayers
        self.__base = self.__type.getBaseBoard()

    def clearEdit(self):
        self.__messageToEdit = None

    def getCardCount(self) -> tuple:
        return self.__fascistPolicies, self.__liberalPolicies

    async def openBoard(self, channel, user):
        playersEmbed = discord.Embed(
            title="**\t Player List **",
            description="A board has been opened. Please enter *sh!join* if you wish to join the game.",
            colour=colours["AQUA"],
        )
        file_embed = discord.File(images["banner.jpg"], filename="banner.jpg")
        playersEmbed.set_author(name=user.name, icon_url=user.avatar_url)
        playersEmbed.set_image(url="attachment://banner.jpg")
        playersEmbed.set_footer(text="Player limit: 5-10")
        self.__messageToEdit = await channel.send(file=file_embed, embed=playersEmbed)

    async def joinBoard(self, channel, userName: str, playerCount: int):
        newEmbed = self.__messageToEdit.embeds[0].copy()
        newEmbed.set_image(url="attachment://banner.jpg")
        newEmbed.add_field(name=playerCount, value=userName)
        newEmbed.set_footer(text=f"{playerCount}/10 players joined")
        await self.__messageToEdit.edit(embed=newEmbed)

    async def beginBoard(self, channel):
        self.clearEdit()
        await channel.send(
            "*The year is 1932. The place is pre-WWII Germany. "
            "In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. "
            "Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler. "
            "There are a total of 17 policies (11 Fascist and 6 Liberal) to choose from."
            "Your roles will be sent to you as a Private Message. The future of the world depends on you."
            "So play wisely and remember, trust* ***no one.***"
        )
        return True

    async def showBoard(self, channel, state: State, players: Players, power: Power):
        def getEmbed():
            if state == State.Nomination:
                desc = f"<@!{players.president.id}>, please pick the chancellor by typing *sh!p @<candidate name>*"
                col = "PURPLE"
            elif state == State.Election:
                desc = "All players, please enter *sh!v ja* -> to vote **YES** and *sh!v nein* -> to vote **NO**"
                col = "GREEN"
            elif state == State.Legislation:
                desc = "The President and the Chancellor would be enacting their policies via private message"
                col = "LIGHT_GREY"
            elif state == State.Execution:
                col = "DARK_VIVID_PINK"
                if not power:
                    raise Exception
                elif power == Power.getParty:
                    desc = f"<@!{players.president.id}>, please pick a player to inspect their party membership by typing *sh!p @<candidate name>*"
                elif power == Power.nextPresident:
                    desc = f"<@!{players.president.id}>, please pick a player to choose as the next President by typing *sh!p @<candidate name>*"
                elif power == Power.peekTop3:
                    desc = f"<@!{players.president.id}>, please pick see the next 3 policies from the draw pile by typing *sh!see*"
                elif power == Power.kill:
                    desc = f"<@!{players.president.id}>, please pick a player to assassinate by typing *sh!p @<candidate name>*"
                elif power == Power.killVeto:
                    desc = f"<@!{players.president.id}>, please pick a player to assassinate by typing *sh!p @<candidate name>* and to veto the policies drawn in this round, type *sh!veto*"
            tableEmbed = discord.Embed(
                title=f"***\t {state}*** Stage", description=desc, colour=colours[col],
            )
            file_embed = discord.File(self.__getImage(
                channel.id), filename="board.png")
            tableEmbed.set_author(
                name=players.president.name, icon_url=players.president.avatar_url
            )
            tableEmbed.set_footer(
                text=f"Number of cards left in the draw pile is {self.__policyPile.noOfCardsInDeck}"
            )
            for player in players.getPlayers():
                if not player.isDead:
                    if state == State.Nomination:
                        if player.id == players.president.id:
                            val = "Current President"
                        elif player.id == players.prevChancellorID:
                            val = "Previous Chancellor"
                        elif player.id == players.prevPresidentID:
                            val = "Previous President"
                        else:
                            val = "Waiting for chancellor nomination"
                    elif state == State.Election:
                        playerVote = players.ballotBox.getVote(player.id)
                        if playerVote is None:
                            val = "Yet to vote"
                        else:
                            val = f"Voted {playerVote.name}"
                    elif state == State.Legislation:
                        if (
                            player.id == players.president.id
                            or player.id == players.chancellor.id
                        ):
                            val = "Picking policy"
                        else:
                            val = "Waiting for Policy legislation"
                    elif state == State.Execution:
                        if player.id == players.president.id:
                            val = "Enacting policy"
                        else:
                            val = "Waiting for Policy execution"
                    tableEmbed.add_field(name=player.name, value=val)
                else:
                    tableEmbed.add_field(
                        name=f"~~{player.name}~~", value="Dead")
            return file_embed, tableEmbed

        file_embed, tableEmbed = getEmbed()
        tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
        if self.__messageToEdit is None:
            self.__messageToEdit = await channel.send(file=file_embed, embed=tableEmbed)
        else:
            await self.__messageToEdit.edit(embed=tableEmbed)

    async def electionResult(self, channel: discord.channel, players: Players):
        flag = None
        result = players.ballotBox.result()
        jaCount, neinCount = players.ballotBox.getVoteSplit()
        players.clearBallot()
        if result == Vote.NEIN:
            self.__failedElection += 1
            if self.__failedElection == 3:
                desc = "The top policy will be drawn and placed"
                flag = True
            else:
                desc = "Failed election marker moves forward"
                flag = False
            resultTitle = "\t Election *Failed*"
            col = "DARK_RED"
            img = images["vote.png"]["Nein"]
        else:
            self.__failedElection = 0
            resultTitle = "\t Election *Passed*"
            col = "DARK_GOLD"
            img = images["vote.png"]["Ja"]
            desc = "Democracy prevails"
        result_embed = discord.Embed(
            title=resultTitle, description=desc, colour=colours[col]
        )
        file_embed = discord.File(img, filename="vote.png")
        result_embed.set_image(url="attachment://vote.png")
        result_embed.set_footer(text=f"with splits of {jaCount} - {neinCount}")
        await channel.send(file=file_embed, embed=result_embed)
        return flag

    async def placeRandomPolicy(self, channel: discord.channel) -> tuple:
        top = self.__policyPile.placeTopPolicy()
        self.__failedElection = 0
        self.__placePolicy(top, channel.id)
        await channel.send(
            f"A {top.name} policy has been picked from the draw pile and has been placed"
        )
        return self.getCardCount()

    async def pickPolicy(
        self, channel: discord.channel, ctx: Context, arg: str, players: Players
    ):
        if ctx.author.id not in (players.president.id, players.chancellor.id):
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid selection. Please wait for the President and Chancellor to pick"
            )
        elif not Policy.getEnum(arg):
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid selection. Please retry!"
            )
        elif (
            ctx.author.id == players.president.id
            and self.__policyPile.cardsInPlay.count == 3
        ):
            discardedPolicy = Policy.getEnum(arg)
            await ctx.send(
                f"You discarded {discardedPolicy.name}. Sending the rest to {players.chancellor.name} now."
            )
            await self.policyPile.chancellorTurn(players.chancellor, discardedPolicy)
            return True
        elif (
            ctx.author.id == players.chancellor.id
            and self.__policyPile.cardsInPlay.count == 2
        ):
            pickedPolicy = Policy.getEnum(arg)
            await ctx.send(
                f"You picked {pickedPolicy.name}. Enacting it on the board now."
            )
            self.__policyPile.acceptPolicy(pickedPolicy)
            await channel.send(
                f"A ***{pickedPolicy.name}*** policy has been placed on the board"
            )
            return self.__placePolicy(pickedPolicy, channel.id)
        else:
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid selection at the moment"
            )
        return False
