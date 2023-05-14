
### 概要

1. modelは、DjangoのチュートリアルのモデルBlog, Tag, BlogTagとしている
1. Blog：Tagは、N 対 N の関係である。
1. 紐づけテーブルはBlogTabとなる

### ManyToMany
1. MBlog, MTagは ManyToManyのサンプルプログラムである
   参考サイト：https://www.northtorch.co.jp/archives/1151

### PositiveIntegerField, GenericRelation
1. PositiveIntegerField, GenericRelationの構成サンプルプログラム
   参考サイト：https://docs.djangoproject.com/ja/4.2/ref/contrib/contenttypes/
   参考サイト：https://blog.narito.ninja/detail/34