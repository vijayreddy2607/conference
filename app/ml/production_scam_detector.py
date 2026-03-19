"""Production-Ready Scam Detector with Tiered Confidence Levels

This is the PRODUCTION version with:
1. Three-stage defensive cascade (Overnight → Indian V2 → TF-IDF)
2. Tiered confidence levels for nuanced response
3. Full error handling and fallbacks
4. Ready for API integration

Use this in your production honeypot system!
"""
import sys
sys.path.append('/Users/vijayreddy/honey pot agent')

import torch
import pickle
import time
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import warnings
warnings.filterwarnings('ignore')

# Advanced enhancements
try:
    from app.ml.metadata_analyzer import MetadataAnalyzer
    from app.ml.monitoring import DetectionMonitor
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    print("⚠️  Advanced enhancements not available, running in basic mode")


class ProductionScamDetector:
    """Production-ready scam detector with tiered confidence."""
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.85  # Aggressive honeypot engagement
    MEDIUM_CONFIDENCE = 0.60  # Cautious engagement
    # Below 0.60 = Treat as potentially legitimate
    
    def __init__(self, enable_monitoring: bool = True, enable_metadata: bool = True):
        """Initialize all three detection stages + enhancements.
        
        Args:
            enable_monitoring: Enable detection logging and analytics
            enable_metadata: Enable metadata feature extraction
        """
        self.stage1_loaded = False
        self.stage2_loaded = False
        self.stage3_loaded = False
        
        # Advanced enhancements
        self.metadata_analyzer = None
        self.monitor = None
        
        if ENHANCEMENTS_AVAILABLE:
            if enable_metadata:
                try:
                    self.metadata_analyzer = MetadataAnalyzer()
                    print("✅ Metadata Analyzer enabled")
                except Exception as e:
                    print(f"⚠️  Metadata Analyzer failed: {e}")
                    
            if enable_monitoring:
                try:
                    self.monitor = DetectionMonitor()
                    print("✅ Detection Monitoring enabled")
                except Exception as e:
                    print(f"⚠️  Monitoring failed: {e}")
        
        print("="*80)
        print("PRODUCTION SCAM DETECTOR - INITIALIZING")
        print("="*80)
        
        # Stage 1: Overnight Model (Broad Coverage)
        try:
            print("\n[Stage 1] Loading Overnight Model (Public Datasets)...")
            checkpoint = torch.load(
                '/Users/vijayreddy/honey pot agent/scam_detector_model_safe.pth',
                map_location='cpu',
                weights_only=False
            )
            
            self.overnight_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
            self.overnight_model = DistilBertForSequenceClassification.from_pretrained(
                'distilbert-base-uncased', num_labels=2
            )
            self.overnight_model.load_state_dict(checkpoint['model_state_dict'])
            self.overnight_model.eval()
            
            self.stage1_accuracy = checkpoint.get('final_accuracy', 0.979)
            self.stage1_loaded = True
            print(f"✅ Stage 1 Ready! Accuracy: {self.stage1_accuracy*100:.1f}%")
            
        except Exception as e:
            print(f"⚠️  Stage 1 unavailable: {e}")
        
        # Stage 2: Indian-Specific Model V2 (Enhanced with real company data)
        try:
            print("\n[Stage 2] Loading Indian-Specific Model V2...")
            checkpoint = torch.load(
                '/Users/vijayreddy/honey pot agent/indian_scam_detector_v3.pth',
                map_location='cpu',
                weights_only=False
            )
            
            self.indian_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
            self.indian_model = DistilBertForSequenceClassification.from_pretrained(
                'distilbert-base-uncased', num_labels=2
            )
            self.indian_model.load_state_dict(checkpoint['model_state_dict'])
            self.indian_model.eval()
            
            self.stage2_accuracy = checkpoint.get('final_accuracy', 0.98)
            self.stage2_loaded = True
            print(f"✅ Stage 2 Ready! Accuracy: {self.stage2_accuracy*100:.1f}% (V2 - Real company data)")
            
        except Exception as e:
            print(f"⚠️  Stage 2 V2 unavailable: {e}")
            print("   Trying V1 fallback...")
            try:
                checkpoint = torch.load(
                    '/Users/vijayreddy/honey pot agent/indian_scam_detector_v2.pth',
                    map_location='cpu',
                    weights_only=False
                )
                self.indian_tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
                self.indian_model = DistilBertForSequenceClassification.from_pretrained(
                    'distilbert-base-uncased', num_labels=2
                )
                self.indian_model.load_state_dict(checkpoint['model_state_dict'])
                self.indian_model.eval()
                self.stage2_accuracy = 1.0
                self.stage2_loaded = True
                print(f"✅ Stage 2 V1 Loaded! Accuracy: 100%")
            except:
                print("   Stage 2 completely unavailable")
        
        # Stage 3: TF-IDF + Naive Bayes (Type Classification)
        try:
            print("\n[Stage 3] Loading TF-IDF + Naive Bayes Type Classifier...")
            with open('/Users/vijayreddy/honey pot agent/production_scam_detector.pkl', 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.label_map = model_data['label_map']
            self.stage3_accuracy = model_data.get('accuracy', 80.0) / 100
            self.stage3_loaded = True
            print(f"✅ Stage 3 Ready! Accuracy: {self.stage3_accuracy*100:.1f}%")
            
        except Exception as e:
            print(f"⚠️  Stage 3 unavailable: {e}")
            print("   Using keyword-based fallback for scam type classification")
            self.stage3_loaded = False
            # Keyword-based fallback will be used in _classify_type_fallback
        
        # Check if ANY detection stage is available
        if not (self.stage1_loaded or self.stage2_loaded or self.stage3_loaded):
            print("\n⚠️  WARNING: No ML models loaded! Using keyword-based detection only.")
            print("   Templates will handle all honeypot responses.")
        
        print("\n" + "="*80)
        print("✅ PRODUCTION DETECTOR READY")
        print("="*80)
        print(f"Stages loaded: S1={self.stage1_loaded}, S2={self.stage2_loaded}, S3={self.stage3_loaded}")
        print(f"Confidence Thresholds:")
        print(f"  High   (≥{self.HIGH_CONFIDENCE}): Aggressive honeypot engagement")
        print(f"  Medium ({self.MEDIUM_CONFIDENCE}-{self.HIGH_CONFIDENCE}): Cautious engagement")
        print(f"  Low    (<{self.MEDIUM_CONFIDENCE}): Treat as potentially legitimate")
        print("="*80 + "\n")
    
    def _detect_binary(self, message, model, tokenizer):
        """Generic binary detection."""
        with torch.no_grad():
            inputs = tokenizer(
                message,
                return_tensors='pt',
                padding='max_length',
                truncation=True,
                max_length=128
            )
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)[0]
            is_scam = probs[1] > 0.5
            confidence = probs[1].item()
            return is_scam.item(), confidence
    
    
    def _classify_type_fallback(self, message):
        """Keyword-based scam type classification (fallback when ML unavailable)."""
        message_lower = message.lower()
        
        # Simple keyword matching for common scam types
        if any(word in message_lower for word in ['upi', 'paytm', 'phonepe', 'gpay', 'prize', 'lottery', 'won']):
            return 'upi_prize_scam', 0.75
        elif any(word in message_lower for word in ['kyc', 'block', 'suspend', 'aadhaar', 'pan']):
            return 'bank_kyc_scam', 0.75
        elif any(word in message_lower for word in ['tax', 'refund', 'gst', 'income tax']):
            return 'tax_refund_scam', 0.75
        elif any(word in message_lower for word in ['job', 'hiring', 'work from home', 'wfh', 'salary']):
            return 'job_offer_scam', 0.75
        elif any(word in message_lower for word in ['invest', 'crypto', 'bitcoin', 'stock', 'trading']):
            return 'investment_scam', 0.75
        elif any(word in message_lower for word in ['police', 'courier', 'parcel', 'customs', 'illegal']):
            return 'police_courier_scam', 0.75
        elif any(word in message_lower for word in ['electricity', 'water', 'bill', 'disconnect']):
            return 'utility_bill_scam', 0.75
        elif any(word in message_lower for word in ['otp', 'verification', 'code']):
            return 'otp_scam', 0.75
        elif any(word in message_lower for word in ['covid', 'vaccine', 'medicine', 'health']):
            return 'health_scam', 0.75
        elif any(word in message_lower for word in ['love', 'marry', 'beautiful', 'handsome', 'relationship']):
            return 'romance_scam', 0.75
        else:
            return 'unknown_scam', 0.60
    
    def _classify_type(self,message):
        """Classify scam type (uses ML if available, fallback otherwise)."""
        if self.stage3_loaded:
            # Use ML classifier
            features = self.vectorizer.transform([message])
            prediction = self.classifier.predict(features)[0]
            confidence = self.classifier.predict_proba(features)[0].max()
            scam_type = self.label_map[prediction]
            return scam_type, confidence
        else:
            # Use keyword-based fallback
            return self._classify_type_fallback(message)

    
    def detect(self, message, use_ensemble: bool = True):
        """
        Production detection with tiered confidence + enhancements.
        
        Args:
            message: Input message to analyze
            use_ensemble: Use ensemble voting between models
        
        Returns:
            {
                'is_scam': bool,
                'confidence_tier': 'HIGH'|'MEDIUM'|'LOW'|'LEGITIMATE',
                'scam_type': str or None,
                'confidence': float,
                'recommended_action': str,
                'detection_path': str,
                'metadata': {...},  # NEW
                'details': {...}
            }
        """
        start_time = time.time()
        
        # Extract metadata features (if enabled)
        metadata = {}
        if self.metadata_analyzer:
            try:
                metadata = self.metadata_analyzer.analyze(message)
            except Exception as e:
                print(f"Metadata analysis error: {e}")
        
        result = {
            'is_scam': False,
            'confidence_tier': 'LEGITIMATE',
            'scam_type': None,
            'confidence': 0.0,
            'recommended_action': 'handle_normally',
            'detection_path': '',
            'details': {}
        }
        
        # Stage 1: Overnight Model
        stage1_scam = False
        stage1_conf = 0.0
        
        if self.stage1_loaded:
            is_scam, conf = self._detect_binary(message, self.overnight_model, self.overnight_tokenizer)
            result['details']['stage1'] = {'detected': is_scam, 'confidence': conf}
            stage1_scam = is_scam
            stage1_conf = conf
            
            if is_scam:
                # Stage 3: Get type
                scam_type, type_conf = self._classify_type(message)
                combined_conf = (conf * type_conf) ** 0.5
                
                result['is_scam'] = True
                result['scam_type'] = scam_type
                result['confidence'] = combined_conf
                result['detection_path'] = 'Overnight→Type'
                result['details']['stage3'] = {'type': scam_type, 'confidence': type_conf}
                
                # Apply metadata boost if available
                if metadata and metadata.get('overall_suspicion', 0) > 0.5:
                    metadata_boost = metadata['overall_suspicion'] * 0.1
                    result['confidence'] = min(result['confidence'] + metadata_boost, 1.0)
                    result['detection_path'] += '→Metadata+'
                
                # Determine tier
                if result['confidence'] >= self.HIGH_CONFIDENCE:
                    result['confidence_tier'] = 'HIGH'
                    result['recommended_action'] = 'engage_aggressive_honeypot'
                elif result['confidence'] >= self.MEDIUM_CONFIDENCE:
                    result['confidence_tier'] = 'MEDIUM'
                    result['recommended_action'] = 'engage_cautious_honeypot'
                else:
                    result['confidence_tier'] = 'LOW'
                    result['recommended_action'] = 'monitor_or_ignore'
                
                result['metadata'] = metadata
                result['latency_ms'] = (time.time() - start_time) * 1000
                
                # Log detection
                if self.monitor:
                    try:
                        result['message'] = message  # For hashing only
                        self.monitor.log_detection(result)
                    except Exception as e:
                        print(f"Monitoring log error: {e}")
                
                return result
        
        # Stage 2: Indian Model (defensive catch + ensemble voting)
        stage2_scam = False
        stage2_conf = 0.0
        
        if self.stage2_loaded:
            is_scam, conf = self._detect_binary(message, self.indian_model, self.indian_tokenizer)
            result['details']['stage2'] = {'detected': is_scam, 'confidence': conf}
            stage2_scam = is_scam
            stage2_conf = conf
            
            # ENSEMBLE VOTING: If both models agree it's a scam, boost confidence
            if use_ensemble and stage1_scam and stage2_scam:
                # Weighted average (Stage 1: 97.9%, Stage 2: 98%)
                ensemble_conf = (stage1_conf * 0.979 + stage2_conf * 0.98) / (0.979 + 0.98)
                
                # Get type
                scam_type, type_conf = self._classify_type(message)
                combined_conf = (ensemble_conf * type_conf) ** 0.5
                
                result['is_scam'] = True
                result['scam_type'] = scam_type
                result['confidence'] = combined_conf
                result['detection_path'] = 'Ensemble(Stage1+2)→Type'
                result['details']['stage3'] = {'type': scam_type, 'confidence': type_conf}
                result['details']['ensemble'] = {
                    'stage1_conf': stage1_conf,
                    'stage2_conf': stage2_conf,
                    'ensemble_conf': ensemble_conf
                }
                
                # Apply metadata boost
                if metadata and metadata.get('overall_suspicion', 0) > 0.5:
                    metadata_boost = metadata['overall_suspicion'] * 0.15  # Higher boost for ensemble
                    result['confidence'] = min(result['confidence'] + metadata_boost, 1.0)
                    result['detection_path'] += '→Metadata++'
                    
            elif is_scam:
                # Only Stage 2 detected (Stage 1 missed)
                scam_type, type_conf = self._classify_type(message)
                combined_conf = (conf * type_conf) ** 0.5
                
                result['is_scam'] = True
                result['scam_type'] = scam_type
                result['confidence'] = combined_conf
                result['detection_path'] = 'Overnight(miss)→Indian→Type'
                result['details']['stage3'] = {'type': scam_type, 'confidence': type_conf}
                
                # Apply metadata boost
                if metadata and metadata.get('overall_suspicion', 0) > 0.5:
                    metadata_boost = metadata['overall_suspicion'] * 0.1
                    result['confidence'] = min(result['confidence'] + metadata_boost, 1.0)
                    result['detection_path'] += '→Metadata+'
            
            # Determine tier & action (if scam detected)
            if result['is_scam']:
                if result['confidence'] >= self.HIGH_CONFIDENCE:
                    result['confidence_tier'] = 'HIGH'
                    result['recommended_action'] = 'engage_aggressive_honeypot'
                elif result['confidence'] >= self.MEDIUM_CONFIDENCE:
                    result['confidence_tier'] = 'MEDIUM'
                    result['recommended_action'] = 'engage_cautious_honeypot'
                else:
                    result['confidence_tier'] = 'LOW'
                    result['recommended_action'] = 'monitor_or_ignore'
                
                result['metadata'] = metadata
                result['latency_ms'] = (time.time() - start_time) * 1000
                
                # Log detection
                if self.monitor:
                    try:
                        result['message'] = message
                        self.monitor.log_detection(result)
                    except Exception as e:
                        print(f"Monitoring log error: {e}")
                
                return result
        
        # Both stages said not scam → Legitimate (but check metadata)
        result['is_scam'] = False
        result['confidence_tier'] = 'LEGITIMATE'
        result['recommended_action'] = 'handle_normally'
        result['detection_path'] = 'Overnight(miss)→Indian(miss)→Legitimate'
        
        # If metadata shows high suspicion despite models saying legit, flag for review
        if metadata and metadata.get('overall_suspicion', 0) > 0.7:
            result['confidence_tier'] = 'LOW'
            result['recommended_action'] = 'monitor_or_review'
            result['detection_path'] += '→Metadata(suspicious!)'
            
        result['metadata'] = metadata
        result['latency_ms'] = (time.time() - start_time) * 1000
        
        # Log even legitimate detections for analytics
        if self.monitor:
            try:
                result['message'] = message
                self.monitor.log_detection(result)
            except Exception as e:
                print(f"Monitoring log error: {e}")
        
        return result


# ============================================================================
# PRODUCTION USAGE EXAMPLES
# ============================================================================

def example_usage():
    """Example of how to use in production."""
    print("="*80)
    print("PRODUCTION USAGE EXAMPLES")
    print("="*80)
    
    detector = ProductionScamDetector()
    
    examples = [
        "Congratulations! You won ₹1 crore lottery. Pay tax now!",
        "Your SBI account has been blocked. Update KYC immediately",
        "Google India: Congratulations! Selected for Software Engineer role",
        "Hi, how are you today?",
    ]
    
    print("\n" + "="*80)
    print("TESTING SAMPLE MESSAGES")
    print("="*80)
    
    for msg in examples:
        result = detector.detect(msg)
        
        print(f"\nMessage: \"{msg[:60]}...\"")
        print(f"  Is Scam: {result['is_scam']}")
        if result['is_scam']:
            print(f"  Type: {result['scam_type']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Tier: {result['confidence_tier']}")
            print(f"  ⚡ Action: {result['recommended_action']}")
        else:
            print(f"  ✅ Legitimate - Handle normally")
        print(f"  Path: {result['detection_path']}")
        print(f"  Latency: {result['latency_ms']:.0f}ms")


if __name__ == "__main__":
    example_usage()
