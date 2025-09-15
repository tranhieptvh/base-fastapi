from pydantic import BaseModel
from typing import Optional, Dict, Any

class LearningFlowRequest(BaseModel):
    word_phrase: str
    example_sentence: str
    
    # The state is optional because the first request won't have it.
    # In subsequent requests (e.g., trying a new sentence after feedback),
    # the frontend would pass the state it received from the previous response.
    # For this implementation, we are keeping it simple and not requiring the full state from the client.
    # current_state: Optional[Dict[str, Any]] = None
