import sys
import datetime
import urllib.request
import copy
import boto3

URL_SYUKUJITSU_CSV = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"

DICT_SWITCH_KEY = 'switch'
DICT_REGION_KEY = 'region'
DICT_DBINSTANCE_IDENTIFIER_KEY = 'DBInstanceIdentifier'
DICT_CHECK_DATE_YYYYMMDD = 'check_date_yyyymmdd'

SWITCH_ON = 'on'
SWITCH_OFF = 'off'

HOLIDAY_NAME = 'name'
HOLIDAY_DATE = 'date'

def handler(event, context):
  print('RDS 起動/停止Lambda Start')
  output_event(event)
  event = check_event_dict(event)
  db_instance(event)
  print('RDS 起動/停止Lambda 終了')
  return {'result': 'success'}

def db_instance(event):
  '''
  SWITCH_ONの場合は、平日以外の場合は何もしないで終了する
  '''
  if event[DICT_SWITCH_KEY] == SWITCH_ON:
    result = is_db_on(event[DICT_CHECK_DATE_YYYYMMDD])
    if False == result:
      return
  if event[DICT_SWITCH_KEY] == SWITCH_ON:
    db_start(event)
  else:
    db_stop(event)


def db_start(event):
  '''
  DB Instans Start
  '''
  rds = boto3.client('rds', region_name=event[DICT_REGION_KEY])
  for instance_name in event[DICT_DBINSTANCE_IDENTIFIER_KEY]:
    #
    # 起動前に状態確認して既に起動しているのなら何もしない
    ret = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
    if "available" == ret["DBInstances"][0]["DBInstanceStatus"]:
      print(f"RDS Instance 既に起動しています instance:[{instance_name}]")
    else:
      ret = rds.start_db_instance(DBInstanceIdentifier=instance_name)
      print(f'RDS Instance Start Success:[{instance_name}]')
      print(ret)
 
 
def db_stop(event): 
  '''
  DB Instans Stop
  '''
  rds = boto3.client('rds', region_name=event[DICT_REGION_KEY])
  for instance_name in event[DICT_DBINSTANCE_IDENTIFIER_KEY]:
    #
    # 起動前に状態確認して既に起動しているのなら何もしない
    ret = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
    if "stopped" == ret["DBInstances"][0]["DBInstanceStatus"]:
      print(f"RDS Instance 既に一時的に停止しています instance:[{instance_name}]")
    else:
      ret = rds.stop_db_instance(DBInstanceIdentifier=instance_name)
      print(f'RDS Instance Stop Success:[{instance_name}]')
      print(ret)


def check_event_dict(event) -> dict:
  result_dict = copy.deepcopy(event)
  if not (DICT_SWITCH_KEY in event ):
    raise Exception(f'event parameter key is not key:{DICT_SWITCH_KEY}')
  if not (DICT_REGION_KEY in event ):
    raise Exception(f'event parameter key is not key:{DICT_REGION_KEY}')
  if not (DICT_DBINSTANCE_IDENTIFIER_KEY in event ):
    raise Exception(f'event parameter key is not key:{DICT_DBINSTANCE_IDENTIFIER_KEY}')
  else:
    if type(result_dict[DICT_DBINSTANCE_IDENTIFIER_KEY]) is str:
      result_dict[DICT_DBINSTANCE_IDENTIFIER_KEY] = [result_dict[DICT_DBINSTANCE_IDENTIFIER_KEY]]
    elif type(event[DICT_DBINSTANCE_IDENTIFIER_KEY]) is not list:
      raise Exception(f'event parameter key is type error key:{DICT_DBINSTANCE_IDENTIFIER_KEY}')
  switch_value = result_dict[DICT_SWITCH_KEY]
  if SWITCH_ON != switch_value and SWITCH_OFF != switch_value:
    raise Exception(f'event parameter value error {switch_value}')

  # 日付設定
  check_date_yyyymmdd = datetime.date.today()
  if DICT_CHECK_DATE_YYYYMMDD in result_dict :
    s_check_date_yyyymmdd = result_dict[DICT_CHECK_DATE_YYYYMMDD]
    year = s_check_date_yyyymmdd[0:4]
    month = s_check_date_yyyymmdd[4:6]
    dd = s_check_date_yyyymmdd[6:8]
    print(f'{year}/{month}/{dd} {s_check_date_yyyymmdd}')
    check_date_yyyymmdd = datetime.date(int(year), int(month), int(dd))
  result_dict[DICT_CHECK_DATE_YYYYMMDD] = check_date_yyyymmdd
  return result_dict

def is_db_on(check_date) -> bool:
  weekday = check_date.weekday()
  if (weekday == 5 ) or (weekday == 6):
    print(f"本日は、土,日なのでお休みです({check_date.strftime('%Y/%m/%d')})")
    return False
  shykujitsu = Shukujitsu()
  result = shykujitsu.get_shukujitsu(check_date=check_date)
  print(result)
  if result is not None:
    print(f"本日は、祝日：{result[HOLIDAY_NAME]}なのでお休みです({check_date.strftime('%Y/%m/%d')})")
    return False    
  print(f"電源ON!!({check_date.strftime('%Y/%m/%d')})")
  return True

def output_context(context):
  print('context')
  print(context)
  return 0

def output_event(event):
  print('event')
  print(event)
  return 0


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
