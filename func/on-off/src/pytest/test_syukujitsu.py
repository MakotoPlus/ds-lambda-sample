import os
import pytest
import datetime
import logging.config
import logging

from ..syukujitsu import Shukujitsu

logging.config.fileConfig(os.getenv('LOGGER_CONFIG', ''))
logger = logging.getLogger(__name__)

class Test_Syukujitsu():
  @pytest.mark.parametrize(
    "check_date, expect",[
      (datetime.date(2023, 10, 8), False)
      ,(datetime.date(2023, 10, 9), True)
    ]
  )
  def test_is_shukujitsu(self, check_date, expect):    
    result = Shukujitsu().is_shukujitsu(check_date=check_date)
    assert result == expect

  @pytest.mark.parametrize(
    "check_date, expect",[
      (datetime.date(2023, 10, 8), (None, ""))
      ,(datetime.date(2023, 10, 9), (True, "スポーツの日"))
      ,(datetime.date(2024, 1, 1), (True, "元日"))
    ]
  )
  def test_get_shukujitsu(self, check_date, expect):    
    result = Shukujitsu().get_shukujitsu(check_date=check_date)
    is_result = None if result is None else True
    if is_result:
      print(f"name=[{result['name']}]")
    assert is_result == expect[0]
    if expect[0]:
      assert expect[1] == result['name']


