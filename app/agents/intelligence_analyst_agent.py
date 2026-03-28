"""
Intelligence Analyst Agent — dedicated sub-agent for real-time intelligence extraction.

Runs in parallel with the persona agent on every turn. Analyzes scammer messages
for extractable intelligence and produces a structured INTELLIGENCE_LOG.

Responsibilities:
1. Extract UPI IDs, phone numbers, bank accounts, phishing links, emails, names
2. Use regex patterns (fast) + keyword detection
3. Produce a structured INTELLIGENCE_LOG dict every turn
4. Identify what the scammer is asking for (OTP, Aadhaar, PAN, etc.)
5. Suggest what fake data to provide if scammer asks for personal info
"""
import logging
import re
from typing import Dict, List, Optional, Any
from app.utils import patterns
from app.utils.dummy_data_generator import DummyDataGenerator

logger = logging.getLogger(__name__)


class IntelligenceAnalystAgent:
    """
    Dedicated intelligence extraction sub-agent.

    Runs alongside the persona agent to analyze every scammer message
    and produce structured intelligence logs.
    """

    # Keywords that indicate scammer is asking for personal data
    PERSONAL_DATA_REQUESTS = {
        "otp": ["otp", "one time password", "verification code", "code bhejo", "code send"],
        "aadhaar": ["aadhaar", "aadhar", "uid number", "aadhaar number"],
        "pan": ["pan card", "pan number", "permanent account number"],
        "bank_account": ["account number", "bank account", "acc number", "account no"],
        "upi": ["upi id", "gpay id", "phonepe id", "paytm id", "send to upi"],
        "cvv": ["cvv", "card verification", "3 digit", "back of card"],
        "pin": ["atm pin", "debit pin", "net banking pin", "mpin"],
        "password": ["password", "login password", "net banking password"],
    }

    # Scammer tactics to identify
    SCAMMER_TACTICS = {
        "urgency": ["immediately", "urgent", "asap", "right now", "within minutes", "deadline", "expires"],
        "threat": ["arrest", "block", "freeze", "legal action", "police", "court", "fir"],
        "authority": ["rbi", "cbi", "police", "government", "bank manager", "officer", "department"],
        "reward": ["won", "prize", "lottery", "congratulations", "selected", "reward", "cashback"],
        "fear": ["compromised", "hacked", "suspicious", "fraud detected", "unauthorized"],
    }

    def __init__(self):
        self.dummy_generator = DummyDataGenerator()

    def analyze_regex(self, message: str) -> Dict[str, List[str]]:
        """Fast regex-based extraction. Returns dict with all extracted items."""
        extracted = {
            "upi_ids": list(patterns.extract_upi_ids(message)),
            "phone_numbers": list(patterns.extract_phone_numbers(message)),
            "bank_accounts": list(patterns.extract_bank_accounts(message)),
            "urls": list(patterns.extract_urls(message)),
            "emails": list(patterns.extract_emails(message)),
            "names": list(patterns.extract_names(message)),
            "employee_ids": list(patterns.extract_employee_ids(message)),
        }
        # Also extract extended fields if available
        if hasattr(patterns, 'extract_case_ids'):
            extracted["case_ids"] = list(patterns.extract_case_ids(message))
        if hasattr(patterns, 'extract_addresses'):
            extracted["addresses"] = list(patterns.extract_addresses(message))
        return extracted

    def detect_data_requests(self, message: str) -> List[str]:
        """Detect what personal data the scammer is requesting."""
        message_lower = message.lower()
        requested = []
        for data_type, keywords in self.PERSONAL_DATA_REQUESTS.items():
            if any(kw in message_lower for kw in keywords):
                requested.append(data_type)
        return requested

    def detect_tactics(self, message: str) -> List[str]:
        """Detect which psychological tactics the scammer is using."""
        message_lower = message.lower()
        detected = []
        for tactic, keywords in self.SCAMMER_TACTICS.items():
            if any(kw in message_lower for kw in keywords):
                detected.append(tactic)
        return detected

    def get_fake_data_suggestion(self, data_requests: List[str]) -> Dict[str, Any]:
        """
        Suggest fake data to provide back if scammer is asking for personal info.
        NEVER suggests OTP — that always redirects to extraction.
        """
        suggestions = {}
        for request in data_requests:
            result = self.dummy_generator.get_response_for_request(request)
            if result["type"] != "otp_blocked" and result["fake_value"]:
                suggestions[request] = result
        return suggestions

    def analyze(self, scammer_message: str, turn_number: int = 1) -> Dict[str, Any]:
        """
        Main analysis function. Call on every scammer message.

        Returns:
            INTELLIGENCE_LOG dict with all extracted data and analysis
        """
        # 1. Extract intelligence via regex
        extracted = self.analyze_regex(scammer_message)

        # 2. Detect what scammer is asking for
        scammer_requesting = self.detect_data_requests(scammer_message)

        # 3. Detect tactics
        tactics_detected = self.detect_tactics(scammer_message)

        # 4. Get fake data suggestions if needed
        fake_data_suggestions = {}
        if scammer_requesting:
            fake_data_suggestions = self.get_fake_data_suggestion(scammer_requesting)

        # 5. Count total intel items
        total_intel = sum(
            len(v) for v in extracted.values() if isinstance(v, list)
        )

        intelligence_log = {
            "turn_number": turn_number,
            "extracted": extracted,
            "total_intel_count": total_intel,
            "scammer_requesting": scammer_requesting,
            "tactics_detected": tactics_detected,
            "fake_data_suggestions": fake_data_suggestions,
            "high_value_found": bool(
                extracted.get("upi_ids") or
                extracted.get("phone_numbers") or
                extracted.get("bank_accounts")
            ),
        }

        if total_intel > 0:
            logger.info(f"[Analyst] Turn {turn_number}: Extracted {total_intel} intel items: "
                       f"{[k for k, v in extracted.items() if v]}")
        if scammer_requesting:
            logger.info(f"[Analyst] Turn {turn_number}: Scammer requesting: {scammer_requesting}")
        if tactics_detected:
            logger.info(f"[Analyst] Turn {turn_number}: Tactics detected: {tactics_detected}")

        return intelligence_log


# Global instance
intelligence_analyst = IntelligenceAnalystAgent()
