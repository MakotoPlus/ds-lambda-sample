import pytest
import datetime
from ..lambda_function import Shukujitsu, is_db_on, check_event_dict
from .. import lambda_function

#
# Build Sample command
# docker build -t docker-image-pytest:test . -f Dockerfile.test
#
# Run Pytest command
# docker run docker-image-pytest:test
class Test_Lambda():
  
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

  #def test_get_shukujitsu_url_error(self, mocker):
  #  mocker.patch('lambda_function.URL_SYUKUJITSU_CSV', 'https://error.abc.co.jp')
  #  result = Shukujitsu().get_shukujitsu(check_date=datetime.date(2023, 1, 1))
  #  assert result == []

  @pytest.mark.parametrize(
    "check_date, expect",[
      (datetime.date(2023, 10, 6), True)
      ,(datetime.date(2023, 10, 9), False)
      ,(datetime.date(2024, 1, 1), False)
    ]
  )
  def test_is_db_on(self, check_date, expect):
    result = is_db_on(check_date)
    assert result == expect

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
    
    if is_success:
      result = check_event_dict(event)
      if False == ('check_date_yyyymmdd' in expect_value):
        expect_value['check_date_yyyymmdd'] = datetime.date.today()
      assert expect_value == result
    else:
      with pytest.raises(Exception) as e:
        check_event_dict(event)
        print(e)
