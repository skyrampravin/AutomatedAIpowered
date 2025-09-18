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