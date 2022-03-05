import gspread
import datetime

gc = gspread.service_account(filename='key.json')
doc = gc.open('test')
worksheet = doc.worksheet("시트1")


cell = worksheet.find("윤우상")

def check_sheet(user, date, limit_hour, limit_min):
    current_time = datetime.datetime.now()
    col = worksheet.find(user).col
    row = worksheet.find(date).row

    if (limit_hour >= current_time.hour) and (limit_min >= current_time.minute):
        worksheet.update_cell(row, col, "O")
    else:
        worksheet.update_cell(row, col, "X")
