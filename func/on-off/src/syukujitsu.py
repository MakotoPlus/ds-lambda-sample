import os
import datetime
import urllib.request
import logging

logger = logging.getLogger(__name__)

URL_SYUKUJITSU_CSV = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
HOLIDAY_NAME = 'name'
HOLIDAY_DATE = 'date'

class Shukujitsu():
  '''
  祝日CSVデータを取得しそのデータを利用して、平日判定を行うクラス。
  
  '''
  def __init__(self):
    self.__shukujitsu_list = self.__get_shukujitsu_data()

  def is_shukujitsu(self, check_date) -> bool:
    '''
    祝日の場合 True
    '''
    holiday = [x for x in self.__shukujitsu_list if x[HOLIDAY_DATE] == check_date]
    if len(holiday) <= 0:
      return False
    holiday = holiday[0]
    logger.info(f"本日は、祝日：{holiday[HOLIDAY_NAME]}です({check_date.strftime('%Y/%m/%d')})")
    return True
  
  def is_normal_date(self, check_date):
    '''
    平日(土、日、祝日以外)の場合 True
    '''
    weekday = check_date.weekday()
    if (weekday == 5 ) or (weekday == 6):
      logger.info(f"本日は、土,日です({check_date.strftime('%Y/%m/%d')})")
      return False
    ret = self.is_shukujitsu(check_date=check_date)
    return not ret
    
  
  def get_shukujitsu(self, check_date):
    '''
    祝日情報を返すが、祝日でない場合はNoneを返す    
    '''
    value = [x for x in self.__shukujitsu_list if x[HOLIDAY_DATE] == check_date]
    holiday = value[0] if len(value) > 0 else None
    if holiday is None:
      return None
    logger.info(f"本日は、祝日：{holiday[HOLIDAY_NAME]}です({check_date.strftime('%Y/%m/%d')})")
    return holiday
  
  def __get_shukujitsu_data(self):
    try:
      req = urllib.request.Request(URL_SYUKUJITSU_CSV)
      with urllib.request.urlopen(req) as res:
        #
        # Binaly -> SJIS変換
        binayBuffer = res.read()
        holiday_data = binayBuffer.decode('Shift_JIS')
        holiday_lines = holiday_data.split('\r\n')
        # 1行目はヘッダーなので除去
        holiday_lines = holiday_lines[1:]
        holiday_bulk = []
        for line in holiday_lines:
          if not line:
              break
          [shukujitsu_str, shukujitsu_name] = line.split(',')
          [year, month, day] = shukujitsu_str.split('/')
          shukujitsu_value = datetime.date(int(year), int(month), int(day))
          holiday_bulk.append({
            HOLIDAY_NAME: shukujitsu_name,
            HOLIDAY_DATE: shukujitsu_value
          })
      return holiday_bulk  
    except Exception as e:
      logger.warning(e)
      return []
