#
# BlogFactory / BlogTagFactory
#
# ManyToManyField:through あり用サンプル
#
import pytest
import factory
import logging
from django.core.management import call_command
from myall.test.factory.personFactory import (
  PersonWithGroupFactory
  ,PersonWithGroupListFactory
  ,MembershipFactory
  ,GroupFactory
  ,PersonFactory
)
from myall import models
logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestPersonM2M():
  def test_001(self):
    '''
    PersonWithGroupFactoryを作って見る
    
    Objectは、Personオブジェクトが返って来るのでリレーションを使ってアクセスすると
    Membership, Groupも出来ている
    '''
    person = PersonWithGroupFactory.create()
    self.__deta_output(person)
    
  def test_002_PersonWithGroupListFactory(self):
    '''
    person : group = 1 : N データ作成
    '''
    membership = factory.RelatedFactoryList(
      MembershipFactory,
      factory_related_name='person',
      size=30
    )
    person = PersonWithGroupListFactory.create(membership=membership)
    logger.debug(type(person)) # myall.models.Person
    self.__deta_output(person)

  def test_003_N_N_Data(self):
    '''
    person : group = N : N データ作成
    Factoryは利用するが、紐づけのテーブルはmodel直接生成
    '''
    persons = PersonFactory.create_batch(size=10)
    groups = GroupFactory.create_batch(size=10)
    for person in persons:
      for group in groups:
        MembershipFactory(person=person, group=group)
      self.__deta_output(person)

  def __deta_output(self, person):
    logger.debug(f'person pk={person.pk} name={person.name}')
    # personからだからリレーションを使ってall()で取得
    for index, membership_obj in enumerate(person.membership_set.all()):
      logger.debug(f'[{person.pk}]-[{membership_obj.group.pk}] membership_obj.group.name={membership_obj.group.name}')
      logger.debug(f'[{person.pk}]-[{membership_obj.group.pk}] membership_obj.date_joined={membership_obj.date_joined}')
      logger.debug(f'[{person.pk}]-[{membership_obj.group.pk}] membership_obj.invite_reason={membership_obj.invite_reason}')
