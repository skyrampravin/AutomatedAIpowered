# Day 2: Bot Framework & Bot Framework Emulator Testing

## 🎯 **Goal**: Create a working bot and test it using Bot Framework Emulator

**Time Required**: 45-60 minutes  
**Prerequisites**: Day 1 completed (Codespace & Bot Framework Emulator installed)  
**Outcome**: Bot responding to messages in Bot Framework Emulator with local testing

---

## **Step 1: Create Bot Configuration (10 minutes)**

### 1.1 Enhanced Config Class
1. **Open**: `src/config.py`
2. **Replace** with local development configuration:

```python
"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

import os
import logging
from dotenv import load_dotenv

# Load local development environment
load_dotenv('.env')

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
```

### 1.2 Test Configuration
```bash
# Test the updated configuration
python -c "
from src.config import Config
if Config.validate_environment():
    print('✅ Configuration is valid!')
else:
    print('❌ Configuration needs fixing')
"
```

---

## **Step 2: Create Local Storage System (15 minutes)**

### 2.1 Create Local Storage Class
1. **Create**: `src/local_storage.py`

```python
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class UserProfile:
    user_id: str
    enrolled_course: Optional[str] = None
    start_date: Optional[str] = None
    total_questions: int = 0
    correct_answers: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_quiz_date: Optional[str] = None
    completed_course: bool = False
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                "difficulty": "medium",
                "notifications": True,
                "quiz_time": "09:00"
            }

@dataclass
class QuizSession:
    session_id: str
    user_id: str
    course: str
    questions: List[Dict[str, Any]]
    answers: List[str]
    score: int
    completed_date: str

class LocalStorage:
    """File-based storage for local development"""
    
    def __init__(self, data_directory: str = "playground/data"):
        self.data_dir = data_directory
        self.users_file = os.path.join(data_directory, "users.json")
        self.sessions_file = os.path.join(data_directory, "quiz_sessions.json")
        self.courses_file = os.path.join(data_directory, "courses.json")
        
        # Ensure directory exists
        os.makedirs(data_directory, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_files(self):
        """Initialize storage files with empty data"""
        files_data = {
            self.users_file: {},
            self.sessions_file: [],
            self.courses_file: {
                "python-basics": {
                    "name": "Python Basics",
                    "description": "Learn fundamental Python programming concepts",
                    "difficulty": "beginner",
                    "estimated_duration": "4 weeks",
                    "topics": ["variables", "functions", "loops", "data structures"]
                },
                "javascript-fundamentals": {
                    "name": "JavaScript Fundamentals", 
                    "description": "Master core JavaScript concepts",
                    "difficulty": "beginner",
                    "estimated_duration": "3 weeks",
                    "topics": ["variables", "functions", "objects", "arrays", "DOM"]
                }
            }
        }
        
        for file_path, default_data in files_data.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
    
    def _load_json_file(self, file_path: str) -> Any:
        """Load and parse JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return {} if file_path != self.sessions_file else []
    
    def _save_json_file(self, file_path: str, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        users = self._load_json_file(self.users_file)
        user_data = users.get(user_id)
        
        if user_data:
            return UserProfile(**user_data)
        return None
    
    def save_user_profile(self, profile: UserProfile) -> bool:
        """Save user profile"""
        users = self._load_json_file(self.users_file)
        users[profile.user_id] = asdict(profile)
        return self._save_json_file(self.users_file, users)
    
    def enroll_user(self, user_id: str, course_id: str) -> bool:
        """Enroll user in a course"""
        profile = self.get_user_profile(user_id)
        
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                enrolled_course=course_id,
                start_date=datetime.now().isoformat()
            )
        else:
            profile.enrolled_course = course_id
            profile.start_date = datetime.now().isoformat()
        
        return self.save_user_profile(profile)
    
    def get_available_courses(self) -> Dict[str, Any]:
        """Get all available courses"""
        return self._load_json_file(self.courses_file)
    
    def save_quiz_session(self, session: QuizSession) -> bool:
        """Save completed quiz session"""
        sessions = self._load_json_file(self.sessions_file)
        sessions.append(asdict(session))
        return self._save_json_file(self.sessions_file, sessions)
    
    def get_user_sessions(self, user_id: str) -> List[QuizSession]:
        """Get all quiz sessions for a user"""
        sessions = self._load_json_file(self.sessions_file)
        user_sessions = [s for s in sessions if s.get('user_id') == user_id]
        return [QuizSession(**session) for session in user_sessions]
    
    def update_user_stats(self, user_id: str, correct_answers: int, total_questions: int) -> bool:
        """Update user statistics after quiz"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return False
        
        profile.total_questions += total_questions
        profile.correct_answers += correct_answers
        profile.last_quiz_date = datetime.now().isoformat()
        
        # Update streak
        if correct_answers == total_questions:
            profile.current_streak += 1
            profile.longest_streak = max(profile.longest_streak, profile.current_streak)
        else:
            profile.current_streak = 0
        
        return self.save_user_profile(profile)
```

### 2.2 Test Storage System
```bash
# Test the storage system
python -c "
from src.local_storage import LocalStorage
storage = LocalStorage()
print('✅ Storage system initialized')
print('Available courses:', list(storage.get_available_courses().keys()))
"
```

---

## **Step 3: Create Sandbox Storage System (15 minutes)**

### 3.1 Create Sandbox Storage Class
1. **Create**: `src/sandbox_storage.py`

```python
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class UserProfile:
    user_id: str
    enrolled_course: Optional[str] = None
    start_date: Optional[str] = None
    total_questions: int = 0
    correct_answers: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_quiz_date: Optional[str] = None
    completed_course: bool = False
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                "difficulty": "medium",
                "notifications": True,
                "quiz_time": "09:00"
            }

@dataclass
class QuizSession:
    session_id: str
    user_id: str
    course: str
    questions: List[Dict[str, Any]]
    answers: List[str]
    score: int
    completed_date: str
    time_taken: int  # seconds

class SandboxStorage:
    """File-based storage system for sandbox development"""
    
    def __init__(self, data_directory: str = "playground/data"):
        self.data_directory = data_directory
        self.logger = logging.getLogger(__name__)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(f"{self.data_directory}/users", exist_ok=True)
        os.makedirs(f"{self.data_directory}/quizzes", exist_ok=True)
        os.makedirs(f"{self.data_directory}/courses", exist_ok=True)
    
    def _get_user_file_path(self, user_id: str) -> str:
        """Get file path for user profile"""
        return f"{self.data_directory}/users/{user_id}_profile.json"
    
    def _get_quiz_file_path(self, user_id: str) -> str:
        """Get file path for user quiz history"""
        return f"{self.data_directory}/quizzes/{user_id}_quizzes.json"
    
    def enroll_user(self, user_id: str, course: str) -> bool:
        """Enroll a user in a course"""
        try:
            profile = self.get_user_profile(user_id)
            if profile is None:
                profile = UserProfile(
                    user_id=user_id,
                    enrolled_course=course,
                    start_date=datetime.now().isoformat()
                )
            else:
                profile.enrolled_course = course
                if profile.start_date is None:
                    profile.start_date = datetime.now().isoformat()
            
            self.save_user_profile(profile)
            self.logger.info(f"User {user_id} enrolled in course {course}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enroll user {user_id}: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        try:
            file_path = self._get_user_file_path(user_id)
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
                return UserProfile(**data)
                
        except Exception as e:
            self.logger.error(f"Failed to get user profile for {user_id}: {e}")
            return None
    
    def save_user_profile(self, profile: UserProfile) -> bool:
        """Save user profile"""
        try:
            file_path = self._get_user_file_path(profile.user_id)
            with open(file_path, 'w') as f:
                json.dump(asdict(profile), f, indent=2)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save user profile: {e}")
            return False
    
    def save_quiz_session(self, session: QuizSession) -> bool:
        """Save quiz session"""
        try:
            file_path = self._get_quiz_file_path(session.user_id)
            
            # Load existing sessions
            sessions = []
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    sessions = json.load(f)
            
            # Add new session
            sessions.append(asdict(session))
            
            # Save updated sessions
            with open(file_path, 'w') as f:
                json.dump(sessions, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save quiz session: {e}")
            return False
    
    def get_user_quiz_history(self, user_id: str) -> List[QuizSession]:
        """Get user's quiz history"""
        try:
            file_path = self._get_quiz_file_path(user_id)
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r') as f:
                sessions_data = json.load(f)
                return [QuizSession(**session) for session in sessions_data]
                
        except Exception as e:
            self.logger.error(f"Failed to get quiz history for {user_id}: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for monitoring"""
        try:
            stats = {
                "total_users": 0,
                "total_quizzes": 0,
                "enrolled_users": 0,
                "active_courses": set(),
                "storage_size_mb": 0
            }
            
            # Count users
            users_dir = f"{self.data_directory}/users"
            if os.path.exists(users_dir):
                user_files = [f for f in os.listdir(users_dir) if f.endswith('_profile.json')]
                stats["total_users"] = len(user_files)
                
                # Count enrolled users and courses
                for user_file in user_files:
                    user_path = os.path.join(users_dir, user_file)
                    try:
                        with open(user_path, 'r') as f:
                            profile_data = json.load(f)
                            if profile_data.get('enrolled_course'):
                                stats["enrolled_users"] += 1
                                stats["active_courses"].add(profile_data['enrolled_course'])
                    except:
                        continue
            
            # Count quizzes
            quizzes_dir = f"{self.data_directory}/quizzes"
            if os.path.exists(quizzes_dir):
                for quiz_file in os.listdir(quizzes_dir):
                    if quiz_file.endswith('_quizzes.json'):
                        quiz_path = os.path.join(quizzes_dir, quiz_file)
                        try:
                            with open(quiz_path, 'r') as f:
                                sessions = json.load(f)
                                stats["total_quizzes"] += len(sessions)
                        except:
                            continue
            
            # Calculate storage size
            def get_dir_size(path):
                total = 0
                if os.path.exists(path):
                    for dirpath, dirnames, filenames in os.walk(path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            total += os.path.getsize(filepath)
                return total
            
            storage_bytes = get_dir_size(self.data_directory)
            stats["storage_size_mb"] = round(storage_bytes / (1024 * 1024), 2)
            stats["active_courses"] = list(stats["active_courses"])
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get storage stats: {e}")
            return {}
```

### 3.2 Test Sandbox Storage System
```bash
# Test the sandbox storage system
python -c "
from src.sandbox_storage import SandboxStorage, UserProfile
from src.config import Config

# Initialize storage
storage = SandboxStorage(Config.DATA_DIRECTORY)

# Test user enrollment
success = storage.enroll_user('test_user', 'python-basics')
print(f'Enrollment: {\"✅\" if success else \"❌\"}')

# Test profile retrieval
profile = storage.get_user_profile('test_user')
print(f'Profile loaded: {\"✅\" if profile else \"❌\"}')

# Test stats
stats = storage.get_storage_stats()
print(f'Stats: {stats}')
"
```

---

## **Step 4: Update Bot Logic for Sandbox (15 minutes)**

### 4.1 Enhanced Bot Implementation
1. **Replace** `src/bot.py` content:

```python
import os
import sys
import json
import traceback
import logging
from datetime import datetime
from dataclasses import asdict

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes

from config import Config
from sandbox_storage import SandboxStorage, UserProfile

# Set up logging
logger = Config.setup_logging()

# Initialize configuration
config = Config()
if not config.validate_environment():
    logger.error("❌ Configuration validation failed")
    sys.exit(1)

# Initialize sandbox storage
storage = SandboxStorage(config.DATA_DIRECTORY)

class EchoBot(ActivityHandler):
    """Bot Framework Emulator Compatible Bot"""
    
    def __init__(self):
        super().__init__()
        self.storage = storage
        self.config = config
        self.logger = logger
        
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""
        user_id = turn_context.activity.from_property.id
        user_name = turn_context.activity.from_property.name or "User"
        message_text = turn_context.activity.text.strip().lower() if turn_context.activity.text else ""
        
        self.logger.info(f"Message from {user_name} ({user_id}): {message_text}")
        
        try:
            # Handle specific commands
            if message_text.startswith('/help'):
                await self.handle_help_command(turn_context)
            elif message_text.startswith('/enroll'):
                await self.handle_enroll_command(turn_context, message_text)
            elif message_text.startswith('/profile'):
                await self.handle_profile_command(turn_context, user_id)
            elif message_text.startswith('/status'):
                await self.handle_status_command(turn_context)
            elif message_text.startswith('/admin'):
                await self.handle_admin_command(turn_context, user_id)
            else:
                # Default response for non-command messages
                await turn_context.send_activity(MessageFactory.text(
                    f"Hello {user_name}! I received your message: '{turn_context.activity.text}'. Try /help to see available commands."
                ))
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            await turn_context.send_activity(MessageFactory.text(
                "❌ Sorry, I encountered an error processing your message. Please try again."
            ))

    async def handle_help_command(self, turn_context: TurnContext):
        """Show help information"""
        help_text = """
🤖 **AI Learning Bot - Sandbox Mode** 🤖

**Available Commands:**
• `/help` - Show this help message
• `/enroll [course]` - Enroll in a learning course
• `/profile` - View your learning profile
• `/status` - Check bot system status
• `/admin` - View system statistics (admin only)

**Available Courses:**
• `python-basics` - Python fundamentals
• `javascript-intro` - JavaScript introduction  
• `data-science` - Data Science concepts
• `web-dev` - Web Development

**Example:**
`/enroll python-basics`

**Getting Started:**
1. Enroll in a course using `/enroll [course-name]`
2. Check your profile with `/profile`
3. Start learning! (Quiz feature coming in Day 4)

*Running in sandbox mode with file-based storage*
"""
        await turn_context.send_activity(MessageFactory.text(help_text))

    async def handle_enroll_command(self, turn_context: TurnContext, message_text: str):
        """Handle user enrollment"""
        user_id = turn_context.activity.from_property.id
        user_name = turn_context.activity.from_property.name or "User"
        
        # Parse course from command
        parts = message_text.split()
        if len(parts) < 2:
            await turn_context.send_activity(MessageFactory.text(
                "❌ Please specify a course. Example: `/enroll python-basics`\n\n"
                "Available courses: python-basics, javascript-intro, data-science, web-dev"
            ))
            return
        
        course = parts[1]
        available_courses = ["python-basics", "javascript-intro", "data-science", "web-dev"]
        
        if course not in available_courses:
            await turn_context.send_activity(MessageFactory.text(
                f"❌ Course '{course}' not found.\n\n"
                f"Available courses: {', '.join(available_courses)}"
            ))
            return
        
        # Enroll user
        success = self.storage.enroll_user(user_id, course)
        
        if success:
            profile = self.storage.get_user_profile(user_id)
            await turn_context.send_activity(MessageFactory.text(
                f"🎉 **Enrollment Successful!**\n\n"
                f"👤 **Student**: {user_name}\n"
                f"📚 **Course**: {course}\n"
                f"📅 **Start Date**: {profile.start_date[:10] if profile.start_date else 'Today'}\n\n"
                f"Welcome to your learning journey! Use `/profile` to check your progress."
            ))
            self.logger.info(f"User {user_id} enrolled in {course}")
        else:
            await turn_context.send_activity(MessageFactory.text(
                "❌ Enrollment failed. Please try again or contact support."
            ))

    async def handle_profile_command(self, turn_context: TurnContext, user_id: str):
        """Show user profile"""
        profile = self.storage.get_user_profile(user_id)
        
        if not profile:
            await turn_context.send_activity(MessageFactory.text(
                "❌ **No Profile Found**\n\n"
                "You haven't enrolled in any courses yet.\n"
                "Use `/enroll [course-name]` to get started!"
            ))
            return
        
        # Calculate progress percentage
        progress_percent = 0
        if profile.total_questions > 0:
            progress_percent = round((profile.correct_answers / profile.total_questions) * 100, 1)
        
        profile_text = f"""
👤 **Learning Profile**

📚 **Course**: {profile.enrolled_course or 'Not enrolled'}
📅 **Started**: {profile.start_date[:10] if profile.start_date else 'Unknown'}
❓ **Questions Answered**: {profile.total_questions}
✅ **Correct Answers**: {profile.correct_answers}
📊 **Accuracy**: {progress_percent}%
🔥 **Current Streak**: {profile.current_streak} days
🏆 **Best Streak**: {profile.longest_streak} days
📝 **Last Quiz**: {profile.last_quiz_date[:10] if profile.last_quiz_date else 'Never'}
🎯 **Course Complete**: {'✅ Yes' if profile.completed_course else '❌ In Progress'}

*Quiz feature coming in Day 4! Stay tuned! 🚀*
"""
        
        await turn_context.send_activity(MessageFactory.text(profile_text))

    async def handle_status_command(self, turn_context: TurnContext):
        """Show bot system status"""
        stats = self.storage.get_storage_stats()
        
        status_text = f"""
🤖 **Bot System Status - Sandbox Mode**

🟢 **Status**: Online and Running
📊 **Statistics**:
  • Total Users: {stats.get('total_users', 0)}
  • Enrolled Users: {stats.get('enrolled_users', 0)}
  • Total Quizzes: {stats.get('total_quizzes', 0)}
  • Active Courses: {len(stats.get('active_courses', []))}
  • Storage Used: {stats.get('storage_size_mb', 0)} MB

🏠 **Environment**: Sandbox (File-based storage)
💾 **Data Location**: playground/data/
📝 **Logs**: playground/logs/

**System Health**: ✅ All systems operational
"""
        
        await turn_context.send_activity(MessageFactory.text(status_text))

    async def handle_admin_command(self, turn_context: TurnContext, user_id: str):
        """Show admin statistics (simplified for sandbox)"""
        stats = self.storage.get_storage_stats()
        
        admin_text = f"""
🔧 **Admin Dashboard - Sandbox Mode**

📈 **User Statistics**:
  • Total Registered: {stats.get('total_users', 0)}
  • Currently Enrolled: {stats.get('enrolled_users', 0)}
  • Total Quiz Sessions: {stats.get('total_quizzes', 0)}

📚 **Course Statistics**:
  • Active Courses: {', '.join(stats.get('active_courses', [])) or 'None'}

💾 **Storage Information**:
  • Storage Type: File-based (Sandbox)
  • Storage Size: {stats.get('storage_size_mb', 0)} MB
  • Data Location: playground/data/

🔍 **System Health**: All services operational

*Note: This is sandbox mode. Full admin features available in production mode.*
"""
        
        await turn_context.send_activity(MessageFactory.text(admin_text))

    async def on_members_added_activity(self, members_added: list, turn_context: TurnContext):
        """Welcome new members"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_text = f"""
🎉 **Welcome to AI Learning Bot!** 🎉

Hello! I'm your AI-powered learning assistant running in sandbox mode.

🚀 **Quick Start:**
1. Type `/help` to see all commands
2. Use `/enroll [course-name]` to join a course
3. Check `/profile` to track your progress

📚 **Available Courses:**
• python-basics
• javascript-intro  
• data-science
• web-dev

Ready to start learning? Try: `/enroll python-basics`

*Currently running in sandbox mode for development and testing.*
"""
                await turn_context.send_activity(MessageFactory.text(welcome_text))

# Create bot instance
bot_app = EchoBot()
```

---

## **Step 5: Set Up Codespace Port Forwarding (5 minutes)**

### 5.1 Start Port Forwarding
```bash
# In your Codespace terminal, start the bot
python src/app.py
```

### 5.2 Configure Port Forwarding
1. **In Codespace**, look for "PORTS" tab at bottom of VS Code
2. **If port 3978 isn't listed**, click "Add Port" 
3. **Enter**: `3978`
4. **Set visibility**: Public (click the lock icon to change)
5. **Copy** the forwarded URL (e.g., `https://username-ai-learning-bot-abc123.github.dev`)

**🎉 Success**: Your bot is now accessible via HTTPS without any firewall issues!

### 🚀 **Alternative: Use Built-in ngrok**

If you prefer ngrok, Codespaces has it pre-installed:
```bash
# In a new terminal (keep bot running)
ngrok http 3978
```

### 5.3 Verify Bot is Running
1. **Check** that your bot is running in the terminal:
   ```bash
   # You should see output like:
   # ✅ Local development environment detected
   # Bot is running on port 3978
   # Bot is ready!
   ```

2. **Test the endpoint** (optional):
   ```bash
   # In a new terminal, test if the bot endpoint responds
   curl http://localhost:3978/api/messages
   # Should return: Method Not Allowed (405) - this is expected
   ```

3. **Note your bot URL** for the emulator:
   - **Local testing**: `http://localhost:3978/api/messages`
   - **Codespace forwarded**: `https://your-codespace-url.github.dev/api/messages`

**💡 Important**: For Bot Framework Emulator testing, you don't need to configure any external services like Teams Developer Portal. The emulator connects directly to your local bot.

---

## **Step 6: Test Bot with Bot Framework Emulator (15 minutes)**

### 6.1 Start the Bot in Codespace
```bash
# In your Codespace terminal
python src/app.py
```

**Expected output**:
```
Bot is running on port 3978
Bot is ready!
Listening for messages...
```

### 6.2 Connect Bot Framework Emulator
1. **Open** Bot Framework Emulator on your local machine
2. **Click** "Open Bot" or "Create a new bot configuration"
3. **Enter Bot URL**: `http://localhost:3978/api/messages`
4. **Leave** Microsoft App ID and Password **empty** (for local testing)
5. **Click** "Connect"

**💡 Important**: For local development with emulator, you don't need real Microsoft App credentials. Leave the App ID and Password fields empty.

### 6.3 Test Basic Bot Commands
Type these commands in the emulator chat window:

```
🔍 Basic Commands:
/help              # Show available commands
/status            # Check bot status

👤 User Commands:
/enroll python-basics    # Enroll in course
/profile                 # View user profile
/progress               # Show learning progress

🔧 Admin Commands:
/admin                  # Admin panel
/stats                  # System statistics
```

### 6.4 Verify Bot Responses
You should see responses like:

**For `/help` command:**
```
🤖 AI Learning Bot Commands:

📚 Learning:
/enroll [course] - Enroll in a course
/quiz - Start daily quiz (coming in Day 3)
/progress - View your progress

👤 Profile:
/profile - View your learning profile
/settings - Update preferences

ℹ️ Information:
/help - Show this help
/status - Bot status
```

**For `/enroll python-basics`:**
```
✅ Successfully enrolled in Python Basics!

📚 Course: Python Basics  
🎯 Level: Beginner
⏱️ Duration: 4 weeks
📝 Daily quizzes will be available starting Day 3

Type /profile to view your enrollment details!
```

### 6.5 Debug Features in Emulator
The Bot Framework Emulator provides excellent debugging capabilities:

1. **Inspector Panel**: See message JSON structure
2. **Log Panel**: View detailed bot logs
3. **Conversation History**: Navigate through message history
4. **Network Traffic**: Monitor HTTP requests/responses

**✅ Success Indicators:**
- Bot connects without errors
- All commands respond appropriately
- User enrollment saves successfully
- Profile shows correct information
- No error messages in console or emulator

---

## **✅ Day 2 Checklist**

Verify all these work in Bot Framework Emulator:

### **Development Environment**
- [ ] GitHub Codespace is running with all project files
- [ ] Updated `src/config.py` with local development configuration
- [ ] Created `src/local_storage.py` with file-based storage
- [ ] Bot starts without errors in Codespace
- [ ] Environment variables loaded correctly

### **Bot Framework Emulator Testing**
- [ ] Bot Framework Emulator installed and launched
- [ ] Bot connects to emulator without errors
- [ ] Bot responds to `/help` command with command list
- [ ] User can enroll with `/enroll python-basics`
- [ ] Profile shows enrollment with `/profile`
- [ ] Status command shows bot information
- [ ] All commands work without errors

### **Data Persistence**
- [ ] User enrollment saves to local files
- [ ] Profile information persists between conversations
- [ ] Playground directory contains user data files
- [ ] Logs being written to `playground/logs/`
- [ ] Configuration validation passes

### **Debugging Capabilities**
- [ ] Can see conversation JSON in emulator
- [ ] Bot logs appear in emulator log panel
- [ ] Message flow is clear and debuggable
- [ ] No error messages in console

---

## **🚀 What's Next?**

**Day 3**: We'll add AI-powered question generation using OpenAI. The Bot Framework Emulator is perfect for testing AI features because you can see the full conversation flow and debug any issues with the AI responses.

---

## **💡 Troubleshooting**

### **Bot Framework Emulator Issues:**

**Issue**: Emulator won't connect to bot  
**Solution**: 
- Verify bot is running on port 3978
- Check URL is `http://localhost:3978/api/messages`
- Leave App ID and Password empty
- Try restarting both bot and emulator

**Issue**: Bot not responding to commands  
**Solution**:
- Check console for error messages
- Verify bot.py handles message routing correctly
- Check environment variables are loaded
- Look at emulator log panel for details

**Issue**: "Connection refused" error  
**Solution**:
- Ensure port 3978 is forwarded in Codespace
- Check bot is actually listening on port 3978
- Verify no firewall blocking the connection

### **Configuration Issues:**

**Issue**: Environment variables not loading  
**Solution**:
- Check `.env` file exists and has correct syntax
- Verify no extra spaces in environment variables
- Test with `Config.validate_environment()`

**Issue**: Storage errors  
**Solution**:
- Check `playground/data` directory exists
- Verify write permissions in Codespace
- Look for error logs in `playground/logs/`

### **Codespace Issues:**

**Issue**: Port forwarding not working  
**Solution**:
- Check PORTS tab in Codespace
- Manually add port 3978 if not forwarded
- Set port visibility to "Public" if needed

**Issue**: Bot crashes on startup  
**Solution**:
- Check requirements.txt dependencies installed
- Verify Python syntax in all files
- Look at console error messages

### **Testing Commands:**

```bash
# Check if bot is running
ps aux | grep python

# Test bot endpoint
curl http://localhost:3978/

# Check port status
ss -tlnp | grep 3978

# Verify environment loading
python -c "from src.config import Config; Config.validate_environment()"

# Test storage system
python -c "from src.local_storage import LocalStorage; print('Storage OK')"
```

### **Emulator Benefits for Learning:**
- ✅ **No subscription required** - Works completely offline
- ✅ **Perfect debugging** - See every message and response
- ✅ **Easy testing** - Instant feedback on your bot logic
- ✅ **JSON inspection** - Understand bot framework message structure
- ✅ **Local development** - No network dependencies

---

**🎉 Success!** Your AI learning bot is now running locally and responding to commands in Bot Framework Emulator. You have a solid foundation for adding AI-powered features without any external dependencies or subscription requirements!
```bash
# In your Codespace terminal
python src/app.py
```

#### C.2 Test via Azure Portal
1. **Go to**: Azure Portal → Your Bot Resource
2. **Click** "Test in Web Chat"
3. **Update** messaging endpoint to your Codespace URL
4. **Test** the bot directly in Azure

#### C.3 Enable Additional Channels
From Azure Portal, you can connect to:
- Microsoft Teams (when available)
- Slack
- Facebook Messenger
- Direct Line (for custom apps)

### **Universal Testing Commands**

Regardless of your testing method, try these commands:

```
🔍 Basic Commands:
/help              # Show available commands
/status            # Check bot status

👤 User Commands:
/enroll python-basics    # Enroll in course
/profile                 # View user profile
/progress               # Show learning progress

🔧 Admin Commands:
/admin                  # Admin panel
/stats                  # System statistics
/logs                   # Recent activity
```

### **Testing Validation Checklist**

Verify these work in your chosen testing environment:

- [ ] Bot responds to `/help` command
- [ ] User can enroll with `/enroll python-basics`
- [ ] Profile shows enrollment with `/profile`
- [ ] Status command shows bot information
- [ ] Admin commands work (if configured)
- [ ] User data persists between conversations
- [ ] Error messages are user-friendly

### **Expected Responses**

**For `/help` command:**
```
🤖 AI Learning Bot Commands:

📚 Learning:
/enroll [course] - Enroll in a course
/quiz - Start daily quiz
/progress - View your progress

👤 Profile:
/profile - View your learning profile
/settings - Update preferences

ℹ️ Information:
/help - Show this help
/status - Bot status
```

**For `/enroll python-basics`:**
```
✅ Successfully enrolled in Python Basics!

📚 Course: Python Basics
🎯 Level: Beginner
⏱️ Duration: 4 weeks
📝 Daily quizzes available

Type /quiz to start your first quiz!
```

---

## **✅ Day 2 Checklist**

Verify based on your testing approach:

### **Common Requirements (All Setups)**
- [ ] GitHub Codespace is running with all project files
- [ ] Updated `src/config.py` with appropriate configuration
- [ ] Created `src/sandbox_storage.py` with file-based storage
- [ ] Updated `src/bot.py` with framework logic
- [ ] Bot starts without errors in Codespace
- [ ] Environment variables loaded correctly

### **Setup A: Teams Testing**
- [ ] Port 3978 forwarded and publicly accessible in Codespace
- [ ] Bot endpoint updated in Teams Developer Portal
- [ ] Bot installed and responding in Teams
- [ ] All commands work in Teams chat

### **Setup B: Bot Framework Emulator**
- [ ] Bot Framework Emulator installed and connected
- [ ] Bot responds to commands in emulator
- [ ] Can see message JSON and debug info
- [ ] Local testing working properly

### **Setup C: Azure Bot Service**
- [ ] Azure Bot resource configured
- [ ] Messaging endpoint updated in Azure Portal
- [ ] Web Chat testing works
- [ ] Bot responds in Azure test interface

### **Data Verification (All Setups)**
- [ ] User enrollment and profile storage working
- [ ] Playground directory contains user data files
- [ ] Logs being written to `playground/logs/`
- [ ] Configuration validation passes

---

## **🚀 What's Next?**

**Day 3**: We'll add AI-powered question generation using OpenAI. This works identically across all testing environments - the AI features are the same whether you're testing in Teams, Emulator, or Azure Bot Service.

---

## **💡 Troubleshooting**

### **Teams Testing Issues:**
**Bot not responding in Teams:**
- Check Codespace port 3978 is forwarded and public
- Verify endpoint URL in Teams Developer Portal
- Ensure bot is running without errors in Codespace

### **Bot Framework Emulator Issues:**
**Emulator won't connect:**
- Check bot is running on localhost:3978
- Verify endpoint URL: `http://localhost:3978/api/messages`
- Leave App ID/Password empty for local testing

**Messages not showing:**
- Check console for errors
- Verify bot configuration
- Try restarting both bot and emulator

### **Azure Bot Service Issues:**
**Web Chat not working:**
- Verify messaging endpoint in Azure Portal
- Check bot credentials match Azure registration
- Ensure Codespace URL is public and accessible

### **Common Issues (All Setups):**
**Environment variable errors:**
- Verify `.env` has all required values based on your setup
- Check BOT_ID and BOT_PASSWORD match your registration
- Ensure OpenAI API key is valid

**Storage errors:**
- Check `playground/data` directory exists in Codespace
- Verify write permissions in cloud environment
- Look for error logs in `playground/logs/`

**Codespace issues:**
- Restart Codespace if unresponsive
- Check GitHub account status and billing
- Verify devcontainer.json configuration

### **Testing Commands by Environment:**

**Codespace Terminal:**
```bash
# Check running services
ps aux | grep python

# Test bot endpoint
curl http://localhost:3978/

# Check port status
ss -tlnp | grep 3978
```

**Teams Testing:**
```bash
# Test public endpoint
curl https://your-codespace-url.github.dev/
```

**Local Testing:**
```bash
# Test local endpoint
curl http://localhost:3978/api/messages
```

---

**🎉 Success!** Your AI learning bot is now running locally and responding to commands in Bot Framework Emulator. You have a solid foundation for adding AI-powered features without any external dependencies or subscription requirements!