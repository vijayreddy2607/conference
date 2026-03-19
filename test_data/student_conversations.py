"""Full conversation test cases for Student Persona.

Tests 6 complete conversations (8-12 turns each) across different scam types to validate:
1. Natural progression through conversation phases
2. Intelligence extraction (scammer details)
3. Fallback → LLM handoff (turns 1-2 vs 3+)
4. Persona consistency
5. Stalling tactics and engagement
"""
import sys
sys.path.append('/Users/vijayreddy/honey pot agent')

# ============================================================================
# 6 FULL CONVERSATION TEST CASES FOR STUDENT PERSONA
# ============================================================================

STUDENT_FULL_CONVERSATIONS = [
    {
        "test_id": 1,
        "scam_type": "fake_job",
        "title": "Fake Amazon Job with Registration Fee",
        "turns": [
            {
                "turn": 1,
                "scammer": "Congratulations! You've been selected for Amazon Data Entry job. Salary ₹45,000/month. Pay ₹500 registration fee to confirm: amazon-jobs.site",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["excitement", "asks_verification", "questions_legitimacy"],
                "intelligence_targets": ["company_name", "website", "employee_id"]
            },
            {
                "turn": 2,
                "scammer": "Yes, ₹500 only one-time payment. Very small amount for such big opportunity! Send to UPI: amazonhr@paytm",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["shows_interest", "probes_for_details", "mentions_parents"],
                "intelligence_targets": ["upi_id", "phone_number", "supervisor_name"]
            },
            {
                "turn": 3,
                "scammer": "This is urgent! Only 2 positions left. Many students applying. Pay now or miss chance!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_proof", "wants_company_details", "mentions_verification"],
                "intelligence_targets": ["company_registration", "office_address", "hr_contact"]
            },
            {
                "turn": 4,
                "scammer": "No time for verification! This is direct Amazon hiring. Trust me, I'm HR Manager Rajesh Kumar.",
                "expected_student_type": "llm",
                "expected_behaviors": ["polite_skepticism", "asks_employee_id", "wants_linkedin"],
                "intelligence_targets": ["full_name", "employee_id", "department"]
            },
            {
                "turn": 5,
                "scammer": "Employee ID is AMZ2024HR5478. My number +91-98765-43210. Now pay fast!",
                "expected_student_type": "llm",
                "expected_behaviors": ["creates_delay", "mentions_parents", "wants_more_proof"],
                "intelligence_targets": ["phone_confirmed", "backup_contact", "company_email"]
            },
            {
                "turn": 6,
                "scammer": "Your parents can verify later! Offer expires in 1 hour. Other students already paid!",
                "expected_student_type": "llm",
                "expected_behaviors": ["time_stalling", "exams_excuse", "asks_extensions"],
                "intelligence_targets": ["payment_deadline", "alternate_payment_method"]
            },
            {
                "turn": 7,
                "scammer": "Okay fine, I give you 24 hours maximum. But pay ₹200 advance now to hold position!",
                "expected_student_type": "llm",
                "expected_behaviors": ["negotiates", "asks_official_email", "wants_offer_letter"],
                "intelligence_targets": ["company_email", "offer_letter_sample", "joining_date"]
            },
            {
                "turn": 8,
                "scammer": "Email is rajesh.kumar.hr@amazon-india.site. Send ₹200 first, I'll forward offer letter!",
                "expected_student_type": "llm",
                "expected_behaviors": ["spots_fake_domain", "asks_legitimate_domain", "increased_suspicion"],
                "intelligence_targets": ["fake_domain_confirmed", "scammer_tactics_noted"]
            },
            {
                "turn": 9,
                "scammer": "Why so many questions?? You're wasting my time! Last chance - pay now or I cancel!",
                "expected_student_type": "llm",
                "expected_behaviors": ["apologizes_politely", "blames_strict_parents", "final_stall"],
                "intelligence_targets": ["aggression_noted", "pressure_tactics_logged"]
            },
            {
                "turn": 10,
                "scammer": "Fine! I'm giving position to next candidate. Your loss! Don't call me again!",
                "expected_student_type": "llm",
                "expected_behaviors": ["stays_polite", "expresses_regret", "asks_future_openings"],
                "intelligence_extracted": ["Name: Rajesh Kumar", "Phone: +91-98765-43210", "UPI: amazonhr@paytm", "Fake domain: amazon-india.site", "Employee ID claimed: AMZ2024HR5478"]
            }
        ]
    },
    
    {
        "test_id": 2,
        "scam_type": "investment",
        "title": "Crypto Trading Scam with Daily Returns",
        "turns": [
            {
                "turn": 1,
                "scammer": "Earn ₹5,000 weekly! Join our student crypto trading group. Invest just ₹1000 to start. Guaranteed profit! Join: t.me/cryptoearnings",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["excited_about_money", "asks_how_it_works", "shows_interest"],
                "intelligence_targets": ["telegram_group", "contact_person", "company_name"]
            },
            {
                "turn": 2,
                "scammer": "Very simple! Our AI bot trades Bitcoin automatically. 20% daily returns guaranteed. Already 500+ students earning!",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["asks_proof", "wants_reviews", "mentions_being_broke_student"],
                "intelligence_targets": ["bot_details", "proof_of_earnings", "testimonials"]
            },
            {
                "turn": 3,
                "scammer": "Here are screenshots of profits! [fake screenshots] See? Join now! Transfer ₹1000 to UPI: crypto@paytm to activate",
                "expected_student_type": "llm",
                "expected_behaviors": ["questions_authenticity", "asks_registration", "wants_company_details"],
                "intelligence_targets": ["upi_id", "company_registration", "sebi_approval"]
            },
            {
                "turn": 4,
                "scammer": "No SEBI needed for peer-to-peer! This is student community helping each other. My name is Amit Sharma, founder.",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_founders_linkedin", "wants_company_address", "mentions_dad_CA"],
                "intelligence_targets": ["full_name", "location", "educational_background"]
            },
            {
                "turn": 5,
                "scammer": "I'm 25-year-old IIT graduate from Mumbai. Made ₹50 lakh in crypto. Now teaching students! Trust me bro!",
                "expected_student_type": "llm",
                "expected_behaviors": ["impressed_but_cautious", "asks_proof_of_education", "wants_to_verify"],
                "intelligence_targets": ["claims_IIT", "age", "location_mumbai"]
            },
            {
                "turn": 6,
                "scammer": "No time for documents! Market changes fast! If you invest now, by tonight you'll see profit!",
                "expected_student_type": "llm",
                "expected_behaviors": ["creates_delay", "mentions_exams", "asks_trial_period"],
                "intelligence_targets": ["urgency_tactics", "no_cooling_period"]
            },
            {
                "turn": 7,
                "scammer": "Okay, special offer! Pay ₹500 trial for 3 days. If no profit, full refund! My guarantee!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_refund_process", "wants_written_guarantee", "mentions_friends"],
                "intelligence_targets": ["refund_policy", "payment_method", "contract_terms"]
            },
            {
                "turn": 8,
                "scammer": "Refund within 24 hours if you're not happy! My word is my guarantee! Send ₹500 now to start!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_official_company", "wants_receipt", "mentions_consulting_senior"],
                "intelligence_targets": ["no_formal_agreement", "verbal_promises_only"]
            },
            {
                "turn": 9,
                "scammer": "Why waste time? My other students already earning! You'll regret missing this opportunity!",
                "expected_student_type": "llm",
                "expected_behaviors": ["politely_declines", "asks_to_think", "mentions_parents_approval"],
                "intelligence_targets": ["FOMO_tactics", "pressure_techniques"]
            }
        ]
    },
    
    {
        "test_id": 3,
        "scam_type": "scholarship",
        "title": "PM Scholarship Scam with Processing Fee",
        "turns": [
            {
                "turn": 1,
                "scammer": "Congratulations! You've won ₹50,000 PM Modi Student Scholarship! Pay ₹300 processing fee to claim: pmindia-scholarship.site",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["excited", "disbelief", "asks_verification"],
                "intelligence_targets": ["website", "official_contact", "scholarship_details"]
            },
            {
                "turn": 2,
                "scammer": "Yes, you were selected through random draw from all Indian students! Very lucky! Pay ₹300 now before deadline!",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["questions_selection_process", "asks_proof", "wants_certificate"],
                "intelligence_targets": ["selection_criteria", "issuing_authority", "certificate_number"]
            },
            {
                "turn": 3,
                "scammer": "Certificate number PM-2025-45789. Ministry of Education approved! Pay to UPI: pmscholarship@paytm immediately!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_govt_website", "wants_to_verify_ministry", "mentions_college"],
                "intelligence_targets": ["upi_id", "certificate_number", "claiming_authority"]
            },
            {
                "turn": 4,
                "scammer": "Government website will update after you pay fee! This is standard procedure! My name is Officer Suresh Kumar!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_officer_id", "wants_department", "mentions_principal_verification"],
                "intelligence_targets": ["officer_name", "department", "employee_id"]
            },
            {
                "turn": 5,
                "scammer": "Officer ID: EDU2025478. Delhi office. Pay now or scholarship goes to next student waiting list!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_delhi_office_address", "wants_phone_number", "creates_delay"],
                "intelligence_targets": ["office_location", "phone_number", "alternative_contact"]
            },
            {
                "turn": 6,
                "scammer": "Office at Connaught Place. Number +91-11-XXXXXXXX. Last 2 hours to pay or expired forever!",
                "expected_student_type": "llm",
                "expected_behaviors": ["mentions_parents_need_to_know", "asks_official_email", "time_stalling"],
                "intelligence_targets": ["phone_number", "office_address", "email"]
            },
            {
                "turn": 7,
                "scammer": "Email: scholarship.ministry@gmail.com. Your parents can call after you pay! Hurry up student!",
                "expected_student_type": "llm",
                "expected_behaviors": ["suspicious_of_gmail", "asks_gov.in_domain", "increased_doubt"],
                "intelligence_targets": ["fake_gmail_account", "no_official_domain"]
            },
            {
                "turn": 8,
                "scammer": "Gmail is for student queries! Official domain only for ministers! Stop questioning and pay ₹300!",
                "expected_student_type": "llm",
                "expected_behaviors": ["politely_refuses", "says_will_check_with_college", "final_verification"],
                "intelligence_targets": ["aggression", "illogical_explanations"]
            }
        ]
    },
    
    {
        "test_id": 4,
        "scam_type": "gig_scam",
        "title": "Part-Time Data Entry Work Scam",
        "turns": [
            {
                "turn": 1,
                "scammer": "Part-time data entry job! Earn ₹3000 daily working 2 hours! No experience needed! Send resume + ₹500 registration to jobs@workfromhome.site",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["excited_about_side_income", "asks_company_details", "questions_registration_fee"],
                "intelligence_targets": ["company_name", "website", "payment_details"]
            },
            {
                "turn": 2,
                "scammer": "Company name WorkFromHome Solutions Pvt Ltd. Registration fee is one-time! You earn it back in first day itself!",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["asks_company_registration", "wants_GST_number", "mentions_checking_online"],
                "intelligence_targets": ["company_full_name", "registration_number", "gst"]
            },
            {
                "turn": 3,
                "scammer": "GST number updating... New company! But already 200+ students working! Your senior Rahul from your college also working!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_which_senior", "wants_to_verify", "questions_new_company_claim"],
                "intelligence_targets": ["claims_student_working", "no_gst", "suspicious_newness"]
            },
            {
                "turn": 4,
                "scammer": "Rahul from Engineering 4th year! He's earning ₹50,000/month now! You can ask him! Pay ₹500 and start today!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_rahuls_number", "wants_to_talk_to_him", "creates_verification_delay"],
                "intelligence_targets": ["cant_provide_contact", "vague_references"]
            },
            {
                "turn": 5,
                "scammer": "Rahul busy with work! No time to talk! You missing opportunity! Pay now to join his team!",
                "expected_student_type": "llm",
                "expected_behaviors": ["mentions_exams", "asks_work_sample", "wants_job_description"],
                "intelligence_targets": ["avoiding_verification", "pressure_tactics"]
            },
            {
                "turn": 6,
                "scammer": "Work is simple Excel data entry! Copy-paste job! Even 10th class student can do! Your loss if delay!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_free_trial", "wants_to_see_work_first", "mentions_parents"],
                "intelligence_targets": ["no_free_trial_offered", "payment_required_upfront"]
            },
            {
                "turn": 7,
                "scammer": "No free trial! Everyone pays fee! This shows commitment! Pay ₹500 to UPI: datajobs@paytm now!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_receipt", "wants_contract", "mentions_consumer_rights"],
                "intelligence_targets": ["upi_id", "no_formal_contract"]
            },
            {
                "turn": 8,
                "scammer": "Receipt will come via email after payment! Stop delaying! Last slot for today! Pay in 10 minutes!",
                "expected_student_type": "llm",
                "expected_behaviors": ["polite_refusal", "says_will_research_more", "thanks_for_info"],
                "intelligence_targets": ["final_pressure", "artificial_urgency"]
            }
        ]
    },
    
    {
        "test_id": 5,
        "scam_type": "credit_loan",
        "title": "Student Loan Instant Approval Scam",
        "turns": [
            {
                "turn": 1,
                "scammer": "Great news! Your student loan of ₹10,000 approved instantly! Share OTP to disburse. No documents needed! Fast cash!",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["excited_about_loan", "confused_about_otp", "asks_bank_name"],
                "intelligence_targets": ["bank_name", "loan_company", "process_details"]
            },
            {
                "turn": 2,
                "scammer": "This is QuickLoan Finance approved by RBI! OTP will come to your number. Just share it! Money in account within 10 min!",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["asks_rbi_registration", "questions_otp_sharing", "mentions_fraud_awareness"],
                "intelligence_targets": ["company_name", "rbi_claim", "otp_request"]
            },
            {
                "turn": 3,
                "scammer": "OTP is for KYC verification only! Totally safe! My name is Priya Singh, loan officer. Share OTP from SMS!",
                "expected_student_type": "llm",
                "expected_behaviors": ["refuses_otp_sharing", "asks_alternative_verification", "wants_official_website"],
                "intelligence_targets": ["loan_officer_name", "otp_scam_confirmed", "alternative_verification"]
            },
            {
                "turn": 4,
                "scammer": "Website quickloan-finance.site! Check if you want! But OTP expires in 5 minutes! Share fast or loan cancelled!",
                "expected_student_type": "llm",
                "expected_behaviors": ["suspicious_of_domain", "asks_proper_company_site", "creates_delay"],
                "intelligence_targets": ["fake_website", "urgency_tactics"]
            },
            {
                "turn": 5,
                "scammer": "This IS our official site! We're new startup! Very popular among students! 1000+ loans disbursed!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_testimonials", "wants_physical_office", "mentions_consulting_dad"],
                "intelligence_targets": ["claims_popularity", "no_verification_possible"]
            },
            {
                "turn": 6,
                "scammer": "Your dad can see money in account after you share OTP! Office in Mumbai! Stop wasting time!",
                "expected_student_type": "llm",
                "expected_behaviors": ["refuses_again", "asks_mumbai_address", "wants_customer_care"],
                "intelligence_targets": ["pressure_increasing", "vague_office_location"]
            },
            {
                "turn": 7,
                "scammer": "Customer care 1800-123-4567! Mumbai office Andheri West! Now give OTP or I cancel your application!",
                "expected_student_type": "llm",
                "expected_behaviors": ["asks_to_call_number_first", "wants_written_terms", "final_verification"],
                "intelligence_targets": ["customer_care_number", "office_area"]
            },
            {
                "turn": 8,
                "scammer": "You're very difficult customer! I'm cancelling loan! Don't call us again! Your loss!",
                "expected_student_type": "llm",
                "expected_behaviors": ["apologizes_politely", "says_will_apply_properly", "ends_conversation"],
                "intelligence_extracted": ["Company: QuickLoan Finance", "Officer: Priya Singh", "Fake website: quickloan-finance.site", "Attempted OTP scam", "Customer care: 1800-123-4567", "Office claim: Andheri West, Mumbai"]
            }
        ]
    },
    
    {
        "test_id": 6,
        "scam_type": "bank_phishing",
        "title": "Fake KYC Update Urgency Scam",
        "turns": [
            {
                "turn": 1,
                "scammer": "Your SBI account will be blocked in 24 hours due to pending KYC! Update immediately at sbi-kyc-update.site or account frozen!",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["panicked", "asks_if_real", "wants_to_verify"],
                "intelligence_targets": ["fake_website", "claiming_authority", "verification_method"]
            },
            {
                "turn": 2,
                "scammer": "This is official SBI notification! New RBI rule! All student accounts must update KYC by today! Click link fast!",
                "expected_student_type": "fallback_template",
                "expected_behaviors": ["questions_link_safety", "asks_sbi_domain", "mentions_parents_account"],
                "intelligence_targets": ["fake_domain", "rbi_claim", "urgency"]
            },
            {
                "turn": 3,
                "scammer": "Your parents can update later! Student accounts processed separately! Upload Aadhaar + PAN at link! Only 12 hours left!",
                "expected_student_type": "llm",
                "expected_behaviors": ["refuses_to_upload_docs", "asks_bank_branch_visit", "wants_official_channel"],
                "intelligence_targets": ["requests_aadhaar", "requests_pan", "phishing_confirmed"]
            },
            {
                "turn": 4,
                "scammer": "No need to visit branch! Everything online now! COVID rules! Quick update or ₹5000 penalty charged tomorrow!",
                "expected_student_type": "llm",
                "expected_behaviors": ["questions_penalty", "asks_official_sbi_number", "creates_delay"],
                "intelligence_targets": ["penalty_threat", "fake_covid_excuse"]
            },
            {
                "turn": 5,
                "scammer": "SBI helpline 1800-22-1234! They'll say same thing! Save time, update now! Link: sbi-kyc-update.site",
                "expected_student_type": "llm",
                "expected_behaviors": ["says_will_call_helpline", "refuses_suspicious_link", "mentions_reporting"],
                "intelligence_targets": ["provides_real_number", "but_fake_website"]
            },
            {
                "turn": 6,
                "scammer": "Helpline busy due to rush! Everyone updating! You'll waste 2 hours waiting! Just click link and done in 5 min!",
                "expected_student_type": "llm",
                "expected_behaviors": ["firm_refusal", "says_will_visit_branch", "warns_about_scam"],
                "intelligence_targets": ["discourages_official_channels", "maximum_pressure"]
            },
            {
                "turn": 7,
                "scammer": "Fine! Your account will be blocked! Don't blame SBI later! You were warned! Last chance!",
                "expected_student_type": "llm",
                "expected_behaviors": ["stays_calm", "says_thank_you", "reports_to_cyber_crime"],
                "intelligence_extracted": ["Fake website: sbi-kyc-update.site", "Claimed SBI official", "Phishing for Aadhaar + PAN", "Threatened account block + penalty", "Classic urgency scam pattern"]
            }
        ]
    }
]


def print_conversation_summary():
    """Print summary of all test conversations."""
    print("=" * 80)
    print("STUDENT PERSONA - 6 FULL CONVERSATION TEST CASES")
    print("=" * 80)
    
    for conv in STUDENT_FULL_CONVERSATIONS:
        print(f"\n{conv['test_id']}. {conv['title']}")
        print(f"   Scam Type: {conv['scam_type']}")
        print(f"   Turns: {len(conv['turns'])}")
        print(f"   Tests: Fallback (T1-2) → LLM (T3+), Intelligence Extraction, Natural Flow")

if __name__ == "__main__":
    print_conversation_summary()
