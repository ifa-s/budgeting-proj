"""
Gemini AI Integration Service for Bank Statement Analysis
"""
import json
import logging
import traceback
from typing import Dict, List, Any
from decimal import Decimal
from datetime import date, datetime
import google.generativeai as genai
from django.conf import settings
import os

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Service class for analyzing transaction data using Google's Gemini AI"""
    
    def __init__(self):
        # Configure Gemini AI - try Django settings first, then environment variable
        try:
            from django.conf import settings
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
        except:
            api_key = None
            
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
            
        if not api_key:
            # Use the API key directly as fallback
            api_key = 'AIzaSyAbF-NHwzGr9HWmENSS8US8PPoLaRhOT_w'
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_pdf_content(self, pdf_content: Dict) -> Dict:
        """
        Analyze complete PDF content and extract transactions with AI insights
        """
        try:
            # Build comprehensive prompt for PDF analysis
            logger.info("Building analysis prompt for Gemini")
            analysis_prompt = self._build_pdf_analysis_prompt(pdf_content)
            logger.info(f"Prompt length: {len(analysis_prompt)} characters")
            logger.info(f"PDF content being sent to Gemini (first 300 chars): {pdf_content.get('formatted_content', '')[:300]}...")
            
            # Get AI analysis
            logger.info("Sending request to Gemini 2.5 Flash model")
            response = self.model.generate_content(analysis_prompt)
            logger.info(f"Received response from Gemini (length: {len(response.text)} chars)")
            logger.info(f"Gemini response preview: {response.text[:500]}...")
            
            # Parse the structured response
            logger.info("Parsing Gemini response")
            analysis_result = self._parse_pdf_analysis_response(response.text)
            logger.info(f"Parsed {len(analysis_result.get('transactions', []))} transactions from Gemini response")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during PDF content analysis: {str(e)}")
            logger.error(f"Exception details: {traceback.format_exc()}")
            return self._get_fallback_pdf_analysis()

    def analyze_transactions(self, transactions: List[Dict], summary_stats: Dict) -> Dict:
        """
        Analyze transaction data and provide AI-curated feedback
        """
        try:
            # Prepare data for analysis
            analysis_prompt = self._build_analysis_prompt(transactions, summary_stats)
            
            # Get AI analysis
            response = self.model.generate_content(analysis_prompt)
            
            # Parse and structure the response
            analysis_result = self._parse_gemini_response(response.text, summary_stats)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error during Gemini analysis: {str(e)}")
            return self._get_fallback_analysis(summary_stats)
    
    def _build_analysis_prompt(self, transactions: List[Dict], summary_stats: Dict) -> str:
        """Build a comprehensive prompt for Gemini AI analysis"""
        
        # Convert transactions to a more readable format
        transaction_summary = []
        for trans in transactions[:20]:  # Limit to recent 20 transactions for prompt size
            # Handle date formatting - could be date object or string
            if hasattr(trans['date'], 'strftime'):
                date_str = trans['date'].strftime('%Y-%m-%d')
            else:
                date_str = str(trans['date'])  # Already a string
                
            transaction_summary.append({
                'date': date_str,
                'description': trans['description'][:50],  # Truncate long descriptions
                'amount': float(trans['amount']),
                'category': trans['category'],
                'type': trans['transaction_type']
            })
        
        # Build category summary
        category_data = []
        for category, data in summary_stats['category_breakdown'].items():
            if category != 'other' or data['count'] > 2:  # Skip 'other' unless significant
                category_data.append({
                    'category': category,
                    'total_spent': float(data['total']),
                    'transaction_count': data['count']
                })
        
        prompt = f"""
You are a financial advisor specializing in college student budgets at Virginia Tech. 
Analyze the following bank statement data and provide personalized financial insights and recommendations.

FINANCIAL SUMMARY:
- Total Income: ${summary_stats['total_income']}
- Total Expenses: ${summary_stats['total_expenses']}  
- Net Change: ${summary_stats['net_change']}
- Number of Transactions: {summary_stats['transaction_count']}

SPENDING BY CATEGORY:
{json.dumps(category_data, indent=2)}

RECENT TRANSACTIONS (sample):
{json.dumps(transaction_summary, indent=2)}

Please provide a comprehensive financial analysis in the following JSON format:

{{
    "spending_patterns": {{
        "top_spending_categories": ["category1", "category2", "category3"],
        "spending_frequency": "daily/weekly/monthly pattern description",
        "unusual_spending": "any unusual or concerning patterns",
        "positive_habits": "good financial habits observed"
    }},
    "budgeting_recommendations": "Detailed budgeting advice specifically for college students, including specific dollar amounts and percentages where appropriate. Focus on practical, actionable advice.",
    "financial_insights": "Key insights about spending behavior, trends, and areas for improvement. Be specific and data-driven.",
    "risk_assessment": "Assessment of financial risks, overspending patterns, or areas of concern. Include specific warnings if needed.",
    "college_student_specific_tips": "Advice tailored specifically for Virginia Tech students - consider dining plans, textbooks, campus activities, etc.",
    "action_items": [
        "Specific action item 1",
        "Specific action item 2", 
        "Specific action item 3"
    ]
}}

Focus on:
1. College student lifestyle and typical expenses
2. Practical budgeting strategies for students
3. Warning about overspending in specific categories
4. Opportunities to save money
5. Building healthy financial habits for the future

Be encouraging but honest about areas needing improvement. Use specific numbers from the data when possible.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str, summary_stats: Dict) -> Dict:
        """Parse and validate Gemini's JSON response"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_response = json.loads(json_str)
            else:
                # Fallback: try parsing the entire response
                parsed_response = json.loads(response_text)
            
            # Validate and structure the response
            analysis_result = {
                'spending_patterns': parsed_response.get('spending_patterns', {}),
                'budgeting_recommendations': parsed_response.get('budgeting_recommendations', ''),
                'financial_insights': parsed_response.get('financial_insights', ''),
                'risk_assessment': parsed_response.get('risk_assessment', ''),
                'college_student_specific_tips': parsed_response.get('college_student_specific_tips', ''),
                'action_items': parsed_response.get('action_items', []),
                'summary_stats': {
                    'total_income': float(summary_stats['total_income']),
                    'total_expenses': float(summary_stats['total_expenses']),
                    'net_change': float(summary_stats['net_change'])
                }
            }
            
            return analysis_result
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse Gemini JSON response: {str(e)}")
            # Return structured fallback with raw response
            return self._get_fallback_analysis_with_raw_response(response_text, summary_stats)
    
    def _get_fallback_analysis(self, summary_stats: Dict) -> Dict:
        """Provide basic analysis when AI analysis fails"""
        net_change = summary_stats['net_change']
        total_expenses = summary_stats['total_expenses']
        
        basic_insights = []
        if net_change < 0:
            basic_insights.append("You spent more than you earned this period.")
        else:
            basic_insights.append("You maintained a positive balance this period.")
        
        if total_expenses > 0:
            top_categories = sorted(
                summary_stats['category_breakdown'].items(),
                key=lambda x: x[1]['total'],
                reverse=True
            )[:3]
            basic_insights.append(f"Your top spending categories were: {', '.join([cat[0] for cat in top_categories])}")
        
        return {
            'spending_patterns': {
                'top_spending_categories': [cat[0] for cat in top_categories[:3]] if total_expenses > 0 else [],
                'spending_frequency': 'Analysis unavailable',
                'unusual_spending': 'Detailed analysis unavailable',
                'positive_habits': 'Detailed analysis unavailable'
            },
            'budgeting_recommendations': 'AI analysis temporarily unavailable. Please review your spending categories and consider creating a monthly budget.',
            'financial_insights': ' '.join(basic_insights),
            'risk_assessment': 'Manual review recommended',
            'college_student_specific_tips': 'Consider using student discounts and campus resources to reduce expenses.',
            'action_items': ['Review monthly expenses', 'Set up a basic budget', 'Track daily spending'],
            'summary_stats': {
                'total_income': float(summary_stats['total_income']),
                'total_expenses': float(summary_stats['total_expenses']),
                'net_change': float(summary_stats['net_change'])
            }
        }
    
    def _get_fallback_analysis_with_raw_response(self, raw_response: str, summary_stats: Dict) -> Dict:
        """Fallback analysis that includes the raw AI response"""
        fallback = self._get_fallback_analysis(summary_stats)
        
        # Try to extract useful insights from raw response
        fallback['financial_insights'] = f"AI Response: {raw_response[:500]}..."  # Truncate if too long
        fallback['budgeting_recommendations'] = raw_response[:1000] if len(raw_response) < 1000 else raw_response[:1000] + "..."
        
        return fallback
    
    def _build_pdf_analysis_prompt(self, pdf_content: Dict) -> str:
        """Build comprehensive prompt for PDF content analysis"""
        prompt = f"""
You are a financial AI assistant specialized in analyzing bank statements for college students. 
Analyze the following bank statement PDF content and provide a comprehensive financial analysis.

BANK STATEMENT CONTENT:
{pdf_content.get('formatted_content', '')}

INSTRUCTIONS:
1. Extract ALL transactions from the PDF content (dates, descriptions, amounts)
2. Categorize each transaction appropriately
3. Calculate financial summaries
4. Provide detailed insights and recommendations for a college student

Please respond with a structured JSON format containing:
{{
    "transactions": [
        {{
            "date": "YYYY-MM-DD",
            "description": "transaction description",
            "amount": -50.00,
            "category": "category_name",
            "transaction_type": "debit" or "credit"
        }}
    ],
    "financial_summary": {{
        "total_income": 0.00,
        "total_expenses": 0.00,
        "net_change": 0.00,
        "transaction_count": 0
    }},
    "category_breakdown": {{
        "category_name": {{
            "total": 0.00,
            "count": 0,
            "percentage": 0.0
        }}
    }},
    "spending_patterns": {{
        "largest_expense": "description",
        "most_frequent_category": "category",
        "weekend_vs_weekday_spending": "analysis",
        "recurring_transactions": ["list of recurring items"]
    }},
    "budgeting_recommendations": "Detailed recommendations for college students...",
    "financial_insights": "Key insights about spending habits...",
    "risk_assessment": "Assessment of financial health and risks...",
    "college_student_tips": "Specific tips for college students...",
    "action_items": ["specific actionable steps"]
}}

Focus on:
- Identifying student-relevant spending (textbooks, dining, entertainment, transportation)
- Virginia Tech campus-specific considerations if applicable
- Budget optimization for student income levels
- Building good financial habits early
- Debt prevention and emergency fund recommendations
"""
        return prompt
    
    def _parse_pdf_analysis_response(self, response_text: str) -> Dict:
        """Parse Gemini's PDF analysis response"""
        try:
            # Clean up the response and extract JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_response = json.loads(json_str)
            else:
                parsed_response = json.loads(response_text)
            
            # Validate required structure
            required_keys = ['transactions', 'financial_summary', 'category_breakdown']
            for key in required_keys:
                if key not in parsed_response:
                    raise KeyError(f"Missing required key: {key}")
            
            # Process transactions to ensure proper format
            transactions = []
            for trans in parsed_response.get('transactions', []):
                if isinstance(trans, dict) and all(k in trans for k in ['date', 'description', 'amount']):
                    # Convert date strings to proper format
                    date_str = trans['date']
                    try:
                        # Parse various date formats
                        if '/' in date_str:
                            parts = date_str.split('/')
                            if len(parts) == 3:
                                if len(parts[2]) == 2:  # YY format
                                    parts[2] = '20' + parts[2]
                                date_str = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                        
                        transactions.append({
                            'date': date_str,
                            'description': trans['description'],
                            'amount': Decimal(str(trans['amount'])),
                            'category': trans.get('category', 'other'),
                            'transaction_type': trans.get('transaction_type', 'debit' if float(trans['amount']) < 0 else 'credit')
                        })
                    except (ValueError, IndexError):
                        logger.warning(f"Could not parse transaction date: {date_str}")
                        continue
            
            # Structure the final result
            result = {
                'transactions': transactions,
                'financial_summary': parsed_response.get('financial_summary', {}),
                'category_breakdown': parsed_response.get('category_breakdown', {}),
                'spending_patterns': parsed_response.get('spending_patterns', {}),
                'budgeting_recommendations': parsed_response.get('budgeting_recommendations', ''),
                'financial_insights': parsed_response.get('financial_insights', ''),
                'risk_assessment': parsed_response.get('risk_assessment', ''),
                'college_student_tips': parsed_response.get('college_student_tips', ''),
                'action_items': parsed_response.get('action_items', [])
            }
            
            return result
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse PDF analysis response: {str(e)}")
            return self._get_fallback_pdf_analysis()
    
    def _get_fallback_pdf_analysis(self) -> Dict:
        """Provide fallback analysis when PDF parsing fails"""
        return {
            'transactions': [],
            'financial_summary': {
                'total_income': Decimal('0.00'),
                'total_expenses': Decimal('0.00'),
                'net_change': Decimal('0.00'),
                'transaction_count': 0
            },
            'category_breakdown': {},
            'spending_patterns': {},
            'budgeting_recommendations': 'Unable to analyze PDF content automatically. Please review your statement manually or try uploading a clearer PDF.',
            'financial_insights': 'PDF analysis failed. The file may not contain readable transaction data or may be in an unsupported format.',
            'risk_assessment': 'Manual review recommended due to processing error.',
            'college_student_tips': 'Consider using a digital banking app for better transaction tracking.',
            'action_items': ['Re-upload a clearer PDF', 'Check if PDF contains readable text', 'Consider manual transaction review']
        }


class StudentBudgetAnalyzer:
    """Specialized analyzer for college student financial patterns"""
    
    @staticmethod
    def analyze_student_spending_patterns(transactions: List[Dict]) -> Dict:
        """Analyze spending patterns specific to college students"""
        patterns = {
            'textbook_spending': 0,
            'dining_out_frequency': 0,
            'entertainment_spending': 0,
            'transportation_costs': 0,
            'late_night_spending': 0,  # Spending after 10 PM
            'weekend_vs_weekday': {'weekend': 0, 'weekday': 0}
        }
        
        for trans in transactions:
            # Analyze timing patterns
            if hasattr(trans['date'], 'weekday'):
                if trans['date'].weekday() >= 5:  # Saturday = 5, Sunday = 6
                    patterns['weekend_vs_weekday']['weekend'] += float(trans['amount'])
                else:
                    patterns['weekend_vs_weekday']['weekday'] += float(trans['amount'])
            
            # Analyze category-specific patterns
            category = trans['category'].lower()
            if 'education' in category or 'textbook' in trans['description'].lower():
                patterns['textbook_spending'] += float(trans['amount'])
            elif category == 'restaurants':
                patterns['dining_out_frequency'] += 1
            elif category == 'entertainment':
                patterns['entertainment_spending'] += float(trans['amount'])
            elif category == 'transportation':
                patterns['transportation_costs'] += float(trans['amount'])
        
        return patterns
    
    @staticmethod
    def get_student_budget_recommendations(spending_patterns: Dict, total_income: Decimal) -> List[str]:
        """Generate budget recommendations specific to college students"""
        recommendations = []
        
        if spending_patterns['dining_out_frequency'] > 15:  # More than 15 restaurant transactions
            recommendations.append("Consider reducing dining out frequency - aim for cooking 4-5 meals per week to save $200+ monthly")
        
        if spending_patterns['entertainment_spending'] > float(total_income) * 0.15:
            recommendations.append("Entertainment spending exceeds 15% of income - try free campus events and student discounts")
        
        if spending_patterns['textbook_spending'] > 500:
            recommendations.append("High textbook costs detected - consider renting, buying used, or digital versions")
        
        weekend_ratio = spending_patterns['weekend_vs_weekday']['weekend'] / (
            spending_patterns['weekend_vs_weekday']['weekend'] + spending_patterns['weekend_vs_weekday']['weekday']
        ) if spending_patterns['weekend_vs_weekday']['weekend'] + spending_patterns['weekend_vs_weekday']['weekday'] > 0 else 0
        
        if weekend_ratio > 0.4:
            recommendations.append("High weekend spending detected - set a weekend budget limit")
        
        return recommendations