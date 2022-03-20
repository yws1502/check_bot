from constants.constants import *
from typing import List
import datetime

def compare_time(compare_hour:int, compare_min:int) -> bool:
    """
    파라미터의 값과 함수가 실행된 시점의 시간, 분을 비교하여 True 혹은 False 반환
    """
    current_time = datetime.datetime.now()
    if compare_hour != current_time.hour or compare_min != current_time.minute:
        return False
    return True

def get_date() -> List[int]:
    """함수가 실행된 시점의 [월, 일, 요일, 시간, 분] 반환"""
    current_time = datetime.datetime.now()
    weekday = current_time.weekday()
    month = f"{current_time.month}".zfill(2)
    day = f"{current_time.day}".zfill(2)
    hour = current_time.hour
    min = current_time.minute

    return [month, day, weekday, hour, min]

def get_cell_location(username:str, plan:bool=False) -> List[int]:
    """
    구글 시트에서 좌표 찾아주는 함수
    return col, row
    """
    month, day, weekday, _, _ = get_date()

    col = WORKSHEET.find(MEMBER_NAMES[username]).col
    row = WORKSHEET.find(f"{month}.{day}({WEEK[weekday]})").row
    row += 1 if plan == True else 0

    return col, row

def has_value_at_cell(col:int, row:int) -> bool:
    """
    해당 행에 값이 있는지 확인

    셀에 값이 있는 경우 True
    셀에 값이 없는 경우 False
    """
    if type(WORKSHEET.cell(row, col).value) == type(None):
        return False
    return True