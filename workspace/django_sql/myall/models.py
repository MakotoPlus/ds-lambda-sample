from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Blog(models.Model):
    title = models.CharField(max_length=10)
    content = models.CharField(max_length=40)
    good_point = models.IntegerField(default=0)
    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class BlogTag(models.Model):
    blog = models.ForeignKey(Blog, related_name="tag_blog", on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name="tag_tag", on_delete=models.CASCADE)

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
