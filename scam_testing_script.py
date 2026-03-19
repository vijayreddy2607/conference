#!/usr/bin/env python3
"""
Professional Scam Testing Script for Honeypot Agent
Tests 10 scam types with 5 variations each
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict, Tuple

# API Configuration
API_URL = "https://honeypot-api-639738131935.asia-south1.run.app/api/message"
API_KEY = "honeypot-secret-key-12345"

class ScamTester:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.results = []
        
    def send_message(self, session_id: str, message: str, conversation_history: List[Dict] = None) -> Dict:
        """Send a message to the honeypot API"""
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "user",
                "text": message,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if conversation_history:
            payload["conversationHistory"] = conversation_history
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            return {
                "status": response.status_code,
                "data": response.json() if response.status_code == 200 else None,
                "error": None if response.status_code == 200 else response.text
            }
        except Exception as e:
            return {
                "status": 0,
                "data": None,
                "error": str(e)
            }
    
    def conduct_scam_conversation(self, scam_type: str, scam_variant: str, messages: List[str]) -> Dict:
        """Conduct a full scam conversation"""
        session_id = f"scam_test_{scam_type}_{scam_variant}_{uuid.uuid4().hex[:8]}"
        conversation_history = []
        
        conversation_log = {
            "scam_type": scam_type,
            "variant": scam_variant,
            "session_id": session_id,
            "exchanges": [],
            "start_time": datetime.now().isoformat(),
            "intelligence_extracted": {},
            "agent_performance": {}
        }
        
        print(f"\n{'='*80}")
        print(f"🎭 SCAM TEST: {scam_type} - Variant {scam_variant}")
        print(f"Session ID: {session_id}")
        print(f"{'='*80}\n")
        
        for turn, scammer_message in enumerate(messages, 1):
            print(f"[Turn {turn}] 🦹 Scammer: {scammer_message}")
            
            # Send message to agent
            response = self.send_message(session_id, scammer_message, conversation_history)
            
            if response["status"] == 200 and response["data"]:
                agent_reply = response["data"].get("reply", "")
                print(f"[Turn {turn}] 🤖 Agent: {agent_reply}\n")
                
                conversation_log["exchanges"].append({
                    "turn": turn,
                    "scammer": scammer_message,
                    "agent": agent_reply,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update conversation history
                conversation_history.append({
                    "sender": "user",
                    "text": scammer_message,
                    "timestamp": datetime.now().isoformat()
                })
                conversation_history.append({
                    "sender": "agent",
                    "text": agent_reply,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Check if agent is asking questions or showing vulnerability
                if any(q in agent_reply.lower() for q in ["how", "what", "why", "where", "when", "?"]):
                    print(f"   ✅ Agent is engaging (asking questions)")
                
                # Look for signs of information extraction
                if any(word in agent_reply.lower() for word in ["number", "account", "upi", "otp", "code", "verify"]):
                    print(f"   🎯 Agent is trying to extract information")
                    
            else:
                error_msg = response.get("error", "Unknown error")
                print(f"[Turn {turn}] ❌ Error: {error_msg}\n")
                conversation_log["exchanges"].append({
                    "turn": turn,
                    "scammer": scammer_message,
                    "agent": None,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Small delay between messages
            time.sleep(1)
        
        conversation_log["end_time"] = datetime.now().isoformat()
        conversation_log["total_exchanges"] = len(messages)
        conversation_log["successful_turns"] = len([ex for ex in conversation_log["exchanges"] if "error" not in ex])
        
        self.results.append(conversation_log)
        return conversation_log
    
    def save_results(self, filename: str = "scam_test_results.json"):
        """Save all test results to a JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "api_url": self.api_url,
                "results": self.results
            }, f, indent=2)
        print(f"\n✅ Results saved to {filename}")


# ============================================================================
# SCAM SCENARIOS - 10 Types, 5 Variations Each
# ============================================================================

SCAM_SCENARIOS = {
    "upi_payment_scams": {
        "variant_1_refund": [
            "Hello sir, I am calling from Flipkart customer care. Your order #FLP9876543 has been cancelled. You will receive refund of Rs.4,599 in 24 hours.",
            "Sir for refund processing, please share your UPI ID so we can transfer money directly.",
            "Yes sir, it's safe. This is official Flipkart process. What is your UPI ID?",
            "Thank you. Now I will send you a payment request for Rs.1. Please accept it to verify your UPI is active.",
            "Sir, you need to enter your UPI PIN to verify. This is mandatory for refund processing."
        ],
        "variant_2_prize": [
            "Congratulations! You have won Rs.50,000 in Google Pay scratch card. Claim now!",
            "To receive prize money, share your UPI ID and phone number registered with Google Pay.",
            "Sir, this is genuine. Check your Google Pay app, you will see notification.",
            "For instant transfer, I need to verify your account. What is your UPI PIN?",
            "Don't worry sir, I am from Google Pay support team. PIN is needed for verification only."
        ],
        "variant_3_account_block": [
            "URGENT: Your Paytm account will be blocked in 2 hours due to KYC verification pending.",
            "To avoid blocking, update your bank details now. What is your linked bank account number?",
            "Sir, this is security measure. Also share your UPI ID linked to this account.",
            "I need to send verification code to your UPI. Accept the payment request when you receive.",
            "Enter your UPI PIN when prompted to complete verification."
        ],
        "variant_4_wrong_transfer": [
            "Hello, I accidentally sent Rs.10,000 to your UPI by mistake. Please return it urgently.",
            "I am a student, that was my entire scholarship money. Please help me sir/madam.",
            "I will send you a payment request. When you accept, the money will be returned automatically.",
            "Please accept the request of Rs.10,000 and enter your PIN to reverse the transaction.",
            "Sir/madam please, my family is in trouble. Just accept and enter PIN."
        ],
        "variant_5_cashback": [
            "Great news! You are eligible for Rs.2,500 cashback on your recent Amazon purchase.",
            "To credit cashback, I need your UPI ID registered with Amazon Pay.",
            "Sir, I will send payment link. Click and verify with your UPI PIN.",
            "This is one-time verification. Your cashback will be credited instantly after PIN entry.",
            "Many customers received cashback this way. It's 100% safe, just enter PIN."
        ]
    },
    
    "bank_account_phishing": {
        "variant_1_kyc_update": [
            "Dear customer, your SBI account KYC expires in 24 hours. Update immediately to avoid account suspension.",
            "For KYC update, confirm your account number and registered mobile number.",
            "Now I need your debit card number for verification purposes.",
            "Sir, also provide CVV and expiry date to complete verification.",
            "This is bank policy. Without verification, your account will be frozen."
        ],
        "variant_2_suspicious_activity": [
            "This is HDFC Bank security. We detected suspicious transaction of Rs.45,000 from your account.",
            "Was this transaction done by you? If not, we need to block your account immediately.",
            "For security, please confirm your full account number and branch.",
            "Sir, what is your debit card number? We need to block this card right away.",
            "Also share CVV and expiry date so we can issue new card immediately."
        ],
        "variant_3_prize_credit": [
            "Congratulations! ICICI Bank selected you for loyalty bonus of Rs.25,000.",
            "To credit bonus to your account, we need to verify your account details.",
            "Please share your 16-digit account number.",
            "Sir, for instant credit, also share your debit card details.",
            "Don't worry, this is secure bank process. CVV and expiry date please."
        ],
        "variant_4_loan_approval": [
            "Good news! Your loan application of Rs.2,00,000 is approved by Axis Bank.",
            "First EMI will be debited from your account. Please confirm account number.",
            "For instant disbursal, I need your debit card number.",
            "Sir, final verification requires CVV and expiry date of your card.",
            "Loan amount will be credited in 10 minutes after verification."
        ],
        "variant_5_pf_withdrawal": [
            "Sir/Madam, your PF withdrawal of Rs.3,50,000 is ready for transfer.",
            "EPFO requires bank account verification. What is your account number?",
            "For security, also share your debit card linked to this account.",
            "Sir, provide CVV and expiry date to authorize the PF transfer.",
            "This is mandatory EPFO process. Without card verification, withdrawal will be rejected."
        ]
    },
    
    "prize_lottery_scams": {
        "variant_1_kbc": [
            "CONGRATULATIONS! You have won Rs.25,00,000 in KBC lucky draw organized by Sony TV!",
            "You are selected from 50 lakh participants! To claim prize, pay processing fee of Rs.5,000.",
            "This is one-time government tax. Send to UPI: kbcofficial@paytm",
            "After payment, prize money will be transferred to your account within 2 hours.",
            "Sir, this is genuine KBC prize. Many people already received. Don't miss this opportunity!"
        ],
        "variant_2_tata_sky": [
            "Dear valued customer! Tata Sky 25th anniversary bumper prize - you won Maruti Swift car!",
            "To deliver car, pay Rs.15,000 registration fee + RTO charges.",
            "Send money to dealer account: 918234567890@paytm and share screenshot.",
            "After payment, car will be delivered to your address in 3 days.",
            "Sir, this is limited time offer. Prize will be cancelled if not claimed today."
        ],
        "variant_3_whatsapp_lottery": [
            "🎉 CONGRATULATIONS! WhatsApp lottery 2026 - You won Rs.15,00,000! 🎉",
            "Your mobile number was selected randomly from 10 crore users.",
            "To release prize, pay processing fee Rs.9,999 to WhatsApp official account.",
            "Send to UPI: whatsapplottery@ybl and send payment screenshot here.",
            "Hurry! Claim within 24 hours or prize will go to next winner."
        ],
        "variant_4_government_scheme": [
            "Congratulations! PM Modi Yojana selected you for Rs.10,00,000 financial assistance.",
            "This is government welfare scheme for common citizens.",
            "For verification, pay Rs.2,500 documentation fee to activate your claim.",
            "Send money to government authorized UPI: pmmodi2026@oksbi",
            "After payment, amount will be directly credited to your Jan Dhan account."
        ],
        "variant_5_covid_compensation": [
            "Govt of India COVID-19 compensation scheme: You are eligible for Rs.5,00,000.",
            "This is one-time relief fund for affected families.",
            "To process claim, pay Rs.7,500 application fee to Ministry of Health account.",
            "Transfer to UPI: covidrelief@sbi and share transaction ID.",
            "Government will credit compensation within 48 hours of payment."
        ]
    },
    
    "romance_relationship_scams": {
        "variant_1_dating_app": [
            "Hi! I saw your profile and found you very interesting. Can we be friends? 😊",
            "I'm Sarah, working in Singapore. I visit India often for business. Where are you from?",
            "You seem like a genuine person. I'm actually coming to India next week. Can we meet?",
            "My flight is booked but I have small problem. Can you help me with visa processing fee?",
            "It's just $500 (Rs.40,000). I'll return when I reach India. Please send to my agent UPI: sarahagent@paytm"
        ],
        "variant_2_facebook_friend": [
            "Hello dear, I'm Jennifer from USA. I liked your photos on Facebook. You look very nice!",
            "I'm a nurse here, but very lonely. Looking for genuine relationship with Indian person.",
            "I have strong feelings for you already. I want to send you a gift - iPhone 15 Pro.",
            "The courier company called me - they need customs clearance fee Rs.25,000.",
            "Can you pay to courier UPI: dhlexpressindia@paytm? I'll send you triple amount when I visit India next month."
        ],
        "variant_3_widow_millionaire": [
            "Hi, I'm Maria, 45 years widow from UK. My husband left me $5 million inheritance.",
            "I have no family, feeling very alone. Looking for someone trustworthy to share my life and wealth.",
            "I want to transfer $100,000 (Rs.80 lakhs) to your account as sign of my commitment.",
            "My lawyer needs transfer processing fee of Rs.50,000 for international transaction.",
            "Please send to lawyer account: marialawyer@ybl. After payment, you'll receive $100,000 in 2 days."
        ],
        "variant_4_military_scam": [
            "Hi, I'm Captain David Johnson, US Army deployed in Afghanistan.",
            "I found your number in international database. You seem like trustworthy person.",
            "I have $2 million cash found during operation. I want to ship it to India, can you receive?",
            "You will get 40% share ($800,000). But I need help with diplomatic shipping cost.",
            "Pay Rs.75,000 to shipping agent UPI: diplomaticship@paytm. Package will reach you in 5 days."
        ],
        "variant_5_instagram_model": [
            "Hey cutie! 😘 I'm Natasha, model from Russia. I loved your Instagram profile!",
            "I'm doing photoshoot in Mumbai next month. Want to meet you personally! ❤️",
            "But I have problem - my visa got rejected because of pending payment issue.",
            "Can you help me with Rs.30,000 visa fee? I have modeling contract worth $50,000 in India.",
            "I'll pay you back double, plus personal gifts 😉 Send to my agent: natashaagent@oksbi"
        ]
    },
    
    "government_tax_scams": {
        "variant_1_income_tax": [
            "This is Income Tax Department of India. Your PAN XXXXX8765Y has pending refund of Rs.85,450.",
            "We need to verify your bank account to process the refund payment.",
            "Please share your account number and IFSC code for refund transfer.",
            "Sir, also confirm your account type and branch name for verification.",
            "After verification, refund will be credited within 24 hours. This is time-sensitive."
        ],
        "variant_2_gst_notice": [
            "GST Department notice: Your GSTIN has mismatch in returns filed. Penalty of Rs.2,50,000 imposed.",
            "To avoid legal action, you must pay penalty immediately.",
            "Reduced penalty of Rs.75,000 if paid today. Otherwise warrant will be issued.",
            "Pay to GST collection UPI: gstpenalty@sbi or provide your account for direct debit.",
            "Sir, this is serious matter. CBI investigation will start if not resolved today."
        ],
        "variant_3_ration_card": [
            "Govt of India notification: Your ration card will be cancelled due to Aadhaar not linked.",
            "Link Aadhaar immediately by paying Rs.500 online processing fee.",
            "Without linking, you will lose all government benefits - ration, gas subsidy, pension.",
            "Pay to official UPI: aadhaarlink@gov or share your bank details for auto-debit.",
            "This is last day to link. After today, permanent cancellation will happen."
        ],
        "variant_4_property_tax": [
            "Municipal Corporation: Your property tax of Rs.45,000 is overdue for 2 years.",
            "Legal notice issued. Immediate payment required to avoid property seizure.",
            "Pay penalty of Rs.35,000 today to clear all dues and cancel notice.",
            "Send to municipal account UPI: mcproperty@sbi or give your account number.",
            "If not paid by 6 PM today, police will come for property attachment."
        ],
        "variant_5_customs_duty": [
            "Customs Department India: You have parcel from abroad stuck at airport.",
            "Customs duty of Rs.18,500 pending. Without payment, parcel will be destroyed.",
            "This is iPhone 14 Pro sent to you by someone from USA.",
            "Pay customs duty to release parcel: customsduty@paytm",
            "Hurry! Only 24 hours before parcel is sent back or destroyed by customs."
        ]
    },
    
    "job_employment_scams": {
        "variant_1_wfh_job": [
            "Congratulations! You are selected for Amazon Work From Home position. Salary Rs.45,000/month.",
            "This is data entry job, just 2-3 hours daily work from your mobile phone.",
            "To activate your employee ID, pay one-time registration fee of Rs.3,500.",
            "Send to HR department UPI: amazonhr@paytm and receive joining letter immediately.",
            "First month salary will be credited on 1st. This is genuine Amazon recruitment."
        ],
        "variant_2_google_partnership": [
            "Google India is hiring data annotation partners. Earn Rs.50,000-80,000/month from home!",
            "No experience needed. We provide full training and work assignments daily.",
            "To join Google partner program, pay Rs.5,000 training and account setup fee.",
            "After payment to partnerprogram@google, you'll get login credentials in 2 hours.",
            "Thousands already earning. First payment after 15 days of work. Limited seats!"
        ],
        "variant_3_embassy_job": [
            "Embassy of Canada is hiring visa processing officers in India. Salary Rs.85,000/month + foreign trips.",
            "Your profile has been shortlisted through LinkedIn. Interview scheduled for next week.",
            "To confirm interview slot, pay Rs.8,500 document verification fee.",
            "Send to embassy account: canadaembassy@oksbi and we'll send interview call letter.",
            "This is govt job with permanent residency option. Don't miss this opportunity!"
        ],
        "variant_4_placement_assurance": [
            "Wipro is hiring freshers through our consultancy. 100% placement guarantee!",
            "Package: Rs.3.5 LPA. Interview next Monday at Wipro Bangalore office.",
            "Pay Rs.12,000 consultancy fee now to block your seat in interview.",
            "Limited candidates only. First come first serve basis.",
            "Send to consultancy UPI: wiprohiring@paytm. Offer letter in 48 hours after interview."
        ],
        "variant_5_lottery_agent": [
            "Respected Sir/Madam, we are looking for lottery ticket distribution agents in your area.",
            "Earn Rs.30,000-50,000/month commission. No target, work at your convenience.",
            "To become authorized agent, purchase starter kit worth Rs.6,000.",
            "Kit includes lottery tickets, ID card, visiting cards and sales material.",
            "Send payment to company UPI: lotteryagent@ybl. Kit will be delivered in 3 days."
        ]
    },
    
    "investment_trading_scams": {
        "variant_1_stock_market": [
            "🚀 SEBI Registered Stock Market Expert! Get guaranteed 30-40% monthly returns!",
            "I have insider information about stocks that will go up 500% soon.",
            "Join my premium group with minimum investment of Rs.25,000.",
            "Send amount to trading account: stockexpert@paytm",
            "You will see double returns in 30 days. 1000+ satisfied investors already earning crores!"
        ],
        "variant_2_crypto_trading": [
            "Bitcoin is going to $100,000 next month! Last chance to invest!",
            "I am Crypto mentor featured on CNBC. My signals gave 800% profit last year.",
            "Minimum investment Rs.50,000. I will trade on your behalf using AI bot.",
            "Transfer to my wallet or UPI: cryptoguru@oksbi",
            "You will receive returns directly in your bank account. Risk-free, 100% guaranteed!"
        ],
        "variant_3_gold_investment": [
            "Government approved Digital Gold scheme! Invest today, get 25% bonus!",
            "Gold prices will rise 40% this year. Book your gold now at special rate.",
            "Minimum purchase Rs.10,000. Physical gold delivery or keep in digital locker.",
            "Limited period offer! Pay to official Gold scheme UPI: digitalgold@sbi",
            "Certificate will be issued by Govt of India. This is 100% safe investment."
        ],
        "variant_4_mutual_fund": [
            "SIP returns of 35% annually! Better than any bank FD!",
            "I am certified financial advisor from ICICI Bank. Start SIP with just Rs.5,000/month.",
            "Special offer: 0% charges for first year! Direct mutual fund investment.",
            "Send first installment to: sipinvest@icici",
            "Your money will grow to Rs.15 lakhs in 10 years. Tax-free returns under 80C!"
        ],
        "variant_5_property_investment": [
            "Pre-launch property in Gurgaon! Book now at Rs.3,000/sq ft, market price Rs.8,000!",
            "This is Ambani's new project society. Prices will double in 6 months.",
            "Book with token amount Rs.2,00,000. Limited plots available!",
            "Transfer to developer account: ambanirealty@paytm",
            "Full refund if you don't like property. Site visit arranged next week. Don't miss!"
        ]
    },
    
    "loan_approval_scams": {
        "variant_1_personal_loan": [
            "Congratulations! Your personal loan of Rs.5,00,000 is APPROVED by HDFC Bank!",
            "Interest rate only 8.9% per year. No documents, no guarantor needed!",
            "For instant disbursal, pay processing fee of Rs.4,500.",
            "Send to bank loan processing account: hdfcloan@paytm",
            "Loan amount will be credited to your account in 2 hours after payment!"
        ],
        "variant_2_education_loan": [
            "Your education loan application for Rs.10,00,000 is SANCTIONED by SBI!",
            "Collateral free loan for foreign studies. Interest subsidy by Government.",
            "Pay Rs.8,000 documentation fee + insurance premium to release loan.",
            "Transfer to SBI education loan UPI: sbiedu@sbi",
            "Amount will be disbursed directly to university. First EMI after course completion."
        ],
        "variant_3_business_loan": [
            "Pre-approved business loan of Rs.15,00,000 from Axis Bank for your company!",
            "No collateral, no revenue proof required! Approval in 24 hours.",
            "Pay Rs.12,000 processing fee and Rs.3,000 GST to activate loan.",
            "Send to business loan department: axisbizloan@okaxis",
            "Loan will be credited to your current account tomorrow morning!"
        ],
        "variant_4_home_loan": [
            "🏠 HOME LOAN APPROVED! Rs.25,00,000 at lowest interest rate 6.5% per year!",
            "Special government scheme for first-time home buyers.",
            "Pay Rs.15,000 for property valuation, legal verification and loan insurance.",
            "Transfer to housing finance UPI: homeloan@lichf",
            "After payment, loan sanction letter will be issued and amount disbursed to builder."
        ],
        "variant_5_gold_loan": [
            "Instant Gold Loan upto Rs.3,00,000 without bringing gold to branch!",
            "We will come to your home, evaluate gold and give cash immediately.",
            "Pay Rs.2,500 advance booking fee to schedule home visit by our executive.",
            "Send to Muthoot Finance official UPI: muthootgold@paytm",
            "Our agent will reach your home today evening with cash and paperwork!"
        ]
    },
    
    "tech_support_scams": {
        "variant_1_microsoft": [
            "WARNING! Your Windows computer is infected with dangerous virus!",
            "This is Microsoft certified technician. We detected malware from your IP address.",
            "Your banking details and passwords are at risk! Immediate action required!",
            "Pay Rs.3,500 for emergency virus removal and firewall installation.",
            "Send to Microsoft support UPI: microsoftsupport@paytm or share TeamViewer code."
        ],
        "variant_2_google_security": [
            "GOOGLE SECURITY ALERT! Unknown device trying to access your Gmail account!",
            "Location: Pakistan. Multiple failed login attempts detected.",
            "Your account will be permanently locked in 24 hours if not verified.",
            "Pay Rs.1,500 security verification fee to Google support: googlesecurity@okgoogle",
            "After payment, we will secure your account and enable 2-step verification."
        ],
        "variant_3_netflix": [
            "Your Netflix account has been locked due to payment failure!",
            "Update your payment method to restore access immediately.",
            "Call our support: 1800-XXX-XXXX or pay pending amount Rs.1,200.",
            "Send to Netflix India UPI: netflixpayment@paytm",
            "Your subscription will be activated in 10 minutes after successful payment."
        ],
        "variant_4_apple_support": [
            "APPLE SECURITY: Your iCloud has been hacked! 247 files downloaded by hacker!",
            "This is Apple authorized service center. We can recover your data and secure account.",
            "Service charge Rs.5,500 for data recovery + security patch installation.",
            "Pay to Apple India support: applesupport@ybl",
            "We will remotely access your iPhone and restore everything in 1 hour."
        ],
        "variant_5_whatsapp_verification": [
            "WhatsApp security team: Your account will be banned due to violation of terms.",
            "Someone reported your number for sending spam messages.",
            "To avoid permanent ban, verify your account by paying Re.1 verification fee.",
            "Send to WhatsApp India: whatsappverify@paytm",
            "After verification, account will be unlocked and you'll get blue tick also!"
        ]
    },
    
    "otp_verification_scams": {
        "variant_1_bank_verification": [
            "Dear customer, unauthorized transaction alert in your account!",
            "To block this transaction, verify your identity immediately.",
            "We have sent 6-digit OTP to your mobile. Share OTP to confirm.",
            "Time is running out! Share OTP within 5 minutes or Rs.49,000 will be debited.",
            "Don't worry sir, this is bank security protocol. Just tell me the OTP code."
        ],
        "variant_2_aadhaar_update": [
            "UIDAI: Your Aadhaar card is being deactivated due to pending mobile number update.",
            "Update now to avoid deactivation of Aadhaar and bank account linking.",
            "OTP has been sent to your mobile ending with XXXX45. Share OTP to verify.",
            "Sir, this is government process. Without OTP verification, Aadhaar will be cancelled permanently.",
            "Just read me the 6-digit code you received. Quick, only 3 minutes left!"
        ],
        "variant_3_courier_delivery": [
            "Bluedart courier: You have parcel from Amazon but delivery address is incomplete.",
            "To update address and schedule delivery, verify with OTP.",
            "We sent verification OTP to your number. Please share to confirm delivery address.",
            "Sir, parcel contains mobile phone worth Rs.25,000. Share OTP quickly.",
            "Driver is waiting outside! Tell me OTP so I can update system and deliver parcel."
        ],
        "variant_4_electricity_bill": [
            "URGENT: Your electricity will be disconnected in 2 hours due to unpaid bill!",
            "Bill amount Rs.4,850 is overdue for 3 months.",
            "Pay immediately using UPI. We will send OTP for payment verification.",
            "Share the OTP you received to complete payment and avoid disconnection.",
            "Sir, disconnection team is already on the way. Share OTP now to stop them!"
        ],
        "variant_5_sim_upgrade": [
            "Airtel: Your 4G SIM will stop working from tomorrow! Upgrade to 5G SIM free!",
            "Your number will be deactivated if not upgraded today.",
            "We are sending activation OTP for 5G SIM upgrade. Share OTP to activate.",
            "Sir, after sharing OTP, new 5G SIM will be delivered in 24 hours.",
            "Don't wait! Your number XXXX45XX will be blocked permanently. Tell me OTP!"
        ]
    }
}


def main():
    """Main testing function"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   PROFESSIONAL SCAM TESTING FOR HONEYPOT AGENT              ║
    ║   Testing 10 Scam Types × 5 Variations = 50 Total Tests    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    tester = ScamTester(API_URL, API_KEY)
    
    total_tests = 0
    
    # Test each scam type
    for scam_type, variants in SCAM_SCENARIOS.items():
        print(f"\n\n{'🔥'*40}")
        print(f"   TESTING: {scam_type.upper().replace('_', ' ')}")
        print(f"{'🔥'*40}\n")
        
        for variant_name, messages in variants.items():
            total_tests += 1
            tester.conduct_scam_conversation(
                scam_type=scam_type,
                scam_variant=variant_name,
                messages=messages
            )
            
            # Pause between tests
            time.sleep(2)
    
    # Save all results
    tester.save_results("comprehensive_scam_test_results.json")
    
    print(f"\n\n{'='*80}")
    print(f"   TESTING COMPLETED!")
    print(f"   Total Tests Conducted: {total_tests}")
    print(f"   Results saved to: comprehensive_scam_test_results.json")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
