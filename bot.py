from utility import compare_time
from sheet import check_sheet
from dotenv import load_dotenv
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

MORNING_ALARM = [0, 10]
MORNING_TIME_LIMIT = [0, 21]

PLAN_ALARM = [2, 50]
PLAN_TIME_LIMIT = [3, 1]

WAKE_UP_MEMBERS = []
DAILY_PLAN_MEMBERS = []
MEMBERS = []

def send_msg_generator(success_members, extra_msg):
    send_msg = " ".join([f"{member.mention}" for member in MEMBERS if member not in success_members])
    send_msg += extra_msg
    return send_msg


async def check_member(channel, success_members, alarm, time_limit, msg):
    if len(MEMBERS) != len(success_members):
        if compare_time(*alarm):
            print('alarm')
            send_msg = send_msg_generator(success_members, msg)
            await channel.send(send_msg)

        elif compare_time(*time_limit):
            print('time out')
            fail_members = list(filter(lambda member: member not in success_members, MEMBERS))
            for fail_member in fail_members:
                is_plan = True if time_limit == PLAN_TIME_LIMIT else False
                check_sheet(fail_member.name, *time_limit, plan=is_plan, fail=True)
            success_members.clear()


@tasks.loop(minutes=1)
async def every_hour_notice():
    wake_up_channel = client.get_guild(GUILD_ID).get_channel(WAKE_UP_CHANNEL_ID)
    daily_channel = client.get_guild(GUILD_ID).get_channel(DAILY_CHANNEL_ID)
    
    await check_member(wake_up_channel, WAKE_UP_MEMBERS, MORNING_ALARM, MORNING_TIME_LIMIT, "일어나세요")
    await check_member(daily_channel, DAILY_PLAN_MEMBERS, PLAN_ALARM, PLAN_TIME_LIMIT, "일일계획 작성 부탁드립니다 : )")


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
    elif message.content.startswith('!기상'):
        WAKE_UP_MEMBERS.append(message.author)
        check_sheet(message.author.name, *MORNING_TIME_LIMIT)
        print("기상 멤버 :", WAKE_UP_MEMBERS)
    elif message.content.startswith("!일일"):
        DAILY_PLAN_MEMBERS.append(message.author)
        check_sheet(message.author.name, *PLAN_TIME_LIMIT, plan=True)
        print("계획 짠 멤버 :", DAILY_PLAN_MEMBERS)


client.run(TOKEN)
