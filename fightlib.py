import asyncio
import discord
import random
import math


def mention_to_id(mention):
    if mention.startswith('<@!') and mention.endswith('>'):
        id = mention.replace('<@!', '')
        id = id.replace('>', '')
        if id.isnumeric():

            return int(id)
        else:
            return None
    else:
        return None


class User:
    def __init__(self, discord_user: discord.User):
        self.user = discord_user
        if not discord_user.bot:
            self.name = discord_user.name
            self.id = discord_user.id
            self.display_name = discord_user.display_name
            self.money = 0
            self.max_health = 100
            self.player1emote = "🤸"
            self.player2emote = "🤺"


ring = "▪▪▪▪▪▪▪▪▪▪\n◼◼◼◼◼◼◼◼◼◼"
left = '⬅'
right = '➡'
attack_emote = '⚔'
defend_emote = '🛡'
refresh_rate = 1
accept = '✅'
decline = '❌'


class Fighter:
    def __init__(self, player: User, pos: int):
        self.user = player
        if not player.user.bot:
            self.health = player.max_health
            self.position = pos
            self.user = player.user
            self.name = player.user.name
            self.id = player.user.id
            self.display_name = player.display_name
            self.player1emote = player.player1emote
            self.player2emote = player.player2emote
            self.action = None
            self.action_name = "None"
            self.opponent = None
            self.parry = False


class Match:
    def __init__(self, client: discord.Client, player1: User, player2: User):
        self.player1 = Fighter(player1, 0)
        self.player2 = Fighter(player2, 9)
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1
        self.embed = None
        self.ring = ring
        self.client = client
        self.accepted = None
        self.done = False
        self.timeout = False

    async def update_ring(self):
        self.ring = ring[:self.player1.position] + self.player1.player1emote + ring[self.player1.position + 1:]
        self.ring = self.ring[:self.player2.position] + self.player2.player2emote + ring[self.player2.position + 1:]
        self.embed = discord.Embed(title=f'{self.player1.name} vs {self.player2.name}',
                                   description=self.ring,
                                   color=0
                                   )

    async def animate(self, message: discord.Message):
        while self.player1.health > 0 and self.player2.health > 0 and not self.done:
            await asyncio.sleep(refresh_rate)
            # do stuff here
            for player in [self.player1, self.player2]:
                player.action_name = player.action
                if player.action == 'left':
                    if player.position != 0 and player.position - 1 != player.opponent.position:
                        player.position -= 1

                if player.action == 'right':
                    if player.position != 9 and player.position + 1 != player.opponent.position:
                        player.position += 1

                if player.action == 'attack':
                    if abs(player.position - player.opponent.position) == 1:
                        if player.opponent.action == 'defend':
                            damage = random.randrange(0, 10)
                        else:
                            damage = random.randrange(12, 23)
                        if player.parry:
                            damage = damage * math.floor(2.2)
                            player.action_name = 'parry'  # -for the user to see the parry
                        player.opponent.health -= damage

                player.parry = False
                if player.action == 'defend':
                    if player.opponent.action == 'attack':
                        player.parry = True

            await self.update_ring()
            if self.player1.action is not None or self.player2.action is not None:
                await message.edit(
                    content=f'p1- ❤: {self.player1.health} action: {self.player1.action_name}\np2- ❤: {self.player2.health} action: {self.player2.action_name}',
                    embed=self.embed)
        if not self.timeout:
            if self.player1.health <= self.player2.health:
                winner = self.player2
            else:
                winner = self.player1
            await message.edit(
                content=f'p1- ❤: {self.player1.health} action: {self.player1.action}\np2- ❤: {self.player2.health} action: {self.player2.action}\n{winner.user.mention} Wins!',
                embed=self.embed)
            self.done = True

    async def react(self, reaction: discord.Reaction, user: discord.User):
        action = None
        if reaction.emoji == left:
            action = "left"
        elif reaction.emoji == right:
            action = "right"
        elif reaction.emoji == attack_emote:
            action = "attack"
        elif reaction.emoji == defend_emote:
            action = "defend"
        if user.id == self.player1.id:
            self.player1.action = action
        elif user.id == self.player2.id:
            self.player2.action = action

        if self.player2.id == user.id and reaction.emoji == accept:
            self.accepted = True
        elif self.player2.id == user.id and reaction.emoji == decline:
            self.accepted = False

    async def timer(self, time: int, message: discord.Message):
        await asyncio.sleep(time)
        self.timeout = True
        if not self.done:
            self.done = True
            await message.edit(content=f"y'all took too long",
                               embed=self.embed)

    async def begin(self, channel: discord.TextChannel):
        message = await channel.send(
            embed=discord.Embed(title=f'{self.player1.name} is challenging {self.player2.name}',
                                description=f'accept:{accept}\ndecline:{decline}',
                                color=discord.Color.red()
                                ))
        await message.add_reaction(accept)
        await message.add_reaction(decline)

        timeout = True
        for i in range(20):
            await asyncio.sleep(1)
            if self.accepted == True:
                timeout = False
                break
            elif self.accepted == False:
                await message.edit(
                    embed=discord.Embed(title=f'{self.player1.name} is challenging {self.player2.name}',
                                        description=f'{self.player2.name} declined',
                                        color=discord.Color.red()
                                        ))
                self.done = True
                return
        if timeout:
            await message.edit(
                embed=discord.Embed(title=f'{self.player1.name} is challenging {self.player2.name}',
                                    description=f"{self.player2.name} didn't respond in time",
                                    color=discord.Color.red()
                                    ))
            self.done = True
            return
        await message.clear_reactions()
        await self.update_ring()
        await message.edit(
            content=f'p1- ❤:{self.player1.health}\np2- ❤:{self.player2.health}', embed=self.embed)
        await message.add_reaction(left)
        await message.add_reaction(right)
        await message.add_reaction(attack_emote)
        await message.add_reaction(defend_emote)

        timer = asyncio.create_task(self.timer(35, message))
        animate = asyncio.create_task(self.animate(message))

        await timer
        await animate


if __name__ == "__main__":
    pass
