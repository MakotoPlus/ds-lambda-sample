import os
import datetime
import copy
from logging import getLogger
import boto3
from .syukujitsu import Shukujitsu
from .on_off import OnOff


logger = getLogger()


class EcsCtrl(OnOff):
  '''
  ECS サービスのタスク数を設定する
  '''
  DICT_EVENT_ECS_SERVICE_KEY = 'EcsService'
  DICT_CLUSTER_KEY = 'cluster'
  DICT_SERVICE_KEY = 'service'
  DICT_DESIRED_COUNT_KEY = 'desiredCount'

  def __init__(self, event, shukujitsu: Shukujitsu):
    super().__init__(event)
    self.shukujitsu = shukujitsu

  def _check_event_dict(self, event) -> dict:
    '''
    ECS サービスのタスク定義が想定通りかチェックする
    
    - EcsService: {['cluster': 'cluster name', 'service':'service name', 'desiredCount': N]}
    '''
    event = super(EcsCtrl, self)._check_event_dict(event)
    if not (EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY in event ):
      raise Exception(f'event parameter key is not key:{EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY}')
    ecs_service_values = event[EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY]
    for ecs_service_value in ecs_service_values:
      if not (EcsCtrl.DICT_CLUSTER_KEY in ecs_service_value):
        raise Exception(f'event parameter key is not key:{EcsCtrl.DICT_CLUSTER_KEY}')
      if not (EcsCtrl.DICT_SERVICE_KEY in ecs_service_value):
        raise Exception(f'event parameter key is not key:{EcsCtrl.DICT_SERVICE_KEY}')
      if not (EcsCtrl.DICT_DESIRED_COUNT_KEY in ecs_service_value):
        raise Exception(f'event parameter key is not key:{EcsCtrl.DICT_DESIRED_COUNT_KEY}')
      desired_count_value = ecs_service_value[EcsCtrl.DICT_DESIRED_COUNT_KEY]
      if not (isinstance(desired_count_value, int)):
        raise Exception(f'event parameter key is not type error:{type(desired_count_value)}')
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
    logger.info(f"ECS起動 処理開始します({check_date.strftime('%Y/%m/%d')})")
    return True

  def _on(self) -> None:
    '''
    ECS Service Start
    '''
    client = boto3.client('ecs')
    ecs_service_values = self.event[EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY]
    for ecs_service_value in ecs_service_values:      
      ret = client.update_service(
           cluster=ecs_service_value[self.DICT_CLUSTER_KEY],
           service=ecs_service_value[self.DICT_SERVICE_KEY],
           desiredCount=ecs_service_value[self.DICT_DESIRED_COUNT_KEY])
      
      logger.debug(ret)
    logger.info('ECS起動 処理完了')

  def _off(self) -> None:
    '''
    ECS Service Stop
    '''
    client = boto3.client('ecs')
    ecs_service_values = self.event[EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY]
    for ecs_service_value in ecs_service_values:      
      ret = client.update_service(
           cluster=ecs_service_value[self.DICT_CLUSTER_KEY],
           service=ecs_service_value[self.DICT_SERVICE_KEY],
           desiredCount = 0
        )
      logger.debug('ECS停止 処理完了')
    logger.info('ECS停止 処理完了')


