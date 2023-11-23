import pytest
import datetime
import logging
import os, sys
from logging import getLogger
sys.path.append(os.getenv("PATH_ROOT","/var/task"))
from util.logging_config import LOGGING_CONFIG 
from util.syukujitsu import Shukujitsu
from service.event_bridge_ctrl import EventBridgeCtrl
from service.on_off import OnOff

logging.config.dictConfig(LOGGING_CONFIG)
logger = getLogger(__name__)

logging.config.dictConfig(LOGGING_CONFIG)
logger = getLogger(__name__)

#
# Build Sample command
# docker build -t docker-image-pytest:test .
#
# Run Pytest command
# docker run docker-image-pytest:test
class Test_EventBridgeCtrl():
  
  #def test_get_shukujitsu_url_error(self, mocker):
  #  mocker.patch('lambda_function.URL_SYUKUJITSU_CSV', 'https://error.abc.co.jp')
  #  result = Shukujitsu().get_shukujitsu(check_date=datetime.date(2023, 1, 1))
  #  assert result == []
  @pytest.mark.parametrize(
    "testno, event, expect",[
      (
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY: "instance"
        }, 
        (
          True, {
            OnOff.DICT_CHECK_DATE_YYYYMMDD: datetime.date(2023,10,6),
            OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
            EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY: ["instance"]
          }
        )
      )
    ]
  )
  def test_check_event_dict(self, testno, event, expect):
    is_success = expect[0]
    expect_value = expect[1]
    syukujitsu = Shukujitsu()    
    if is_success:
      event_bridge = EventBridgeCtrl(event, syukujitsu)
      if False == ('check_date_yyyymmdd' in expect_value):
        expect_value['check_date_yyyymmdd'] = datetime.date.today()
      assert expect_value == event_bridge.event
    else:
      with pytest.raises(Exception) as e:
        event_bridge(event, syukujitsu)
        print(e)

  @pytest.mark.parametrize(
    "testno, event", [
      (
        "001",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY: "instance"
        }
      )
      ,(
        "002",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_OFF,
          EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY: "instance"
        }
      )
      ,(
        "003",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY: ["instanceA", "instanceB"]
        }
      )
      ,(
        "004",
        {
          OnOff.DICT_CHECK_DATE_YYYYMMDD: "20231006",
          OnOff.DICT_SWITCH_KEY: OnOff.SWITCH_ON,
          EventBridgeCtrl.DICT_EVENT_BRIDGE_KEY: []
        }
      )
  ])
  def test_event_bridge_on(self, testno, event, mocker):
    bridge_start_mock = mocker.MagicMock(return_value=True)
    bridge_stop_mock = mocker.MagicMock(return_value=True)
    event_bridge = EventBridgeCtrl(event, Shukujitsu())
    mocker.patch.object(event_bridge, "_on", bridge_start_mock)
    mocker.patch.object(event_bridge, "_off", bridge_stop_mock)
    event_bridge.run()
