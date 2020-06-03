import discord
from discord.ext.commands import Context


from game_state import State
from game_board import Board, Power
from players_manager import Players


class Game:
    def __init__(self, channel: discord.channel, user: discord.User):
        self.__channel = channel
        self.__owner = user
        self.__state = None
        self.__board = Board()
        self.__players = Players()
        self.__currentPower = None
        self.__dangerZone = False

    def __electionDone(self):
        self.__board.clearEdit()
        flag = self.__board.electionResult(self.__channel, self.__players)
        if flag is None:
            self.__players.freezePrevious()
            if self.__dangerZone and await self.__checkWin():
                self.__state = State.GameOver
            else:
                self.__state = State.Legislation
                await self.__board.showBoard(
                    self.__channel, self.__state, self.__players, self.__currentPower
                )
                await self.__board.policyPile.presidentTurn(
                    self.__channel, self.__players.president
                )
        else:
            if flag:
                (
                    fascistCardCount,
                    liberalCardCount,
                ) = await self.__board.placeRandomPolicy(self.__channel)
                if await self.__checkWin(fascistCardCount, liberalCardCount):
                    self.__state = State.GameOver
                    return
                elif fascistCardCount > 3:
                    self.__dangerZone = True
            self.__state = State.Nomination
            self.__players.nextPresident()
            await self.__board.showBoard(
                self.__channel, self.__state, self.__players, self.__currentPower
            )

    async def launch(self):
        self.__state = State.launch(self.__state)
        await self.__board.openBoard(self.__channel, self.__owner)

    async def join(self, user: discord.User) -> bool:
        if await self.__state.check(
            State.Inactive, self.__channel, user
        ) and await self.__players.addPlayer(self.__channel, user):
            await self.__board.joinBoard(
                self.__channel, user.name, self.__players.count
            )
            return True
        return False

    async def begin(self, user: discord.User):
        if await self.__players.beginGame(
            self.__channel, user
        ) and await self.__board.beginBoard(self.__channel):
            self.__state = State.Nomination
            self.__players.generateRoles()
            self.__board.setType(self.__players.count)
            await self.__board.showBoard(
                self.__channel, self.__state, self.__players, self.__currentPower
            )

    async def pick(self, ctx: Context, arg: str):
        if self.__state == State.Election:
            await ctx.send(
                f"Sorry {ctx.author.name}, thats an invalid command at the moment"
            )
            return
        elif self.__state == State.Nomination and await self.__players.pickChancellor(
            ctx, arg
        ):
            self.__state = State.Election
            self.__board.clearEdit()
        elif self.__state == State.Legislation:
            flag = await self.__board.pickPolicy(
                self.__channel, ctx, arg, self.__players
            )
            if flag == True:
                if self.__currentPower == Power.killVeto:
                    self.__currentPower = None
            elif flag == False:
                return
            else:
                self.__board.clearEdit()
                fascistCardCount, liberalCardCount = self.__board.getCardCount()
                if await self.__checkWin(fascistCardCount, liberalCardCount):
                    self.__state = State.GameOver
                    return
                else:
                    if fascistCardCount > 3:
                        self.__dangerZone = True
                    if flag:
                        self.__currentPower = flag
                        self.__state = State.Execution
                    else:
                        self.__players.nextPresident()
                        self.__state = State.Nomination
        elif self.__state == State.Execution:
            if ctx.author.id != self.__players.president.id:
                await ctx.send(
                    f"Sorry {ctx.author.name}, only the President can execute Presidential Powers"
                )
                return
            elif (
                arg[:3] != "<@!"
                or not self.__players.checkPlayerID(int(arg[3:-1]))
                or arg[3:-1] == self.__players.president.id
            ):
                await ctx.send(
                    f"Sorry {ctx.author.name}, that's an invalid selection, please retry!"
                )
                return
            else:
                candidateID = arg[3:-1]
                if self.__currentPower in (Power.kill, Power.killVeto):
                    await self.__players.assassinate(self.__channel, candidateID)
                    self.__players.nextPresident()
                elif self.__currentPower == Power.getParty:
                    await self.__players.inspect(self.__channel, candidateID)
                    self.__players.nextPresident()
                elif self.__currentPower == Power.nextPresident:
                    self.__players.chooseSuccessor(self.__channel, candidateID)
                else:
                    raise Exception("Unkown Power")
                self.__board.clearEdit()
                self.__state = State.Nomination
                if self.__currentPower != Power.killVeto:
                    self.__currentPower = None
        else:
            return
        await self.__board.showBoard(
            self.__channel, self.__state, self.__players, self.__currentPower
        )

    async def vote(self, ctx: Context, arg: str):
        if await self.__state.check(
            State.Election, ctx.channel, ctx.author
        ) and await self.__players.markVote(ctx, arg):
            await self.__board.showBoard(
                self.__channel, self.__state, self.__players, self.__currentPower
            )
            if self.__players.votingComplete():
                self.__electionDone()

    async def see(self, ctx: Context):
        if (
            self.__state != State.Execution
            or self.__currentPower != Power.peekTop3
            or self.__players.president.id != ctx.author.id
        ):
            await ctx.send(
                f"Sorry {ctx.author.name}, this seems to be an invalid command"
            )
        else:
            await self.__board.policyPile.executeTop3(self.__players.president)
            self.__currentPower = None
            self.__board.clearEdit()
            self.__players.nextPresident()
            self.__state = State.Nomination
            await self.__channel.send(
                f"President {ctx.author.name} has peeked the next set of Policies"
            )
            await self.__board.showBoard(
                self.__channel, self.__state, self.__players, self.__currentPower
            )

    async def veto(self, ctx: Context):
        if (
            self.__currentPower != Power.killVeto
            or self.__players.president.id != ctx.author.id
            or self.__state != State.Legislation
        ):
            await self.__channel.send(
                f"Sorry {ctx.author.name}, you don't have the power to veto right now!"
            )
        else:
            self.__currentPower = None
            self.__board.clearEdit()
            self.__players.nextPresident()
            self.__state = State.Nomination
            await self.__board.showBoard(
                self.__channel, self.__state, self.__players, self.__currentPower
            )

    async def __checkWin(self, fascistCardCount=0, liberalCardCount=0):
        if (
            not (fascistCardCount or liberalCardCount)
            and self.__dangerZone
            and self.__players.hitler.id == self.__players.chancellor.id
        ):
            await self.__channel.send("Facists win! Hitler has been made Chancellor")
            return True
        elif fascistCardCount == 6:
            await self.__channel.send(
                "Facists win! 6 Fascist policies have been passed"
            )
            return True
        elif liberalCardCount == 5:
            await self.__channel.send(
                "Liberals win! 5 Liberal policies have been passed"
            )
            return True
        else:
            for player in self.__players.getPlayers():
                if player.id == self.__players.hitler.id and player.isDead:
                    await self.__channel.send(
                        "Liberals win! Hitler has been assassinated"
                    )
                    return True
        return False
