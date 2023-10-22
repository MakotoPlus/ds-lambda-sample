import sys
import datetime
import urllib.request
import copy
import boto3
from .syukujitsu import HOLIDAY_DATE, HOLIDAY_NAME, Shukujitsu

URL_SYUKUJITSU_CSV = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"
DICT_SWITCH_KEY = 'switch'
DICT_REGION_KEY = 'region'
DICT_DBINSTANCE_IDENTIFIER_KEY = 'DBInstanceIdentifier'
DICT_CHECK_DATE_YYYYMMDD = 'check_date_yyyymmdd'
SWITCH_ON = 'on'
SWITCH_OFF = 'off'


class RdsCtl():
  def __init__(self, event, shukujitsu: Shukujitsu):
    self.event = self.__check_event_dict(event)
    self.shukujitsu = shukujitsu

  def run(self):
    '''
    SWITCH_ONの場合は、平日以外の場合は何もしないで終了する
    SWITCH_OFFはいつでもOFFを実行する
    '''
    if self.event[DICT_SWITCH_KEY] == SWITCH_ON:
      result = self.__is_db_on(self.event[DICT_CHECK_DATE_YYYYMMDD])
      if False == result:
        return
    if self.event[DICT_SWITCH_KEY] == SWITCH_ON:
      self.__db_start(self.event)
    else:
      self.__db_stop(self.event)
  
  def __check_event_dict(self, event) -> dict:
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
  
  def __is_db_on(self, check_date) -> bool:
    weekday = check_date.weekday()
    if (weekday == 5 ) or (weekday == 6):
      print(f"本日は、土,日なのでお休みです({check_date.strftime('%Y/%m/%d')})")
      return False
    #shykujitsu = Shukujitsu()
    result = self.shykujitsu.get_shukujitsu(check_date=check_date)
    print(result)
    if result is not None:
      print(f"本日は、祝日：{result[HOLIDAY_NAME]}なのでお休みです({check_date.strftime('%Y/%m/%d')})")
      return False    
    print(f"電源ON!!({check_date.strftime('%Y/%m/%d')})")
    return True

  def __db_start(self):
    '''
    DB Instans Start
    '''
    rds = boto3.client('rds', region_name=self.event[DICT_REGION_KEY])
    for instance_name in self.event[DICT_DBINSTANCE_IDENTIFIER_KEY]:
      #
      # 起動前に状態確認して既に起動しているのなら何もしない
      ret = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
      if "available" == ret["DBInstances"][0]["DBInstanceStatus"]:
        print(f"RDS Instance 既に起動しています instance:[{instance_name}]")
      else:
        ret = rds.start_db_instance(DBInstanceIdentifier=instance_name)
        print(f'RDS Instance Start Success:[{instance_name}]')
        print(ret)

  def db_stop(self):
    '''
    DB Instans Stop
    '''
    rds = boto3.client('rds', region_name=self.event[DICT_REGION_KEY])
    for instance_name in self.event[DICT_DBINSTANCE_IDENTIFIER_KEY]:
      #
      # 起動前に状態確認して既に起動しているのなら何もしない
      ret = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
      if "stopped" == ret["DBInstances"][0]["DBInstanceStatus"]:
        print(f"RDS Instance 既に一時的に停止しています instance:[{instance_name}]")
      else:
        ret = rds.stop_db_instance(DBInstanceIdentifier=instance_name)
        print(f'RDS Instance Stop Success:[{instance_name}]')
        print(ret)
