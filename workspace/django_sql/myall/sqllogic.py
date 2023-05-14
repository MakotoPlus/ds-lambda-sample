import logging
from django.db.models import Prefetch
from myall import models
from myall.test.factory import test_factory
from django.db import connection
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)

def check_01_select_related(tag_name : str) -> QuerySet:
  #
  # tag.name = アニメのBlogデータを取得する
  # この場合は Tag -> BlogTagとなるが 子から親のため select_relatedは利用出来ない
  #
  # prefetch_relatedを利用する
  # Prefetch( XXXX, queryset, to_attr=attrlist) 
  # xxxx は、releted_nameを指定すれば逆参照も可能。
  # modelにreleted_nameが定義されている場合は正しく指定しないとエラーになる
  # attrlistは、アクセスする際の名前となる。
  #
  #
  # https://just-python.com/document/django/orm-query/select_related-prefetch_related
  return models.Tag.objects.filter(
        name=tag_name
      ).prefetch_related(
        Prefetch(
          'tag_tag',
          queryset=models.BlogTag.objects.select_related('blog'),
          to_attr='blogTaglist'
        )
      )
