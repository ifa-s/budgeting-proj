from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start_conversation, name='start_conversation'),
    path('send/', views.send_message, name='send_message'),
    path('status/', views.get_status, name='get_status'),
    path('test-bucket/', views.test_bucket_operations, name='test_bucket'),
    path('export/', views.export_budget_data, name='export_budget'),
]
