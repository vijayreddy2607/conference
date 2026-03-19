"""Enhanced ML-based scam detection using ProductionScamDetector.

This module acts as an adapter for the ProductionScamDetector to ensure 
compatibility with the existing application structure.
"""
import logging
import re
from typing import Dict, List, Tuple
from app.ml.production_scam_detector import ProductionScamDetector

logger = logging.getLogger(__name__)

# Global Singleton
_production_detector = None

def get_detector():
    """Get or initialize the production detector."""
    global _production_detector
    if _production_detector is None:
        try:
            _production_detector = ProductionScamDetector()
            logger.info("✅ ProductionScamDetector wrapper initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init ProductionScamDetector: {e}")
            return None
    return _production_detector

class PersonaSwitchDetector:
    """Detects when scammer changes tactics requiring persona switch."""
    
    def __init__(self):
        self.conversation_scam_types = []
        
    def _map_scam_to_persona(self, scam_type: str) -> str:
        """Map scam type to best persona."""
        persona_mapping = {
            "fake_job": "techsavvy",
            "investment": "techsavvy",
            "credit_loan": "student",
            "lottery_prize": "student",
            "marketplace_scam": "aunty",
            "gig_scam": "student",
            "bank_phishing": "uncle",
            "digital_arrest": "worried",
            "sextortion": "worried",
            "delivery_scam": "aunty",
            "impersonation": "worried"
        }
        return persona_mapping.get(scam_type, "uncle")

    def should_switch_persona(
        self,
        current_message: str,
        conversation_history: List[Dict],
        current_scam_type: str,
        current_persona: str
    ) -> Tuple[bool, str, str]:
        """Detect if scammer changed tactics requiring persona switch."""
        detector = get_detector()
        if not detector:
            return False, current_persona, "detector_unavailable"
            
        result = detector.detect(current_message)
        new_type = result.get('scam_type')
        confidence = result.get('confidence', 0.0)
        
        if not new_type or new_type == "unknown":
            return False, current_persona, "unknown_type"
            
        # Track history
        self.conversation_scam_types.append(new_type)
        
        # Check for consistent change (last 3 messages)
        recent_types = self.conversation_scam_types[-3:]
        if len(recent_types) >= 3 and all(t == new_type for t in recent_types):
             if new_type != current_scam_type and confidence > 0.6:
                 new_persona = self._map_scam_to_persona(new_type)
                 if new_persona != current_persona:
                     return True, new_persona, f"Scam type changed to {new_type}"
                     
        return False, current_persona, "no_switch"

def enhanced_scam_detection(message: str, conversation_history: List[str] = None) -> Dict:
    """
    Adapter function for ProductionScamDetector.
    
    Returns:
        Dict compatible with app legacy format:
        {
            "scam_type": str,
            "confidence": float,
            "metadata": dict,
            "recommended_persona": str
        }
    """
    detector = get_detector()
    
    if detector:
        try:
            result = detector.detect(message)
            
            # Map production result to legacy format
            scam_type = result.get('scam_type', 'unknown')
            confidence = result.get('confidence', 0.0)
            
            # Compute basic metadata if missing
            metadata = result.get('details', {})
            metadata.update({
                "confidence_tier": result.get('confidence_tier'),
                "action": result.get('recommended_action'),
                "path": result.get('detection_path')
            })
            
            # Determine recommended persona
            persona_detector = PersonaSwitchDetector()
            recommended_persona = persona_detector._map_scam_to_persona(scam_type)
            
            return {
                "scam_type": scam_type,
                "confidence": confidence,
                "metadata": metadata,
                "recommended_persona": recommended_persona
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced_scam_detection: {e}")
            
    # Fallback response
    return {
        "scam_type": "unknown",
        "confidence": 0.0,
        "metadata": {"error": "detection_failed"},
        "recommended_persona": "uncle"
    }

if __name__ == "__main__":
    print("Testing Enhanced Detection Adapter...")
    res = enhanced_scam_detection("Congratulations! You won 1 crore lottery")
    print(res)
