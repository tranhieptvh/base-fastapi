from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.db.models.vocabulary import Vocabulary, Example, SpacedRepetition
from src.db.models.user import User
from src.services.spaced_repetition import SpacedRepetitionService
import logging

logger = logging.getLogger(__name__)


class VocabularyService:
    """Service for managing vocabulary and examples"""
    
    def __init__(self, db: Session):
        self.db = db
        self.spaced_rep_service = SpacedRepetitionService(db)
    
    async def save_vocabulary_with_example(
        self,
        user_id: int,
        word_phrase: str,
        classification: str,
        pronunciation: str,
        meaning: str,
        example_sentence: str,
        ai_feedback: str
    ) -> Dict[str, Any]:
        """
        Save vocabulary item with example and create spaced repetition record
        
        Args:
            user_id: ID of the user
            word_phrase: The word or phrase
            classification: Part of speech
            pronunciation: Phonetic pronunciation
            meaning: Definition/meaning
            example_sentence: Example sentence
            ai_feedback: AI feedback on the example
            
        Returns:
            Dictionary with saved vocabulary and example data
        """
        try:
            # Check if vocabulary already exists for this user
            existing_vocab = self.db.query(Vocabulary).filter(
                and_(
                    Vocabulary.user_id == user_id,
                    Vocabulary.word_phrase == word_phrase
                )
            ).first()
            
            if existing_vocab:
                raise ValueError("This word/phrase already exists in your vocabulary")
            
            # Create vocabulary record
            vocabulary = Vocabulary(
                user_id=user_id,
                word_phrase=word_phrase,
                classification=classification,
                pronunciation=pronunciation,
                meaning=meaning
            )
            
            self.db.add(vocabulary)
            self.db.flush()  # Get the ID without committing
            
            # Create example record
            example = Example(
                vocabulary_id=vocabulary.id,
                example_sentence=example_sentence,
                ai_feedback=ai_feedback
            )
            
            self.db.add(example)
            
            # Create spaced repetition record
            spaced_rep = self.spaced_rep_service.create_spaced_repetition_record(
                user_id, vocabulary.id
            )
            
            self.db.commit()
            
            return {
                "vocabulary": {
                    "id": vocabulary.id,
                    "word_phrase": vocabulary.word_phrase,
                    "classification": vocabulary.classification,
                    "pronunciation": vocabulary.pronunciation,
                    "meaning": vocabulary.meaning,
                    "created_at": vocabulary.created_at
                },
                "example": {
                    "id": example.id,
                    "example_sentence": example.example_sentence,
                    "ai_feedback": example.ai_feedback,
                    "created_at": example.created_at
                },
                "spaced_repetition": {
                    "id": spaced_rep.id,
                    "proficiency_level": spaced_rep.proficiency_level,
                    "next_review_date": spaced_rep.next_review_date,
                    "review_count": spaced_rep.review_count
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving vocabulary: {e}")
            raise e
    
    def get_user_vocabulary(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        proficiency_level: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's vocabulary with optional filtering
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            proficiency_level: Filter by proficiency level (optional)
            
        Returns:
            List of vocabulary items with examples and spaced repetition data
        """
        query = self.db.query(Vocabulary).filter(Vocabulary.user_id == user_id)
        
        if proficiency_level is not None:
            query = query.join(SpacedRepetition).filter(
                SpacedRepetition.proficiency_level == proficiency_level
            )
        
        vocabularies = query.offset(skip).limit(limit).all()
        
        result = []
        for vocab in vocabularies:
            # Get examples
            examples = self.db.query(Example).filter(
                Example.vocabulary_id == vocab.id
            ).all()
            
            # Get spaced repetition data
            spaced_rep = self.db.query(SpacedRepetition).filter(
                SpacedRepetition.vocabulary_id == vocab.id
            ).first()
            
            result.append({
                "id": vocab.id,
                "word_phrase": vocab.word_phrase,
                "classification": vocab.classification,
                "pronunciation": vocab.pronunciation,
                "meaning": vocab.meaning,
                "created_at": vocab.created_at,
                "examples": [
                    {
                        "id": ex.id,
                        "example_sentence": ex.example_sentence,
                        "ai_feedback": ex.ai_feedback,
                        "created_at": ex.created_at
                    } for ex in examples
                ],
                "spaced_repetition": {
                    "proficiency_level": spaced_rep.proficiency_level if spaced_rep else 0,
                    "next_review_date": spaced_rep.next_review_date if spaced_rep else None,
                    "review_count": spaced_rep.review_count if spaced_rep else 0,
                    "ease_factor": spaced_rep.ease_factor if spaced_rep else 2.5
                } if spaced_rep else None
            })
        
        return result
    
    def get_today_reviews(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get vocabulary items for today's review
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of vocabulary items for review
        """
        vocabularies = self.spaced_rep_service.get_today_reviews(user_id)
        
        result = []
        for vocab in vocabularies:
            # Get examples
            examples = self.db.query(Example).filter(
                Example.vocabulary_id == vocab.id
            ).all()
            
            # Get spaced repetition data
            spaced_rep = self.db.query(SpacedRepetition).filter(
                SpacedRepetition.vocabulary_id == vocab.id
            ).first()
            
            result.append({
                "id": vocab.id,
                "word_phrase": vocab.word_phrase,
                "classification": vocab.classification,
                "pronunciation": vocab.pronunciation,
                "meaning": vocab.meaning,
                "examples": [
                    {
                        "id": ex.id,
                        "example_sentence": ex.example_sentence,
                        "ai_feedback": ex.ai_feedback
                    } for ex in examples
                ],
                "spaced_repetition": {
                    "proficiency_level": spaced_rep.proficiency_level,
                    "next_review_date": spaced_rep.next_review_date,
                    "review_count": spaced_rep.review_count,
                    "ease_factor": spaced_rep.ease_factor
                }
            })
        
        return result
    
    def get_dashboard_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get dashboard statistics for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with statistics
        """
        return self.spaced_rep_service.get_dashboard_statistics(user_id)
    
    def update_review_performance(
        self,
        user_id: int,
        vocabulary_id: int,
        performance_score: int,
        time_spent: int = 0
    ) -> Dict[str, Any]:
        """
        Update review performance for a vocabulary item
        
        Args:
            user_id: ID of the user
            vocabulary_id: ID of the vocabulary item
            performance_score: Performance score (0-3)
            time_spent: Time spent in seconds
            
        Returns:
            Updated spaced repetition data
        """
        try:
            spaced_rep = self.spaced_rep_service.update_review_performance(
                user_id, vocabulary_id, performance_score, time_spent
            )
            
            return {
                "proficiency_level": spaced_rep.proficiency_level,
                "next_review_date": spaced_rep.next_review_date,
                "review_count": spaced_rep.review_count,
                "ease_factor": spaced_rep.ease_factor
            }
            
        except Exception as e:
            logger.error(f"Error updating review performance: {e}")
            raise e
    
    def delete_vocabulary(self, user_id: int, vocabulary_id: int) -> bool:
        """
        Delete a vocabulary item and all related data
        
        Args:
            user_id: ID of the user
            vocabulary_id: ID of the vocabulary item
            
        Returns:
            True if successful
        """
        try:
            vocabulary = self.db.query(Vocabulary).filter(
                and_(
                    Vocabulary.id == vocabulary_id,
                    Vocabulary.user_id == user_id
                )
            ).first()
            
            if not vocabulary:
                raise ValueError("Vocabulary item not found")
            
            # Delete related records (cascade should handle this)
            self.db.delete(vocabulary)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting vocabulary: {e}")
            raise e
