from django.contrib import admin
from .models import PDFUpload, Transaction, AIAnalysis, CategorySummary


@admin.register(PDFUpload)
class PDFUploadAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'status', 'uploaded_at', 'file_size']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['file_name']
    readonly_fields = ['id', 'uploaded_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'amount', 'transaction_type', 'category', 'pdf_upload']
    list_filter = ['transaction_type', 'category', 'date']
    search_fields = ['description']
    date_hierarchy = 'date'


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['pdf_upload', 'total_income', 'total_expenses', 'net_change', 'analyzed_at']
    list_filter = ['analyzed_at', 'gemini_model_used']
    readonly_fields = ['analyzed_at']


@admin.register(CategorySummary)
class CategorySummaryAdmin(admin.ModelAdmin):
    list_display = ['analysis', 'category_name', 'total_amount', 'transaction_count', 'percentage_of_expenses']
    list_filter = ['category_name']
