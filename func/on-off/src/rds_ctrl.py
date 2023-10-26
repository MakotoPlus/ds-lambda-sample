import datetime
import copy
import boto3
from .syukujitsu import HOLIDAY_NAME, Shukujitsu
from .on_off import OnOff


class RdsCtrl(OnOff):
  DICT_DBINSTANCE_IDENTIFIER_KEY = 'DBInstanceIdentifier'
  DICT_REGION_KEY = 'region'


  def __init__(self, event, shukujitsu: Shukujitsu):
    super().__init__(event)
    self.shukujitsu = shukujitsu

  
  def _check_event_dict(self, event) -> dict:
    super(RdsCtrl, self)._check_event_dict(event)
    result_dict = copy.deepcopy(event)
    if not (RdsCtrl.DICT_REGION_KEY in event ):
      raise Exception(f'event parameter key is not key:{RdsCtrl.DICT_REGION_KEY}')
    if not (RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY in event ):
      raise Exception(f'event parameter key is not key:{RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY}')
    if type(result_dict[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]) is str:
      result_dict[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY] = [result_dict[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]]
    elif type(event[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]) is not list:
      raise Exception(f'event parameter key is type error key:{RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY}')
    return result_dict

  
  def _is_running(self, check_date) -> bool:
    if not (super(RdsCtrl, self)._is_running(check_date)):
      return False
    result = self.shukujitsu.get_shukujitsu(check_date=check_date)
    if result is not None:
      print(f"本日は、祝日：{result[HOLIDAY_NAME]}なのでお休みです({check_date.strftime('%Y/%m/%d')})")
      return False
    print(f"RDS 起動 処理開始します({check_date.strftime('%Y/%m/%d')})")
    return True


  def _on(self):
    '''
    DB Instans Start
    '''
    rds = boto3.client('rds', region_name=self.event[RdsCtrl.DICT_REGION_KEY])
    for instance_name in self.event[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]:
      #
      # 起動前に状態確認して既に起動しているのなら何もしない
      ret = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
      if "available" == ret["DBInstances"][0]["DBInstanceStatus"]:
        print(f"RDS Instance 既に起動しています instance:[{instance_name}]")
      else:
        ret = rds.start_db_instance(DBInstanceIdentifier=instance_name)
        print(f'RDS Instance Start Success:[{instance_name}]')
        #print(ret)


  def _off(self):
    '''
    DB Instans Stop
    '''
    rds = boto3.client('rds', region_name=self.event[RdsCtrl.DICT_REGION_KEY])
    for instance_name in self.event[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]:
      #
      # 起動前に状態確認して既に起動しているのなら何もしない
      ret = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
      if "stopped" == ret["DBInstances"][0]["DBInstanceStatus"]:
        print(f"RDS Instance 既に一時的に停止しています instance:[{instance_name}]")
      else:
        ret = rds.stop_db_instance(DBInstanceIdentifier=instance_name)
        print(f'RDS Instance Stop Success:[{instance_name}]')
        #print(ret)
    print("RDS 停止 処理完了")
