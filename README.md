# budgeting-proj

Project for VTHacks

## Setup Instructions

### Python Virtual Environment with Django

Follow these steps to set up a Python virtual environment with the latest Django version:

#### 1. Create a Virtual Environment
```bash
# Create a new virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

#### 2. Install Django
```bash
# Upgrade pip to the latest version
pip install --upgrade pip

# Install the latest Django version
pip install django

# Verify Django installation
python -m django --version
```

#### 3. Create a Django Project (Optional)
```bash
# Create a new Django project
django-admin startproject budgeting_app .

# Run the development server
python manage.py runserver
```

#### 4. Deactivate Virtual Environment
```bash
# When you're done working, deactivate the virtual environment
deactivate
```

### Notes
- Always activate your virtual environment before working on the project
- The virtual environment folder (`venv/`) should be added to `.gitignore`
- Use `pip freeze > requirements.txt` to save your project dependencies
