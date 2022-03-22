from constants.constants import *
from utility.utility import *
from typing import List

from discord.ext import tasks
import discord


def send_msg_generator(fail_members:List[str], extra_msg:str) -> str:
    """인증 못한 분들을 태그한 텍스트 생성 함수"""
    send_msg = " ".join([f"{member.mention}" for member in fail_members])
    send_msg += extra_msg
    return send_msg


async def alarm(channel:object, fail_members:List[str], msg:str) -> None:
    """인증 못한 사람들 알려주는 메시지 보내기 함수 """
    if len(fail_members) != 0:
        send_msg = send_msg_generator(fail_members, msg)
        await channel.send(send_msg)


async def time_out(channel:object, fail_members:List[str], plan:bool=False) -> None:
    month, day, _, _, _ = get_date()

    success_count = len(MEMBERS) - len(fail_members)
    for fail_member in fail_members:
        col, row, success = get_cell_location(fail_member.name, plan)
        if success == False:  return
        WORKSHEET.update_cell(row, col, "X")
    await channel.send(f"---------{month}월{day}일 {success_count}/{len(MEMBER_NAMES)} 완료---------")


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
            fail_members = await get_fail_members(MEMBERS, wake_up_channel)
            await alarm(wake_up_channel, fail_members, "일어나세요!!🙈")
        elif compare_time(*PLAN_ALARM):
            print("일일 계획 알람")
            fail_members = await get_fail_members(MEMBERS, daily_channel, True)
            await alarm(daily_channel, fail_members, "일일계획 작성 부탁드립니다 ✏")
        elif compare_time(*MORNING_TIME_LIMIT):
            print("기상 미션 체크")
            fail_members = await get_fail_members(MEMBERS, wake_up_channel)
            await time_out(wake_up_channel, fail_members)
        elif compare_time(*PLAN_TIME_LIMIT):
            print("일일 계획 체크")
            fail_members = await get_fail_members(MEMBERS, daily_channel, True)
            await time_out(daily_channel, fail_members, True)


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
            col, row, success = get_cell_location(message.author.name, True)
            if success == False:
                await message.channel.send("이름이 변경되어 체크할 위치를 찾을 수 없습니다 😭")
                return
            if (12 == hour and 11 < min) or (12 < hour < 17):
                return
            elif weekday == 6 or has_value_at_cell(col, row) == True:
                # 내일 계획 미리 세우는 경우 or 일요일날 계획 세운 경우
                row += 2

            WORKSHEET.update_cell(row, col, "O")
            await message.channel.send("일일계획 확인되었습니다. 📚")

        elif message.content.startswith('!기상'):
            col, row, success = get_cell_location(message.author.name)
            if success == False:
                await message.channel.send("이름이 변경되어 체크할 위치를 찾을 수 없습니다 😭")
                return
            limit_hour, limit_min = MORNING_TIME_LIMIT

            if limit_hour > hour or (limit_hour == hour and limit_min >= min):
                # 제한 시간안에 인증한 경우
                WORKSHEET.update_cell(row, col, "O")
                msg = "기상 확인되었습니다. 오늘도 화이텡! 💪"
            else:
                # 제한 시간 지난 경우
                WORKSHEET.update_cell(row, col, "X")
                location = f"{chr(col+64)}{row}"
                format = {
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red":1, "green": 0.4274, "blue": 0.0039}
                    }
                }
                WORKSHEET.format(location, format)
                msg = "내일은 꼭!! 😭"

            await message.channel.send(msg)

        elif message.content.startswith("!휴식"):
            col, row, success = get_cell_location(message.author.name)
            if success == False:
                await message.channel.send("이름이 변경되어 체크할 위치를 찾을 수 없습니다 😭")
                return
            location_wake = f"{chr(col+64)}{row+2}"
            location_plan = f"{chr(col+64)}{row+3}"

            format = {
                "backgroundColor": {"red":0.8509, "green":0.8509, "blue":0.8509}
            }
            WORKSHEET.update(location_wake, "-")
            WORKSHEET.update(location_plan, "-")
            WORKSHEET.format(location_wake, format)
            WORKSHEET.format(location_plan, format)

            await message.channel.send("🔋")


    client.run(TOKEN)
