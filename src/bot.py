import os
import sys
import json
import traceback
import logging
from sandbox_question_generator import SandboxQuestionGenerator, QuizQuestion
from sandbox_answer_evaluator import SandboxAnswerEvaluator
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

# Add after storage initialization
question_generator = SandboxQuestionGenerator(config, storage)
answer_evaluator = SandboxAnswerEvaluator(config, storage)

# Track active quiz sessions
active_quizzes = {}  # user_id -> QuizQuestion

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
        message_text = turn_context.activity.text.strip() if turn_context.activity.text else ""
        
        self.logger.info(f"Message from {user_name} ({user_id}): {message_text}")
        
        try:
            # Check if user is answering a quiz question
            if user_id in active_quizzes:
                await self.handle_quiz_answer(turn_context, user_id, message_text)
                return
            
            # Handle specific commands
            message_lower = message_text.lower()
            if message_lower.startswith('/help'):
                await self.handle_help_command(turn_context)
            elif message_lower.startswith('/enroll'):
                await self.handle_enroll_command(turn_context, message_text)
            elif message_lower.startswith('/profile'):
                await self.handle_profile_command(turn_context, user_id)
            elif message_lower.startswith('/quiz'):
                await self.handle_quiz_command(turn_context, user_id)
            elif message_lower.startswith('/sample'):
                await self.handle_sample_command(turn_context, message_text)
            elif message_lower.startswith('/cancel'):
                await self.handle_cancel_command(turn_context, user_id)
            elif message_lower.startswith('/status'):
                await self.handle_status_command(turn_context)
            elif message_lower.startswith('/admin'):
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

**Learning Commands:**
• `/quiz` - Start a personalized quiz question
• `/sample [course]` - Preview a sample question
• `/cancel` - Cancel current quiz

**Account Commands:**
• `/enroll [course]` - Enroll in a learning course
• `/profile` - View your learning profile and progress

**System Commands:**
• `/help` - Show this help message
• `/status` - Check bot system status
• `/admin` - View system statistics

**Available Courses:**
• `python-basics` - Python fundamentals
• `javascript-intro` - JavaScript introduction  
• `data-science` - Data Science concepts
• `web-dev` - Web Development

**Example Usage:**
```
/enroll python-basics
/quiz
/sample javascript-intro
```

**Getting Started:**
1. Enroll: `/enroll python-basics`
2. Start Quiz: `/quiz`
3. Answer questions and track your progress!

*🚀 New in Day 3: AI-powered personalized questions! 🚀*
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
        
        # Test OpenAI status
        openai_status = "🔴 Quota Exceeded"
        openai_details = "OpenAI API quota exceeded. Using enhanced fallback questions."
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=self.config.OPENAI_MODEL_NAME,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            openai_status = "🟢 Active"
            openai_details = "OpenAI API working normally"
        except Exception as e:
            if "insufficient_quota" in str(e):
                openai_status = "🔴 Quota Exceeded"
                openai_details = "OpenAI API quota exceeded. Add billing to enable AI generation."
            elif "429" in str(e):
                openai_status = "🟡 Rate Limited"
                openai_details = "OpenAI API rate limited. Please wait a moment."
            else:
                openai_status = "🔴 Error"
                openai_details = f"OpenAI API error: {str(e)[:50]}..."
        
        status_text = f"""
🤖 **Bot System Status - Sandbox Mode**

🟢 **Bot Status**: Online and Running
🤖 **AI Status**: {openai_status}
   └─ {openai_details}

📊 **Statistics**:
  • Total Users: {stats.get('total_users', 0)}
  • Enrolled Users: {stats.get('enrolled_users', 0)}
  • Total Quizzes: {stats.get('total_quizzes', 0)}
  • Active Courses: {len(stats.get('active_courses', []))}
  • Storage Used: {stats.get('storage_size_mb', 0)} MB

🏠 **Environment**: Sandbox (File-based storage)
💾 **Data Location**: playground/data/
📝 **Logs**: playground/logs/

**Current Mode**: Enhanced fallback questions (High quality pre-built questions)
**System Health**: ✅ All systems operational

💡 **To enable AI generation**: Add OpenAI billing at https://platform.openai.com/account/billing
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

    async def handle_quiz_command(self, turn_context: TurnContext, user_id: str):
        """Handle quiz start command"""
        try:
            # Check if user is enrolled
            profile = storage.get_user_profile(user_id)
            if not profile or not profile.enrolled_course:
                await turn_context.send_activity(MessageFactory.text(
                    "❌ **Please enroll in a course first!**\n\n"
                    "Use `/enroll [course-name]` to get started.\n"
                    "Available courses: python-basics, javascript-intro, data-science, web-dev"
                ))
                return
            
            # Check if user already has an active quiz
            if user_id in active_quizzes:
                await turn_context.send_activity(MessageFactory.text(
                    "⚠️ **You already have an active quiz!**\n\n"
                    "Please answer the current question or use `/cancel` to start a new quiz."
                ))
                return
            
            # Generate personalized question
            await turn_context.send_activity(MessageFactory.text(
                "🤔 **Generating your personalized question...**\n\n"
                "This may take a few seconds while I create a question tailored to your progress."
            ))
            
            question = await question_generator.generate_personalized_question(user_id)
            
            if not question:
                await turn_context.send_activity(MessageFactory.text(
                    "❌ **Sorry, I couldn't generate a question right now.**\n\n"
                    "Please try again in a moment. If the problem persists, contact support."
                ))
                return
            
            # Store active quiz
            active_quizzes[user_id] = question
            
            # Format and send question
            question_text = f"""
📚 **Quiz Question - {question.course.replace('-', ' ').title()}**

🎯 **Topic**: {question.topic}
⚡ **Difficulty**: {question.difficulty.title()}
⏱️ **Estimated Time**: {question.estimated_time}s

❓ **Question**:
{question.question_text}

**Options**:
{chr(10).join(question.options)}

**Instructions**:
• Reply with just the letter (A, B, C, or D)
• You can also type the option number (1, 2, 3, or 4)
• Use `/cancel` to cancel this quiz

*Take your time and think carefully!*
"""
            
            await turn_context.send_activity(MessageFactory.text(question_text))
            self.logger.info(f"Quiz question sent to user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling quiz command for user {user_id}: {e}")
            await turn_context.send_activity(MessageFactory.text(
                "❌ Sorry, I encountered an error starting your quiz. Please try again."
            ))

    async def handle_quiz_answer(self, turn_context: TurnContext, user_id: str, answer: str):
        """Handle quiz answer from user"""
        try:
            question = active_quizzes.get(user_id)
            if not question:
                await turn_context.send_activity(MessageFactory.text(
                    "❌ No active quiz found. Use `/quiz` to start a new quiz."
                ))
                return
            
            # Check answer
            result = question_generator.check_answer(question, answer)
            
            # Evaluate answer and update profile
            evaluation = answer_evaluator.evaluate_answer(user_id, question, result)
            
            if not evaluation.get("success"):
                await turn_context.send_activity(MessageFactory.text(
                    "❌ Error processing your answer. Please try again."
                ))
                return
            
            # Remove from active quizzes
            del active_quizzes[user_id]
            
            # Format response
            feedback = evaluation["feedback"]
            performance = evaluation["performance_summary"]
            
            response_text = f"""
{feedback["immediate"]}

📖 **Explanation**:
{feedback["explanation"]}

📊 **Your Progress**:
• Total Questions: {performance["total_questions"]}
• Correct Answers: {performance["correct_answers"]}
• Accuracy: {performance["accuracy"]:.1%}
• Current Streak: {performance["current_streak"]}
• Performance Level: {performance["emoji"]} {performance["level"]}

💡 **{feedback["encouragement"]}**

🚀 **Next Steps**: {feedback["next_steps"]}

Ready for another question? Type `/quiz` to continue learning!
"""
            
            await turn_context.send_activity(MessageFactory.text(response_text))
            
            # Log quiz completion
            self.logger.info(f"Quiz completed by user {user_id}: {'Correct' if result.is_correct else 'Incorrect'}")
            
        except Exception as e:
            self.logger.error(f"Error handling quiz answer for user {user_id}: {e}")
            # Clean up active quiz
            if user_id in active_quizzes:
                del active_quizzes[user_id]
            await turn_context.send_activity(MessageFactory.text(
                "❌ Error processing your answer. Please try `/quiz` to start a new question."
            ))

    async def handle_sample_command(self, turn_context: TurnContext, message_text: str):
        """Handle sample question command"""
        try:
            # Parse course from command
            parts = message_text.split()
            if len(parts) < 2:
                await turn_context.send_activity(MessageFactory.text(
                    "❌ Please specify a course. Example: `/sample python-basics`\n\n"
                    "Available courses: python-basics, javascript-intro, data-science, web-dev"
                ))
                return
            
            course = parts[1]
            available_courses = question_generator.get_available_courses()
            
            if course not in available_courses:
                course_list = ', '.join(available_courses.keys())
                await turn_context.send_activity(MessageFactory.text(
                    f"❌ Course '{course}' not found.\n\n"
                    f"Available courses: {course_list}"
                ))
                return
            
            # Generate sample question
            await turn_context.send_activity(MessageFactory.text(
                f"🤔 **Generating sample question for {course}...**"
            ))
            
            question = await question_generator.generate_sample_question(course)
            
            if not question:
                await turn_context.send_activity(MessageFactory.text(
                    "❌ Sorry, I couldn't generate a sample question right now. Please try again."
                ))
                return
            
            # Format sample question (no quiz functionality)
            sample_text = f"""
📚 **Sample Question - {course.replace('-', ' ').title()}**

🎯 **Topic**: {question.topic}
⚡ **Difficulty**: {question.difficulty.title()}

❓ **Question**:
{question.question_text}

**Options**:
{chr(10).join(question.options)}

📖 **Answer**: {question.correct_answer}
💡 **Explanation**: {question.explanation}

*This is just a preview! Use `/enroll {course}` to start learning and `/quiz` for interactive questions.*
"""
            
            await turn_context.send_activity(MessageFactory.text(sample_text))
            self.logger.info(f"Sample question generated for course {course}")
            
        except Exception as e:
            self.logger.error(f"Error handling sample command: {e}")
            await turn_context.send_activity(MessageFactory.text(
                "❌ Sorry, I encountered an error generating a sample question."
            ))

    async def handle_cancel_command(self, turn_context: TurnContext, user_id: str):
        """Handle quiz cancellation"""
        if user_id in active_quizzes:
            del active_quizzes[user_id]
            await turn_context.send_activity(MessageFactory.text(
                "✅ **Quiz cancelled.**\n\n"
                "Use `/quiz` when you're ready to try again!"
            ))
        else:
            await turn_context.send_activity(MessageFactory.text(
                "ℹ️ No active quiz to cancel.\n\n"
                "Use `/quiz` to start a new question!"
            ))

# Create bot instance
bot_app = EchoBot()