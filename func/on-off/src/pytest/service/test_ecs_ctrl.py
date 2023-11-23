import os
import pytest
import datetime
import logging
from logging import getLogger
import sys

sys.path.append(os.getenv("PATH_ROOT","/var/task"))
from service.ecs_ctrl import EcsCtrl
from service.on_off import OnOff
from util.logging_config import LOGGING_CONFIG 
from util.syukujitsu import Shukujitsu

logging.config.dictConfig(LOGGING_CONFIG)
logger = getLogger(__name__)

class Test_EcsCtrl():
  @pytest.mark.parametrize(
    "testno, event, expect",[
      (
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[{
            EcsCtrl.DICT_CLUSTER_KEY: "cluster",
            EcsCtrl.DICT_SERVICE_KEY: "service",
            EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
          }]
        }, 
        (
          True, {
            OnOff.DICT_CHECK_DATE_YYYYMMDD: datetime.date(2023,10,6),
            OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
            EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[{
              EcsCtrl.DICT_CLUSTER_KEY: "cluster",
              EcsCtrl.DICT_SERVICE_KEY: "service",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
            }]
          }
        )
      )
      ,(
        "002",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster01",
              EcsCtrl.DICT_SERVICE_KEY: "service01",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
            },
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster02",
              EcsCtrl.DICT_SERVICE_KEY: "service02",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 100
            }
          ]
        }, 
        (
          True, {
            OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
            EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[
              {
                EcsCtrl.DICT_CLUSTER_KEY: "cluster01",
                EcsCtrl.DICT_SERVICE_KEY: "service01",
                EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
              },
              {
                EcsCtrl.DICT_CLUSTER_KEY: "cluster02",
                EcsCtrl.DICT_SERVICE_KEY: "service02",
                EcsCtrl.DICT_DESIRED_COUNT_KEY: 100
              }
            ]
          }
        )
      )
    ]
  )
  def test_check_event_dict(self, testno, event, expect):
    '''
    オブジェクト生成後の .eventが想定通りの値になっているかのテスト
    '''
    is_success = expect[0]
    expect_value = expect[1]
    syukujitsu = Shukujitsu()    
    if is_success:
      ecs_ctrl = EcsCtrl(event, syukujitsu)
      if False == ('check_date_yyyymmdd' in expect_value):
        expect_value['check_date_yyyymmdd'] = datetime.date.today()
      assert expect_value == ecs_ctrl.event
    else:
      with pytest.raises(Exception) as e:
        ecs_ctrl(event, syukujitsu)
        print(e)

  @pytest.mark.parametrize(
    "testno, event", [
      (
        "001",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster01",
              EcsCtrl.DICT_SERVICE_KEY: "service01",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
            },
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster02",
              EcsCtrl.DICT_SERVICE_KEY: "service02",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 100
            }
          ]
        }
      )
      ,(
        "002",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster01",
              EcsCtrl.DICT_SERVICE_KEY: "service01",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
            },
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster02",
              EcsCtrl.DICT_SERVICE_KEY: "service02",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 100
            }
          ]
        }
      )
      ,(
        "003",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[]
        }
      )
    ]
  )
  def test_event_ecs_on_off(self, testno, event, mocker):
    '''
    ON OFF処理が例外が発生しないかの確認
    on_off_2()で十分だが、MagicMockのサンプルになるのでとりあえず残した
    '''
    ecs_start_mock = mocker.MagicMock(return_value=True)
    ecs_stop_mock = mocker.MagicMock(return_value=True)
    ecs_ctrl = EcsCtrl(event, Shukujitsu())
    mocker.patch.object(ecs_ctrl, "_on", ecs_start_mock)
    mocker.patch.object(ecs_ctrl, "_off", ecs_stop_mock)
    ecs_ctrl.run()


  @pytest.mark.parametrize(
    "testno, event", [
      (
        "001",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster01",
              EcsCtrl.DICT_SERVICE_KEY: "service01",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
            }
          ]
        }
      )
      ,(
        "002",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster02",
              EcsCtrl.DICT_SERVICE_KEY: "service02",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 1
            },
            {
              EcsCtrl.DICT_CLUSTER_KEY: "cluster03",
              EcsCtrl.DICT_SERVICE_KEY: "service03",
              EcsCtrl.DICT_DESIRED_COUNT_KEY: 100
            }
          ]
        }
      )
      ,(
        "003",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[]
        }
      )
      ,(
        "004",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          EcsCtrl.DICT_EVENT_ECS_SERVICE_KEY:[]
        }
      )
    ]
  )
  def test_event_ecs_on_off_2(self, testno, event, mocker):
    '''
    ON OFF処理が例外が発生しないかの確認
    '''
    class MockBoto3():
      def update_service(self, *args, **kwargs):
        return kwargs
    mocker.patch("boto3.client", return_value=MockBoto3())
    EcsCtrl(event, Shukujitsu()).run()

