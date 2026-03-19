"""Fake detail generator for baiting scammers.

Generates realistic but fake Indian personal details to:
1. Build trust with scammers
2. Extract more intelligence by appearing cooperative
3. Keep scammers engaged longer
"""

import random
from typing import Dict, Optional

# Regional Indian names for authenticity
MALE_FIRST_NAMES = [
    "Rajesh", "Suresh", "Ramesh", "Mahesh", "Dinesh", "Anil", "Vijay", 
    "Ravi", "Kumar", "Prakash", "Sanjay", "Amit", "Ashok", "Mohan",
    "Ganesh", "Harish", "Praveen", "Deepak", "Rakesh", "Santosh"
]

FEMALE_FIRST_NAMES = [
    "Lakshmi", "Priya", "Kavita", "Sunita", "Anita", "Savita", "Geeta",
    "Radha", "Sita", "Maya", "Rekha", "Pooja", "Nisha", "Meera",
    "Asha", "Usha", "Mala", "Kamala", "Parvati", "Durga"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Patel", "Singh", "Reddy", "Nair", "Rao",
    "Iyer", "Menon", "Joshi", "Desai", "Gupta", "Verma", "Das",
    "Pillai", "Naidu", "Choudhury", "Mukherjee", "Banerjee", "Shah"
]

# UPI providers commonly used in India
UPI_PROVIDERS = [
    "@paytm", "@ybl", "@oksbi", "@okaxis", "@okicici", "@okhdfcbank",
    "@axl", "@ibl", "@upi", "@fbl", "@pnb", "@citi"
]

# Bank names for account generation
BANKS = [
    "SBI", "HDFC", "ICICI", "Axis", "PNB", "BOI", "Canara",
    "Union", "IDBI", "Yes", "Kotak", "IndusInd"
]


class FakeDetailGenerator:
    """Generates realistic fake details for baiting scammers."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for reproducibility."""
        if seed:
            random.seed(seed)
    
    def generate_name(self, gender: str = "random") -> Dict[str, str]:
        """
        Generate a realistic Indian name.
        
        Args:
            gender: 'male', 'female', or 'random'
            
        Returns:
            Dict with first_name, last_name, full_name
        """
        if gender == "random":
            gender = random.choice(["male", "female"])
        
        if gender == "male":
            first = random.choice(MALE_FIRST_NAMES)
        else:
            first = random.choice(FEMALE_FIRST_NAMES)
        
        last = random.choice(LAST_NAMES)
        
        return {
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}",
            "gender": gender
        }
    
    def generate_upi_id(self, name: Optional[str] = None) -> str:
        """
        Generate a realistic fake UPI ID.
        
        Args:
            name: Optional name to base UPI on (makes it more believable)
            
        Returns:
            Fake UPI ID string
        """
        provider = random.choice(UPI_PROVIDERS)
        
        if name:
            # Use name-based UPI (more realistic)
            base = name.lower().replace(" ", "")
            # Add some numbers for variation
            suffix = random.randint(1, 999)
            return f"{base}{suffix}{provider}"
        else:
            # Generate random phone-like UPI
            phone = self.generate_phone_number()
            return f"{phone}{provider}"
    
    def generate_phone_number(self, include_country_code: bool = False) -> str:
        """
        Generate a realistic fake Indian phone number.
        
        Args:
            include_country_code: Whether to include +91
            
        Returns:
            10-digit or +91 prefixed phone number
        """
        # Indian mobile numbers start with 6, 7, 8, or 9
        first_digit = random.choice([6, 7, 8, 9])
        remaining = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        phone = f"{first_digit}{remaining}"
        
        if include_country_code:
            return f"+91{phone}"
        return phone
    
    def generate_bank_account(self, bank: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a realistic fake bank account number with checksum.
        
        Args:
            bank: Optional bank name
            
        Returns:
            Dict with account_number, ifsc_code, bank_name
        """
        if not bank:
            bank = random.choice(BANKS)
        
        # Indian bank accounts are typically 9-18 digits
        # Most common is 11-14 digits
        length = random.choice([11, 12, 13, 14])
        account_number = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        
        # IFSC code format: BANKXXXX123 (4 letters + 7 alphanumeric)
        # First 4: Bank code, 5th: always 0, last 6: branch code
        bank_code = bank[:4].upper().ljust(4, 'X')
        branch_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        ifsc = f"{bank_code}0{branch_code}"
        
        return {
            "account_number": account_number,
            "ifsc_code": ifsc,
            "bank_name": bank,
            "account_type": random.choice(["Savings", "Current"])
        }
    
    def generate_complete_profile(self, gender: str = "random") -> Dict[str, any]:
        """
        Generate a complete fake profile with all details.
        
        Args:
            gender: 'male', 'female', or 'random'
            
        Returns:
            Complete profile dictionary
        """
        name_dict = self.generate_name(gender)
        
        return {
            "name": name_dict["full_name"],
            "first_name": name_dict["first_name"],
            "last_name": name_dict["last_name"],
            "gender": name_dict["gender"],
            "phone": self.generate_phone_number(),
            "phone_with_code": self.generate_phone_number(include_country_code=True),
            "upi_id": self.generate_upi_id(name_dict["full_name"]),
            "bank_account": self.generate_bank_account(),
            "age": random.randint(45, 75),  # Elderly targets are more common
        }
    
    def get_believable_details_for_scam(self, scam_type: str) -> Dict[str, str]:
        """
        Get relevant fake details based on scam type.
        
        Args:
            scam_type: Type of scam (bank, upi, lottery, etc.)
            
        Returns:
            Relevant fake details for that scam type
        """
        profile = self.generate_complete_profile()
        
        if "bank" in scam_type.lower() or "kyc" in scam_type.lower():
            return {
                "type": "bank_details",
                "account_number": profile["bank_account"]["account_number"],
                "bank_name": profile["bank_account"]["bank_name"],
                "ifsc": profile["bank_account"]["ifsc_code"],
                "name": profile["name"]
            }
        
        elif "upi" in scam_type.lower() or "payment" in scam_type.lower():
            return {
                "type": "upi_details",
                "upi_id": profile["upi_id"],
                "phone": profile["phone"],
                "name": profile["name"]
            }
        
        elif "phone" in scam_type.lower() or "otp" in scam_type.lower():
            return {
                "type": "contact_details",
                "phone": profile["phone"],
                "name": profile["name"]
            }
        
        else:
            # Generic details
            return {
                "type": "general",
                "name": profile["name"],
                "phone": profile["phone"],
                "upi_id": profile["upi_id"]
            }


# Example usage
if __name__ == "__main__":
    generator = FakeDetailGenerator()
    
    print("=== Fake Detail Generator Test ===\n")
    
    # Test name generation
    print("1. Sample Names:")
    for _ in range(3):
        name = generator.generate_name()
        print(f"   {name['full_name']} ({name['gender']})")
    
    print("\n2. Sample UPI IDs:")
    for _ in range(3):
        print(f"   {generator.generate_upi_id()}")
    
    print("\n3. Sample Phone Numbers:")
    for _ in range(3):
        print(f"   {generator.generate_phone_number(include_country_code=True)}")
    
    print("\n4. Sample Bank Accounts:")
    for _ in range(2):
        account = generator.generate_bank_account()
        print(f"   {account['bank_name']}: {account['account_number']} ({account['ifsc_code']})")
    
    print("\n5. Complete Profile:")
    profile = generator.generate_complete_profile()
    print(f"   Name: {profile['name']}")
    print(f"   Age: {profile['age']}")
    print(f"   Phone: {profile['phone_with_code']}")
    print(f"   UPI: {profile['upi_id']}")
    print(f"   Bank: {profile['bank_account']['bank_name']} - {profile['bank_account']['account_number']}")
    
    print("\n6. Scam-Specific Details:")
    for scam_type in ["bank_kyc", "upi_payment", "otp_verification"]:
        details = generator.get_believable_details_for_scam(scam_type)
        print(f"   {scam_type}: {details}")
