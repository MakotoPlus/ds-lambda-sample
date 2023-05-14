import pytest
import factory
import logging
from django.db.models import Prefetch
from django.contrib.contenttypes.fields import GenericRelation
from myall.test.factory import test_factory
from myall import models

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestGenericAdjustment():
  
  @pytest.mark.parametrize(
    "objIsPaypays, values, use_names, tags, lineids, expects",
    [
      ([True, False], [1, 10], ["paypay", "linepay", ], ["paypay-user", "linepay"], [None, "Line-001"], [{"use_name": "paypay-user", "value": 1}])
    ]
  )
  def test_001(self, objIsPaypays, values, use_names, tags, lineids, expects):
    '''GenericAdjustment,PayPayのデータ登録確認'''
    
    for (objIsPaypay, value, use_name, tag, lineid) in zip(objIsPaypays, values, use_names, tags, lineids):
      if objIsPaypay:
        obj = models.PayPay(value=value, use_name=use_name)
      else:
        obj = models.LinePay(value=value, use_name=use_name, lineid=lineid)
      obj.save()              
      genericObj = models.GenericAdjustment(content_object=obj, tag=tag)
      genericObj.save()
    geneRecords = models.GenericAdjustment.objects.filter(tag="paypay")
    for (re, expect) in zip(geneRecords, expects):
      print(re.content_type)
      print(re.object_id)
      print(re.tag)
      print(re.content_object)
      print("type")
      print(type(re.content_type))
      print(type(re.object_id))
      print(type(re.tag))
      print(type(re.content_object))
      assert (isinstance(re.content_object, models.PayPay))
      assert re.content_object.use_name == expect["use_name"]
      assert re.content_object.value == expect["value"]
    