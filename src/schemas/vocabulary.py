from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class WordAnalysisResponse(BaseModel):
    """Response schema for word analysis"""
    classification: str = Field(..., description="Part of speech classification")
    pronunciation: str = Field(..., description="Phonetic pronunciation")
    meaning: str = Field(..., description="Definition/meaning")
    difficulty_level: str = Field(..., description="Difficulty level (beginner/intermediate/advanced)")


class ExampleFeedbackResponse(BaseModel):
    """Response schema for example feedback"""
    grammar_correctness: str = Field(..., description="Assessment of grammar correctness")
    natural_usage: str = Field(..., description="Evaluation of natural usage in context")
    suggestions: str = Field(..., description="Suggestions for improvement")
    alternative_examples: List[str] = Field(..., description="Alternative example sentences")


class SaveVocabularyRequest(BaseModel):
    """Request schema for saving vocabulary"""
    word_phrase: str = Field(..., min_length=1, max_length=255, description="Word or phrase")
    classification: str = Field(..., description="Part of speech")
    pronunciation: str = Field(..., description="Phonetic pronunciation")
    meaning: str = Field(..., description="Definition/meaning")
    example_sentence: str = Field(..., min_length=1, description="Example sentence")
    ai_feedback: str = Field(..., description="AI feedback on the example")


class ExampleSchema(BaseModel):
    """Schema for example data"""
    id: int
    example_sentence: str
    ai_feedback: str
    created_at: datetime

    class Config:
        from_attributes = True


class SpacedRepetitionSchema(BaseModel):
    """Schema for spaced repetition data"""
    proficiency_level: int = Field(..., description="0=new, 1=learning, 2=familiar, 3=mastered")
    next_review_date: Optional[datetime] = Field(None, description="Next review date")
    review_count: int = Field(..., description="Number of reviews completed")
    ease_factor: float = Field(..., description="Ease factor for SM-2 algorithm")

    class Config:
        from_attributes = True


class VocabularySchema(BaseModel):
    """Schema for vocabulary data"""
    id: int
    word_phrase: str
    classification: str
    pronunciation: str
    meaning: str
    created_at: datetime
    examples: List[ExampleSchema] = []
    spaced_repetition: Optional[SpacedRepetitionSchema] = None

    class Config:
        from_attributes = True


class SaveVocabularyResponse(BaseModel):
    """Response schema for saving vocabulary"""
    vocabulary: VocabularySchema
    example: ExampleSchema
    spaced_repetition: SpacedRepetitionSchema


class VocabularyListResponse(BaseModel):
    """Response schema for vocabulary list"""
    vocabularies: List[VocabularySchema]
    total: int
    skip: int
    limit: int


class TodayReviewResponse(BaseModel):
    """Response schema for today's reviews"""
    reviews: List[VocabularySchema]
    total: int


class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics"""
    total_vocabulary: int
    proficiency_levels: Dict[str, int] = Field(..., description="Count by proficiency level")
    today_reviews: int


class ReviewPerformanceRequest(BaseModel):
    """Request schema for updating review performance"""
    performance_score: int = Field(..., ge=0, le=3, description="0=again, 1=hard, 2=good, 3=easy")
    time_spent: int = Field(0, ge=0, description="Time spent in seconds")


class ReviewPerformanceResponse(BaseModel):
    """Response schema for review performance update"""
    proficiency_level: int
    next_review_date: datetime
    review_count: int
    ease_factor: float

class VocabularyFilterRequest(BaseModel):
    """Request schema for filtering vocabulary"""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    proficiency_level: Optional[int] = Field(None, ge=0, le=3, description="Filter by proficiency level")

