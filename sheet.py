from utility import get_date
import gspread

gc = gspread.service_account(filename='key.json')
doc = gc.open('test')
worksheet = doc.worksheet("시트1")
week = ["월", "화", "수", "목", "금", "토", "일"]


def check_sheet(user, limit_hour, limit_min, plan=False):
    month, day, weekday, hour, min = get_date()

    col = worksheet.find(user).col
    row = worksheet.find(f"{month}.{day}({week[weekday]})").row
    row = row if plan == False else row - 1

    if (limit_hour >= hour) and (limit_min >= min):
        worksheet.update_cell(row, col, "O")
    else:
        worksheet.update_cell(row, col, "X")

# check_sheet("윤우상", 12, 20)