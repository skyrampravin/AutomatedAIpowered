# Day 2: Bot Framework & GitHub Codespaces Deployment

## 🎯 **Goal**: Create a working bot deployed in GitHub Codespaces

**Time Required**: 45-60 minutes  
**Prerequisites**: Day 1 completed (Codespace & Teams setup)  
**Outcome**: Bot responding to messages in Teams via cloud deployment

---

## **Step 1: Update Bot Configuration (10 minutes)**

### 1.1 Enhanced Config Class
1. **Open**: `src/config.py`
2. **Replace** with sandbox-optimized configuration:

```python
"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

import os
import logging
from dotenv import load_dotenv

# Load sandbox environment
load_dotenv('.env.sandbox')

class Config:
    """Sandbox-optimized Bot Configuration"""

    # Server Configuration
    PORT = int(os.environ.get("PORT", 3978))
    
    # Bot Configuration
    APP_ID = os.environ.get("BOT_ID", "")
    APP_PASSWORD = os.environ.get("BOT_PASSWORD", "")
    APP_TYPE = os.environ.get("BOT_TYPE", "")
    APP_TENANTID = os.environ.get("BOT_TENANT_ID", "")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Sandbox Configuration
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "sandbox")
    STORAGE_TYPE = os.environ.get("STORAGE_TYPE", "file")
    DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY", "playground/data")
    LOG_DIRECTORY = os.environ.get("LOG_DIRECTORY", "playground/logs")
    
    @staticmethod
    def validate_environment():
        """Validate sandbox environment configuration"""
        missing = []
        required_vars = ["BOT_ID", "BOT_PASSWORD", "OPENAI_API_KEY"]
        
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)
        
        if missing:
            print(f"❌ Missing required environment variables: {', '.join(missing)}")
            print("Please update your .env.sandbox file with the missing values.")
            return False
        
        # Environment-specific validations
        env = Config.ENVIRONMENT.lower()
        if env == "sandbox":
            print("✅ Sandbox environment detected")
            print(f"   Bot ID: {Config.APP_ID[:8]}...")
            print(f"   OpenAI Model: {Config.OPENAI_MODEL_NAME}")
            print(f"   Storage Type: {Config.STORAGE_TYPE}")
            print(f"   Data Directory: {Config.DATA_DIRECTORY}")
        
        return True
    
    @staticmethod
    def setup_logging():
        """Set up logging for sandbox environment"""
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
```powershell
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

## **Step 2: Create Sandbox Storage System (15 minutes)**

### 2.1 Create SandboxStorage Class
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

### 2.2 Test Storage System
```powershell
# Test the storage system
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

## **Step 3: Update Bot Logic for Sandbox (15 minutes)**

### 3.1 Enhanced Bot Implementation
1. **Replace** `src/bot.py` content:

```python
import os
import sys
import json
import traceback
import logging
from datetime import datetime
from dataclasses import asdict

from botbuilder.core import MemoryStorage, TurnContext, MessageFactory, CardFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from teams import Application, ApplicationOptions, TeamsAdapter
from teams.ai import AIOptions
from teams.ai.models import OpenAIModel, OpenAIModelOptions
from teams.ai.planners import ActionPlanner, ActionPlannerOptions
from teams.ai.prompts import PromptManager, PromptManagerOptions
from teams.state import TurnState

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

# Create AI components
model = OpenAIModel(
    OpenAIModelOptions(
        api_key=config.OPENAI_API_KEY,
        default_model=config.OPENAI_MODEL_NAME,
    )
)

prompts = PromptManager(PromptManagerOptions(prompts_folder=f"{os.getcwd()}/src/prompts"))

planner = ActionPlanner(
    ActionPlannerOptions(
        model=model,
        prompts=prompts,
        default_prompt="chat",
        enable_feedback_loop=True,
    )
)

# Define storage and application
memory_storage = MemoryStorage()
bot_app = Application[TurnState](
    ApplicationOptions(
        bot_app_id=config.APP_ID,
        storage=memory_storage,
        adapter=TeamsAdapter(config),
        ai=AIOptions(planner=planner, enable_feedback_loop=True),
    )
)

@bot_app.message()
async def on_message(context: TurnContext, state: TurnState):
    """Handle incoming messages"""
    user_id = context.activity.from_property.id
    user_name = context.activity.from_property.name or "User"
    message_text = context.activity.text.strip().lower()
    
    logger.info(f"Message from {user_name} ({user_id}): {message_text}")
    
    try:
        # Handle specific commands
        if message_text.startswith('/help'):
            await handle_help_command(context)
        elif message_text.startswith('/enroll'):
            await handle_enroll_command(context, message_text)
        elif message_text.startswith('/profile'):
            await handle_profile_command(context, user_id)
        elif message_text.startswith('/status'):
            await handle_status_command(context)
        elif message_text.startswith('/admin'):
            await handle_admin_command(context, user_id)
        else:
            # Default AI response using the planner
            await bot_app.ai.run(context, state)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Sorry, I encountered an error processing your message. Please try again."
        ))

async def handle_help_command(context: TurnContext):
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
    await context.send_activity(MessageFactory.text(help_text))

async def handle_enroll_command(context: TurnContext, message_text: str):
    """Handle user enrollment"""
    user_id = context.activity.from_property.id
    user_name = context.activity.from_property.name or "User"
    
    # Parse course from command
    parts = message_text.split()
    if len(parts) < 2:
        await context.send_activity(MessageFactory.text(
            "❌ Please specify a course. Example: `/enroll python-basics`\n\n"
            "Available courses: python-basics, javascript-intro, data-science, web-dev"
        ))
        return
    
    course = parts[1]
    available_courses = ["python-basics", "javascript-intro", "data-science", "web-dev"]
    
    if course not in available_courses:
        await context.send_activity(MessageFactory.text(
            f"❌ Course '{course}' not found.\n\n"
            f"Available courses: {', '.join(available_courses)}"
        ))
        return
    
    # Enroll user
    success = storage.enroll_user(user_id, course)
    
    if success:
        profile = storage.get_user_profile(user_id)
        await context.send_activity(MessageFactory.text(
            f"🎉 **Enrollment Successful!**\n\n"
            f"👤 **Student**: {user_name}\n"
            f"📚 **Course**: {course}\n"
            f"📅 **Start Date**: {profile.start_date[:10] if profile.start_date else 'Today'}\n\n"
            f"Welcome to your learning journey! Use `/profile` to check your progress."
        ))
        logger.info(f"User {user_id} enrolled in {course}")
    else:
        await context.send_activity(MessageFactory.text(
            "❌ Enrollment failed. Please try again or contact support."
        ))

async def handle_profile_command(context: TurnContext, user_id: str):
    """Show user profile"""
    profile = storage.get_user_profile(user_id)
    
    if not profile:
        await context.send_activity(MessageFactory.text(
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
    
    await context.send_activity(MessageFactory.text(profile_text))

async def handle_status_command(context: TurnContext):
    """Show bot system status"""
    stats = storage.get_storage_stats()
    
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
    
    await context.send_activity(MessageFactory.text(status_text))

async def handle_admin_command(context: TurnContext, user_id: str):
    """Show admin statistics (simplified for sandbox)"""
    stats = storage.get_storage_stats()
    
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
    
    await context.send_activity(MessageFactory.text(admin_text))

@bot_app.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, state: TurnState):
    """Welcome new members"""
    for member in context.activity.members_added:
        if member.id != context.activity.recipient.id:
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
            await context.send_activity(MessageFactory.text(welcome_text))
```

---

## **Step 4: Set Up Codespace Port Forwarding (5 minutes)**

### 4.1 Start Port Forwarding
```bash
# In your Codespace terminal, start the bot
python src/app.py
```

### 4.2 Configure Port Forwarding
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

### 4.3 Update Teams Developer Portal
1. **Go back** to: https://dev.teams.microsoft.com/
2. **Navigate** to your app → App features → Bot
3. **Update** "Messaging endpoint":
   ```
   https://your-codespace-url.github.dev/api/messages
   ```
   **Or** if using ngrok: `https://abc123.ngrok.io/api/messages`
4. **Click** "Save"

---

## **Step 5: Test Bot in Teams (10 minutes)**

### 5.1 Start the Bot in Codespace
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

### 5.2 Verify Port Forwarding
1. **Check** the PORTS tab shows port 3978 forwarded as public
2. **Visit** your Codespace URL in browser: `https://your-url.github.dev/`
3. **Should see**: "Bot is running!"

### 5.3 Install Bot in Teams
1. **Go to**: Teams Developer Portal
2. **Navigate** to: Preview in Teams
3. **Click** "Preview in Teams"
4. **Click** "Add" to install the bot
5. **Start chatting** with your bot!

### 5.4 Test Bot Commands
Try these commands in Teams:
```
/help
/status
/enroll python-basics
/profile
/admin
```

**✅ Success**: Your bot is now running in GitHub Codespaces and responding in Teams!

---

## **✅ Day 2 Checklist**

Verify all these work:

- [ ] GitHub Codespace is running with all project files
- [ ] Updated `src/config.py` with sandbox configuration
- [ ] Created `src/sandbox_storage.py` with file-based storage
- [ ] Updated `src/bot.py` with sandbox-optimized logic
- [ ] Port 3978 forwarded and publicly accessible in Codespace
- [ ] Bot endpoint updated in Teams Developer Portal
- [ ] Bot running in Codespace without errors
- [ ] Bot installed and responding in Teams
- [ ] All commands work: `/help`, `/enroll`, `/profile`, `/status`
- [ ] User enrollment and profile storage working
- [ ] Playground directory contains user data files

---

## **🚀 What's Next?**

**Day 3**: We'll add AI-powered question generation using OpenAI, creating the foundation for personalized quizzes - all running smoothly in your GitHub Codespace.

---

## **💡 Troubleshooting**

### Common Issues:

**Bot not responding in Teams:**
- Check Codespace port 3978 is forwarded and public
- Verify endpoint URL in Teams Developer Portal
- Ensure bot is running without errors in Codespace

**Codespace issues:**
- Restart Codespace if unresponsive
- Check GitHub account status and billing
- Verify devcontainer.json configuration

**Environment variable errors:**
- Verify `.env` has all required values
- Check BOT_ID and BOT_PASSWORD are correct
- Ensure OpenAI API key is valid

**Storage errors:**
- Check `playground/data` directory exists in Codespace
- Verify write permissions in cloud environment
- Look for error logs in `playground/logs/`

**Port forwarding issues:**
- Set port 3978 visibility to "Public" in PORTS tab
- Update endpoint URL in Teams Developer Portal with new Codespace URL
- Restart port forwarding if connection fails

### Codespace-Specific Commands:
```bash
# Check running services
ps aux | grep python

# Test bot endpoint
curl https://your-codespace-url.github.dev/

# Check port status
ss -tlnp | grep 3978
```

---

**🎉 Success!** Your AI learning bot is now running in GitHub Codespaces and responding to commands in Teams. No firewall restrictions, no local setup required!