"""Reward calculator for reinforcement learning."""
from typing import Dict, Any
from app.models import Intelligence
import logging

logger = logging.getLogger(__name__)


class RewardCalculator:
    """Calculate rewards for RL agent based on session outcomes."""
    
    # Reward weights
    INTELLIGENCE_REWARD = 10.0  # Per intelligence item
    CONVERSATION_TURN_REWARD = 1.0  # Per turn
    SCAMMER_FRUSTRATION_REWARD = 20.0  # If scammer shows frustration
    COMPLETION_REWARD = 50.0  # Session completed with good intel
    TIME_PENALTY = -0.01  # Small penalty for very long responses
    
    @classmethod
    def calculate_reward(
        cls,
        intelligence_extracted: int,
        conversation_turns: int,
        scammer_message: str,
        session_completed: bool = False,
        intelligence_threshold: int = 5
    ) -> float:
        """
        Calculate reward for current action.
        
        Args:
            intelligence_extracted: Number of new intelligence items this turn
            conversation_turns: Total turns in conversation
            scammer_message: Latest scammer message (to detect frustration)
            session_completed: Whether session completed successfully
            intelligence_threshold: Min intelligence for completion bonus
            
        Returns:
            Reward value (can be negative)
        """
        reward = 0.0
        
        # 1. Intelligence extraction reward (main objective)
        reward += intelligence_extracted * cls.INTELLIGENCE_REWARD
        
        # 2. Conversation engagement reward
        reward += cls.CONVERSATION_TURN_REWARD
        
        # 3. Scammer frustration detection (good sign!)
        if cls._detect_frustration(scammer_message):
            reward += cls.SCAMMER_FRUSTRATION_REWARD
            logger.info(f"Scammer frustration detected! +{cls.SCAMMER_FRUSTRATION_REWARD} reward")
        
        # 4. Session completion bonus
        if session_completed and intelligence_extracted >= intelligence_threshold:
            reward += cls.COMPLETION_REWARD
            logger.info(f"Session completed successfully! +{cls.COMPLETION_REWARD} reward")
        
        # 5. Small time penalty for very long conversations with no progress
        if conversation_turns > 20 and intelligence_extracted == 0:
            reward += cls.TIME_PENALTY * (conversation_turns - 20)
        
        logger.debug(f"Calculated reward: {reward:.2f}")
        return reward
    
    @staticmethod
    def _detect_frustration(message: str) -> bool:
        """
        Detect if scammer is getting frustrated.
        
        Frustration indicators:
        - Repetition
        - Anger/threats
        - Giving up language
        """
        message_lower = message.lower()
        
        frustration_indicators = [
            # Repetition/urgency escalation
            'i told you', 'i said', 'listen', 'are you listening',
            
            # Anger
            'why you', 'what is your problem', 'stupid', 'idiot',
            
            # Giving up
            'forget it', 'never mind', 'waste of time', 'goodbye',
            
            # Increased threats
            'police will come', 'you will be arrested', 'your fault'
        ]
        
        return any(indicator in message_lower for indicator in frustration_indicators)
    
    @classmethod
    def calculate_session_success_score(
        cls,
        total_intelligence: int,
        total_turns: int,
        engagement_duration: int,
        scam_confirmed: bool
    ) -> float:
        """
        Calculate overall success score for a session (0-100).
        
        This is used for analytics and comparison.
        
        Args:
            total_intelligence: Total intelligence items extracted
            total_turns: Total conversation turns
            engagement_duration: Duration in seconds
            scam_confirmed: Whether scam was actually confirmed
            
        Returns:
            Success score (0-100)
        """
        score = 0.0
        
        # Intelligence component (40 points max)
        score += min(total_intelligence * 4, 40)
        
        # Engagement component (30 points max)
        score += min(total_turns * 1, 30)
        
        # Duration component (20 points max)
        score += min(engagement_duration / 30, 20)  # 10 min = 20 points
        
        # Confirmation bonus (10 points)
        if scam_confirmed:
            score += 10
        
        return min(score, 100.0)
