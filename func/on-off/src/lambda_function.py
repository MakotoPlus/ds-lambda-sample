import os, sys
import logging
from logging import getLogger, config
from service.on_off import OnOff
from service.rds_ctrl import RdsCtrl
from service.ecs_ctrl import EcsCtrl
from service.ec2_ctrl import Ec2Ctrl
from service.event_bridge_ctrl import EventBridgeCtrl
from util.syukujitsu import Shukujitsu
from util.logging_config import LOGGING_CONFIG 

logging.config.dictConfig(LOGGING_CONFIG)
logger = getLogger(__name__)

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
    - EC2
  - OFFの場合は下記順番でオブジェクトのリストを生成する
    - EC2
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
    ctrl_objs.append(Ec2Ctrl(event, shukujitsu))
  elif (switch_value == OnOff.SWITCH_OFF):
    ctrl_objs.append(Ec2Ctrl(event, shukujitsu))
    ctrl_objs.append(EcsCtrl(event, shukujitsu))
    ctrl_objs.append(EventBridgeCtrl(event, shukujitsu))
    ctrl_objs.append(RdsCtrl(event, shukujitsu))
  else:
    raise Exception(f'event parameter value error {switch_value}')

  return ctrl_objs

