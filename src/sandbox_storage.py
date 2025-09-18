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