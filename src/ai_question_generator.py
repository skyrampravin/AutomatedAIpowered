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
from local_storage import LocalStorage, UserProfile

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