import os
import logging
from dotenv import load_dotenv

# Load local development environment - look for .env in parent directory first
if os.path.exists('../.env'):
    load_dotenv('../.env')
elif os.path.exists('.env'):
    load_dotenv('.env')
else:
    load_dotenv()  # Look in default locations

class Config:
    """Bot Framework Emulator Configuration"""

    # Server Configuration
    PORT = int(os.environ.get("PORT", 3978))
    
    # Bot Configuration (for local testing, these can be dummy values)
    APP_ID = os.environ.get("BOT_ID", "")
    APP_PASSWORD = os.environ.get("BOT_PASSWORD", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Local Development Configuration
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "local-development")
    STORAGE_TYPE = os.environ.get("STORAGE_TYPE", "file")
    DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY", "playground/data")
    LOG_DIRECTORY = os.environ.get("LOG_DIRECTORY", "playground/logs")
    
    @staticmethod
    def validate_environment():
        """Validate local development environment configuration"""
        missing = []
        required_vars = ["OPENAI_API_KEY"]  # BOT_ID and BOT_PASSWORD not required for emulator
        
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)
        
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            print("Please update your .env file with the missing values.")
            return False
        
        # Environment-specific validations
        env = Config.ENVIRONMENT.lower()
        if env == "local-development":
            print("✅ Local development environment detected")
            print(f"   Bot ID: {Config.APP_ID or 'Using emulator defaults'}")
            print(f"   OpenAI Model: {Config.OPENAI_MODEL_NAME}")
            print(f"   Storage Type: {Config.STORAGE_TYPE}")
            print(f"   Data Directory: {Config.DATA_DIRECTORY}")
        
        return True
    
    @staticmethod
    def setup_logging():
        """Set up logging for local development"""
        os.makedirs(Config.LOG_DIRECTORY, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{Config.LOG_DIRECTORY}/bot.log'),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)
