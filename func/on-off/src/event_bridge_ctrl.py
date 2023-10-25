import datetime
import copy
import boto3
from .syukujitsu import HOLIDAY_NAME, Shukujitsu
from .on_off import OnOff


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
    if not (super(EventBridgeCtrl, self)._is_running(check_date)):
      return False
    result = self.shukujitsu.get_shukujitsu(check_date=check_date)
    if result is not None:
      print(f"本日は、祝日：{result[HOLIDAY_NAME]}なのでお休みです({check_date.strftime('%Y/%m/%d')})")
      return False    
    print(f"電源ON!!({check_date.strftime('%Y/%m/%d')})")
    return True

  def _on(self):
    '''
    EventBridge Start
    '''
    client = boto3.client('events')
    for event_name in self.event[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY]:
      ret = client.enable_rule(Name=event_name)
      print(ret)

  def _off(self):
    '''
    EventBridge stop
    '''
    client = boto3.client('events')
    for event_name in self.event[EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY]:
      print(f'event_name={event_name}')
      ret = client.disable_rule(Name=event_name)
      print(ret)

