import pytest
from ..lambda_function import output_context, output_event, handler
#from ..lambda_function import output_event
#from .. import lambda_function

class Test_Paramters():
  def test_01(self):
    ret = output_context("test")
    assert 0 == ret
  
  def test_02(self):
    ret = output_event("test")
    assert 0 == ret
  
  def test_03(self):
    event = {
      "evnet":"start",
      "id": 223,
      "date": "2023/10/09"
    }
    context = {}
    ret = handler(event, context)
    print(ret)

