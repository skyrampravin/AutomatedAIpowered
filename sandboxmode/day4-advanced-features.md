# Day 4: Advanced Features & Analytics (Codespaces)

## 🎯 **Goal**: Implement adaptive difficulty, topic tracking, and comprehensive learning analytics

**Time Required**: 75-90 minutes  
**Prerequisites**: Day 1-3 completed (Codespace with AI features)  
**Outcome**: Advanced learning platform with personalized paths and detailed analytics in cloud

---

## **Step 1: Enhanced Learning Analytics (25 minutes)**

### 1.1 Advanced Analytics Engine
1. **Create**: `src/sandbox_learning_analytics.py`

```python
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics

from config import Config
from sandbox_storage import SandboxStorage, UserProfile
from sandbox_question_generator import QuizQuestion, QuizResult

@dataclass
class TopicPerformance:
    topic: str
    total_questions: int
    correct_answers: int
    accuracy: float
    average_time: float
    difficulty_distribution: Dict[str, int]
    last_attempted: str
    mastery_level: str  # "learning", "progressing", "proficient", "mastered"

@dataclass
class LearningPath:
    user_id: str
    current_topics: List[str]
    completed_topics: List[str]
    struggling_topics: List[str]
    recommended_next: List[str]
    estimated_completion_days: int
    confidence_score: float

@dataclass
class PerformanceTrend:
    period: str  # "daily", "weekly", "monthly"
    accuracy_trend: List[float]
    speed_trend: List[float]
    difficulty_trend: List[str]
    topic_focus: List[str]
    prediction: str  # "improving", "stable", "declining"

class SandboxLearningAnalytics:
    """Advanced learning analytics and adaptive learning engine"""
    
    def __init__(self, config: Config, storage: SandboxStorage):
        self.config = config
        self.storage = storage
        self.logger = logging.getLogger(__name__)
        
        # Mastery thresholds
        self.mastery_thresholds = {
            "learning": 0.5,      # 50% accuracy
            "progressing": 0.7,   # 70% accuracy
            "proficient": 0.85,   # 85% accuracy
            "mastered": 0.95      # 95% accuracy
        }
        
        # Minimum questions for reliable analytics
        self.min_questions_for_analytics = 3
    
    def analyze_user_performance(self, user_id: str) -> Dict[str, Any]:
        """Comprehensive analysis of user's learning performance"""
        try:
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                return {"error": "User profile not found"}
            
            quiz_history = self.storage.get_user_quiz_history(user_id)
            
            # Topic-wise performance analysis
            topic_performance = self._analyze_topic_performance(quiz_history)
            
            # Learning path recommendation
            learning_path = self._generate_learning_path(profile, topic_performance)
            
            # Performance trends
            performance_trend = self._analyze_performance_trends(quiz_history)
            
            # Adaptive difficulty recommendation
            recommended_difficulty = self._recommend_difficulty(profile, topic_performance)
            
            # Learning insights
            insights = self._generate_advanced_insights(profile, topic_performance, performance_trend)
            
            analysis = {
                "user_id": user_id,
                "analysis_date": datetime.now().isoformat(),
                "overall_performance": {
                    "total_questions": profile.total_questions,
                    "accuracy": profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0,
                    "current_streak": profile.current_streak,
                    "best_streak": profile.longest_streak,
                    "learning_days": self._calculate_learning_days(profile.start_date)
                },
                "topic_performance": topic_performance,
                "learning_path": asdict(learning_path),
                "performance_trend": asdict(performance_trend),
                "recommended_difficulty": recommended_difficulty,
                "insights": insights,
                "recommendations": self._generate_study_recommendations(profile, topic_performance)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing user performance for {user_id}: {e}")
            return {"error": str(e)}
    
    def _analyze_topic_performance(self, quiz_history: List[Dict[str, Any]]) -> Dict[str, TopicPerformance]:
        """Analyze performance by topic"""
        topic_stats = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "times": [],
            "difficulties": [],
            "dates": []
        })
        
        # Aggregate stats by topic
        for session in quiz_history:
            questions = session.get("questions", [])
            answers = session.get("answers", [])
            
            for i, question in enumerate(questions):
                topic = question.get("topic", "Unknown")
                difficulty = question.get("difficulty", "beginner")
                is_correct = i < len(answers) and answers[i] == question.get("correct_answer")
                
                topic_stats[topic]["total"] += 1
                if is_correct:
                    topic_stats[topic]["correct"] += 1
                
                topic_stats[topic]["difficulties"].append(difficulty)
                topic_stats[topic]["dates"].append(session.get("completed_date", ""))
                topic_stats[topic]["times"].append(session.get("time_taken", 60))
        
        # Convert to TopicPerformance objects
        topic_performance = {}
        for topic, stats in topic_stats.items():
            if stats["total"] > 0:
                accuracy = stats["correct"] / stats["total"]
                avg_time = statistics.mean(stats["times"]) if stats["times"] else 60
                
                # Determine mastery level
                mastery_level = "learning"
                for level, threshold in sorted(self.mastery_thresholds.items(), key=lambda x: x[1], reverse=True):
                    if accuracy >= threshold:
                        mastery_level = level
                        break
                
                topic_performance[topic] = TopicPerformance(
                    topic=topic,
                    total_questions=stats["total"],
                    correct_answers=stats["correct"],
                    accuracy=accuracy,
                    average_time=avg_time,
                    difficulty_distribution=dict(Counter(stats["difficulties"])),
                    last_attempted=max(stats["dates"]) if stats["dates"] else "",
                    mastery_level=mastery_level
                )
        
        return topic_performance
    
    def _generate_learning_path(self, profile: UserProfile, topic_performance: Dict[str, TopicPerformance]) -> LearningPath:
        """Generate personalized learning path"""
        try:
            # Get course curriculum
            from sandbox_question_generator import SandboxQuestionGenerator
            temp_generator = SandboxQuestionGenerator(self.config, self.storage)
            curricula = temp_generator.get_available_courses()
            
            if profile.enrolled_course not in curricula:
                return LearningPath(
                    user_id=profile.user_id,
                    current_topics=[],
                    completed_topics=[],
                    struggling_topics=[],
                    recommended_next=[],
                    estimated_completion_days=0,
                    confidence_score=0.0
                )
            
            course_topics = curricula[profile.enrolled_course]["topics"]
            
            # Categorize topics
            completed_topics = []
            struggling_topics = []
            current_topics = []
            
            for topic in course_topics:
                if topic in topic_performance:
                    perf = topic_performance[topic]
                    if perf.mastery_level in ["proficient", "mastered"]:
                        completed_topics.append(topic)
                    elif perf.accuracy < 0.6:
                        struggling_topics.append(topic)
                    else:
                        current_topics.append(topic)
                else:
                    # Not attempted yet
                    current_topics.append(topic)
            
            # Recommend next topics
            recommended_next = []
            if struggling_topics:
                # Prioritize struggling topics
                recommended_next.extend(struggling_topics[:2])
            
            if len(recommended_next) < 3:
                # Add new topics
                remaining_topics = [t for t in course_topics if t not in completed_topics and t not in struggling_topics]
                recommended_next.extend(remaining_topics[:3-len(recommended_next)])
            
            # Estimate completion time
            total_topics = len(course_topics)
            completed_count = len(completed_topics)
            remaining_count = total_topics - completed_count
            
            # Assume 2-3 days per topic based on current pace
            days_per_topic = 3 if profile.total_questions < 10 else 2
            estimated_days = remaining_count * days_per_topic
            
            # Calculate confidence score
            overall_accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
            topic_mastery_score = len(completed_topics) / total_topics if total_topics > 0 else 0
            confidence_score = (overall_accuracy + topic_mastery_score) / 2
            
            return LearningPath(
                user_id=profile.user_id,
                current_topics=current_topics,
                completed_topics=completed_topics,
                struggling_topics=struggling_topics,
                recommended_next=recommended_next,
                estimated_completion_days=estimated_days,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Error generating learning path: {e}")
            return LearningPath(
                user_id=profile.user_id,
                current_topics=[],
                completed_topics=[],
                struggling_topics=[],
                recommended_next=[],
                estimated_completion_days=0,
                confidence_score=0.0
            )
    
    def _analyze_performance_trends(self, quiz_history: List[Dict[str, Any]]) -> PerformanceTrend:
        """Analyze performance trends over time"""
        try:
            if len(quiz_history) < 3:
                return PerformanceTrend(
                    period="insufficient_data",
                    accuracy_trend=[],
                    speed_trend=[],
                    difficulty_trend=[],
                    topic_focus=[],
                    prediction="insufficient_data"
                )
            
            # Sort by date
            sorted_history = sorted(quiz_history, key=lambda x: x.get("completed_date", ""))
            
            # Calculate trends
            accuracy_trend = []
            speed_trend = []
            difficulty_trend = []
            topic_focus = []
            
            for session in sorted_history[-10:]:  # Last 10 sessions
                # Calculate session accuracy
                questions = session.get("questions", [])
                answers = session.get("answers", [])
                correct_count = sum(1 for i, q in enumerate(questions) 
                                 if i < len(answers) and answers[i] == q.get("correct_answer"))
                session_accuracy = correct_count / len(questions) if questions else 0
                accuracy_trend.append(session_accuracy)
                
                # Average speed
                avg_speed = session.get("time_taken", 60) / len(questions) if questions else 60
                speed_trend.append(avg_speed)
                
                # Most common difficulty
                difficulties = [q.get("difficulty", "beginner") for q in questions]
                if difficulties:
                    difficulty_trend.append(Counter(difficulties).most_common(1)[0][0])
                
                # Topics covered
                topics = [q.get("topic", "Unknown") for q in questions]
                topic_focus.extend(topics)
            
            # Predict trend
            prediction = "stable"
            if len(accuracy_trend) >= 3:
                recent_avg = statistics.mean(accuracy_trend[-3:])
                earlier_avg = statistics.mean(accuracy_trend[:-3]) if len(accuracy_trend) > 3 else accuracy_trend[0]
                
                if recent_avg > earlier_avg + 0.1:
                    prediction = "improving"
                elif recent_avg < earlier_avg - 0.1:
                    prediction = "declining"
            
            return PerformanceTrend(
                period="recent_sessions",
                accuracy_trend=accuracy_trend,
                speed_trend=speed_trend,
                difficulty_trend=difficulty_trend,
                topic_focus=list(Counter(topic_focus).keys())[:5],
                prediction=prediction
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance trends: {e}")
            return PerformanceTrend(
                period="error",
                accuracy_trend=[],
                speed_trend=[],
                difficulty_trend=[],
                topic_focus=[],
                prediction="error"
            )
    
    def _recommend_difficulty(self, profile: UserProfile, topic_performance: Dict[str, TopicPerformance]) -> str:
        """Recommend appropriate difficulty level"""
        try:
            if profile.total_questions < self.min_questions_for_analytics:
                return "beginner"
            
            overall_accuracy = profile.correct_answers / profile.total_questions
            
            # Consider recent performance
            if topic_performance:
                recent_accuracies = [perf.accuracy for perf in topic_performance.values() 
                                   if perf.total_questions >= 2]
                if recent_accuracies:
                    avg_recent_accuracy = statistics.mean(recent_accuracies)
                    overall_accuracy = (overall_accuracy + avg_recent_accuracy) / 2
            
            # Recommend based on accuracy and streak
            if overall_accuracy >= 0.9 and profile.current_streak >= 5:
                return "advanced"
            elif overall_accuracy >= 0.75 and profile.current_streak >= 3:
                return "intermediate"
            elif overall_accuracy >= 0.6:
                return "intermediate" if profile.total_questions >= 10 else "beginner"
            else:
                return "beginner"
                
        except Exception as e:
            self.logger.error(f"Error recommending difficulty: {e}")
            return "beginner"
    
    def _generate_advanced_insights(self, profile: UserProfile, topic_performance: Dict[str, TopicPerformance], 
                                  trend: PerformanceTrend) -> List[Dict[str, Any]]:
        """Generate advanced learning insights"""
        insights = []
        
        try:
            # Performance trend insight
            if trend.prediction == "improving":
                insights.append({
                    "type": "positive_trend",
                    "title": "📈 Performance Improving!",
                    "message": "Your accuracy has been consistently improving over recent sessions.",
                    "confidence": 0.9
                })
            elif trend.prediction == "declining":
                insights.append({
                    "type": "concern",
                    "title": "📉 Performance Declining", 
                    "message": "Your recent accuracy has decreased. Consider reviewing fundamentals.",
                    "confidence": 0.8
                })
            
            # Mastery insights
            mastered_topics = [topic for topic, perf in topic_performance.items() 
                             if perf.mastery_level == "mastered"]
            if mastered_topics:
                insights.append({
                    "type": "achievement",
                    "title": f"🏆 {len(mastered_topics)} Topic(s) Mastered!",
                    "message": f"You've achieved mastery in: {', '.join(mastered_topics)}",
                    "confidence": 1.0
                })
            
            # Struggling areas
            struggling_topics = [topic for topic, perf in topic_performance.items() 
                               if perf.accuracy < 0.5 and perf.total_questions >= 3]
            if struggling_topics:
                insights.append({
                    "type": "improvement_area",
                    "title": "💪 Focus Areas Identified",
                    "message": f"Consider additional practice in: {', '.join(struggling_topics)}",
                    "confidence": 0.8
                })
            
            # Speed insights
            if trend.speed_trend and len(trend.speed_trend) >= 3:
                avg_speed = statistics.mean(trend.speed_trend)
                if avg_speed < 30:
                    insights.append({
                        "type": "speed",
                        "title": "⚡ Quick Learner!",
                        "message": "You're answering questions quickly while maintaining accuracy.",
                        "confidence": 0.7
                    })
                elif avg_speed > 120:
                    insights.append({
                        "type": "speed",
                        "title": "🤔 Take Your Time",
                        "message": "Consider slowing down to think through questions more carefully.",
                        "confidence": 0.6
                    })
            
            # Consistency insights
            if profile.current_streak >= 10:
                insights.append({
                    "type": "consistency",
                    "title": f"🔥 Amazing Streak!",
                    "message": f"You're on a {profile.current_streak}-question winning streak!",
                    "confidence": 1.0
                })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating advanced insights: {e}")
            return []
    
    def _generate_study_recommendations(self, profile: UserProfile, topic_performance: Dict[str, TopicPerformance]) -> List[str]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        try:
            overall_accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
            
            # Basic recommendations
            if profile.total_questions < 5:
                recommendations.append("Complete more quiz questions to unlock detailed analytics")
            
            # Performance-based recommendations
            if overall_accuracy < 0.6:
                recommendations.append("Focus on understanding fundamental concepts before advancing")
                recommendations.append("Review explanations carefully after each question")
            elif overall_accuracy > 0.85:
                recommendations.append("You're ready for more challenging questions!")
                recommendations.append("Consider exploring advanced topics in your course")
            
            # Topic-specific recommendations
            if topic_performance:
                struggling_topics = [topic for topic, perf in topic_performance.items() 
                                   if perf.accuracy < 0.6 and perf.total_questions >= 2]
                if struggling_topics:
                    recommendations.append(f"Dedicate extra time to: {', '.join(struggling_topics[:2])}")
                
                mastered_topics = [topic for topic, perf in topic_performance.items() 
                                 if perf.mastery_level == "mastered"]
                if len(mastered_topics) >= 3:
                    recommendations.append("Consider advancing to a more challenging course")
            
            # Streak-based recommendations
            if profile.current_streak == 0 and profile.total_questions >= 5:
                recommendations.append("Don't give up! Every expert was once a beginner")
                recommendations.append("Take a short break and return with fresh focus")
            elif profile.current_streak >= 5:
                recommendations.append("Keep the momentum going with regular practice")
            
            # Learning schedule recommendations
            learning_days = self._calculate_learning_days(profile.start_date)
            if learning_days > 7 and profile.total_questions < 10:
                recommendations.append("Try to increase your practice frequency for better retention")
            elif profile.total_questions > 50:
                recommendations.append("Excellent dedication! Consider teaching others to reinforce your knowledge")
            
            # Default recommendation
            if not recommendations:
                recommendations.append("Continue regular practice to maintain and improve your skills")
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating study recommendations: {e}")
            return ["Continue practicing regularly to improve your skills"]
    
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
    
    def get_course_analytics(self, course: str) -> Dict[str, Any]:
        """Get aggregated analytics for a course"""
        try:
            # Get all users enrolled in the course
            stats = self.storage.get_storage_stats()
            
            # This would need to be implemented with proper user enumeration
            # For sandbox mode, return basic course info
            
            from sandbox_question_generator import SandboxQuestionGenerator
            temp_generator = SandboxQuestionGenerator(self.config, self.storage)
            curricula = temp_generator.get_available_courses()
            
            if course not in curricula:
                return {"error": "Course not found"}
            
            course_info = curricula[course]
            
            return {
                "course": course,
                "description": course_info["description"],
                "total_topics": len(course_info["topics"]),
                "topics": course_info["topics"],
                "difficulty_levels": course_info["difficulty_levels"],
                "enrolled_users": "Not available in sandbox mode",
                "completion_rate": "Not available in sandbox mode",
                "average_performance": "Not available in sandbox mode"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting course analytics for {course}: {e}")
            return {"error": str(e)}
```

### 1.2 Test Analytics Engine in Codespace
```bash
# Test the analytics system in Codespace terminal
python -c "
import asyncio
from src.config import Config
from src.sandbox_storage import SandboxStorage
from src.sandbox_learning_analytics import SandboxLearningAnalytics

config = Config()
storage = SandboxStorage(config.DATA_DIRECTORY)
analytics = SandboxLearningAnalytics(config, storage)

# Test course analytics
course_stats = analytics.get_course_analytics('python-basics')
print('Course Analytics:')
print(f'  Topics: {len(course_stats.get(\"topics\", []))}')
print('✅ Analytics engine working!')
"
```

---

## **Step 2: Adaptive Difficulty System (20 minutes)**

### 2.1 Enhanced Question Generator with Adaptive Difficulty
1. **Update** `src/sandbox_question_generator.py` to add adaptive difficulty:

```python
# Add this method to the SandboxQuestionGenerator class

def determine_adaptive_difficulty(self, user_id: str, topic: str) -> str:
    """Determine adaptive difficulty based on user's performance in specific topic"""
    try:
        profile = self.storage.get_user_profile(user_id)
        if not profile or profile.total_questions < 3:
            return "beginner"
        
        quiz_history = self.storage.get_user_quiz_history(user_id)
        
        # Analyze topic-specific performance
        topic_correct = 0
        topic_total = 0
        recent_topic_correct = 0
        recent_topic_total = 0
        
        for session in quiz_history:
            questions = session.get("questions", [])
            answers = session.get("answers", [])
            
            for i, question in enumerate(questions):
                if question.get("topic") == topic:
                    topic_total += 1
                    if i < len(answers) and answers[i] == question.get("correct_answer"):
                        topic_correct += 1
                    
                    # Count recent performance (last 5 sessions)
                    if len(quiz_history) - quiz_history.index(session) <= 5:
                        recent_topic_total += 1
                        if i < len(answers) and answers[i] == question.get("correct_answer"):
                            recent_topic_correct += 1
        
        # Calculate topic accuracy
        topic_accuracy = topic_correct / topic_total if topic_total > 0 else 0
        recent_accuracy = recent_topic_correct / recent_topic_total if recent_topic_total > 0 else topic_accuracy
        
        # Weight recent performance more heavily
        weighted_accuracy = (recent_accuracy * 0.7) + (topic_accuracy * 0.3)
        
        # Consider overall performance and streak
        overall_accuracy = profile.correct_answers / profile.total_questions
        streak_bonus = min(profile.current_streak * 0.05, 0.3)  # Max 30% bonus for streak
        
        final_score = (weighted_accuracy * 0.8) + (overall_accuracy * 0.2) + streak_bonus
        
        # Determine difficulty with hysteresis to prevent oscillation
        if final_score >= 0.9 and profile.current_streak >= 3:
            return "advanced"
        elif final_score >= 0.75 and topic_total >= 3:
            return "intermediate"
        elif final_score >= 0.6:
            return "intermediate" if topic_total >= 5 else "beginner"
        else:
            return "beginner"
            
    except Exception as e:
        self.logger.error(f"Error determining adaptive difficulty: {e}")
        return "beginner"

async def generate_adaptive_question(self, user_id: str, preferred_topic: str = None) -> Optional[QuizQuestion]:
    """Generate question with adaptive difficulty and smart topic selection"""
    try:
        profile = self.storage.get_user_profile(user_id)
        if not profile or not profile.enrolled_course:
            return None
        
        course = profile.enrolled_course
        if course not in self.course_curricula:
            return None
        
        # Smart topic selection
        if preferred_topic and preferred_topic in self.course_curricula[course]["topics"]:
            topic = preferred_topic
        else:
            topic = self._select_adaptive_topic(user_id, course)
        
        # Adaptive difficulty
        difficulty = self.determine_adaptive_difficulty(user_id, topic)
        
        self.logger.info(f"Generating adaptive question for user {user_id}: topic={topic}, difficulty={difficulty}")
        
        # Generate question with adaptive parameters
        question = await self._generate_ai_question(course, topic, difficulty)
        
        if question:
            # Add adaptive metadata
            question.question_id += f"_adaptive_{difficulty}"
        
        return question
        
    except Exception as e:
        self.logger.error(f"Error generating adaptive question: {e}")
        return None

def _select_adaptive_topic(self, user_id: str, course: str) -> str:
    """Intelligently select topic based on user's learning progress"""
    try:
        quiz_history = self.storage.get_user_quiz_history(user_id)
        available_topics = self.course_curricula[course]["topics"]
        
        # Analyze topic performance
        topic_performance = {}
        
        for session in quiz_history:
            questions = session.get("questions", [])
            answers = session.get("answers", [])
            
            for i, question in enumerate(questions):
                topic = question.get("topic", "Unknown")
                if topic in available_topics:
                    if topic not in topic_performance:
                        topic_performance[topic] = {"correct": 0, "total": 0, "last_seen": ""}
                    
                    topic_performance[topic]["total"] += 1
                    if i < len(answers) and answers[i] == question.get("correct_answer"):
                        topic_performance[topic]["correct"] += 1
                    topic_performance[topic]["last_seen"] = session.get("completed_date", "")
        
        # Topic selection strategy
        struggling_topics = []
        mastered_topics = []
        untouched_topics = []
        
        for topic in available_topics:
            if topic in topic_performance:
                accuracy = topic_performance[topic]["correct"] / topic_performance[topic]["total"]
                if accuracy < 0.6 and topic_performance[topic]["total"] >= 2:
                    struggling_topics.append(topic)
                elif accuracy >= 0.9 and topic_performance[topic]["total"] >= 3:
                    mastered_topics.append(topic)
            else:
                untouched_topics.append(topic)
        
        # Selection priority:
        # 1. Struggling topics (need reinforcement)
        # 2. New topics (progression)
        # 3. Random from practiced topics (maintenance)
        
        if struggling_topics:
            return random.choice(struggling_topics)
        elif untouched_topics:
            return untouched_topics[0]  # Sequential progression
        else:
            # Select from non-mastered topics
            non_mastered = [t for t in available_topics if t not in mastered_topics]
            return random.choice(non_mastered) if non_mastered else random.choice(available_topics)
            
    except Exception as e:
        self.logger.error(f"Error selecting adaptive topic: {e}")
        return random.choice(self.course_curricula[course]["topics"])

# Update the existing generate_personalized_question method to use adaptive logic
async def generate_personalized_question(self, user_id: str) -> Optional[QuizQuestion]:
    """Generate a personalized question based on user's progress (now with adaptive features)"""
    return await self.generate_adaptive_question(user_id)
```

---

## **Step 3: Enhanced Bot Commands (20 minutes)**

### 3.1 Add Advanced Bot Commands
1. **Update** `src/bot.py` to add new analytics commands:

```python
# Add these imports at the top
from sandbox_learning_analytics import SandboxLearningAnalytics

# Add after answer_evaluator initialization
learning_analytics = SandboxLearningAnalytics(config, storage)

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

async def handle_analytics_command(context: TurnContext, user_id: str):
    """Show detailed learning analytics"""
    try:
        analysis = learning_analytics.analyze_user_performance(user_id)
        
        if "error" in analysis:
            await context.send_activity(MessageFactory.text(
                f"❌ {analysis['error']}\n\nMake sure you're enrolled in a course and have answered some questions."
            ))
            return
        
        overall = analysis["overall_performance"]
        learning_path = analysis["learning_path"]
        insights = analysis["insights"]
        
        analytics_text = f"""
📊 **Detailed Learning Analytics**

📈 **Overall Performance**:
• Questions Answered: {overall["total_questions"]}
• Accuracy: {overall["accuracy"]:.1%}
• Current Streak: {overall["current_streak"]}
• Best Streak: {overall["best_streak"]}
• Learning Days: {overall["learning_days"]}

🎯 **Learning Progress**:
• Topics Completed: {len(learning_path["completed_topics"])}
• Topics In Progress: {len(learning_path["current_topics"])}
• Areas Needing Focus: {len(learning_path["struggling_topics"])}
• Confidence Score: {learning_path["confidence_score"]:.1%}
• Est. Completion: {learning_path["estimated_completion_days"]} days

🧠 **Key Insights**:
"""
        
        for insight in insights[:3]:  # Show top 3 insights
            analytics_text += f"• {insight['title']}\n"
        
        if not insights:
            analytics_text += "• Complete more questions to unlock detailed insights\n"
        
        analytics_text += f"\n📚 **Recommended Difficulty**: {analysis['recommended_difficulty'].title()}"
        
        await context.send_activity(MessageFactory.text(analytics_text))
        
    except Exception as e:
        logger.error(f"Error handling analytics command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error generating analytics. Please try again."
        ))

async def handle_progress_command(context: TurnContext, user_id: str):
    """Show learning progress by topic"""
    try:
        analysis = learning_analytics.analyze_user_performance(user_id)
        
        if "error" in analysis:
            await context.send_activity(MessageFactory.text(
                "❌ No progress data available. Start taking quizzes to track your progress!"
            ))
            return
        
        topic_performance = analysis["topic_performance"]
        
        if not topic_performance:
            await context.send_activity(MessageFactory.text(
                "📚 **No topic progress yet!**\n\n"
                "Take some quizzes to see your progress by topic.\n"
                "Use `/quiz` to get started!"
            ))
            return
        
        progress_text = "📚 **Progress by Topic**\n\n"
        
        # Sort topics by mastery level and accuracy
        mastery_order = {"mastered": 4, "proficient": 3, "progressing": 2, "learning": 1}
        sorted_topics = sorted(topic_performance.items(), 
                             key=lambda x: (mastery_order.get(x[1].mastery_level, 0), x[1].accuracy),
                             reverse=True)
        
        for topic, perf in sorted_topics:
            mastery_emoji = {
                "mastered": "🏆",
                "proficient": "🌟", 
                "progressing": "📈",
                "learning": "🌱"
            }
            
            progress_text += f"{mastery_emoji.get(perf.mastery_level, '📚')} **{topic}**\n"
            progress_text += f"   Accuracy: {perf.accuracy:.1%} ({perf.correct_answers}/{perf.total_questions})\n"
            progress_text += f"   Level: {perf.mastery_level.title()}\n"
            progress_text += f"   Avg Time: {perf.average_time:.0f}s\n\n"
        
        await context.send_activity(MessageFactory.text(progress_text))
        
    except Exception as e:
        logger.error(f"Error handling progress command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error loading progress data. Please try again."
        ))

async def handle_topics_command(context: TurnContext, user_id: str):
    """Show available topics and recommendations"""
    try:
        profile = storage.get_user_profile(user_id)
        if not profile or not profile.enrolled_course:
            await context.send_activity(MessageFactory.text(
                "❌ Please enroll in a course first to see available topics."
            ))
            return
        
        analysis = learning_analytics.analyze_user_performance(user_id)
        
        # Get course curriculum
        curricula = question_generator.get_available_courses()
        course_topics = curricula[profile.enrolled_course]["topics"]
        
        topics_text = f"📚 **Topics in {profile.enrolled_course.replace('-', ' ').title()}**\n\n"
        
        if "error" not in analysis and analysis.get("learning_path"):
            learning_path = analysis["learning_path"]
            
            # Show completed topics
            if learning_path["completed_topics"]:
                topics_text += "✅ **Completed Topics**:\n"
                for topic in learning_path["completed_topics"]:
                    topics_text += f"   • {topic}\n"
                topics_text += "\n"
            
            # Show current focus
            if learning_path["struggling_topics"]:
                topics_text += "🎯 **Need Extra Practice**:\n"
                for topic in learning_path["struggling_topics"]:
                    topics_text += f"   • {topic}\n"
                topics_text += "\n"
            
            # Show recommendations
            if learning_path["recommended_next"]:
                topics_text += "🚀 **Recommended Next**:\n"
                for topic in learning_path["recommended_next"][:3]:
                    topics_text += f"   • {topic}\n"
                topics_text += "\n"
        
        # Show all available topics
        topics_text += "📖 **All Available Topics**:\n"
        for i, topic in enumerate(course_topics, 1):
            topics_text += f"   {i}. {topic}\n"
        
        topics_text += "\n💡 Use `/quiz` to practice any of these topics!"
        
        await context.send_activity(MessageFactory.text(topics_text))
        
    except Exception as e:
        logger.error(f"Error handling topics command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error loading topics. Please try again."
        ))

async def handle_study_command(context: TurnContext, user_id: str):
    """Show personalized study recommendations"""
    try:
        analysis = learning_analytics.analyze_user_performance(user_id)
        
        if "error" in analysis:
            await context.send_activity(MessageFactory.text(
                "📚 **Study Recommendations**\n\n"
                "• Start by enrolling in a course\n"
                "• Take your first quiz questions\n"
                "• Return here for personalized recommendations!\n\n"
                "Use `/enroll [course-name]` to begin."
            ))
            return
        
        recommendations = analysis["recommendations"]
        insights = analysis["insights"]
        
        study_text = "📚 **Personalized Study Plan**\n\n"
        
        # Show key insights
        if insights:
            study_text += "🧠 **Key Insights**:\n"
            for insight in insights[:2]:
                study_text += f"• {insight['message']}\n"
            study_text += "\n"
        
        # Show recommendations
        study_text += "🎯 **Study Recommendations**:\n"
        for i, rec in enumerate(recommendations[:5], 1):
            study_text += f"{i}. {rec}\n"
        
        # Add performance summary
        overall = analysis["overall_performance"]
        study_text += f"\n📊 **Current Performance**:\n"
        study_text += f"• Accuracy: {overall['accuracy']:.1%}\n"
        study_text += f"• Streak: {overall['current_streak']} questions\n"
        study_text += f"• Learning for: {overall['learning_days']} days\n"
        
        study_text += "\n🚀 Ready to continue? Use `/quiz` for your next question!"
        
        await context.send_activity(MessageFactory.text(study_text))
        
    except Exception as e:
        logger.error(f"Error handling study command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error generating study recommendations. Please try again."
        ))

# Update the help command to include new features
async def handle_help_command(context: TurnContext):
    """Show help information"""
    help_text = """
🤖 **AI Learning Bot - Advanced Features** 🤖

**📚 Learning Commands:**
• `/quiz` - Start adaptive quiz (adjusts to your level!)
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

**✨ New Features:**
• **Adaptive Difficulty**: Questions adjust to your skill level
• **Topic Mastery**: Track mastery across different topics
• **Learning Analytics**: Detailed insights into your progress
• **Smart Recommendations**: Personalized study suggestions

**Quick Start:**
```
/enroll python-basics
/quiz
/analytics
```

*🧠 Day 4: Advanced learning features with AI-powered adaptation! 🧠*
"""
    await context.send_activity(MessageFactory.text(help_text))
```

---

## **Step 4: Test Advanced Features (10 minutes)**

### 4.1 Test Complete Advanced Flow in Codespace
```bash
# Restart the bot to load new features
# Stop current bot (Ctrl+C in terminal)
# Then restart:
python src/app.py
```

### 4.2 Verify Codespace Status
1. **Check** port 3978 is forwarded and public
2. **Confirm** all files saved in Codespace
3. **Test** endpoint accessibility

### 4.3 Test in Teams
1. **Test** new analytics commands:
```
/analytics
/progress  
/topics
/study
```

2. **Take several quizzes** to generate data:
```
/quiz
# Answer with A, B, C, or D
/quiz
# Answer again
/quiz
# Answer again
```

3. **Check analytics** after multiple quizzes:
```
/analytics
/progress
```

### 4.3 Verify Adaptive Behavior
- Take multiple quizzes and verify difficulty adapts
- Check that struggling topics are prioritized
- Confirm insights and recommendations update

---

## **✅ Day 4 Checklist**

Verify all these work:

- [ ] Created `src/sandbox_learning_analytics.py` with comprehensive analytics
- [ ] Updated `src/sandbox_question_generator.py` with adaptive difficulty
- [ ] Enhanced `src/bot.py` with new analytics commands
- [ ] `/analytics` command shows detailed performance data
- [ ] `/progress` command displays topic-wise mastery levels
- [ ] `/topics` command shows course topics and recommendations
- [ ] `/study` command provides personalized study plan
- [ ] Adaptive difficulty adjusts based on performance
- [ ] Topic selection prioritizes struggling areas
- [ ] Learning insights generate automatically
- [ ] Performance trends are calculated correctly
- [ ] File storage maintains all analytics data

---

## **🚀 What's Next?**

**Day 5**: We'll add course completion certificates, achievement badges, and advanced learning pathways - all running smoothly in your GitHub Codespace.

---

## **💡 Troubleshooting**

### Common Issues:

**Analytics not showing:**
- Complete at least 3-5 quiz questions first
- Check that quiz sessions are saving properly in Codespace
- Verify file storage has quiz history in `playground/data/`

**Adaptive difficulty not working:**
- Ensure multiple quiz sessions completed
- Check topic performance calculations
- Verify difficulty determination logic in cloud environment

**Codespace performance issues:**
- Monitor Codespace resource usage
- Check terminal for errors or warnings
- Restart Codespace if sluggish performance

**File storage issues in Codespace:**
- Verify playground directories exist and are writable
- Check Codespace disk space usage
- Ensure proper file permissions in cloud environment

**Recommendations not accurate:**
- Verify sufficient data for analysis
- Check topic performance thresholds
- Allow more quiz sessions for better algorithm training

### Codespace-Specific Debug:
```bash
# Check file storage
du -sh playground/data/

# Monitor running processes
ps aux | grep python

# Check system resources
df -h
```
- Review learning path generation logic

---

**🎉 Success!** Your AI learning bot now features advanced analytics, adaptive difficulty, and personalized learning recommendations!