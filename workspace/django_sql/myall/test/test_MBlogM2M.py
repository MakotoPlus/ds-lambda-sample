#
# BlogFactory / BlogTagFactory
#
# ManyToManyField 用サンプル
#
import pytest
import factory
import logging
from django.core.management import call_command
from myall.test.factory.test_factory import (
  MtagFactory
  ,MBlogTagFactory
)

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestMBlogM2M():
  @pytest.mark.parametrize(
    "caseno, is_client",
    [
      ("001", False),
      ("002", True)
    ]
  )
  def test_001(self, caseno, is_client):
    logger.debug(f'caseno=[{caseno}]')
    mtags = MtagFactory.create_batch(5)
    if is_client:
      mblog = MBlogTagFactory.create(tags=mtags)
    else:
      mblog = MBlogTagFactory.build(tags=mtags)
    #print(mblog)

    # Mblogの情報表示
    logger.debug(f'mblog.title=[{mblog.title}]')
    logger.debug(f'mblog.content=[{mblog.content}]')
    
    # MBTagの情報表示 (型:ManyRelatedManager)
    # buildでは、mblog.tagsはアクセスすると例外が発生するので注意
    if is_client:
      logger.debug(f'mblog.tags is not None')
      mbtags = mblog.tags.all()
      for mtag in mbtags:
        logger.debug(f'mblog.tags.name=[{mtag.name}]')
      # JSON Output
      self.output_data()

    else:
      logger.debug(f'mblog.tags is None')

  def output_data(self):
    '''
    Output DBDATA to JSONファイル

    '''
    params = [
      "dumpdata"
      ,"--indent"
      ,"4"
      ,"-o"
      ,"output/20230806_dump_blogM2M.json"
      ,"myall"
    ]
    call_command(*params)
