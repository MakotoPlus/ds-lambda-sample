
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

### CICDについて
- Docker
  - conservice.yml
    - Django, Nginxを別々のサービスとして起動させて通信させるバージョン
      - 動かなくなっている。原因はnginxの.confだと思うが修正方法が分からず
      - Django, Nginxを別々のサービスで動かす需要が無さそうなので放置
  - conservice-single.yml
    - Django, Nginxを同一サービスで同一タスク定義内で起動させて通信させるバージョン