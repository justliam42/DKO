import discord
import os
import fightlib
from fightlib import Match, mention_to_id, User
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client(intents=discord.Intents.all())

global fight


@client.event
async def on_ready():
    global fight
    print(f"{client.user.name} is now running on discord.py version {discord.__version__}")
    fight = Match(client, User(client.user), User(client.user))
    fight.done = True


@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    content = message.content.lower()
    arg = None
    global fight
    if " " in message.content:
        arg = message.content.split()[1]
    if content.startswith('fight') and arg is not None and mention_to_id(arg) is not None:
        if fight.done:
            player_id = mention_to_id(arg)
            player2 = client.get_user(player_id)
            if player2 is not None and player2.id != message.author.id:
                player1 = User(message.author)  # here is where you can add saved player data content
                player2 = User(player2)

                fight = Match(client, player1, player2)
                await fight.begin(message.channel)
                while not fight.done:
                    pass

        else:
            await message.channel.send("there is a fight going on rn")


@client.event
async def on_reaction_add(reaction, user):
    if user == client.user or user.bot:
        return
    global fight
    await fight.react(reaction, user)


@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user or user.bot:
        return
    global fight
    await fight.react(reaction, user)


client.run(TOKEN)
