from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from src.db.models.vocabulary import Vocabulary, SpacedRepetition, ReviewSession
from src.db.models.user import User
import logging

logger = logging.getLogger(__name__)


class SpacedRepetitionService:
    """Service for managing spaced repetition learning algorithm"""
    
    # SM-2 Algorithm constants
    INITIAL_INTERVAL = 1  # days
    EASY_FACTOR = 2.5
    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 2.5
    
    # Performance levels
    PERFORMANCE_AGAIN = 0
    PERFORMANCE_HARD = 1
    PERFORMANCE_GOOD = 2
    PERFORMANCE_EASY = 3
    
    # Proficiency levels
    PROFICIENCY_NEW = 0
    PROFICIENCY_LEARNING = 1
    PROFICIENCY_FAMILIAR = 2
    PROFICIENCY_MASTERED = 3
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_next_review(
        self, 
        performance_score: int, 
        current_ease_factor: float,
        review_count: int
    ) -> Tuple[datetime, float, int]:
        """
        Calculate next review date using SM-2 algorithm
        
        Args:
            performance_score: 0=again, 1=hard, 2=good, 3=easy
            current_ease_factor: Current ease factor
            review_count: Number of times reviewed
            
        Returns:
            Tuple of (next_review_date, new_ease_factor, new_review_count)
        """
        now = datetime.utcnow()
        
        if performance_score == self.PERFORMANCE_AGAIN:
            # Reset to beginning
            next_review = now + timedelta(days=self.INITIAL_INTERVAL)
            new_ease_factor = current_ease_factor
            new_review_count = 0
        else:
            # Calculate new ease factor
            new_ease_factor = self._calculate_ease_factor(
                performance_score, current_ease_factor
            )
            
            # Calculate interval
            if review_count == 0:
                interval = 1
            elif review_count == 1:
                interval = 6
            else:
                interval = int(review_count * new_ease_factor)
            
            next_review = now + timedelta(days=interval)
            new_review_count = review_count + 1
        
        return next_review, new_ease_factor, new_review_count
    
    def _calculate_ease_factor(self, performance_score: int, current_ease_factor: float) -> float:
        """Calculate new ease factor based on performance"""
        if performance_score == self.PERFORMANCE_HARD:
            new_ease_factor = current_ease_factor - 0.2
        elif performance_score == self.PERFORMANCE_GOOD:
            new_ease_factor = current_ease_factor
        elif performance_score == self.PERFORMANCE_EASY:
            new_ease_factor = current_ease_factor + 0.15
        else:
            new_ease_factor = current_ease_factor
        
        # Clamp between min and max
        return max(self.MIN_EASE_FACTOR, min(self.MAX_EASE_FACTOR, new_ease_factor))
    
    def get_proficiency_level(self, review_count: int, ease_factor: float) -> int:
        """
        Determine proficiency level based on review count and ease factor
        
        Args:
            review_count: Number of successful reviews
            ease_factor: Current ease factor
            
        Returns:
            Proficiency level (0=new, 1=learning, 2=familiar, 3=mastered)
        """
        if review_count == 0:
            return self.PROFICIENCY_NEW
        elif review_count < 5:
            return self.PROFICIENCY_LEARNING
        elif review_count < 10:
            return self.PROFICIENCY_FAMILIAR
        else:
            return self.PROFICIENCY_MASTERED
    
    def create_spaced_repetition_record(
        self, 
        user_id: int, 
        vocabulary_id: int
    ) -> SpacedRepetition:
        """
        Create initial spaced repetition record for a new vocabulary item
        
        Args:
            user_id: ID of the user
            vocabulary_id: ID of the vocabulary item
            
        Returns:
            Created SpacedRepetition record
        """
        now = datetime.utcnow()
        next_review = now + timedelta(days=self.INITIAL_INTERVAL)
        
        spaced_rep = SpacedRepetition(
            user_id=user_id,
            vocabulary_id=vocabulary_id,
            proficiency_level=self.PROFICIENCY_NEW,
            next_review_date=next_review,
            review_count=0,
            ease_factor=self.EASY_FACTOR
        )
        
        self.db.add(spaced_rep)
        self.db.commit()
        self.db.refresh(spaced_rep)
        
        return spaced_rep
    
    def update_review_performance(
        self,
        user_id: int,
        vocabulary_id: int,
        performance_score: int,
        time_spent: int = 0
    ) -> SpacedRepetition:
        """
        Update spaced repetition record after a review session
        
        Args:
            user_id: ID of the user
            vocabulary_id: ID of the vocabulary item
            performance_score: Performance score (0-3)
            time_spent: Time spent in seconds
            
        Returns:
            Updated SpacedRepetition record
        """
        # Get current spaced repetition record
        spaced_rep = self.db.query(SpacedRepetition).filter(
            SpacedRepetition.user_id == user_id,
            SpacedRepetition.vocabulary_id == vocabulary_id
        ).first()
        
        if not spaced_rep:
            raise ValueError("Spaced repetition record not found")
        
        # Calculate new values
        next_review, new_ease_factor, new_review_count = self.calculate_next_review(
            performance_score, spaced_rep.ease_factor, spaced_rep.review_count
        )
        
        new_proficiency = self.get_proficiency_level(new_review_count, new_ease_factor)
        
        # Update record
        spaced_rep.next_review_date = next_review
        spaced_rep.ease_factor = new_ease_factor
        spaced_rep.review_count = new_review_count
        spaced_rep.proficiency_level = new_proficiency
        
        # Create review session record
        review_session = ReviewSession(
            user_id=user_id,
            vocabulary_id=vocabulary_id,
            performance_score=performance_score,
            time_spent=time_spent
        )
        
        self.db.add(review_session)
        self.db.commit()
        self.db.refresh(spaced_rep)
        
        return spaced_rep
    
    def get_today_reviews(self, user_id: int) -> List[Vocabulary]:
        """
        Get vocabulary items that need to be reviewed today
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of Vocabulary items for today's review
        """
        today = datetime.utcnow().date()
        
        spaced_reps = self.db.query(SpacedRepetition).filter(
            SpacedRepetition.user_id == user_id,
            SpacedRepetition.next_review_date <= today
        ).all()
        
        vocabulary_ids = [sr.vocabulary_id for sr in spaced_reps]
        
        return self.db.query(Vocabulary).filter(
            Vocabulary.id.in_(vocabulary_ids)
        ).all()
    
    def get_dashboard_statistics(self, user_id: int) -> dict:
        """
        Get dashboard statistics for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with statistics
        """
        # Get total vocabulary count
        total_vocabulary = self.db.query(Vocabulary).filter(
            Vocabulary.user_id == user_id
        ).count()
        
        # Get proficiency level counts
        proficiency_counts = self.db.query(SpacedRepetition.proficiency_level).filter(
            SpacedRepetition.user_id == user_id
        ).all()
        
        new_count = sum(1 for level, in proficiency_counts if level == self.PROFICIENCY_NEW)
        learning_count = sum(1 for level, in proficiency_counts if level == self.PROFICIENCY_LEARNING)
        familiar_count = sum(1 for level, in proficiency_counts if level == self.PROFICIENCY_FAMILIAR)
        mastered_count = sum(1 for level, in proficiency_counts if level == self.PROFICIENCY_MASTERED)
        
        # Get today's review count
        today_reviews = len(self.get_today_reviews(user_id))
        
        return {
            "total_vocabulary": total_vocabulary,
            "proficiency_levels": {
                "new": new_count,
                "learning": learning_count,
                "familiar": familiar_count,
                "mastered": mastered_count
            },
            "today_reviews": today_reviews
        }
    
    def get_learning_progress(self, user_id: int, days: int = 30) -> List[dict]:
        """
        Get learning progress over the last N days
        
        Args:
            user_id: ID of the user
            days: Number of days to look back
            
        Returns:
            List of daily progress data
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get review sessions for the period
        sessions = self.db.query(ReviewSession).filter(
            ReviewSession.user_id == user_id,
            ReviewSession.session_date >= start_date
        ).order_by(ReviewSession.session_date).all()
        
        # Group by date
        daily_data = {}
        for session in sessions:
            date_key = session.session_date.date()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "total_reviews": 0,
                    "correct_answers": 0,
                    "time_spent": 0
                }
            
            daily_data[date_key]["total_reviews"] += 1
            if session.performance_score >= self.PERFORMANCE_GOOD:
                daily_data[date_key]["correct_answers"] += 1
            daily_data[date_key]["time_spent"] += session.time_spent
        
        return list(daily_data.values())
