from dotenv import load_dotenv
from utility import check_time
import time, os

from discord.ext import tasks
import discord


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

WAKE_UP = []
MEMBERS = []

@tasks.loop(seconds=1)
async def every_hour_notice():
    current_channel = client.get_guild(GUILD_ID).get_channel(CHANNEL_ID)
    # 주말인 경우는 제외
    if check_time(9, 15) and len(MEMBERS) != len(WAKE_UP):
        wake_up_info = ""
        for member in MEMBERS:
            if member not in WAKE_UP:
                wake_up_info += f"{member.mention}"
        wake_up_info += "일어나세요"
        await current_channel.send(wake_up_info)
    elif check_time(9, 20) and len(MEMBERS) != len(WAKE_UP):
        # 구글 스프레드에 체크하는 로직
        pass
    time.sleep(1)

@client.event
async def on_ready():
    global MEMBERS, WAKE_UP
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} 봇 연결\n'
        f'{guild.name}(id: {guild.id})\n'
    )
    MEMBERS = [member for member in guild.members if member != client.user]

    print("멤버들")
    for member in MEMBERS:
        print(f'- {member.name}')

    every_hour_notice.start()


@client.event
async def on_message(message):
    global WAKE_UP, MEMBERS
    if message.author == client.user:
        return
    elif message.content.startswith('기상'):
        WAKE_UP.append(message.author)

    await message.channel.send("잘했어")


client.run(TOKEN)

