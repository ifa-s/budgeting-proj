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

#### 3. Deactivate Virtual Environment
```bash
# When you're done working, deactivate the virtual environment
deactivate
```

### Notes
- Always activate your virtual environment before working on the project
- The virtual environment folder (`venv/`) should be added to `.gitignore`
- Use `pip freeze > requirements.txt` to save your project dependencies


## Backend structure
We want to manage various dynamic-sized buckets to add up to 100, and to complain when they don't add up
Classes:
BucketManager (uses underlaying array/dict/? to manage various buckets, and ensure they add properly)
Bucket (current money, max money, sizing (percent or dollar), etc)
SQLite to store buckets probably
AIManager -- Talks to OpenRouter, provides correct context, runs command when needed etc 

Figure out django stuff -- uhh it's been a minute but lowkey not my problem
Make API for the backend? Essentially translate bucketmanager aspects into easy commands for the ai, with output sent back to it
A

TODO LIST:
Eventually make sqlite db and multiple chats work? --> post-hackathon