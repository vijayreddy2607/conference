"""Feedback Database for Active Learning.

Stores human feedback on scam detections for model improvement.
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "feedback.db"


class FeedbackDatabase:
    """Manages feedback collection for active learning."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with feedback schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_id TEXT UNIQUE,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    feedback_type TEXT NOT NULL,
                    original_detection TEXT,
                    corrected_scam_type TEXT,
                    confidence_before REAL,
                    notes TEXT,
                    reviewed_by TEXT,
                    status TEXT DEFAULT 'pending',
                    used_in_training BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Index for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session 
                ON feedback(session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON feedback(status)
            """)
            
            # Training dataset table (merged original + feedback)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_text TEXT NOT NULL,
                    scam_type TEXT NOT NULL,
                    source TEXT,
                    added_date DATE DEFAULT CURRENT_DATE,
                    is_validated BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Model versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_versions (
                    version INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_path TEXT,
                    accuracy REAL,
                    training_size INTEGER,
                    test_size INTEGER,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Feedback database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize feedback database: {e}")
            
    def add_feedback(self, feedback_data: Dict) -> str:
        """Add new feedback entry.
        
        Args:
            feedback_data: Dict with feedback details
            
        Returns:
            Feedback ID
        """
        try:
            import hashlib
            import time
            
            # Generate unique feedback ID
            feedback_id = f"fb-{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback 
                (feedback_id, session_id, feedback_type, original_detection,
                 corrected_scam_type, confidence_before, notes, reviewed_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_id,
                feedback_data.get('session_id'),
                feedback_data.get('feedback_type'),
                feedback_data.get('original_detection'),
                feedback_data.get('corrected_scam_type'),
                feedback_data.get('confidence_before'),
                feedback_data.get('notes'),
                feedback_data.get('reviewed_by')
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Feedback recorded: {feedback_id}")
            return feedback_id
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            raise
            
    def get_feedback(self, feedback_id: str) -> Optional[Dict]:
        """Retrieve specific feedback entry."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM feedback WHERE feedback_id = ?
            """, (feedback_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'feedback_id': row[1],
                    'session_id': row[2],
                    'timestamp': row[3],
                    'feedback_type': row[4],
                    'original_detection': row[5],
                    'corrected_scam_type': row[6],
                    'confidence_before': row[7],
                    'notes': row[8],
                    'reviewed_by': row[9],
                    'status': row[10],
                    'used_in_training': row[11]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving feedback: {e}")
            return None
            
    def get_pending_feedback(self, limit: int = 50) -> List[Dict]:
        """Get all pending feedback entries for review."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM feedback 
                WHERE status = 'pending'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'feedback_id': row[1],
                    'session_id': row[2],
                    'timestamp': row[3],
                    'feedback_type': row[4],
                    'original_detection': row[5],
                    'corrected_scam_type': row[6],
                    'notes': row[8]
                })
                
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting pending feedback: {e}")
            return []
            
    def approve_feedback(self, feedback_id: str) -> bool:
        """Mark feedback as approved for training."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE feedback 
                SET status = 'approved'
                WHERE feedback_id = ?
            """, (feedback_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error approving feedback: {e}")
            return False
            
    def get_training_candidates(self) -> List[Dict]:
        """Get approved feedback ready for training.
        
        Returns:
            List of (message, corrected_scam_type) pairs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # This would need to join with session data to get actual messages
            # For now, return metadata
            cursor.execute("""
                SELECT feedback_id, session_id, corrected_scam_type
                FROM feedback
                WHERE status = 'approved' AND used_in_training = FALSE
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'feedback_id': row[0],
                    'session_id': row[1],
                    'scam_type': row[2]
                })
                
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting training candidates: {e}")
            return []
            
    def get_statistics(self) -> Dict:
        """Get feedback statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Total feedback
            cursor.execute("SELECT COUNT(*) FROM feedback")
            stats['total_feedback'] = cursor.fetchone()[0]
            
            # By status
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM feedback 
                GROUP BY status
            """)
            stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # By type
            cursor.execute("""
                SELECT feedback_type, COUNT(*) 
                FROM feedback 
                GROUP BY feedback_type
            """)
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Ready for training
            cursor.execute("""
                SELECT COUNT(*) FROM feedback
                WHERE status = 'approved' AND used_in_training = FALSE
            """)
            stats['ready_for_training'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


# Testing
if __name__ == "__main__":
    db = FeedbackDatabase()
    
    # Test feedback
    test_feedback = {
        'session_id': 'test-session-123',
        'feedback_type': 'false_positive',
        'original_detection': 'fake_job',
        'corrected_scam_type': 'legitimate',
        'confidence_before': 0.85,
        'notes': 'This was actually a legitimate job posting',
        'reviewed_by': 'admin@test.com'
    }
    
    fb_id = db.add_feedback(test_feedback)
    print(f"✅ Feedback added: {fb_id}")
    
    # Get stats
    stats = db.get_statistics()
    print(f"\n📊 Statistics: {stats}")
