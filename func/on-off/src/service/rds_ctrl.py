import copy, logging, boto3
from util.syukujitsu import Shukujitsu
from service.on_off import OnOff

logger = logging.getLogger()


class RdsCtrl(OnOff):
  DICT_DBINSTANCE_IDENTIFIER_KEY = 'DBInstanceIdentifier'
  DICT_REGION_KEY = 'region'


  def __init__(self, event, shukujitsu: Shukujitsu):
    super().__init__('RDS', event)
    self.shukujitsu = shukujitsu

  
  def _check_event_dict(self, event) -> dict:
    super(RdsCtrl, self)._check_event_dict(event)
    result_dict = copy.deepcopy(event)
    if not (RdsCtrl.DICT_REGION_KEY in event ):
      raise Exception(f'{self.name} event parameter key is not key:{RdsCtrl.DICT_REGION_KEY}')
    if not (RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY in event ):
      raise Exception(f'{self.name} event parameter key is not key:{RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY}')
    if type(result_dict[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]) is str:
      result_dict[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY] = [result_dict[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]]
    elif type(event[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]) is not list:
      raise Exception(f'{self.name} event parameter key is type error key:{RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY}')
    return result_dict

  
  def _is_running(self, check_date) -> bool:
    '''
    起動判断
    - Returns
      - true: 起動すべき時(土日、祝日でない)
      - false: 起動すべきではない時     
    '''
    if not self.shukujitsu.is_normal_date(name=self.name, check_date=check_date):
      return False
    logger.info(f"{self.name}起動 処理開始します({check_date.strftime('%Y/%m/%d')})")
    return True


  def _on(self) -> None:
    '''
    DB Instans Start
    '''
    rds = boto3.client('rds', region_name=self.event[RdsCtrl.DICT_REGION_KEY])
    for instance_name in self.event[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]:
      #
      # 起動前に状態確認して既に起動しているのなら何もしない
      status = self._get_db_instance_status(rds, instance_name)
      if "available" == status:
        logger.warning(f"{self.name} 既に起動しています instance:[{instance_name}]")
      elif "stopped" == status:
        ret = rds.start_db_instance(DBInstanceIdentifier=instance_name)
        logger.info(f'{self.name} Start Success:[{instance_name}]')
        logger.debug(ret)
      else:
        logger.warning(f'{self.name} Start Errorステータス更新中です :[{instance_name}]')    

  def _off(self) -> None:
    '''
    DB Instans Stop
    '''
    rds = boto3.client('rds', region_name=self.event[RdsCtrl.DICT_REGION_KEY])
    for instance_name in self.event[RdsCtrl.DICT_DBINSTANCE_IDENTIFIER_KEY]:
      #
      # 起動前に状態確認して既に停止しているのなら何もしない
      status = self._get_db_instance_status(rds, instance_name)
      if "stopped" == status:
        logger.warning(f"{self.name} 既に一時的に停止しています instance:[{instance_name}]")
      elif "available" == status:
        ret = rds.stop_db_instance(DBInstanceIdentifier=instance_name)
        logger.info(f'{self.name} Stop Success:[{instance_name}]')
        logger.debug(ret)
      else:
        logger.warning(f'{self.name} Stop Errorステータス更新中です :[{instance_name}]')
    logger.info(f"{self.name} 停止 処理完了")


  def _get_db_instance_status(self, rds, instance_name) -> str:
    '''
    RDS インスタンスステータスを返す
    '''
    ret = rds.describe_db_instances(DBInstanceIdentifier=instance_name)
    return ret["DBInstances"][0]["DBInstanceStatus"]
