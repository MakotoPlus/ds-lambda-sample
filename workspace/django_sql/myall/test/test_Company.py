#
# Company, SubCompany
#
import pytest
import sys
import factory
import logging
from django.db.models import Prefetch, FilteredRelation, Q, Min, F, Count
from django.db import connection

from django.core.management import call_command
from myall.test.factory.test_factory import(
  CompanyFactory, SubCompanyFactory, SubCompanyTypeFactory
)
from myall.models import (Company, SubCompany, SubCompanyType)

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestCompany():
  
  @pytest.fixture
  def create_data_01(self):
    CompanyFactory.create(name='Test株式会社004 サブなし')
    CompanyFactory.create(name='Test株式会社003 サブなし')
    company = CompanyFactory.create(name='Test株式会社001')
    sub = SubCompanyFactory.create(subName='001サブ名001', company_id=company)
    sub = SubCompanyFactory.create(subName='001サブ名002', company_id=company)
    sub = SubCompanyFactory.create(subName='001サブ名003', company_id=company)
    company = CompanyFactory.create(name='Test株式会社002')
    sub = SubCompanyFactory.create(subName='002サブ名001', company_id=company)
    sub = SubCompanyFactory.create(subName='002サブ名002', company_id=company)

  @pytest.fixture
  def create_data_02(self):    
    CompanyFactory.create(name='Test株式会社004 サブなし')
    CompanyFactory.create(name='Test株式会社003 サブなし')
    company1 = CompanyFactory.create(name='Test株式会社001')
    company2 = CompanyFactory.create(name='Test株式会社002')

    type_a = SubCompanyTypeFactory.create(
      type_name="TYPE_A",
      disp_order = 1,
    )
    type_b = SubCompanyTypeFactory.create(
      type_name="TYPE_B",
      disp_order = 2,
    )
    type_c = SubCompanyTypeFactory.create(
      type_name="TYPE_C",
      disp_order = 3,
    )
    sub1_1 = SubCompanyFactory.create(
      subName='サブ名001', 
      company_id=company1, 
      sub_company_type=type_c
    )
    sub1_2 = SubCompanyFactory.create(
      subName='サブ名002', 
      company_id=company1,
      sub_company_type=type_b
    )
    sub1_3 = SubCompanyFactory.create(
      subName='サブ名003',
      company_id=company1,
      sub_company_type=type_a
    )
    sub2_1 = SubCompanyFactory.create(
      subName='002サブ名001',
      company_id=company2,
      sub_company_type=type_b
      )
    sub2_2 = SubCompanyFactory.create(
      subName='002サブ名002',
      company_id=company2,
      sub_company_type=type_c
    )
    

    
  def test_01(self, create_data_01):
    '''
    Company, SubCompany
    親データからの外部結合の確認

    prefetch_relatedを使うとSQL文が二つに軽減される。
    二つのSQLは、Python側で結合処理が入るので 2つ目のSQLのINNER JOINは無駄である。
    原因は、subcompany_setをrelatedで指定しているため。
    
    SELECT "myall_company"."id", "myall_company"."name" FROM "myall_company"; args=() (/usr/local/lib/python3.8/site-packages/django/db/backends/utils.py:125)
    SELECT "myall_subcompany"."id", "myall_subcompany"."subName", "myall_subcompany"."company_id_id", "myall_company"."id", "myall_company"."name" 
      FROM "myall_subcompany" 
      INNER JOIN "myall_company" ON 
      ("myall_subcompany"."company_id_id" = "myall_company"."id") WHERE "myall_subcompany"."company_id_id" IN (1, 2, 3, 4); args=(1, 2, 3, 4) (/usr/local/lib/python3.8/site-packages/django/db/backends/utils.py:125)
    '''
    
    result = Company.objects.all().prefetch_related(
      Prefetch(
        'subcompany_set', 
        queryset=SubCompany.objects.select_related('company_id'),
        to_attr='SubCompanyList')
    )
    print(type(result))
    for r in result:
      print(f'{r.id}:{r.name}')
      print(f'     sub count={len(r.SubCompanyList)}')
      for subCompany in r.SubCompanyList:
        print(f'     {subCompany.subName}')

    #self.output()


  def test_02(self, create_data_01):
    '''
    Company, SubCompany
    親データからの外部結合の確認
    
    prefetch_relatedを使うとSQL文が二つに軽減される
    test_01とは同じ結果となる。
    
    prefetch_relatedを、subcompany_set のリレーションを指定しているだけのため無駄な
    INNER JOINは存在していない。    
    
    SQL結果
    SELECT "myall_company"."id", "myall_company"."name" FROM "myall_company"; args=() (/usr/local/lib/python3.8/site-packages/django/db/backends/utils.py:125)
    SELECT "myall_subcompany"."id", "myall_subcompany"."subName", "myall_subcompany"."company_id_id" FROM "myall_subcompany" WHERE "myall_subcompany"."company_id_id" IN (1, 2, 3, 4); args=(1, 2, 3, 4) (/usr/local/lib/python3.8/site-packages/django/db/backends/utils.py:125)
    '''
    CompanyFactory.create(name='Test株式会社 サブなし')
    company = CompanyFactory.create(name='Test株式会社001')
    sub = SubCompanyFactory.create(subName='サブ名001', company_id=company)
    sub = SubCompanyFactory.create(subName='サブ名002', company_id=company)
    result = Company.objects.all().prefetch_related("subcompany_set")
    print(type(result))
    for r in result:
      print(f'{r.id}:{r.name}')
      #print(f'{r.subcompany_set}')
      print(f'     sub count={len(r.subcompany_set.all())}')
      for subCompany in r.subcompany_set.all():
        print(f'     {subCompany.subName}')


  def test_03(self, create_data_01):
    '''
    このやり方がマニュアル通りなのだがなぜか
    condition の条件がSQLに含まれていない。。
    '''
    result = Company.objects.annotate(
      subcompany_set=FilteredRelation(
        'subcompany', condition=Q(subcompany__subName__contains='001'),
      )
    ).values(
      'name', 'subcompany__id'
    )
    print(f'count{len(result)}')
    for r in result:
      print(r["name"])

  def test_04(self, create_data_01):
    '''
    INNER JOIN or LEFT OUTER JOINのやりかた
    - filterで名前を指定しているからSQLは INNER JOINになっている
    - test_03のやり方がマニュアル通りなのだがなぜか
      condition の条件がSQLに含まれていないので、Filterでカバー
    - 戻り値の方はCompanyとなってしまい、対象の子レコードのアクセスができなくなるため、
      valuesで値を指定する。
    '''
    result = Company.objects.annotate(
      subcompany_set=FilteredRelation(
        'subcompany', condition=Q(subcompany__subName='001')
      )
    ).filter(
      subcompany__subName__contains='001'
    ).values(
      'name', 'subcompany__subName'
    )
    print(f'count{len(result)}')
    for r in result:
      print(r["name"])
      print(r["subcompany__subName"])

  def test_05(self, create_data_01):
    '''
    INNER JOIN or LEFT OUTER JOINのやりかた
    - filter指定していないからSQLは LEFT OUTER JOINになっている
    - test_03のやり方がマニュアル通りなのだがなぜか
      condition の条件がSQLに含まれていない(親から子だから無視されている？)
    - 戻り値の方はCompanyとなってしまい、対象の子レコードのアクセスができなくなるため、
      valuesで値を指定する。
    '''
    print('test_05')
    result = Company.objects.annotate(
      subcompany_set=FilteredRelation(
        'subcompany', condition=Q(subcompany__id__isnull=True)
      )
      ).filter(
        subcompany__id__isnull=True
    ).values(
      'name', 'subcompany__subName'
    )
    print(f'count{len(result)}')
    for r in result:
      print(r["name"])
      print(r["subcompany__subName"])


  def test_06(self, create_data_02):
    '''
    Companyは全レコードを抽出
    SubCompanyは紐づくレコードがあれば出力
    出力順序は、Company.id, SubCompanyType.disp_order
    '''
    print('test06------------')
    result = Company.objects.all().prefetch_related(
      Prefetch(
        "subcompany_set",
        queryset=SubCompany.objects.select_related(
          "sub_company_type"
        ).order_by(
          "sub_company_type__disp_order"
        )
      )
    ).order_by('id')
      
    print(type(result))
    for r in result:
      print(f'[{r.id}]:[{r.name}]')
      #print(f'{type(r.subcompany_set)}')
      for subcompany in r.subcompany_set.all():
        print(f'\tsubcompany.subName=[{subcompany.subName}]')
        print(f'\ttype_name=[{subcompany.sub_company_type.type_name}]')
        print(f'\tdisp_order=[{subcompany.sub_company_type.disp_order}]')

  def test_07(self, create_data_02):
    '''
    disp_order が最小のレコードを抽出している。
    但しSubCompanyが主なためSubComapnyレコードが存在しないレコードは抽出していない。
    '''
    print('test07------------')
    result = SubCompany.objects.values(
      "company_id__id"
    ).annotate(
        min_order=Min('sub_company_type__disp_order')
    )
    for r in result:
      print('-----------')
      print(r)

    self.output()
  

  def test_09(self, create_data_02):
    '''
    下記の様な構成で、Company から SubCompany を
    LEFT JOIN してCompany単位でGroup byし 最小のdisp_orderのデータを取得
    Company --------> SubCompany
    SubCompanyType ->
    '''
    print('test08------------')
    result = Company.objects.prefetch_related(
      "subcompany_set"
      ).values(
        "id", "name"
      ).annotate(
        subcompany_min = Min("subcompany__sub_company_type__disp_order")
      )
    print(result)
    result2 = result.filter(name="Test株式会社001")    
    for r in result2:
      print(r["name"])
      print(r["subcompany_min"])
    
    Qobj = Q()
    for r in result:
      Qobj.add(Q(company_id=r["id"], sub_company_type__disp_order=r["subcompany_min"]), Q.OR)
    
    qobj_subcompanys = SubCompany.objects.filter(Qobj).distinct()
    for qobj_subcompany in qobj_subcompanys:
      print(f'company={qobj_subcompany.company_id.name} '
        f'subName={qobj_subcompany.subName}, '
        f'disp_order=[{qobj_subcompany.sub_company_type.disp_order}]')
  
  def test_10(self, create_data_02):
    '''
    件数取得
    annotateは、グループ単位の集計となる。
    '''
    print('test10------------')
    result = Company.objects.prefetch_related(
      "subcompany_set"
      ).values(
        "id", "name"
      ).annotate(
        subcompany_min = Count("subcompany__sub_company_type")
      )
    print(result)
    
  def test_11(self, create_data_02):
    '''
    CompanyでLEFT OUTER JOINとして、SubCompanyType.disp_orderが最小値の
    SubCompanyデータを取得する
    但し。select_relatedがうまく行っておらず、subcompanyのselectが毎レコードで発行されている
    
    Qでデータレコード分 絞込条件が増えてしまうので業務で使うのであればちょっとSQL文が長すぎて微妙かも
    '''
    result = Company.objects.prefetch_related(
        "subcompany_set"
        ).values(
          "id", "name"
        ).annotate(
          subcompany_min = Min("subcompany__sub_company_type__disp_order")
        )

    Qobj = Q()
    for r in result:
      Qobj.add(Q(subcompany__id=r["id"], subcompany__sub_company_type__disp_order=r["subcompany_min"]), Q.OR)

    result2 = Company.objects.annotate(
      subcompany_set=FilteredRelation(
        'subcompany', condition=Qobj
      )
    ).order_by('id')

    for r in result2:
        print(f'name={r.name}')
        for sub in r.subcompany_set.all():
            print(f'    {sub.subName}')
            print(f'       type_name={sub.sub_company_type.type_name}')
            print(f'       disp_order={sub.sub_company_type.disp_order}')

    
  def test_12(self, create_data_02):
    '''
    Companyは全レコードを抽出
    SubCompanyは紐づくレコードでSubCompanyType.disp_orderが一番小さいレコードのみ抽出
    出力順序は、Company.id
    '''
    result = Company.objects.prefetch_related(
      "subcompany_set"
    ).values(
      "id", "name"
    ).annotate(
      subcompany_min = Min("subcompany__sub_company_type__disp_order")
    )
    
    SubQobj = Q()
    for r in result:
        SubQobj.add(
          Q(id=r["id"],sub_company_type__disp_order=r["subcompany_min"]), Q.OR)

    result2 = Company.objects.prefetch_related(
        Prefetch(
          "subcompany_set",
          queryset=SubCompany.objects.filter(
            SubQobj
          ).select_related(
            'sub_company_type'
          )
      )
    ).order_by(
      'id'
    )

    for r in result2:
      print(f'[{r.id}]:[{r.name}]')
      for sub in r.subcompany_set.all():
        print(f'\t{sub.subName}')
        print(f'\ttype_name={sub.sub_company_type.type_name}')
        print(f'\tdisp_order={sub.sub_company_type.disp_order}')


    #print(result.query)    
    #print(result2.query)
    #
    # https://teratail.com/questions/28omlbvgodothz
    #  OuterRef, Subquery
    #　これで解決するかも？
    # 
    #result = result.all().annotate(
    #  subdata = qobj_subcompanys
    #)
    #print(result)
      
    #names = list(map(lambda x: x["name"], result))
    #result = Company.objects.filter(name__in=names)    
    #print(type(result))
    #print(result)
    #for r in result:
    #  print(r)

  def output(self):
    '''
    Output DBDATA to JSONファイル

    '''
    out_file_name = "output/export_test_company_data.json"
    params = [
      "dumpdata"
      ,"--indent"
      ,"4"
      ,"-o"
      ,out_file_name
      ,"myall"
    ]
    call_command(*params)
