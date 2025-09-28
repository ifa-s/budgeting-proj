# Bucket! - Smart Budget Management 🎯

**VTHacks 13 Submission** | *Made with ❤️ in Blacksburg, VA*

An intelligent budget management platform that combines conversational AI with powerful PDF bank statement analysis to help you take control of your finances.

![Bucket Screenshot](https://img.shields.io/badge/VTHacks-13-orange?style=for-the-badge) ![Django](https://img.shields.io/badge/Django-4.2.24-green?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)

## 🚀 What is Bucket!?

Bucket! is a comprehensive financial management tool that makes budgeting intuitive and intelligent. Instead of complex spreadsheets, chat with an AI that understands your money and helps you organize it into smart "buckets" - whether it's rent, groceries, savings, or that weekend fund.

### 🎯 Key Features

- **🤖 AI Budget Assistant** - Chat naturally about your finances and get personalized advice
- **📄 Smart PDF Analysis** - Upload bank statements and get instant financial insights
- **🎨 Beautiful UI** - Clean, modern interface with dark/light theme support
- **📊 Interactive Charts** - Visualize your spending patterns and budget allocation
- **🔒 Secure & Local** - Your financial data stays on your machine

## 🛠 Tech Stack

- **Backend**: Django 4.2.24, Python 3.9+
- **Frontend**: Vanilla JavaScript, Bootstrap 5, Chart.js
- **AI**: OpenRouter API, Google Gemini
- **Database**: SQLite
- **PDF Processing**: pdfplumber
- **Styling**: Custom CSS with glassmorphism effects

## 🎨 Screenshots & Demo

### AI Chat Interface
- Natural language budget management
- Real-time budget visualization
- Smart recommendations based on your spending

### PDF Bank Statement Analysis
- Upload and analyze bank statements
- Automatic transaction categorization
- Risk assessment and financial insights
- Interactive spending breakdown charts

### Dark Mode Support
- Consistent theming across all pages
- Professional dark/light mode toggle
- Optimized for extended use

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ifa-s/budgeting-proj.git
   cd budgeting-proj
   ```

2. **Set up Python virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Run database migrations**
   ```bash
   cd budgeting_app
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open your browser**
   Navigate to `http://127.0.0.1:8000/`

## 🔑 Configuration

### Environment Variables

Create a `.env` file in the root directory with:

```env
# AI Service Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Application Settings
DEBUG=True
SECRET_KEY=your_secret_key_here
```

### API Keys Setup

- **OpenRouter API**: Get your key from [OpenRouter](https://openrouter.ai/)
- **Google Gemini API**: Get your key from [Google AI Studio](https://aistudio.google.com/)

## 💡 How It Works

### 1. AI Budget Management
- Chat with the AI about your income, expenses, and financial goals
- The AI creates and manages budget "buckets" for different categories
- Get intelligent recommendations based on your spending patterns

### 2. PDF Bank Statement Analysis
- Upload PDF bank statements for analysis
- AI automatically categorizes transactions
- Generates insights about spending habits and financial risks
- Creates visual charts showing spending breakdown

### 3. Smart Budget Buckets
- Organize your money into percentage-based buckets
- Automatic validation ensures budgets add up to 100%
- Visual charts show allocation and remaining funds

## 🎭 Features in Detail

### AI Chat Assistant
- **Natural Language Processing**: Talk about your finances in plain English
- **Context Awareness**: Remembers your budget state throughout the conversation
- **Smart Recommendations**: Suggests budget optimizations based on your goals
- **Command Processing**: Automatically executes budget changes as you chat

### PDF Analyzer
- **Transaction Categorization**: AI categorizes expenses automatically
- **Risk Assessment**: Identifies potential financial risks in your spending
- **Visual Analytics**: Interactive charts showing spending patterns
- **Export Functionality**: Generate comprehensive budget reports

### Modern UI/UX
- **Glassmorphism Design**: Beautiful frosted glass effects
- **Dark Mode**: Comfortable viewing in any lighting
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **Accessibility**: Designed with accessibility best practices

## 🏗 Architecture

```
budgeting_app/
├── chat/                 # AI Chat Interface
│   ├── models.py        # Chat data models
│   ├── views.py         # Chat API endpoints
│   └── templates/       # Chat UI templates
├── pdf_analyzer/        # PDF Analysis System
│   ├── models.py        # PDF & transaction models
│   ├── views.py         # PDF processing endpoints
│   ├── ai_service.py    # AI analysis integration
│   └── templates/       # PDF analyzer UI
├── backend/             # Core Business Logic
│   ├── buckets/         # Budget bucket management
│   ├── AIM.py          # AI manager
│   └── user_client.py  # User interaction layer
└── budgeting_app/       # Django configuration
```

## 🎯 VTHacks 13 Journey

This project was built during VTHacks 13 with the goal of making personal finance management more accessible and intelligent. We wanted to solve the problem of complex budgeting tools by creating something that feels like having a conversation with a financial advisor.

### What We Learned
- Integrating multiple AI APIs for different use cases
- Building responsive, accessible web interfaces
- Processing and analyzing financial data securely
- Creating intuitive user experiences for complex data

### Challenges Overcome
- Managing state across AI conversations
- Processing PDF bank statements reliably
- Creating a consistent dark mode experience
- Balancing security with user convenience

## 🚧 Future Roadmap

- [ ] **Multi-user Support** - User accounts and authentication
- [ ] **Bank Integration** - Direct connection to banking APIs
- [ ] **Mobile App** - React Native mobile application
- [ ] **Advanced Analytics** - Machine learning spending predictions
- [ ] **Export Options** - CSV, Excel, and PDF report generation
- [ ] **Collaborative Budgets** - Shared budgets for families/couples

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **VTHacks 13** for providing an amazing hackathon experience
- **Virginia Tech** for hosting and supporting student innovation
- **OpenRouter** and **Google** for providing powerful AI APIs
- **The Django Community** for excellent documentation and tools

## 📧 Contact

Built with ❤️ for VTHacks 13 in Blacksburg, VA

**Team**: William (Bill) Campbell, Yashwanth (Yash) Kantheti, Hong Lin, Satwik Harapanahalli

**GitHub**: [ifa-s](https://github.com/ifa-s) [yashkantheti] (https://github.com/YashKantheti) [sho026] (https://github.com/sho026) [SathwikH] (https://github.com/SathwikH)

---

*"Making budgeting as easy as having a conversation"* ✨