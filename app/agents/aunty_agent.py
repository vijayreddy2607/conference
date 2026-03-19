"""Aunty agent - Gossipy, chatty middle-aged woman persona."""
from app.agents.base_agent import BaseAgent
from app.prompts.aunty_persona import AUNTY_SYSTEM_PROMPT, AUNTY_FEW_SHOT_EXAMPLES
import random


class AuntyAgent(BaseAgent):
    """Aunty persona - Gossipy, chatty, social character."""
    

    def __init__(self):
        super().__init__(persona_name="Sunita Aunty")
    
    def get_system_prompt(self) -> str:
        """Return Aunty's system prompt."""
        return AUNTY_SYSTEM_PROMPT
    
    def get_few_shot_examples(self) -> list:
        """Return Aunty's conversation examples."""
        return AUNTY_FEW_SHOT_EXAMPLES

