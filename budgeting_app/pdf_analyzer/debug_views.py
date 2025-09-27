"""
Debug views for PDF analyzer troubleshooting
"""
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import PDFProcessor

logger = logging.getLogger(__name__)

def debug_page(request):
    """Debug page for testing PDF uploads"""
    return render(request, 'pdf_analyzer/debug.html')

@csrf_exempt
@require_http_methods(["POST"])
def debug_pdf_upload(request):
    """Debug endpoint to test PDF processing step by step"""
    try:
        if 'pdf_file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['pdf_file']
        
        # Basic file info
        file_info = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'content_type': uploaded_file.content_type,
        }
        
        # Validate it's a PDF
        if not uploaded_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'error': 'Not a PDF file',
                'file_info': file_info
            }, status=400)
        
        # Test new Gemini-powered PDF processing
        processor = PDFProcessor()
        
        try:
            # Step 1: Extract complete PDF content
            with uploaded_file.open('rb') as pdf_file:
                pdf_content = processor.extract_complete_pdf_content(pdf_file)
            
            result = {
                'success': True,
                'file_info': file_info,
                'step1_pdf_extraction': {
                    'text_length': len(pdf_content.get('raw_text', '')),
                    'num_tables': len(pdf_content.get('structured_tables', [])),
                    'formatted_content_preview': pdf_content.get('formatted_content', '')[:800] + '...' if len(pdf_content.get('formatted_content', '')) > 800 else pdf_content.get('formatted_content', ''),
                    'metadata': pdf_content.get('metadata', {})
                }
            }
            
            # Step 2: Test Gemini AI Analysis
            try:
                from .ai_service import GeminiAnalyzer
                analyzer = GeminiAnalyzer()
                
                analysis_result = analyzer.analyze_pdf_content(pdf_content)
                
                result['step2_gemini_analysis'] = {
                    'success': True,
                    'transactions_extracted': len(analysis_result.get('transactions', [])),
                    'financial_summary': analysis_result.get('financial_summary', {}),
                    'categories_found': len(analysis_result.get('category_breakdown', {})),
                    'insights_preview': analysis_result.get('financial_insights', '')[:200] + '...' if len(analysis_result.get('financial_insights', '')) > 200 else analysis_result.get('financial_insights', ''),
                    'sample_transactions': analysis_result.get('transactions', [])[:3]  # First 3 transactions
                }
            except Exception as ai_error:
                result['step2_gemini_analysis'] = {
                    'success': False,
                    'error': str(ai_error),
                    'error_type': type(ai_error).__name__
                }
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'error': f'PDF processing failed: {str(e)}',
                'file_info': file_info,
                'error_type': type(e).__name__
            }, status=500)
            
    except Exception as e:
        logger.error(f"Debug upload error: {str(e)}")
        return JsonResponse({
            'error': f'Upload failed: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)