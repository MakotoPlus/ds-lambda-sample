import sys
from .rds_ctrl import RdsCtrl
from .event_bridge_ctrl import EventBridgeCtrl
from .syukujitsu import Shukujitsu

def handler(event, context):
  print('RDS 起動/停止Lambda Start')
  output_event(event)
  
  shukujitsu = Shukujitsu()
  #
  # STOP の場合はEventBridgeを先に実行する
  # STARTの場合はRDSを先に実行する  
  ctrl_objs = []
  if (event['switch'] == 'on'):
    ctrl_objs.append(create_rds_ctrlobj(event, shukujitsu))
    ctrl_objs.append(create_event_bridge_ctrlobj(event, shukujitsu))
  elif (event['switch'] == 'off'):
    ctrl_objs.append(create_event_bridge_ctrlobj(event, shukujitsu))
    ctrl_objs.append(create_rds_ctrlobj(event, shukujitsu))
  
  for ctrl_obj in ctrl_objs:
    if ctrl_obj is not None:
      ctrl_obj.run()
      
  print('RDS 起動/停止Lambda 終了')
  return {'result': 'success'}

def output_context(context):
  print('context')
  print(context)
  return 0

def output_event(event):
  print('event')
  print(event)
  return 0

def create_rds_ctrlobj(event, shukujitsu):
  try:
    ctrlobj = RdsCtrl(event, shukujitsu)
    return ctrlobj
  except Exception as e:
    print(e)
    return None

def create_event_bridge_ctrlobj(event, shukujitsu):
  try:
    ctrlobj = EventBridgeCtrl(event, shukujitsu)
    return ctrlobj
  except Exception as e:
    print(e)
    return None

