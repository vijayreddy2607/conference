"""
Scam Type Detector - Identifies scam category from message content.
Used to select appropriate persona (student, elderly, professional, etc.)
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ScamTypeDetector:
    """Detects scam type from message content to select appropriate persona."""

    SCAM_TYPE_PATTERNS = {
        "loan": [
            "loan", "instant approval", "processing fee", "credit score",
            "disburse", "loan officer", "KYC", "eligibility", "EMI",
            "लोन", r"instant.*lakh", r"approved.*minutes"
        ],
        "credit_card": [
            "credit card", "CVV", "card number", "fraud transaction",
            "suspicious activity", r"block.*card", r"card.*expir", r"card.*ending",
            "क्रेडिट कार्ड", "debit card", "ATM", r"verify.*card",
            r"card.*security", r"fraud.*dept"
        ],
        "job": [
            "selected", "work from home", "WFH", "registration fee",
            "joining", "HR", "interview", "employ", "salary", r"congratulations.*selected",
            "नौकरी", r"Amazon.*job", r"₹.*month", r"₹.*per month"
        ],
        "investment": [
            "returns", "profit", "crypto", "trading", "invest",
            r"guaranteed.*%", "fund", "stock", "forex", "bitcoin",
            "निवेश", "500%", r"earn.*crore"
        ],
        "digital_arrest": [
            "CBI", "police", "arrest", r"Aadhaar.*link", "illegal",
            r"money.*launder", r"case.*register", "court", "FIR",
            "गिरफ्तारी", "पुलिस", "jail", r"fine.*lakh"
        ],
        "delivery": [
            "delivery", "package", "courier", "redeliver", "parcel",
            r"Amazon.*package", "tracking", "shipment", "customs", r"delivery.*failed",
            "डिलीवरी", r"failed.*delivery", r"pay.*₹.*redeliver"
        ],
        "phishing": [
            r"KYC.*expir", r"update.*account", r"verify.*account",
            r"link.*click", r"blocked.*account", r"re-.*activ",
            "केवाईसी", "expire", "suspend"
        ],
        "upi_otp": [
            "OTP", "UPI", r"account.*block", r"verify.*identit",
            "PIN", "transfer", "payment", "transaction",
            "ओटीपी", "यूपीआई", r"urgent.*account"
        ],
        "bank_kyc": [
            "SBI", "HDFC", "ICICI", "bank", r"KYC.*update", r"account.*freeze",
            r"net.*banking", "branch", r"debit.*card", r"banking.*block"
        ],
        "prize_lottery": [
            "lottery", "prize", "winner", "won", r"cash.*prize",
            r"lucky.*draw", r"select.*winner", "congratulations", "reward",
            "लॉटरी", r"₹.*lakh.*won"
        ],
    }

    def detect(self, text: str) -> str:
        """
        Detect scam type from message text.

        Args:
            text: Message content to analyze

        Returns:
            Scam type string or "generic" if unknown
        """
        text_lower = text.lower()
        scores = {}
        for scam_type, keywords in self.SCAM_TYPE_PATTERNS.items():
            score = 0
            for keyword in keywords:
                if re.search(keyword, text_lower):
                    score += 1
            if score > 0:
                scores[scam_type] = score

        if not scores:
            return "generic"

        detected = max(scores, key=scores.get)
        logger.info(f"[ScamTypeDetector] Detected: '{detected}' (scores: {scores})")
        return detected

    def detect_with_confidence(self, text: str) -> dict:
        """Returns scam type with confidence score."""
        text_lower = text.lower()
        scores = {}
        for scam_type, keywords in self.SCAM_TYPE_PATTERNS.items():
            score = 0
            total = len(keywords)
            for keyword in keywords:
                if re.search(keyword, text_lower):
                    score += 1
            if score > 0:
                scores[scam_type] = {"count": score, "confidence": score / total}

        if not scores:
            return {"type": "generic", "confidence": 0.0}

        best = max(scores, key=lambda k: scores[k]["count"])
        return {
            "type": best,
            "confidence": scores[best]["confidence"],
            "all_scores": scores
        }


# Global instance
scam_type_detector = ScamTypeDetector()
