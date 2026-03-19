"""Regex patterns for intelligence extraction."""
import re

# UPI ID Pattern: word@word (e.g., scammer@paytm, user@ybl)
# AGGRESSIVE: Accept ALL @word patterns as UPI (don't filter gmail/yahoo)
UPI_PATTERN = re.compile(r'\b([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)\b')

# Email Pattern: standard email format
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Bank Account Pattern: 11-18 digits (Indian bank accounts)
# FIXED: Exclude 10-digit phone numbers by requiring 11+ digits
BANK_ACCOUNT_PATTERN = re.compile(r'\b\d{11,18}\b')

# Enhanced Phone Number Pattern: Indian phone numbers with multiple formats
# AGGRESSIVE: Accept any 10-digit number starting with 6-9
PHONE_PATTERN = re.compile(
    r'(?:\+91[-\s]?)?[6-9]\d{9}|'  # +91 or without, starting with 6-9
    r'\b[6-9]\d{2}[-\s]?\d{3}[-\s]?\d{4}\b|'  # With dashes/spaces
    r'\b[6-9]\d{9}\b'  # Simple 10 digits
)

# Enhanced URL Pattern: http/https + short links + dot-separated domains
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    r'|\b(?:bit\.ly|tinyurl\.com|goo\.gl|short\.link)/[a-zA-Z0-9]+'  # Short links
)

# Phishing domain keywords
PHISHING_KEYWORDS = [
    'bit.ly', 'tinyurl', 'short.link', 'goo.gl', 't.co',
    'login', 'verify', 'secure', 'account', 'update', 'confirm'
]

# Suspicious Keywords
SCAM_KEYWORDS = [
    # Urgency
    "urgent", "immediately", "now", "today", "within 24 hours", "expires",
    "limited time", "hurry", "quick", "fast",
    
    # Threats
    "blocked", "suspended", "deactivated", "frozen", "locked", "banned",
    "arrest", "legal action", "court", "police", "penalty", "fine",
    
    # Verification/Authentication
    "verify", "confirm", "authenticate", "validate", "update", "secure",
    "otp", "password", "pin", "cvv", "card details",
    
    # Financial
    "account", "bank", "upi", "payment", "transfer", "refund", "prize",
    "lottery", "winner", "cashback", "reward", "bonus",
    
    # Authority Impersonation
    "rbi", "government", "tax department", "income tax", "gst",
    "custom duty", "fedex", "courier", "delivery",
    
    # Call to Action
    "click here", "call now", "reply immediately", "share", "provide",
    "send", "forward", "download", "install",
]

# Payment App Names
PAYMENT_APPS = [
    "paytm", "phonepe", "googlepay", "gpay", "bhim", "amazon pay",
    "whatsapp pay", "mobikwik", "freecharge", "airtel money"
]


def extract_upi_ids(text: str) -> list[str]:
    """
    Extract UPI IDs from text.
    AGGRESSIVE: Accept ALL @word patterns (including prizewinner@paytm, etc.)
    """
    matches = UPI_PATTERN.findall(text.lower())
    # CHANGED: Don't filter out anything that looks like UPI
    # Accept prizewinner@paytm, techsupport99@paytm, etc.
    upi_candidates = []
    for m in matches:
        # Only filter out obvious email domains
        if any(domain in m for domain in ['.com', '.org', '.in', '.net', '.co']):
            continue  # This is an email, not UPI
        upi_candidates.append(m)
    return upi_candidates


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    return EMAIL_PATTERN.findall(text)


def extract_bank_accounts(text: str) -> list[str]:
    """
    Extract bank account numbers from text.
    AGGRESSIVE: Accept any 9+ digit sequence
    """
    matches = BANK_ACCOUNT_PATTERN.findall(text)
    # Don't filter out anything - let intelligence system decide
    return matches


def extract_phone_numbers(text: str) -> list[str]:
    """
    Extract phone numbers from text with AGGRESSIVE detection.
    Accept any format: 9876543210, +91 9876543210, 987-654-3210, etc.
    """
    matches = PHONE_PATTERN.findall(text)
    # Clean up and deduplicate
    cleaned = []
    seen = set()
    
    for match in matches:
        # Remove spaces, dashes, and +91 prefix
        cleaned_num = re.sub(r'[-\s+]', '', match)
        cleaned_num = cleaned_num.replace('91', '', 1) if cleaned_num.startswith('91') else cleaned_num
        
        if len(cleaned_num) == 10 and cleaned_num[0] in '6789' and cleaned_num not in seen:
            cleaned.append(cleaned_num)
            seen.add(cleaned_num)
    
    return cleaned


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return URL_PATTERN.findall(text)


def categorize_link(url: str) -> str:
    """Categorize a link as likely phishing or normal."""
    url_lower = url.lower()
    if any(keyword in url_lower for keyword in PHISHING_KEYWORDS):
        return "phishing_suspected"
    return "normal"


def extract_keywords(text: str) -> list[str]:
    """Extract suspicious keywords from text."""
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    # Also check for payment apps
    for app in PAYMENT_APPS:
        if app in text_lower:
            found_keywords.append(app)
    
    return list(set(found_keywords))  # Remove duplicates
