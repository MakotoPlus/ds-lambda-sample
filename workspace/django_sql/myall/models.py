from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

#
# 中間モデルを作成
# ManyToManyFieldで中間テーブルを指定
#
class Blog(models.Model):
    title = models.CharField(max_length=10)
    content = models.CharField(max_length=40)
    good_point = models.IntegerField(default=0)
    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=10)
    blog_tags = models.ManyToManyField(Blog, through="BlogTag")
    def __str__(self):
        return self.name

class BlogTag(models.Model):
    blog = models.ForeignKey(Blog, related_name="tag_blog", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name="tag_tag", on_delete=models.CASCADE)
    create_date = models.DateTimeField(null=True)
    class Meta:
        unique_together = ('blog', 'tag',)

    def __str__(self):
        return "{}:<{}>".format(self.blog.title, self.tag.name)


class MTag(models.Model):
    name = models.CharField(max_length=10)
    class Meta:
        db_table = 'M_Tag'
        verbose_name = 'M_Tag'
        verbose_name_plural = 'M_Tag'
        unique_together = ('name',)

    def __str__(self):
        return self.name


class MBlog(models.Model):
    title = models.CharField(max_length=10)
    content = models.CharField(max_length=40)
    good_point = models.IntegerField(default=0)
    tags = models.ManyToManyField(MTag, related_name="tags_mtag", blank=True)
    class Meta:
        db_table = 'M_Blog'
        verbose_name = 'M_Blog'
        verbose_name_plural = 'M_Blog'
        unique_together = ('title',)

    def __str__(self):
        return self.title


class GenericAdjustment(models.Model):
    '''Generic精算情報'''
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.tag
    class Meta:
        db_table = 'GENERIC_ADJUSTMENT'
        verbose_name = '汎用精算'
        verbose_name_plural = '汎用精算'
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class PayPay(models.Model):
    def __str__(self):
        return self.use_name
    class Meta:
        db_table = 'GENERIC_ADJUSTMENT_PAYPAY'
        verbose_name = 'PAYPAY'
        verbose_name_plural = 'PAYPAY'
    value = models.IntegerField(default=0, verbose_name="利用額")
    use_name = models.CharField(max_length=30, verbose_name="利用者")
    tags = GenericRelation(GenericAdjustment)


class LinePay(models.Model):
    def __str__(self):
        return self.use_name
    class Meta:
        db_table = 'GENERIC_ADJUSTMENT_LINEPAY'
        verbose_name = 'LINEPAY'
        verbose_name_plural = 'LINEPAY'
    value = models.IntegerField(default=0, verbose_name="利用額")
    use_name = models.CharField(max_length=30, verbose_name="利用者")
    lineid = models.CharField(max_length=30, verbose_name="Lineid")
    tags = GenericRelation(GenericAdjustment)

class Publication(models.Model):
    title = models.CharField(max_length=30)
    
class Author(models.Model):
    headline = models.CharField(max_length=100)
    publications = models.ManyToManyField(Publication)    

class SubCompanyType(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=40)
    disp_order = models.IntegerField(verbose_name="表示順序")
    class Meta:
        db_table = 'sub_company_type'
        verbose_name = 'サブ店舗タイプ'

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)    

class SubCompany(models.Model):
    id = models.AutoField(primary_key=True)
    subName =models.CharField(max_length=100)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    sub_company_type = models.ForeignKey(SubCompanyType, null=True, on_delete=models.CASCADE)


class Person(models.Model):
    name            = models.CharField(max_length=128)
    def __str__(self):
        return self.name

class Group(models.Model):
    name            = models.CharField(max_length=128)
    members         = models.ManyToManyField(Person, through='Membership', through_fields=('group', 'person'), )
    def __str__(self):
        return self.name

class Membership(models.Model):
    person          = models.ForeignKey(Person, on_delete=models.CASCADE)
    group           = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined     = models.DateField()
    invite_reason   = models.CharField(max_length=64)
