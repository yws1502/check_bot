from dotenv import load_dotenv
from utility import check_time
from sheet import check_sheet
from timeVariable import MORNING_ALARM, MORNING_TIME_LIMIT, PLAN_ALARM, PLAN_TIME_LIMIT
import os

from discord.ext import tasks
import discord


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = int(os.getenv('GUILD_ID'))
WAKE_UP_CHANNEL_ID = int(os.getenv('WAKE_UP_CHANNEL_ID'))
DAILY_CHANNEL_ID = int(os.getenv('DAILY_CHANNEL_ID'))

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

WAKE_UP_MEMBERS = []
DAILY_PLAN_MEMBERS = []
MEMBERS = []

def send_msg_generator(group_mode, extra_msg):
    send_msg = " ".join([f"{member.mention}" for member in MEMBERS if member not in group_mode])
    send_msg += extra_msg
    return send_msg


def time_out(group_mode, limit_time, plan=False):
    fail_members = list(filter(lambda member: member not in group_mode, MEMBERS))
    for fail_member in fail_members:
        check_sheet(fail_member.name, *limit_time, plan)


@tasks.loop(minutes=1)
async def every_hour_notice():
    wake_up_channel = client.get_guild(GUILD_ID).get_channel(WAKE_UP_CHANNEL_ID)
    daily_channel = client.get_guild(GUILD_ID).get_channel(DAILY_CHANNEL_ID)
    # 기상 미션
    if check_time(*MORNING_ALARM) and len(MEMBERS) != len(WAKE_UP_MEMBERS):
        msg = send_msg_generator(WAKE_UP_MEMBERS, "일어나세요")
        await wake_up_channel.send(msg)
    elif check_time(*MORNING_TIME_LIMIT) and len(MEMBERS) != len(WAKE_UP_MEMBERS):
        time_out(WAKE_UP_MEMBERS, MORNING_TIME_LIMIT, True)
        WAKE_UP_MEMBERS.clear()

    # 일일 계획
    elif check_time(*PLAN_ALARM) and len(MEMBERS) != len(DAILY_PLAN_MEMBERS):
        msg = send_msg_generator(DAILY_PLAN_MEMBERS, "일일계획 작성 부탁드립니다 : )")
        await daily_channel.send(msg)
    elif check_time(*PLAN_TIME_LIMIT) and len(MEMBERS) != len(DAILY_PLAN_MEMBERS):
        time_out(DAILY_PLAN_MEMBERS, PLAN_TIME_LIMIT)
        DAILY_PLAN_MEMBERS.clear()


@client.event
async def on_ready():
    global MEMBERS
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
    if message.author == client.user:
        return
    elif message.content.startswith('기상'):
        WAKE_UP_MEMBERS.append(message.author)
        check_sheet(message.author.name, *MORNING_TIME_LIMIT)
        print(WAKE_UP_MEMBERS)
    elif message.content.startswith("일일"):
        DAILY_PLAN_MEMBERS.append(message.author)
        check_sheet(message.author.name, *PLAN_TIME_LIMIT, plan=True)
        print(DAILY_PLAN_MEMBERS)


client.run(TOKEN)
