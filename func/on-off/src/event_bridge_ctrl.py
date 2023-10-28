import os
import datetime
import copy
import logging.config
import boto3
from .syukujitsu import Shukujitsu
from .on_off import OnOff

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv('LOG_LEVEL', 'WARNING'))

class EventBridgeCtrl(OnOff):
  DICT_EVENT_BRIDGE_KEY = 'EventBridge'
  '''
  EventBridgeサービスを有効・無効設定するクラス
  '''
  def __init__(self, event, shukujitsu: Shukujitsu):
    super().__init__(event)
    self.shukujitsu = shukujitsu

  def _check_event_dict(self, event) -> dict:
    event = super(EventBridgeCtrl, self)._check_event_dict(event)
    result_dict = copy.deepcopy(event)
    if not (EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY in event ):
      raise Exception(f'event parameter key is not key:{EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY}')
    if type(result_dict[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY]) is str:
      result_dict[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY] = [result_dict[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY]]
    elif type(event[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY]) is not list:
      raise Exception(f'event parameter key is type error key:{EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY}')
    return result_dict

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
    logger.info(f"EventBridge起動 処理開始します({check_date.strftime('%Y/%m/%d')})")
    return True

  def _on(self) -> None:
    '''
    EventBridge Start
    '''
    client = boto3.client('events')
    for event_name in self.event[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY]:
      ret = client.enable_rule(Name=event_name)
      logger.debug(ret)
    logger.info("EventBridge起動 処理完了")

  def _off(self) -> None:
    '''
    EventBridge Stop
    '''
    client = boto3.client('events')
    for event_name in self.event[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY]:
      logger.debug(f'EventBridge event_name={event_name}')
      ret = client.disable_rule(Name=event_name)
      logger.debug(ret)
    logger.info("EventBridge停止 処理完了")
