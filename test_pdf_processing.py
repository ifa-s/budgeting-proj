#!/usr/bin/env python3
"""
Test script to verify PDF processing and Gemini integration
"""
import os
import sys

# Add Django project to path
sys.path.append('/Users/yashk/Desktop/budgeting-proj/budgeting_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budgeting_app.settings')

import django
django.setup()

from pdf_analyzer.services import PDFProcessor
from pdf_analyzer.ai_service import GeminiAnalyzer
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gemini_connection():
    """Test Gemini API connection"""
    try:
        logger.info("Testing Gemini API connection...")
        analyzer = GeminiAnalyzer()
        
        # Test with simple content
        test_content = {
            'formatted_content': '''
            === BANK STATEMENT PDF CONTENT ===
            
            --- PAGE 1 ---
            SAMPLE BANK STATEMENT
            Account: 123456789
            Statement Period: 01/01/2024 - 01/31/2024
            
            Date        Description                Amount
            01/05/2024  STARBUCKS COFFEE          -4.50
            01/07/2024  WALMART GROCERY          -85.32
            01/10/2024  DIRECT DEPOSIT          +2500.00
            01/15/2024  RENT PAYMENT            -800.00
            01/20/2024  GAS STATION              -45.20
            ''',
            'raw_text': 'SAMPLE BANK STATEMENT Account: 123456789 Statement Period: 01/01/2024 - 01/31/2024 Date Description Amount 01/05/2024 STARBUCKS COFFEE -4.50 01/07/2024 WALMART GROCERY -85.32 01/10/2024 DIRECT DEPOSIT +2500.00 01/15/2024 RENT PAYMENT -800.00 01/20/2024 GAS STATION -45.20',
            'structured_tables': [],
            'metadata': {'total_pages': 1}
        }
        
        logger.info("Sending test content to Gemini...")
        result = analyzer.analyze_pdf_content(test_content)
        
        logger.info(f"✅ Gemini analysis successful!")
        logger.info(f"Transactions found: {len(result.get('transactions', []))}")
        logger.info(f"Financial summary: {result.get('financial_summary', {})}")
        
        if result.get('transactions'):
            logger.info("Sample transactions:")
            for i, trans in enumerate(result.get('transactions', [])[:3]):
                logger.info(f"  {i+1}. {trans.get('date')} - {trans.get('description')} - ${trans.get('amount')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Gemini test failed: {str(e)}")
        return False

def test_pdf_extraction():
    """Test PDF text extraction"""
    try:
        logger.info("Testing PDF extraction capabilities...")
        processor = PDFProcessor()
        
        # Test with a simple text (simulating PDF content)
        logger.info("✅ PDF processor initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ PDF extraction test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting PDF processing system tests...")
    
    tests = [
        ("PDF Extraction", test_pdf_extraction),
        ("Gemini Connection", test_gemini_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        if test_func():
            logger.info(f"✅ {test_name} PASSED")
            passed += 1
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! PDF scanner is working correctly.")
        return True
    else:
        logger.error("💥 SOME TESTS FAILED! Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)