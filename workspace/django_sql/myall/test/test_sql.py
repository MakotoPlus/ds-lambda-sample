import pytest
import factory
import logging
from django.db.models import Prefetch
from myall import models
from  myall.test.factory import test_factory
from django.db import connection
from myall import sqllogic

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestSql():
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
  def test_002(self, sqlclear, create_blogtag, tagname, expected):
    records = sqllogic.check_01_select_related(tagname)
    for record in records:
        print("++++++++++++++++")
        for blogTagRecord in record.blogTaglist:
            print(f'tag=[{record.name}],title=[{blogTagRecord.blog.title}]')
            assert blogTagRecord.blog.title in expected
    # Pytestでは出力されないのでコメントアウト
    # print(connection.queries)
    