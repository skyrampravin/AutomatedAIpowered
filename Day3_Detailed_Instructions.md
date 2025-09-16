# Day 3: Detailed Step-by-Step Instructions - Bot Development in Sandbox

## Important: Sandbox Development Environment
**This day focuses on core bot development using your sandbox environment from Day 1.** You can complete all Day 3 tasks using your sandbox bot and `env/.env.playground` configuration, without needing Azure infrastructure deployment.

## Task 1: Review Existing Bot Code Structure (20 minutes)

### 1.1 Understanding the Bot Framework
1. Open `src/bot.py` in VS Code
2. Review the current structure:
   - **Teams AI Library**: Uses Microsoft Teams AI SDK
   - **OpenAI Integration**: Model configuration for AI responses
   - **Prompt Management**: Handles AI prompts and responses
   - **Application Setup**: Bot application with memory storage
3. Understand key components:
   ```python
   # Model configuration (OpenAI or Azure OpenAI)
   model = OpenAIModel(OpenAIModelOptions(...))
   
   # Prompt management system
   prompts = PromptManager(PromptManagerOptions(...))
   
   # AI planner for handling responses
   planner = ActionPlanner(ActionPlannerOptions(...))
   
   # Main bot application
   bot_app = Application[TurnState](ApplicationOptions(...))
   ```

### 1.2 Understanding the Web Server
1. Open `src/app.py` and review:
   - **HTTP Server**: Uses aiohttp for async web server
   - **Message Endpoint**: `/api/messages` route for Teams communication
   - **Bot Processing**: Routes Teams messages to bot logic
2. Understand the flow:
   ```
   Teams → /api/messages → bot_app.process() → bot.py logic → Response
   ```

**Sandbox Testing**: You can run this locally with ngrok or dev tunnels to test with your sandbox bot.

### 1.3 Configuration Management
1. Open `src/config.py` and review:
   - **Environment Variables**: Loads from .env files
   - **Bot Credentials**: APP_ID, APP_PASSWORD, etc.
   - **OpenAI Configuration**: API keys and model settings
2. Verify your `env/.env.playground` has all required environment variables from Day 1
3. **For sandbox development**: Ensure you're using the playground environment configuration

## Task 2: Design User Enrollment System (30 minutes)

### 2.1 Define Data Models
1. **Create data structures** for user enrollment:
   ```python
   # User enrollment data structure
   class UserEnrollment:
       user_id: str
       course_id: str
       enrollment_date: datetime
       current_day: int
       total_days: int = 30
       status: str = "active"  # active, completed, paused
   
   # User progress tracking
   class UserProgress:
       user_id: str
       course_id: str
       day: int
       questions_answered: int
       correct_answers: int
       wrong_answers: List[dict]
       completion_date: Optional[datetime]
   ```

2. **Plan storage options**:
   - **Simple approach**: JSON files or in-memory storage (for development)
   - **Production approach**: Azure Table Storage or Cosmos DB
   - **For Day 3**: Use simple file-based storage to focus on logic

### 2.2 Design Enrollment Flow
1. **User Commands**:
   - `/enroll [course_name]` - Enroll in a course
   - `/status` - Check current progress
   - `/courses` - List available courses
2. **Enrollment Process**:
   ```
   User sends /enroll → Check if already enrolled → Create enrollment record → 
   Send welcome message → Schedule first day questions
   ```

### 2.3 Create Storage Helper Functions
1. **For sandbox development**: Design simple file-based storage functions:
   ```python
   def save_user_enrollment(user_id: str, course_id: str) -> bool
   def get_user_enrollment(user_id: str) -> Optional[UserEnrollment]
   def update_user_progress(user_id: str, day: int, progress: dict) -> bool
   def get_user_progress(user_id: str, day: int) -> Optional[UserProgress]
   ```

2. **Storage strategy for sandbox**:
   - Use JSON files in `playground/` directory
   - Simple, fast development without external dependencies
   - Easy to inspect and debug during development
   - Can be migrated to Azure Storage later

## Task 3: Implement User Enrollment Logic (45 minutes)

### 3.1 Create Sandbox Storage Module
1. **Create `src/storage.py`** for sandbox development:
   ```python
   import json
   import os
   from datetime import datetime
   from typing import Optional, List, Dict
   from dataclasses import dataclass, asdict
   
   @dataclass
   class UserEnrollment:
       user_id: str
       course_id: str
       enrollment_date: str
       current_day: int
       total_days: int = 30
       status: str = "active"
   
   @dataclass
   class UserProgress:
       user_id: str
       course_id: str
       day: int
       questions_answered: int
       correct_answers: int
       wrong_questions: List[Dict]
       completed_at: Optional[str] = None
   
   class SandboxStorage:
       """Simple file-based storage for sandbox development"""
       def __init__(self, storage_dir: str = "playground"):
           self.storage_dir = storage_dir
           self.ensure_directories()
       
       def ensure_directories(self):
           """Create necessary directories for file storage"""
           os.makedirs(f"{self.storage_dir}/progress", exist_ok=True)
           os.makedirs(f"{self.storage_dir}/courses", exist_ok=True)
       
       def save_user_enrollment(self, enrollment: UserEnrollment) -> bool:
           """Save user enrollment to JSON file"""
           try:
               enrollments_file = f"{self.storage_dir}/enrollments.json"
               enrollments = {}
               if os.path.exists(enrollments_file):
                   with open(enrollments_file, 'r') as f:
                       enrollments = json.load(f)
               
               enrollments[enrollment.user_id] = asdict(enrollment)
               
               with open(enrollments_file, 'w') as f:
                   json.dump(enrollments, f, indent=2)
               return True
           except Exception as e:
               print(f"Error saving enrollment: {e}")
               return False
   ```

2. **Add storage methods for progress tracking**:
   ```python
       def get_user_enrollment(self, user_id: str) -> Optional[UserEnrollment]:
           """Get user enrollment from JSON file"""
           try:
               enrollments_file = f"{self.storage_dir}/enrollments.json"
               if not os.path.exists(enrollments_file):
                   return None
               
               with open(enrollments_file, 'r') as f:
                   enrollments = json.load(f)
               
               if user_id in enrollments:
                   data = enrollments[user_id]
                   return UserEnrollment(**data)
               return None
           except Exception as e:
               print(f"Error loading enrollment: {e}")
               return None
   ```

**Sandbox Benefits**: This approach allows rapid development and testing without external dependencies.
       def __init__(self, data_dir="data"):
           self.data_dir = data_dir
           os.makedirs(data_dir, exist_ok=True)
       
       def save_enrollment(self, enrollment: UserEnrollment) -> bool:
           # Implementation for saving enrollment
           pass
       
       def get_enrollment(self, user_id: str) -> Optional[UserEnrollment]:
           # Implementation for retrieving enrollment
           pass
       
       def save_progress(self, progress: UserProgress) -> bool:
           # Implementation for saving daily progress
           pass
       
       def get_progress(self, user_id: str, day: int) -> Optional[UserProgress]:
           # Implementation for retrieving progress
           pass
   ```

### 3.2 Update Bot Logic for Sandbox Enrollment
1. **Modify `src/bot.py`** to add enrollment handlers for sandbox:
   ```python
   from storage import SandboxStorage, UserEnrollment
   from datetime import datetime
   
   # Initialize sandbox storage
   storage = SandboxStorage("playground")
   
   # Add message handler for enrollment
   @bot_app.message("/enroll")
   async def on_enroll_command(context: TurnContext, state: TurnState):
       user_id = context.activity.from_property.id
       user_name = context.activity.from_property.name or "Student"
       
       # Check if user is already enrolled
       existing_enrollment = storage.get_user_enrollment(user_id)
       if existing_enrollment:
           await context.send_activity(
               f"Hi {user_name}! You're already enrolled in {existing_enrollment.course_id}. "
               f"You're on day {existing_enrollment.current_day}."
           )
           return
       
       # Create new enrollment (default to python-basics for sandbox)
       enrollment = UserEnrollment(
           user_id=user_id,
           course_id="python-basics",
           enrollment_date=datetime.now().isoformat(),
           current_day=1
       )
       
       success = storage.save_user_enrollment(enrollment)
       if success:
           await context.send_activity(
               f"🎉 Welcome {user_name}! You're enrolled in Python Basics. "
               f"Your 30-day learning journey starts now! Type '/status' to check progress."
           )
       else:
           await context.send_activity("Sorry, enrollment failed. Please try again.")
   
   @bot_app.message("/status")
   async def on_status_command(context: TurnContext, state: TurnState):
       user_id = context.activity.from_property.id
       enrollment = storage.get_user_enrollment(user_id)
       
       if not enrollment:
           await context.send_activity(
               "You're not enrolled yet! Type '/enroll' to start your learning journey."
           )
           return
       
       # Send status message
       await context.send_activity(
           f"📊 Your Progress:\n"
           f"Course: {enrollment.course_id}\n"
           f"Current Day: {enrollment.current_day}/{enrollment.total_days}\n"
           f"Status: {enrollment.status}\n"
           f"Enrolled: {enrollment.enrollment_date[:10]}"
       )
   ```

2. **Add course listing command**:
   ```python
   @bot_app.message("/courses")
   async def on_courses_command(context: TurnContext, state: TurnState):
       await context.send_activity(
           "📚 Available Courses:\n"
           "• Python Basics (30 days)\n"
           "• Azure Fundamentals (coming soon)\n\n"
           "Type '/enroll' to start Python Basics!"
       )
   ```

**Sandbox Testing**: These commands can be tested immediately in your sandbox Teams environment.

### 3.3 Create Course Configuration
1. **Create `src/courses.py`** to define available courses:
   ```python
   AVAILABLE_COURSES = {
       "python-basics": {
           "name": "Python Programming Basics",
           "description": "Learn Python fundamentals in 30 days",
           "topics": ["Variables", "Functions", "Classes", "Modules", ...],
           "difficulty": "beginner"
       },
       "azure-fundamentals": {
           "name": "Azure Cloud Fundamentals",
           "description": "Master Azure basics in 30 days",
           "topics": ["Compute", "Storage", "Networking", "Security", ...],
           "difficulty": "intermediate"
       }
   }
   ```

## Task 4: Implement Basic User Interaction (30 minutes)

### 4.1 Welcome and Help Messages
1. **Add welcome message handler**:
   ```python
   @bot_app.message("hello")
   async def on_hello_message(context: TurnContext, state: TurnState):
       welcome_text = """
       🎓 Welcome to AI Learning Challenge!
       
       Available commands:
       • /enroll [course] - Start a 30-day learning journey
       • /status - Check your progress
       • /courses - View available courses
       • /help - Show this help message
       """
       await context.send_activity(welcome_text)
   ```

### 4.2 Course Listing
1. **Add course listing handler**:
   ```python
   @bot_app.message("/courses")
   async def on_courses_command(context: TurnContext, state: TurnState):
       from courses import AVAILABLE_COURSES
       
       courses_text = "📚 Available Courses:\n\n"
       for course_id, course_info in AVAILABLE_COURSES.items():
           courses_text += f"• **{course_info['name']}** (`{course_id}`)\n"
           courses_text += f"  {course_info['description']}\n"
           courses_text += f"  Difficulty: {course_info['difficulty']}\n\n"
       
       await context.send_activity(courses_text)
   ```

### 4.3 Error Handling
1. **Add error handling for invalid commands**:
   ```python
   @bot_app.message()
   async def on_message_activity(context: TurnContext, state: TurnState):
       # Handle unrecognized messages
       if not any(context.activity.text.startswith(cmd) for cmd in ["/enroll", "/status", "/courses", "/help"]):
           await context.send_activity("Sorry, I didn't understand that. Type /help for available commands.")
   ```

## Task 5: Test Enrollment Flow in Teams (30 minutes)

### 5.1 Deploy Updated Code
1. **Install Python dependencies** (if not already done):
   ```powershell
   cd "C:\Users\rajaseharanr\AgentsToolkitProjects\AutomatedAIpowered"
   pip install -r src/requirements.txt
   ```

2. **Test locally first**:
   ```powershell
   cd src
   python app.py
   ```

3. **Deploy to Azure Web App**:
   ```powershell
   # Using Teams Toolkit
   teamsfx deploy
   
   # Or using Azure CLI
   az webapp up --name your-web-app-name --resource-group your-resource-group
   ```

### 5.2 Test in Teams
1. **Install your app in Teams**:
   - Use Teams Developer Portal or Teams Toolkit
   - Upload your app package (manifest + icons)
   - Install in your personal scope or test team

2. **Test basic commands**:
   - Send "hello" message
   - Try "/courses" command
   - Test "/enroll python-basics" command
   - Check "/status" command

### 5.3 Verify Data Storage
1. **Check if enrollment data is saved**:
   - Look for created data files
   - Verify user enrollment is recorded
   - Test error cases (duplicate enrollment, invalid course)

## Task 6: Implement Progress Tracking Structure (25 minutes)

### 6.1 Create Progress Tracking Functions
1. **Add progress tracking to `src/storage.py`**:
   ```python
   def get_user_wrong_questions(self, user_id: str) -> List[Dict]:
       # Get all wrong questions for re-asking
       pass
   
   def add_wrong_question(self, user_id: str, question: Dict) -> bool:
       # Add a question to wrong questions queue
       pass
   
   def remove_wrong_question(self, user_id: str, question_id: str) -> bool:
       # Remove question when answered correctly
       pass
   
   def get_daily_progress(self, user_id: str) -> Dict:
       # Get overall progress summary
       pass
   ```

### 6.2 Design Question Structure
1. **Define question format**:
   ```python
   question_format = {
       "id": "unique_question_id",
       "question": "What is a variable in Python?",
       "options": ["A) A container for data", "B) A function", "C) A loop", "D) A condition"],
       "correct_answer": "A",
       "explanation": "A variable is a container that stores data values.",
       "topic": "Variables",
       "difficulty": "easy",
       "day_introduced": 1
   }
   ```

### 6.3 Progress Calculation Logic
1. **Add progress calculation functions**:
   ```python
   def calculate_daily_score(self, user_id: str, day: int) -> float:
       # Calculate percentage score for a specific day
       pass
   
   def calculate_overall_progress(self, user_id: str) -> Dict:
       # Calculate overall course progress
       pass
   
   def get_mastery_level(self, user_id: str, topic: str) -> str:
       # Determine mastery level for specific topics
       pass
   ```

## Task 7: Test Sandbox Bot Functionality (15 minutes)

### 7.1 Local Testing Setup
1. **Set up ngrok for sandbox testing** (if not already done):
   ```powershell
   # Install ngrok
   choco install ngrok
   # Or download from https://ngrok.com/download
   
   # Start ngrok tunnel
   ngrok http 3978
   ```

2. **Update sandbox bot endpoint**:
   - Copy the ngrok HTTPS URL (e.g., https://abc123.ngrok.io)
   - Go to Developer Portal → Your bot → Configuration
   - Update messaging endpoint to: `https://abc123.ngrok.io/api/messages`

3. **Run the bot locally**:
   ```powershell
   # Ensure you're using playground environment
   $env:ENVIRONMENT = "playground"
   
   # Run the bot
   cd src
   python app.py
   ```

### 7.2 Test Enrollment Commands in Sandbox
1. **Test in your sandbox Teams**:
   - Send `/enroll` to your bot
   - Send `/status` to check enrollment
   - Send `/courses` to see available courses
   - Test error handling with invalid commands

2. **Verify file storage**:
   - Check that `playground/enrollments.json` is created
   - Inspect enrollment data structure
   - Ensure data persists between bot restarts

### 7.3 Prepare for Day 4 AI Integration
1. **Check OpenAI/Azure OpenAI setup in playground**:
   - Verify API keys are configured in `env/.env.playground`
   - Test basic AI model connectivity
   - Review prompt templates in `src/prompts/chat/`

2. **Document current state**:
   - Bot responds to enrollment commands
   - User data is stored in playground files
   - Ready for AI question generation integration

### 7.2 Plan Question Generation
1. **Review current prompt structure**:
   - Look at `src/prompts/chat/skprompt.txt`
   - Understand how to modify for question generation
   - Plan integration with course content

### 7.3 Document Day 3 Progress
1. **Create development notes**:
   ```
   Day 3 Completion Status:
   - User enrollment system: [IMPLEMENTED/PARTIAL]
   - Basic bot commands: [IMPLEMENTED/PARTIAL]
   - Data storage: [IMPLEMENTED/PARTIAL]
   - Teams integration testing: [COMPLETED/PARTIAL]
   - Progress tracking structure: [IMPLEMENTED/PARTIAL]
   ```

---

## Important Notes:
- **Sandbox Development** - All Day 3 work can be completed in sandbox environment without Azure infrastructure
- **File-based Storage** - Use simple JSON files for rapid development and testing
- **Local Testing** - Use ngrok to test sandbox bot locally before deploying to Azure
- **Error handling** - Add proper error messages for user experience
- **Data validation** - Ensure user inputs are validated properly

## Common Issues:
- **ngrok tunnel expired** - Restart ngrok and update bot endpoint in Developer Portal
- **Environment variables** - Ensure `env/.env.playground` has all required keys
- **File permissions** - Check that playground directory is writable
- **Bot not responding** - Verify messaging endpoint is correct and bot is running
- **Teams caching** - Clear Teams cache if bot responses seem delayed

## Success Criteria:
- ✅ Bot responds to `/enroll`, `/status`, and `/courses` commands in sandbox Teams
- ✅ User enrollment data is stored in `playground/enrollments.json`
- ✅ Local development environment works with ngrok tunnel
- ✅ Error handling for enrollment edge cases
- ✅ Ready for AI integration on Day 4

**Total estimated time: 2.5-3 hours (sandbox development)**

---
## Sandbox Mode Notes
| Aspect | Sandbox Advantage |
|--------|------------------|
| **Development Speed** | No Azure infrastructure needed - start coding immediately with file storage. |
| **Testing Environment** | Use sandbox Teams with ngrok for immediate feedback on bot commands. |
| **Storage Solution** | JSON files in `playground/` directory - easy to inspect and debug. |
| **Deployment** | Local development with ngrok tunnel - no Azure deployments required. |
| **Cost** | Free development - only pay for OpenAI API calls when testing AI features. |

**Next Steps**: Day 4 will add AI question generation while continuing to use the sandbox environment. Azure infrastructure can be added later when ready for production features.
- **Bot not responding**: Check messaging endpoint and Azure Web App status
- **Environment variables**: Ensure all required variables are set correctly
- **Teams app installation**: May need to reinstall app after code changes
- **Storage errors**: Check file permissions and directory creation

## Success Criteria:
- ✅ Users can enroll in courses using bot commands
- ✅ Enrollment data is stored and retrievable
- ✅ Basic bot commands work in Teams
- ✅ Progress tracking structure is in place
- ✅ Ready for AI question generation in Day 4

**Total estimated time: 3-3.5 hours**

---
## Sandbox Mode Notes
| Aspect | Sandbox Guidance |
|--------|------------------|
| Enrollment Persistence | Use JSON or in-memory dict; no external DB yet. |
| User Identity | Teams user IDs in sandbox sufficient; no AAD graph lookups needed. |
| Data Reset | Accept that restart may clear state—log minimal snapshots for debugging. |
| Error Logging | Console print adequate; structured logging deferred. |
| Abstraction | Create a simple storage interface to ease migration later. |

Keep implementation lean to accelerate validation of learning flow cadence.