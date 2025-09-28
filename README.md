# 🪣 Bucket Finance - AI-Powered Budgeting Assistant

**Live Site:** [https://bucketfinance.us](https://bucketfinance.us)

A beautiful, modern budgeting application with AI-powered financial analysis and glassmorphism UI design. Built with Django and deployed using Cloudflare Tunnel.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2.24-green.svg)
![Status](https://img.shields.io/badge/status-live-brightgreen.svg)

## ✨ Features

- 🤖 **AI Budget Assistant** - Chat with an intelligent AI for personalized financial advice
- 📊 **PDF Bank Statement Analysis** - Upload and analyze bank statements with detailed spending breakdowns
- 🎨 **Glassmorphism UI** - Modern glass-effect design with light/dark theme support
- 📱 **Responsive Design** - Works beautifully on desktop, tablet, and mobile
- 🔒 **Secure & Fast** - SSL encryption, DDoS protection, and global CDN
- ⚡ **Real-time Processing** - Instant PDF analysis and AI responses

## 🚀 Live Demo

Visit [bucketfinance.us](https://bucketfinance.us) to try the application:

1. **Landing Page** - Beautiful animated introduction
2. **AI Chat** - Get instant budgeting advice and financial guidance
3. **PDF Analyzer** - Upload bank statements for detailed spending analysis

## 🛠️ Technology Stack

- **Backend:** Django 4.2.24, Python 3.9+
- **AI Integration:** OpenRouter API, Google Gemini API
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript
- **Database:** SQLite
- **Deployment:** Cloudflare Tunnel
- **Security:** SSL/HTTPS, CSRF Protection, Security Headers

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/ifa-s/budgeting-proj.git
cd budgeting-proj
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run database migrations**
```bash
cd budgeting_app
python3 manage.py migrate
```

5. **Start the development server**
```bash
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the application.

## 🔧 Configuration

### Required API Keys

Add these to your `.env` file:

- `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai/)
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://aistudio.google.com/)
- `DJANGO_SECRET` - Generate a secure secret key

### Production Settings

For production deployment, update these in your `.env`:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

## 🌐 Deployment

This project is deployed using Cloudflare Tunnel for secure, serverless hosting:

1. **Django** runs with Gunicorn WSGI server
2. **Cloudflare Tunnel** exposes the local server to the internet
3. **SSL/HTTPS** automatically provided by Cloudflare
4. **Global CDN** for fast worldwide access

For detailed deployment instructions, see the setup guides in the project.

## 📱 Architecture

### Core Components

- **`chat/`** - AI-powered budget assistant with conversation interface
- **`pdf_analyzer/`** - Bank statement PDF processing and analysis
- **`templates/`** - Glassmorphism UI templates with theme support

### Key Features

- **Bucket-based Budgeting** - Dynamic budget categories that adapt to spending
- **AI Financial Advice** - Context-aware recommendations based on spending patterns  
- **PDF Processing** - Extract and categorize transactions from bank statements
- **Data Visualization** - Interactive charts and spending breakdowns

## 🎨 Design

The application features a modern **glassmorphism** design with:

- Translucent backgrounds with backdrop blur effects
- Smooth gradients and animations
- Light/dark theme support
- Responsive design for all devices
- Emoji-based navigation icons

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- Originally created for VTHacks hackathon
- Built with modern web technologies and AI integration
- Deployed with Cloudflare for global accessibility

---

**Live at:** [https://bucketfinance.us](https://bucketfinance.us) 🚀