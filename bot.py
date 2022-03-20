from constants.constants import *
from utility.utility import *

from discord.ext import tasks
import discord


def check_sheet(username, limit_hour, limit_min, plan=False, fail=False):
    _, _, weekday, hour, min = get_date()

    if weekday in [5, 6]:
        return

    col, row = get_cell_location(username, plan)


    if type(WORKSHEET.cell(row, col).value) == type(None):
        if fail:
            WORKSHEET.update_cell(row, col, "X")
        elif plan or (limit_hour > hour) or ((limit_hour >= hour) and (limit_min >= min)):
            WORKSHEET.update_cell(row, col, "O")
        else:
            WORKSHEET.update_cell(row, col, "X")
    elif type(WORKSHEET.cell(row, col).value) == type("string") and plan:
        if fail: return
        if weekday < 4:
            row += 2
        elif weekday == 6:
            row += 3
        WORKSHEET.update_cell(row, col, "O")

def send_msg_generator(group_mode, extra_msg):
    send_msg = " ".join([f"{member.mention}" for member in MEMBERS if member not in group_mode])
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


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)

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

        if message.content.startswith('!기상'):
            WAKE_UP_MEMBERS.add(message.author)
            check_sheet(message.author.name, *MORNING_TIME_LIMIT)
            await message.channel.send("기상 확인되었습니다. 오늘도 화이텡! : )")
            print("기상 멤버 :", WAKE_UP_MEMBERS)
        elif message.content.startswith("!일일") or\
            message.content.endswith("계획"):
            DAILY_PLAN_MEMBERS.add(message.author)
            check_sheet(message.author.name, *PLAN_TIME_LIMIT, plan=True)
            await message.channel.send("일일계획 확인되었습니다. 화이텡! : )")
            print("계획 짠 멤버 :", DAILY_PLAN_MEMBERS)

    client.run(TOKEN)
