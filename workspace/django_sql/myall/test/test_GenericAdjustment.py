import pytest
import factory
import logging
import json
import copy
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
      (
        [True, False],
        [1, 10],
        ["paypay", "linepay", ],
        ["paypay-user", "linepay"],
        [None, "Line-001"],
        [{"use_name": "paypay", "value": 1}]
      )
    ]
  )
  def test_001(self, objIsPaypays, values, use_names, tags, lineids, expects):
    '''GenericAdjustment,PayPayのデータ登録確認'''
    
    for (objIsPaypay, value, use_name, tag, lineid) in zip(objIsPaypays, values, use_names, tags, lineids):
      if objIsPaypay:
        obj = models.PayPay(value=value, use_name=use_name)
      else:
        obj = models.LinePay(value=value, use_name=use_name, lineid=lineid)
      print(f'Save Type {type(obj)}')
      obj.save()              
      genericObj = models.GenericAdjustment(content_object=obj, tag=tag)
      genericObj.save()
      print(f'Save Type {type(genericObj)}')
    geneRecords = models.GenericAdjustment.objects.filter(tag="paypay-user")
    assert len(geneRecords) == len(expects)
    for (re, expect) in zip(geneRecords, expects):
      print('Check!!!!!!!!!!!!!!!!!!!')
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

  @pytest.mark.parametrize(
    "datas, expects",
    [
      (
        [
          {
          "type": True,
          "value" : 1,
          "use_name": "paypay",
          "tags": "paypay-user",
          "lineid": None,
          }
        ,{
          "type": False,
          "value" : 10,
          "use_name": "linepay",
          "tags": "linepay",
          "lineid": "Line-001",
          }
        ]
        ,[
          {"use_name": "paypay", "value": 1}
        ]
      )
    ]
  )
  def test_002(self, datas, expects):
    '''
    GenericAdjustment,PayPayのデータ登録確認
      - パラメータをＤＢ登録単位に変更
    '''
    for data in datas:
      if data["type"]:
        values = copy.copy(data)
        del values["type"], values["tags"], values["lineid"]
        obj = models.PayPay(**values)
      else:
        values = copy.copy(data)
        del values["type"], values["tags"]
        obj = models.LinePay(**values)
      print(f'Save Type {type(obj)}')
      obj.save()
      genericObj = models.GenericAdjustment(content_object=obj, tag=data["tags"])
      genericObj.save()
      print(f'Save Type {type(genericObj)}')
    geneRecords = models.GenericAdjustment.objects.filter(tag="paypay-user")
    assert len(geneRecords) == len(expects)
    for (re, expect) in zip(geneRecords, expects):
      assert (isinstance(re.content_object, models.PayPay))
      assert re.content_object.use_name == expect["use_name"]
      assert re.content_object.value == expect["value"]
  
  @pytest.mark.parametrize(
    "mtags_cnt, expects",
    [
      (3, "")
    ]
  )
  def test_003(self, mtags_cnt, expects) :
    pubs = test_factory.M2MSimple_PublicationFactory.create_batch(mtags_cnt)
    record = test_factory.M2MSimple_AuthorFactory(publications=pubs,)

    print(f'tags lne={len(record.publications.all())}')
    for r in record.publications.all():
      print(r.title)

  def test_004(self) :
    # 別名定義 aliasでもいいのに・・
    authorFact = test_factory.AuthorFactory002.create(form_attributes='headlineだよ')
    print(authorFact.headline)
    #print(type(authorFact.get_model_calss()))

  def test_005(self) :
    # 別名定義 aliasでもいいのに・・
    authorFact = test_factory.AuthorFactory003()
    print(type(authorFact))
    print(f'headline={authorFact.headline}')

  def test_006(self) :
    line_pay = test_factory.LienyPayTraitFactory(data=True)
    print(f'line_pay.id=[{line_pay.id}]')
    print(f'line_pay=[{line_pay}]')
    print(f'line_pay.lineid=[{line_pay.lineid}]')
    print(f'line_pay.value=[{line_pay.value}]')

  def test_007(self) :
    sub_company = test_factory.SubCompany2TraitFactory(parent_company=True)
    print(f'company.id=[{sub_company.id}]')
    print(f'subName=[{sub_company.subName}]')
    if sub_company.company_id:
      print(f'company_id=[{sub_company.company_id.id}]')
      print(f'company_name=[{sub_company.company_id.name}]')
      #print(sub_company.get_model_calss())
    
  def test_008(self):
    '''
    Factory Line data 
    '''