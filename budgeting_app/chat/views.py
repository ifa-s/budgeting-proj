import json
import sys
import os
from pathlib import Path
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Add the parent directory to sys.path to import backend modules
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from backend.user_client import UserClient
from backend.buckets.bucket import Bucket


def log_system_context(user_client, enhanced_user_message, response):
    """Append system context details to a log file under project logs directory."""
    try:
        logs_dir = project_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = logs_dir / "system_context.log"

        timestamp = datetime.utcnow().isoformat()
        sections = [
            f"[{timestamp} UTC]",
            
            "-- Enhanced User Message--",
            enhanced_user_message,
            "Frontend Response:",
            response['frontend'],
            "=== BUCKET MANAGER STATUS ===",
            user_client.get_status(),
            "Backend Response:",
            response['backend'],
            "",
        ]
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n".join(sections) + "\n")
    except Exception as e:
        print(f"[WARN] Failed to write system context log: {e}")


def get_detailed_bucket_data(bucket_manager):
    """Extract detailed bucket information for chart visualization"""
    try:
        bucket_names = bucket_manager.get_bucket_names()
        bucket_data = []
        total_budget = bucket_manager.get_total_budget()
        print(f"[DEBUG] get_detailed_bucket_data - Raw bucket names: {bucket_names}")
        
        for name in bucket_names:
            bucket = bucket_manager.get_bucket(name)
            if bucket:
                # Include all defined buckets; unallocated is implicit (100 - allocated)
                current_amount = total_budget * (bucket.get_percentage() / 100.0)
                bucket_info = {
                    'name': name,
                    'current': current_amount,
                    'max': total_budget * (bucket.get_percentage() / 100.0),
                    'percentage': bucket.get_percentage()
                }
                bucket_data.append(bucket_info)
                print(f"[DEBUG] Added bucket to chart data: {bucket_info}")
        
        # Get actual total budget and percentage
        total_percentage = bucket_manager.get_total_percentage()
        
        # Debug info
        debug_info = {
            'bucket_manager_str': str(bucket_manager),
            'raw_bucket_names': bucket_names,
            'filtered_bucket_count': len(bucket_data),
            'total_budget': total_budget,
            'total_percentage': total_percentage,
            'buckets_detail': [f"{b['name']}: {b['percentage']:.1f}% (${b['current']:.2f})" for b in bucket_data]
        }
        
        return {
            'buckets': bucket_data,
            'total_budget': total_budget,
            'total_percentage': total_percentage,
            'debug': debug_info
        }
    except Exception as e:
        return {
            'buckets': [],
            'total_budget': 0,
            'total_percentage': 0,
            'error': str(e)
        }


def generate_backend_recommendations(user_message, ai_response, bucket_data):
    """Generate intelligent recommendations based on user interaction and budget state"""
    recommendations = []
    
    try:
        user_text = user_message.lower()
        ai_text = ai_response.lower()
        
        # Budget setup recommendations
        if 'income' in user_text or 'salary' in user_text or 'make' in user_text:
            recommendations.append({
                'id': 'budget_foundation',
                'text': 'Great start! Consider the 50/30/20 rule: 50% needs, 30% wants, 20% savings.',
                'category': 'Budget Setup',
                'priority': 'medium',
                'trigger': 'income_mentioned'
            })
        
        # Spending category recommendations
        if any(word in user_text for word in ['restaurant', 'eating out', 'food', 'groceries']):
            recommendations.append({
                'id': 'food_budget_tip',
                'text': 'Meal planning can reduce food costs by 15-20%. Consider cooking more meals at home.',
                'category': 'Food & Dining',
                'priority': 'low',
                'trigger': 'food_spending'
            })
        
        # Housing recommendations
        if any(word in user_text for word in ['rent', 'mortgage', 'housing', 'apartment']):
            recommendations.append({
                'id': 'housing_rule',
                'text': 'Keep housing costs under 30% of your income to maintain financial flexibility.',
                'category': 'Housing',
                'priority': 'high',
                'trigger': 'housing_mentioned'
            })
        
        # Emergency fund recommendations
        if 'emergency' in user_text or 'savings' in user_text:
            recommendations.append({
                'id': 'emergency_goal',
                'text': 'Aim for 3-6 months of expenses in your emergency fund for optimal financial security.',
                'category': 'Emergency Fund',
                'priority': 'high',
                'trigger': 'emergency_discussed'
            })
        
        # Entertainment spending
        if any(word in user_text for word in ['entertainment', 'movies', 'games', 'streaming', 'netflix']):
            recommendations.append({
                'id': 'entertainment_audit',
                'text': 'Review your entertainment subscriptions monthly - cancel unused services.',
                'category': 'Entertainment',
                'priority': 'medium',
                'trigger': 'entertainment_spending'
            })
        
        # Transportation recommendations
        if any(word in user_text for word in ['car', 'gas', 'transportation', 'uber', 'lyft']):
            recommendations.append({
                'id': 'transport_optimization',
                'text': 'Consider carpooling, public transit, or biking to reduce transportation costs.',
                'category': 'Transportation',
                'priority': 'medium',
                'trigger': 'transport_mentioned'
            })
        
        # Investment mentions
        if any(word in user_text for word in ['invest', 'stocks', 'retirement', '401k', 'ira']):
            recommendations.append({
                'id': 'investment_consistency',
                'text': 'Consistent monthly investing often outperforms trying to time the market.',
                'category': 'Investment',
                'priority': 'medium',
                'trigger': 'investment_interest'
            })
        
        # Debt management
        if any(word in user_text for word in ['debt', 'credit card', 'loan', 'payment']):
            recommendations.append({
                'id': 'debt_strategy',
                'text': 'Pay off high-interest debt first (avalanche method) to minimize total interest paid.',
                'category': 'Debt Management',
                'priority': 'high',
                'trigger': 'debt_mentioned'
            })
            
        return recommendations
        
    except Exception as e:
        return []


class ChatSession:
    """Simple session management for chat interface"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatSession, cls).__new__(cls)
            cls._instance.user_client = None
            print("[DEBUG] Created new ChatSession instance")
        return cls._instance
    
    def get_user_client(self):
        if self.user_client is None:
            self.user_client = UserClient()
            print("[DEBUG] Created new UserClient instance")
        else:
            print("[DEBUG] Reusing existing UserClient instance")
        return self.user_client


def index(request):
    """Main chat interface"""
    return render(request, 'chat/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def start_conversation(request):
    """Initialize a new conversation"""
    try:
        session = ChatSession()
        # Reset the user client for a fresh conversation
        session.user_client = UserClient()
        
        # Get the initial greeting
        greeting = session.get_user_client().start_conversation()
        
        return JsonResponse({
            'success': True,
            'message': greeting,
            'type': 'greeting'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Process user message and return AI response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        session = ChatSession()
        user_client = session.get_user_client()
        
        # Get current bucket state for AI context
        bucket_data = get_detailed_bucket_data(user_client.bucket_manager)
        
        # Add chart context to the user message
        chart_context = ""
        if bucket_data['buckets']:
            chart_context = f"\n\nCURRENT CHART STATE: Your budget is visualized with {len(bucket_data['buckets'])} buckets. "
            chart_context += f"Total budget: ${bucket_data['total_budget']:.2f}, "
            chart_context += f"Total allocated: {bucket_data['total_percentage']:.1f}%. "
            chart_context += "Buckets: " + ", ".join([f"{b['name']} ({b['percentage']:.1f}%)" for b in bucket_data['buckets']])
        else:
            chart_context = "\n\nCURRENT CHART STATE: No budget buckets have been created yet. The chart shows 100% unallocated."
        
        # Process the user input with chart context
        enhanced_user_message = user_message + chart_context
        response = user_client.process_user_input(enhanced_user_message)
        
        # Debug: Log what commands were executed
        print(f"[DEBUG] User Message: {user_message}")
        print(f"[DEBUG] Frontend Response: {response['frontend']}")
        print(f"[DEBUG] Backend Commands: {response['backend']}")
        print(f"[DEBUG] Command Results: {response['commands']}")
        
        # Get bucket status for visualization
        status = user_client.get_status()
        bucket_summary = user_client.get_bucket_manager_summary()
        
        # Get updated detailed bucket information for charts (after AI processing)
        updated_bucket_data = get_detailed_bucket_data(user_client.bucket_manager)
        print(f"[DEBUG] Updated bucket data: {updated_bucket_data}")
        
        # Generate smart recommendations based on the interaction
        backend_recommendations = generate_backend_recommendations(
            user_message, 
            response['frontend'], 
            updated_bucket_data
        )
        # Log system context before invoking the model
        try:
            log_system_context(user_client, enhanced_user_message, response)
        except Exception as e:
            print(f"[WARN] system context logging failed: {e}")
        return JsonResponse({
            'success': True,
            'frontend_response': response['frontend'],
            'backend_response': response['backend'],
            'commands': response['commands'],
            'status': status,
            'bucket_summary': bucket_summary,
            'bucket_data': updated_bucket_data,
            'recommendations': backend_recommendations,
            'type': 'response'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_status(request):
    """Get current bucket status and summary"""
    try:
        session = ChatSession()
        user_client = session.get_user_client()
        
        status = user_client.get_status()
        bucket_summary = user_client.get_bucket_manager_summary()
        bucket_data = get_detailed_bucket_data(user_client.bucket_manager)
        
        return JsonResponse({
            'success': True,
            'status': status,
            'bucket_summary': bucket_summary,
            'bucket_data': bucket_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_bucket_operations(request):
    """Test bucket operations directly"""
    try:
        session = ChatSession()
        user_client = session.get_user_client()
        
        if request.method == "POST":
            # Execute test operations
            user_client.bucket_manager.set_total_budget(3000.0)
            user_client.bucket_manager.add_bucket("rent", 50.0)
            user_client.bucket_manager.add_bucket("food", 20.0)
            user_client.bucket_manager.add_bucket("entertainment", 15.0)
            
            result_msg = "Added test buckets: rent (50%), food (20%), entertainment (15%)"
        else:
            result_msg = "GET request - ready to test"
        
        # Get current state
        bucket_data = get_detailed_bucket_data(user_client.bucket_manager)
        status = user_client.get_status()
        bucket_summary = user_client.get_bucket_manager_summary()
        
        return JsonResponse({
            'success': True,
            'message': result_msg,
            'bucket_data': bucket_data,
            'status': status,
            'bucket_summary': bucket_summary,
            'bucket_manager_debug': str(user_client.bucket_manager)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)