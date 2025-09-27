# PDF Bank Statement Analyzer - Setup Guide

This is the second component of the VT Budget Tracker website that provides AI-powered analysis of PDF bank statements using Google's Gemini AI.

## Features

- **PDF Upload**: Upload bank statement PDFs with drag-and-drop interface
- **Transaction Extraction**: Automatically parse transactions, dates, amounts, and categories
- **AI Analysis**: Gemini AI provides personalized financial insights and recommendations
- **Student-Focused**: Tailored advice specifically for Virginia Tech college students
- **Spending Visualization**: Interactive charts showing spending breakdowns by category
- **Real-time Processing**: Track analysis progress with live status updates

## Setup Instructions

### 1. Environment Setup

The project uses a Python virtual environment. Activate it:

```bash
cd /Users/yashk/Desktop/budgeting-proj
source .venv/bin/activate  # On macOS/Linux
# or .venv\Scripts\activate on Windows
```

### 2. Install Dependencies

All required packages should already be installed, but if needed:

```bash
pip install Django==4.2.24 python-dotenv PyPDF2 google-generativeai Pillow openai
```

### 3. Environment Variables

Create a `.env` file in the project root with your Gemini API key:

```bash
# Create .env file
cp env.example .env

# Edit .env file and add your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your .env file

### 4. Database Migrations

Migrations are already applied, but if you need to reset:

```bash
cd budgeting_app
python manage.py makemigrations pdf_analyzer
python manage.py migrate
```

### 5. Run the Development Server

```bash
cd budgeting_app
python manage.py runserver
```

The application will be available at:
- Main chat interface: http://localhost:8000/
- PDF analyzer: http://localhost:8000/pdf-analyzer/

## Usage Guide

### Uploading PDFs

1. Navigate to http://localhost:8000/pdf-analyzer/
2. Drag and drop a PDF bank statement or click to browse
3. Click "Analyze My Statement" to upload and process
4. Wait for processing to complete (typically 30-60 seconds)

### Viewing Results

The analysis results include:
- **Financial Overview**: Income, expenses, and net change
- **Spending Breakdown**: Interactive pie chart by category
- **AI Insights**: Personalized financial advice from Gemini
- **Student Recommendations**: College-specific budgeting tips
- **Transaction List**: Detailed view of all parsed transactions

### Supported Bank Statement Formats

The PDF processor can handle most common bank statement formats that include:
- Transaction dates (MM/DD/YYYY or similar formats)
- Transaction descriptions
- Transaction amounts
- Basic transaction categorization

## Architecture

### Django Apps Structure

```
budgeting_app/
├── budgeting_app/          # Main project settings
├── chat/                   # Existing chat functionality (DO NOT MODIFY)
└── pdf_analyzer/           # New PDF analysis app
    ├── models.py          # Database models
    ├── views.py           # Request handlers
    ├── services.py        # PDF processing logic
    ├── ai_service.py      # Gemini AI integration
    ├── urls.py            # URL routing
    ├── admin.py           # Admin interface
    └── templates/         # HTML templates
```

### Key Components

1. **PDFProcessor** (`services.py`): Extracts text and parses transactions from PDFs
2. **GeminiAnalyzer** (`ai_service.py`): Sends data to Gemini AI for analysis
3. **StudentBudgetAnalyzer** (`ai_service.py`): College-specific spending pattern analysis
4. **Models** (`models.py`): Database schema for uploads, transactions, and analyses

### Database Models

- **PDFUpload**: Stores uploaded files and processing status
- **Transaction**: Individual transactions extracted from PDFs
- **AIAnalysis**: AI-generated insights and recommendations
- **CategorySummary**: Spending totals by category

## API Endpoints

- `POST /pdf-analyzer/upload/`: Upload PDF file
- `GET /pdf-analyzer/status/{id}/`: Check processing status
- `GET /pdf-analyzer/results/{id}/`: View analysis results
- `GET /pdf-analyzer/api/transactions/{id}/`: Get transaction data (JSON)
- `POST /pdf-analyzer/delete/{id}/`: Delete upload and data

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all packages are installed in the virtual environment
2. **PDF Processing Fails**: Check that the PDF contains readable text (not scanned images)
3. **Gemini API Errors**: Verify your API key is correct and has quota remaining
4. **File Upload Issues**: Check Django `MEDIA_ROOT` settings and file permissions

### Error Logs

Check the Django development server output and browser console for error messages. The application includes comprehensive error handling with user-friendly messages.

### Performance

- PDF processing typically takes 10-30 seconds
- Large PDFs (>5MB) may take longer to process
- Gemini API calls add 5-15 seconds to analysis time

## Development Notes

### Extending the Analyzer

To add new transaction categories or improve parsing:

1. Edit the `category_patterns` in `PDFProcessor` class
2. Add new transaction type keywords to `debit_keywords` or `credit_keywords`
3. Update the Gemini prompt in `GeminiAnalyzer._build_analysis_prompt()` for better AI insights

### Adding New Features

The modular architecture makes it easy to add features:
- New analysis types: Extend `StudentBudgetAnalyzer`
- Different file formats: Modify `PDFProcessor` or create new processors
- Enhanced visualizations: Add JavaScript libraries to templates
- Export functionality: Create new views for PDF/CSV export

### Testing

Basic testing can be done by uploading sample bank statement PDFs. Ensure test files:
- Are valid PDF format
- Contain readable transaction data
- Include dates, descriptions, and amounts
- Are under 10MB file size limit

## Security Considerations

- PDF files are stored in `media/pdf_uploads/` directory
- File uploads are limited to 10MB and .pdf extension only
- User data is stored locally in SQLite database
- Gemini AI receives transaction data - review Google's privacy policies
- Consider implementing user authentication for production use

## Production Deployment

For production deployment:

1. Change `DEBUG = False` in Django settings
2. Set up proper database (PostgreSQL recommended)
3. Configure static file serving
4. Set up SSL/HTTPS
5. Implement user authentication and authorization
6. Add file storage backup and cleanup policies
7. Monitor Gemini API usage and costs

## Support

This PDF analyzer integrates seamlessly with the existing budget chat functionality. Users can upload bank statements for detailed analysis and then use the chat interface for ongoing budget management.