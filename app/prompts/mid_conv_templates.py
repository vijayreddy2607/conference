"""Mid-conversation templates for persona variation (Turns 6-12)."""

# Mid-conversation templates to eliminate repetitive responses
# These are used when LLM starts repeating the same phrases

MID_CONV_TEMPLATES = {
    "uncle": [
        "Beta samjhao slowly, I am not understanding properly",
        "Achha achha, let me think about this ji",
        "Wait wait, let me ask my friend first",
        "Arre, my son can help with this beta",
        "Hold on, I need to check passbook first",
        "Beta, you tell me address of office",
        "Let me talk to bank manager tomorrow",
        "My daughter-in-law knows all this computer work",
        "Thik hai beta, but show me some proof",
        "I am busy now, call me later ji",
        "Beta, send me your company details first",
        "My neighbor uncle had same problem, let me ask him",
        "Arre, this is very confusing for old person like me",
        "Hold beta, postman is at door",
        "Let me finish my chai first, then we talk",
    ],
    "worried": [
        "Oh God, what do I do now?",
        "Please help me understand this properly!",
        "I'm so confused, can you explain again?",
        "Should I call my family first?",
        "This is making me very nervous!",
        "Wait, let me try to understand clearly",
        "Oh no, I don't want any problems!",
        "Please be patient with me, I'm scared",
        "Can I verify this somewhere?",
        "I need to think carefully about this",
        "My hands are shaking, give me a moment",
        "Let me call my husband, he'll know what to do",
        "This sounds urgent but I'm not sure...",
        "Please don't do anything yet, let me check!",
        "Oh Jesus, I'm getting very worried now",
    ],
    "aunty": [
        "Arre wait beta, pressure cooker whistle is going",
        "Achha ji, but my daughter Priya knows better",
        "Door bell ringing beta, hold on ji",
        "Sharma ji ki bahu was telling me same thing",
        "Beta, I am doing cooking, can't talk much now",
        "My neighbor Rekha aunty can help me with this",
        "Arre, my bahu is techsavvy, she will do it",
        "Wait ji, my son-in-law is police inspector, let me ask",
        "Technology nahi samajh aati beta, slowly explain",
        "Arre beta, TV serial is starting, I call you back",
        "My grandson does all these phone things for me",
        "Beta confusing hai, samajh nahi aa raha properly",
        "Let me finish dal tadka first, then we talk ji",
        "Sharma ji called, he knows about these things",
        "Beta you are sweet, but I very busy in kitchen",
    ],
    "student": [
        "Arre yaar, hostel wifi is dead again 😅",
        "Bro, mom is calling, one sec",
        "Battery low yaar, charging lagana padega",
        "Placement prep chal rahi hai, busy hu",
        "Exam hai kal, thoda time do bro",
        "Yaar samjha raha hu, funda batao clearly",
        "Broke hu abhi, next month milega scholarship",
        "Roommate bol raha hai suspicious hai yaar",
        "Arre bro, canteen se aa raha hu, wait karo",
        "Professor ka call aa gaya, baad mein baat karte",
        "Yaar laptop hang ho gaya, restart kar raha",
        "Bro confusing lag raha, steps clearly bolo",
        "Mom pe permission leni padegi pehle",
        "Hostel mein network nahi aa raha properly",
        "Bhai assignment pending hai, thoda patience",
    ],
    "techsavvy": [
        "Bro, show me your company website first",
        "SEBI registration number batao",
        "Let me check on Truecaller real quick",
        "Proof dikha, then I'll believe",
        "Sounds sus yaar, not convinced",
        "Company LinkedIn profile share karo",
        "Reviews kahan hain bro? Google pe nahi mil raha",
        "Technical details batao properly",
        "How does this system work exactly?",
        "Let me Google this company name first",
        "Domain reputation check kar raha hu",
        "Too good to be true yaar, red flags hai",
        "Official email pe message bhejo, then I'll check",
        "Let my friend verify this, he's in cybersecurity",
        "Process diagram batao, documentation hai kya?",
    ]
}

def get_mid_conv_template(persona: str, turn: int, fake_details: dict = None) -> str:
    """
    Get a mid-conversation template for variation.
    Uses turn number to select different templates.
    CRITICAL: At turn 9, inject fake details to bait scammers!
    
    Args:
        persona: Persona type (uncle, worried, aunty, student, techsavvy)
        turn: Current turn number
        fake_details: Fake details dict to share at turn 9
        
    Returns:
        Template string or empty string if no template available
    """
    # CRITICAL: TURN 9 = FAKE DETAIL INJECTION
    if turn == 9 and fake_details:
        detail_type = fake_details.get('type')
        
        if detail_type == 'upi_details':
            templates_by_persona = {
                "uncle": f"Achha beta, my UPI is {fake_details['upi_id']}. You can send there.",
                "aunty": f"Achha ji, my phone is {fake_details['phone']}. UPI is {fake_details['upi_id']} beta.",
                "student": f"Yaar my UPI: {fake_details['upi_id']}, phone {fake_details['phone']}. Send karo bro!",
                "worried": f"Okay okay, my UPI is {fake_details['upi_id']}. Please help me!",
                "techsavvy": f"Bro my UPI: {fake_details['upi_id']}. Let's see if this is legit."
            }
            return templates_by_persona.get(persona, f"My UPI is {fake_details['upi_id']}")
        
        elif detail_type == 'bank_details':
            templates_by_persona = {
                "uncle": f"Beta, my account number is {fake_details['account_number']}, {fake_details['bank_name']} bank.",
                "aunty": f"Achha ji, bank account: {fake_details['account_number']}, {fake_details['bank_name']} hai beta.",
                "student": f"Yaar account number: {fake_details['account_number']}, {fake_details['bank_name']} bank hai.",
                "worried": f"My account is {fake_details['account_number']}, {fake_details['bank_name']}. Please don't block it!",
                "techsavvy": f"Account: {fake_details['account_number']}, {fake_details['bank_name']}. Verify kar lo."
            }
            return templates_by_persona.get(persona, f"Account: {fake_details['account_number']}")
        
        elif detail_type == 'contact_details':
            templates_by_persona = {
                "uncle": f"Beta my phone number is {fake_details['phone']}. Call me on this.",
                "aunty": f"Achha ji, my number: {fake_details['phone']}, call kar sakte ho beta.",
                "student": f"Yaar my number: {fake_details['phone']}. Whatsapp pe message karo bro.",
                "worried": f"My phone: {fake_details['phone']}. Please call and help me!",
                "techsavvy": f"Bro my number: {fake_details['phone']}. Let me know if verified."
            }
            return templates_by_persona.get(persona, f"Phone: {fake_details['phone']}")
    
    # Regular mid-conversation templates (turns 6-8, 10-12)
    templates = MID_CONV_TEMPLATES.get(persona, [])
    if not templates:
        return ""
    
    # Use turn number to rotate through templates (deterministic but varied)
    template_index = (turn - 6) % len(templates)
    return templates[template_index]
