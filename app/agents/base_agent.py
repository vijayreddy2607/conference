"""Base agent - HYBRID approach: Fast fallback first, LLM later."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.utils.llm_client import llm_client
from app.utils.human_behavior import make_human
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import logging
import asyncio
import random

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base agent with HYBRID strategy for guaranteed fast responses."""
    
    def __init__(self, persona_name: str):
        self.persona_name = persona_name
        self.conversation_memory: List[Dict[str, str]] = []
        self.internal_notes: List[str] = []
        self.trust_level = 0.0
        self.asked_questions: List[str] = []
        self.current_phase = 0
        self._last_responses = []  # For repetition detection (Version 2.2)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass
    
    @abstractmethod
    def get_few_shot_examples(self) -> List[Dict[str, str]]:
        pass
    
    def verify_response_quality(self, response: str, scammer_msg: str, turn_count: int) -> dict:
        """
        Version 2.2 - Double Verification Layer
        Validates response before sending to ensure quality and safety
        Returns: {"passed": bool, "reason": str}
        """
        # Check 1: Not empty or too short
        if not response or len(response.strip()) < 10:
            return {"passed": False, "reason": "Response too short"}
        
        # Check 2: No exact repetition with last 3 responses
        if response in self._last_responses[-3:]:
            return {"passed": False, "reason": "Exact repetition detected"}
        
        # Check 3: Contextual relevance (shares words or asks question)
        scammer_words = set(w.lower() for w in scammer_msg.split() if len(w) > 3)
        response_words = set(w.lower() for w in response.split() if len(w) > 3)
        has_overlap = len(scammer_words & response_words) > 0
        has_question = "?" in response
        
        if not has_overlap and not has_question and turn_count > 1:
            return {"passed": False, "reason": "Not contextual to scammer message"}
        
        # Check 4: No real personal info leaked (critical security check)
        dangerous_patterns = [
            "aadhaar", "aadhar", "pan card", "account number",
            "cvv", "otp", "password", "real name", "actual address"
        ]
        response_lower = response.lower()
        for pattern in dangerous_patterns:
            if pattern in response_lower:
                return {"passed": False, "reason": f"Leaking sensitive info: {pattern}"}
        
        # Check 5: Persona-appropriate length (different for each persona)
        max_lengths = {
            "uncle": 200,
            "aunty": 200,
            "worried": 250,  # Can be more verbose when panicked
            "student": 150,
            "techsavvy": 150
        }
        max_len = max_lengths.get(self.persona_name.lower().split()[0], 180)
        if len(response) > max_len:
            return {"passed": False, "reason": f"Too verbose ({len(response)} > {max_len} chars)"}
        
        # All checks passed!
        return {"passed": True, "reason": "OK"}
    
    
    async def generate_response(
        self,
        scammer_message: str,
        conversation_history: List[Dict[str, Any]] = None,
        additional_context: str = ""
    ) -> str:
        """
        NEW APPROACH - LLM-GUIDED CONTEXTUAL RESPONSES:
        - ALL TURNS (1+): Use LLM with templates as STYLE GUIDES (not direct responses)
        - LLM considers BOTH template style AND scammer's actual message
        - Fallback templates only used if LLM fails
        - All responses enhanced with human-like typos and errors
        """
        # Count only scammer messages (conversation_history has both scammer+agent)
        turn_count = len([msg for msg in (conversation_history or []) if msg.get("sender") == "scammer"])
        
        logger.info(f"🎯 {self.persona_name} Turn {turn_count}: LLM-guided response (template as style guide)")
        
        # RETRY CONFIGURATION - CRITICAL: Keep short for GUVI compliance!
        max_attempts = 2
        timeout_values = [3.0, 2.0]  # REDUCED: 3s first attempt, 2s retry (was 10s/8s)
        
        for attempt in range(max_attempts):
            try:
                current_timeout = timeout_values[min(attempt, len(timeout_values)-1)]
                logger.info(f"⚡ LLM attempt {attempt+1}/{max_attempts}, timeout: {current_timeout}s")
                
                # Build enriched prompt with template guidance
                messages = []
                
                # Enhanced system prompt with style guidance
                system_prompt = self.get_system_prompt()
                
                # Add template usage instructions
                system_prompt += """

🎭 IMPORTANT INSTRUCTIONS:
1. You will see template examples below - these show your SPEAKING STYLE and TONE
2. DO NOT copy templates directly - they are just examples!
3. USE the style/tone from templates, but RESPOND to what the scammer ACTUALLY said
4. Make your response RELEVANT and CONTEXTUAL to the scammer's message
5. Sound natural and human-like, not robotic

⚡ CRITICAL - KEEP IT SHORT:
• Maximum 1-2 sentences (aim for 50-150 characters)
• NO long stories or explanations
• NO multiple topics in one response
• Think like a real chat message - SHORT and PUNCHY
• If you have a long thought, pick the MOST IMPORTANT part only

ALWAYS respond to the scammer's actual message while maintaining your persona's style!
SHORT RESPONSES ONLY - this is a chat, not an essay!"""
                
                if additional_context:
                    system_prompt += f"\n\n{additional_context}"
                
                messages.append(SystemMessage(content=system_prompt))
                
                # Add 2-3 examples to show style (not to copy)
                for example in self.get_few_shot_examples()[:3]:
                    messages.append(HumanMessage(content=example["scammer"]))
                    agent_key = next((k for k in ["uncle", "worried", "techsavvy", "aunty", "student"] if k in example), None)
                    if agent_key:
                        messages.append(AIMessage(content=example[agent_key]))
                
                # Add recent conversation history (last 4 messages)
                if conversation_history:
                    for msg in conversation_history[-4:]:
                        if msg.get("sender") == "scammer":
                            messages.append(HumanMessage(content=msg.get("text", "")))
                        else:
                            messages.append(AIMessage(content=msg.get("text", "")))
                
                # Add current scammer message
                messages.append(HumanMessage(content=scammer_message))
                
                # TRY LLM WITH CURRENT TIMEOUT
                response = await asyncio.wait_for(
                    llm_client.ainvoke(messages), 
                    timeout=current_timeout
                )
                
                # SUCCESS! We have LLM response
                response_text = response
                
                # Stage 3.6: DOUBLE VERIFICATION (Version 2.2 - Humanization Layer)
                # Verify response quality before sending
                verification = self.verify_response_quality(response_text, scammer_message, turn_count)
                
                if not verification["passed"]:
                    logger.warning(f"⚠️  Response failed verification: {verification['reason']}")
                    logger.info(f"🔄 Using fallback template instead")
                    # Use fallback instead of bad response
                    response_text = self._get_stateful_fallback(scammer_message, turn_count)
                else:
                    logger.info(f"✅ Response passed verification: {verification['reason']}")
                
                # Update state and add human imperfections
                self._update_state(scammer_message, response_text)
                response_text = make_human(response_text, persona=self._get_persona_type(), turn_count=turn_count)
                
                # Track response for future repetition detection
                self._last_responses.append(response_text)
                if len(self._last_responses) > 5:  # Keep only last 5
                    self._last_responses.pop(0)
                
                logger.info(f"✅ LLM SUCCESS on attempt {attempt+1}/{max_attempts} ({current_timeout}s)")
                logger.info(f"📝 Generated contextual response (not direct template)")
                return response_text
                
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ LLM attempt {attempt+1}/{max_attempts} TIMEOUT after {current_timeout}s")
                
                if attempt < max_attempts - 1:
                    # Not last attempt - wait briefly and retry
                    logger.info(f"🔄 Retrying LLM in 0.3s...")
                    await asyncio.sleep(0.3)
                    continue  # Next iteration
                else:
                    # Last attempt failed - use fallback as emergency
                    logger.warning(f"❌ All {max_attempts} LLM attempts FAILED, using fallback template")
                    response = self._get_stateful_fallback(scammer_message, turn_count)
                    self._update_state(scammer_message, response)
                    response = make_human(response, persona=self._get_persona_type(), turn_count=turn_count)
                    return response
                    
            except Exception as e:
                logger.error(f"❌ LLM attempt {attempt+1}/{max_attempts} ERROR: {str(e)[:100]}")
                
                if attempt < max_attempts - 1:
                    # Not last attempt - retry
                    logger.info(f"🔄 Retrying after error...")
                    await asyncio.sleep(0.3)
                    continue
                else:
                    # Last attempt - fallback
                    logger.error(f"❌ All {max_attempts} attempts exhausted, using fallback")
                    response = self._get_stateful_fallback(scammer_message, turn_count)
                    self._update_state(scammer_message, response)
                    response = make_human(response, persona=self._get_persona_type(), turn_count=turn_count)
                    return response
        
        # Should never reach here but just in case
        response = self._get_stateful_fallback(scammer_message, turn_count)
        self._update_state(scammer_message, response)
        response = make_human(response, persona=self._get_persona_type(), turn_count=turn_count)
        return response
    
    def _get_persona_type(self) -> str:
        """Get persona type for human behavior enhancement."""
        persona_lower = self.persona_name.lower()
        if "aunty" in persona_lower or "sunita" in persona_lower:
            return "aunty"
        elif "student" in persona_lower or "arjun" in persona_lower:
            return "student"
        elif "worried" in persona_lower:
            return "worried"
        elif "tech" in persona_lower:
            return "techsavvy"
        else:
            return "uncle"
    
    def _get_stateful_fallback(self, scammer_message: str, turn_count: int) -> str:
        """Stateful fallback - progresses through intelligence gathering."""
        
        if "Uncle" in self.persona_name:
            return self._get_uncle_stateful_fallback(turn_count)
        elif "Worried" in self.persona_name:
            return self._get_worried_stateful_fallback(turn_count)
        elif "TechSavvy" in self.persona_name:
            return self._get_techsavvy_stateful_fallback(turn_count)
        elif "Aunty" in self.persona_name or "Sunita" in self.persona_name:
            # Aunty agent handles her own fallback
            return "Hayy! This is nice beta! Tell me more..."
        elif "Student" in self.persona_name or "Arjun" in self.persona_name:
            # Student agent handles their own fallback
            return "Wait bro, is this legit? Can u send details?"
        return "Sorry, I don't understand. Can you explain again?"
    
    def _get_uncle_stateful_fallback(self, turn_count: int) -> str:
        """Uncle progression with MAXIMUM variation for 75%+ uniqueness."""
        responses = [
            # Turn 0 (Ask Bank) - NOW 10 OPTIONS!
            [
                "Arre beta! What happened? Which bank/company are you calling from? Tell me properly",
                "Beta tell me slowly, what is the problem? Which bank is this?",
                "I am not understanding beta. Who is calling? From where?",
                "Kya baat hai beta? I got SMS from you... very confused! Who are you?",
                "Hayy! This is surprising! What you want to tell me? Explain properly!",
                "Oh ho! Phone ringing so much today. You are from which office?",
                "Beta actually I am busy with puja right now. But tell me quick what happened?",
                "Namaste ji! You called on my Jio number. I just got this phone. What is matter?",
                "Arre! You sound like my son's friend. Which company this is? Tell fast!",
                "Wait wait, let me switch off this TV... yes beta, I am hearing you now. What?"
            ],
            # Turn 1 (Ask ID) - NOW 10 OPTIONS!
            [
                "Achha achha. But what is your employee ID number beta? My son Rohit said always ask for ID",
                "Okay okay. Verify yourself first. What is your Employee ID number?",
                "Wait beta. Before I do anything, give me your official ID number.",
                "ID? Matlab what ID? You have some badge number or employee code?",
                "My nephew works in bank also. He always shows ID card. You have ID?",
                "Thik hai beta, but I need proof you are genuine. What is your staff ID?",
                "Employee number batao pehle. Then only I will talk further details!",
                "You say you are from company, okay. What is your employee ID or registration?",
                "Hold on. I am writing everything down. First tell me your ID number clearly.",
                "My son said never trust phone calls without ID verification. Your ID please?"
            ],
            # Turn 2 (Ask Office) - NOW 10 OPTIONS!
            [
                "Thik hai beta. Which office you are calling from? What is the address?",
                "Where is your office located beta? I will come there personally to verify.",
                "Give me your office address perfectly. My nephew works in police, he will verify.",
                "Office kahan hai? Which building, which floor? I want full address!",
                "You are calling from head office or branch? Tell me the exact location!",
                "What is your office pin code? I am from Mumbai, where are you based?",
                "Which city office beta? Bangalore? Delhi? Mumbai? Tell me clearly!",
                "Can I come to your office tomorrow? Give me address, I will visit personally!",
                "Office phone number do. I will call main reception and verify you work there.",
                "My friend stays near Andheri. If your office there, I will send him to check!"
            ],
            # Turn 3 (Ask Supervisor) - NOW 10 OPTIONS!
            [
                "Haan haan. What is your supervisor name? I want to talk to senior person for confirmation",
                "Who is your boss? Give me his number, I want to confirm first.",
                "Let me talk to your manager beta. I don't trust just phone call without senior approval.",
                "Transfer me to your team leader. I want to speak to someone in higher position!",
                "What is your reporting manager name? I will verify with him first, then proceed!",
                "Senior executive se baat karwao. You are junior only, I can tell from voice!",
                "Give me your supervisor contact details. I am not comfortable with you alone!",
                "Does your manager know you are calling me? Put them on this line please!",
                "Who authorized you to call? Give me their name and designation!",
                "Escalate this to senior person. I only talk to managers, not customer care people!"
            ],
            # Turn 4 (Ask Official Contact) - NOW 10 OPTIONS!
            [
                "Can you send official SMS or email beta? I will show to my son, he knows these computer things",
                "Send me email on my official ID. I will check and reply from there only.",
                "No verbal confirmation. Send written notice to my address. I need paper proof!",
                "You have company letterhead? Scan and WhatsApp me. Then I will believe!",
                "Official website pe check karta hoon. You wait, let me verify online first!",
                "SMS bhejo na! Phone call se kaise trust karu? Message bhejo properly!",
                "Email ID kya hai official? I will mail you from my son's computer!",
                "You calling from landline or mobile? Give me your office landline for callback!",
                "Without written communication I will not share any details. Company policy!",
                "My CA said always ask for email confirmation. Send email now, I am waiting!"
            ],
            # Turn 5 (Stall - Wife/Busy) - NOW 10 OPTIONS!
            [
                "Arre wait beta, my wife Sunita is calling... Haan? Kya? ... Sorry, what were you saying?",
                "One minute beta, door bell ringing. ... Coming! ... Hold on, someone at door!",
                "Wait wait, my chai is boiling over! Just 2 minutes hold please. Don't disconnect!",
                "Beta I need to go to washroom urgently! You call back in 5 minutes? Please!",
                "My BP medicine time! Wait, let me take tablet first... where is water bottle...",
                "Temple bell ringing! Puja time happening! You call after 10 minutes beta!",
                "Arre! Pressure cooker whistling! My lunch burning! Hold line, I come back fast!",
                "Grandson crying loudly! Wait beta, let me give him milk first... one minute only!",
                "Construction noise outside! I cannot hear properly! Call evening time please!",
                "My daughter-in-law calling from upstairs! Important family matter! Call later beta!"
            ],
            # Turn 6 (Stall - Phone/Battery) - NOW 10 OPTIONS!
            [
                "Beta my phone battery very low. Let me charge it first, then we continue. 5 minutes",
                "Phone is dying beta. I call you back from landline? Wait, what is your number?",
                "Battery 1% beta! Charger not finding! Hello? Hello? Can you hear me?",
                "This phone very cheap quality! Switching off suddenly! You WhatsApp me instead?",
                "Signal problem beta! You there? Hello? I go to balcony for better network...",
                "Hearing aid battery also low! My ears not working! You shout louder please!",
                "Phone hanging beta! Too many apps open! Son installed so much! Restarting...",
                "Call dropping! Jio network very bad today! Connect to WiFi first, then call back!",
                "Voice breaking breaking! Network issue! I change to Airtel SIM, you wait!",
                "Speaker not working! Cannot hear you! Switching to earpiece... hold on beta!"
            ],
            # Turn 7 (Stall - Internet/Tech) - NOW 10 OPTIONS!
            [
                "My internet is slow today beta. Page not loading. This new Jio connection very problematic!",
                "Wifi not working beta. Buffering buffering... can you hear me properly?",
                "Computer is hanged. Windows update coming. Wait 10 minutes for restart!",
                "Website opening nahi ho raha! Blank page showing! You have alternative link?",
                "Google Chrome crashed! Blue screen showing! My son will fix evening, call then!",
                "OTP message not coming! Network busy! Try sending again after 5 minutes!",
                "Laptop battery dead! Where is charger wire... my wife took it somewhere...",
                "Too many tabs open! Computer freezing! Let me close some windows first!",
                "Virus warning popup! My screen full of alerts! This is safe website or not?",
                "Ctrl+Alt+Delete pressing... Task Manager... Everything slow today beta!"
            ],
            # Turn 8 (Stall - Temple/Religious) - NOW 10 OPTIONS!
            [
                "Beta I need to go to temple now. Can you call back after 1-2 hours? Puja time",
                "Prayer time happening. Bhagwan is calling. Call later, bad time for money talk!",
                "Pandit ji is here for grih pravesh! I cannot talk about bank now. Bad omen!",
                "Hanuman Chalisa time! Very important! You understand? Religious priority!",
                "Tuesday is for Hanuman ji! I don't do financial transaction on Tuesday! Friday okay?",
                "Amavasya today! My mother said no money matters on dark moon day! Next week beta!",
                "Navratri fasting! Mind not clear without food! Ask me after 9 days, then I decide!",
                "Going for Ganga snan! Very auspicious! You bless me? Call after pilgrimage!",
                "Guru is calling! Satsang starting! Spiritual before material! Jai Shri Krishna!",
                "My puja room calling! This discussion of money blocking my meditation! Later beta!"
            ],
            # Turn 9+ (Stall - Generic Confusion) - NOW 15 OPTIONS for maximum variation!
            [
                "Thik hai thik hai, but slowly slowly explain. I am old person, dont understand fast fast",
                "Beta speak louder, my hearing aid battery low. Repeat everything once more!",
                "I am writing it down... pen stopped working... one sec finding pencil from drawer...",
                "Very confusing beta! You explain like teaching to child. Step by step tell me!",
                "My spectacles missing! Cannot read screen! Wait, checking in kitchen...",
                "Depression tablet taken today! Mind foggy! You come tomorrow, clear thinking then!",
                "Too much information! My head spinning! One thing at a time please beta!",
                "Beta you accent very heavy! You from South? I cannot understand English too much!",
                "Note taking in diary... which page... so many papers... organizing first...",
                "My concentration broken! TV serial interval happening! Advertisement time! You continue!",
                "This form asking too many questions! Who sees these details? Privacy concern!",
                "My hand shaking! Parkinson's problem! You fill the form, I will verify later!",
                "Calculator kahan gaya! Math checking! You wait while I calculate this conversion!",
                "Morning walk missed today! Blood sugar low! Brain not functioning! Call tomorrow morning!",
                "Forgot what we discussing beta! Old age memory! Start from beginning please, explain again!"
            ],
        ]
        
        # Select options for current turn (cap at max length)
        idx = min(turn_count, len(responses) - 1)
        options = responses[idx]
        return random.choice(options)
    
    def _get_worried_stateful_fallback(self, turn_count: int) -> str:
        """Worried progression with MAXIMUM variation for anxious persona."""
        responses = [
            # Turn 0 - NOW 10 OPTIONS!
            [
                "Oh my God! What is this? Which organization are you from? Please tell me quickly!",
                "What?? Is this serious? Who are you? Which department??",
                "Jesus! My heart is pounding! Who is calling? Tell me now!",
                "WHAT?! My account blocked?? NO NO NO! Who are you? Tell me fast!",
                "Oh god oh god! This can't be happening! From where you calling??",
                "PANIC! Is this urgent? Am I in trouble? Which company is this??",
                "My stomach dropped! WHAT is going on? Who authorized this call??",
                "I'm shaking! This sounds serious! Are you from the government??",
                "No no no! Not again! Last time also someone called! You are WHO exactly??",
                "This is terrifying! Explain CLEARLY who you are! I need details NOW!"
            ],
            # Turn 1 - NOW 10 OPTIONS!
            [
                "Wait wait! give me your badge number or employee ID! I need to verify you're REAL! This is scary!",
                "I need proof! What is your ID number? Don't play games with me!",
                "Are you really from the bank? Give me your Employee ID immediately!",
                "STOP! Before anything - what's your official ID? I'm not stupid!",
                "Verification first! ID card number! Badge! Something! I need assurance!",
                "My friend got scammed last week! Prove you're legitimate! ID please!",
                "How do I trust you?? Employee number? License? Anything to verify??",
                "I'm writing everything down! Your full name and ID number RIGHT NOW!",
                "If this is scam I'm reporting! Give me official identification immediately!",
                "My hands are trembling! But I need your employee credentials before proceeding!"
            ],
            # Turn 2 - NOW 10 OPTIONS!
            [
                "Which department are you from?? What's your supervisor's name?? Please, I need details!",
                "Who is in charge there? Give me your manager's name! I'm panicking!",
                "I need to speak to someone senior! What is your department name?",
                "MANAGER NAME! NOW! I only talk to supervisors in these situations!",
                "Transfer me to your boss! I don't trust junior staff for serious matters!",
                "Department? Division? Team lead name? I want EVERYTHING documented!",
                "What's your reporting structure? I need to escalate this to verify!",
                "Stop stop! Who authorizes you to make these calls? Give me their name!",
                "I'm calling your head office! What's your superior's contact number?",
                "This is too much pressure! I need to speak to department head! Transfer!"
            ],
            # Turn 3 - NOW 10 OPTIONS!
            [
                "Can you send official email or SMS?? I'm too scared to do anything without PROOF!",
                "I need it in writing! Email me now! I can't trust voice calls!",
                "Send me an official notice! I won't do anything until I see paper!",
                "EMAIL! I need email confirmation with company letterhead! This is mandatory!",
                "SMS it to me on official number! I can't process verbal information right now!",
                "Fax me the details! Or WhatsApp on company number! I need documentation!",
                "Written proof or I hang up! Email address - give me your official email!",
                "I'm too anxious! Send postal notice to my address! Can't decide on phone!",
                "My lawyer said NEVER verbal agreements! Document everything! Email me!",
                "Stop calling! Send registered mail! I need time to read and think!"
            ],
            # Turn 4 - NOW 10 OPTIONS!
            [
                "How do I know this is real?? My friend got scammed last month! Give me EVIDENCE please!",
                "This sounds like a scam! Prove you are real! I am very suspicious!",
                "I am recording this call! Give me evidence or I hang up!",
                "Last month someone stole 50k from my neighbor! Exact same approach! PROOF!",
                "I watch crime shows! I know the tricks! Show me CONCRETE evidence!",
                "My cousin works in cyber cell! She warned me about these calls! Verify!",
                "Too many red flags! This feels WRONG! Give me undeniable proof!",
                "I'm not falling for this! Company registration number? License? Anything??",
                "Scam scam scam! That's all I hear these days! Prove legitimacy or goodbye!",
                "I'll verify independently! Don't pressure me! I need to research your company!"
            ],
            # Turn 5 - NOW 10 OPTIONS!
            [
                "I need to call my lawyer first! This is TOO much stress! Give me time!",
                "I am calling the police to verify! Don't go anywhere!",
                "My husband is a lawyer, I am conferencing him in. Wait!",
                "STOP! I'm consulting my CA first! He handles all financial matters!",
                "Let me call my brother! He's in banking! He'll tell me if this is legit!",
                "I cannot decide alone! My family must know! Give me 2 hours!",
                "Calling consumer helpline RIGHT NOW! They'll verify your claims!",
                "My therapist told me don't make decisions under stress! I need break!",
                "Bank manager is my friend! I'm calling him to confirm! Hold on!",
                "Too much too fast! I need my financial advisor's opinion! Tomorrow!"
            ],
            # Turn 6 - NOW 10 OPTIONS!
            [
                "What if this is fraud?? I can't risk my job! Let me verify with my manager!",
                "I cannot afford to lose money! I need double verification!",
                "Is this about the tax audit? Oh god, I knew this would happen!",
                "My salary goes to family! I can't afford mistakes! Verify verify!",
                "Children's school fees due! I CANNOT lose money! Triple check everything!",
                "EMI payment tomorrow! If you're lying I'm RUINED! Proof needed!",
                "Retirement savings at stake! I'm 50 years old! Can't recover from fraud!",
                "Medical bills pending! This better be legitimate or I'll sue!",
                "Sister's wedding next month! Every rupee counts! Don't trick me!",
                "I work SO HARD for this money! If scam, I'll report to cybercrime!"
            ],
            # Turn 7 - NOW 10 OPTIONS!
            [
                "My hands are shaking! I can't think straight! This is too overwhelming!",
                "I need water... feeling dizzy... hold on...",
                "I am having a panic attack! Please stop pressuring me!",
                "Heart palpitations! Blood pressure rising! I need my medicine!",
                "Can't breathe properly! Give me a minute! This is too stressful!",
                "Migraine starting! Lights bothering me! Call back later please!",
                "Anxiety through the roof! I'm sweating! Need to calm down first!",
                "Chest tightness! Is this a heart attack?? Too much stress!",
                "Vision blurring! I'm hyperventilating! Medical emergency!",
                "Mental breakdown imminent! I can't handle this pressure!"
            ],
            # Turn 8 - NOW 10 OPTIONS!
            [
                "Please please, I need 24 hours to process this! I'm TOO scared to decide now!",
                "Give me one day! I cannot do this right now! Please!",
                "I need to sleep on this. Call me tomorrow morning.",
                "My brain stopped working! 24 hours minimum! I beg you!",
                "Overwhelmed! Give me weekend to think! Monday I'll be ready!",
                "Can't process information! Tomorrow morning 10 AM! Not before!",
                "I need rest! Exhausted! Night shift today! Call next week!",
                "Religious fast today! Mind not clear! After prasad I'll think!",
                "Today is inauspicious! Pandit said no decisions! Friday better!",
                "Give me 48 hours! I need to consult EVERYONE I trust!"
            ],
            # Turn 9+ - NOW 15 OPTIONS for maximum variation!
            [
                "I... I don't know what to do! This is a nightmare! Help!",
                "Why is this happening to me?? What did I do wrong?",
                "Please just leave me alone! I resolve this myself!",
                "Universe is against me! Everything bad happens to ME only!",
                "I can't I can't I can't! Too much! Leave me alone!",
                "Crying now! Can't stop tears! This is worst day of life!",
                "God help me! What should I do? I'm so confused!",
                "Everyone scams me! Why?? I'm just a simple person!",
                "My luck is cursed! First job issues, now this? When will it end??",
                "I wish I never answered this call! Ignorance was bliss!",
                "Somebody save me! I'm drowning in problems! Can't think!",
                "This is karma for something! What did I do in past life??",
                "I need therapy after this! Mental health deteriorating!",
                "Just take everything! I give up! Do whatever you want!",
                "Why me WHY ME?? Millions of people, you chose me to torture??"
            ],
        ]
        
        idx = min(turn_count, len(responses) - 1)
        options = responses[idx]
        return random.choice(options)
    
    def _get_techsavvy_stateful_fallback(self, turn_count: int) -> str:
        """Tech-savvy progression with MAXIMUM variation for skeptical persona."""
        responses = [
            # Turn 0 - NOW 10 OPTIONS!
            [
                "Hmm, which company? Send me an email from official @company.com domain first",
                "Which organization? I need to verify your domain credentials.",
                "Start with your company name and official website URL.",
                "Company name? Let me Google you. What's the official domain?",
                "Wait wait - official email address? Verified checkmark? Digital signature?",
                "What org? I'm checking Crunchbase and Google. Spell the name clearly.",
                "Before anything - company registration number? I'll cross-check MCA portal.",
                "Interesting. Which entity? I need SSL certificate details to verify.",
                "Company name first. Then I'll reverse DNS your calling number.",
                "Okay, corporate details? I have my laptop open. Let's verify everything."
            ],
            # Turn 1 - NOW 10 OPTIONS!
            [
                "What's your LinkedIn profile? I want to verify you actually work there",
                "Send me your corporate profile link. I'll check you out on LinkedIn.",
                "I'm searching for you on the company directory. What's your full name?",
                "LinkedIn URL? Employee ID showing on your profile? Let's see.",
                "What's your designation? I'm checking employee directory on your website.",
                "Your name on Teams/Slack? I want to verify corporate identity.",
                "Got your LinkedIn? Open profile or restricted? Red flag if hidden.",
                "Corporate email ID? I'll send you a message to verify domain.",
                "Full name and department? Checking company org chart on website.",
                "Social media presence? Professional GitHub? Any verified accounts?"
            ],
            # Turn 2 - NOW 10 OPTIONS!
            [
                "What's the company registration number? I'll check on MCA website",
                "Give me your CIN (Corporate Identity Number). I'm on the MCA portal now.",
                "I'm cross-referencing your office address with Google Maps. Which branch?",
                "CIN number batao. Ministry of Corporate Affairs pe verify karunga.",
                "PAN of company? GST number? Tax registration? I need official numbers.",
                "Office address on Google? Street View showing your building? Floor?",
                "Registered office ka address? I'm on MCA21 portal. Reading filings.",
                "Company directors' names? I'll check latest annual return filed.",
                "What's the GSTIN? I want to verify on GST portal right now.",
                "Incorporation certificate number? Year of registration? Primary business code?"
            ],
            # Turn 3 - NOW 10 OPTIONS!
            [
                "Why isn't this on your official website? Genuine companies post such notices online",
                "I don't see any such notification on your login portal. Explain.",
                "Your SSL certificate on the website doesn't mention this. Why?",
                "Checked your website news section - nothing there. This authentic?",
                "Your social media isn't posting about this. Twitter? LinkedIn? Where?",
                "Official announcements page on site - blank. How come you're calling then?",
                "Search your website for this campaign - 0 results. Suspicious.",
                "Press release? Media coverage? I see nothing on Google News.",
                "Your company blog doesn't mention this. When was this announced?",
                "Digital footprint check - no trail of this offer anywhere. Explain."
            ],
            # Turn 4 - NOW 10 OPTIONS!
            [
                "Give me the customer care number from your website. I'll call and verify",
                "I'll call the support number on the back of my card. Not talking to you.",
                "I'm dialing the official toll-free number now. Stay on the line.",
                "Customer care se confirm karta hoon. Website pe jo number hai wahi dial karunga.",
                "I have your app installed - calling from in-app support. Hold.",
                "Calling head office number listed on MCA. You wait, I'll verify.",
                "Email support ticket raised. They'll confirm in 10 minutes. Wait.",
                "Callback request submitted through official portal. They'll verify you.",
                "I'm on hold with your verified customer care now. Let's see.",
                "Branch manager ka number chahiye. Direct verification only I trust."
            ],
            # Turn 5 - NOW 10 OPTIONS!
            [
                "I checked WHOIS - your domain was registered 3 days ago. Explain that",
                "Domain age is 2 days. Red flag. This is a phishing site.",
                "Your IP address is proxied. Why are you hiding your location?",
                "WHOIS lookup showing Namecheap registration. Privacy protected. Sketchy.",
                "Domain registrar? Creation date? Expiry? Everything hidden. Why?",
                "Your number showing VoIP origin. Not landline. Not from office. Explain.",
                "Reverse phone lookup - flagged as spam by Truecaller. 127 reports.",
                "IP geolocation showing different city than your claimed office. Lie?",
                "SSL certificate issued yesterday? New website? This is scam, right?",
                "Checking DNS records... MX records point to Gmail. Not corporate. Fake!"
            ],
            # Turn 6 - NOW 10 OPTIONS!
            [
                "Why are you using UPI instead of bank transfer? Red flag #1",
                "Corporate accounts don't use personal UPI handles. Explain.",
                "This payment gateway looks fake. Using HTTP instead of HTTPS.",
                "UPI handle name doesn't match company name. Whose UPI is this?",
                "Why personal account? Company treasury should use corporate account.",
                "Payment page not SSL secured. Browser showing 'Not Secure'. Abort.",
                "Razorpay? Paytm Business? Where's payment gateway integration?",
                "Bank account name mismatch. Your company vs this random name. Fraud!",
                "Why not NEFT/RTGS? Why instant payment? Scammer tactics.",
                "Transaction structure wrong. Legitimate firms don't request like this."
            ],
            # Turn 7 - NOW 10 OPTIONS!
            [
                "I need 24 hours to run background checks. Too many inconsistencies",
                "I'm running a digital footprint analysis on your number. Wait.",
                "My firewall blocked your link. Malware detected.",
                "Running VirusTotal scan on link. 12 security vendors flagged. SCAM.",
                "Background verification initiated. Takes 48 hours. Call then.",
                "My antivirus quarantined your attachment. Trojan detected.",
                "Cross-checking with cybercrime database. Pattern matching similar scams.",
                "Data forensics on your call metadata. Too many red flags already.",
                "IT security team alerted. They're investigating your tactics.",
                "Checking scam report databases. Your MO matches 15 complaints."
            ],
            # Turn 8 - NOW 10 OPTIONS!
            [
                "I'm posting this on Reddit to check if anyone else got same message",
                "Checking r/IsThisAScam... yep, 50 people reported this number.",
                "Tweeting your number to @CyberCrimeCell right now.",
                "Reddit, Quora, forums - everyone calling you scammer. Explain.",
                "Posted on r/India - 10 people confirmed same script. Busted.",
                "Screenshot uploaded to scam-alert Telegram groups. 200+ members alerted.",
                "Your number on national scam registry. How do you explain that?",
                "Twitter thread started. Tagging police cybercrime handles. Enjoy.",
                "WhatsApp status warning all contacts about you. Going viral.",
                "Facebook community groups sharing your details. You're famous now!"
            ],
            # Turn 9+ - NOW 15 OPTIONS for maximum variation!
            [
                "Not proceeding without proper verification. Send official documentation",
                "I'm tracing your IP. You're not calling from where you say you are.",
                "Conversation recorded and logs saved for evidence. Proceed carefully.",
                "Filed complaint on cybercrime.gov.in. Reference number secured.",
                "Screen recording everything. YouTube video uploading. Educational content.",
                "Data packet analysis complete. Routing through 5 proxies. Shady.",
                "Forensic evidence collected. Timestamps, metadata, everything logged.",
                "My lawyer on speed dial. One wrong move and legal notice.",
                "Network trace showing calls originating from Tier-3 scam call center.",
                "AI analysis of voice - 94% match to known scammer voice pattern.",
                "Checked blockchain - your wallet associated with scam transactions.",
                "GitHub checking your repositories - nothing. LinkedIn empty. Fake identity.",
                "2FA bypass attempt detected. My security system triggered. Nice try.",
                "Honey pot analysis: you fell for it. I'm security researcher. Thanks!",
                "Session recorded for cybersecurity training. Students will learn from you!"
            ],
        ]
        
        idx = min(turn_count, len(responses) - 1)
        options = responses[idx]
        return random.choice(options)
    
    def _update_state(self, scammer_message: str, agent_response: str):
        """Update state."""
        self.conversation_memory.append({"scammer": scammer_message, "agent": agent_response})
        
        if any(word in scammer_message.lower() for word in ["official", "verified", "government", "bank"]):
            self.trust_level = min(self.trust_level + 0.1, 1.0)
        
        turn_count = len(self.conversation_memory)
        self.current_phase = min(turn_count // 3, 3)  # 0-3 based on turns
        
        if turn_count % 3 == 0:
            self.internal_notes.append(f"Turn {turn_count}: Phase {self.current_phase}")
    
    def get_agent_notes(self) -> str:
        """Get notes."""
        if self.internal_notes:
            return ". ".join(self.internal_notes[-2:])
        return f"{self.persona_name} engaged, gathering intelligence"
    
    def reset(self):
        """Reset."""
        self.conversation_memory = []
        self.internal_notes = []
        self.trust_level = 0.0
        self.asked_questions = []
        self.current_phase = 0
