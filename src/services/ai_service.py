from typing import Dict, Any, List
from langchain_core.pydantic_v1 import BaseModel, Field
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


# --- Pydantic Models for Output Parsing ---
class WordAnalysis(BaseModel):
    classification: str = Field(description="part of speech (noun, verb, adjective, adverb, phrase, etc.)")
    pronunciation: str = Field(description="phonetic pronunciation using IPA symbols")
    meaning: str = Field(description="clear and concise definition in English")
    difficulty_level: str = Field(description="beginner, intermediate, or advanced")

class ExampleFeedback(BaseModel):
    grammar_correctness: str = Field(description="Brief assessment of grammar - correct/incorrect with specific issues if any")
    natural_usage: str = Field(description="Evaluation if the word/phrase is used naturally and appropriately in context")
    suggestions: str = Field(description="Specific suggestions if needed, or 'No improvements needed' if perfect")
    alternative_examples: List[str] = Field(description="A list of exactly 3 alternative example sentences")

class SentenceEvaluation(BaseModel):
    evaluation: str = Field(description="The final verdict. Must be a single word: either 'good' or 'needs_improvement'.")


# --- Prompts ---
analysis_prompt = PromptTemplate(
    template="""
    Analyze the following English word or phrase: "{word_phrase}"
    {format_instructions}
    Be accurate and provide helpful information for English learners.
    """,
    input_variables=["word_phrase"],
    partial_variables={"format_instructions": PydanticOutputParser(pydantic_object=WordAnalysis).get_format_instructions()}
)

feedback_prompt = PromptTemplate(
    template="""
    As an English language tutor, provide structured feedback on this example sentence using the word/phrase "{word_phrase}":
    Example: "{example_sentence}"
    {format_instructions}
    Guidelines:
    - Keep each field concise (1-2 sentences max)
    - Be encouraging and constructive
    - Focus on practical usage
    - If the sentence is perfect, acknowledge it and provide additional examples
    - Use simple, clear language
    - Provide exactly 3 alternative examples
    """,
    input_variables=["word_phrase", "example_sentence"],
    partial_variables={"format_instructions": PydanticOutputParser(pydantic_object=ExampleFeedback).get_format_instructions()}
)

evaluation_prompt = PromptTemplate(
    template="""
    You are an expert evaluator. Based on the following feedback given to a student,
    decide if their original sentence was 'good' or if it 'needs_improvement'.
    
    The final evaluation must be a single word: either 'good' or 'needs_improvement'.

    Feedback Provided:
    - Grammar Correctness: {grammar_correctness}
    - Natural Usage: {natural_usage}
    - Suggestions: {suggestions}

    {format_instructions}
    """,
    input_variables=["grammar_correctness", "natural_usage", "suggestions"],
    partial_variables={"format_instructions": PydanticOutputParser(pydantic_object=SentenceEvaluation).get_format_instructions()},
)


class AIService:
    """AI service for word analysis and feedback using Gemini"""
    
    def __init__(self):
        """Initialize the AI service with Gemini API"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Define chains
        self.analysis_chain = analysis_prompt | self.model | PydanticOutputParser(pydantic_object=WordAnalysis)
        self.feedback_chain = feedback_prompt | self.model | PydanticOutputParser(pydantic_object=ExampleFeedback)
        self.evaluation_chain = evaluation_prompt | self.model | PydanticOutputParser(pydantic_object=SentenceEvaluation)
    
    async def analyze_word(self, word_phrase: str) -> Dict[str, Any]:
        """Analyzes a word by invoking the analysis_chain."""
        try:
            response = await self.analysis_chain.ainvoke({"word_phrase": word_phrase})
            return response.dict()
        except Exception as e:
            logger.error(f"Error in analysis_chain for '{word_phrase}': {e}")
            return {
                "classification": "unknown",
                "pronunciation": "",
                "meaning": "Error occurred during analysis",
                "difficulty_level": "intermediate"
            }
    
    async def provide_feedback(self, word_phrase: str, example_sentence: str) -> Dict[str, Any]:
        """Provides feedback by invoking the feedback_chain."""
        try:
            response = await self.feedback_chain.ainvoke({
                "word_phrase": word_phrase,
                "example_sentence": example_sentence
            })
            return response.dict()
        except Exception as e:
            logger.error(f"Error in feedback_chain for '{word_phrase}': {e}")
            return {
                "grammar_correctness": "Error occurred during analysis",
                "natural_usage": "Error occurred during analysis",
                "suggestions": "Unable to provide feedback at this time. Please try again later.",
                "alternative_examples": []
            }

    async def evaluate_sentence(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates sentence by invoking the evaluation_chain."""
        try:
            response = await self.evaluation_chain.ainvoke({
                "grammar_correctness": feedback.get("grammar_correctness", ""),
                "natural_usage": feedback.get("natural_usage", ""),
                "suggestions": feedback.get("suggestions", "")
            })
            return response.dict()
        except Exception as e:
            logger.error(f"Error in evaluation_chain: {e}")
            return {"evaluation": "error"}


# Global instance
ai_service = AIService()
