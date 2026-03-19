"""Comprehensive scam detection test dataset covering all 10 Indian scam types.

Based on 2025 India fraud statistics. Each scam type has multiple examples
representing different variations and attack patterns.
"""

# ============================================================================
# COMPREHENSIVE SCAM DATASET (100+ Examples)
# ============================================================================

INDIAN_SCAM_DATASET = {
    # 1. Fake Job Notifications/Offers (64% of falls - MOST COMMON)
    "fake_job": [
        "Congratulations! You've been selected for a job at Google. Pay ₹500 registration fee to proceed. Click: jobs-google.site",
        "Urgent job offer from HDFC Bank. Send resume and Aadhaar to confirm. Salary ₹45,000/month guaranteed!",
        "Amazon hiring data entry operators. Work from home. Earn ₹50,000/month. Pay ₹1000 training fee",
        "Selected for TCS internship! Offer letter ready. Transfer ₹2000 document processing fee to proceed",
        "Part-time job alert! Flipkart product review work. Earn ₹3000 daily. Registration fee: ₹500 only",
        "Infosys hiring freshers. No interview needed. Send ₹1500 for background verification. Joining immediate!",
        "Work 2 hours daily, earn ₹40000 monthly! No skills required. Pay ₹800 account activation fee",
        "Microsoft remote job. Salary $50,000/year. Processing charge ₹5000. Limited slots available!",
        "Government job vacancy announced. Apply now with ₹3000 application fee. Direct selection guaranteed",
        "Wipro urgent hiring! Send passport size photo + ₹1200 offer letter fee. Join next Monday!"
    ],
    
    # 2. Bank Alert/Phishing (52% falls)
    "bank_phishing": [
        "Your bank account will be blocked today due to KYC failure. Verify immediately at sbi-kyc-verify.com",
        "Alert: Suspicious transaction of ₹45,000 on your SBI account. Call 1800-123-4567 to stop immediately",
        "HDFC Bank: Your card is temporarily blocked. Update details: hdfc-secure-login.site or call now",
        "URGENT: Your account shows unusual activity. Confirm identity by sharing OTP sent to your number",
        "PNB Alert: Account will deactivate in 24 hours. Complete KYC at pnb-ekyc.in with Aadhaar + PAN",
        "ICICI Bank: Failed payment of ₹12,000. Rectify now at icici-payment-fix.com before account freeze",
        "Axis Bank Security: Unauthorized login detected. Reset password immediately: axis-reset.site",
        "BOI Customer: Your ATM card expired. Renew online at bank-ofindia-renew.com within 48 hours",
        "SBI KYC Alert: Submit documents today or ₹10,000 penalty. Upload at sbi-kyc-2025.site",
        "Canara Bank: Account dormant. Reactivate by sharing last 4 transactions at canara-activate.in"
    ],
    
    # 3. Investment/Trading Scams (77% of 2025 losses - HIGHEST LOSSES)
    "investment":  [
        "Invest ₹10,000 in our crypto scheme, earn 20% daily returns! Join WhatsApp group: wa.me/91XXXXXXXX",
        "You've been selected for exclusive stock tips. Transfer ₹5000 to UPI: trading@paytm for insider info",
        "Bitcoin doubling offer! Send any amount, get 2X back in 24 hours. Limited time: btc-double.site",
        "Forex trading alert! Turn ₹1000 into ₹10000 in one week. Register now with ₹500 membership fee",
        "IPO special: Get Zomato shares before listing. Pay ₹25,000 to reserve allocation. Huge profits!",
        "Mutual fund returns 50% quarterly! Government backed. Minimum investment ₹20,000. Act fast!",
        "Join our stock market telegram group. ₹1500 lifetime. 100% accurate calls. Never lose money!",
        "Real estate investment opportunity! 500% returns in 6 months. Book with ₹50,000 token amount",
        "Gold trading scheme approved! Invest ₹15,000, get ₹3000 monthly passive income forever",
        "SEBI registered firm offering 40% annual returns. Deposit ₹30,000 minimum. Tax-free earnings!"
    ],
    
    # 4. Digital Arrest Scams (8% losses, trending up)
    "digital_arrest": [
        "This is CBI calling. You're under digital arrest for money laundering. Stay on video call to verify identity",
        "ED notice: Arrest warrant issued in your name. Share screen immediately or face legal action",
        "Cyber Crime department: Your Aadhaar linked to terror funding case. Pay ₹50,000 fine to avoid jail",
        "Supreme Court order: Digital arrest activated. Join Zoom call to clear charges or FIR will be filed",
        "Income Tax raid pending at your address. Transfer ₹1,00,000 settlement or officers coming tomorrow",
        "Mumbai Police: Drugs parcel sent from your address. Pay ₹75,000 penalty or 10 years imprisonment",
        "Ministry of Home Affairs: Suspicious activity detected. Join video call with officer or legal notice issued",
        "Customs department: Illegal gold import in your name. Clear dues ₹2,00,000 or arrest tomorrow 6 AM",
        "RBI fraud case registered against you. Cooperate via video call or account seizure. Share OTP now",
        "Narcotics Bureau: Your number linked to drug case. Pay ₹85,000 bail amount urgently to close"
    ],
    
    # 5. Credit Card/Loan Approval Scams (7% losses)
    "credit_loan": [
        "Your credit card limit increased to ₹5 lakh! Click to activate: hdfc-card-upgrade.site",
        "Instant loan approved for ₹50,000! Share OTP to disburse amount in 10 minutes. No documents!",
        "Pre-approved personal loan ₹2 lakh at 0% interest for students. Pay ₹1000 processing fee only",
        "SBI Credit card application approved! Lifetime free. Submit ₹500 courier charges for delivery",
        "Gold loan sanctioned ₹3 lakh instantly. Transfer ₹2000 documentation fee to get cash today",
        "Your CIBIL score improved! Get credit card ₹10 lakh limit. Activation charge ₹1500 one-time",
        "Education loan ₹10 lakh approved in 5 minutes! Pay ₹5000 verification fee. No guarantor needed",
        "Business loan ready for ₹25 lakh. Interest-free first year. Send ₹10000 processing ASAP",
        "Paytm Postpaid increased to ₹1 lakh! Confirm by sharing OTP. Shop now, pay after 30 days!",
        "Car loan pre-sanctioned ₹8 lakh. 100% finance. Pay ₹3000 agreement charges. Drive today!"
    ],
    
    # 6. Lottery/Prize Winner Scams (41% falls)
    "lottery_prize": [
        "You've won ₹1 crore in KBC lottery! Pay tax ₹25,000 to claim prize via UPI: kbc@paytm",
        "Prize alert: iPhone 15 Pro won in lucky draw! Verify details at iphone-winner.site & pay ₹2000 shipping",
        "Congratulations! ₹50 lakh Jio lottery winner. Transfer ₹10000 income tax to receive cheque",
        "WhatsApp anniversary giveaway! You won ₹25 lakh. Claim at whatsapp-prize.com with ₹5000 fee",
        "Google Play lucky draw: MacBook Air winner! Pay ₹3000 customs duty for international delivery",
        "IPL bumper prize ₹75 lakh! Your number drawn. Send Aadhaar + ₹15000 processing to claim",
        "Amazon Great Indian Sale winner! ₹2 lakh gift voucher. Activate with ₹1000 verification charge",
        "State lottery jackpot ₹1.5 crore! Government tax ₹50000 must be paid first. Deadline 24 hours",
        "Flipkart Big Billion Days: Grand prize ₹10 lakh won! Courier charges ₹2500 to send cheque",
        "Kaun Banega Crorepati lucky winner! ₹40 lakh prize. Pay ₹8000 TDS immediately to Big B's account"
    ],
    
    # 7. Fake Delivery/FedEx Scams (23% falls)
    "delivery_scam": [
        "Your package held at customs due to illegal contents. Pay ₹5000 fine or face arrest. Call: 9876543210",
        "FedEx alert: Delivery address incomplete. Update immediately at fedex-india-update.site or parcel returned",
        "DHL shipment pending: ₹3000 customs duty unpaid. Pay now at dhl-customs-pay.com or package destroyed",
        "India Post: Registered parcel №5478 requires ₹1500 clearance fee. Collect from indiapost-track.in",
        "BlueDart urgent: Your iPhone order stuck. Pay ₹2000 processing or delivery cancelled forever",
        "Amazon shipment delayed: Wrong pin code. Update + pay ₹500 rescheduling charge or order auto-refund",
        "Aramex courier: International parcel has suspicious item. Pay ₹10000 inspection fee or police case filed",
        "DTDC alert: COD amount ₹8000 declined. Retry payment at dtdc-retry.site within 2 hours or RTO",
        "Customs Department: Your parcel contains prohibited goods. Clear ₹15000 penalty at customs-clear.in",
        "Ecom Express: Failed delivery attempt 3/3. Pay ₹1000 redelivery charge or parcel auctioned tomorrow"
    ],
    
    # 8. Sextortion/Blackmail Scams (4% losses, highly sensitive)
    "sextortion": [
        "I have your private video from webcam. Pay ₹50,000 in Bitcoin or I send to all contacts within 24hrs",
        "Your browsing history recorded. Explicit sites visited. Pay ₹30000 to delete or family gets video",
        "Hi, remember me from dating app? Send ₹25000 or I share our intimate chat screenshots publicly",
        "Your email account hacked. I have compromising photos. Transfer ₹40000 Bitcoin or leak everywhere",
        "Recorded you through phone camera. Very embarrassing footage. Pay ₹20000 urgently or upload on social media",
        "We have your WhatsApp messages with affair partner. Pay ₹35000 or screenshots sent to spouse",
        "Your laptop webcam was hacked 3 months ago. Have 50+ private videos. ₹1 lakh or release online",
        "Downloaded all your private photos from cloud. Pay ₹60000 Bitcoin or leak to Facebook friends list",
        "Malware installed on your device. Recorded everything. ₹45000 ransom or blackmail continues forever",
        "Your Instagram DMs exposed. Very inappropriate content. Pay ₹15000 or screenshots viral on Twitter"
    ],
    
    # 9. OLX/Marketplace Scams
    "marketplace_scam": [
        "Interested in your ad for iPhone. Scan this QR code to receive ₹35000 payment directly to account",
        "Army officer buying your laptop. Can't meet. Transfer ₹2000 shipping fee first, I'll pay full amount",
        "Want to purchase your bike. Send me Google Pay request for ₹500 token money to hold till weekend",
        "Buying your sofa set. I'm in different city. My agent will collect. First send ₹1000 for transport booking",
        "Your phone ad looks good! Send UPI ID, I'll transfer ₹18000 advance. Pickup arranged for tomorrow",
        "Interested in camera for sale. Can you pay ₹300 OLX premium listing fee? I'll refund + full payment",
        "Buying your car urgently. Bank transfer needs your account screenshot. Share for ₹5 lakh payment",
        "Your product perfect! Clicked payment link but says verify with ₹100 first. Can you do and I'll pay back?",
        "Sister's wedding, need gold urgently. Your ad ideal! Send ₹1500 for jeweler verification certificate",
        "Want refrigerator desperately! Pay ₹50 OLX delivery charge, I'll immediately transfer ₹12000 full"
    ],
    
    # 10. Impersonation/Friend-in-Need Scams
    "impersonation": [
        "Mom, lost my phone. Urgent need ₹20,000 for hospital. Send to this UPI: emergency@paytm please hurry!",
        "Hey bro, emergency abroad! Wallet stolen in Dubai. Wire money ₹35000 via Western Union ASAP",
        "Dad here. Phone broken, using friend's number. Accident happened. Need ₹50000 immediately for hospital bills",
        "Hi beta, Aunty speaking. Your father had heart attack. Pay ₹75000 surgery advance or doctor won't operate",
        "It's me Rahul! New number. Stuck at police station. Need ₹15000 bail urgently. Don't tell anyone pls",
        "Papa I'm crying. Boyfriend's family demanding ₹1 lakh or marriage off. Help me please, very urgent",
        "Son trapped in China! COVID quarantine facility charging $5000. Pay via UPI: china-rescue@paytm now!",
        "Your cousin Priya. Met accident, phone damaged. Medical emergency ₹30000 needed. Send fast to survive",
        "Mama here. Lost in Mumbai, don't know what to do. Need ₹10000 for ticket home. Please beta help",
        "Your brother arrested for driving! Fine ₹40000 must pay today 5 PM or jail. Send immediately"
    ]
}

# Expected classification for each
SCAM_TYPE_MAPPING = {
    "fake_job": ["fake_job", "job_offer"],
    "bank_phishing": ["phishing", "bank_fraud"],
    "investment": ["investment"],
    "digital_arrest": ["legal_threat", "authority_impersonation"],
    "credit_loan": ["credit_loan", "fake_loan"],
    "lottery_prize": ["lottery_prize", "scholarship"],  # Similar pattern
    "delivery_scam": ["delivery_scam"],
    "sextortion": ["sextortion", "blackmail"],
    "marketplace_scam": ["marketplace_scam", "gig_scam"],  # Similar
    "impersonation": ["impersonation"]
}


def get_scam_statistics():
    """Get statistics about the dataset."""
    total = sum(len(examples) for examples in INDIAN_SCAM_DATASET.values())
    stats = {
        "total_examples": total,
        "scam_types": len(INDIAN_SCAM_DATASET),
        "examples_per_type": {k: len(v) for k, v in INDIAN_SCAM_DATASET.items()}
    }
    return stats


if __name__ == "__main__":
    stats = get_scam_statistics()
    print("=" * 70)
    print("COMPREHENSIVE INDIAN SCAM DATASET")
    print("=" * 70)
    print(f"\nTotal Examples: {stats['total_examples']}")
    print(f"Scam Types: {stats['scam_types']}")
    print("\nExamples per type:")
    for scam_type, count in stats['examples_per_type'].items():
        print(f"  {scam_type}: {count}")
