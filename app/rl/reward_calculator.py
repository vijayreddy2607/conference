"""Reward calculator for reinforcement learning."""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class RewardCalculator:
    """Calculate rewards for RL agent based on session outcomes."""

    # Reward weights
    INTELLIGENCE_REWARD = 10.0       # Per intelligence item extracted
    CONVERSATION_TURN_REWARD = 1.0   # Per turn (engagement reward)
    SCAMMER_CONFIDENCE_REWARD = 15.0 # Scammer feels in control — BIG BONUS
    SCAMMER_FRUSTRATION_PENALTY = -10.0  # Scammer frustrated — PENALTY
    COMPLETION_REWARD = 50.0         # Session completed with good intel
    TIME_PENALTY = -0.01             # Small penalty for very long unproductive convs

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

        OPTIMIZATION GOAL: Make scammer feel IN CONTROL while extracting intelligence.
        - High reward if scammer sounds confident/excited (thinks victim is convinced)
        - Penalty if scammer sounds frustrated/suspicious (might abandon)
        """
        reward = 0.0

        # 1. Intelligence extraction reward (main objective)
        reward += intelligence_extracted * cls.INTELLIGENCE_REWARD

        # 2. Conversation engagement reward
        reward += cls.CONVERSATION_TURN_REWARD

        # 3. Scammer confidence detection (BIG BONUS)
        confidence_score = cls._detect_scammer_confidence(scammer_message)
        if confidence_score >= 0.7:
            reward += cls.SCAMMER_CONFIDENCE_REWARD
            logger.info(f"✅ Scammer CONFIDENT (score={confidence_score:.2f})! +{cls.SCAMMER_CONFIDENCE_REWARD} reward")

        # 4. Scammer frustration detection (PENALTY)
        if cls._detect_frustration(scammer_message):
            reward += cls.SCAMMER_FRUSTRATION_PENALTY
            logger.warning(f"⚠️ Scammer FRUSTRATED! {cls.SCAMMER_FRUSTRATION_PENALTY} penalty")

        # 5. Session completion bonus
        if session_completed and intelligence_extracted >= intelligence_threshold:
            reward += cls.COMPLETION_REWARD
            logger.info(f"Session completed successfully! +{cls.COMPLETION_REWARD} reward")

        # 6. Small time penalty for very long conversations with no progress
        if conversation_turns > 20 and intelligence_extracted == 0:
            reward += cls.TIME_PENALTY * (conversation_turns - 20)

        logger.debug(f"Calculated reward: {reward:.2f}")
        return reward

    @staticmethod
    def _detect_scammer_confidence(message: str) -> float:
        """
        Detect scammer confidence level (0.0-1.0).
        HIGH CONFIDENCE (0.7-1.0) — Scammer thinks victim is convinced.
        """
        message_lower = message.lower()

        high_confidence_phrases = [
            'yes yes', 'very easy', 'simple process', 'trust me',
            "don't worry", 'no problem', 'safe', 'guaranteed',
            'just do', 'only take', 'quick', 'fast', 'easy way',
            'i will help', 'let me show', 'step by step'
        ]

        low_confidence_phrases = [
            'why you', 'are you going to', 'decide fast', 'yes or no',
            'stop asking', 'too many questions', "don't waste"
        ]

        high_matches = sum(1 for phrase in high_confidence_phrases if phrase in message_lower)
        low_matches = sum(1 for phrase in low_confidence_phrases if phrase in message_lower)
        message_length = len(message.split())

        if high_matches >= 2 or message_length > 30:
            return 0.9
        elif high_matches == 1:
            return 0.7
        elif low_matches >= 1:
            return 0.2
        elif message_length < 5:
            return 0.3
        else:
            return 0.5

    @staticmethod
    def _detect_frustration(message: str) -> bool:
        """Detect if scammer is getting frustrated (PENALTY trigger)."""
        message_lower = message.lower()
        frustration_indicators = [
            'i told you', 'i said', 'listen', 'are you listening',
            'why you', 'what is your problem', 'stupid', 'idiot',
            'forget it', 'never mind', 'waste of time', 'goodbye',
            'police will come', 'you will be arrested', 'your fault',
            'how long', 'hurry up', 'decide now', 'last chance'
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
        """Calculate overall success score for a session (0-100)."""
        score = 0.0
        score += min(total_intelligence * 4, 40)   # Intel component (40 pts max)
        score += min(total_turns * 1, 30)           # Engagement component (30 pts max)
        score += min(engagement_duration / 30, 20)  # Duration component (20 pts max)
        if scam_confirmed:
            score += 10                             # Confirmation bonus (10 pts)
        return min(score, 100.0)
