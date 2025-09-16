# Day 6: Course Completion & Data Export (Codespaces)

## 🎯 **Goal**: Implement course completion certificates, progress export, and prepare for production features

**Time Required**: 75-90 minutes  
**Prerequisites**: Day 1-5 completed (Codespace with gamification)  
**Outcome**: Complete learning platform with certificates and data portability in cloud

---

## **Step 1: Course Completion System (25 minutes)**

### 1.1 Create Course Manager
1. **Create**: `src/sandbox_course_manager.py`

```python
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics

from config import Config
from sandbox_storage import SandboxStorage, UserProfile
from sandbox_learning_analytics import SandboxLearningAnalytics, TopicPerformance
from sandbox_achievements import SandboxAchievementSystem, Certificate

@dataclass
class CourseProgress:
    course: str
    user_id: str
    enrolled_date: str
    completion_percentage: float
    topics_completed: List[str]
    topics_in_progress: List[str]
    topics_not_started: List[str]
    overall_accuracy: float
    time_spent_hours: float
    estimated_completion_date: str
    is_completed: bool

@dataclass
class CourseCertificate:
    certificate_id: str
    user_id: str
    course: str
    completion_date: str
    final_accuracy: float
    total_questions_answered: int
    time_spent_days: int
    achievements_earned: int
    grade: str  # "A+", "A", "B+", "B", "C", "Incomplete"
    certificate_data: Dict[str, Any]

class SandboxCourseManager:
    """Complete course management and certification system"""
    
    def __init__(self, config: Config, storage: SandboxStorage, analytics: SandboxLearningAnalytics, achievements: SandboxAchievementSystem):
        self.config = config
        self.storage = storage
        self.analytics = analytics
        self.achievements = achievements
        self.logger = logging.getLogger(__name__)
        
        # Course requirements
        self.course_requirements = self._initialize_course_requirements()
        
        # Certificate storage
        self.certificate_dir = f"{config.DATA_DIRECTORY}/certificates"
        os.makedirs(self.certificate_dir, exist_ok=True)
    
    def _initialize_course_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize course completion requirements"""
        return {
            "python-basics": {
                "min_questions_per_topic": 5,
                "min_overall_accuracy": 0.75,
                "min_topic_mastery": 6,  # Must master 6 out of 8 topics
                "total_topics": 8,
                "estimated_duration_days": 14,
                "passing_grades": {
                    "A+": 0.95, "A": 0.90, "B+": 0.85, "B": 0.80, "C": 0.75
                }
            },
            "javascript-intro": {
                "min_questions_per_topic": 5,
                "min_overall_accuracy": 0.75,
                "min_topic_mastery": 6,
                "total_topics": 8,
                "estimated_duration_days": 14,
                "passing_grades": {
                    "A+": 0.95, "A": 0.90, "B+": 0.85, "B": 0.80, "C": 0.75
                }
            },
            "data-science": {
                "min_questions_per_topic": 6,
                "min_overall_accuracy": 0.70,
                "min_topic_mastery": 6,
                "total_topics": 8,
                "estimated_duration_days": 21,
                "passing_grades": {
                    "A+": 0.92, "A": 0.87, "B+": 0.82, "B": 0.77, "C": 0.70
                }
            },
            "web-dev": {
                "min_questions_per_topic": 5,
                "min_overall_accuracy": 0.75,
                "min_topic_mastery": 7,
                "total_topics": 8,
                "estimated_duration_days": 18,
                "passing_grades": {
                    "A+": 0.95, "A": 0.90, "B+": 0.85, "B": 0.80, "C": 0.75
                }
            }
        }
    
    def check_course_completion(self, user_id: str) -> Optional[CourseProgress]:
        """Check if user has completed their enrolled course"""
        try:
            profile = self.storage.get_user_profile(user_id)
            if not profile or not profile.enrolled_course:
                return None
            
            course = profile.enrolled_course
            if course not in self.course_requirements:
                return None
            
            requirements = self.course_requirements[course]
            
            # Get user's performance analysis
            analysis = self.analytics.analyze_user_performance(user_id)
            if "error" in analysis:
                return None
            
            topic_performance = analysis.get("topic_performance", {})
            
            # Analyze completion status
            topics_completed = []
            topics_in_progress = []
            topics_not_started = []
            
            # Get course topics
            from sandbox_question_generator import SandboxQuestionGenerator
            temp_generator = SandboxQuestionGenerator(self.config, self.storage)
            curricula = temp_generator.get_available_courses()
            course_topics = curricula[course]["topics"]
            
            for topic in course_topics:
                if topic in topic_performance:
                    perf = topic_performance[topic]
                    if hasattr(perf, 'mastery_level'):
                        if perf.mastery_level in ["proficient", "mastered"]:
                            topics_completed.append(topic)
                        elif perf.total_questions >= requirements["min_questions_per_topic"] // 2:
                            topics_in_progress.append(topic)
                        else:
                            topics_not_started.append(topic)
                    else:
                        topics_not_started.append(topic)
                else:
                    topics_not_started.append(topic)
            
            # Calculate completion percentage
            completion_percentage = len(topics_completed) / len(course_topics) * 100
            
            # Calculate time spent
            time_spent_hours = self._calculate_time_spent(profile)
            
            # Determine if course is completed
            overall_accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
            mastered_topics = len(topics_completed)
            
            is_completed = (
                overall_accuracy >= requirements["min_overall_accuracy"] and
                mastered_topics >= requirements["min_topic_mastery"] and
                len(topics_not_started) == 0
            )
            
            # Estimate completion date
            if is_completed:
                estimated_completion_date = datetime.now().isoformat()
            else:
                remaining_topics = len(topics_not_started) + len(topics_in_progress)
                days_per_topic = 2  # Estimate
                estimated_days = remaining_topics * days_per_topic
                estimated_completion_date = (datetime.now() + timedelta(days=estimated_days)).isoformat()
            
            return CourseProgress(
                course=course,
                user_id=user_id,
                enrolled_date=profile.start_date or "",
                completion_percentage=completion_percentage,
                topics_completed=topics_completed,
                topics_in_progress=topics_in_progress,
                topics_not_started=topics_not_started,
                overall_accuracy=overall_accuracy,
                time_spent_hours=time_spent_hours,
                estimated_completion_date=estimated_completion_date,
                is_completed=is_completed
            )
            
        except Exception as e:
            self.logger.error(f"Error checking course completion for user {user_id}: {e}")
            return None
    
    def generate_certificate(self, user_id: str) -> Optional[CourseCertificate]:
        """Generate course completion certificate"""
        try:
            progress = self.check_course_completion(user_id)
            if not progress or not progress.is_completed:
                return None
            
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                return None
            
            course = progress.course
            requirements = self.course_requirements[course]
            
            # Calculate grade
            grade = self._calculate_grade(progress.overall_accuracy, requirements["passing_grades"])
            
            # Get achievements earned during course
            user_achievements = self.achievements.get_user_achievements(user_id)
            
            # Calculate time spent in days
            time_spent_days = self._calculate_learning_days(profile.start_date)
            
            # Generate certificate
            certificate_id = f"cert_{user_id}_{course}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            certificate_data = {
                "template": "standard_completion",
                "issued_by": "AI Learning Bot - Sandbox Mode",
                "course_title": course.replace('-', ' ').title(),
                "completion_requirements": {
                    "min_accuracy": requirements["min_overall_accuracy"],
                    "topics_mastered": len(progress.topics_completed),
                    "total_questions": profile.total_questions
                },
                "verification_code": f"VERIFY-{certificate_id[-8:].upper()}",
                "digital_signature": "sandbox_verified"
            }
            
            certificate = CourseCertificate(
                certificate_id=certificate_id,
                user_id=user_id,
                course=course,
                completion_date=datetime.now().isoformat(),
                final_accuracy=progress.overall_accuracy,
                total_questions_answered=profile.total_questions,
                time_spent_days=time_spent_days,
                achievements_earned=len(user_achievements),
                grade=grade,
                certificate_data=certificate_data
            )
            
            # Save certificate
            self._save_certificate(certificate)
            
            # Mark course as completed
            profile.completed_course = True
            self.storage.save_user_profile(profile)
            
            self.logger.info(f"Certificate generated for user {user_id}, course {course}, grade {grade}")
            return certificate
            
        except Exception as e:
            self.logger.error(f"Error generating certificate for user {user_id}: {e}")
            return None
    
    def _calculate_grade(self, accuracy: float, grade_thresholds: Dict[str, float]) -> str:
        """Calculate letter grade based on accuracy"""
        for grade, threshold in sorted(grade_thresholds.items(), key=lambda x: x[1], reverse=True):
            if accuracy >= threshold:
                return grade
        return "Incomplete"
    
    def _calculate_time_spent(self, profile: UserProfile) -> float:
        """Calculate estimated time spent learning (in hours)"""
        # Rough estimate: 2 minutes per question on average
        return (profile.total_questions * 2) / 60.0
    
    def _calculate_learning_days(self, start_date: str) -> int:
        """Calculate days since learning started"""
        try:
            if not start_date:
                return 0
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            return (datetime.now() - start).days
        except:
            return 0
    
    def _save_certificate(self, certificate: CourseCertificate):
        """Save certificate to file"""
        try:
            file_path = f"{self.certificate_dir}/{certificate.certificate_id}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(certificate), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving certificate: {e}")
    
    def get_user_certificates(self, user_id: str) -> List[CourseCertificate]:
        """Get all certificates for a user"""
        try:
            certificates = []
            for filename in os.listdir(self.certificate_dir):
                if filename.startswith(f"cert_{user_id}_") and filename.endswith('.json'):
                    file_path = os.path.join(self.certificate_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            certificates.append(CourseCertificate(**data))
                    except:
                        continue
            
            return sorted(certificates, key=lambda x: x.completion_date, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting certificates for user {user_id}: {e}")
            return []
    
    def get_course_statistics(self, course: str) -> Dict[str, Any]:
        """Get statistics for a specific course"""
        try:
            if course not in self.course_requirements:
                return {"error": "Course not found"}
            
            requirements = self.course_requirements[course]
            
            # In a full implementation, this would aggregate data from all users
            # For sandbox mode, return course information
            
            from sandbox_question_generator import SandboxQuestionGenerator
            temp_generator = SandboxQuestionGenerator(self.config, self.storage)
            curricula = temp_generator.get_available_courses()
            
            course_info = curricula.get(course, {})
            
            return {
                "course": course,
                "title": course.replace('-', ' ').title(),
                "description": course_info.get("description", ""),
                "topics": course_info.get("topics", []),
                "total_topics": requirements["total_topics"],
                "requirements": {
                    "min_accuracy": requirements["min_overall_accuracy"],
                    "min_topic_mastery": requirements["min_topic_mastery"],
                    "min_questions_per_topic": requirements["min_questions_per_topic"]
                },
                "estimated_duration": requirements["estimated_duration_days"],
                "difficulty_levels": course_info.get("difficulty_levels", []),
                "passing_grades": requirements["passing_grades"]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting course statistics for {course}: {e}")
            return {"error": str(e)}
```

---

## **Step 2: Data Export System (20 minutes)**

### 2.1 Create Export Manager
1. **Create**: `src/sandbox_export_manager.py`

```python
import os
import json
import csv
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict
import zipfile

from config import Config
from sandbox_storage import SandboxStorage
from sandbox_learning_analytics import SandboxLearningAnalytics
from sandbox_achievements import SandboxAchievementSystem
from sandbox_course_manager import SandboxCourseManager

class SandboxExportManager:
    """Data export and portability system"""
    
    def __init__(self, config: Config, storage: SandboxStorage, analytics: SandboxLearningAnalytics, 
                 achievements: SandboxAchievementSystem, course_manager: SandboxCourseManager):
        self.config = config
        self.storage = storage
        self.analytics = analytics
        self.achievements = achievements
        self.course_manager = course_manager
        self.logger = logging.getLogger(__name__)
        
        # Export directory
        self.export_dir = f"{config.DATA_DIRECTORY}/exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_user_data(self, user_id: str, export_format: str = "json") -> Optional[str]:
        """Export all user data in specified format"""
        try:
            # Gather all user data
            user_data = self._gather_user_data(user_id)
            if not user_data:
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format.lower() == "json":
                return self._export_json(user_data, user_id, timestamp)
            elif export_format.lower() == "csv":
                return self._export_csv(user_data, user_id, timestamp)
            elif export_format.lower() == "zip":
                return self._export_zip(user_data, user_id, timestamp)
            else:
                self.logger.error(f"Unsupported export format: {export_format}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error exporting user data for {user_id}: {e}")
            return None
    
    def _gather_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Gather comprehensive user data for export"""
        try:
            # User profile
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                return None
            
            # Learning analytics
            analytics_data = self.analytics.analyze_user_performance(user_id)
            
            # Achievements and gamification
            user_achievements = self.achievements.get_user_achievements(user_id)
            user_badges = self.achievements.get_user_badges(user_id)
            total_points = self.achievements.calculate_user_score(user_id)
            
            # Course progress
            course_progress = self.course_manager.check_course_completion(user_id)
            
            # Certificates
            certificates = self.course_manager.get_user_certificates(user_id)
            
            # Quiz history
            quiz_history = self.storage.get_user_quiz_history(user_id)
            
            # Compile export data
            export_data = {
                "export_metadata": {
                    "user_id": user_id,
                    "export_date": datetime.now().isoformat(),
                    "export_version": "1.0",
                    "source": "AI Learning Bot - Sandbox Mode"
                },
                "user_profile": asdict(profile) if profile else {},
                "learning_analytics": analytics_data,
                "achievements": {
                    "earned": [asdict(ach) for ach in user_achievements],
                    "total_points": total_points,
                    "badges": [asdict(badge) for badge in user_badges]
                },
                "course_progress": asdict(course_progress) if course_progress else {},
                "certificates": [asdict(cert) for cert in certificates],
                "quiz_history": quiz_history,
                "storage_stats": self.storage.get_storage_stats()
            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error gathering user data for {user_id}: {e}")
            return None
    
    def _export_json(self, user_data: Dict[str, Any], user_id: str, timestamp: str) -> str:
        """Export data as JSON file"""
        try:
            filename = f"user_data_{user_id}_{timestamp}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(user_data, f, indent=2)
            
            self.logger.info(f"JSON export completed: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting JSON: {e}")
            return None
    
    def _export_csv(self, user_data: Dict[str, Any], user_id: str, timestamp: str) -> str:
        """Export data as CSV files (multiple files in a directory)"""
        try:
            export_folder = f"user_data_{user_id}_{timestamp}"
            folder_path = os.path.join(self.export_dir, export_folder)
            os.makedirs(folder_path, exist_ok=True)
            
            # Export profile data
            if user_data.get("user_profile"):
                profile_file = os.path.join(folder_path, "profile.csv")
                with open(profile_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Field", "Value"])
                    for key, value in user_data["user_profile"].items():
                        writer.writerow([key, str(value)])
            
            # Export quiz history
            if user_data.get("quiz_history"):
                quiz_file = os.path.join(folder_path, "quiz_history.csv")
                with open(quiz_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    if user_data["quiz_history"]:
                        # Headers
                        headers = ["session_id", "completed_date", "score", "time_taken", "questions_count"]
                        writer.writerow(headers)
                        
                        for session in user_data["quiz_history"]:
                            row = [
                                session.get("session_id", ""),
                                session.get("completed_date", ""),
                                session.get("score", 0),
                                session.get("time_taken", 0),
                                len(session.get("questions", []))
                            ]
                            writer.writerow(row)
            
            # Export achievements
            if user_data.get("achievements", {}).get("earned"):
                ach_file = os.path.join(folder_path, "achievements.csv")
                with open(ach_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Achievement ID", "Unlocked Date"])
                    for ach in user_data["achievements"]["earned"]:
                        writer.writerow([ach.get("achievement_id", ""), ach.get("unlocked_date", "")])
            
            # Export topic performance
            if user_data.get("learning_analytics", {}).get("topic_performance"):
                topic_file = os.path.join(folder_path, "topic_performance.csv")
                with open(topic_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Topic", "Total Questions", "Correct Answers", "Accuracy", "Mastery Level"])
                    for topic, perf in user_data["learning_analytics"]["topic_performance"].items():
                        if hasattr(perf, 'total_questions'):
                            writer.writerow([
                                topic,
                                perf.total_questions,
                                perf.correct_answers,
                                f"{perf.accuracy:.2%}",
                                perf.mastery_level
                            ])
            
            self.logger.info(f"CSV export completed: {folder_path}")
            return folder_path
            
        except Exception as e:
            self.logger.error(f"Error exporting CSV: {e}")
            return None
    
    def _export_zip(self, user_data: Dict[str, Any], user_id: str, timestamp: str) -> str:
        """Export data as ZIP archive with multiple formats"""
        try:
            zip_filename = f"user_data_{user_id}_{timestamp}.zip"
            zip_filepath = os.path.join(self.export_dir, zip_filename)
            
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add JSON export
                json_content = json.dumps(user_data, indent=2)
                zipf.writestr(f"user_data_{user_id}.json", json_content)
                
                # Add CSV exports
                # Profile CSV
                if user_data.get("user_profile"):
                    csv_content = "Field,Value\\n"
                    for key, value in user_data["user_profile"].items():
                        csv_content += f'"{key}","{str(value)}"\\n'
                    zipf.writestr("profile.csv", csv_content)
                
                # Quiz history CSV
                if user_data.get("quiz_history"):
                    csv_content = "Session ID,Date,Score,Time Taken,Questions\\n"
                    for session in user_data["quiz_history"]:
                        csv_content += f'"{session.get("session_id", "")}","{session.get("completed_date", "")}",{session.get("score", 0)},{session.get("time_taken", 0)},{len(session.get("questions", []))}\\n'
                    zipf.writestr("quiz_history.csv", csv_content)
                
                # Achievements CSV
                if user_data.get("achievements", {}).get("earned"):
                    csv_content = "Achievement ID,Unlocked Date\\n"
                    for ach in user_data["achievements"]["earned"]:
                        csv_content += f'"{ach.get("achievement_id", "")}","{ach.get("unlocked_date", "")}\"\\n'
                    zipf.writestr("achievements.csv", csv_content)
                
                # Add README
                readme_content = f"""
AI Learning Bot - User Data Export
==================================

User ID: {user_id}
Export Date: {datetime.now().isoformat()}
Export Version: 1.0
Source: AI Learning Bot - Sandbox Mode

Files Included:
- user_data_{user_id}.json: Complete data in JSON format
- profile.csv: User profile information
- quiz_history.csv: Complete quiz session history
- achievements.csv: Earned achievements and unlock dates

Data Privacy:
This export contains your personal learning data from the AI Learning Bot.
Keep this file secure and do not share it with unauthorized parties.

For questions about this export, contact support.
"""
                zipf.writestr("README.txt", readme_content)
            
            self.logger.info(f"ZIP export completed: {zip_filepath}")
            return zip_filepath
            
        except Exception as e:
            self.logger.error(f"Error creating ZIP export: {e}")
            return None
    
    def generate_progress_report(self, user_id: str) -> Optional[str]:
        """Generate detailed progress report"""
        try:
            user_data = self._gather_user_data(user_id)
            if not user_data:
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"progress_report_{user_id}_{timestamp}.txt"
            filepath = os.path.join(self.export_dir, filename)
            
            # Generate human-readable report
            with open(filepath, 'w') as f:
                f.write("AI LEARNING BOT - PROGRESS REPORT\\n")
                f.write("=" * 50 + "\\n\\n")
                
                # User info
                profile = user_data.get("user_profile", {})
                f.write(f"User ID: {user_id}\\n")
                f.write(f"Course: {profile.get('enrolled_course', 'N/A')}\\n")
                f.write(f"Start Date: {profile.get('start_date', 'N/A')[:10]}\\n")
                f.write(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
                
                # Overall performance
                f.write("OVERALL PERFORMANCE\\n")
                f.write("-" * 20 + "\\n")
                f.write(f"Total Questions: {profile.get('total_questions', 0)}\\n")
                f.write(f"Correct Answers: {profile.get('correct_answers', 0)}\\n")
                accuracy = profile.get('correct_answers', 0) / profile.get('total_questions', 1) if profile.get('total_questions', 0) > 0 else 0
                f.write(f"Overall Accuracy: {accuracy:.1%}\\n")
                f.write(f"Current Streak: {profile.get('current_streak', 0)}\\n")
                f.write(f"Best Streak: {profile.get('longest_streak', 0)}\\n\\n")
                
                # Topic performance
                f.write("TOPIC PERFORMANCE\\n")
                f.write("-" * 17 + "\\n")
                topic_perf = user_data.get("learning_analytics", {}).get("topic_performance", {})
                if topic_perf:
                    for topic, perf in topic_perf.items():
                        if hasattr(perf, 'total_questions'):
                            f.write(f"{topic}:\\n")
                            f.write(f"  Questions: {perf.total_questions}\\n")
                            f.write(f"  Accuracy: {perf.accuracy:.1%}\\n")
                            f.write(f"  Mastery: {perf.mastery_level.title()}\\n\\n")
                
                # Achievements
                f.write("ACHIEVEMENTS\\n")
                f.write("-" * 12 + "\\n")
                achievements = user_data.get("achievements", {}).get("earned", [])
                f.write(f"Total Achievements: {len(achievements)}\\n")
                f.write(f"Total Points: {user_data.get('achievements', {}).get('total_points', 0)}\\n")
                if achievements:
                    for ach in achievements[-5:]:  # Show last 5
                        f.write(f"- {ach.get('achievement_id', '')} (unlocked: {ach.get('unlocked_date', '')[:10]})\\n")
                f.write("\\n")
                
                # Recommendations
                recommendations = user_data.get("learning_analytics", {}).get("recommendations", [])
                if recommendations:
                    f.write("RECOMMENDATIONS\\n")
                    f.write("-" * 15 + "\\n")
                    for i, rec in enumerate(recommendations[:5], 1):
                        f.write(f"{i}. {rec}\\n")
                
                f.write("\\n" + "=" * 50 + "\\n")
                f.write("End of Report\\n")
            
            self.logger.info(f"Progress report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating progress report: {e}")
            return None
    
    def cleanup_old_exports(self, days_old: int = 30):
        """Clean up old export files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for filename in os.listdir(self.export_dir):
                filepath = os.path.join(self.export_dir, filename)
                if os.path.isfile(filepath):
                    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_modified < cutoff_date:
                        os.remove(filepath)
                        cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} old export files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up exports: {e}")
            return 0
```

---

## **Step 3: Update Bot with Completion Features (15 minutes)**

### 3.1 Add Course Completion and Export Commands
1. **Update** `src/bot.py` to add completion and export features:

```python
# Add these imports at the top
from sandbox_course_manager import SandboxCourseManager
from sandbox_export_manager import SandboxExportManager

# Add after gamification initialization
course_manager = SandboxCourseManager(config, storage, learning_analytics, achievement_system)
export_manager = SandboxExportManager(config, storage, learning_analytics, achievement_system, course_manager)

# Add new command handlers
async def handle_completion_command(context: TurnContext, user_id: str):
    """Show course completion status and certificate options"""
    try:
        progress = course_manager.check_course_completion(user_id)
        
        if not progress:
            await context.send_activity(MessageFactory.text(
                "📚 **Course Completion Status**\\n\\n"
                "❌ No active course enrollment found.\\n"
                "Use `/enroll [course-name]` to start a course!"
            ))
            return
        
        completion_text = f"""
📚 **Course Completion Status**

**Course**: {progress.course.replace('-', ' ').title()}
**Progress**: {progress.completion_percentage:.1f}% Complete

📊 **Topic Progress**:
✅ **Completed** ({len(progress.topics_completed)}): {', '.join(progress.topics_completed) if progress.topics_completed else 'None'}

🔄 **In Progress** ({len(progress.topics_in_progress)}): {', '.join(progress.topics_in_progress) if progress.topics_in_progress else 'None'}

📝 **Not Started** ({len(progress.topics_not_started)}): {', '.join(progress.topics_not_started) if progress.topics_not_started else 'None'}

📈 **Performance**:
• Overall Accuracy: {progress.overall_accuracy:.1%}
• Time Spent: {progress.time_spent_hours:.1f} hours
• Enrolled: {progress.enrolled_date[:10] if progress.enrolled_date else 'Unknown'}
"""
        
        if progress.is_completed:
            completion_text += "\\n🎉 **COURSE COMPLETED!** 🎉\\n"
            completion_text += "Use `/certificate` to generate your completion certificate!"
        else:
            completion_text += f"\\n🎯 **Estimated Completion**: {progress.estimated_completion_date[:10]}"
            completion_text += "\\nKeep practicing to complete your course!"
        
        await context.send_activity(MessageFactory.text(completion_text))
        
    except Exception as e:
        logger.error(f"Error handling completion command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error checking course completion. Please try again."
        ))

async def handle_certificate_command(context: TurnContext, user_id: str):
    """Generate and display course completion certificate"""
    try:
        # Check if course is completed
        progress = course_manager.check_course_completion(user_id)
        
        if not progress or not progress.is_completed:
            await context.send_activity(MessageFactory.text(
                "📜 **Certificate Generation**\\n\\n"
                "❌ Course not yet completed.\\n\\n"
                "Complete your enrolled course first:\\n"
                "• Master all required topics\\n"
                "• Maintain minimum accuracy\\n"
                "• Answer sufficient questions per topic\\n\\n"
                "Use `/completion` to check your progress!"
            ))
            return
        
        # Generate certificate
        certificate = course_manager.generate_certificate(user_id)
        
        if not certificate:
            await context.send_activity(MessageFactory.text(
                "❌ Error generating certificate. Please contact support."
            ))
            return
        
        # Display certificate
        certificate_text = f"""
🎓 **COURSE COMPLETION CERTIFICATE** 🎓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📜 **CERTIFICATE OF COMPLETION**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Student**: User {user_id[:8]}...
**Course**: {certificate.course.replace('-', ' ').title()}
**Completion Date**: {certificate.completion_date[:10]}

**Performance Summary**:
🎯 **Final Grade**: {certificate.grade}
📊 **Final Accuracy**: {certificate.final_accuracy:.1%}
📝 **Questions Answered**: {certificate.total_questions_answered}
📅 **Time Investment**: {certificate.time_spent_days} days
🏆 **Achievements Earned**: {certificate.achievements_earned}

**Certificate Details**:
🔍 **Verification Code**: {certificate.certificate_data['verification_code']}
✅ **Digital Signature**: {certificate.certificate_data['digital_signature']}
🏛️ **Issued By**: {certificate.certificate_data['issued_by']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 **Congratulations on your achievement!** 🎉

*This certificate verifies successful completion of the course requirements including mastery of topics, accuracy standards, and comprehensive assessment.*
"""
        
        await context.send_activity(MessageFactory.text(certificate_text))
        
        # Offer export options
        await context.send_activity(MessageFactory.text(
            "📤 **Want to keep your certificate?**\\n\\n"
            "Use `/export` to download all your learning data including certificates!"
        ))
        
    except Exception as e:
        logger.error(f"Error handling certificate command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error generating certificate. Please try again."
        ))

async def handle_export_command(context: TurnContext, user_id: str, message_text: str = ""):
    """Handle data export request"""
    try:
        # Parse export format
        parts = message_text.lower().split()
        export_format = "json"  # default
        
        if len(parts) > 1 and parts[1] in ["json", "csv", "zip"]:
            export_format = parts[1]
        
        await context.send_activity(MessageFactory.text(
            f"📤 **Exporting your data in {export_format.upper()} format...**\\n\\n"
            "This may take a moment..."
        ))
        
        # Export user data
        export_path = export_manager.export_user_data(user_id, export_format)
        
        if not export_path:
            await context.send_activity(MessageFactory.text(
                "❌ Export failed. Please try again or contact support."
            ))
            return
        
        # Get file info
        file_size = os.path.getsize(export_path) / 1024  # KB
        
        export_text = f"""
✅ **Export Complete!**

📁 **File Created**: {os.path.basename(export_path)}
📊 **Format**: {export_format.upper()}
💾 **Size**: {file_size:.1f} KB
📅 **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Export Contains**:
✅ Complete learning profile
✅ Quiz history and performance
✅ All achievements and badges
✅ Course progress and certificates
✅ Detailed analytics data

**File Location** (Sandbox Mode):
`{export_path}`

**Note**: In production mode, this would be available for download through a secure link.

**Data Privacy**: Your exported data is stored securely and only accessible to you.
"""
        
        await context.send_activity(MessageFactory.text(export_text))
        
    except Exception as e:
        logger.error(f"Error handling export command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error creating export. Please try again."
        ))

# Update the message handler to include new commands
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
        elif message_lower.startswith('/completion'):
            await handle_completion_command(context, user_id)
        elif message_lower.startswith('/certificate'):
            await handle_certificate_command(context, user_id)
        elif message_lower.startswith('/export'):
            await handle_export_command(context, user_id, message_text)
        elif message_lower.startswith('/achievements'):
            await handle_achievements_command(context, user_id)
        elif message_lower.startswith('/level'):
            await handle_level_command(context, user_id)
        elif message_lower.startswith('/analytics'):
            await handle_analytics_command(context, user_id)
        elif message_lower.startswith('/progress'):
            await handle_progress_command(context, user_id)
        elif message_lower.startswith('/topics'):
            await handle_topics_command(context, user_id)
        elif message_lower.startswith('/quiz'):
            await handle_quiz_command(context, user_id)
        elif message_lower.startswith('/sample'):
            await handle_sample_command(context, message_text)
        elif message_lower.startswith('/study'):
            await handle_study_command(context, user_id)
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

# Update the help command to include completion features
async def handle_help_command(context: TurnContext):
    """Show help information"""
    help_text = """
🤖 **AI Learning Bot - Complete Learning Platform** 🤖

**🎓 Course Completion:**
• `/completion` - Check course completion status
• `/certificate` - Generate completion certificate
• `/export [format]` - Export all your data (json/csv/zip)

**🎮 Gamification Features:**
• `/achievements` - View earned achievements and badges
• `/level` - Check your level and progress
• `/quiz` - Take adaptive quizzes (earn points!)

**📚 Learning Commands:**
• `/sample [course]` - Preview sample questions
• `/cancel` - Cancel current quiz

**📊 Progress & Analytics:**
• `/profile` - View basic learning profile
• `/analytics` - Detailed performance analytics
• `/progress` - Progress by topic with mastery levels
• `/topics` - Course topics and recommendations
• `/study` - Personalized study plan

**👤 Account Commands:**
• `/enroll [course]` - Enroll in a learning course
• `/help` - Show this help message

**🔧 System Commands:**
• `/status` - Check bot system status
• `/admin` - View system statistics

**🚀 Available Courses:**
• `python-basics` - Python fundamentals
• `javascript-intro` - JavaScript introduction  
• `data-science` - Data Science concepts
• `web-dev` - Web Development

**🎯 Course Completion Requirements:**
• Master 6+ topics per course
• Maintain 75%+ overall accuracy
• Complete minimum questions per topic
• Earn completion certificate with grade

**📤 Data Export Options:**
• JSON: Complete structured data
• CSV: Spreadsheet-compatible format
• ZIP: Multiple formats in archive

**Quick Start:**
```
/enroll python-basics
/quiz (repeat multiple times)
/completion
/certificate
/export
```

*🎓 Day 6: Complete learning platform with certificates and data export! 🎓*
"""
    await context.send_activity(MessageFactory.text(help_text))
```

---

## **Step 4: Test Complete System (15 minutes)**

### 4.1 Test Course Completion Flow in Codespace
```bash
# Restart the bot to load new features
# Stop current bot (Ctrl+C in terminal)
# Then restart:
python src/app.py
```

### 4.2 Verify Codespace Setup
1. **Check** port 3978 is forwarded and public
2. **Confirm** all completion/export files saved
3. **Test** endpoint accessibility

### 4.3 Test in Teams
1. **Test** completion commands:
```
/completion
/certificate
/export json
```

2. **Complete course requirements** (if not already done):
```
/quiz
# Answer multiple questions correctly across different topics
/completion
# Check progress towards completion
```

4. **Test export functionality**:
```
/export json
/export csv
/export zip
```

### 4.4 Verify File Creation in Codespace
```bash
# Check export files are created in Codespace
ls playground/data/exports/
ls playground/data/certificates/

# View an export file
cat playground/data/exports/user_data_*.json
```

---

## **✅ Day 6 Checklist**

Verify all these work:

- [ ] Created `src/sandbox_course_manager.py` with completion tracking
- [ ] Created `src/sandbox_export_manager.py` with data export
- [ ] Updated `src/bot.py` with completion and export commands
- [ ] `/completion` command shows course progress accurately
- [ ] `/certificate` command generates certificates for completed courses
- [ ] `/export` command creates data exports in multiple formats
- [ ] Course completion requirements are enforced properly
- [ ] Certificates include all required information
- [ ] Export files contain comprehensive user data
- [ ] Files are saved in appropriate directories
- [ ] Grade calculation works based on accuracy
- [ ] Data export includes analytics, achievements, and certificates

---

## **🚀 What's Next?**

**Day 7**: We'll prepare for production migration, add deployment guides, and create the final production-ready features.

---

## **💡 Troubleshooting**

### Common Issues:

**Course not completing:**
- Check accuracy meets minimum requirements (75%+)
- Verify sufficient questions answered per topic
- Ensure all topics have been attempted
- Check mastery level calculations

**Certificate generation failing:**
- Confirm course completion status first
- Check file permissions in certificates directory
- Verify all required data is available
- Look for errors in logs

**Export not working:**
- Check file permissions in exports directory
- Verify user has data to export
- Monitor disk space for large exports
- Check for JSON serialization errors

**File storage issues:**
- Ensure all directories exist and are writable
- Monitor disk space usage
- Check for file corruption
- Verify backup strategies

---

**🎉 Success!** Your AI learning bot now features complete course management with certificates and comprehensive data export capabilities!