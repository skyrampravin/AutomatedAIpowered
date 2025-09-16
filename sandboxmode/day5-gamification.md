# Day 5: Achievements & Gamification with Bot Framework Emulator

## 🎯 **Goal**: Implement achievement badges, course completion certificates, and gamification features testable in Bot Framework Emulator

**Time Required**: 80-95 minutes  
**Prerequisites**: Day 1-4 completed (Codespace with analytics, Bot Framework Emulator connected)  
**Outcome**: Engaging gamified learning platform with achievements and rewards - fully testable locally

---

## **Step 1: Achievement System (30 minutes)**

### 1.1 Create Achievement Engine
1. **Create**: `src/sandbox_achievements.py`

```python
import os
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from config import Config
from sandbox_storage import SandboxStorage, UserProfile
from sandbox_learning_analytics import SandboxLearningAnalytics

class AchievementType(Enum):
    STREAK = "streak"
    ACCURACY = "accuracy"
    SPEED = "speed"
    VOLUME = "volume"
    CONSISTENCY = "consistency"
    MASTERY = "mastery"
    MILESTONE = "milestone"
    SPECIAL = "special"

class AchievementRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    emoji: str
    type: AchievementType
    rarity: AchievementRarity
    criteria: Dict[str, Any]
    points: int
    unlocked_message: str
    
@dataclass
class UserAchievement:
    achievement_id: str
    user_id: str
    unlocked_date: str
    progress_when_unlocked: Dict[str, Any]

@dataclass
class Badge:
    id: str
    name: str
    description: str
    emoji: str
    requirements: List[str]  # List of achievement IDs required
    tier: str  # "bronze", "silver", "gold", "platinum"

@dataclass
class Certificate:
    id: str
    user_id: str
    course: str
    completion_date: str
    final_accuracy: float
    total_questions: int
    time_spent_days: int
    achievements_earned: int
    certificate_url: str  # In production, would be actual URL

class SandboxAchievementSystem:
    """Gamification and achievement system for learning platform"""
    
    def __init__(self, config: Config, storage: SandboxStorage, analytics: SandboxLearningAnalytics):
        self.config = config
        self.storage = storage
        self.analytics = analytics
        self.logger = logging.getLogger(__name__)
        
        # Initialize achievements database
        self.achievements = self._initialize_achievements()
        self.badges = self._initialize_badges()
        
        # Create achievement storage directory
        self.achievement_dir = f"{config.DATA_DIRECTORY}/achievements"
        os.makedirs(self.achievement_dir, exist_ok=True)
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize the complete achievement system"""
        achievements = {}
        
        # 🔥 STREAK ACHIEVEMENTS
        achievements["first_streak"] = Achievement(
            id="first_streak",
            name="Getting Started",
            description="Answer 3 questions correctly in a row",
            emoji="🔥",
            type=AchievementType.STREAK,
            rarity=AchievementRarity.COMMON,
            criteria={"streak": 3},
            points=10,
            unlocked_message="You're on fire! Keep the momentum going!"
        )
        
        achievements["streak_master"] = Achievement(
            id="streak_master",
            name="Streak Master",
            description="Answer 10 questions correctly in a row",
            emoji="🌟",
            type=AchievementType.STREAK,
            rarity=AchievementRarity.UNCOMMON,
            criteria={"streak": 10},
            points=50,
            unlocked_message="Incredible consistency! You're becoming unstoppable!"
        )
        
        achievements["unstoppable"] = Achievement(
            id="unstoppable",
            name="Unstoppable Force",
            description="Answer 25 questions correctly in a row",
            emoji="⚡",
            type=AchievementType.STREAK,
            rarity=AchievementRarity.RARE,
            criteria={"streak": 25},
            points=150,
            unlocked_message="Absolutely legendary streak! You're unstoppable!"
        )
        
        # 🎯 ACCURACY ACHIEVEMENTS
        achievements["perfectionist"] = Achievement(
            id="perfectionist",
            name="Perfectionist",
            description="Maintain 100% accuracy over 10 questions",
            emoji="🎯",
            type=AchievementType.ACCURACY,
            rarity=AchievementRarity.UNCOMMON,
            criteria={"accuracy": 1.0, "min_questions": 10},
            points=75,
            unlocked_message="Flawless execution! Your attention to detail is remarkable!"
        )
        
        achievements["expert_level"] = Achievement(
            id="expert_level",
            name="Expert Level",
            description="Achieve 90% accuracy over 50 questions",
            emoji="🏆",
            type=AchievementType.ACCURACY,
            rarity=AchievementRarity.RARE,
            criteria={"accuracy": 0.9, "min_questions": 50},
            points=200,
            unlocked_message="Expert-level mastery achieved! You're in the top tier!"
        )
        
        # ⚡ SPEED ACHIEVEMENTS
        achievements["quick_draw"] = Achievement(
            id="quick_draw",
            name="Quick Draw",
            description="Answer 5 questions in under 30 seconds each",
            emoji="⚡",
            type=AchievementType.SPEED,
            rarity=AchievementRarity.COMMON,
            criteria={"max_time": 30, "consecutive_count": 5},
            points=25,
            unlocked_message="Lightning fast! Your quick thinking is impressive!"
        )
        
        achievements["speed_demon"] = Achievement(
            id="speed_demon",
            name="Speed Demon",
            description="Answer 20 questions in under 20 seconds each",
            emoji="🚀",
            type=AchievementType.SPEED,
            rarity=AchievementRarity.RARE,
            criteria={"max_time": 20, "consecutive_count": 20},
            points=150,
            unlocked_message="Incredible speed! You're thinking at lightning pace!"
        )
        
        # 📚 VOLUME ACHIEVEMENTS
        achievements["dedicated_learner"] = Achievement(
            id="dedicated_learner",
            name="Dedicated Learner",
            description="Answer 100 questions total",
            emoji="📚",
            type=AchievementType.VOLUME,
            rarity=AchievementRarity.COMMON,
            criteria={"total_questions": 100},
            points=50,
            unlocked_message="Your dedication to learning is inspiring!"
        )
        
        achievements["knowledge_seeker"] = Achievement(
            id="knowledge_seeker",
            name="Knowledge Seeker",
            description="Answer 500 questions total",
            emoji="🧠",
            type=AchievementType.VOLUME,
            rarity=AchievementRarity.UNCOMMON,
            criteria={"total_questions": 500},
            points=150,
            unlocked_message="Your thirst for knowledge knows no bounds!"
        )
        
        achievements["learning_legend"] = Achievement(
            id="learning_legend",
            name="Learning Legend",
            description="Answer 1000 questions total",
            emoji="👑",
            type=AchievementType.VOLUME,
            rarity=AchievementRarity.LEGENDARY,
            criteria={"total_questions": 1000},
            points=500,
            unlocked_message="Legendary commitment to learning! You're an inspiration!"
        )
        
        # 📅 CONSISTENCY ACHIEVEMENTS
        achievements["daily_learner"] = Achievement(
            id="daily_learner",
            name="Daily Learner",
            description="Learn for 7 consecutive days",
            emoji="📅",
            type=AchievementType.CONSISTENCY,
            rarity=AchievementRarity.COMMON,
            criteria={"consecutive_days": 7},
            points=40,
            unlocked_message="Consistency is key! You're building great habits!"
        )
        
        achievements["commitment_champion"] = Achievement(
            id="commitment_champion",
            name="Commitment Champion",
            description="Learn for 30 consecutive days",
            emoji="🏅",
            type=AchievementType.CONSISTENCY,
            rarity=AchievementRarity.RARE,
            criteria={"consecutive_days": 30},
            points=250,
            unlocked_message="Your commitment is extraordinary! A true champion!"
        )
        
        # 🎓 MASTERY ACHIEVEMENTS
        achievements["topic_master"] = Achievement(
            id="topic_master",
            name="Topic Master",
            description="Achieve mastery in 3 different topics",
            emoji="🎓",
            type=AchievementType.MASTERY,
            rarity=AchievementRarity.UNCOMMON,
            criteria={"mastered_topics": 3},
            points=100,
            unlocked_message="True mastery across multiple areas! Exceptional!"
        )
        
        achievements["course_conqueror"] = Achievement(
            id="course_conqueror",
            name="Course Conqueror",
            description="Complete an entire course with 85% accuracy",
            emoji="🏆",
            type=AchievementType.MILESTONE,
            rarity=AchievementRarity.EPIC,
            criteria={"course_completion": True, "min_accuracy": 0.85},
            points=300,
            unlocked_message="Course conquered! Your mastery is undeniable!"
        )
        
        # 🌟 SPECIAL ACHIEVEMENTS
        achievements["comeback_kid"] = Achievement(
            id="comeback_kid",
            name="Comeback Kid",
            description="Improve accuracy by 30% over 20 questions",
            emoji="💪",
            type=AchievementType.SPECIAL,
            rarity=AchievementRarity.UNCOMMON,
            criteria={"accuracy_improvement": 0.3, "question_window": 20},
            points=75,
            unlocked_message="Incredible comeback! Never give up spirit!"
        )
        
        achievements["night_owl"] = Achievement(
            id="night_owl",
            name="Night Owl",
            description="Answer questions after 10 PM on 5 different days",
            emoji="🦉",
            type=AchievementType.SPECIAL,
            rarity=AchievementRarity.UNCOMMON,
            criteria={"late_night_sessions": 5},
            points=50,
            unlocked_message="Burning the midnight oil! Dedicated learner!"
        )
        
        achievements["early_bird"] = Achievement(
            id="early_bird",
            name="Early Bird",
            description="Answer questions before 7 AM on 5 different days",
            emoji="🐦",
            type=AchievementType.SPECIAL,
            rarity=AchievementRarity.UNCOMMON,
            criteria={"early_morning_sessions": 5},
            points=50,
            unlocked_message="Early bird catches the worm! Great discipline!"
        )
        
        return achievements
    
    def _initialize_badges(self) -> Dict[str, Badge]:
        """Initialize badge system"""
        badges = {}
        
        badges["bronze_learner"] = Badge(
            id="bronze_learner",
            name="Bronze Learner",
            description="Complete basic learning milestones",
            emoji="🥉",
            requirements=["first_streak", "dedicated_learner"],
            tier="bronze"
        )
        
        badges["silver_scholar"] = Badge(
            id="silver_scholar",
            name="Silver Scholar",
            description="Demonstrate consistent learning excellence",
            emoji="🥈",
            requirements=["streak_master", "perfectionist", "daily_learner"],
            tier="silver"
        )
        
        badges["gold_master"] = Badge(
            id="gold_master",
            name="Gold Master",
            description="Achieve high-level mastery and consistency",
            emoji="🥇",
            requirements=["expert_level", "topic_master", "commitment_champion"],
            tier="gold"
        )
        
        badges["platinum_legend"] = Badge(
            id="platinum_legend",
            name="Platinum Legend",
            description="Legendary learning achievement",
            emoji="💎",
            requirements=["learning_legend", "unstoppable", "course_conqueror"],
            tier="platinum"
        )
        
        return badges
    
    def check_achievements(self, user_id: str) -> List[UserAchievement]:
        """Check and unlock new achievements for user"""
        try:
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                return []
            
            # Get user's current achievements
            current_achievements = self.get_user_achievements(user_id)
            unlocked_ids = {ach.achievement_id for ach in current_achievements}
            
            new_achievements = []
            
            # Get comprehensive user analytics
            analysis = self.analytics.analyze_user_performance(user_id)
            if "error" in analysis:
                return []
            
            # Check each achievement
            for achievement_id, achievement in self.achievements.items():
                if achievement_id in unlocked_ids:
                    continue  # Already unlocked
                
                if self._check_achievement_criteria(achievement, profile, analysis):
                    # Unlock achievement
                    user_achievement = UserAchievement(
                        achievement_id=achievement_id,
                        user_id=user_id,
                        unlocked_date=datetime.now().isoformat(),
                        progress_when_unlocked={
                            "total_questions": profile.total_questions,
                            "accuracy": profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0,
                            "current_streak": profile.current_streak
                        }
                    )
                    
                    new_achievements.append(user_achievement)
                    self._save_user_achievement(user_achievement)
                    
                    self.logger.info(f"Achievement unlocked: {achievement.name} for user {user_id}")
            
            return new_achievements
            
        except Exception as e:
            self.logger.error(f"Error checking achievements for user {user_id}: {e}")
            return []
    
    def _check_achievement_criteria(self, achievement: Achievement, profile: UserProfile, analysis: Dict[str, Any]) -> bool:
        """Check if achievement criteria are met"""
        try:
            criteria = achievement.criteria
            
            if achievement.type == AchievementType.STREAK:
                return profile.current_streak >= criteria.get("streak", 0)
            
            elif achievement.type == AchievementType.ACCURACY:
                min_questions = criteria.get("min_questions", 1)
                target_accuracy = criteria.get("accuracy", 0)
                
                if profile.total_questions < min_questions:
                    return False
                
                current_accuracy = profile.correct_answers / profile.total_questions
                return current_accuracy >= target_accuracy
            
            elif achievement.type == AchievementType.VOLUME:
                return profile.total_questions >= criteria.get("total_questions", 0)
            
            elif achievement.type == AchievementType.MASTERY:
                if "mastered_topics" in criteria:
                    topic_performance = analysis.get("topic_performance", {})
                    mastered_count = sum(1 for perf in topic_performance.values() 
                                       if hasattr(perf, 'mastery_level') and perf.mastery_level == "mastered")
                    return mastered_count >= criteria["mastered_topics"]
            
            elif achievement.type == AchievementType.MILESTONE:
                if "course_completion" in criteria:
                    return (profile.completed_course and 
                           profile.correct_answers / profile.total_questions >= criteria.get("min_accuracy", 0))
            
            # Add more criteria checks as needed
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking criteria for achievement {achievement.id}: {e}")
            return False
    
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get all achievements for a user"""
        try:
            file_path = f"{self.achievement_dir}/{user_id}_achievements.json"
            if not os.path.exists(file_path):
                return []
            
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [UserAchievement(**item) for item in data]
                
        except Exception as e:
            self.logger.error(f"Error getting achievements for user {user_id}: {e}")
            return []
    
    def _save_user_achievement(self, user_achievement: UserAchievement):
        """Save new achievement for user"""
        try:
            file_path = f"{self.achievement_dir}/{user_achievement.user_id}_achievements.json"
            
            # Load existing achievements
            achievements = []
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    achievements = json.load(f)
            
            # Add new achievement
            achievements.append(asdict(user_achievement))
            
            # Save updated achievements
            with open(file_path, 'w') as f:
                json.dump(achievements, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving achievement: {e}")
    
    def get_user_badges(self, user_id: str) -> List[Badge]:
        """Get earned badges for user"""
        try:
            user_achievements = self.get_user_achievements(user_id)
            achievement_ids = {ach.achievement_id for ach in user_achievements}
            
            earned_badges = []
            for badge in self.badges.values():
                if all(req_id in achievement_ids for req_id in badge.requirements):
                    earned_badges.append(badge)
            
            return earned_badges
            
        except Exception as e:
            self.logger.error(f"Error getting badges for user {user_id}: {e}")
            return []
    
    def generate_certificate(self, user_id: str, course: str) -> Optional[Certificate]:
        """Generate course completion certificate"""
        try:
            profile = self.storage.get_user_profile(user_id)
            if not profile or not profile.completed_course or profile.enrolled_course != course:
                return None
            
            user_achievements = self.get_user_achievements(user_id)
            
            # Calculate learning duration
            if profile.start_date:
                start_date = datetime.fromisoformat(profile.start_date.replace('Z', '+00:00'))
                time_spent = (datetime.now() - start_date).days
            else:
                time_spent = 0
            
            certificate = Certificate(
                id=f"cert_{user_id}_{course}_{datetime.now().strftime('%Y%m%d')}",
                user_id=user_id,
                course=course,
                completion_date=datetime.now().isoformat(),
                final_accuracy=profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0,
                total_questions=profile.total_questions,
                time_spent_days=time_spent,
                achievements_earned=len(user_achievements),
                certificate_url=f"sandbox://certificates/{certificate.id}.json"  # Sandbox URL
            )
            
            # Save certificate
            cert_path = f"{self.achievement_dir}/{certificate.id}.json"
            with open(cert_path, 'w') as f:
                json.dump(asdict(certificate), f, indent=2)
            
            return certificate
            
        except Exception as e:
            self.logger.error(f"Error generating certificate for user {user_id}: {e}")
            return None
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard data (simplified for sandbox)"""
        try:
            # In sandbox mode, return mock leaderboard
            # In production, this would aggregate data from all users
            
            return [
                {
                    "rank": 1,
                    "user_id": "demo_user_1",
                    "total_points": 1250,
                    "achievements": 15,
                    "accuracy": 0.92,
                    "course": "python-basics"
                },
                {
                    "rank": 2,
                    "user_id": "demo_user_2", 
                    "total_points": 980,
                    "achievements": 12,
                    "accuracy": 0.88,
                    "course": "javascript-intro"
                },
                {
                    "rank": 3,
                    "user_id": "demo_user_3",
                    "total_points": 750,
                    "achievements": 9,
                    "accuracy": 0.85,
                    "course": "data-science"
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return []
    
    def calculate_user_score(self, user_id: str) -> int:
        """Calculate total gamification score for user"""
        try:
            achievements = self.get_user_achievements(user_id)
            total_points = 0
            
            for user_ach in achievements:
                if user_ach.achievement_id in self.achievements:
                    total_points += self.achievements[user_ach.achievement_id].points
            
            # Bonus points for profile stats
            profile = self.storage.get_user_profile(user_id)
            if profile:
                # Accuracy bonus
                accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
                total_points += int(accuracy * 100)  # Up to 100 bonus points for perfect accuracy
                
                # Streak bonus
                total_points += profile.longest_streak * 5  # 5 points per best streak
            
            return total_points
            
        except Exception as e:
            self.logger.error(f"Error calculating score for user {user_id}: {e}")
            return 0
```

### 1.2 Test Achievement System in Codespace
```bash
# Test the achievement system in Codespace terminal
python -c "
from src.config import Config
from src.sandbox_storage import SandboxStorage
from src.sandbox_learning_analytics import SandboxLearningAnalytics
from src.sandbox_achievements import SandboxAchievementSystem

config = Config()
storage = SandboxStorage(config.DATA_DIRECTORY)
analytics = SandboxLearningAnalytics(config, storage)
achievements = SandboxAchievementSystem(config, storage, analytics)

# Test achievement initialization
print(f'Total achievements: {len(achievements.achievements)}')
print(f'Total badges: {len(achievements.badges)}')
print('✅ Achievement system initialized!')
"
```

---

## **Step 2: Gamification Features (25 minutes)**

### 2.1 Create Gamification Manager
1. **Create**: `src/sandbox_gamification.py`

```python
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from config import Config
from sandbox_storage import SandboxStorage
from sandbox_achievements import SandboxAchievementSystem, Achievement, UserAchievement, Badge

@dataclass
class DailyChallenge:
    id: str
    title: str
    description: str
    emoji: str
    target_value: int
    current_progress: int
    reward_points: int
    expires_date: str
    challenge_type: str  # "questions", "accuracy", "streak", "topics"

@dataclass
class LevelInfo:
    level: int
    title: str
    emoji: str
    min_points: int
    max_points: int
    perks: List[str]

class SandboxGamification:
    """Comprehensive gamification system for enhanced engagement"""
    
    def __init__(self, config: Config, storage: SandboxStorage, achievements: SandboxAchievementSystem):
        self.config = config
        self.storage = storage
        self.achievements = achievements
        self.logger = logging.getLogger(__name__)
        
        # Level system
        self.levels = self._initialize_levels()
        
        # Daily challenges
        self.daily_challenges = self._generate_daily_challenges()
    
    def _initialize_levels(self) -> Dict[int, LevelInfo]:
        """Initialize the level progression system"""
        levels = {}
        
        levels[1] = LevelInfo(
            level=1,
            title="Curious Newcomer",
            emoji="🌱",
            min_points=0,
            max_points=99,
            perks=["Basic quiz access", "Progress tracking"]
        )
        
        levels[2] = LevelInfo(
            level=2,
            title="Eager Learner",
            emoji="📚",
            min_points=100,
            max_points=249,
            perks=["Adaptive difficulty", "Basic analytics"]
        )
        
        levels[3] = LevelInfo(
            level=3,
            title="Dedicated Student",
            emoji="🎯",
            min_points=250,
            max_points=499,
            perks=["Topic insights", "Study recommendations"]
        )
        
        levels[4] = LevelInfo(
            level=4,
            title="Knowledge Seeker",
            emoji="🧠",
            min_points=500,
            max_points=999,
            perks=["Advanced analytics", "Daily challenges"]
        )
        
        levels[5] = LevelInfo(
            level=5,
            title="Skilled Practitioner",
            emoji="⚡",
            min_points=1000,
            max_points=1999,
            perks=["Speed challenges", "Mastery tracking"]
        )
        
        levels[6] = LevelInfo(
            level=6,
            title="Expert Scholar",
            emoji="🏆",
            min_points=2000,
            max_points=3999,
            perks=["Expert mode", "Advanced challenges"]
        )
        
        levels[7] = LevelInfo(
            level=7,
            title="Master Teacher",
            emoji="👑",
            min_points=4000,
            max_points=7999,
            perks=["All features", "Leaderboard access"]
        )
        
        levels[8] = LevelInfo(
            level=8,
            title="Learning Legend",
            emoji="💎",
            min_points=8000,
            max_points=15999,
            perks=["Legendary status", "Special recognition"]
        )
        
        levels[9] = LevelInfo(
            level=9,
            title="Wisdom Guardian",
            emoji="🌟",
            min_points=16000,
            max_points=31999,
            perks=["Ultimate mastery", "Exclusive access"]
        )
        
        levels[10] = LevelInfo(
            level=10,
            title="Transcendent Sage",
            emoji="✨",
            min_points=32000,
            max_points=999999,
            perks=["Maximum level", "Eternal recognition"]
        )
        
        return levels
    
    def _generate_daily_challenges(self) -> List[DailyChallenge]:
        """Generate daily challenges for engagement"""
        today = datetime.now().strftime("%Y%m%d")
        
        challenges = [
            DailyChallenge(
                id=f"daily_questions_{today}",
                title="Question Marathon",
                description="Answer 10 questions today",
                emoji="📝",
                target_value=10,
                current_progress=0,
                reward_points=50,
                expires_date=today,
                challenge_type="questions"
            ),
            DailyChallenge(
                id=f"daily_accuracy_{today}",
                title="Precision Challenge",
                description="Maintain 80% accuracy over 5 questions",
                emoji="🎯",
                target_value=5,
                current_progress=0,
                reward_points=75,
                expires_date=today,
                challenge_type="accuracy"
            ),
            DailyChallenge(
                id=f"daily_streak_{today}",
                title="Streak Builder",
                description="Build a 5-question correct streak",
                emoji="🔥",
                target_value=5,
                current_progress=0,
                reward_points=60,
                expires_date=today,
                challenge_type="streak"
            )
        ]
        
        return challenges
    
    def get_user_level(self, user_id: str) -> LevelInfo:
        """Get user's current level information"""
        try:
            total_points = self.achievements.calculate_user_score(user_id)
            
            for level_num in sorted(self.levels.keys(), reverse=True):
                level_info = self.levels[level_num]
                if total_points >= level_info.min_points:
                    return level_info
            
            return self.levels[1]  # Default to level 1
            
        except Exception as e:
            self.logger.error(f"Error getting user level for {user_id}: {e}")
            return self.levels[1]
    
    def get_progress_to_next_level(self, user_id: str) -> Dict[str, Any]:
        """Get progress information to next level"""
        try:
            total_points = self.achievements.calculate_user_score(user_id)
            current_level = self.get_user_level(user_id)
            
            next_level_num = current_level.level + 1
            if next_level_num in self.levels:
                next_level = self.levels[next_level_num]
                points_needed = next_level.min_points - total_points
                progress_percent = min((total_points - current_level.min_points) / 
                                     (current_level.max_points - current_level.min_points) * 100, 100)
            else:
                next_level = None
                points_needed = 0
                progress_percent = 100
            
            return {
                "current_level": current_level,
                "next_level": next_level,
                "current_points": total_points,
                "points_needed": points_needed,
                "progress_percent": progress_percent
            }
            
        except Exception as e:
            self.logger.error(f"Error getting level progress for {user_id}: {e}")
            return {}
    
    def check_daily_challenges(self, user_id: str) -> List[DailyChallenge]:
        """Check and update daily challenge progress"""
        try:
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                return []
            
            # Update challenge progress based on user activity
            updated_challenges = []
            
            for challenge in self.daily_challenges:
                if challenge.challenge_type == "questions":
                    # Count questions answered today
                    challenge.current_progress = min(profile.total_questions % 50, challenge.target_value)
                
                elif challenge.challenge_type == "accuracy":
                    # Check recent accuracy
                    recent_accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
                    if recent_accuracy >= 0.8:
                        challenge.current_progress = min(profile.total_questions % 10, challenge.target_value)
                
                elif challenge.challenge_type == "streak":
                    challenge.current_progress = min(profile.current_streak, challenge.target_value)
                
                updated_challenges.append(challenge)
            
            return updated_challenges
            
        except Exception as e:
            self.logger.error(f"Error checking daily challenges for {user_id}: {e}")
            return []
    
    def get_user_stats_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics for gamification"""
        try:
            profile = self.storage.get_user_profile(user_id)
            if not profile:
                return {}
            
            user_achievements = self.achievements.get_user_achievements(user_id)
            user_badges = self.achievements.get_user_badges(user_id)
            level_info = self.get_user_level(user_id)
            level_progress = self.get_progress_to_next_level(user_id)
            total_points = self.achievements.calculate_user_score(user_id)
            
            # Calculate additional stats
            accuracy = profile.correct_answers / profile.total_questions if profile.total_questions > 0 else 0
            
            # Learning duration
            if profile.start_date:
                start_date = datetime.fromisoformat(profile.start_date.replace('Z', '+00:00'))
                learning_days = (datetime.now() - start_date).days
            else:
                learning_days = 0
            
            return {
                "level": level_info,
                "level_progress": level_progress,
                "total_points": total_points,
                "achievements": {
                    "total": len(user_achievements),
                    "by_rarity": self._count_achievements_by_rarity(user_achievements)
                },
                "badges": {
                    "total": len(user_badges),
                    "earned": [badge.name for badge in user_badges]
                },
                "performance": {
                    "accuracy": accuracy,
                    "total_questions": profile.total_questions,
                    "current_streak": profile.current_streak,
                    "best_streak": profile.longest_streak,
                    "learning_days": learning_days
                },
                "course_info": {
                    "enrolled": profile.enrolled_course,
                    "completed": profile.completed_course
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user stats summary for {user_id}: {e}")
            return {}
    
    def _count_achievements_by_rarity(self, user_achievements: List[UserAchievement]) -> Dict[str, int]:
        """Count achievements by rarity level"""
        rarity_count = {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "legendary": 0}
        
        for user_ach in user_achievements:
            if user_ach.achievement_id in self.achievements.achievements:
                achievement = self.achievements.achievements[user_ach.achievement_id]
                rarity_count[achievement.rarity.value] += 1
        
        return rarity_count
    
    def generate_motivation_message(self, user_id: str) -> str:
        """Generate personalized motivation message"""
        try:
            stats = self.get_user_stats_summary(user_id)
            if not stats:
                return "Keep learning and growing! Every question brings you closer to mastery! 🌟"
            
            level = stats["level"]
            performance = stats["performance"]
            achievements_total = stats["achievements"]["total"]
            
            # Generate contextual motivation
            messages = []
            
            # Level-based motivation
            if level.level <= 2:
                messages.append(f"Welcome to your learning journey! You're a {level.title} {level.emoji}")
            elif level.level <= 5:
                messages.append(f"Great progress! You've reached {level.title} level {level.emoji}")
            else:
                messages.append(f"Incredible achievement! You're a {level.title} {level.emoji}")
            
            # Performance-based motivation
            if performance["accuracy"] >= 0.9:
                messages.append("Your accuracy is outstanding! Keep up the excellent work! 🎯")
            elif performance["accuracy"] >= 0.8:
                messages.append("Great accuracy! You're mastering the concepts! 📚")
            elif performance["current_streak"] >= 5:
                messages.append(f"Amazing streak of {performance['current_streak']}! You're on fire! 🔥")
            
            # Achievement-based motivation
            if achievements_total >= 10:
                messages.append(f"Wow! {achievements_total} achievements unlocked! You're a true achiever! 🏆")
            elif achievements_total >= 5:
                messages.append(f"{achievements_total} achievements earned! Keep collecting! ⭐")
            
            # Progress-based motivation
            if performance["learning_days"] >= 30:
                messages.append(f"{performance['learning_days']} days of learning! Your dedication is inspiring! 💪")
            elif performance["learning_days"] >= 7:
                messages.append(f"A whole week of learning! Consistency is key! 📅")
            
            # Default motivation if no specific triggers
            if not messages:
                messages.append("Every expert was once a beginner. Keep pushing forward! 🚀")
            
            return " ".join(messages[:2])  # Limit to 2 motivational statements
            
        except Exception as e:
            self.logger.error(f"Error generating motivation message for {user_id}: {e}")
            return "You're doing great! Keep up the amazing work! 🌟"
    
    def get_celebration_message(self, user_achievements: List[UserAchievement]) -> str:
        """Generate celebration message for new achievements"""
        if not user_achievements:
            return ""
        
        if len(user_achievements) == 1:
            achievement = self.achievements.achievements[user_achievements[0].achievement_id]
            return f"🎉 **Achievement Unlocked!** 🎉\n\n{achievement.emoji} **{achievement.name}**\n{achievement.unlocked_message}\n+{achievement.points} points!"
        else:
            total_points = sum(self.achievements.achievements[ach.achievement_id].points 
                             for ach in user_achievements 
                             if ach.achievement_id in self.achievements.achievements)
            
            return f"🎉 **Multiple Achievements Unlocked!** 🎉\n\n{len(user_achievements)} new achievements earned!\n+{total_points} total points!\n\nYou're on fire! 🔥"
```

---

## **Step 3: Update Bot with Gamification (15 minutes)**

### 3.1 Integrate Gamification into Bot
1. **Update** `src/bot.py` to add gamification features:

```python
# Add these imports at the top
from sandbox_achievements import SandboxAchievementSystem
from sandbox_gamification import SandboxGamification

# Add after learning_analytics initialization
achievement_system = SandboxAchievementSystem(config, storage, learning_analytics)
gamification = SandboxGamification(config, storage, achievement_system)

# Update the quiz answer handler to check for achievements
async def handle_quiz_answer(context: TurnContext, user_id: str, answer: str):
    """Handle quiz answer from user (now with achievement checking)"""
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
        
        # CHECK FOR NEW ACHIEVEMENTS!
        new_achievements = achievement_system.check_achievements(user_id)
        
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
"""

        # Add achievement notifications
        if new_achievements:
            celebration = gamification.get_celebration_message(new_achievements)
            response_text += f"\n\n{celebration}"
        
        # Add level progress
        level_progress = gamification.get_progress_to_next_level(user_id)
        if level_progress:
            current_level = level_progress["current_level"]
            response_text += f"\n\n📈 **Level**: {current_level.emoji} {current_level.title} (Level {current_level.level})"
            if level_progress["next_level"]:
                response_text += f"\n🎯 **Next Level**: {level_progress['points_needed']} points needed"
        
        # Add motivation
        motivation = gamification.generate_motivation_message(user_id)
        response_text += f"\n\n💫 {motivation}"
        
        response_text += f"\n\n💡 **{feedback['encouragement']}**"
        response_text += f"\n🚀 **Next Steps**: {feedback['next_steps']}"
        response_text += "\n\nReady for another question? Type `/quiz` to continue learning!"
        
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

# Add new gamification commands
async def handle_achievements_command(context: TurnContext, user_id: str):
    """Show user achievements and badges"""
    try:
        user_achievements = achievement_system.get_user_achievements(user_id)
        user_badges = achievement_system.get_user_badges(user_id)
        total_points = achievement_system.calculate_user_score(user_id)
        
        if not user_achievements:
            await context.send_activity(MessageFactory.text(
                "🏆 **No Achievements Yet!**\n\n"
                "Start taking quizzes to unlock achievements!\n"
                "Use `/quiz` to begin earning rewards! 🌟"
            ))
            return
        
        # Group achievements by rarity
        rarity_groups = {"common": [], "uncommon": [], "rare": [], "epic": [], "legendary": []}
        
        for user_ach in user_achievements:
            if user_ach.achievement_id in achievement_system.achievements:
                achievement = achievement_system.achievements[user_ach.achievement_id]
                rarity_groups[achievement.rarity.value].append(achievement)
        
        achievements_text = f"🏆 **Your Achievements** ({len(user_achievements)} earned)\n"
        achievements_text += f"💎 **Total Points**: {total_points}\n\n"
        
        # Display achievements by rarity
        rarity_emojis = {
            "legendary": "💎", "epic": "🌟", "rare": "⚡", 
            "uncommon": "🔥", "common": "⭐"
        }
        
        for rarity in ["legendary", "epic", "rare", "uncommon", "common"]:
            achievements = rarity_groups[rarity]
            if achievements:
                achievements_text += f"{rarity_emojis[rarity]} **{rarity.title()}** ({len(achievements)}):\n"
                for ach in achievements:
                    achievements_text += f"   {ach.emoji} {ach.name} (+{ach.points}pts)\n"
                achievements_text += "\n"
        
        # Display badges
        if user_badges:
            achievements_text += "🎖️ **Badges Earned**:\n"
            for badge in user_badges:
                achievements_text += f"   {badge.emoji} {badge.name} ({badge.tier.title()})\n"
        
        await context.send_activity(MessageFactory.text(achievements_text))
        
    except Exception as e:
        logger.error(f"Error handling achievements command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error loading achievements. Please try again."
        ))

async def handle_level_command(context: TurnContext, user_id: str):
    """Show user level and progress"""
    try:
        stats = gamification.get_user_stats_summary(user_id)
        
        if not stats:
            await context.send_activity(MessageFactory.text(
                "📈 **Start Your Journey!**\n\n"
                "Enroll in a course and take quizzes to begin leveling up!\n"
                "Use `/enroll [course-name]` to get started! 🚀"
            ))
            return
        
        level = stats["level"]
        level_progress = stats["level_progress"]
        total_points = stats["total_points"]
        
        level_text = f"""
📈 **Your Learning Level**

{level.emoji} **{level.title}** (Level {level.level})
💎 **Total Points**: {total_points}

📊 **Progress to Next Level**:
"""
        
        if level_progress.get("next_level"):
            next_level = level_progress["next_level"]
            progress_percent = level_progress["progress_percent"]
            points_needed = level_progress["points_needed"]
            
            # Create progress bar
            progress_bar = "█" * int(progress_percent // 10) + "░" * (10 - int(progress_percent // 10))
            
            level_text += f"🎯 **Target**: {next_level.emoji} {next_level.title} (Level {next_level.level})\n"
            level_text += f"📊 **Progress**: {progress_percent:.1f}% [{progress_bar}]\n"
            level_text += f"⚡ **Points Needed**: {points_needed}\n\n"
        else:
            level_text += "🏆 **Maximum Level Achieved!** 🏆\n\n"
        
        # Show level perks
        level_text += "🎁 **Level Perks**:\n"
        for perk in level.perks:
            level_text += f"   ✅ {perk}\n"
        
        # Show performance stats
        performance = stats["performance"]
        level_text += f"\n📚 **Performance**:\n"
        level_text += f"   🎯 Accuracy: {performance['accuracy']:.1%}\n"
        level_text += f"   📝 Questions: {performance['total_questions']}\n"
        level_text += f"   🔥 Best Streak: {performance['best_streak']}\n"
        level_text += f"   📅 Learning Days: {performance['learning_days']}\n"
        
        await context.send_activity(MessageFactory.text(level_text))
        
    except Exception as e:
        logger.error(f"Error handling level command: {e}")
        await context.send_activity(MessageFactory.text(
            "❌ Error loading level information. Please try again."
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

# Update the help command to include gamification features
async def handle_help_command(context: TurnContext):
    """Show help information"""
    help_text = """
🤖 **AI Learning Bot - Gamified Learning** 🤖

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

**🏆 Gamification Features:**
• **Achievements**: Unlock 20+ unique achievements
• **Badges**: Earn bronze, silver, gold, and platinum badges
• **Levels**: Progress through 10 learning levels
• **Points**: Earn points for correct answers and achievements
• **Streaks**: Build and maintain learning streaks

**Quick Start:**
```
/enroll python-basics
/quiz
/achievements
/level
```

*🎮 Day 5: Gamified learning with achievements and levels! 🎮*
"""
    await context.send_activity(MessageFactory.text(help_text))
```

---

## **Step 4: Test Gamification System (10 minutes)**

### 4.1 Test Complete Gamification Flow in Codespace
```bash
# Restart the bot to load new features
# Stop current bot (Ctrl+C in terminal)
# Then restart:
python src/app.py
```

### 4.2 Verify Codespace Status
1. **Check** port 3978 is forwarded and public
2. **Confirm** all gamification files saved
3. **Test** endpoint accessibility

### 4.3 Test in Teams
1. **Test** gamification commands:
```
/achievements
/level
```

2. **Take multiple quizzes** to unlock achievements:
```
/quiz
# Answer correctly to build streaks
/quiz
# Keep answering to unlock achievements
```

3. **Check progress** after earning achievements:
```
/achievements
/level
```

### 4.3 Verify Achievement System
- Complete 3+ correct answers in a row (should unlock first streak achievement)
- Check that points are calculated correctly
- Verify level progression works
- Confirm achievement notifications appear after quiz answers

---

## **✅ Day 5 Checklist**

Verify all these work:

- [ ] Created `src/sandbox_achievements.py` with comprehensive achievement system
- [ ] Created `src/sandbox_gamification.py` with levels and motivation
- [ ] Updated `src/bot.py` with gamification integration
- [ ] `/achievements` command shows earned achievements and points
- [ ] `/level` command displays current level and progress
- [ ] Achievement notifications appear after quiz completion
- [ ] Points system calculates correctly
- [ ] Level progression works based on points
- [ ] Achievement files are saved in `playground/data/achievements/`
- [ ] Motivation messages generate appropriately
- [ ] Badge system recognizes achievement combinations
- [ ] Streak achievements unlock automatically

---

## **🚀 What's Next?**

**Day 6**: We'll add course completion certificates, progress export, and prepare for production migration features.

---

## **💡 Troubleshooting**

### Common Issues:

**Achievements not unlocking:**
- Take at least 3-5 quiz questions to trigger achievements
- Check that profile data is saving correctly
- Verify achievement criteria in the code

**Level not updating:**
- Ensure achievements are being saved
- Check point calculation logic
- Verify level thresholds are correct

**Points not calculating:**
- Check that achievements are being recorded
- Verify user_achievements files are being created
- Look for calculation errors in logs

**Gamification features not showing:**
- Restart the bot after adding new features
- Check that imports are correct
- Verify file permissions for achievement storage

---

**🎉 Success!** Your AI learning bot now features a complete gamification system with achievements, levels, badges, and motivational features!