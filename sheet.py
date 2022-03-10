from dotenv import load_dotenv
from utility import get_date
import gspread, os


load_dotenv()

DOCUMENT = os.getenv('DOCUMENT')
SHEET = os.getenv('SHEET')

gc = gspread.service_account(filename='key.json')
doc = gc.open(DOCUMENT)
worksheet = doc.worksheet(SHEET)
week = ["월", "화", "수", "목", "금", "토", "일"]


def check_sheet(user, limit_hour, limit_min, plan=False, fail=False):
    month, day, weekday, hour, min = get_date()

    if weekday in [5, 6]:
        return

    col = worksheet.find(user).col
    row = worksheet.find(f"{month}.{day}({week[weekday]})").row
    row = row + 1 if plan else row

    if fail == False or ((limit_hour > hour) and (limit_min > min)):
        worksheet.update_cell(row, col, "O")
    else:
        worksheet.update_cell(row, col, "X")

