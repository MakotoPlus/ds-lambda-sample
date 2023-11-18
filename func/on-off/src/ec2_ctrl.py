import os
import datetime
import copy
from enum import Enum
import logging.config
import logging
import boto3
from .syukujitsu import Shukujitsu
from .on_off import OnOff

# 下記行を有効にするとDockerでも出力出来る
logging.config.fileConfig(os.getenv('LOGGER_CONFIG', ''))
logger = logging.getLogger(__name__)

class StopMode(Enum):
  NORMAL = 'normal'
  HARD = 'hard'

class Ec2Ctrl(OnOff):
  '''
  ECS サービスのタスク数を設定する
  '''
  DICT_EVENT_EC2_SERVICE_KEY = 'EC2'
  DICT_INSTANCE_KEY = 'instance'
  DICT_STOP_MODE_KEY = 'stopMode'

  ECS_RUNNING = 16

  def __init__(self, event, shukujitsu: Shukujitsu):
    super().__init__(event)
    self.shukujitsu = shukujitsu

  def _check_event_dict(self, event) -> dict:
    '''
    EC2 サービスのタスク定義が想定通りかチェックする
    
    - EC2: {'instance': ['instance name',...], 'stopMode': 'normal' or 'hard'}
    '''
    logger.debug('check_event_dict::ec2')
    event = super(Ec2Ctrl, self)._check_event_dict(event)
    if not (Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY in event ):
      raise Exception(f'event parameter key is not key:{Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY}')
    ec2_service_values = event[Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY]
    if not Ec2Ctrl.DICT_INSTANCE_KEY in ec2_service_values:
      return event
    instances = ec2_service_values[Ec2Ctrl.DICT_INSTANCE_KEY]
    if type(instances) is str:
      ec2_service_values[Ec2Ctrl.DICT_INSTANCE_KEY] = [instances]
    elif type(instances) is not list:
      raise Exception(f'event parameter key is type error key:{Ec2Ctrl.DICT_INSTANCE_KEY}')

    if not Ec2Ctrl.DICT_STOP_MODE_KEY in ec2_service_values:
      ec2_service_values[Ec2Ctrl.DICT_STOP_MODE_KEY] = StopMode.NORMAL.value
      logger.info("STOP_MODE Nothing")
      return event

    if ec2_service_values[Ec2Ctrl.DICT_STOP_MODE_KEY] != StopMode.HARD.value:
      ec2_service_values[Ec2Ctrl.DICT_STOP_MODE_KEY] = StopMode.NORMAL.value
      logger.info("STOP_MODE NOT HARD")
      return event
      
    logger.info("STOP_MODE HARD")
    return event

  def _is_running(self, check_date) -> bool:
    '''
    起動判断
    - Returns
      - true: 起動すべき時(土日、祝日でない)
      - false: 起動すべきではない時     
    '''
    result = self.shukujitsu.is_normal_date(check_date=check_date)
    if not result:
      return False
    logger.info(f"EC2起動 処理開始します({check_date.strftime('%Y/%m/%d')})")
    return True

  def _on(self) -> None:
    '''
    EC2 Service Start
    '''
    client = boto3.client('ec2')
    ec2_instances = self.event[Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY][Ec2Ctrl.DICT_INSTANCE_KEY]
    ret = client.start_instances(InstanceIds=[ec2_instances])
    logger.debug(ret)
    logger.info('EC2起動 処理完了')

  def _off(self) -> None:
    '''
    EC2 Service Stop
    '''
    client = boto3.client('ec2')
    
    #
    # Instance Status 取得
    ec2_instance_names = self.event[Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY][Ec2Ctrl.DICT_INSTANCE_KEY]
    status = client.describe_instance_status(InstanceIds=ec2_instance_names)
    instans_status = status['InstanceStatuses']
    for ec2_instance_name in ec2_instance_names:
      for ecs_status in instans_status :
        if ec2_instance_name == ecs_status['InstanceId']:
          # Instance Status Check
          logger.debug(
            f'InstanceName=[{ec2_instance_name}] status=[{ecs_status["InstanceState"]["Name"]}]'
          )
          if ecs_status["InstanceState"]["Code"] != Ec2Ctrl.ECS_RUNNING:
            logger.info(
              f'ec2 instances=[{ec2_instance_name}]は起動中ではありませんでした。'  \
              f'停止処理をスキップします status={ecs_status["InstanceState"]["Code"]}'
            )
            break
          #
          # STOP Mode 「hard」の場合は停止保護を解除する
          if StopMode.HARD.value == \
            self.event[Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY][Ec2Ctrl.DICT_STOP_MODE_KEY]:
            client.modify_instance_attribute(
              InstanceId=ec2_instance_name,
              DisableApiStop={"Value" : False}
            )
          response = client.stop_instances(
            InstanceIds=[ec2_instance_name]
          )
          logger.info(
            f'ec2 instances=[{ec2_instance_name}]の停止処理を実行しました。'
          )
          logger.debug(
            f'ec2 stop_instances=[{ec2_instance_name}] status=[{response}]'
          )
          break
      else:
        logger.info(f'no_instances_status=[{ec2_instance_name}]')
    logger.info('EC2停止 処理完了')


