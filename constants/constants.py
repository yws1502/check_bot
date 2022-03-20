from dotenv import load_dotenv
import gspread
import os

load_dotenv()

# discord 봇 관련
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = int(os.getenv('GUILD_ID'))
WAKE_UP_CHANNEL_ID = int(os.getenv('WAKE_UP_CHANNEL_ID'))
DAILY_CHANNEL_ID = int(os.getenv('DAILY_CHANNEL_ID'))


# 시간 변수
MORNING_ALARM = [0, 10]
MORNING_TIME_LIMIT = [0, 21]

PLAN_ALARM = [2, 50]
PLAN_TIME_LIMIT = [3, 1]


# 출석 확인 DB
WAKE_UP_MEMBERS = set()
DAILY_PLAN_MEMBERS = set()
MEMBERS = []


# google sheet 관련
document = "test2"
sheet = "Sheet1"
gc = gspread.service_account(filename='key.json')
doc = gc.open(document)

WORKSHEET = doc.worksheet(sheet)
WEEK = ["월", "화", "수", "목", "금", "토", "일"]
MEMBER_NAMES = {
"강혜진": "강혜진",
"영진쓰": "고영진",
"kykim": "김기영",
"Danim Kim": "김다님",
"김창현": "김창현",
"누리": "박누리",
"페둘찌윤🕊": "박지윤",
"parfume": "신현수",
"여운화": "여운화",
"윤우상": "윤우상",
"choar": "조아라",
"1. 홍예림": "홍예림",
"2. 홍제섭": "홍제섭"
}
