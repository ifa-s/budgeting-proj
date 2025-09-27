from django.urls import path
from . import views
from . import debug_views
from . import simple_views

app_name = 'pdf_analyzer'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('process/<uuid:upload_id>/', views.process_pdf, name='process_pdf'),
    path('status/<uuid:upload_id>/', views.analysis_status, name='analysis_status'),
    path('results/<uuid:upload_id>/', views.analysis_results, name='analysis_results'),
    path('delete/<uuid:upload_id>/', views.delete_upload, name='delete_upload'),
    
    # API endpoints
    path('api/status/<uuid:upload_id>/', views.get_analysis_status, name='api_status'),
    path('api/transactions/<uuid:upload_id>/', views.transaction_list, name='api_transactions'),
    
    # Debug endpoints
    path('debug/', debug_views.debug_page, name='debug_page'),
    path('debug/upload/', debug_views.debug_pdf_upload, name='debug_upload'),
    
    # Fallback endpoints
    path('simple-process/<uuid:upload_id>/', simple_views.simple_process_pdf, name='simple_process'),
]