import sys
from .rds import RdsCtl
from .syukujitsu import Shukujitsu

def handler(event, context):
  print('RDS 起動/停止Lambda Start')
  output_event(event)  
  rds_ctl = RdsCtl(event, Shukujitsu())
  rds_ctl.run() 
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


