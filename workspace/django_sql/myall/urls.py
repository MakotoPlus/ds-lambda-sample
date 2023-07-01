from django.urls import path, include
from django.conf.urls import url
from . import views

app_name = 'myall'

urlpatterns = [
  path('many2many/', views.ManyToManyListView.as_view(), name='many2many'),
  path('mbloglist/<int:pk>', views.MBlogListView.as_view(), name='mbloglist'),
  path('adjustlist/paypay/', views.PayPayView.as_view(), name='adjustlist_paypay'),
  path('adjustlist/line/', views.LineView.as_view(), name='adjustlist_line'),
  path('adjust/datail/<int:pk>', views.AdjustDetailView.as_view(), name='adjust_detail'),
  path('adjustlist/', views.AdjustListView.as_view(), name='adjustlist'),
  path('sqs_message/', include('sqs_message.urls')),
  path('', views.index, name='index'),
]
