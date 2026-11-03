import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'apla-shetkari-default-secret-key-safe-2025'
    
    # On Vercel serverless functions, the file system is read-only except /tmp
    if os.environ.get('VERCEL'):
        DATABASE_PATH = '/tmp/database.db'
        seed_db = BASE_DIR / 'instance' / 'database.db'
        if seed_db.exists() and not Path('/tmp/database.db').exists():
            try:
                shutil.copy(seed_db, '/tmp/database.db')
            except Exception:
                pass
    else:
        INSTANCE_DIR = BASE_DIR / 'instance'
        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        DATABASE_PATH = os.environ.get('DATABASE_PATH') or str(INSTANCE_DIR / 'database.db')
    
    # Google Gemini AI API Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    PORT = int(os.environ.get('PORT', 5000))
