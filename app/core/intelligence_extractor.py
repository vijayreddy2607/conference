"""Intelligence extraction from conversations."""
from app.models.intelligence import Intelligence
from app.utils import patterns
import logging

logger = logging.getLogger(__name__)


class IntelligenceExtractor:
    """Extracts intelligence from scam conversations."""
    
    def __init__(self):
        self.intelligence = Intelligence()
    
    def extract_from_message(self, text: str, source: str = "scammer") -> Intelligence:
        """
        Extract intelligence from a single message.
        CRITICAL: Extract from BOTH scammer and agent messages for maximum intelligence!
        
        Args:
            text: Message text to analyze
            source: "scammer" or "agent" - extract from both!
        
        Returns:
            Intelligence object with extracted data
        """
        # Extract UPI IDs (AGGRESSIVE MODE - accept all @word patterns)
        upi_ids = patterns.extract_upi_ids(text)
        for upi_id in upi_ids:
            self.intelligence.add_upi_id(upi_id)
            logger.info(f"✅ Extracted UPI ID ({source}): {upi_id}")
        
        # Extract emails
        emails = patterns.extract_emails(text)
        for email in emails:
            self.intelligence.add_email(email)
            logger.info(f"✅ Extracted email ({source}): {email}")
        
        # Extract bank accounts (AGGRESSIVE - any 9+ digit sequence)
        bank_accounts = patterns.extract_bank_accounts(text)
        for account in bank_accounts:
            # Additional validation: must be at least 9 digits
            if len(account) >= 9:
                self.intelligence.add_bank_account(account)
                logger.info(f"✅ Extracted bank account ({source}): {account}")
        
        # Extract phone numbers (AGGRESSIVE - all formats)
        phone_numbers = patterns.extract_phone_numbers(text)
        for phone in phone_numbers:
            self.intelligence.add_phone_number(phone)
            logger.info(f"✅ Extracted phone ({source}): {phone}")
        
        # Extract URLs
        urls = patterns.extract_urls(text)
        for url in urls:
            # Categorize the link
            link_type = patterns.categorize_link(url)
            self.intelligence.add_phishing_link(url)
            logger.info(f"✅ Extracted URL ({source}, {link_type}): {url}")
        
        # Extract suspicious keywords (only from scammer to avoid noise)
        if source == "scammer":
            keywords = patterns.extract_keywords(text)
            for keyword in keywords:
                self.intelligence.add_keyword(keyword)
        
        return self.intelligence
    
    def get_intelligence(self) -> Intelligence:
        """Get accumulated intelligence."""
        return self.intelligence
    
    def reset(self):
        """Reset intelligence for new session."""
        self.intelligence = Intelligence()
