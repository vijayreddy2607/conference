"""Student agent - Young, tech-aware but naive persona."""
from app.agents.base_agent import BaseAgent
from app.prompts.student_persona import (
    STUDENT_SYSTEM_PROMPT, 
    STUDENT_FEW_SHOT_EXAMPLES
)
import logging

logger = logging.getLogger(__name__)


class StudentAgent(BaseAgent):
    """Student persona - Naive college student targeted by youth scams.
    
    Features:
    - Natural Hinglish with slang, emojis, typos
    - Uses centralized fallback templates via Orchestrator
    """
    
    def __init__(self):
        super().__init__(persona_name="Arjun (Student)")
    
    def get_system_prompt(self) -> str:
        """Return Student's enhanced system prompt."""
        return STUDENT_SYSTEM_PROMPT
    
    def get_few_shot_examples(self) -> list:
        """Return Student's conversation examples."""
        return STUDENT_FEW_SHOT_EXAMPLES

