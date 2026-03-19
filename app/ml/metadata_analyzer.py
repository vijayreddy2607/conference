"""Metadata Analyzer - Extract signals beyond text content.

Analyzes URLs, phone numbers, payment patterns, and urgency signals
to enhance scam detection accuracy.
"""
import re
from typing import Dict, List, Set
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Suspicious TLDs
SUSPICIOUS_TLDS = {
    '.site', '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', 
    '.top', '.win', '.bid', '.loan', '.download', '.click'
}

# Known legitimate Indian domains
LEGITIMATE_DOMAINS = {
    'hdfc.com', 'sbi.co.in', 'icicibank.com', 'axisbank.com',
    'amazon.in', 'flipkart.com', 'myntra.com', 'swiggy.com',
    'google.com', 'microsoft.com', 'tcs.com', 'infosys.com',
    'paytm.com', 'phonepe.com', 'googlepay.com', 'bharatpe.com'
}

# Common brand misspellings for phishing
BRAND_VARIATIONS = {
    'hdfc': ['hdfcbank', 'hdfc-bank', 'myhdfc', 'hdfc-verify'],
    'sbi': ['sbibank', 'onlinesbi', 'sbi-verify', 'mysbi'],
    'google': ['gooogle', 'googel', 'google-jobs'],
    'amazon': ['amazone', 'amazon-india', 'amazondelivery']
}


class MetadataAnalyzer:
    """Extracts and analyzes metadata signals from scam messages."""
    
    def __init__(self):
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.domain_pattern = re.compile(r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'(?:\+91|0)?[789]\d{9}')
        self.upi_pattern = re.compile(r'[\w.-]+@(?:paytm|ybl|upi|okaxis|oksbi|okhdfcbank)')
        self.bitcoin_pattern = re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b')
        
    def analyze(self, message: str) -> Dict:
        """Extract all metadata features from message.
        
        Returns:
            Dict with extracted features and risk scores
        """
        metadata = {
            'has_url': False,
            'has_suspicious_url': False,
            'has_phone': False,
            'has_multiple_phones': False,
            'has_upi': False,
            'has_bitcoin': False,
            'urgency_score': 0.0,
            'threat_score': 0.0,
            'legitimacy_score': 0.0,
            'overall_suspicion': 0.0,
            'extracted_data': {}
        }
        
        # Extract URLs
        urls = self._extract_urls(message)
        if urls:
            metadata['has_url'] = True
            metadata['has_suspicious_url'] = any(
                self._is_suspicious_url(url) for url in urls
            )
            metadata['extracted_data']['urls'] = urls
            
        # Extract phone numbers
        phones = self._extract_phones(message)
        if phones:
            metadata['has_phone'] = True
            metadata['has_multiple_phones'] = len(phones) > 1
            metadata['extracted_data']['phones'] = list(phones)
            
        # Extract UPI IDs
        upis = self._extract_upis(message)
        if upis:
            metadata['has_upi'] = True
            metadata['extracted_data']['upis'] = list(upis)
            
        # Check for Bitcoin addresses
        if self.bitcoin_pattern.search(message):
            metadata['has_bitcoin'] = True
            
        # Calculate urgency score
        metadata['urgency_score'] = self._calculate_urgency(message)
        
        # Calculate threat score
        metadata['threat_score'] = self._calculate_threat(message)
        
        # Calculate legitimacy score
        metadata['legitimacy_score'] = self._calculate_legitimacy(message, urls)
        
        # Overall suspicion score (0-1)
        metadata['overall_suspicion'] = self._calculate_overall_suspicion(metadata)
        
        return metadata
    
    def _extract_urls(self, message: str) -> List[str]:
        """Extract all URLs from message."""
        urls = self.url_pattern.findall(message)
        # Also check for domains without http://
        domains = self.domain_pattern.findall(message)
        all_urls = urls + [d for d in domains if d not in ' '.join(urls)]
        return list(set(all_urls))
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL is suspicious."""
        try:
            # Check for suspicious TLDs
            if any(url.endswith(tld) for tld in SUSPICIOUS_TLDS):
                return True
                
            # Check for URL shorteners
            shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
            if any(short in url for short in shorteners):
                return True
                
            # Check for phishing patterns (brand misspellings)
            lower_url = url.lower()
            for brand, variations in BRAND_VARIATIONS.items():
                if brand in lower_url:
                    # Check if it's a legitimate domain
                    if not any(legit in lower_url for legit in LEGITIMATE_DOMAINS):
                        # Check for variations
                        if any(var in lower_url for var in variations):
                            return True
                            
            return False
        except:
            return False
    
    def _extract_phones(self, message: str) -> Set[str]:
        """Extract phone numbers."""
        return set(self.phone_pattern.findall(message))
    
    def _extract_upis(self, message: str) -> Set[str]:
        """Extract UPI IDs."""
        return set(self.upi_pattern.findall(message))
    
    def _calculate_urgency(self, message: str) -> float:
        """Calculate urgency score based on time-pressure keywords."""
        urgency_words = [
            'urgent', 'immediately', 'now', 'fast', 'hurry', 'quick',
            'today', 'expire', 'last chance', 'limited time', '24 hours',
            'deadline', 'soon', 'asap', 'instant'
        ]
        message_lower = message.lower()
        count = sum(1 for word in urgency_words if word in message_lower)
        return min(count / 5.0, 1.0)  # Normalize to 0-1
    
    def _calculate_threat(self, message: str) -> float:
        """Calculate threat score based on threatening language."""
        threat_words = [
            'blocked', 'arrest', 'police', 'cbi', 'court', 'legal action',
            'warrant', 'suspended', 'terminated', 'penalty', 'fine',
            'punishment', 'jail', 'case filed', 'investigation', 'seized'
        ]
        message_lower = message.lower()
        count = sum(1 for word in threat_words if word in message_lower)
        return min(count / 4.0, 1.0)  # Normalize to 0-1
    
    def _calculate_legitimacy(self, message: str, urls: List[str]) -> float:
        """Calculate legitimacy score (higher = more legitimate)."""
        legitimacy_score = 0.0
        message_lower = message.lower()
        
        # Check for legitimate domains
        for url in urls:
            if any(domain in url.lower() for domain in LEGITIMATE_DOMAINS):
                legitimacy_score += 0.3
                
        # Check for legitimate message patterns
        legit_patterns = [
            'otp', 'verification code', 'credited to account',
            'transaction successful', 'payment received', 'order confirmed'
        ]
        for pattern in legit_patterns:
            if pattern in message_lower:
                legitimacy_score += 0.2
                
        # If message is very short (< 20 chars) and has OTP pattern
        if len(message) < 30 and re.search(r'\b\d{4,6}\b', message):
            legitimacy_score += 0.3
            
        return min(legitimacy_score, 1.0)
    
    def _calculate_overall_suspicion(self, metadata: Dict) -> float:
        """Calculate overall suspicion score from all signals."""
        suspicion = 0.0
        
        # URL-based suspicion
        if metadata['has_suspicious_url']:
            suspicion += 0.4
        elif metadata['has_url']:
            suspicion += 0.1
            
        # Multiple phones is suspicious
        if metadata['has_multiple_phones']:
            suspicion += 0.2
        elif metadata['has_phone']:
            suspicion += 0.05
            
        # Payment patterns
        if metadata['has_bitcoin']:
            suspicion += 0.3
        if metadata['has_upi']:
            suspicion += 0.1
            
        # Urgency and threats
        suspicion += metadata['urgency_score'] * 0.3
        suspicion += metadata['threat_score'] * 0.4
        
        # Subtract legitimacy
        suspicion -= metadata['legitimacy_score'] * 0.3
        
        # Normalize to 0-1 range
        return max(0.0, min(suspicion, 1.0))


# Quick testing
if __name__ == "__main__":
    analyzer = MetadataAnalyzer()
    
    test_cases = [
        "Your SBI account blocked! Update KYC at sbi-verify.site NOW or lose access.",
        "HDFC Bank: Rs 25000 credited to account ending 1234. Ref: TXN98765",
        "Call +917894561230 or +919876543210 for urgent job offer. Limited time!",
        "Pay Rs 5000 to paytm@upi or send to Bitcoin address 1A2B3C4D5E6F7G8H",
        "Your OTP is 123456. Valid for 5 minutes."
    ]
    
    for msg in test_cases:
        result = analyzer.analyze(msg)
        print(f"\nMessage: {msg[:60]}...")
        print(f"Suspicion: {result['overall_suspicion']:.2f}")
        print(f"  Urgency: {result['urgency_score']:.2f}, Threat: {result['threat_score']:.2f}")
        print(f"  Has URL: {result['has_suspicious_url']}, Has Phone: {result['has_phone']}")
