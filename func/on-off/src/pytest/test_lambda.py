import os
import pytest
import datetime
import logging.config
import logging

#from unittest.mock import patch
from ..syukujitsu import Shukujitsu
from ..rds_ctrl import RdsCtrl
from ..lambda_function import handler

logging.config.fileConfig(os.getenv('LOGGER_CONFIG', ''))
logger = logging.getLogger(__name__)


class Test_Lambda():
  @pytest.mark.parametrize(
    "testno, event", [
      (
        "001",
        {
          "check_date_yyyymmdd":"20231006",
          "switch": "on",
          "region": "ap-northeast-1",
          "DBInstanceIdentifier": "instance"
        }
      )
  ])
  def test_001(self, testno, event, mocker):
    #handler(event, None)
    pass