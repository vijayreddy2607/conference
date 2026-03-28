"""Regex patterns for intelligence extraction — comprehensive version."""
import re

# UPI ID Pattern
UPI_PATTERN = re.compile(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)', re.IGNORECASE)

# Bank Account Pattern: 11-18 digits ONLY (exclude 10-digit phone numbers!)
BANK_ACCOUNT_PATTERN = re.compile(r'\b(\d{11,18}|\d{4}[-\s]?\d{4}[-\s]?\d{4,10})\b')

# Phone Number Pattern: Indian phone numbers (ALL formats)
PHONE_PATTERN = re.compile(
    r'(?:\(?\ +?91\)?[\s.\-]?|(?<!\d)0)?'
    r'('
    r'[6-9]\d{4}[\s.\-]\d{5}'
    r'|(?<!\d)[6-9]\d{9}(?!\d)'
    r')',
    re.IGNORECASE
)

# URL Pattern: http/https links
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

# Obfuscated URL Pattern: "dot com", "[.]com", "hxxp://"
OBFUSCATED_URL_PATTERN = re.compile(
    r'(?:https?|hxxps?|h\*\*p)://[^\s]+|'
    r'(?<![@\-a-zA-Z0-9])(?:[a-z0-9][a-z0-9-]{2,})\s*(?:dot|\[?\.\ ]?|\(\s*dot\s*\))\s*(?:com|in|org|net|co|info)(?:/[^\s]*)?|'
    r'(?:[a-z0-9-]+\[\.\][a-z]+(?:/[^\s]*)?)',
    re.IGNORECASE
)

# Employee ID Pattern
EMPLOYEE_ID_PATTERN = re.compile(
    r'(?:employee\s*id|emp\s*id|staff\s*id|customer\s*id|id)[\s:]*(?:is\s+)?([A-Z0-9]{4,10})',
    re.IGNORECASE
)

# Name Pattern
NAME_PATTERN = re.compile(
    r'(?:naam|name|I am|main|mera naam)\s+(?:hai\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)|(?:Mr\.?|Mrs\.?|Ms\.?)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
    re.IGNORECASE
)

# Address Pattern
ADDRESS_PATTERN = re.compile(
    r'(\d+[/-]?\d*,?\s+[A-Z][A-Za-z\s]+(?:Road|Street|Sector|Plot|Floor|Building|Branch)[,\s]+[A-Za-z\s]+)',
    re.IGNORECASE
)

# Hindi Address Pattern
HINDI_ADDRESS_PATTERN = re.compile(
    r'([\u0900-\u097F\w\s]+(?:सिटी|बाजार|रोड|मार्ग|नगर|इलाका|क्षेत्र)[,\s]*[\u0900-\u097F\w\s]*)',
    re.IGNORECASE
)

# Email Pattern
EMAIL_PATTERN = re.compile(r'[\w.-]+@[\w.-]+\.\w+')

# Pincode Pattern
PINCODE_PATTERN = re.compile(r'\b[1-9]\d{5}\b')

# Written Number Pattern
WRITTEN_NUMBER_MAP = {
    'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
    'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
}
WRITTEN_NUMBER_PATTERN = re.compile(
    r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine)(?:\s+(?:zero|one|two|three|four|five|six|seven|eight|nine)){2,}\b',
    re.IGNORECASE
)

# Case ID Pattern
CASE_ID_PATTERN = re.compile(
    r'\b(?:case|ref(?:erence)?|ticket|complaint|incident|claim|request)'
    r'(?:\s+(?:no\.?|number|id|reference))?'
    r'\s*(?:is\s+|:\s*|-\s*|\s)?'
    r'([A-Z0-9][A-Z0-9\-]{2,18}(?:\d[A-Z0-9\-]*|[A-Z0-9\-]*\d[A-Z0-9\-]*))',
    re.IGNORECASE
)

# Policy Number Pattern
POLICY_NUMBER_PATTERN = re.compile(
    r'\b(?:policy|pol)\s*(?:no\.?|number|#|:)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-]{3,19})\b',
    re.IGNORECASE
)

# Order Number Pattern
ORDER_NUMBER_PATTERN = re.compile(
    r'\b(?:order|ord|transaction|txn|booking|invoice)\s*(?:id|no\.?|number|#|:)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-]{2,18}(?:\d[A-Z0-9\-]*|[A-Z0-9\-]*\d[A-Z0-9\-]*))\b',
    re.IGNORECASE
)

# Suspicious Keywords
SCAM_KEYWORDS = [
    "urgent", "immediately", "now", "today", "within 24 hours", "expires",
    "limited time", "hurry", "quick", "fast",
    "blocked", "suspended", "deactivated", "frozen", "locked", "banned",
    "arrest", "legal action", "court", "police", "penalty", "fine",
    "verify", "confirm", "authenticate", "validate", "update", "secure",
    "otp", "password", "pin", "cvv", "card details",
    "account", "bank", "upi", "payment", "transfer", "refund", "prize",
    "lottery", "winner", "cashback", "reward", "bonus",
    "rbi", "government", "tax department", "income tax", "gst",
    "custom duty", "fedex", "courier", "delivery",
    "click here", "call now", "reply immediately", "share", "provide",
    "send", "forward", "download", "install",
]

PAYMENT_APPS = [
    "paytm", "phonepe", "googlepay", "gpay", "bhim", "amazon pay",
    "whatsapp pay", "mobikwik", "freecharge", "airtel money"
]


def extract_upi_ids(text: str) -> list:
    text_lower = text.lower()
    upi_ids = []
    for match in UPI_PATTERN.finditer(text_lower):
        m = match.group(1)
        end_pos = match.end()
        next_char = text_lower[end_pos] if end_pos < len(text_lower) else ''
        if next_char == '-':
            continue
        if next_char == '.':
            char_after_dot = text_lower[end_pos + 1] if end_pos + 1 < len(text_lower) else ''
            if char_after_dot.isalpha():
                continue
        at_pos = m.rfind('@')
        domain_part = m[at_pos+1:] if at_pos >= 0 else ''
        if '.' not in domain_part:
            upi_ids.append(m)
    return list(set(upi_ids))


def extract_bank_accounts(text: str) -> list:
    matches = BANK_ACCOUNT_PATTERN.findall(text)
    filtered = []
    for m in matches:
        clean = re.sub(r'[-\s]', '', m)
        if len(clean) >= 11:
            filtered.append(m)
        elif len(clean) == 10 and not clean[0] in '6789':
            filtered.append(m)
    return filtered


def convert_written_numbers(text: str) -> str:
    matches = WRITTEN_NUMBER_PATTERN.findall(text)
    for match in matches:
        words = match.lower().split()
        digits = ''.join([WRITTEN_NUMBER_MAP.get(word, '') for word in words])
        text = text.replace(match, digits)
    return text


def extract_phone_numbers(text: str) -> list:
    text_converted = convert_written_numbers(text)
    matches = PHONE_PATTERN.findall(text_converted)
    cleaned = []
    for match in matches:
        clean = re.sub(r'[\s.\-]', '', match)
        if len(clean) == 10 and clean[0] in '6789':
            cleaned.append('+91-' + clean)
    return list(set(cleaned))


def extract_urls(text: str) -> list:
    urls = []
    urls.extend(URL_PATTERN.findall(text))
    obfuscated = OBFUSCATED_URL_PATTERN.findall(text)
    for url in obfuscated:
        normalized = url.replace(' dot ', '.').replace('dot ', '.').replace(' dot', '.')
        normalized = normalized.replace('[.]', '.').replace('(.)', '.')
        normalized = normalized.replace('hxxp', 'http').replace('h**p', 'http')
        if normalized not in urls:
            urls.append(normalized)
    cleaned = []
    for url in urls:
        url = url.rstrip('.,;:"\')')
        if url:
            cleaned.append(url)
    return list(set(cleaned))


def extract_employee_ids(text: str) -> list:
    return EMPLOYEE_ID_PATTERN.findall(text)


def extract_names(text: str) -> list:
    matches = NAME_PATTERN.findall(text)
    names = []
    for match in matches:
        if isinstance(match, tuple):
            names.extend([m for m in match if m])
        else:
            names.append(match)
    return list(set(names))


def extract_addresses(text: str) -> list:
    addresses = []
    addresses.extend(ADDRESS_PATTERN.findall(text))
    hindi_matches = HINDI_ADDRESS_PATTERN.findall(text)
    addresses.extend(hindi_matches)
    cleaned = [addr.strip() for addr in addresses if len(addr.strip()) > 10]
    return list(set(cleaned))


def extract_emails(text: str) -> list:
    emails = []
    matches = EMAIL_PATTERN.findall(text)
    for m in matches:
        at_pos = m.rfind('@')
        domain_part = m[at_pos+1:] if at_pos >= 0 else ''
        if '.' in domain_part:
            emails.append(m.lower())
    return list(set(emails))


def extract_pincodes(text: str) -> list:
    matches = PINCODE_PATTERN.findall(text)
    valid_pincodes = []
    for code in matches:
        if len(set(code)) == 1:
            continue
        if all(int(code[i]) == int(code[i-1]) + 1 for i in range(1, len(code))):
            continue
        if all(int(code[i]) == int(code[i-1]) - 1 for i in range(1, len(code))):
            continue
        valid_pincodes.append(code)
    return list(set(valid_pincodes))


def extract_case_ids(text: str) -> list:
    matches = CASE_ID_PATTERN.findall(text)
    return list(set(m for m in matches if not m.isdigit() or len(m) < 8))


def extract_policy_numbers(text: str) -> list:
    matches = POLICY_NUMBER_PATTERN.findall(text)
    return list(set(m for m in matches if any(c.isdigit() for c in m)))


def extract_order_numbers(text: str) -> list:
    matches = ORDER_NUMBER_PATTERN.findall(text)
    return list(set(matches))


def extract_keywords(text: str) -> list:
    text_lower = text.lower()
    found_keywords = []
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    for app in PAYMENT_APPS:
        if app in text_lower:
            found_keywords.append(app)
    return list(set(found_keywords))
