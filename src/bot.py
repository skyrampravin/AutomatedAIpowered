import os
import sys
import json
import traceback
import logging
from datetime import datetime
from dataclasses import asdict

from botbuilder.core import (
    ActivityHandler, 
    TurnContext, 
    MessageFactory,
    MemoryStorage,
    ConversationState,
    UserState
)
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
        # Initialize conversation and user state
        memory_storage = MemoryStorage()
        self.conversation_state = ConversationState(memory_storage)
        self.user_state = UserState(memory_storage)

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""
        user_id = turn_context.activity.from_property.id
        user_name = turn_context.activity.from_property.name or "User"
        message_text = turn_context.activity.text.strip().lower()
        
        logger.info(f"Message from {user_name} ({user_id}): {message_text}")
        
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
                    f"You said: {turn_context.activity.text}\n\n"
                    f"Try using commands like `/help`, `/enroll python-basics`, or `/profile`!"
                ))
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
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
        success = storage.enroll_user(user_id, course)
        
        if success:
            profile = storage.get_user_profile(user_id)
            await turn_context.send_activity(MessageFactory.text(
                f"🎉 **Enrollment Successful!**\n\n"
                f"👤 **Student**: {user_name}\n"
                f"📚 **Course**: {course}\n"
                f"📅 **Start Date**: {profile.start_date[:10] if profile.start_date else 'Today'}\n\n"
                f"Welcome to your learning journey! Use `/profile` to check your progress."
            ))
            logger.info(f"User {user_id} enrolled in {course}")
        else:
            await turn_context.send_activity(MessageFactory.text(
                "❌ Enrollment failed. Please try again or contact support."
            ))

    async def handle_profile_command(self, turn_context: TurnContext, user_id: str):
        """Show user profile"""
        profile = storage.get_user_profile(user_id)
        
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
        
        await turn_context.send_activity(MessageFactory.text(status_text))

    async def handle_admin_command(self, turn_context: TurnContext, user_id: str):
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