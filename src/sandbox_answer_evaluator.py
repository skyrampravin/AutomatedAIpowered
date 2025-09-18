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