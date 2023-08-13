'''
Blog, Tag, BlogTag テーブルのテストケース
（中間テーブルを独自作成)
ManyToManyFieldフィールドを使用しない場合
'''
import pytest
import sys
import factory
import logging
from django.core.management import call_command
from django.db.models import Prefetch
from myall import models
from myall.test.factory import test_factory
from django.db import connection
from myall import sqllogic

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestBlogNotRelatedFactory():
  '''
  Factory BoyのRelatedFactoryを使ってる
  なんか使っててもあまり意味無いような・・。
  '''
  def test_001(self):
    print("test001 start")
    t = 1
    assert 1 == t

  def create_blog(self, title, good_point) :
    return test_factory.BlogFactory.create(
      title=title,
      content=f'content {title}',
      good_point=good_point,
    )

  @pytest.fixture
  def create_blogtag(self):
    """Blogは、複数のタグをつける事が可能なため
      以下データを作成
      [Tag]         -- [Blog]
      チェンソーマン -- チェンソーマン
      ガンダム       -- 初代機動戦士ガンダム
                    -- 機動戦士ZZガンダム
      アニメ         -- チェンソーマン
                    -- 初代機動戦士ガンダム
                    -- 機動戦士ZZガンダム
      Succer        -- J1
    """
    blog = self.create_blog('チェンソーマン', 11)
    tagChenson = test_factory.TagFactory.create(name='チェンソーマン')
    tagAnime = test_factory.TagFactory.create(name='アニメ')    
    test_factory.BlogTagFactory(
      blog = blog,
      tag = tagChenson
    )
    test_factory.BlogTagFactory(
      blog = blog,
      tag = tagAnime
    )
    
    blogGamdam_1 = self.create_blog('初代機動戦士ガンダム', 9)
    blogGamdam_2 = self.create_blog('機動戦士ZZガンダム', 5)
    tagGamdam = test_factory.TagFactory.create(name='ガンダム')

    test_factory.BlogTagFactory(
      blog = blogGamdam_1,
      tag = tagGamdam
    )
    test_factory.BlogTagFactory(
      blog = blogGamdam_1,
      tag = tagAnime
    )
    test_factory.BlogTagFactory(
      blog = blogGamdam_2,
      tag = tagGamdam
    )
    test_factory.BlogTagFactory(
      blog = blogGamdam_2,
      tag = tagAnime
    )
    blogSuccer = self.create_blog('J1', 12)
    tagSuccer = test_factory.TagFactory.create(name='Succer')
    test_factory.BlogTagFactory(
      blog = blogSuccer,
      tag = tagSuccer
    )

  @pytest.mark.parametrize(
    "tagname, expected", 
    [
      ('Succer', ['J1']), 
      ('ガンダム', ['初代機動戦士ガンダム', '機動戦士ZZガンダム']), 
      ('チェンソーマン', ['チェンソーマン']), 
      ('アニメ', ['チェンソーマン', '初代機動戦士ガンダム', '機動戦士ZZガンダム']), 
    ]
  )
  def test_002(self, create_blogtag, tagname, expected):
    records = sqllogic.check_01_select_related(tagname)
    for record in records:
        print("++++++++++++++++")
        for blogTagRecord in record.blogTaglist:
            print(f'tag=[{record.name}],title=[{blogTagRecord.blog.title}]')
            assert blogTagRecord.blog.title in expected
    # Pytestでは出力されないのでコメントアウト
    # print(connection.queries)
  
  def test_003(self, create_blogtag):
    '''
    Output DBDATA to JSONファイル

    '''
    #b = call_command('dumpdata')
    #out_file_name = "export_data.json"
    #sys.stdout = open(out_file_name, mode = "w")
    #call_command('dumpdata')
    params = [
      "dumpdata"
      ,"--indent"
      ,"4"
      ,"-o"
      ,"output/20230806_dump_myall.json"
      ,"myall"
    ]
    #call_command(*params)
   
    
@pytest.mark.django_db
class TestBlogRelatedFactory():
  '''
  Factory BoyのRelatedFactoryを使うバージョン
  といってもFactory側に作る必要があるんやけど
  '''
  @pytest.fixture
  def tag_data_01(self):
    #--------------------------------------------------
    # Factoryで生成してあとからデータ内容を変更するパターン
    #--------------------------------------------------
    tag_data = test_factory.TagWithBlogFactory.create(name="チェンソーマン")
    tag_data.tag_tag.all()[0].blog.title = "チェンソーマン"
    for blog_tag in tag_data.tag_tag.all():
      blog_tag.blog.title = "チェンソーマン"
      blog_tag.blog.save()
    return tag_data

  @pytest.fixture
  def tag_data_02(self):
    #--------------------------------------------------
    # 事前にblogデータを生成しておくパターン だけど１データしか作れん・・。
    #--------------------------------------------------
    blog_tag = factory.RelatedFactory(
      test_factory.BlogTagFactory, 
      factory_related_name = 'tag',
      blog__title = "J1"
    )
    tag_data = test_factory.TagWithBlogFactory.create(name="Succer", blog_tag=blog_tag)
    return tag_data

  @pytest.fixture
  def tag_data_03(self):
    #--------------------------------------------------
    # 複数の blogを生成するパターン
    #--------------------------------------------------
    blog_tag = factory.RelatedFactoryList(
      test_factory.BlogTagFactory,
      factory_related_name='tag',
      size=2
    )
    logger.debug("type(blog_tag)--------------")
    logger.debug(type(blog_tag))
    tag_data = test_factory.TagWithBlogListFactory.create(name="ガンダム", blog_tag=blog_tag)
    # 生成した後でTAGの名前変えパターン
    GUMDAMS = ['初代機動戦士ガンダム', '機動戦士ZZガンダム']
    for gumdam, blog_tag in zip(GUMDAMS, tag_data.tag_tag.all()):
      blog_tag.blog.title = gumdam      
      blog_tag.blog.save()
      #logger.debug("type(blog_tag)------")
      #logger.debug(type(blog_tag))
    return tag_data

  @pytest.fixture
  def tag_data_04(self):
    '''
      チェンソーマン、ガンダムタグに紐づく全てのBlogをアニメにも紐づくデータを作成
      -  TagWithBlogListFactoryは、tag : blog = 1 : N のデータを作成しており
      -  N : N のデータを作成できないような・・。
      -  他のサイトでは、Tag, Blogは、Factoryで生成し
      -  中間テーブルは、model直接で生成することで解決していた例
      -  https://djangobrothers.com/blogs/django_manytomany_through/
      -  下記では、中間テーブルをFactoryで生成している
    '''
    # blog 作成
    tag_chenman = test_factory.TagFactory(name="チャンソーマン")
    tag_gandam = test_factory.TagFactory(name="ガンダム")
    tag_anime = test_factory.TagFactory(name="アニメ")
    blog_chanman = test_factory.BlogFactory(title="チャンソーマン")
    blog_gandam = test_factory.BlogFactory(title="初代機動戦士ガンダム")
    blog_zz_gandam = test_factory.BlogFactory(title="機動戦士ZZガンダム")
    
    # FactoryBoyでは解決出来ない？
    datas = [
      [tag_chenman, [blog_chanman]]
      ,[tag_gandam, [blog_gandam, blog_zz_gandam]]
      ,[tag_anime, [blog_chanman, blog_gandam, blog_zz_gandam]]
    ]
    for data in datas:
      tagobj = data[0]
      for blog in data[1]:
        #models.BlogTag.objects.create(tag=tagobj, blog=blog)
        test_factory.BlogTagFactory(tag=tagobj, blog=blog)     
    return (tag_chenman, tag_gandam, tag_anime)
  
  def test_001(self, tag_data_01):
    logger.debug("【test_001】----------------")
    self._output(tag_data_01)

  def test_002(self, tag_data_02):
    logger.debug("【test_002】----------------")
    self._output(tag_data_02)

  def test_003(self, tag_data_03):
    logger.debug("【test_003】----------------")
    self._output(tag_data_03)

  def test_004(self, tag_data_04):
    logger.debug("【test_004】----------------")
    for tag in tag_data_04:
      self._output(tag)

  def _output(self, data):
    logger.debug(f'tag_data id=[{data.pk}] name=[{data.name}]')
    for blog_tag in data.tag_tag.all():
      logger.debug(f'tag id/blog id=[{data.pk}/{blog_tag.blog.pk}] title=[{blog_tag.blog.title}]')
      #logger.debug(f'blog.content=[{blog_tag.blog.content}]')
      #logger.debug(f'blog.good_point=[{blog_tag.blog.good_point}]')
