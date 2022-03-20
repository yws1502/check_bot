from constants.constants import *
from utility.utility import *
from typing import List

from discord.ext import tasks
import discord


def check_sheet(username:str, limit_hour:int, limit_min:int, plan:bool=False, fail:bool=False) -> None:
    """
    해당 유저가 제 시간에 인증을 했는지 확인하여 구글 시트에 check해주는 함수 
    """
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


def send_msg_generator(success_members:List[str], extra_msg:str) -> str:
    """인증 못한 분들을 태그한 텍스트 생성 함수"""
    send_msg = " ".join([f"{member.mention}" for member in MEMBERS if member not in success_members])
    send_msg += extra_msg
    return send_msg


async def check_member(channel:object, success_members:List[str], alarm:List[int], time_limit:List[int], msg:str) -> None:
    """인증 마감 시간에 인증 못한 분들 구글 시트에 체크하는 함수"""
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
        _, _, weekday, hour, min = get_date()
        if message.author == client.user or weekday == 5: return

        if message.content.startswith("!일일"):
            col, row = get_cell_location(message.author.name, True)
            if has_value_at_cell(col, row) == True:
                # 내일 계획 미리 세우는 경우
                row += 2
            elif weekday == 6:
                # 일요일날 계획 세운 경우
                row += 3

            DAILY_PLAN_MEMBERS.add(message.author)
            WORKSHEET.update_cell(row, col, "O")
            await message.channel.send("일일계획 확인되었습니다. 화이텡! : )")

        elif message.content.startswith('!기상'):
            col, row = get_cell_location(message.author.name)
            limit_hour, limit_min = MORNING_TIME_LIMIT

            if limit_hour > hour or (limit_hour == hour and limit_min >= min):
                # 제한 시간안에 인증한 경우
                WAKE_UP_MEMBERS.add(message.author)
                WORKSHEET.update_cell(row, col, "O")
                msg = "기상 확인되었습니다. 오늘도 화이텡! : )"
            else:
                # 제한 시간 지난 경우
                WORKSHEET.update_cell(row, col, "X")
                msg = "내일은 꼭!!"

            await message.channel.send(msg)

    client.run(TOKEN)
