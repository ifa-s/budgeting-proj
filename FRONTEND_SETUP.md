# Bucket! AI Assistant - Frontend Setup

## Overview
This is a simple ChatGPT-like frontend interface that connects to your backend `user_client` for budget management. The interface provides a clean chat experience where users can interact with your AI budget assistant.

## Features
- 💬 ChatGPT-style interface with clean UI/UX
- 🔄 Real-time conversation with AI assistant
- 📊 **Real-time Interactive Charts** - Live visualization of budget data
- 📈 **Budget Allocation Pie Chart** - Visual breakdown of spending buckets
- 📉 **Spending Timeline Graph** - Track budget changes over time
- 💡 **Smart Recommendations Checklist** - AI-powered financial advice sidebar
- ✅ **Interactive Task Management** - Check off completed recommendations
- 🎯 **Contextual Suggestions** - Personalized tips based on your spending patterns
- 🌙 **Dark/Light Theme Toggle** - Beautiful theme switching with smooth transitions
- 💾 **Theme Persistence** - Remembers your preferred theme across sessions
- 📱 Responsive design for mobile and desktop
- ⚡ Real-time bucket management visualization

## Setup Instructions

### 1. Set up your OpenRouter API Key
Create a `.env` file in the project root (same directory as README.md):
```bash
cp env.example .env
```

Edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 2. Install Dependencies
Make sure your virtual environment is activated:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
cd budgeting_app
python manage.py migrate
```

### 4. Start the Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
Open your browser and go to: http://127.0.0.1:8000/

## How It Works

### Frontend-Backend Integration
- The Django app creates a `UserClient` instance from your backend
- Chat messages are processed through your `user_client.process_user_input()` method
- **Real-time chart synchronization** - Charts display actual bucket data from the backend
- **AI chart awareness** - The AI knows about current chart state and bucket allocations
- **Accurate data extraction** - Bucket percentages, amounts, and names pulled directly from BucketManager
- The interface handles both frontend AI responses and backend command execution

### API Endpoints
- `GET /` - Main chat interface
- `POST /start/` - Initialize conversation
- `POST /send/` - Send message and get AI response
- `GET /status/` - Get current bucket status

### File Structure
```
budgeting_app/
├── chat/                    # Django app for chat interface
│   ├── templates/chat/      # HTML templates
│   ├── views.py            # API views connecting to backend
│   └── urls.py             # URL routing
├── budgeting_app/          # Django project settings
└── manage.py               # Django management script
```

## Usage
1. Start the server and open the chat interface
2. The AI will greet you automatically
3. Start by telling the AI about your income or financial situation
4. Ask it to create spending buckets, set budgets, or track expenses
5. **Watch the real-time charts update** as you interact:
   - **Budget Allocation Chart** - Shows how your money is distributed across buckets
   - **Spending Timeline** - Tracks your budget changes over time
   - **Live Stats** - Real-time budget totals and allocation percentages
   - **Smart Recommendations** - AI-generated financial advice checklist
6. **Check off recommendations** as you complete financial tasks
7. **Toggle between light and dark themes** using the 🌙/☀️ button in the header
8. The header will show real-time updates of your budget status

## Real-time Chart Features

### Budget Allocation Chart (Doughnut Chart)
- **Visual breakdown** of spending buckets with dynamic colors
- **Real-time updates** as you create/modify buckets
- **Interactive labels** showing bucket names and percentages
- **Unallocated funds** displayed separately

### Spending Timeline (Line Chart)
- **Live tracking** of budget changes over time
- **Automatic timestamps** for each interaction
- **Smooth animations** with gradient fills
- **Last 10 data points** kept for performance

### Dynamic Stats Panel
- **Total Budget** with currency formatting
- **Allocation Percentage** with real-time calculation
- **Bucket Count** automatically updated
- **Responsive design** for all screen sizes

### Smart Recommendations Checklist
- **AI-Generated Suggestions** based on your conversation and spending patterns
- **Priority-Based Sorting** - High, medium, and low priority recommendations
- **Interactive Checkboxes** - Mark recommendations as completed
- **Contextual Tips** triggered by specific spending categories:
  - Housing recommendations when you mention rent/mortgage
  - Emergency fund advice for savings discussions
  - Debt management strategies for loan/credit mentions
  - Investment tips for retirement planning
  - Food budget optimization for dining expenses
- **Real-time Updates** - New recommendations appear as you chat
- **Color-coded Categories** - Easy visual identification of advice types

### Dark/Light Theme System
- **Instant Theme Toggle** - Click the 🌙/☀️ button in the header
- **Smooth Transitions** - 0.3s ease animations for all color changes
- **Complete Theme Coverage** - All components adapt to chosen theme:
  - Background colors and text contrast optimized for readability
  - Chart colors and legends automatically adjust
  - Borders, shadows, and accent colors themed consistently
  - Input fields, buttons, and interactive elements styled appropriately
- **Persistent Preference** - Theme choice saved in localStorage
- **System Integration** - Respects user's preference across browser sessions
- **Accessibility Focused** - High contrast ratios maintained in both themes

## Customization
- Modify `chat/templates/chat/index.html` to change the UI appearance or chart styling
- Update `chat/views.py` to add new API endpoints or modify chart data
- Adjust the AI models in the backend by modifying the `UserClient` initialization
- Customize chart colors and animations in the JavaScript Chart.js configuration

## Troubleshooting
- Make sure your `.env` file contains a valid OpenRouter API key
- Ensure the backend modules are accessible (check Python path)
- Check Django logs for any import or configuration errors
- Verify all dependencies are installed in your virtual environment
