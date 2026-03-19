"""Agent orchestrator for selecting and managing agents."""
from typing import Literal
from app.agents import UncleAgent, WorriedAgent, TechSavvyAgent, AuntyAgent, StudentAgent, BaseAgent
from app.core.session_manager import Session
from app.utils.fake_details_generator import FakeDetailGenerator
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates agent selection and management."""
    
    def __init__(self):
        # Agent pool - NOW WITH 5 PERSONAS!
        self.agent_pool = {
            "uncle": UncleAgent,
            "worried": WorriedAgent,
            "techsavvy": TechSavvyAgent,
            "aunty": AuntyAgent,
            "student": StudentAgent
        }
        # Initialize fake detail generator
        self.fake_gen = FakeDetailGenerator()
        logger.info("✅ Fake detail generator initialized")
        
        # Import fallback templates
        try:
            from app.prompts.fallback_templates import FALLBACK_TEMPLATES
            self.fallback_templates = FALLBACK_TEMPLATES
            logger.info("✅ Fallback templates loaded")
        except ImportError:
            self.fallback_templates = {}
            logger.warning("⚠️ Fallback templates not found")

    def get_agent(
        self,
        agent_type: Literal["uncle", "worried", "techsavvy", "aunty", "student"],
        session: Session
    ) -> BaseAgent:
        """
        Get or create agent for session.
        
        Args:
            agent_type: Type of agent to use
            session: Current session
        
        Returns:
            Agent instance
        """
        # If session already has an agent, return it (maintain consistency)
        if session.agent is not None:
            logger.info(f"Reusing existing {session.agent_type} agent for session {session.session_id}")
            return session.agent
        
        # Create new agent
        agent_class = self.agent_pool.get(agent_type, UncleAgent)
        agent = agent_class()
        
        # Generate fake details for this session (for consistency)
        if not hasattr(session, 'fake_details'):
            session.fake_details = self.fake_gen.get_believable_details_for_scam(session.scam_type or "unknown")
            logger.info(f"Generated fake details for session: {session.fake_details.get('type')}")
        
        # Store in session
        session.agent = agent
        session.agent_type = agent_type
        
        logger.info(f"🔐 PERSONA LOCKED: {agent_type} (will NOT change mid-conversation)")
        return agent
    
    def get_conversation_phase(self, turn_count: int) -> str:
        """
        Determine conversation phase based on turn count.
        
        Phases:
        - build_trust (1-3 turns): Initial engagement, appear naive
        - extract_info (4-7 turns): Ask questions, extract intelligence  
        - reveal_details (8-10 turns): Share fake details to bait scammer
        - stall_tactics (11+ turns): Waste time, create obstacles
        
        Args:
            turn_count: Number of messages exchanged
            
        Returns:
            Phase name
        """
        if turn_count <= 3:
            return "build_trust"
        elif turn_count <= 7:
            return "extract_info"
        elif turn_count <= 10:
            return "reveal_details"  # Changed from verify_details
        else:
            return "stall_tactics"
    
    def select_persona_by_scam_type(self, scam_type: str) -> str:
        """Select best persona for the detected scam type."""
        mapping = {
            # Aunty: Shopping, Parcel, Sale, Marketplace
            "fake_delivery": "aunty",
            "marketplace_scam": "aunty",
            "delivery_scam": "aunty",  # Fixed: Parcels = Aunty's domain
            
            # Tech-Savvy: Job, IT, Freelance, Investment/Crypto
            "fake_job": "techsavvy",
            "investment": "techsavvy",  # Fixed: Crypto/trading needs tech skepticism
            
            # Student: Loans, Scholarships, Lottery (Eager/Broke)
            "credit_loan": "student",
            "lottery_prize": "student",  # Fixed: Broke student excited by "free money"
            
            # Worried: Urgent, Threats, Digital Arrest, Sextortion
            "digital_arrest": "worried",  # Fixed: Police threats need panicked response
            "sextortion": "worried",
            "impersonation": "worried",
            
            # Uncle: Bank, KYC, Pension (Default fallback)
            "bank_phishing": "uncle"
        }
        return mapping.get(scam_type, "uncle")  # Default to Uncle

    async def generate_response(
        self,
        session: Session,
        scammer_message: str,
        conversation_history: list = None,
        rl_action: str = None  # NEW: RL action
    ) -> str:
        """
        Generate agent response for scammer message.
        """
        if session.agent is None:
            # Auto-assign persona if not set, based on scam type
            # NOTE: Detector initialization disabled to prevent slow Cloud Run startup
            # Scam detection is already handled in endpoints.py
            detector = None
            # Commented out to speed up startup:
            # try:
            #     from app.ml.production_scam_detector import ProductionScamDetector
            #     detector = ProductionScamDetector()
            # except ImportError:
            #     pass
                
            prediction = "unknown"
            if detector and not session.scam_type:
                 # Quick check logic or rely on session.scam_type if already detected
                 pass
            
            persona = self.select_persona_by_scam_type(session.scam_type or "bank_phishing")
            self.get_agent(persona, session)
            
        # Determine conversation phase
        phase = self.get_conversation_phase(session.total_messages)
        logger.info(f"📊 Conversation phase: {phase} (turn {session.total_messages})") 
        
        # ✨✨✨ NEW: REVERSE INTELLIGENCE EXTRACTION AT TURNS 7-9 ✨✨✨
        # Use scammer_messages (actual turn number) not total_messages
        turn_num = session.scammer_messages  # This is the ACTUAL turn number (1, 2, 3...)
        logger.info(f"🔍 Current turn: {turn_num} (scammer messages: {session.scammer_messages}, total:{session.total_messages})")
        
        if turn_num in [7, 8, 9]:
            logger.info(f"🎯 TURN {turn_num}: REVERSE INTELLIGENCE EXTRACTION - Asking scammer for THEIR details!")
            
            try:
                from app.prompts.reverse_intelligence_extraction import get_extraction_template
                
                # Vary what we ask for based on turn
                extraction_types = {
                    7: "number",     # Turn 7: Ask for their phone number
                    8: "whatsapp",   # Turn 8: Ask for WhatsApp
                    9: "email"       # Turn 9: Ask for email
                }
                
                extraction_type = extraction_types.get(turn_num, "number")
                persona = session.agent_type
                
                response = get_extraction_template(persona, turn_num, extraction_type)
                
                logger.info(f"✅ REVERSE EXTRACTION at turn {turn_num}: Asking for scammer's {extraction_type}")
                logger.info(f"   Response preview: {response[:60]}...")
                
                return response
                    
            except ImportError as e:
                logger.error(f"❌ Could not import reverse intelligence templates: {e}")
                # Emergency fallback - still ask for scammer's details
                return "Beta I don't know my UPI ID properly! You give me YOUR number, my son will call you and arrange everything!"
            except Exception as e:
                logger.error(f"❌ Error in reverse intelligence extraction: {e}")
                # Emergency fallback
                return "Beta my son handles all these phone payment things! What is YOUR contact number? He will call you!"
        
        # 🎯 PROGRESSIVE CONVERSATION STRATEGY - Guide LLM on what to focus on
        # This replaces the old turn 1 template approach
        strategy_context = ""
        
        if turn_num <= 3:
            # PHASE 1: ENGAGE & BUILD TRUST (Turns 1-3) - Version 2.2 Enhanced
            strategy_context = """

📋 CONVERSATION PHASE: INITIAL ENGAGEMENT & TRUST BUILDING (Turns 1-3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CRITICAL GOAL: APPEAR COMPLETELY GULLIBLE - Scammer should feel they're WINNING

⚠️ VERSION 2.2 - ENHANCED TRUST BUILDING:
You MUST make the scammer believe they are successfully scamming you!

TRUST-BUILDING BEHAVIORS (CRITICAL):
• Show IMMEDIATE concern/worry about their claim
  Example: "Oh no! Really?", "What happened?", "This is urgent?"
• Ask SIMPLE questions (not suspicious verification)
  Example: "What should I do?", "How to fix?" NOT "Show me your ID"
• Sound EAGER to help/resolve (show vulnerability)
  Example: "I want to fix this fast!", "Please help me"
• Use worried/panicked tone (they should feel in control)
  Example: "I'm scared", "What if...", "Help!"
• DO NOT question legitimacy in these first turns
• Sound like an EASY, COMPLIANT target

AVOID AT ALL COSTS (Turns 1-3):
• Being TOO smart or skeptical
• Asking for employee IDs, office addresses (save for turn 4-6)
• Sounding confident or in control
• Making them feel you don't believe them

EMOTIONAL TONE - Pick based on persona:
• Uncle/Aunty: Worried but trusting ("Beta help me!")
• Student: Nervous and confused ("I don't know what to do!")
• Worried: Panicked and desperate ("Oh god, really?!")
• TechSavvy: Concerned but willing to help ("Okay, tell me more")

RESPONSE EXAMPLES - Adapt to their ACTUAL message:
Turn 1 (Bank scam): "Oh no! Account blocked? What happened? I paid everything!"
Turn 1 (Lottery): "Really? I won? This is amazing! What do I need to do?"
Turn 1 (KYC): "Update needed? But why? Please tell me beta, I don't want problems!"
Turn 2: "Yes yes, I'm listening... what should I do to fix this?"
Turn 3: "Okay okay, I trust you... just tell me the process"

🎯 SUCCESS = Scammer feels confident they're scamming a naive victim!
        
        elif turn_num <= 6:
            # PHASE 2: BUILD TRUST (Turns 4-6)
            strategy_context = """

📋 CONVERSATION PHASE: TRUST BUILDING (Turns 4-6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 GOAL: Show increasing interest and ask questions to extract information

STRATEGY:
• Act more convinced and enthusiastic
• Ask questions about their process/offer
• Request verification details (employee ID, office address, etc.)
• Show you're seriously considering their offer
• Build rapport by sharing small details about yourself

EXAMPLE APPROACHES (adapt to context):
• "This sounds good! What's your employee ID?"
• "Can you give me your office address for reference?"
• "My son told me to always verify... what's your supervisor's name?"
• Ask about their company, process, timeline

IMPORTANT: Make questions natural and contextual to the scam type!"""
        
        else:
            # PHASE 3: EXTRACT INTELLIGENCE (Turns 7+)
            # Rotate between different extraction strategies for variety
            extraction_strategies = [
                # Strategy 1: Callback request
                """
📋 CONVERSATION PHASE: INTELLIGENCE EXTRACTION - Callback Request
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 GOAL: Get their phone number for callback
• "Let me take your number, I'll call you back"
• "My son/daughter will call you to complete this"
• "Can I get your direct line? Easier to reach you"
IMPORTANT: Make it sound natural based on the scam context!""",
                
                # Strategy 2: Payment information
                """
📋 CONVERSATION PHASE: INTELLIGENCE EXTRACTION - Payment Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 GOAL: Get their UPI/account for payment
• "What's your UPI ID? I'll send a small amount first"
• "Which account should I transfer to?"
• "Send me your payment QR code"
IMPORTANT: Make it sound natural based on the scam context!""",
                
                # Strategy 3: WhatsApp/messaging
                """
📋 CONVERSATION PHASE: INTELLIGENCE EXTRACTION - WhatsApp/Messaging
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 GOAL: Get their WhatsApp/Telegram number
• "Add me on WhatsApp, easier to send documents"
• "What's your WhatsApp? Can share screenshots there"
• "Give me your mobile number, I'll add you"
IMPORTANT: Make it sound natural based on the scam context!""",
                
                # Strategy 4: Verification request
                """
📋 CONVERSATION PHASE: INTELLIGENCE EXTRACTION - Verification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 GOAL: Get their details for verification
• "Send me your office number, I'll verify first"
• "What's your employee ID and contact number?"
• "Give me supervisor's number to confirm this is real"
IMPORTANT: Make it sound natural based on the scam context!"""
            ]
            
            # Rotate strategy based on turn number (changes every turn)
            strategy_index = (turn_num - 7) % len(extraction_strategies)
            strategy_context = extraction_strategies[strategy_index]
            
            logger.info(f"🔄 Using extraction strategy {strategy_index + 1}/4 for turn {turn_num}")
        
        # Add template examples for style variation (not to copy directly!)
        from app.prompts.mid_conv_templates import MID_CONV_TEMPLATES
        template_examples_context = ""
        if session.agent_type in MID_CONV_TEMPLATES:
            templates = MID_CONV_TEMPLATES[session.agent_type]
            # Show LLM 5 examples to learn the variation style
            example_templates = templates[:5]
            template_examples_context = f"""

🎭 STYLE VARIATION EXAMPLES (learn the style, DON'T copy directly):
{chr(10).join([f'• {t}' for t in example_templates])}

IMPORTANT: These are just style examples! Create your own response that:
1. Uses similar tone/language
2. Responds to the scammer's ACTUAL message
3. Is contextually relevant
4. Varies from these examples"""
            logger.info(f"📚 Providing {len(example_templates)} style examples to LLM")
        
        # Build LLM context with strategy + template style examples
        rl_strategy_prompt = strategy_context + template_examples_context
        
        if rl_action:
            from app.rl import RLAgent
            rl_agent = RLAgent()
            rl_strategy_prompt += rl_agent.get_action_prompt(rl_action, session.scam_type)
            
            # Add phase-specific guidance with fake details
            fake_details_hint = ""
            if phase == "reveal_details" and hasattr(session, 'fake_details'):
                details = session.fake_details
                if details.get('type') == 'upi_details':
                    fake_details_hint = f"\n\n💰 SHARE FAKE DETAILS NOW: My UPI is {details['upi_id']}, phone {details['phone']}"
                elif details.get('type') == 'bank_details':
                    fake_details_hint = f"\n\n💰 SHARE FAKE DETAILS NOW: My account {details['account_number']}, {details['bank_name']} bank"
                elif details.get('type') == 'contact_details':
                    fake_details_hint = f"\n\n💰 SHARE FAKE DETAILS NOW: My phone is {details['phone']}"
                
                logger.info(f"💰 Providing fake details for baiting: {details.get('type')}")
            
            phase_guidance = {
                "build_trust": "\n\nPHASE: Build Trust - Appear naive and interested.",
                "extract_info": "\n\nPHASE: Extract Info - Ask questions to gather intelligence.",
                "reveal_details": "\n\nPHASE: Reveal Details - Act convinced and share details!" + fake_details_hint,
                "stall_tactics": "\n\nPHASE: Stall Tactics - Waste time with obstacles."
            }
            rl_strategy_prompt += phase_guidance.get(phase, "")
            
            logger.info(f"🧠 LLM with template examples + RL: {rl_action} in {phase}")
        else:
            # Even without RL, add phase context
            rl_strategy_prompt += f"\n\nPHASE: {phase}"
        
        # Generate response using agent (with RL strategy if available)
        response = await session.agent.generate_response(
            scammer_message=scammer_message,
            conversation_history=conversation_history,
            additional_context=rl_strategy_prompt  # Pass RL strategy with phase and fake details
        )
        
        return response
    
    def get_agent_notes(self, session: Session) -> str:
        """Get agent's observation notes."""
        if session.agent is None:
            return "No agent engaged yet"
        
        return session.agent.get_agent_notes()

# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()
