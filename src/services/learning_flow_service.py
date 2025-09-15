from typing import TypedDict
from langgraph.graph import StateGraph, END
import logging
from src.services.ai_service import ai_service

logger = logging.getLogger(__name__)

# --- Graph State ---
class LearningGraphState(TypedDict):
    """
    Represents the state of our learning graph.
    """
    word_phrase: str
    analysis_result: dict
    example_sentence: str
    feedback_result: dict
    evaluation_result: str # "good" or "needs_improvement"
    error: str


# --- Graph Nodes ---
async def analyze_word(state: LearningGraphState):
    """
    Analyzes the user's word or phrase.
    """
    logger.info(f"---ANALYZING WORD: {state['word_phrase']}---")
    try:
        result = await ai_service.analyze_word(state['word_phrase'])
        return {"analysis_result": result}
    except Exception as e:
        logger.error(f"Error in analyze_word node: {e}")
        return {"error": "Failed to analyze the word."}

async def provide_feedback(state: LearningGraphState):
    """
    Provides feedback on the user's example sentence.
    """
    logger.info(f"---PROVIDING FEEDBACK FOR: {state['example_sentence']}---")
    try:
        result = await ai_service.provide_feedback(state['word_phrase'], state['example_sentence'])
        return {"feedback_result": result}
    except Exception as e:
        logger.error(f"Error in provide_feedback node: {e}")
        return {"error": "Failed to provide feedback."}

async def evaluate_sentence(state: LearningGraphState):
    """
    Evaluates the sentence quality by calling the centralized AIService.
    """
    logger.info("---EVALUATING SENTENCE---")
    try:
        feedback = state['feedback_result']
        evaluation_response = await ai_service.evaluate_sentence(feedback)
        
        logger.info(f"---EVALUATION RESULT: {evaluation_response['evaluation']}---")
        return {"evaluation_result": evaluation_response['evaluation']}

    except Exception as e:
        logger.error(f"Error in evaluate_sentence node: {e}")
        return {"error": "Failed to evaluate the sentence."}


class LearningFlowService:
    def __init__(self):
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(LearningGraphState)

        # Add nodes
        workflow.add_node("analyze_word", analyze_word)
        workflow.add_node("provide_feedback", provide_feedback)
        workflow.add_node("evaluate_sentence", evaluate_sentence)

        # Set entry and edges for a linear flow
        workflow.set_entry_point("analyze_word")
        workflow.add_edge("analyze_word", "provide_feedback")
        workflow.add_edge("provide_feedback", "evaluate_sentence")
        workflow.add_edge("evaluate_sentence", END) # Always end after evaluation
        
        return workflow.compile()

    async def run(self, initial_state: dict):
        """
        Runs the learning flow graph.
        """
        return await self.workflow.ainvoke(initial_state)

# Global instance
learning_flow_service = LearningFlowService()
