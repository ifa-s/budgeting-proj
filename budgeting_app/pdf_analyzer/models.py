from django.db import models
from django.core.validators import FileExtensionValidator
import uuid


class PDFUpload(models.Model):
    """Model to store uploaded PDF bank statements"""
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(
        upload_to='pdf_uploads/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.status}"


class Transaction(models.Model):
    """Model to store individual transactions extracted from PDFs"""
    
    TRANSACTION_TYPES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('fee', 'Fee'),
        ('interest', 'Interest'),
    ]
    
    pdf_upload = models.ForeignKey(PDFUpload, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100, blank=True)  # AI-determined category
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.description[:50]} - ${self.amount}"


class AIAnalysis(models.Model):
    """Model to store AI-generated analysis and feedback"""
    
    pdf_upload = models.OneToOneField(PDFUpload, on_delete=models.CASCADE, related_name='analysis')
    
    # Summary statistics
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # AI-generated insights
    spending_patterns = models.JSONField(default=dict)  # Category breakdowns, trends
    budgeting_recommendations = models.TextField()
    financial_insights = models.TextField()
    risk_assessment = models.TextField(blank=True)
    
    # Metadata
    analyzed_at = models.DateTimeField(auto_now_add=True)
    gemini_model_used = models.CharField(max_length=100, default='gemini-pro')
    
    def __str__(self):
        return f"Analysis for {self.pdf_upload.file_name}"


class CategorySummary(models.Model):
    """Model to store spending summaries by category"""
    
    analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE, related_name='category_summaries')
    category_name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_count = models.IntegerField()
    percentage_of_expenses = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        unique_together = ['analysis', 'category_name']
    
    def __str__(self):
        return f"{self.category_name}: ${self.total_amount}"
