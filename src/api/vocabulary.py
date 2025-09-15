from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.dependencies.auth import get_current_user
from src.db.models.user import User
from src.services.vocabulary_service import VocabularyService
from src.schemas.vocabulary import (
    WordAnalysisResponse,
    ExampleFeedbackResponse,
    SaveVocabularyRequest,
    SaveVocabularyResponse,
    VocabularyListResponse,
    TodayReviewResponse,
    DashboardStatsResponse,
    ReviewPerformanceRequest,
    ReviewPerformanceResponse,
    VocabularyFilterRequest
)
from src.schemas.learning_flow import LearningFlowRequest
from src.services.learning_flow_service import learning_flow_service
from src.core.response import success_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/learn/interactive")
async def interactive_learning_session(
    request: LearningFlowRequest,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Handles an interactive learning session using a stateful graph.
    """
    try:
        # The frontend would send the initial state.
        # For the first turn, it's just the word.
        # For subsequent turns (if the sentence needs improvement),
        # the frontend would send back the whole state object it received,
        # plus the new 'example_sentence'.
        initial_state = {
            "word_phrase": request.word_phrase,
            "example_sentence": request.example_sentence
        }
        
        # The graph will run from the start or continue from where it left off
        # based on the provided state. For this simplified endpoint, we run
        # the full analysis and feedback path each time.
        final_state = await learning_flow_service.run(initial_state)

        return success_response(
            data=final_state,
            message="Learning session updated successfully"
        )
    except Exception as e:
        logger.error(f"Error during interactive learning session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during the interactive session."
        )


@router.post("/save")
async def save_vocabulary(
    request: SaveVocabularyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Save vocabulary item with example and create spaced repetition record
    """
    try:
        vocabulary_service = VocabularyService(db)
        result = await vocabulary_service.save_vocabulary_with_example(
            user_id=current_user.id,
            word_phrase=request.word_phrase,
            classification=request.classification,
            pronunciation=request.pronunciation,
            meaning=request.meaning,
            example_sentence=request.example_sentence,
            ai_feedback=request.ai_feedback
        )
        
        return success_response(data=result, message="Vocabulary saved successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error saving vocabulary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save vocabulary"
        )


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get dashboard statistics for the current user
    """
    try:
        vocabulary_service = VocabularyService(db)
        stats = vocabulary_service.get_dashboard_statistics(current_user.id)
        
        return success_response(data=stats, message="Dashboard statistics retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard statistics"
        )


@router.get("/today-review")
async def get_today_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get vocabulary items for today's review
    """
    try:
        vocabulary_service = VocabularyService(db)
        reviews = vocabulary_service.get_today_reviews(current_user.id)
        
        return success_response(
            data={
                "reviews": reviews,
                "total": len(reviews)
            }, 
            message="Today's reviews retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting today's reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get today's reviews"
        )


@router.get("/list")
async def get_vocabulary_list(
    skip: int = 0,
    limit: int = 100,
    proficiency_level: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user's vocabulary list with optional filtering
    """
    try:
        vocabulary_service = VocabularyService(db)
        vocabularies = vocabulary_service.get_user_vocabulary(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            proficiency_level=proficiency_level
        )
        
        # Get total count for pagination
        total = len(vocabularies)
        
        return success_response(
            data={
                "vocabularies": vocabularies,
                "total": total,
                "skip": skip,
                "limit": limit
            },
            message="Vocabulary list retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting vocabulary list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get vocabulary list"
        )


@router.post("/{vocabulary_id}/review")
async def update_review_performance(
    vocabulary_id: int,
    request: ReviewPerformanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update review performance for a vocabulary item
    """
    try:
        vocabulary_service = VocabularyService(db)
        result = vocabulary_service.update_review_performance(
            user_id=current_user.id,
            vocabulary_id=vocabulary_id,
            performance_score=request.performance_score,
            time_spent=request.time_spent
        )
        
        return success_response(data=result, message="Review performance updated successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating review performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review performance"
        )


@router.delete("/{vocabulary_id}")
async def delete_vocabulary(
    vocabulary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a vocabulary item and all related data
    """
    try:
        vocabulary_service = VocabularyService(db)
        success = vocabulary_service.delete_vocabulary(
            user_id=current_user.id,
            vocabulary_id=vocabulary_id
        )
        
        if success:
            return success_response(message="Vocabulary item deleted successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete vocabulary item"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting vocabulary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete vocabulary item"
        )
