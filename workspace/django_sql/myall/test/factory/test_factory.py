import factory
from factory.django import DjangoModelFactory
from myall import models

class TagFactory(DjangoModelFactory):
  class Meta:
    model = models.Tag
    django_get_or_create = ('name',)  

class BlogFactory(DjangoModelFactory):
  class Meta:
    model = models.Blog

class BlogTagFactory(DjangoModelFactory):
  class Meta:
    model = models.BlogTag
