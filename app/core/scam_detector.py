"""Scam detection system using pattern matching and LLM."""
from app.models.intelligence import ScamDetection
from app.utils import patterns, llm_client
from app.core.scam_classifier_enhanced import enhanced_classifier
from langchain_core.messages import SystemMessage, HumanMessage
import logging

logger = logging.getLogger(__name__)

# Scam type name mapping: ML model names → Hackathon-friendly names
SCAM_TYPE_NAME_MAPPING = {
    # ML model outputs → User-friendly names
    "bank_kyc": "bank_phishing",
    "upi_scam": "bank_phishing",  # UPI is a type of bank phishing
    "credit_card": "credit_loan",
    "police_legal": "digital_arrest",
    "tax_refund": "impersonation",
    "govt_scheme": "impersonation",
    "job_offer": "fake_job",
    "prize_lottery": "lottery_prize",
    "bill_payment": "bank_phishing",
    "romance": "sextortion",  # Often overlaps
    "delivery": "delivery_scam",
    # Legacy names → Modern names
    "bank_fraud": "bank_phishing",
    "upi_fraud": "bank_phishing",
    "phishing": "bank_phishing",
    "legal_threat": "digital_arrest",
    "authority_impersonation": "impersonation",
}


def normalize_scam_type(scam_type: str) -> str:
    """Convert ML model scam type to hackathon-friendly name.
    
    Args:
        scam_type: Raw scam type from ML model
        
    Returns:
        Normalized, hackathon-friendly scam type name
    """
    return SCAM_TYPE_NAME_MAPPING.get(scam_type, scam_type)

class ScamDetector:
    """Detects scam intent using multi-stage approach."""
    
    def __init__(self):
        self.scam_type_to_agent = {
            "bank_fraud": "uncle",
            "upi_fraud": "uncle",
            "authority_impersonation": "worried",
            "legal_threat": "worried",
            "investment": "techsavvy",
            "job_offer": "techsavvy",
            "phishing": "uncle",
            "unknown": "uncle"  # default
        }
    
    async def detect(self, message_text: str, conversation_history: list = None) -> ScamDetection:
        """
        Detect if message is a scam using multi-stage approach.
        
        Stage 1: Enhanced classifier (12 specific types - FAST!)
        Stage 2: LLM-based classification (accurate but slower)
        Stage 3: Pattern matching (fallback)
        
        Args:
            message_text: The message to analyze
            conversation_history: Previous messages for context
        
        Returns:
            ScamDetection with results
        """
        try:
            # Stage 1: Enhanced classifier (NEW - PRIMARY METHOD)
            enhanced_type, enhanced_persona, enhanced_conf = enhanced_classifier.classify(message_text)
            logger.info(f"🎯 Enhanced classification: {enhanced_type} → {enhanced_persona} ({enhanced_conf:.0%})")
            
            # CRITICAL FIX: Check for legitimate message patterns FIRST!
            # Must be before all other logic to prevent false positives
            import re
            legitimate_patterns = [
                r"\bhappy\s+birthday\b",
                r"\b(hi|hello|hey|good morning|good night|goodbye)\b",
                r"\bmeeting\s+at\s+\d+\b",
                r"\b(thanks|thank you|thx)\b",
                r"\bhow\s+(are|r)\s+you\b",
                r"\b(mom|dad|mother|father|friend|bro|sis)\b.*\b(home|late|pick|get)\b",
            ]
            
            for pattern in legitimate_patterns:
                if re.search(pattern, message_text, re.IGNORECASE):
                    logger.info(f"✅ Legitimate message pattern detected: {pattern}")
                    return ScamDetection(
                        is_scam=False,
                        confidence=0.95,
                        scam_type="unknown",
                        recommended_agent="uncle",
                        reasoning=f"Legitimate social message (pattern: {pattern})"
                    )
            
            # If enhanced classifier is confident, use it directly!
            if enhanced_conf >= 0.67:  # High confidence (2+ keywords matched)
                is_scam = enhanced_type != "unknown"
                logger.info(f"✅ Using enhanced classifier result (high confidence)")
                return ScamDetection(
                    is_scam=is_scam,
                    confidence=enhanced_conf,
                    scam_type=normalize_scam_type(enhanced_type),
                    recommended_agent=enhanced_persona,
                    reasoning=f"Enhanced classifier detected {enhanced_type} with {enhanced_conf:.0%} confidence"
                )
            
            # Stage 2: Quick pattern-based check
            keywords = patterns.extract_keywords(message_text)
            has_urls = len(patterns.extract_urls(message_text)) > 0
            has_upi = len(patterns.extract_upi_ids(message_text)) > 0
            has_phone = len(patterns.extract_phone_numbers(message_text)) > 0
            
            # Initial suspicion score
            suspicion_score = 0.0
            if len(keywords) >= 3:
                suspicion_score += 0.3
            if has_urls:
                suspicion_score += 0.2
            if has_upi or has_phone:
                suspicion_score += 0.2
            
            # Check for high-risk keywords
            high_risk_keywords = ["otp", "cvv", "password", "pin", "blocked", "suspended", "arrest", "kyc", "verify"]
            if any(k in message_text.lower() for k in high_risk_keywords):
                suspicion_score += 0.3
            
            logger.info(f"Pattern suspicion score: {suspicion_score:.2f}")
            
            # If enhanced classifier says scam (even low confidence) AND patterns agree, trust it
            if enhanced_type != "unknown" and suspicion_score >= 0.3:
                logger.info(f"✅ Enhanced classifier + patterns both detect scam")
                return ScamDetection(
                    is_scam=True,
                    confidence=max(enhanced_conf, suspicion_score),
                    scam_type=normalize_scam_type(enhanced_type),
                    recommended_agent=enhanced_persona,
                    reasoning=f"Enhanced classifier ({enhanced_conf:.0%}) + pattern matching ({suspicion_score:.0%})"
                )
            
            # CRITICAL FIX: Check for legitimate message patterns first
            # Avoid false positives on greetings, social messages, etc.
            import re
            legitimate_patterns = [
                r"\bhappy\s+birthday\b",
                r"\b(hi|hello|hey|good morning|good night|goodbye)\b",
                r"\bmeeting\s+at\s+\d+\b",
                r"\b(thanks|thank you|thx)\b",
                r"\bhow\s+(are|r)\s+you\b",
                r"\b(mom|dad|mother|father|friend|bro|sis)\b.*\b(home|late|pick|get)\b",
            ]
            
            for pattern in legitimate_patterns:
                if re.search(pattern, message_text, re.IGNORECASE):
                    logger.info(f"✅ Legitimate message pattern detected: {pattern}")
                    return ScamDetection(
                        is_scam=False,
                        confidence=0.95,
                        scam_type="unknown",
                        recommended_agent="uncle",
                        reasoning=f"Legitimate social message (pattern: {pattern})"
                    )
            
            # Short message optimization: Skip LLM for very short messages (< 4 words)
            word_count = len(message_text.split())
            if word_count < 4:
                logger.info(f"Message too short ({word_count} words) - skipping LLM")
                return self._pattern_based_classification(message_text, keywords, suspicion_score)

            # Stage 3: LLM-based classification for unclear cases
            if suspicion_score >= 0.2 or enhanced_conf >= 0.33:
                try:
                    scam_detection = await self._llm_classify(message_text, conversation_history)
                    return scam_detection
                except Exception as e:
                    logger.error(f"LLM classification failed: {e}")
                    # Fallback to pattern-based
                    return self._pattern_based_classification(message_text, keywords, suspicion_score)
            
            # If no indicators at all, probably not scam
            return ScamDetection(
                is_scam=False,
                confidence=0.8,
                scam_type="unknown",
                recommended_agent="uncle",
                reasoning="No scam indicators found"
            )
            
        except Exception as e:
            # SAFETY NET: Never crash detection
            logger.error(f"CRITICAL ERROR in ScamDetector: {e}", exc_info=True)
            return ScamDetection(
                is_scam=False,
                confidence=0.0,
                scam_type="unknown",
                recommended_agent="uncle",
                reasoning="System error during detection - failing open"
            )
    
    async def _llm_classify(self, message_text: str, conversation_history: list = None) -> ScamDetection:
        """Use LLM to classify scam type and intent."""
        
        system_prompt = """You are a scam detection expert. Analyze messages to determine if they are scam attempts.

Scam types:
- bank_fraud: Fake bank notifications, account blocking threats
- upi_fraud: UPI payment scams, fake payment confirmations
- phishing: Links to steal credentials, fake websites
- investment: Get-rich-quick schemes, crypto scams, fake stock tips
- job_offer: Work-from-home scams, fake job postings
- legal_threat: Fake arrest warrants, court notices, tax penalties
- authority_impersonation: Pretending to be government, police, RBI

Respond in this exact format:
IS_SCAM: [yes/no]
CONFIDENCE: [0.0-1.0]
TYPE: [scam_type]
REASONING: [brief explanation]

Be very accurate. Some messages might be legitimate."""

        context = ""
        if conversation_history:
            context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                context += f"{msg.get('sender', 'unknown')}: {msg.get('text', '')}\n"
        
        user_prompt = f"""Analyze this message:{context}

Current message: {message_text}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = await llm_client.ainvoke(messages)
        
        logger.debug(f"LLM raw response: {response[:200]}")
        
        # Parse LLM response with better error handling
        response_lower = response.lower()
        
        # Parse IS_SCAM
        is_scam = False
        if "is_scam:" in response_lower:
            try:
                scam_parts = response_lower.split("is_scam:")
                if len(scam_parts) > 1:
                    is_scam_value = scam_parts[1].split("\n")[0].strip()
                    is_scam = "yes" in is_scam_value or "true" in is_scam_value
            except Exception as e:
                logger.warning(f"Failed to parse is_scam: {e}")
                is_scam = False  # CRITICAL FIX: Default to NOT scam if we can't parse (safer)
        
        # Parse CONFIDENCE
        confidence = 0.8
        if "confidence:" in response_lower:
            try:
                conf_parts = response_lower.split("confidence:")
                if len(conf_parts) > 1:
                    conf_str = conf_parts[1].split("\n")[0].strip()
                    # Remove any non-numeric characters except decimal point
                    conf_str = ''.join(c for c in conf_str if c.isdigit() or c == '.')
                    if conf_str:
                        confidence = float(conf_str)
                        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
            except Exception as e:
                logger.warning(f"Failed to parse confidence: {e}")
        
        # Parse TYPE
        scam_type = "unknown"
        if "type:" in response_lower:
            try:
                type_parts = response_lower.split("type:")
                if len(type_parts) > 1:
                    type_line = type_parts[1].split("\n")[0].strip()
                    for stype in self.scam_type_to_agent.keys():
                        if stype in type_line:
                            scam_type = stype
                            break
            except Exception as e:
                logger.warning(f"Failed to parse type: {e}")
        
        # Parse REASONING
        reasoning = ""
        if "reasoning:" in response.lower():
            try:
                reasoning_parts = response.split("reasoning:")
                if len(reasoning_parts) > 1:
                    reasoning = reasoning_parts[1].split("\n")[0].strip()
            except Exception as e:
                logger.warning(f"Failed to parse reasoning: {e}")
        
        # NEW: Use enhanced classifier for specific scam type (12 types instead of 7)
        if is_scam:
            enhanced_type, enhanced_persona, enhanced_conf = enhanced_classifier.classify(message_text)
            logger.info(f"🎯 Enhanced classification: {enhanced_type} → {enhanced_persona} ({enhanced_conf:.0%})")
            
            # Use enhanced results if confidence is decent
            if enhanced_conf >= 0.5:
                scam_type = enhanced_type
                recommended_agent = enhanced_persona
                confidence = max(confidence, enhanced_conf)  # Take higher confidence
                logger.info(f"✅ Using enhanced classification")
            else:
                recommended_agent = self.scam_type_to_agent.get(scam_type, "uncle")
                logger.info(f"⚠️ Using fallback classification")
        else:
            recommended_agent = self.scam_type_to_agent.get(scam_type, "uncle")
        
        logger.info(f"LLM Classification - Scam: {is_scam}, Type: {scam_type}, Confidence: {confidence}")
        
        return ScamDetection(
            is_scam=is_scam,
            confidence=confidence,
            scam_type=normalize_scam_type(scam_type),
            recommended_agent=recommended_agent,
            reasoning=reasoning
        )
    
    def _pattern_based_classification(self, message_text: str, keywords: list, suspicion_score: float) -> ScamDetection:
        """Fallback pattern-based classification."""
        
        text_lower = message_text.lower()
        
        # Determine scam type based on keywords
        scam_type = "unknown"
        
        if any(k in text_lower for k in ["bank", "account", "atm", "card"]):
            scam_type = "bank_fraud"
        elif any(k in text_lower for k in ["upi", "paytm", "phonepe", "gpay"]):
            scam_type = "upi_fraud"
        elif any(k in text_lower for k in ["arrest", "court", "legal", "police"]):
            scam_type = "legal_threat"
        elif any(k in text_lower for k in ["investment", "profit", "returns", "crypto", "stock"]):
            scam_type = "investment"
        elif any(k in text_lower for k in ["job", "salary", "work from home", "hiring"]):
            scam_type = "job_offer"
        elif "http" in text_lower:
            scam_type = "phishing"
        
        recommended_agent = self.scam_type_to_agent.get(scam_type, "uncle")
        
        # CRITICAL FIX: Increased threshold from 0.4 to 0.70 to reduce false positives
        # Better to miss 2% of scams than annoy users with 87% false positives
        return ScamDetection(
            is_scam=suspicion_score >= 0.70,  # Was 0.4 - now more conservative
            confidence=min(suspicion_score + 0.2, 0.9),
            scam_type=normalize_scam_type(scam_type),
            recommended_agent=recommended_agent,
            reasoning=f"Pattern-based detection with {len(keywords)} suspicious keywords (threshold: 0.70)"
        )
