from constants.constants import *
from utility.utility import *
from typing import List

from discord.ext import tasks
import discord


def send_msg_generator(success_members:List[str], extra_msg:str) -> str:
    """인증 못한 분들을 태그한 텍스트 생성 함수"""
    send_msg = " ".join([f"{member.mention}" for member in MEMBERS if member not in success_members])
    send_msg += extra_msg
    return send_msg


async def alarm(channel:object, success_members:List[str], msg:str) -> None:
    """인증 못한 사람들 알려주는 메시지 보내기 함수 """
    if len(MEMBERS) != len(success_members):
        send_msg = send_msg_generator(success_members, msg)
        await channel.send(send_msg)


async def time_out(channel:object, success_members:List[str], plan:bool=False) -> None:
    month, day, _, _, _ = get_date()
    fail_members = list(filter(lambda member: member not in success_members, MEMBERS))

    for fail_member in fail_members:
        col, row = get_cell_location(fail_member.name, plan)
        WORKSHEET.update_cell(row, col, "X")
    await channel.send(f"---------{month}월{day}일 {len(success_members)}/{len(MEMBER_NAMES)} 완료---------")
    success_members.clear()


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)

    @tasks.loop(minutes=1)
    async def every_notice():
        _, _, weekday, _, _ = get_date()
        if weekday in [5, 6]: return

        wake_up_channel = client.get_guild(GUILD_ID).get_channel(WAKE_UP_CHANNEL_ID)
        daily_channel = client.get_guild(GUILD_ID).get_channel(DAILY_CHANNEL_ID)

        if compare_time(*MORNING_ALARM):
            print("기상 알람")
            await alarm(wake_up_channel, WAKE_UP_MEMBERS, "일어나세요!!🙈")
        elif compare_time(*PLAN_ALARM):
            print("일일 계획 알람")
            await alarm(daily_channel, DAILY_PLAN_MEMBERS, "일일계획 작성 부탁드립니다 🖍")
        elif compare_time(*MORNING_TIME_LIMIT):
            print("기상 미션 체크")
            await time_out(wake_up_channel, WAKE_UP_MEMBERS)
        elif compare_time(*PLAN_TIME_LIMIT):
            print("일일 계획 체크")
            await time_out(daily_channel, DAILY_PLAN_MEMBERS, True)


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

        every_notice.start()


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
            await message.channel.send("일일계획 확인되었습니다. 📚")

        elif message.content.startswith('!기상'):
            col, row = get_cell_location(message.author.name)
            limit_hour, limit_min = MORNING_TIME_LIMIT

            if limit_hour > hour or (limit_hour == hour and limit_min >= min):
                # 제한 시간안에 인증한 경우
                WAKE_UP_MEMBERS.add(message.author)
                WORKSHEET.update_cell(row, col, "O")
                msg = "기상 확인되었습니다. 오늘도 화이텡! 💪"
            else:
                # 제한 시간 지난 경우
                WORKSHEET.update_cell(row, col, "X")
                msg = "내일은 꼭!! 😭"

            await message.channel.send(msg)

        elif message.content.startswith("!휴식"):
            col, row = get_cell_location(message.author.name)
            WORKSHEET.update_cell(row+2, col, "-")
            WORKSHEET.update_cell(row+3, col, "-")
            DAILY_PLAN_MEMBERS.add(message.author)
            WAKE_UP_MEMBERS.add(message.author)
            await message.channel.send("🔋")


    client.run(TOKEN)
