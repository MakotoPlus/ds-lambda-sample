import os
import logging
import logging.config
from .rds_ctrl import RdsCtrl
from .ecs_ctrl import EcsCtrl
from .on_off import OnOff
from .event_bridge_ctrl import EventBridgeCtrl
from .syukujitsu import Shukujitsu

logging.config.fileConfig(os.getenv('LOGGER_CONFIG', ''))
logger = logging.getLogger(__name__)


def handler(event, context):
  logger.info('起動/停止Lambda Start')
  for ctrl_obj in get_ctrl_objs(event, Shukujitsu()):
    ctrl_obj.run()      
  logger.info('起動/停止Lambda 終了')
  return {'result': 'success'}


def get_ctrl_objs(event, shukujitsu):
  '''
  オブジェクトのリストを生成する
  
  - ONの場合は下記順番でオブジェクトのリストを生成する
    - RDS
    - EventBridge    
    - ECS
  - OFFの場合は下記順番でオブジェクトのリストを生成する
    - ECS
    - EventBridge
    - RDS
  '''
  ctrl_objs = []
  if not (OnOff.DICT_SWITCH_KEY in event):
    raise Exception(f'event parameter key is not key:{OnOff.DICT_SWITCH_KEY}')

  switch_value = event[OnOff.DICT_SWITCH_KEY]
  if (switch_value == OnOff.SWITCH_ON):
    ctrl_objs.append(RdsCtrl(event, shukujitsu))
    ctrl_objs.append(EventBridgeCtrl(event, shukujitsu))
    ctrl_objs.append(EcsCtrl(event, shukujitsu))
  elif (switch_value == OnOff.SWITCH_OFF):
    ctrl_objs.append(EcsCtrl(event, shukujitsu))
    ctrl_objs.append(EventBridgeCtrl(event, shukujitsu))
    ctrl_objs.append(RdsCtrl(event, shukujitsu))
  else:
    raise Exception(f'event parameter value error {switch_value}')

  return ctrl_objs

