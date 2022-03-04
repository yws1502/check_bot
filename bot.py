from dotenv import load_dotenv
import datetime
import time
import os

from discord.ext import tasks
import discord
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = 946446779619086376
CHANNEL_ID = 946446779619086379

wake_up_check = []

client = discord.Client()

@tasks.loop(seconds=1)
async def every_hour_notice():
    current_time = datetime.datetime.now()
    current_channel = client.get_guild(GUILD_ID).get_channel(CHANNEL_ID)
    # 주말인 경우는 제외
    if current_time.weekday() == 0 and current_time.hour == 11 and current_time.minute == 50:
        await current_channel.send("@윤우상 주간 계획 작성해주세요!")

    elif current_time.weekday() not in [4, 6]:
        if current_time.hour == 2 and current_time.minute == 7:
            await current_channel.send("@윤우상 일어나 코딩해야지")
        elif current_time.hour == 11 and current_time.minute == 50:
            await current_channel.send("@윤우상 일일 계획 작성해주세요!")

    time.sleep(1)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

    every_hour_notice.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith('기상'):
        wake_up_check.append(message.author.name)
        print(wake_up_check)
        await message.channel.send(f"{message.author.mention} 일어나세요")


client.run(TOKEN)

