import pytest
import os
import logging
from logging import getLogger, config
from ..logging_config import LOGGING_CONFIG 
import datetime
from ..syukujitsu import Shukujitsu
from ..ec2_ctrl import Ec2Ctrl, StopMode
from ..on_off import OnOff

logging.config.dictConfig(LOGGING_CONFIG)
logger = getLogger(__name__)

#
# Build Sample command
# cd on-off
# docker build -t docker-image-pytest:test .
#
# Run Pytest command
# docker run docker-image-pytest:test
# docker logs pytest-test
#
class Test_Ec2Ctrl():

  @pytest.mark.parametrize(
    "testno, event, expect",[
      (
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: "instance-name",
            Ec2Ctrl.DICT_STOP_MODE_KEY: StopMode.HARD.value
          }
        },
        (
          True, {
            OnOff.DICT_CHECK_DATE_YYYYMMDD: datetime.date(2023,10,6),
            OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
            Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
              Ec2Ctrl.DICT_INSTANCE_KEY: ["instance-name"],
              Ec2Ctrl.DICT_STOP_MODE_KEY: StopMode.HARD.value
            }            
          }
        )
      )
      ,(
        "002",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: "instance-name",
          }
        },
        (
          True, {
            OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
            Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
              Ec2Ctrl.DICT_INSTANCE_KEY: ["instance-name"],
              Ec2Ctrl.DICT_STOP_MODE_KEY: StopMode.NORMAL.value
            }            
          }
        )
      )
      ,(
        "003",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{}
        },
        (
          True, {
            OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
            Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{}
          }
        )
      )
      ,(
        "004",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
        },
        (
          False, {
          }
        )
      )
      ,(
        "005",
        {
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
          }
        },
        (
          False, {
          }
        )
      )
    ])
  def test_check_event_dict(self, testno, event, expect):
    '''
    オブジェクト生成後の .eventが想定通りの値になっているかのテスト
    '''
    logger.info(f'test_check_event_dict::testno={testno}')
    is_success = expect[0]
    expect_value = expect[1]
    syukujitsu = Shukujitsu()    
    if is_success:
      ec2_ctrl = Ec2Ctrl(event, syukujitsu)
      if False == ('check_date_yyyymmdd' in expect_value):
        expect_value['check_date_yyyymmdd'] = datetime.date.today()
      assert expect_value == ec2_ctrl.event
    else:
      with pytest.raises(Exception) as e:
        ec2_ctrl(event, syukujitsu)
        print(e)

  @pytest.mark.parametrize(
    "testno, event",[
      (
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: "instance-name-001",
            Ec2Ctrl.DICT_STOP_MODE_KEY: StopMode.HARD.value
          }
        },
      )
      ,(
        "002",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: ["instance-name-001", "instance-name-002"]
          }
        },
      )
    ]
  )
  def test_ec2_on_normal(self, testno, event, mocker):
    logger.info(f'test_ec2_on_normal::testno={testno}')
    class MockBoto3():
      def start_instances(self, *args, **kwargs):
        logger.info(f'start_instances() parameter::{kwargs["InstanceIds"]}')
        return kwargs
    mocker.patch("boto3.client", return_value=MockBoto3())
    Ec2Ctrl(event, Shukujitsu()).run()


  @pytest.mark.parametrize(
    "testno, event",[
      (
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: "instance-name-001",
            Ec2Ctrl.DICT_STOP_MODE_KEY: StopMode.HARD.value
          }
        },
      )
      ,(
        "002",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: ["instance-name-001",
                                        "instance-name-002",
                                        "instance-name-003"
                                        ]
          }
        },
      )
      ,( # 指定したインスタンス名のステータスが返ってこなかった場合の動作確認
        "003",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: ["instance-name-X01",
                                        "instance-name-X02",
                                        "instance-name-X03"
                                        ]
          }
        },
      )
    ]
  )
  def test_ec2_off_normal(self, testno, event, mocker):
    logger.info(f'test_ec2_off_normal::testno={testno}')
    class MockBoto3():
      def describe_instance_status(self, *args, **kwargs):
        logger.info(f'describe_instance_status() parameter::{kwargs}')
        return {
          'InstanceStatuses': [{
            'InstanceId': 'instance-name-001',
            'InstanceState': {
              'Name' : 'Running',
              'Code' : Ec2Ctrl.ECS_RUNNING
            }
          },
          {
            'InstanceId': 'instance-name-002',
            'InstanceState': {
              'Name' : 'Running',
              'Code' : Ec2Ctrl.ECS_RUNNING
            }
          },
          {
            'InstanceId': 'instance-name-003',
            'InstanceState': {
              'Name' : 'Running',
              'Code' : 'Stopping'
            }
          },
        ]}
      def modify_instance_attribute(self, *args, **kwargs):
        '''
        Test Case 001 以外は呼出されないメソッドなのでその場合は例外を投げる
        '''
        logger.info(f'modify_instance_attribute() parameter::{kwargs}')
        if testno != "001":
          raise Exception('call error')

      def stop_instances(self, *args, **kwargs):
        '''
        インスタンス名がinstance-name-001, instance-name-002以外は例外を投げる
        '''
        logger.info(f'stop_instances() parameter::{kwargs}')
        if kwargs["InstanceIds"][0] != "instance-name-001" and  \
          kwargs["InstanceIds"][0] != "instance-name-002":
          raise Exception('call error')          
        return {"result": "success"}

    mocker.patch("boto3.client", return_value=MockBoto3())
    Ec2Ctrl(event, Shukujitsu()).run()


  @pytest.mark.parametrize(
    "testno, event",[
      ( # 指定したインスタンス名のステータスが返ってこなかった場合の動作確認
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
            Ec2Ctrl.DICT_INSTANCE_KEY: ["instance-name-X01",
                                        ]
          }
        },
      )
    ]
  )
  def test_ec2_off_log_output_check(self, testno, event, mocker, caplog):
    logger.info(f'test_ec2_off_log_output_check::testno={testno}')
    class MockBoto3():
      def describe_instance_status(self, *args, **kwargs):
        logger.info(f'describe_instance_status() parameter::{kwargs}')
        return {
          'InstanceStatuses': [{
            'InstanceId': 'instance-name-001',
            'InstanceState': {
              'Name' : 'Running',
              'Code' : Ec2Ctrl.ECS_RUNNING
            }
          },
        ]}
      def modify_instance_attribute(self, *args, **kwargs):
        '''
        呼出されないメソッドなのでその場合は例外を投げる
        '''
        logger.info(f'modify_instance_attribute() parameter::{kwargs}')
        raise Exception('call error')

      def stop_instances(self, *args, **kwargs):
        '''
        呼出されないメソッドなのでその場合は例外を投げる
        '''
        logger.info(f'stop_instances() parameter::{kwargs}')
        raise Exception('call error')          

    mocker.patch("boto3.client", return_value=MockBoto3())
    Ec2Ctrl(event, Shukujitsu()).run()
    # 単独のTest時にしかログ出力が有効にならないためこれは通らないためコメントアウト
    # assert( "task.ec2_ctrl", logging.INFO, "no_instances_status=[instance-name-X01]") in caplog.record_tuples

  @pytest.mark.parametrize(
    "testno, event",[
      ( # 未設定のOFF動作確認
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
          }
        },
      )
      ,( # 未設定のON動作確認
        "002",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          Ec2Ctrl.DICT_EVENT_EC2_SERVICE_KEY:{
          }
        },
      )
    ]
  )
  def test_ec2_nothing(self, testno, event, mocker):
    logger.info(f'test_ec2_nothing::testno={testno}')
    class MockBoto3():
      pass

    mocker.patch("boto3.client", return_value=MockBoto3())
    Ec2Ctrl(event, Shukujitsu()).run()
    # 単独のTest時にしかログ出力が有効にならないためこれは通らないためコメントアウト
    # assert( "task.ec2_ctrl", logging.INFO, "no_instances_status=[instance-name-X01]") in caplog.record_tuples

