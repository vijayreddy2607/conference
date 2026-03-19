"""Conversation relevance detector - detects if scammer is still engaged or conversation has gone off-topic."""
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ConversationRelevanceDetector:
    """Detects if conversation is still relevant or has gone off-topic."""
    
    # Keywords for different scam types
    SCAM_TYPE_KEYWORDS = {
        "bank_phishing": ["bank", "account", "atm", "card", "kyc", "block", "verify", "update", "otp", "cvv", "pin"],
        "fake_delivery": ["delivery", "parcel", "package", "courier", "shipping", "address", "rto", "customs", "fedex", "dhl", "dtdc"],
        "digital_arrest": ["police", "arrest", "court", "case", "fir", "crime", "investigation", "officer", "legal", "warrant"],
        "credit_loan": ["loan", "credit", "emi", "interest", "approve", "sanction", "disburs", "cibil", "score", "eligible"],
        "lottery_prize": ["lottery", "prize", "winner", "congratulation", "claim", "lucky", "draw", "reward", "won", "jackpot"],
        "fake_job": ["job", "work", "hire", "salary", "company", "interview", "resume", "position", "employ", "recruitment"],
        "investment": ["invest", "profit", "return", "trading", "stock", "crypto", "bitcoin", "forex", "scheme", "earn"],
        "sextortion": ["video", "photo", "expose", "leak", "share", "contact", "embarrass", "family", "friends", "social"],
        "impersonation": ["officer", "government", "official", "department", "authority", "tax", "income", "refund", "penalty"],
        "marketplace_scam": ["olx", "quikr", "buy", "sell", "payment", "advance", "product", "interested", "buyer", "seller"]
    }
    
    # Generic engagement keywords
    ENGAGEMENT_KEYWORDS = ["yes", "ok", "okay", "sure", "tell", "how", "what", "when", "where", "why", "explain", 
                          "interested", "want", "need", "help", "please", "details", "information"]
    
    # Low engagement signals
    LOW_ENGAGEMENT_SIGNALS = ["k", "hmm", "hmmm", "ok ok", "yes yes", "haan", "achha", "thik", "bye", "later", "busy"]
    
    def is_conversation_relevant(
        self,
        scammer_messages: List[str],
        scam_type: str,
        min_messages: int = 3
    ) -> Dict:
        """
        Detect if conversation is still relevant and scammer is engaged.
        
        Args:
            scammer_messages: List of recent scammer messages (in chronological order)
            scam_type: Type of scam detected
            min_messages: Minimum messages to analyze (default: 3)
        
        Returns:
            {
                "is_relevant": bool,
                "confidence": float (0.0 to 1.0),
                "reason": str,
                "engagement_level": str  ("high", "medium", "low")
            }
        """
        # Need at least min_messages messages to analyze
        if len(scammer_messages) < min_messages:
            return {
                "is_relevant": True,
                "confidence": 1.0,
                "reason": "Too few messages to determine relevance",
                "engagement_level": "unknown"
            }
        
        # Analyze last 3-4 messages
        recent_messages = scammer_messages[-4:]
        
        # Check 1: Are scammer messages too short/generic?
        avg_length = sum(len(msg) for msg in recent_messages) / len(recent_messages)
        if avg_length < 10:
            logger.info(f"⚠️ Low engagement detected: Average message length too short ({avg_length:.1f} chars)")
            return {
                "is_relevant": False,
                "confidence": 0.8,
                "reason": "Scammer messages are very short and non-committal",
                "engagement_level": "low"
            }
        
        # Check 2: Contains scam-relevant keywords?
        scam_keywords = self.SCAM_TYPE_KEYWORDS.get(scam_type, [])
        
        keyword_matches = 0
        for msg in recent_messages:
            msg_lower = msg.lower()
            for keyword in scam_keywords:
                if keyword in msg_lower:
                    keyword_matches += 1
                    break  # Count each message only once
        
        keyword_relevance_ratio = keyword_matches / len(recent_messages)
        
        # Check 3: Contains generic engagement keywords?
        engagement_count = 0
        for msg in recent_messages:
            msg_lower = msg.lower()
            for keyword in self.ENGAGEMENT_KEYWORDS:
                if keyword in msg_lower:
                    engagement_count += 1
                    break
        
        # Check 4: Contains low engagement signals?
        low_engagement_count = 0
        for msg in recent_messages:
            msg_lower = msg.lower().strip()
            for signal in self.LOW_ENGAGEMENT_SIGNALS:
                if msg_lower == signal or msg_lower.startswith(signal + " "):
                    low_engagement_count += 1
                    break
        
        # DECISION LOGIC
        
        # If >50% of messages are low engagement → NOT relevant
        if low_engagement_count / len(recent_messages) > 0.5:
            logger.info(f"🚫 Off-topic: {low_engagement_count}/{len(recent_messages)} messages show low engagement")
            return {
                "is_relevant": False,
                "confidence": 0.9,
                "reason": f"Scammer showing low engagement ({low_engagement_count}/{len(recent_messages)} generic responses)",
                "engagement_level": "low"
            }
        
        # If scam keywords present → relevant
        if keyword_relevance_ratio > 0.33:  # At least 1 in 3 messages has scam keywords
            logger.info(f"✅ Relevant: {keyword_matches}/{len(recent_messages)} messages contain scam keywords")
            return {
                "is_relevant": True,
                "confidence": 0.7 + (keyword_relevance_ratio * 0.3),
                "reason": f"Scammer still discussing {scam_type} topic",
                "engagement_level": "high"
            }
        
        # If engagement keywords present → medium relevance
        if engagement_count > 0:
            logger.info(f"⚠️ Medium: {engagement_count}/{len(recent_messages)} messages show engagement")
            return {
                "is_relevant": True,
                "confidence": 0.6,
                "reason": "Scammer still engaged but topic may be drifting",
                "engagement_level": "medium"
            }
        
        # Default: Topic has drifted
        logger.info(f"🚫 Off-topic: No scam keywords or engagement signals in recent {len(recent_messages)} messages")
        return {
            "is_relevant": False,
            "confidence": 0.7,
            "reason": "Conversation topic has drifted from original scam",
            "engagement_level": "low"
        }
    
    def should_end_conversation(
        self,
        scammer_messages: List[str],
        scam_type: str,
        turn_count: int,
        min_turn_threshold: int = 6
    ) -> Dict:
        """
        Determine if conversation should be ended based on relevance.
        
        Args:
            scammer_messages: List of all scammer messages
            scam_type: Type of scam
            turn_count: Current turn number
            min_turn_threshold: Minimum turns before checking relevance (default: 6)
        
        Returns:
            {
                "should_end": bool,
                "reason": str,
                "sentiment": str ("graceful", "frustrated", "neutral")
            }
        """
        # Don't end too early
        if turn_count < min_turn_threshold:
            return {
                "should_end": False,
                "reason": f"Turn {turn_count} < minimum threshold {min_turn_threshold}",
                "sentiment": "neutral"
            }
        
        # Check relevance
        relevance = self.is_conversation_relevant(scammer_messages, scam_type)
        
        if not relevance["is_relevant"] and relevance["confidence"] > 0.7:
            # End conversation
            logger.info(f"🛑 Ending conversation: {relevance['reason']}")
            
            # Choose sentiment based on engagement level
            if relevance["engagement_level"] == "low":
                sentiment = "frustrated"
            else:
                sentiment = "graceful"
            
            return {
                "should_end": True,
                "reason": relevance["reason"],
                "sentiment": sentiment
            }
        
        # Continue conversation
        return {
            "should_end": False,
            "reason": f"Conversation still relevant (confidence: {relevance['confidence']:.2f})",
            "sentiment": "neutral"
        }
    
    def get_ending_message(self, persona: str, sentiment: str = "graceful") -> str:
        """
        Get appropriate ending message based on persona and sentiment.
        
        Args:
            persona: Agent persona type
            sentiment: "graceful", "frustrated", or "neutral"
        
        Returns:
            Ending message string
        """
        endings = {
            "uncle": {
                "graceful": "Beta, I think there is some confusion. I am not interested right now. Thank you for calling. Bye.",
                "frustrated": "Arre, you are wasting my time! I am busy with other work. Don't call again!",
                "neutral": "OK beta, I will think about it. You don't call me, I will call you if needed."
            },
            "aunty": {
                "graceful": "Beta, I think I will ask my husband first. Thank you for the information. Bye bye!",
                "frustrated": "Hayy! Too much talking! I am very busy with cooking. Don't disturb me again!",
                "neutral": "OK OK, let me check with family. I will let you know later beta."
            },
            "student": {
                "graceful": "Bro, I'll think about it and get back to you. Thanks for the info!",
                "frustrated": "Dude, this doesn't sound right. I'm not interested anymore. Peace out.",
                "neutral": "Okay man, let me check with my friends first. I'll call you if I'm interested."
            },
            "techsavvy": {
                "graceful": "I need to do more research on this. I'll reach out if I'm interested. Thanks.",
                "frustrated": "This doesn't pass my verification checks. Not interested. Please don't contact me again.",
                "neutral": "Let me verify this independently. I'll get in touch if needed."
            },
            "worried": {
                "graceful": "I... I need to talk to my family first. This is too much stress. Goodbye.",
                "frustrated": "Stop calling me! You're making me very anxious! I don't want any of this!",
                "neutral": "I'm too confused right now. Let me calm down first. I'll contact you later if needed."
            }
        }
        
        return endings.get(persona, {}).get(sentiment, "I'm not interested. Goodbye.")


# Global instance
relevance_detector = ConversationRelevanceDetector()
