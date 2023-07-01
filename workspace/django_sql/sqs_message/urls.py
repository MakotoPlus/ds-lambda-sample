from django.urls import path, include
from django.conf.urls import url
from . import views

app_name = 'sqs_message'

urlpatterns = [
  path('', views.MessageView.as_view(), name='index'),
]
