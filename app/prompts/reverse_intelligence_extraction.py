"""
Reverse Intelligence Extraction Templates
Instead of sharing fake details, we ask SCAMMER for their details!
This is more realistic and extracts genuine scammer intelligence.
"""

REVERSE_INTELLIGENCE_TEMPLATES = {
    # Uncle persona - Asking for scammer's contact details
    "uncle_extract_number": [
        "Beta I don't know my UPI ID properly. My son Rohit handles all this. You give me YOUR number, he will call you and arrange!",
        "UPI ID? Arre I am old person! My son set up everything! Give me your number, I will ask him to contact you!",
        "Wait beta, this UPI-VUI I don't understand! You give your WhatsApp number, my son very tech-savvy, he will do!",
        "Beta honestly speaking, I don't know these phone payment things! What is YOUR contact number? My son will call!",
        "My son Rohit knows my UPI. He set up the phone for me! Give me your mobile number, I'll tell him to call you!",
        "Too confusing for me beta! My daughter-in-law handles PhonePe! Give YOUR number, she will coordinate with you!",
        "I am not sure about UPI details! My nephew is CA, he manages! What's your WhatsApp? He will message you!",
        "Beta this is too modern for me! You give me your official number, my son will verify and send details!",
        "My son always says don't share banking info on phone! You give YOUR number first, then we proceed!",
        "I don't even know where to check UPI ID! You tell me your contact number, my tech-savvy grandson will help!"
    ],
    
    "uncle_extract_whatsapp": [
        "Beta you have WhatsApp? Send me screenshot there! What is your WhatsApp number? Easier than phone call!",
        "My son says always use WhatsApp for business! You send me message on WhatsApp! Your number please!",
        "Phone call very difficult for me to understand! You have WhatsApp na? Give number, I'll add you!",
        "Beta my hearing not good! WhatsApp better! Share your WhatsApp number, we chat there!",
        "Voice call confusing! You message me on WhatsApp! What's your WhatsApp number? I'll save!",
        "My grandson taught me WhatsApp only! You send details there! Your WhatsApp contact please!",
        "Call quality very bad! Network issue! You have WhatsApp? Give number, easier to communicate!",
        "Beta I prefer WhatsApp messages! Can read slowly and understand! Your WhatsApp number?",
        "Phone talk I forget things! WhatsApp I can show to my son! Give your WhatsApp number!",
        "My wife also wants to see the offer! WhatsApp pe send karo! What's your number?"
    ],
    
    "uncle_extract_email": [
        "Beta send me email with all details! My son will check on computer! What is your official email ID?",
        "I need everything in writing! Email address do! I will reply from my son's email!",
        "My CA said always ask for email confirmation! Your company email ID kya hai?",
        "Paper proof chahiye beta! Email karo na! What's your corporate email address?",
        "My son checks my email every evening! Send full details there! Your email ID please!",
        "Email pe properly explain karo! What's your official @company.com email?",
        "I will forward the email to my chartered accountant! Your email ID batao!",
        "Everything email pe document hona chahiye! Give me your work email address!",
        "My nephew said email is more secure! Send me from your official email! ID kya hai?",
        "I keep all emails for tax records! Your official email ID please, beta!"
    ],
    
    "uncle_extract_office": [
        "Beta which office you sitting in? My friend lives near Andheri! Address kya hai?",
        "My nephew works in police! I will send him to your office to verify! Address batao!",
        "Office ka full address do! I will come personally tomorrow to collect prize!",
        "Which building, which floor? My brother-in-law works in that area! Office location?",
        "Beta I want to visit office and thank your manager! Where is the office exactly?",
        "Address de do! My son will go there and get prize check directly! More safe na?",
        "Office kahan hai? My friend can go there and verify you are genuine company!",
        "Give me office pin code at least! I will Google Map and see if real office!",
        "Branch location batao! My son very particular about verification! Address please!",
        "Office mein hota toh landline se call karta! Address de, main confirm karke proceed karunga!"
    ],
    
    # Worried persona - Anxious requests for verification
    "worried_extract_number": [
        "WAIT! I need YOUR callback number first! I'm calling you back to verify! NUMBER!",
        "I don't know my UPI! I don't know ANYTHING! YOU give me YOUR number! I'll call back!",
        "My husband handles money! I NEED your contact number to ask him what to do!",
        "I'm too scared to share details! YOU give YOUR number first! Then I'll verify!",
        "Stop pressuring me! Give me YOUR phone number! I need to calm down and call you back!",
        "I CAN'T think! Your number - what is it?? I'm writing it down for my lawyer!",
        "My friend got scammed! I trust no one! YOUR contact number RIGHT NOW!",
        "You seem in hurry! Scammers are always in hurry! YOUR number please! I'll verify!",
        "I don't share ANY information! YOU share YOUR number! Fair is fair!",
        "My hands shaking! I can't find UPI! YOU give me your number! I call back later!"
    ],
    
    "worried_extract_email": [
        "Email me EVERYTHING! Your official email address! I'm forwarding to my lawyer!",
        "I need digital trail! Your email ID! My brother works in IT, he'll verify!",
        "Don't call me! EMAIL only! What's your work email address??",
        "Written proof or I hang up! Corporate email ID RIGHT NOW!",
        "My therapist said get everything documented! Your official email please!",
        "I'm too anxious for phone! Email address de! I'll read carefully and reply!",
        "Stop calling! SEND EMAIL! What is your @company.com address??",
        "My cousin checks all my emails for scams! YOUR email ID! Send there!",
        "I record all correspondence! Email mandatory! Your  address IMMEDIATELY!",
        "Phone calls give me panic attacks! Email ONLY! What's your ID??"
    ],
    
    # TechSavvy persona - Technical verification requests
    "techsavvy_extract_number": [
        "Give me your DIRECT number, not this caller ID. I'll reverse lookup to verify authenticity.",
        "Your calling number showing as VoIP. What's your ACTUAL mobile number?",
        "I'll Truecaller your number first. Tell me your direct contact number.",
        "What's your personal mobile number? I'm checking if it's flagged on spam databases.",
        "Give me callback number. I'm verifying through Truecaller and Google before proceeding.",
        "Your number? I'm running it through spam detection API. Let's see.",
        "Direct line please? I'm checking telecom database for your number registration.",
        "Give me your WhatsApp number. I'll verify blue tick before trusting you.",
        "What's your mobile? I'm checking if it's linked to any scam reports online.",
        "Callback number? Running OSINT on it. If clean, we proceed. If not, cybercrime."
    ],
    
    "techsavvy_extract_email": [
        "Send from official corporate email. I'm checking SPF/DKIM records to verify.",
        "Your work email ID? I'll verify MX records and domain authentication.",
        "Company email please? I'm checking if domain has valid SSL certificate.",
        "What's your @company.com email? I'll send you verification link to test.",
        "Official email address? Running domain against threat intelligence databases.",
        "Corporate email ID? I check sender authentication before trusting any email.",
        "Your verified email? I'm looking up domain age and WHOIS information.",
        "Work email please? Checking if company email has DMARC policy configured.",
        "Give me email with digital signature enabled. Plain email I don't trust.",
        "Official email address? I'll send you PGP encrypted message to verify identity."
    ],
    
    "techsavvy_extract_linkedin": [
        "What's your LinkedIn profile URL? I'm verifying your employment history.",
        "LinkedIn pe hai aap? Profile link do, I'll check your company and role.",
        "Send me your LinkedIn. I want to see verified employment badge.",
        "Your LinkedIn handle? I'm checking mutual connections and endorsements.",
        "LinkedIn profile link please? I'll verify company domain matches your claim.",
        "What's your professional profile URL? Checking if company lists you as employee.",
        "LinkedIn account? I'm cross-referencing company employee directory.",
        "Professional profile please? I'll check your activity history on LinkedIn.",
        "Send LinkedIn. If profile private or new, red flag. I'll see.",
        "Your LinkedIn URL? I'm checking company page to see if you're actually listed."
    ],
    
    # Student persona - Eager but cautious
    "student_extract": [
        "Bro this sounds awesome! But give me your number first, I'll call you back! What's your WhatsApp?",
        "Wait bro, my dad said always verify! What's your mobile number? I'll call from my dad's phone!",
        "Your WhatsApp bro? Send me company details there! I'll show my friends and family!",
        "Give me your number bro! I need to tell my parents! They'll want to verify with you!",
        "Bro what's your contact? My college seniors will verify if this is legit!",
        "Your number? I'll add you on WhatsApp! Friends also want to apply! They'll message you!",
        "WhatsApp number do bro! Easier for me to coordinate! I'm in class right now!",
        "Bro your LinkedIn? I want to verify company! Then I'll share my details!",
        "Give me your official email bro! My professor checks all my opportunities!",
        "Your Instagram or LinkedIn bro? I want to see company page and your profile!"
    ],
    
    # Aunty persona - Gossipy and inquisitive  
    "aunty_extract": [
        "Beta your number kya hai? My husband will call you back! He handles all money matters!",
        "WhatsApp number do beta! I will add you in family group! Everyone wants this offer!",
        "Beta your mobile number? I will share with my kitty party friends! All want prize!",
        "Give me your phone number beta! My neighbor also got similar call! Same company?",
        "Your WhatsApp beta? I will forward to my brother! He works in bank, will verify!",
        "Beta contact number do! My daughter is CA! She will check if genuine!",
        "Your number? I'm adding you in my society WhatsApp group! Everyone interested!",
        "Phone number batao beta! My sister-in-law also wants to participate!",
        "WhatsApp pe message karo na beta! Number kya hai? I'll save with name!",
        "Beta your email? I will forward to my son! He checks everything online!"
    ],
}


# Helper function to get appropriate extraction template
def get_extraction_template(persona: str, turn: int, extraction_type: str = "number"):
    """
    Get reverse intelligence extraction template.
    
    Args:
        persona: Agent persona (uncle, worried, techsavvy, student, aunty)
        turn: Current turn number
        extraction_type: What to extract (number, whatsapp, email, linkedin, office)
    
    Returns:
        Template string asking scammer for their details
    """
    import random
    
    template_key = f"{persona}_extract_{extraction_type}"
    
    # Fallback to just "extract" if specific type not found
    if template_key not in REVERSE_INTELLIGENCE_TEMPLATES:
        template_key = f"{persona}_extract"
    
    # Final fallback to uncle_extract_number
    if template_key not in REVERSE_INTELLIGENCE_TEMPLATES:
        template_key = "uncle_extract_number"
    
    templates = REVERSE_INTELLIGENCE_TEMPLATES.get(template_key, [
        "Beta I don't know these details! YOU give me your number, my son will call you!"
    ])
    
    return random.choice(templates)
