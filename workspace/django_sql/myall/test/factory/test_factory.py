import factory
from factory.django import DjangoModelFactory
from myall import models
from faker import Faker

fake = Faker('ja-JP')

class BlogFactory(DjangoModelFactory):
  class Meta:
    model = models.Blog
  title = factory.Sequence(lambda n: "Title #%s" % n)
  content = factory.Sequence(lambda n: "Content-#%s" % n)
  good_point = factory.Sequence(lambda n: n)

class TagFactory(DjangoModelFactory):
  class Meta:
    model = models.Tag
  name = factory.Sequence(lambda n: "TAG-Name-%s" % n)

class BlogTagFactory(DjangoModelFactory):
  class Meta:
    model = models.BlogTag
  blog = factory.SubFactory(BlogFactory)
  tag = factory.SubFactory(TagFactory)

class TagWithBlogFactory(TagFactory):
  blog_tag = factory.RelatedFactory(
    BlogTagFactory,
    factory_related_name = 'tag'
  )

class TagWithBlogListFactory(TagFactory):
  blog_tag = factory.RelatedFactoryList(
    BlogTagFactory,
    factory_related_name = 'tag',
    size=1
  )
  

class MtagFactory(DjangoModelFactory):
  class Meta:
    model = models.MTag
  name = factory.Sequence(lambda n: f'{fake.name()}({n+1})')
  #name = fake.name()

class MBlogTagFactory(DjangoModelFactory):
  class Meta:
    model = models.MBlog

  title = fake.name()
  content = factory.LazyAttribute(lambda o: f'content_{o.title}')
  good_point = fake.random_number(fix_len=True, digits=10)


  @factory.post_generation
  def tags(self, create, extracted, **kwargs):
    if not create:
      return
    if extracted:
      for mtag in extracted:
        self.tags.add(mtag)

class M2MSimple_PublicationFactory(DjangoModelFactory):
  title = factory.Sequence(lambda n: "Title #%s" % n)
  class Meta:
    model = models.Publication

#
# Meny to Meny テーブルを同時に生成するFactory
class M2MSimple_AuthorFactory(factory.django.DjangoModelFactory):
  headline = 'm2m_simple_headline'
  
  class Meta:
    model = models.Author
      
  @factory.post_generation
  def publications(self, create, extracted, **kwargs):
    if not create:
      # Simple build, do nothing.
      return

    if extracted:
      for publication in extracted:
        self.publications.add(publication)

class AuthorFactory002(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Author
    rename = {'form_attributes': 'headline'}
    
class AuthorFactory003(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Author

  headline = 'headlineheadline'
  @classmethod
  def generate(cls, strategy, **kwargs):
    print(f'strategy=[{strategy}]')
    if strategy == factory.CREATE_STRATEGY:
      print(f'TagFactory........create')
      return TagFactory.create(name='test', **kwargs)
    return super().generate(strategy, kwargs)

class LienyPayTraitFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.LinePay
  value = 1
  use_name = 'name'
  lineid = 'iiid'
  
  class Params:
    data = factory.Trait(
        use_name='shipped',
        value=100,
        lineid='123',
    )


class CompanyFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.Company
  name = "company"

class SubCompany2TraitFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = models.SubCompany
  subName = "SubCompany"
  #company_id = factory.SubFactory(CompanyFactory)

  class Params:
    parent_company = factory.Trait(
      subName = fake.text(),
      company_id = factory.SubFactory(CompanyFactory)
    )


