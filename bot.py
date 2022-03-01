import os
import discord

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print('{} 연결'.format(client.user))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith('ping'):
        await message.channel.send('pong')


client.run(TOKEN)



