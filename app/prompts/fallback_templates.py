"""Static fallback templates for Indian personas (First 2 Turns).

These templates ensure:
1. Immediate, high-quality response (no latency)
2. Authentic Hinglish phrasing (research-backed)
3. "Proper chat" feel before switching to dynamic LLM

Usage:
    template = FALLBACK_TEMPLATES[persona_type][turn_number].format(
        scam_type=scam_type, 
        reference_history=last_message_snippet
    )
"""

FALLBACK_TEMPLATES = {
    "aunty": {
        1: "Arre beta, kya hua? Batao properly... I don't understand all this. What you want?",
        2: "Haan haan beta... {reference_history} samjhao properly? Number do call kar lun?"
    },
    
    "techsavvy": {
        1: "Hey, what's this about? Sounds interesting bro... share more details?",
        2: "Wait... {reference_history} explain properly? Send email or number please?"
    },
    
    "student": {
        1: "Bro what? Really? 😳 Thik hai sounds good! What I need to do... batao?",
        2: "Cool ok! But... {reference_history} samjhao yaar? Link ya details share karo?"
    },
    
    "worried": {
        1: "What?! Oh no... 😰 kya problem hai? Please tell me what happened... what I should do?",
        2: "Arre yaar panic ho raha... {reference_history} kaise fix? Number ya link dedo please?"
    },
    
    "uncle": {
        1: "Haan beta, kya baat hai? I got your message... thik se batao what is this about?",
        2: "Achha ji... {reference_history} samjhao properly? Number ya details do check karun."
    }
}
