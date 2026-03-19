"""Data models for intelligence tracking."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class Intelligence(BaseModel):
    """Accumulated intelligence from conversations."""
    model_config = ConfigDict(validate_assignment=True)
    
    bankAccounts: set[str] = Field(default_factory=set)
    upiIds: set[str] = Field(default_factory=set)  # Fixed typo
    phishingLinks: set[str] = Field(default_factory=set)
    phoneNumbers: set[str] = Field(default_factory=set)
    emails: set[str] = Field(default_factory=set)  # NEW: Email addresses
    suspiciousKeywords: set[str] = Field(default_factory=set)
    
    def add_bank_account(self, account: str):
        """Add a bank account to intelligence."""
        self.bankAccounts.add(account)
    
    def add_upi_id(self, upi_id: str):
        """Add a UPI ID to intelligence."""
        self.upiIds.add(upi_id)  # Fixed typo

    
    def add_phishing_link(self, link: str):
        """Add a phishing link to intelligence."""
        self.phishingLinks.add(link)
    
    def add_phone_number(self, phone: str):
        """Add a phone number to intelligence."""
        self.phoneNumbers.add(phone)
    
    def add_email(self, email: str):
        """Add an email address to intelligence."""
        self.emails.add(email)
    
    def add_keyword(self, keyword: str):
        """Add a suspicious keyword to intelligence."""
        self.suspiciousKeywords.add(keyword)
    
    def to_dict(self) -> dict:
        """Convert to dictionary with lists instead of sets."""
        return {
            "bankAccounts": list(self.bankAccounts),
            "upiIds": list(self.upiIds),  # Fixed typo
            "phishingLinks": list(self.phishingLinks),
            "phoneNumbers": list(self.phoneNumbers),
            "emails": list(self.emails),
            "suspiciousKeywords": list(self.suspiciousKeywords)
        }
    
    def count_items(self) -> int:
        """Count total intelligence items."""
        return (
            len(self.bankAccounts) +
            len(self.upiIds) +  # Fixed typo
            len(self.phishingLinks) +
            len(self.phoneNumbers) +
            len(self.emails) +
            len(self.suspiciousKeywords)
        )


class ScamDetection(BaseModel):
    """Result of scam detection."""
    is_scam: bool
    confidence: float  # 0.0 to 1.0
    scam_type: Literal[
        # Hackathon-friendly names (Problem Statement 2)
        "bank_phishing",         # Bank phishing/KYC scams
        "fake_job",              # Job offer scams
        "digital_arrest",        # Police/CBI/legal threats
        "investment",            # Investment/trading/crypto scams
        "lottery_prize",         # Lottery/prize scams
        "delivery_scam",         # Package delivery scams
        "credit_loan",           # Credit card/loan scams
        "sextortion",            # Sextortion scams
        "impersonation",         # Authority impersonation
        "marketplace_scam",      # Online marketplace scams
        # Original classifier types (backward compatibility)
        "bank_kyc",              # Bank KYC/verification scams
        "upi_scam",              # UPI/payment app scams
        "credit_card",           # Credit card fraud
        "police_legal",          # Police/legal threats
        "tax_refund",            # Tax/Aadhaar scams
        "govt_scheme",           # Government scheme scams
        "job_offer",             # Job/work-from-home scams
        "prize_lottery",         # Prize/lottery scams
        "bill_payment",          # Bill payment scams
        "romance",               # Romance/friendship scams
        "delivery",              # Package delivery scams
        # Legacy types
        "bank_fraud",
        "upi_fraud",
        "phishing",
        "legal_threat",
        "authority_impersonation",
        "unknown"
    ]
    recommended_agent: Literal["uncle", "worried", "techsavvy", "aunty", "student"]
    reasoning: str = ""
