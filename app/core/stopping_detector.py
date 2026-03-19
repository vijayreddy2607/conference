"""Intelligent conversation stopping detection.

This module determines when the honeypot should stop engaging with a scammer
based on various intelligence signals:
- Sufficient intelligence extracted
- Scammer frustration/suspicion detected
- Conversation becoming unproductive
- Maximum engagement time/turns reached
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ConversationStoppingDetector:
    """Detects when conversation should intelligently stop."""
    
    # Frustration/suspicion indicators from scammer
    FRUSTRATION_PATTERNS = [
        r"(?i)(fake|fraud|scam|lie|lying|liar)",
        r"(?i)(waste.*time|wasting.*time)",
        r"(?i)(don'?t.*believe|not.*real|suspicious)",
        r"(?i)(police|report|complaint)",
        r"(?i)(block|blocked|blocking)",
        r"(?i)(stop.*messaging|don'?t.*message)",
        r"(?i)(who.*you|are.*you.*real)",
        r"(?i)(testing|honeypot|trap)",
    ]
    
    # Signs scammer is giving up
    GIVING_UP_PATTERNS = [
        r"(?i)(forget.*it|never.*mind)",
        r"(?i)(goodbye|bye|later)",
        r"(?i)(okay.*fine|fine.*okay)",
        r"(?i)(whatever|suit yourself)",
    ]
    
    # Very short/low effort responses (scammer losing interest)
    LOW_EFFORT_THRESHOLD = 10  # characters
    
    def __init__(
        self,
        max_turns: int = 25,
        min_intelligence_items: int = 5,
        frustration_threshold: int = 3,
        low_effort_streak: int = 5,
        min_turns_before_stopping: int = 8
    ):
        """
        Initialize stopping detector.
        
        Args:
            max_turns: Maximum conversation turns (default 25)
            min_intelligence_items: Minimum intelligence to call it "successful" (default 5)
            frustration_threshold: How many frustration signals before stopping (default 3)
            low_effort_streak: How many short responses in a row before stopping (default 5)
            min_turns_before_stopping: Hard minimum turns before stopping allowed (default 8)
        """
        self.max_turns = max_turns
        self.min_intelligence_items = min_intelligence_items
        self.frustration_threshold = frustration_threshold
        self.low_effort_streak = low_effort_streak
        self.min_turns_before_stopping = min_turns_before_stopping
    
    def should_stop(
        self,
        turn_count: int,
        intelligence_count: int,
        scammer_messages: List[str],
        engagement_duration_seconds: int,
        max_duration_seconds: int = 1800  # 30 minutes
    ) -> Dict[str, Any]:
        """
        Determine if conversation should stop.
        
        Args:
            turn_count: Current turn number
            intelligence_count: Number of intelligence items extracted
            scammer_messages: List of recent scammer messages (latest first)
            engagement_duration_seconds: How long conversation has been going
            max_duration_seconds: Maximum allowed duration
        
        Returns:
            Dict with:
                - should_stop: bool
                - reason: str (why stopping)
                - is_successful: bool (extracted enough intel)
                - confidence: float (0-1, how confident in stopping decision)
        """
        
        # CRITICAL FIX: Don't stop before minimum turn threshold
        # This ensures we engage scammer long enough for good intelligence extraction
        if turn_count < self.min_turns_before_stopping:
            return {
                "should_stop": False,
                "reason": "continue_min_turns_not_met",
                "is_successful": False,
                "confidence": 0.0
            }
        
        # Check max turns (hard limit)
        if turn_count >= self.max_turns:
            logger.info(f"🛑 Stopping: Max turns reached ({self.max_turns})")
            return {
                "should_stop": True,
                "reason": "max_turns_reached",
                "is_successful": intelligence_count >= self.min_intelligence_items,
                "confidence": 1.0
            }
        
        # Check max duration (hard limit)
        if engagement_duration_seconds >= max_duration_seconds:
            logger.info(f"🛑 Stopping: Max duration reached ({max_duration_seconds}s)")
            return {
                "should_stop": True,
                "reason": "max_duration_reached",
                "is_successful": intelligence_count >= self.min_intelligence_items,
                "confidence": 1.0
            }
        
        # Check if we have enough intelligence AND enough turns for good engagement
        # CRITICAL FIX: Increased from 3 to 5 items and from 10 to 12 turns
        if intelligence_count >= self.min_intelligence_items:
            # Good stopping point - mission accomplished!
            if turn_count >= 12:  # At least 12 turns for thorough intelligence extraction
                logger.info(f"✅ Stopping: Intelligence goal met ({intelligence_count} items) after {turn_count} turns")
                return {
                    "should_stop": True,
                    "reason": "intelligence_goal_met",
                    "is_successful": True,
                    "confidence": 0.9
                }
        
        # Analyze recent scammer messages for patterns
        if len(scammer_messages) >= 3:
            recent_msgs = scammer_messages[:5]  # Last 5 messages
            
            # Check for frustration/suspicion
            frustration_count = 0
            for msg in recent_msgs:
                for pattern in self.FRUSTRATION_PATTERNS:
                    if re.search(pattern, msg):
                        frustration_count += 1
                        break  # Count once per message
            
            # CRITICAL FIX: Frustration threshold increased from 2 to 3
            # This prevents false positives from scammer using word "police" etc.
            if frustration_count >= self.frustration_threshold:
                logger.info(f"😤 Stopping: Scammer showing frustration ({frustration_count} indicators)")
                return {
                    "should_stop": True,
                    "reason": "scammer_frustrated",
                    "is_successful": intelligence_count >= self.min_intelligence_items,
                    "confidence": 0.85
                }
            
            # Check for giving up signals
            for msg in recent_msgs[:2]:  # Just check last 2
                for pattern in self.GIVING_UP_PATTERNS:
                    if re.search(pattern, msg):
                        logger.info(f"👋 Stopping: Scammer giving up ('{msg[:50]}...')")
                        return {
                            "should_stop": True,
                            "reason": "scammer_giving_up",
                            "is_successful": intelligence_count >= self.min_intelligence_items,
                            "confidence": 0.8
                        }
            
            # Check for low-effort streak (scammer losing interest)
            low_effort_count = 0
            for msg in recent_msgs[:self.low_effort_streak]:
                if len(msg.strip()) <= self.LOW_EFFORT_THRESHOLD:
                    low_effort_count += 1
            
            # CRITICAL FIX: Low effort streak increased from 3 to 5
            # This prevents stopping when scammer sends occasional short responses
            if low_effort_count >= self.low_effort_streak:
                logger.info(f"💤 Stopping: Scammer showing low effort ({low_effort_count} short messages)")
                return {
                    "should_stop": True,
                    "reason": "low_effort_detected",
                    "is_successful": intelligence_count >= self.min_intelligence_items,
                    "confidence": 0.75
                }
        
        # High intelligence with reasonable engagement (soft stop)
        # CRITICAL FIX: Changed to 10+ items (was 6) for exceptional intelligence
        if intelligence_count >= 10 and turn_count >= 10:
            logger.info(f"🎯 Stopping: Exceptional intelligence extracted ({intelligence_count} items)")
            return {
                "should_stop": True,
                "reason": "exceptional_intelligence",
                "is_successful": True,
                "confidence": 0.95
            }
        
        # Continue conversation
        return {
            "should_stop": False,
            "reason": "continue",
            "is_successful": False,
            "confidence": 0.0
        }
    
    def get_stopping_message(self, reason: str, persona: str = "uncle") -> str:
        """
        Get appropriate final message based on stopping reason.
        
        Args:
            reason: Stopping reason from should_stop()
            persona: Which persona is engaged
        
        Returns:
            Final message string
        """
        
        # Frustrated scammer - polite exit
        if reason == "scammer_frustrated":
            messages = {
                "uncle": "Achha theek hai beta, I'm busy now. Talk later.",
                "aunty": "Okay ji okay, I have work to do. Bye bye.",
                "techsavvy": "Alright bro, I'll check later. Peace out.",
                "student": "Okay cool, gotta go study. Bye!",
                "worried": "Okay okay... I'll figure it out later. Thanks..."
            }
        
        # Giving up - understanding response
        elif reason == "scammer_giving_up":
            messages = {
                "uncle": "Okay beta, no problem. Take care.",
                "aunty": "Achha ji, thik hai. God bless.",
                "techsavvy": "Cool bro, no worries. Later!",
                "student": "Okay yaar, chill. Bye!",
                "worried": "Okay... thank you for telling me. Bye."
            }
        
        # Mission accomplished - satisfied exit
        elif reason in ["intelligence_goal_met", "exceptional_intelligence"]:
            messages = {
                "uncle": "Okay beta, I will think about this. Thanks for info.",
                "aunty": "Achha ji, let me check with my son first. Thank you beta.",
                "techsavvy": "Alright, got it. I'll research this more. Thanks.",
                "student": "Cool bro, I'll discuss with friends. Thanks!",
                "worried": "Okay... I'll be careful. Thank you for warning me."
            }
        
        # Max turns/duration - natural exit
        else:
            messages = {
                "uncle": "Beta, I'm getting tired now. Let's talk tomorrow.",
                "aunty": "Bas beta bas, too much talking. I rest now.",
                "techsavvy": "Yo, gotta bounce. We'll continue later.",
                "student": "Bro I gotta go, class starting. Bye!",
                "worried": "I... I need time to think. Talk later please."
            }
        
        return messages.get(persona, messages["uncle"])
