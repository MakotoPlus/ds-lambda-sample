import datetime
import urllib.request

URL_SYUKUJITSU_CSV = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
HOLIDAY_NAME = 'name'
HOLIDAY_DATE = 'date'

class Shukujitsu():
  '''
  祝日CSVデータを取得しそのデータを利用して、祝日判定を行うクラス
  '''
  def __init__(self):
    self.__shukujitsu_list = self.__get_shukujitsu_data()

  def is_shukujitsu(self, check_date) -> bool:
    check = [x for x in self.__shukujitsu_list if x[HOLIDAY_DATE] == check_date]
    return True if len(check) > 0 else False
  
  def get_shukujitsu(self, check_date):
    value = [x for x in self.__shukujitsu_list if x[HOLIDAY_DATE] == check_date]
    return value[0] if len(value) > 0 else None
  
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
          #print(f'[{line}]')
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
      print(e)
      return []
