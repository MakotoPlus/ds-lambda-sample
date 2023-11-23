import os
import pytest
import datetime
import logging.config
import logging
from logging import getLogger

import sys
sys.path.append(os.getenv("PATH_ROOT","/var/task"))
#from util.syukujitsu import Shukujitsu
from util.logging_config import LOGGING_CONFIG 
#from service.rds_ctrl import RdsCtrl
from lambda_function import handler

logging.config.dictConfig(LOGGING_CONFIG)
logger = getLogger(__name__)


class Test_Lambda():
  @pytest.mark.parametrize(
    "testno, event", [
      (
        "001",
        {
          "check_date_yyyymmdd":"20231006",
          "switch": "on",
          "region": "ap-northeast-1",
          "DBInstanceIdentifier": [],
          "EventBridge": [],
          "EcsService": [],
          "EC2": {}
        }
      )
  ])
  def test_001(self, testno, event, mocker):
    logger.info(f"start {testno}")
    class MockBoto3():
      pass
    mocker.patch("boto3.client", return_value=MockBoto3())
    handler(event, None)
