from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base


class Vocabulary(Base):
    """Vocabulary model for storing words and phrases"""
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    word_phrase = Column(String(255), nullable=False)
    classification = Column(String(100), nullable=True)  # noun, verb, adjective, etc.
    pronunciation = Column(String(255), nullable=True)  # phonetic pronunciation
    meaning = Column(Text, nullable=True)  # definition/meaning
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="vocabularies")
    examples = relationship("Example", back_populates="vocabulary", cascade="all, delete-orphan")
    spaced_repetitions = relationship("SpacedRepetition", back_populates="vocabulary", cascade="all, delete-orphan")


class Example(Base):
    """Example sentences for vocabulary"""
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=False, index=True)
    example_sentence = Column(Text, nullable=False)
    ai_feedback = Column(Text, nullable=True)  # AI feedback on the example
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vocabulary = relationship("Vocabulary", back_populates="examples")


class SpacedRepetition(Base):
    """Spaced repetition tracking for vocabulary"""
    __tablename__ = "spaced_repetition"

    id = Column(Integer, primary_key=True, index=True)
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    proficiency_level = Column(Integer, default=0)  # 0=new, 1=learning, 2=familiar, 3=mastered
    next_review_date = Column(DateTime(timezone=True), nullable=False)
    review_count = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)  # SM-2 algorithm ease factor
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vocabulary = relationship("Vocabulary", back_populates="spaced_repetitions")
    user = relationship("User", back_populates="spaced_repetitions")


class ReviewSession(Base):
    """Review sessions for tracking learning progress"""
    __tablename__ = "review_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"), nullable=False, index=True)
    session_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    performance_score = Column(Integer, nullable=False)  # 0=again, 1=hard, 2=good, 3=easy
    time_spent = Column(Integer, default=0)  # time in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    vocabulary = relationship("Vocabulary")
