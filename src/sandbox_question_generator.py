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

            try:
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
                
            except Exception as openai_error:
                self.logger.warning(f"OpenAI API error: {openai_error}. Using fallback question.")
                # Fallback to predefined questions when OpenAI fails
                question_data = self._get_fallback_question(course, topic, difficulty)
            
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
            # Try fallback question
            question_data = self._get_fallback_question(course, topic, difficulty)
            return self._create_question_from_data(course, topic, difficulty, question_data)
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            # Try fallback question
            question_data = self._get_fallback_question(course, topic, difficulty)
            return self._create_question_from_data(course, topic, difficulty, question_data)
    
    def _get_fallback_question(self, course: str, topic: str, difficulty: str) -> Dict[str, Any]:
        """Get a fallback question when OpenAI API is unavailable"""
        fallback_questions = {
            "python-basics": {
                "Variables and Data Types": [
                    {
                        "question_text": "What is the correct way to create a variable in Python?",
                        "options": ["A) var x = 5", "B) x = 5", "C) int x = 5", "D) declare x = 5"],
                        "correct_answer": "B",
                        "explanation": "In Python, variables are created by simply assigning a value using the equals sign. No special keywords are needed.",
                        "estimated_time": 45
                    },
                    {
                        "question_text": "Which of the following is a valid Python variable name?",
                        "options": ["A) 2variable", "B) variable-name", "C) variable_name", "D) variable name"],
                        "correct_answer": "C",
                        "explanation": "Python variable names can contain letters, numbers, and underscores, but cannot start with a number or contain spaces/hyphens.",
                        "estimated_time": 40
                    },
                    {
                        "question_text": "What data type would Python assign to the variable: x = 3.14?",
                        "options": ["A) int", "B) float", "C) string", "D) decimal"],
                        "correct_answer": "B",
                        "explanation": "Python automatically assigns the float data type to numbers with decimal points.",
                        "estimated_time": 35
                    }
                ],
                "Lists and Dictionaries": [
                    {
                        "question_text": "What is the correct way to create a list in Python?",
                        "options": ["A) list = {1, 2, 3}", "B) list = [1, 2, 3]", "C) list = (1, 2, 3)", "D) list = <1, 2, 3>"],
                        "correct_answer": "B",
                        "explanation": "Lists in Python are created using square brackets []. Curly braces {} create sets, parentheses () create tuples.",
                        "estimated_time": 50
                    },
                    {
                        "question_text": "How do you access the first element of a list called 'my_list'?",
                        "options": ["A) my_list[1]", "B) my_list[0]", "C) my_list.first()", "D) my_list.get(1)"],
                        "correct_answer": "B",
                        "explanation": "Python uses zero-based indexing, so the first element is accessed with index [0].",
                        "estimated_time": 45
                    },
                    {
                        "question_text": "What is the correct syntax to create a dictionary in Python?",
                        "options": ["A) dict = [key: value]", "B) dict = (key: value)", "C) dict = {key: value}", "D) dict = <key: value>"],
                        "correct_answer": "C",
                        "explanation": "Dictionaries in Python are created using curly braces {} with key-value pairs separated by colons.",
                        "estimated_time": 55
                    }
                ],
                "Functions and Parameters": [
                    {
                        "question_text": "How do you define a function in Python?",
                        "options": ["A) function myFunc():", "B) def myFunc():", "C) func myFunc():", "D) define myFunc():"],
                        "correct_answer": "B",
                        "explanation": "Functions in Python are defined using the 'def' keyword followed by the function name and parentheses.",
                        "estimated_time": 40
                    },
                    {
                        "question_text": "How do you call a function named 'calculate' with no parameters?",
                        "options": ["A) call calculate()", "B) calculate()", "C) run calculate", "D) execute calculate()"],
                        "correct_answer": "B",
                        "explanation": "Functions are called by writing the function name followed by parentheses, even if no parameters are needed.",
                        "estimated_time": 35
                    }
                ],
                "Control Flow (if/else, loops)": [
                    {
                        "question_text": "What is the correct syntax for an if statement in Python?",
                        "options": ["A) if (x == 5) {", "B) if x == 5:", "C) if x = 5:", "D) if x equals 5:"],
                        "correct_answer": "B",
                        "explanation": "Python if statements use a colon (:) and do not require parentheses or curly braces.",
                        "estimated_time": 45
                    },
                    {
                        "question_text": "Which loop is best for iterating over a list in Python?",
                        "options": ["A) while loop", "B) for loop", "C) do-while loop", "D) repeat loop"],
                        "correct_answer": "B",
                        "explanation": "For loops are ideal for iterating over sequences like lists, strings, and tuples in Python.",
                        "estimated_time": 50
                    }
                ],
                "Object-Oriented Programming Basics": [
                    {
                        "question_text": "How do you define a class in Python?",
                        "options": ["A) class MyClass:", "B) Class MyClass:", "C) define MyClass:", "D) object MyClass:"],
                        "correct_answer": "A",
                        "explanation": "Classes in Python are defined using the 'class' keyword (lowercase) followed by the class name and a colon.",
                        "estimated_time": 50
                    },
                    {
                        "question_text": "What is the special method used to initialize objects in a Python class?",
                        "options": ["A) __start__()", "B) __create__()", "C) __init__()", "D) __new__()"],
                        "correct_answer": "C",
                        "explanation": "The __init__() method is automatically called when a new object is created from a class.",
                        "estimated_time": 55
                    }
                ]
            },
            "javascript-intro": {
                "Variables (let, const, var)": [
                    {
                        "question_text": "Which keyword should you use to declare a variable that won't be reassigned?",
                        "options": ["A) var", "B) let", "C) const", "D) final"],
                        "correct_answer": "C",
                        "explanation": "The 'const' keyword is used for variables that won't be reassigned after their initial value.",
                        "estimated_time": 40
                    },
                    {
                        "question_text": "What is the difference between 'let' and 'var' in JavaScript?",
                        "options": ["A) No difference", "B) 'let' has block scope, 'var' has function scope", "C) 'var' is newer", "D) 'let' is faster"],
                        "correct_answer": "B",
                        "explanation": "'let' has block scope (limited to the nearest enclosing block), while 'var' has function scope.",
                        "estimated_time": 60
                    }
                ],
                "Functions and Arrow Functions": [
                    {
                        "question_text": "What is the correct syntax for an arrow function in JavaScript?",
                        "options": ["A) function => {}", "B) () => {}", "C) -> {}", "D) lambda {}"],
                        "correct_answer": "B",
                        "explanation": "Arrow functions use the syntax () => {} where parameters go in parentheses followed by => and the function body.",
                        "estimated_time": 45
                    }
                ],
                "Arrays and Objects": [
                    {
                        "question_text": "How do you add an element to the end of a JavaScript array?",
                        "options": ["A) array.add(element)", "B) array.push(element)", "C) array.append(element)", "D) array.insert(element)"],
                        "correct_answer": "B",
                        "explanation": "The push() method adds one or more elements to the end of an array and returns the new length.",
                        "estimated_time": 40
                    }
                ]
            },
            "data-science": {
                "Data Types and Structures": [
                    {
                        "question_text": "Which Python library is most commonly used for data manipulation?",
                        "options": ["A) NumPy", "B) Pandas", "C) Matplotlib", "D) Scikit-learn"],
                        "correct_answer": "B",
                        "explanation": "Pandas is the primary library for data manipulation and analysis, providing DataFrames and Series structures.",
                        "estimated_time": 45
                    }
                ],
                "Statistics and Probability": [
                    {
                        "question_text": "What does a p-value represent in statistical testing?",
                        "options": ["A) The probability of the hypothesis being true", "B) The probability of observing the data given the null hypothesis is true", "C) The power of the test", "D) The confidence interval"],
                        "correct_answer": "B",
                        "explanation": "A p-value is the probability of observing the test results under the assumption that the null hypothesis is correct.",
                        "estimated_time": 70
                    }
                ]
            },
            "web-dev": {
                "HTML5 Semantics": [
                    {
                        "question_text": "Which HTML5 element should be used for the main content of a page?",
                        "options": ["A) <div>", "B) <main>", "C) <content>", "D) <section>"],
                        "correct_answer": "B",
                        "explanation": "The <main> element represents the main content of the page, excluding headers, footers, and sidebars.",
                        "estimated_time": 40
                    }
                ],
                "CSS3 and Flexbox": [
                    {
                        "question_text": "Which CSS property is used to create a flex container?",
                        "options": ["A) display: flex", "B) flex: container", "C) layout: flex", "D) position: flex"],
                        "correct_answer": "A",
                        "explanation": "The display: flex property turns an element into a flex container, enabling flexbox layout for its children.",
                        "estimated_time": 45
                    }
                ]
            }
        }
        
        # Get fallback question or create a generic one
        course_questions = fallback_questions.get(course, {})
        topic_questions = course_questions.get(topic, [])
        
        if topic_questions:
            # Select a random question from the available ones for this topic
            selected_question = random.choice(topic_questions)
            return selected_question
        else:
            # Generic fallback with more realistic content
            difficulty_indicators = {
                "beginner": "fundamental",
                "intermediate": "practical", 
                "advanced": "complex"
            }
            
            indicator = difficulty_indicators.get(difficulty, "sample")
            
            return {
                "question_text": f"This is a {indicator} {difficulty}-level question about {topic} in {course.replace('-', ' ')}. What is the best practice for implementing this concept?",
                "options": [
                    "A) Use the most common approach with basic syntax", 
                    "B) Follow industry best practices and conventions", 
                    "C) Optimize for performance over readability", 
                    "D) Use the newest available features"
                ],
                "correct_answer": "B",
                "explanation": f"Following industry best practices ensures your {topic.lower()} code is maintainable, readable, and follows established conventions in {course.replace('-', ' ')}.",
                "estimated_time": 60
            }
    
    def _create_question_from_data(self, course: str, topic: str, difficulty: str, question_data: Dict[str, Any]) -> QuizQuestion:
        """Create a QuizQuestion object from question data"""
        return QuizQuestion(
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