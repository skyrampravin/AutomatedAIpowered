# Day 3: AI-Powered Question Generation (Codespaces)

## 🎯 **Goal**: Implement OpenAI-powered personalized question generation in cloud

**Time Required**: 60-75 minutes  
**Prerequisites**: Day 1 & 2 completed (Codespace running)  
**Outcome**: Bot generates and asks personalized learning questions in cloud environment

---

## **Step 1: Create Question Generator (20 minutes)**

### 1.1 OpenAI Question Generator Class
1. **Create**: `src/sandbox_question_generator.py`

```python
import os
import json
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

import openai
from openai import OpenAI

from config import Config
from sandbox_storage import SandboxStorage, UserProfile

@dataclass
class QuizQuestion:
    question_id: str
    course: str
    difficulty: str
    question_text: str
    question_type: str  # "multiple_choice", "true_false", "short_answer"
    options: List[str]  # For multiple choice
    correct_answer: str
    explanation: str
    topic: str
    estimated_time: int  # seconds
    created_date: str

@dataclass  
class QuizResult:
    question_id: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    time_taken: int
    timestamp: str

class SandboxQuestionGenerator:
    """AI-powered question generation for sandbox learning"""
    
    def __init__(self, config: Config, storage: SandboxStorage):
        self.config = config
        self.storage = storage
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Course curriculum definitions
        self.course_curricula = {
            "python-basics": {
                "topics": [
                    "Variables and Data Types",
                    "Control Flow (if/else, loops)",
                    "Functions and Parameters", 
                    "Lists and Dictionaries",
                    "String Manipulation",
                    "File Operations",
                    "Error Handling",
                    "Object-Oriented Programming Basics"
                ],
                "description": "Fundamental Python programming concepts",
                "difficulty_levels": ["beginner", "intermediate"]
            },
            "javascript-intro": {
                "topics": [
                    "Variables (let, const, var)",
                    "Functions and Arrow Functions",
                    "Arrays and Objects", 
                    "DOM Manipulation",
                    "Event Handling",
                    "Promises and Async/Await",
                    "ES6+ Features",
                    "Basic Node.js"
                ],
                "description": "JavaScript fundamentals for web development",
                "difficulty_levels": ["beginner", "intermediate"]
            },
            "data-science": {
                "topics": [
                    "Data Types and Structures",
                    "Statistics and Probability",
                    "Pandas DataFrames",
                    "Data Visualization",
                    "Machine Learning Basics",
                    "Data Cleaning",
                    "NumPy Arrays",
                    "Hypothesis Testing"
                ],
                "description": "Introduction to data science concepts",
                "difficulty_levels": ["intermediate", "advanced"]
            },
            "web-dev": {
                "topics": [
                    "HTML5 Semantics",
                    "CSS3 and Flexbox",
                    "Responsive Design",
                    "JavaScript DOM",
                    "RESTful APIs",
                    "Git and Version Control",
                    "Web Security Basics",
                    "Performance Optimization"
                ],
                "description": "Modern web development practices",
                "difficulty_levels": ["beginner", "intermediate", "advanced"]
            }
        }
    
    async def generate_personalized_question(self, user_id: str) -> Optional[QuizQuestion]:
        """Generate a personalized question based on user's progress"""
        try:
            # Get user profile
            profile = self.storage.get_user_profile(user_id)
            if not profile or not profile.enrolled_course:
                self.logger.error(f"No enrolled course found for user {user_id}")
                return None
            
            course = profile.enrolled_course
            if course not in self.course_curricula:
                self.logger.error(f"Unknown course: {course}")
                return None
            
            # Determine difficulty based on user's performance
            difficulty = self._determine_difficulty(profile)
            
            # Select topic based on progress
            topic = self._select_topic(profile, course)
            
            # Generate question using OpenAI
            question = await self._generate_ai_question(course, topic, difficulty)
            
            if question:
                self.logger.info(f"Generated question for user {user_id}, course {course}, topic {topic}")
                return question
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating question for user {user_id}: {e}")
            return None
    
    def _determine_difficulty(self, profile: UserProfile) -> str:
        """Determine appropriate difficulty based on user's performance"""
        if profile.total_questions == 0:
            return "beginner"
        
        accuracy = profile.correct_answers / profile.total_questions
        
        if accuracy >= 0.8 and profile.total_questions >= 5:
            return "intermediate"
        elif accuracy >= 0.9 and profile.total_questions >= 10:
            return "advanced"
        else:
            return "beginner"
    
    def _select_topic(self, profile: UserProfile, course: str) -> str:
        """Select topic based on user's progress and course curriculum"""
        available_topics = self.course_curricula[course]["topics"]
        
        # For now, select randomly from available topics
        # In a full implementation, this would be based on:
        # - Topics user hasn't seen yet
        # - Topics where user performed poorly
        # - Sequential progression through curriculum
        
        return random.choice(available_topics)
    
    async def _generate_ai_question(self, course: str, topic: str, difficulty: str) -> Optional[QuizQuestion]:
        """Generate question using OpenAI"""
        try:
            course_info = self.course_curricula[course]
            
            # Create prompt for OpenAI
            prompt = f"""
Generate a {difficulty} level educational question for the course "{course_info['description']}" on the topic "{topic}".

Requirements:
- Create a multiple choice question with 4 options (A, B, C, D)
- Include clear, concise question text
- Provide one correct answer and three plausible distractors
- Add a brief explanation of why the correct answer is right
- Make the question practical and applicable
- Difficulty level: {difficulty}

Format your response as JSON with this exact structure:
{{
    "question_text": "Your question here?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A",
    "explanation": "Explanation of why the correct answer is right.",
    "estimated_time": 60
}}

Topic: {topic}
Course: {course_info['description']}
Difficulty: {difficulty}
"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Generate high-quality, accurate learning questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            question_data = json.loads(response_text)
            
            # Create QuizQuestion object
            question = QuizQuestion(
                question_id=f"{course}_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                course=course,
                difficulty=difficulty,
                question_text=question_data["question_text"],
                question_type="multiple_choice",
                options=question_data["options"],
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"],
                topic=topic,
                estimated_time=question_data.get("estimated_time", 60),
                created_date=datetime.now().isoformat()
            )
            
            return question
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            self.logger.error(f"Response text: {response_text}")
            return None
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            return None
    
    def check_answer(self, question: QuizQuestion, user_answer: str) -> QuizResult:
        """Check if user's answer is correct"""
        user_answer_clean = user_answer.strip().upper()
        correct_answer_clean = question.correct_answer.strip().upper()
        
        # Handle different answer formats
        if user_answer_clean in ['A', 'B', 'C', 'D']:
            is_correct = user_answer_clean == correct_answer_clean
        elif user_answer_clean in ['1', '2', '3', '4']:
            # Convert number to letter
            letter_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
            is_correct = letter_map.get(user_answer_clean) == correct_answer_clean
        else:
            # Try to match against option text
            for i, option in enumerate(question.options):
                if user_answer.lower() in option.lower():
                    letter = chr(65 + i)  # Convert to A, B, C, D
                    is_correct = letter == correct_answer_clean
                    break
            else:
                is_correct = False
        
        return QuizResult(
            question_id=question.question_id,
            user_answer=user_answer,
            correct_answer=question.correct_answer,
            is_correct=is_correct,
            time_taken=0,  # Will be calculated by the bot
            timestamp=datetime.now().isoformat()
        )
    
    def get_question_stats(self) -> Dict[str, Any]:
        """Get statistics about generated questions"""
        try:
            stats = {
                "total_questions_generated": 0,
                "questions_by_course": {},
                "questions_by_difficulty": {},
                "questions_by_topic": {}
            }
            
            # Note: In a full implementation, we would track generated questions
            # For sandbox mode, we'll return basic stats
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting question stats: {e}")
            return {}
    
    def get_available_courses(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available courses"""
        return self.course_curricula
    
    async def generate_sample_question(self, course: str) -> Optional[QuizQuestion]:
        """Generate a sample question for course preview"""
        try:
            if course not in self.course_curricula:
                return None
            
            topic = random.choice(self.course_curricula[course]["topics"])
            question = await self._generate_ai_question(course, topic, "beginner")
            
            return question
            
        except Exception as e:
            self.logger.error(f"Error generating sample question for {course}: {e}")
            return None
```

### 1.2 Test Question Generator
```powershell
# Test the question generator
python -c "
import asyncio
from src.config import Config
from src.sandbox_storage import SandboxStorage
from src.sandbox_question_generator import SandboxQuestionGenerator

async def test_generator():
    config = Config()
    storage = SandboxStorage(config.DATA_DIRECTORY)
    generator = SandboxQuestionGenerator(config, storage)
    
    # Test sample question generation
    question = await generator.generate_sample_question('python-basics')
    if question:
        print('✅ Question generation working!')
        print(f'Topic: {question.topic}')
        print(f'Question: {question.question_text[:50]}...')
    else:
        print('❌ Question generation failed')

asyncio.run(test_generator())
"
```

---

## **Step 2: Create Answer Evaluator (15 minutes)**

### 2.1 Intelligent Answer Evaluation
1. **Create**: `src/sandbox_answer_evaluator.py`

```python
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from config import Config
from sandbox_storage import SandboxStorage, UserProfile
from sandbox_question_generator import QuizQuestion, QuizResult

@dataclass
class LearningInsight:
    user_id: str
    insight_type: str  # "strength", "weakness", "recommendation"
    topic: str
    message: str
    confidence: float
    generated_date: str

class SandboxAnswerEvaluator:
    """Intelligent answer evaluation and learning analytics"""
    
    def __init__(self, config: Config, storage: SandboxStorage):
        self.config = config
        self.storage = storage
        self.logger = logging.getLogger(__name__)
    
    def evaluate_answer(self, user_id: str, question: QuizQuestion, result: QuizResult) -> Dict[str, Any]:
        """Evaluate user's answer and update their profile"""
        try:
            # Get user profile
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                self.logger.error(f"No profile found for user {user_id}")
                return {"success": False, "error": "User profile not found"}
            
            # Update profile statistics
            profile.total_questions += 1
            if result.is_correct:
                profile.correct_answers += 1
                profile.current_streak += 1
                if profile.current_streak > profile.longest_streak:
                    profile.longest_streak = profile.current_streak
            else:
                profile.current_streak = 0
            
            profile.last_quiz_date = datetime.now().isoformat()
            
            # Save updated profile
            self.storage.save_user_profile(profile)
            
            # Generate feedback
            feedback = self._generate_feedback(profile, question, result)
            
            # Generate learning insights
            insights = self._generate_learning_insights(profile, question, result)
            
            evaluation = {
                "success": True,
                "result": result,
                "feedback": feedback,
                "insights": insights,
                "updated_profile": profile,
                "performance_summary": self._get_performance_summary(profile)
            }
            
            self.logger.info(f"Evaluated answer for user {user_id}: {'Correct' if result.is_correct else 'Incorrect'}")
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating answer for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_feedback(self, profile: UserProfile, question: QuizQuestion, result: QuizResult) -> Dict[str, str]:
        """Generate personalized feedback for the user"""
        feedback = {
            "immediate": "",
            "explanation": question.explanation,
            "encouragement": "",
            "next_steps": ""
        }
        
        if result.is_correct:
            # Positive feedback
            if profile.current_streak >= 5:
                feedback["immediate"] = f"🔥 Excellent! You're on a {profile.current_streak}-question streak!"
            elif profile.current_streak >= 3:
                feedback["immediate"] = f"🌟 Great job! {profile.current_streak} correct answers in a row!"
            else:
                feedback["immediate"] = "✅ Correct! Well done!"
            
            feedback["encouragement"] = "Keep up the great work! You're making excellent progress."
            
            # Suggest next steps based on performance
            accuracy = profile.correct_answers / profile.total_questions
            if accuracy >= 0.8 and profile.total_questions >= 5:
                feedback["next_steps"] = "You're ready for more challenging questions!"
            else:
                feedback["next_steps"] = "Try another question to build your confidence."
                
        else:
            # Constructive feedback
            feedback["immediate"] = "❌ Not quite right, but that's okay! Learning happens through mistakes."
            feedback["encouragement"] = "Don't give up! Every expert was once a beginner."
            
            # Provide helpful next steps
            if profile.total_questions < 3:
                feedback["next_steps"] = "Take your time and read questions carefully. You're just getting started!"
            elif profile.current_streak == 0 and profile.total_questions >= 5:
                feedback["next_steps"] = "Consider reviewing the basics for this topic before continuing."
            else:
                feedback["next_steps"] = "Try breaking down the problem step by step."
        
        return feedback
    
    def _generate_learning_insights(self, profile: UserProfile, question: QuizQuestion, result: QuizResult) -> List[LearningInsight]:
        """Generate learning insights based on user's performance"""
        insights = []
        
        try:
            # Calculate current accuracy
            accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
            
            # Insight 1: Performance trend
            if profile.total_questions >= 5:
                if accuracy >= 0.8:
                    insights.append(LearningInsight(
                        user_id=profile.user_id,
                        insight_type="strength",
                        topic=question.topic,
                        message=f"You're performing excellently with {accuracy:.1%} accuracy!",
                        confidence=0.9,
                        generated_date=datetime.now().isoformat()
                    ))
                elif accuracy < 0.5:
                    insights.append(LearningInsight(
                        user_id=profile.user_id,
                        insight_type="weakness",
                        topic=question.topic,
                        message=f"Consider reviewing fundamental concepts. Current accuracy: {accuracy:.1%}",
                        confidence=0.8,
                        generated_date=datetime.now().isoformat()
                    ))
            
            # Insight 2: Streak analysis
            if profile.current_streak >= 5:
                insights.append(LearningInsight(
                    user_id=profile.user_id,
                    insight_type="strength",
                    topic="General",
                    message=f"Amazing streak of {profile.current_streak} correct answers!",
                    confidence=0.95,
                    generated_date=datetime.now().isoformat()
                ))
            
            # Insight 3: Topic-specific recommendation
            if not result.is_correct:
                insights.append(LearningInsight(
                    user_id=profile.user_id,
                    insight_type="recommendation",
                    topic=question.topic,
                    message=f"Focus on '{question.topic}' - practice makes perfect!",
                    confidence=0.7,
                    generated_date=datetime.now().isoformat()
                ))
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating learning insights: {e}")
            return []
    
    def _get_performance_summary(self, profile: UserProfile) -> Dict[str, Any]:
        """Get performance summary for the user"""
        accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
        
        # Determine performance level
        if accuracy >= 0.9:
            level = "Excellent"
            emoji = "🏆"
        elif accuracy >= 0.8:
            level = "Great"
            emoji = "🌟"
        elif accuracy >= 0.7:
            level = "Good"
            emoji = "👍"
        elif accuracy >= 0.6:
            level = "Fair"
            emoji = "📚"
        else:
            level = "Learning"
            emoji = "🌱"
        
        return {
            "accuracy": accuracy,
            "level": level,
            "emoji": emoji,
            "total_questions": profile.total_questions,
            "correct_answers": profile.correct_answers,
            "current_streak": profile.current_streak,
            "longest_streak": profile.longest_streak
        }
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a user"""
        try:
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            quiz_history = self.storage.get_user_quiz_history(user_id)
            
            analytics = {
                "profile_summary": self._get_performance_summary(profile),
                "learning_progress": {
                    "course": profile.enrolled_course,
                    "start_date": profile.start_date,
                    "days_learning": self._calculate_learning_days(profile.start_date),
                    "total_sessions": len(quiz_history),
                    "completion_status": "In Progress" if not profile.completed_course else "Completed"
                },
                "performance_metrics": {
                    "accuracy_trend": "Improving",  # Would be calculated from history
                    "preferred_difficulty": self._get_preferred_difficulty(profile),
                    "strong_topics": [],  # Would be calculated from topic performance
                    "areas_for_improvement": []  # Would be calculated from mistakes
                },
                "recommendations": self._get_recommendations(profile)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting user analytics for {user_id}: {e}")
            return {"error": str(e)}
    
    def _calculate_learning_days(self, start_date: str) -> int:
        """Calculate days since user started learning"""
        try:
            if not start_date:
                return 0
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            now = datetime.now()
            return (now - start).days
        except:
            return 0
    
    def _get_preferred_difficulty(self, profile: UserProfile) -> str:
        """Determine user's preferred difficulty level"""
        accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
        
        if accuracy >= 0.8 and profile.total_questions >= 10:
            return "Advanced"
        elif accuracy >= 0.7 and profile.total_questions >= 5:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _get_recommendations(self, profile: UserProfile) -> List[str]:
        """Get personalized recommendations for the user"""
        recommendations = []
        
        accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
        
        if profile.total_questions < 5:
            recommendations.append("Complete more questions to get personalized insights")
        
        if accuracy < 0.6:
            recommendations.append("Review course fundamentals before tackling new topics")
        
        if profile.current_streak >= 5:
            recommendations.append("You're on fire! Try some advanced topics")
        
        if profile.current_streak == 0 and profile.total_questions >= 3:
            recommendations.append("Take a short break and come back refreshed")
        
        if len(recommendations) == 0:
            recommendations.append("Keep practicing regularly to maintain your progress")
        
        return recommendations
```

---

## **Step 3: Update Bot with Question Generation (20 minutes)**

### 3.1 Enhanced Bot with Quiz Functionality
1. **Update** `src/bot.py` to include question generation:

```python
# Add these imports at the top of bot.py
from sandbox_question_generator import SandboxQuestionGenerator, QuizQuestion
from sandbox_answer_evaluator import SandboxAnswerEvaluator

# Add after storage initialization
question_generator = SandboxQuestionGenerator(config, storage)
answer_evaluator = SandboxAnswerEvaluator(config, storage)

# Track active quiz sessions
active_quizzes = {}  # user_id -> QuizQuestion

# Add these new handlers before the existing @bot_app.message() handler

@bot_app.message()
async def on_message(context: TurnContext, state: TurnState):
    """Handle incoming messages"""
    user_id = context.activity.from_property.id
    user_name = context.activity.from_property.name or "User"
    message_text = context.activity.text.strip()
    
    logger.info(f"Message from {user_name} ({user_id}): {message_text}")
    
    try:
        # Check if user is answering a quiz question
        if user_id in active_quizzes:
            await handle_quiz_answer(context, user_id, message_text)
            return
        
        # Handle specific commands
        message_lower = message_text.lower()
        if message_lower.startswith('/help'):
            await handle_help_command(context)
        elif message_lower.startswith('/enroll'):
            await handle_enroll_command(context, message_text)
        elif message_lower.startswith('/profile'):
            await handle_profile_command(context, user_id)
        elif message_lower.startswith('/quiz'):
            await handle_quiz_command(context, user_id)
        elif message_lower.startswith('/sample'):
            await handle_sample_command(context, message_text)
        elif message_lower.startswith('/status'):
            await handle_status_command(context)
        elif message_lower.startswith('/admin'):
            await handle_admin_command(context, user_id)
        elif message_lower.startswith('/cancel'):
            await handle_cancel_command(context, user_id)
        else:
            # Default AI response using the planner
            await bot_app.ai.run(context, state)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Sorry, I encountered an error processing your message. Please try again."
        ))

async def handle_quiz_command(context: TurnContext, user_id: str):
    """Handle quiz start command"""
    try:
        # Check if user is enrolled
        profile = storage.get_user_profile(user_id)
        if not profile or not profile.enrolled_course:
            await context.send_activity(MessageFactory.text(
                "❌ **Please enroll in a course first!**\n\n"
                "Use `/enroll [course-name]` to get started.\n"
                "Available courses: python-basics, javascript-intro, data-science, web-dev"
            ))
            return
        
        # Check if user already has an active quiz
        if user_id in active_quizzes:
            await context.send_activity(MessageFactory.text(
                "⚠️ **You already have an active quiz!**\n\n"
                "Please answer the current question or use `/cancel` to start a new quiz."
            ))
            return
        
        # Generate personalized question
        await context.send_activity(MessageFactory.text(
            "🤔 **Generating your personalized question...**\n\n"
            "This may take a few seconds while I create a question tailored to your progress."
        ))
        
        question = await question_generator.generate_personalized_question(user_id)
        
        if not question:
            await context.send_activity(MessageFactory.text(
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
        
        await context.send_activity(MessageFactory.text(question_text))
        logger.info(f"Quiz question sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling quiz command for user {user_id}: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Sorry, I encountered an error starting your quiz. Please try again."
        ))

async def handle_quiz_answer(context: TurnContext, user_id: str, answer: str):
    """Handle quiz answer from user"""
    try:
        question = active_quizzes.get(user_id)
        if not question:
            await context.send_activity(MessageFactory.text(
                "❌ No active quiz found. Use `/quiz` to start a new quiz."
            ))
            return
        
        # Record answer time (simplified for sandbox)
        start_time = datetime.now()
        
        # Check answer
        result = question_generator.check_answer(question, answer)
        
        # Evaluate answer and update profile
        evaluation = answer_evaluator.evaluate_answer(user_id, question, result)
        
        if not evaluation.get("success"):
            await context.send_activity(MessageFactory.text(
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
        
        await context.send_activity(MessageFactory.text(response_text))
        
        # Log quiz completion
        logger.info(f"Quiz completed by user {user_id}: {'Correct' if result.is_correct else 'Incorrect'}")
        
    except Exception as e:
        logger.error(f"Error handling quiz answer for user {user_id}: {e}")
        # Clean up active quiz
        if user_id in active_quizzes:
            del active_quizzes[user_id]
        await context.send_activity(MessageFactory.text(
            "❌ Error processing your answer. Please try `/quiz` to start a new question."
        ))

async def handle_sample_command(context: TurnContext, message_text: str):
    """Handle sample question command"""
    try:
        # Parse course from command
        parts = message_text.split()
        if len(parts) < 2:
            await context.send_activity(MessageFactory.text(
                "❌ Please specify a course. Example: `/sample python-basics`\n\n"
                "Available courses: python-basics, javascript-intro, data-science, web-dev"
            ))
            return
        
        course = parts[1]
        available_courses = question_generator.get_available_courses()
        
        if course not in available_courses:
            course_list = ', '.join(available_courses.keys())
            await context.send_activity(MessageFactory.text(
                f"❌ Course '{course}' not found.\n\n"
                f"Available courses: {course_list}"
            ))
            return
        
        # Generate sample question
        await context.send_activity(MessageFactory.text(
            f"🤔 **Generating sample question for {course}...**"
        ))
        
        question = await question_generator.generate_sample_question(course)
        
        if not question:
            await context.send_activity(MessageFactory.text(
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
        
        await context.send_activity(MessageFactory.text(sample_text))
        logger.info(f"Sample question generated for course {course}")
        
    except Exception as e:
        logger.error(f"Error handling sample command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Sorry, I encountered an error generating a sample question."
        ))

async def handle_cancel_command(context: TurnContext, user_id: str):
    """Handle quiz cancellation"""
    if user_id in active_quizzes:
        del active_quizzes[user_id]
        await context.send_activity(MessageFactory.text(
            "✅ **Quiz cancelled.**\n\n"
            "Use `/quiz` when you're ready to try again!"
        ))
    else:
        await context.send_activity(MessageFactory.text(
            "ℹ️ No active quiz to cancel.\n\n"
            "Use `/quiz` to start a new question!"
        ))

# Update the help command to include new quiz features
async def handle_help_command(context: TurnContext):
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
    await context.send_activity(MessageFactory.text(help_text))
```

---

## **Step 4: Test AI Question Generation (15 minutes)**

### 4.1 Test Complete Question Flow in Codespace
```bash
# Restart the bot to load new features
# Stop current bot (Ctrl+C in terminal)
# Then restart:
python src/app.py
```

### 4.2 Verify Codespace is Running
1. **Check** the PORTS tab shows port 3978 forwarded
2. **Ensure** visibility is set to "Public"
3. **Test** endpoint: `curl https://your-codespace-url.github.dev/`

### 4.3 Test in Teams
1. **Open** your bot in Teams
2. **Test** the new commands:

```
/help
/sample python-basics
/enroll python-basics
/quiz
```

4. **Answer** the quiz question with A, B, C, or D
5. **Check** your progress with `/profile`

### 4.4 Verify File Storage in Codespace
```bash
# Check that data files are created in Codespace
ls playground/data/users/
ls playground/data/quizzes/

# View a user profile
cat playground/data/users/*_profile.json
```

---

## **✅ Day 3 Checklist**

Verify all these work:

- [ ] Created `src/sandbox_question_generator.py` with OpenAI integration
- [ ] Created `src/sandbox_answer_evaluator.py` with intelligent feedback
- [ ] Updated `src/bot.py` with quiz functionality
- [ ] `/sample [course]` command shows preview questions
- [ ] `/quiz` command generates personalized questions
- [ ] Quiz questions display properly with multiple choice options
- [ ] Answer evaluation works for A, B, C, D responses
- [ ] User profile updates after answering questions
- [ ] Feedback and performance summary display correctly
- [ ] Quiz cancellation works with `/cancel`
- [ ] Files are saved in `playground/data/` directories in Codespace
- [ ] OpenAI API calls successful (check logs in Codespace terminal)
- [ ] Port forwarding working correctly in Codespace

---

## **🚀 What's Next?**

**Day 4**: We'll add advanced quiz features including adaptive difficulty, topic tracking, and detailed learning analytics - all running seamlessly in your GitHub Codespace.

---

## **💡 Troubleshooting**

### Common Issues:

**OpenAI API errors:**
- Check API key in `.env` file (not .env.sandbox)
- Verify account has sufficient credits
- Check rate limits (especially for free tier)

**Codespace-specific issues:**
- Ensure environment variables are loaded (restart bot if needed)
- Check if port 3978 is properly forwarded
- Verify Codespace hasn't hibernated (restart if inactive)

**Question generation fails:**
- Check OpenAI response format
- Look for JSON parsing errors in logs
- Verify model name is correct (gpt-3.5-turbo)

**Quiz session issues:**
- Clear active_quizzes if bot restarts
- Check user enrollment before starting quiz
- Verify storage permissions

**File storage errors:**
- Ensure `playground/data/` directories exist
- Check write permissions
- Monitor disk space

---

**🎉 Success!** Your AI learning bot now generates personalized questions using OpenAI and provides intelligent feedback to learners!