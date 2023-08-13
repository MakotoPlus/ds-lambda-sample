import factory
import datetime
from factory.django import DjangoModelFactory
from myall import models
from faker import Faker

fake = Faker('ja-JP')
#
# Person, Group, Membership系のFactory
#
class PersonFactory(DjangoModelFactory):
  class Meta:
    model = models.Person
  name = fake.name()
  #name = 'PERSON'

class GroupFactory(DjangoModelFactory):
  class Meta:
    model = models.Group
  #name = fake.name()
  name = factory.Sequence(lambda n: f'{n}-{fake.name()}')

class MembershipFactory(DjangoModelFactory):
  class Meta:
    model = models.Membership
  person = factory.SubFactory(PersonFactory)
  group = factory.SubFactory(GroupFactory)
  date_joined = datetime.date.today()
  invite_reason = 1

class PersonWithGroupFactory(PersonFactory):
  membership = factory.RelatedFactory(
    MembershipFactory,
    factory_related_name='person'
  )
  
class PersonWithGroupListFactory(PersonFactory):
  membership = factory.RelatedFactoryList(
    MembershipFactory,
    factory_related_name='person',
    size=1
  )
  