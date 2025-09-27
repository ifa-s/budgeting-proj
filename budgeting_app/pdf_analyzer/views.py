import json
import logging
import traceback
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import default_storage
from django.conf import settings
from decimal import Decimal

from .models import PDFUpload, Transaction, AIAnalysis, CategorySummary
from .services import PDFProcessor
from .ai_service import GeminiAnalyzer, StudentBudgetAnalyzer

logger = logging.getLogger(__name__)


def index(request):
    """Main page for PDF analyzer with upload form and recent uploads"""
    recent_uploads = PDFUpload.objects.all()[:10]
    
    context = {
        'recent_uploads': recent_uploads,
        'max_file_size_mb': 10,  # 10MB limit
    }
    return render(request, 'pdf_analyzer/index.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def upload_pdf(request):
    """Handle PDF file upload and initiate processing"""
    try:
        if 'pdf_file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['pdf_file']
        
        # Validate file
        if not uploaded_file.name.lower().endswith('.pdf'):
            return JsonResponse({'error': 'Only PDF files are allowed'}, status=400)
        
        # Check file size (10MB limit)
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse({'error': 'File size must be less than 10MB'}, status=400)
        
        # Create PDFUpload record
        pdf_upload = PDFUpload.objects.create(
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,
            status='uploaded'
        )
        
        # Automatically start processing using new Gemini-powered approach
        try:
            # Update status to processing
            pdf_upload.status = 'processing'
            pdf_upload.save()
            
            # Process the PDF using new approach - let Gemini handle everything
            processor = PDFProcessor()
            analyzer = GeminiAnalyzer()
            
            # Extract complete PDF content for Gemini analysis
            logger.info(f"Extracting complete PDF content for upload {pdf_upload.id}")
            with pdf_upload.file.open('rb') as pdf_file:
                pdf_content = processor.extract_complete_pdf_content(pdf_file)
            
            logger.info(f"PDF content extracted - Text length: {len(pdf_content.get('raw_text', ''))}, Tables: {len(pdf_content.get('structured_tables', []))}")
            logger.info(f"PDF formatted content preview: {pdf_content.get('formatted_content', '')[:200]}...")
            
            # Let Gemini analyze the complete content and extract transactions
            logger.info("Starting Gemini AI analysis of PDF content")
            logger.info("Sending PDF content to Gemini for analysis...")
            analysis_result = analyzer.analyze_pdf_content(pdf_content)
            
            logger.info(f"Gemini analysis complete - Found {len(analysis_result.get('transactions', []))} transactions")
            
            # Create Transaction records from Gemini's analysis
            transactions_data = []
            for trans_data in analysis_result.get('transactions', []):
                try:
                    transaction = Transaction.objects.create(
                        pdf_upload=pdf_upload,
                        date=trans_data['date'],
                        description=trans_data['description'],
                        amount=trans_data['amount'],
                        category=trans_data['category'],
                        transaction_type=trans_data['transaction_type']
                    )
                    transactions_data.append({
                        'date': trans_data['date'],
                        'description': trans_data['description'],
                        'amount': float(trans_data['amount']),
                        'category': trans_data['category'],
                        'transaction_type': trans_data['transaction_type']
                    })
                except Exception as trans_error:
                    logger.warning(f"Could not create transaction: {str(trans_error)}")
                    continue
            
            # Use financial summary from Gemini or calculate from transactions
            financial_summary = analysis_result.get('financial_summary', {})
            
            if financial_summary and 'total_income' in financial_summary:
                total_income = Decimal(str(financial_summary['total_income']))
                total_expenses = Decimal(str(financial_summary['total_expenses']))
                net_change = Decimal(str(financial_summary['net_change']))
            else:
                # Fallback calculation if Gemini didn't provide summary
                total_income = sum(Decimal(str(t['amount'])) for t in transactions_data if float(t['amount']) > 0)
                total_expenses = abs(sum(Decimal(str(t['amount'])) for t in transactions_data if float(t['amount']) < 0))
                net_change = total_income - total_expenses
            
            # Create AI Analysis record with Gemini's insights
            ai_analysis = AIAnalysis.objects.create(
                pdf_upload=pdf_upload,
                total_income=total_income,
                total_expenses=total_expenses,
                net_change=net_change,
                spending_patterns=json.dumps(analysis_result.get('spending_patterns', {})),
                budgeting_recommendations=analysis_result.get('budgeting_recommendations', ''),
                financial_insights=analysis_result.get('financial_insights', ''),
                risk_assessment=analysis_result.get('risk_assessment', ''),
                gemini_model_used='gemini-2.5-flash'
            )
            
            # Create category summaries from Gemini's analysis
            category_breakdown = analysis_result.get('category_breakdown', {})
            for category_name, category_data in category_breakdown.items():
                try:
                    CategorySummary.objects.create(
                        analysis=ai_analysis,
                        category_name=category_name,
                        total_amount=Decimal(str(category_data.get('total', 0))),
                        transaction_count=category_data.get('count', 0),
                        percentage_of_expenses=Decimal(str(category_data.get('percentage', 0)))
                    )
                except Exception as cat_error:
                    logger.warning(f"Could not create category summary for {category_name}: {str(cat_error)}")
                    continue
            
            # Update status to completed
            pdf_upload.status = 'completed'
            pdf_upload.save()
            
            logger.info(f"Processing completed successfully for upload {pdf_upload.id}")
            
            # Return success response directing to results
            return JsonResponse({
                'success': True,
                'upload_id': str(pdf_upload.id),
                'file_name': pdf_upload.file_name,
                'status': 'completed',
                'redirect_url': reverse('pdf_analyzer:analysis_results', args=[pdf_upload.id])
            })
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_upload.id}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            pdf_upload.status = 'failed'
            pdf_upload.save()
            
            return JsonResponse({
                'success': True,
                'upload_id': str(pdf_upload.id),
                'file_name': pdf_upload.file_name,
                'status': 'processing',  # Show processing status initially
                'redirect_url': reverse('pdf_analyzer:analysis_status', args=[pdf_upload.id])
            })
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return JsonResponse({'error': 'Upload failed. Please try again.'}, status=500)


def process_pdf(request, upload_id):
    """Process the uploaded PDF and extract transactions"""
    pdf_upload = get_object_or_404(PDFUpload, id=upload_id)
    
    if pdf_upload.status != 'uploaded':
        messages.warning(request, 'This PDF has already been processed or is currently being processed.')
        return redirect('pdf_analyzer:analysis_results', upload_id=upload_id)
    
    try:
        # Update status to processing
        pdf_upload.status = 'processing'
        pdf_upload.save()
        logger.info(f"Processing PDF upload {upload_id}")
        
        # Process the PDF
        processor = PDFProcessor()
        
        # Extract structured data from PDF (both text and tables)
        try:
            with pdf_upload.file.open('rb') as pdf_file:
                logger.info("Extracting structured data from PDF")
                structured_data = processor.extract_structured_data(pdf_file)
                logger.info(f"Extracted text length: {len(structured_data.get('text', ''))}")
                logger.info(f"Number of tables found: {len(structured_data.get('tables', []))}")
        except Exception as e:
            logger.error(f"Error extracting data from PDF: {str(e)}")
            raise
        
        # Parse transactions from both text and tables for better coverage
        transactions_data = []
        
        # Try parsing from text first
        if structured_data.get('text'):
            try:
                logger.info("Parsing transactions from text")
                text_transactions = processor.parse_transactions(structured_data['text'])
                logger.info(f"Found {len(text_transactions)} transactions from text")
                transactions_data.extend(text_transactions)
            except Exception as e:
                logger.error(f"Error parsing text transactions: {str(e)}")
        
        # Try parsing from tables for better structured data extraction
        if structured_data.get('tables'):
            try:
                logger.info("Parsing transactions from tables")
                table_transactions = processor.parse_transactions_from_tables(structured_data['tables'])
                logger.info(f"Found {len(table_transactions)} transactions from tables")
                transactions_data.extend(table_transactions)
            except Exception as e:
                logger.error(f"Error parsing table transactions: {str(e)}")
        
        # Remove duplicates that might occur from parsing both text and tables
        if transactions_data:
            try:
                logger.info(f"Removing duplicates from {len(transactions_data)} transactions")
                transactions_data = processor._remove_duplicate_transactions(transactions_data)
                logger.info(f"After deduplication: {len(transactions_data)} transactions")
            except Exception as e:
                logger.error(f"Error removing duplicates: {str(e)}")
                # Continue without deduplication if it fails
        
        if not transactions_data:
            pdf_upload.status = 'failed'
            pdf_upload.save()
            messages.error(request, 'No transactions found in the PDF. Please ensure it\'s a valid bank statement.')
            return redirect('pdf_analyzer:index')
        
        # Save transactions to database
        transactions = []
        for trans_data in transactions_data:
            transaction = Transaction.objects.create(
                pdf_upload=pdf_upload,
                date=trans_data['date'],
                description=trans_data['description'],
                amount=trans_data['amount'],
                transaction_type=trans_data['transaction_type'],
                category=trans_data['category']
            )
            transactions.append(transaction)
        
        # Calculate summary statistics
        summary_stats = processor.calculate_summary_stats(transactions_data)
        
        # Generate AI analysis
        try:
            analyzer = GeminiAnalyzer()
            ai_analysis_data = analyzer.analyze_transactions(transactions_data, summary_stats)
            
            # Create AI Analysis record
            ai_analysis = AIAnalysis.objects.create(
                pdf_upload=pdf_upload,
                total_income=summary_stats['total_income'],
                total_expenses=summary_stats['total_expenses'],
                net_change=summary_stats['net_change'],
                spending_patterns=ai_analysis_data['spending_patterns'],
                budgeting_recommendations=ai_analysis_data['budgeting_recommendations'],
                financial_insights=ai_analysis_data['financial_insights'],
                risk_assessment=ai_analysis_data.get('risk_assessment', ''),
                gemini_model_used='gemini-2.5-flash'
            )
            
            # Create category summaries
            for category, data in summary_stats['category_breakdown'].items():
                if data['total'] > 0:  # Only create summaries for categories with spending
                    total_expenses_float = float(summary_stats['total_expenses'])
                    percentage = (float(data['total']) / total_expenses_float * 100) if total_expenses_float > 0 else 0
                    
                    CategorySummary.objects.create(
                        analysis=ai_analysis,
                        category_name=category,
                        total_amount=data['total'],
                        transaction_count=data['count'],
                        percentage_of_expenses=Decimal(str(round(percentage, 2)))
                    )
            
        except Exception as e:
            logger.error(f"AI analysis failed for upload {upload_id}: {str(e)}")
            # Continue without AI analysis - user can still see transactions
            ai_analysis = AIAnalysis.objects.create(
                pdf_upload=pdf_upload,
                total_income=summary_stats['total_income'],
                total_expenses=summary_stats['total_expenses'],
                net_change=summary_stats['net_change'],
                budgeting_recommendations='AI analysis temporarily unavailable. Please review your transactions manually.',
                financial_insights='Basic transaction processing completed successfully.',
                risk_assessment='Manual review recommended.',
            )
        
        # Update status to completed
        pdf_upload.status = 'completed'
        pdf_upload.save()
        
        messages.success(request, f'Successfully processed {len(transactions)} transactions from your bank statement.')
        return redirect('pdf_analyzer:analysis_results', upload_id=upload_id)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error processing PDF {upload_id}: {str(e)}")
        logger.error(f"Full traceback: {error_details}")
        print(f"❌ PDF PROCESSING ERROR: {str(e)}")
        print(f"❌ FULL TRACEBACK: {error_details}")
        pdf_upload.status = 'failed'
        pdf_upload.save()
        messages.error(request, f'Failed to process PDF: {str(e)}')
        return redirect('pdf_analyzer:index')


def analysis_status(request, upload_id):
    """Show processing status and redirect when ready"""
    pdf_upload = get_object_or_404(PDFUpload, id=upload_id)
    
    if pdf_upload.status == 'completed':
        return redirect('pdf_analyzer:analysis_results', upload_id=upload_id)
    elif pdf_upload.status == 'failed':
        messages.error(request, 'PDF processing failed. Please try uploading again.')
        return redirect('pdf_analyzer:index')
    
    context = {
        'pdf_upload': pdf_upload,
        'progress_percentage': 75 if pdf_upload.status == 'processing' else 25
    }
    
    return render(request, 'pdf_analyzer/status.html', context)


def analysis_results(request, upload_id):
    """Display analysis results and insights"""
    pdf_upload = get_object_or_404(PDFUpload, id=upload_id)
    
    if pdf_upload.status != 'completed':
        return redirect('pdf_analyzer:analysis_status', upload_id=upload_id)
    
    try:
        analysis = pdf_upload.analysis
        transactions = pdf_upload.transactions.all()
        category_summaries = analysis.category_summaries.all().order_by('-total_amount')
        
        # Get student-specific insights
        transactions_data = []
        for trans in transactions:
            transactions_data.append({
                'date': trans.date,
                'description': trans.description,
                'amount': trans.amount,
                'category': trans.category,
                'transaction_type': trans.transaction_type
            })
        
        student_patterns = StudentBudgetAnalyzer.analyze_student_spending_patterns(transactions_data)
        student_recommendations = StudentBudgetAnalyzer.get_student_budget_recommendations(
            student_patterns, analysis.total_income
        )
        
        context = {
            'pdf_upload': pdf_upload,
            'analysis': analysis,
            'transactions': transactions[:50],  # Show recent 50 transactions
            'transaction_count': transactions.count(),
            'category_summaries': category_summaries,
            'student_patterns': student_patterns,
            'student_recommendations': student_recommendations,
        }
        
        return render(request, 'pdf_analyzer/results.html', context)
        
    except AIAnalysis.DoesNotExist:
        messages.error(request, 'Analysis data not found. Please reprocess the PDF.')
        return redirect('pdf_analyzer:process_pdf', upload_id=upload_id)


@require_http_methods(["GET"])
def get_analysis_status(request, upload_id):
    """API endpoint to check processing status"""
    pdf_upload = get_object_or_404(PDFUpload, id=upload_id)
    
    response_data = {
        'status': pdf_upload.status,
        'file_name': pdf_upload.file_name,
        'uploaded_at': pdf_upload.uploaded_at.isoformat(),
    }
    
    if pdf_upload.status == 'completed':
        response_data['results_url'] = reverse('pdf_analyzer:analysis_results', args=[upload_id])
    elif pdf_upload.status == 'failed':
        response_data['error'] = 'Processing failed'
    
    return JsonResponse(response_data)


def transaction_list(request, upload_id):
    """API endpoint to get all transactions for an upload"""
    pdf_upload = get_object_or_404(PDFUpload, id=upload_id)
    transactions = pdf_upload.transactions.all()
    
    transactions_data = []
    for trans in transactions:
        transactions_data.append({
            'id': trans.id,
            'date': trans.date.isoformat(),
            'description': trans.description,
            'amount': str(trans.amount),
            'transaction_type': trans.transaction_type,
            'category': trans.category,
        })
    
    return JsonResponse({
        'transactions': transactions_data,
        'count': len(transactions_data)
    })


def delete_upload(request, upload_id):
    """Delete an uploaded PDF and all associated data"""
    if request.method == 'POST':
        pdf_upload = get_object_or_404(PDFUpload, id=upload_id)
        
        # Delete the file from storage
        if pdf_upload.file:
            try:
                default_storage.delete(pdf_upload.file.name)
            except:
                pass  # File might not exist
        
        # Delete the database record (cascades to related objects)
        file_name = pdf_upload.file_name
        pdf_upload.delete()
        
        messages.success(request, f'Successfully deleted {file_name} and all associated data.')
        return redirect('pdf_analyzer:index')
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
