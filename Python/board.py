import random
from enum import Enum

import discord
from PIL import Image

from ballot_box import BallotBox, Vote
from game import GameStage
from players import Player
from policypile import Policy, PolicyPile
from static_data import colours, coordinates, images


class BoardState(Enum):
    Inactive = 0
    Open = 1
    Active = 2


class Power(Enum):
    getParty = 1
    peekTop3 = 2
    nextPresident = 3
    kill = 4
    killVeto = 5


class BoardType(Enum):
    FiveToSix = 1
    SevenToEight = 2
    NineToTen = 3

    def getBaseBoard(self) -> str:
        return images["baseboard.png"][self.name]

    def getPowers(self, cardIndex: int) -> Power:
        powers = {4: Power.kill, 5: Power.killVeto}
        if self.value == 3:
            powers[1] = Power.getParty
        if self.value > 1:
            powers[3] = Power.nextPresident
            powers[2] = Power.getParty
        elif self.value == 1:
            powers[3] = Power.peekTop3
        else:
            raise Exception
        if cardIndex in powers.keys():
            return powers[cardIndex]
        return None


class Board:
    def __init__(self):
        self.__state = BoardState.Inactive
        self.__messageToEdit = None
        self.__type = None
        self.__playerCount = 0
        self.__base = None
        self.__ballotBox = BallotBox()
        self.__policyPile = PolicyPile()
        self.__failedElection = 0
        self.__fascistPolicies = 0
        self.__liberalPolicies = 0

    @property
    def type(self) -> BoardType:
        return self.__type

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

    def markVote(self, playerID: int, vote: str):
        self.__ballotBox.vote(playerID, vote)
        return self.__votingComplete()

    def electionResult(self) -> tuple():
        self.clearEdit()
        if self.__ballotBox.result() == Vote.nein:
            self.__failedElection += 1
        return (
            self.__ballotBox.result(),
            self.__ballotBox.getVoteSplit(),
            self.__failedElection,
        )

    def endLegislation(self, picked: Policy) -> tuple():
        self.__policyPile.acceptPolicy(picked)
        return (
            self.__placePolicy(picked),
            self.__fascistPolicies,
            self.__liberalPolicies,
        )

    async def openBoard(self, channel: channel, user: user):
        self.__state = BoardState.Open
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

    async def joinBoard(self, channel: channel, userName: str, playerCount: int):
        if await self.__checkBoardState(channel, userName, "Open"):
            newEmbed = self.__messageToEdit.embeds[0].copy()
            newEmbed.set_image(url="attachment://banner.jpg")
            newEmbed.add_field(name=playerCount + 1, value=userName)
            newEmbed.set_footer(text=f"{playerCount+1}/10 players joined")
            return await self.__messageToEdit.edit(embed=newEmbed)

    async def beginBoard(self, channel: channel, userName: str):
        if await self.__checkBoardState(channel, userName, "Open"):
            self.__state = BoardState.Active
            self.__messageToEdit = None
            await channel.send(
                "*The year is 1932. The place is pre-WWII Germany. "
                "In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. "
                "Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler. "
                "Your roles will be sent to you as a Private Message. The future of the world depends on you."
                "So play wisely and remember, trust* ***no one.***"
            )
            return True

    async def showBoard(
        self,
        channel: channel,
        stage: GameStage,
        players: list(),
        president: Player,
        chancellor: Player,
        prevPresidentID: int,
        prevChancellorID: int,
        power: str,
    ):
        def getEmbed():
            if stage == GameStage.Nomination:
                desc = f"<@!{president.id}>, please pick the chancellor by typing *sh!p @<candidate name>*"
                col = "PURPLE"
            elif stage == GameStage.Election:
                desc = "All players, please enter *sh!v ja* -> to vote **YES** and *sh!v nein* -> to vote **NO**"
                col = "GREY"
            elif stage == GameStage.Execution:
                col = "DARK_VIVID_PINK"
                if not power:
                    raise Exception
                elif power == Power.getParty:
                    desc = f"<@!{president.id}>, please pick a player to inspect their party membership by typing *sh!p @<candidate name>*"
                elif power == Power.nextPresident:
                    desc = f"<@!{president.id}>, please pick a player to choose as the next President by typing *sh!p @<candidate name>*"
                elif power == Power.peekTop3:
                    desc = f"<@!{president.id}>, please pick see the next 3 policies from the draw pile by typing *sh!see*"
                elif power == Power.kill:
                    desc = f"<@!{president.id}>, please pick a player to assassinate by typing *sh!p @<candidate name>*"
                elif power == Power.killVeto:
                    desc = f"<@!{president.id}>, please pick a player to assassinate by typing *sh!p @<candidate name>* and to veto the policies drawn in this round, type *sh!veto*"
            tableEmbed = discord.Embed(
                title=f"***\t {stage.name}*** Stage",
                description=desc,
                colour=colours[col],
            )
            file_embed = discord.File(self.__getImage(), filename="board.png")
            tableEmbed.set_author(name=president.name, icon_url=president.avatar_url)
            for player in players:
                if not player.isDead:
                    if stage == GameStage.Nomination:
                        if player.id == president.id:
                            val = "Current President"
                        elif player.id == prevChancellorID:
                            val = "Previous Chancellor"
                        elif player.id == prevPresidentID:
                            val = "Previous President"
                        else:
                            val = "Waiting for chancellor nomination"
                    elif stage == GameStage.Election:
                        playerVote = self.__ballotBox.getVote(player.id)
                        if playerVote is None:
                            val = "Yet to vote"
                        else:
                            val = f"Voted {playerVote}"
                    elif stage == GameStage.Legislation:
                        if player.id == president.id or player.id == chancellor.id:
                            val = "Picking policy"
                        else:
                            val = "Waiting for Policy legislation"
                    elif stage == GameStage.Execution:
                        if player.id == president.id:
                            val = "Enacting policy"
                        else:
                            val = "Waiting for Policy execution"
                    tableEmbed.add_field(name=player.name, value=val)
                else:
                    tableEmbed.add_field(name=f"~~{player.name}~~", value="Dead")
            return file_embed, tableEmbed

        file_embed, tableEmbed = await getEmbed()
        tableEmbed.set_image(url=f"attachment://{file_embed.filename}")
        if not self.__messageToEdit:
            self.__messageToEdit = await channel.send(file=file_embed, embed=tableEmbed)
        else:
            await self.__messageToEdit.edit(embed=tableEmbed)

    async def presidentTurn(self, channel, president: Player) -> list():
        shuffled = self.__policyPile.draw()
        cardsInPlay = self.__policyPile.peekCardsInPlay()
        if shuffled:
            await channel.send(
                f"The deck has been reshuffled and there are {self.__policyPile.noOfCardsInDeck}"
            )
        file_embed = discord.File(
            images["presidentdeck.png"][cardsInPlay.count(Policy.Fascist)],
            filename="policydeck.png",
        )
        cardsEmbed = discord.Embed(
            title=f"\t **Discard** one Policy",
            description="Type *sh!p <color/name>* of the card that you wish to discard from the 3 given below: ",
            colour=colours["DARK_AQUA"],
        )
        cardsEmbed.set_image(url="attachment://policydeck.png")
        await president.send(file=file_embed, embed=cardsEmbed)
        return cardsInPlay

    async def chancellorTurn(self, chancellor: Player, discarded: Policy) -> list():
        self.__policyPile.discardPolicy(discarded)
        cardsInPlay = self.__policyPile.peekCardsInPlay()
        file_embed = discord.File(
            images["chancellordeck.png"][cardsInPlay.count(Policy.Fascist)],
            filename="policydeck.png",
        )
        cardsEmbed = discord.Embed(
            title=f"\t **Pick** one Policy",
            description="Type *sh!p <color/name>* of the card that you wish to enact from the 2 given below: ",
            colour=colours["GOLD"],
        )
        cardsEmbed.set_image(url="attachment://policydeck.png")
        await chancellor.send(file=file_embed, embed=cardsEmbed)
        return cardsInPlay

    async def executeTop3(self, president: Player):
        top3 = self.__policyPile.peekTop3()
        file_embed = discord.File(
            images["presidentdeck.png"][top3.count(Policy.Fascist)],
            filename="policydeck.png",
        )
        cardsEmbed = discord.Embed(
            title="\t Next cards in the draw pile", colour=colours["DARK_AQUA"],
        )
        cardsEmbed.set_image(url="attachment://policydeck.png")
        await president.send(file=file_embed, embed=cardsEmbed)

    async def failedElectionReset(self, channel) -> tuple():
        top = self.__policyPile.placeTopPolicy()
        self.__placePolicy(top)
        await channel.send(
            f"A {top.name} policy has been picked from the draw pile and has been placed"
        )
        self.__failedElection = 0
        return self.__fascistPolicies, self.__liberalPolicies

    def __votingComplete(self) -> bool:
        return self.__playerCount == self.__ballotBox.getTotalVoteCount()

    def __getImage(self) -> str:
        baseImg = Image.open(self.__base)
        dot = Image.open(images["dot.png"])
        new = baseImg.copy()
        new.paste(dot, coordinates["failedElection"][self.__failedElection], dot)
        new.save(images["currentboard.png"], "PNG")
        return images["currentboard.png"]

    def __placePolicy(self, card: Policy) -> Power:
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
        new.save(images["newbase.png"], "PNG")
        self.__base = images["newbase.png"]
        return power

    async def __checkBoardState(self, channel: channel, userName: str, stateName: str):
        if self.__state != BoardState[stateName]:
            await channel.send(f"Sorry {userName}, the board is not {stateName}")
            return False
        return True
