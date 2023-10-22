import pytest
import datetime
from ..syukujitsu import Shukujitsu
from ..rds import RdsCtl

#
# Build Sample command
# docker build -t docker-image-pytest:test .
#
# Run Pytest command
# docker run docker-image-pytest:test
class Test_Rds():
  
  #def test_get_shukujitsu_url_error(self, mocker):
  #  mocker.patch('lambda_function.URL_SYUKUJITSU_CSV', 'https://error.abc.co.jp')
  #  result = Shukujitsu().get_shukujitsu(check_date=datetime.date(2023, 1, 1))
  #  assert result == []
  @pytest.mark.parametrize(
    "testno, event, expect",[
      (
        "001",
        {
          "check_date_yyyymmdd":"20231006",
          "switch": "on",
          "region": "ap-northeast-1",
          "DBInstanceIdentifier": "instance"
        }, 
        (
          True, {
            "check_date_yyyymmdd": datetime.date(2023,10,6),
            "switch": "on",
            "region": "ap-northeast-1",
            "DBInstanceIdentifier": ["instance"]
          }
        )
      )
      ,(
        "002",
        {
          "switch": "on",
          "region": "ap-northeast-1",
            "DBInstanceIdentifier": ["instance-1", "instance-2"]
        }, 
        (
          True, {
            "switch": "on",
            "region": "ap-northeast-1",
            "DBInstanceIdentifier": ["instance-1", "instance-2"]
          }
        )
      )
      ,(
        "003",
        {
          "check_date_yyyymmdd":"20231009",
          "switch": "off",
          "region": "ap-northeast-1",
            "DBInstanceIdentifier": ["instance"]
        }, 
        (
          True, {
            "check_date_yyyymmdd": datetime.date(2023, 10, 9),
            "switch": "off",
            "region": "ap-northeast-1",
            "DBInstanceIdentifier": ["instance"]
          }
        )
      )
      ,(
        "004",
        {
          "region": "ap-northeast-1",
          "DBInstanceIdentifier": ["instance"]
        }, 
        (
          False, {}
        )
      )
      ,(
        "005",
        {
          "switch": "off",
          "DBInstanceIdentifier": ["instance"]
        }, 
        (
          False, {}
        )
      )
      ,(
        "006",
        {
          "switch": "off",
          "region": "ap-northeast-1",
        }, 
        (
          False, {}
        )
      )
    ]
  )
  def test_check_event_dict(self, testno, event, expect):    
    is_success = expect[0]
    expect_value = expect[1]
    syukujitsu = Shukujitsu()    
    if is_success:
      rds_ctl = RdsCtl(event, syukujitsu)
      if False == ('check_date_yyyymmdd' in expect_value):
        expect_value['check_date_yyyymmdd'] = datetime.date.today()
      assert expect_value == rds_ctl.event
    else:
      with pytest.raises(Exception) as e:
        rds_ctl = RdsCtl(event, syukujitsu)
        print(e)
