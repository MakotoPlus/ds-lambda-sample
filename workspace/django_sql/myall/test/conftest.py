import pytest
import factory
#from rest_framework.test import APIClient
#from rest_framework.test import APIRequestFactory
from django.db import reset_queries

'''
@pytest.fixture(scope='function')
def fixtureUser():
  print("fixtureUser")
  return UserFactory()

@pytest.fixture
def fixtureClient():
  return APIClient()
'''

# 意味ない
# @pytest.fixture(scope='function')
#def sqlclear():
#  reset_queries()
