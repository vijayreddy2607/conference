"""Monitoring & Logging System for Production Scam Detection.

Tracks detection performance, confidence distributions, and provides
analytics for continuous improvement.
"""
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "production_logs.db"


class DetectionMonitor:
    """Monitors and logs scam detection performance in production."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Detections table (detailed logs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    message_hash TEXT,
                    is_scam BOOLEAN,
                    scam_type TEXT,
                    confidence REAL,
                    confidence_tier TEXT,
                    detection_path TEXT,
                    metadata_json TEXT,
                    latency_ms INTEGER
                )
            """)
            
            # Daily stats table (aggregated)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date DATE PRIMARY KEY,
                    total_detections INTEGER DEFAULT 0,
                    scam_count INTEGER DEFAULT 0,
                    legit_count INTEGER DEFAULT 0,
                    avg_confidence REAL,
                    high_confidence_count INTEGER DEFAULT 0,
                    medium_confidence_count INTEGER DEFAULT 0,
                    low_confidence_count INTEGER DEFAULT 0
                )
            """)
            
            # Confidence distribution table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confidence_distribution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    confidence_bucket TEXT,
                    count INTEGER DEFAULT 0,
                    UNIQUE(date, confidence_bucket)
                )
            """)
            
            # Scam type performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scam_type_stats (
                    scam_type TEXT PRIMARY KEY,
                    total_detections INTEGER DEFAULT 0,
                    avg_confidence REAL,
                    last_detected DATETIME
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Monitoring database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize monitoring database: {e}")
            
    def log_detection(self, result: Dict):
        """Log a single detection result.
        
        Args:
            result: Detection result from ProductionScamDetector
        """
        try:
            # Hash message for privacy (don't store actual content)
            message_hash = hashlib.sha256(
                str(result.get('message', '')).encode()
            ).hexdigest()[:16]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert detection record
            cursor.execute("""
                INSERT INTO detections 
                (message_hash, is_scam, scam_type, confidence, confidence_tier,
                 detection_path, metadata_json, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_hash,
                result.get('is_scam', False),
                result.get('scam_type'),
                result.get('confidence', 0.0),
                result.get('confidence_tier', 'UNKNOWN'),
                result.get('detection_path', ''),
                json.dumps(result.get('details', {})),
                int(result.get('latency_ms', 0))
            ))
            
            conn.commit()
            conn.close()
            
            # Update aggregated stats
            self._update_daily_stats(result)
            self._update_confidence_distribution(result)
            self._update_scam_type_stats(result)
            
        except Exception as e:
            logger.error(f"Error logging detection: {e}")
            
    def _update_daily_stats(self, result: Dict):
        """Update daily aggregated statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date()
            is_scam = result.get('is_scam', False)
            tier = result.get('confidence_tier', 'UNKNOWN')
            
            # Insert or update daily stats
            cursor.execute("""
                INSERT INTO daily_stats 
                (date, total_detections, scam_count, legit_count,
                 high_confidence_count, medium_confidence_count, low_confidence_count)
                VALUES (?, 1, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    total_detections = total_detections + 1,
                    scam_count = scam_count + ?,
                    legit_count = legit_count + ?,
                    high_confidence_count = high_confidence_count + ?,
                    medium_confidence_count = medium_confidence_count + ?,
                    low_confidence_count = low_confidence_count + ?
            """, (
                today,
                1 if is_scam else 0,
                0 if is_scam else 1,
                1 if tier == 'HIGH' else 0,
                1 if tier == 'MEDIUM' else 0,
                1 if tier == 'LOW' else 0,
                # For UPDATE clause
                1 if is_scam else 0,
                0 if is_scam else 1,
                1 if tier == 'HIGH' else 0,
                1 if tier == 'MEDIUM' else 0,
                1 if tier == 'LOW' else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")
            
    def _update_confidence_distribution(self, result: Dict):
        """Update confidence distribution histogram."""
        try:
            confidence = result.get('confidence', 0.0)
            
            # Bucket confidence into ranges
            if confidence >= 0.9:
                bucket = '0.9-1.0'
            elif confidence >= 0.8:
                bucket = '0.8-0.9'
            elif confidence >= 0.7:
                bucket = '0.7-0.8'
            elif confidence >= 0.6:
                bucket = '0.6-0.7'
            elif confidence >= 0.5:
                bucket = '0.5-0.6'
            else:
                bucket = '0.0-0.5'
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().date()
            
            cursor.execute("""
                INSERT INTO confidence_distribution (date, confidence_bucket, count)
                VALUES (?, ?, 1)
                ON CONFLICT(date, confidence_bucket) DO UPDATE SET
                    count = count + 1
            """, (today, bucket))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating confidence distribution: {e}")
            
    def _update_scam_type_stats(self, result: Dict):
        """Update per-scam-type statistics."""
        if not result.get('is_scam'):
            return
            
        try:
            scam_type = result.get('scam_type', 'unknown')
            confidence = result.get('confidence', 0.0)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current stats
            cursor.execute("""
                SELECT total_detections, avg_confidence 
                FROM scam_type_stats 
                WHERE scam_type = ?
            """, (scam_type,))
            
            row = cursor.fetchone()
            if row:
                total, avg_conf = row
                new_total = total + 1
                new_avg = (avg_conf * total + confidence) / new_total
            else:
                new_total = 1
                new_avg = confidence
                
            cursor.execute("""
                INSERT INTO scam_type_stats 
                (scam_type, total_detections, avg_confidence, last_detected)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(scam_type) DO UPDATE SET
                    total_detections = ?,
                    avg_confidence = ?,
                    last_detected = CURRENT_TIMESTAMP
            """, (scam_type, new_total, new_avg, new_total, new_avg))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating scam type stats: {e}")
            
    def get_confidence_distribution(self, days: int = 7) -> Dict:
        """Get confidence distribution for last N days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = datetime.now().date() - timedelta(days=days)
            
            cursor.execute("""
                SELECT confidence_bucket, SUM(count) as total
                FROM confidence_distribution
                WHERE date >= ?
                GROUP BY confidence_bucket
                ORDER BY confidence_bucket DESC
            """, (start_date,))
            
            distribution = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting confidence distribution: {e}")
            return {}
            
    def get_daily_summary(self, date: str = None) -> Dict:
        """Get summary statistics for a specific date (default: today)."""
        try:
            target_date = date or datetime.now().date()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM daily_stats WHERE date = ?
            """, (target_date,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'date': row[0],
                    'total_detections': row[1],
                    'scam_count': row[2],
                    'legit_count': row[3],
                    'avg_confidence': row[4],
                    'high_confidence': row[5],
                    'medium_confidence': row[6],
                    'low_confidence': row[7]
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return {}
            
    def get_scam_type_performance(self) -> List[Dict]:
        """Get performance metrics per scam type."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT scam_type, total_detections, avg_confidence, last_detected
                FROM scam_type_stats
                ORDER BY total_detections DESC
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'scam_type': row[0],
                    'total_detections': row[1],
                    'avg_confidence': row[2],
                    'last_detected': row[3]
                })
                
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting scam type performance: {e}")
            return []


# Testing
if __name__ == "__main__":
    monitor = DetectionMonitor()
    
    # Test logging
    test_result = {
        'message': 'Test scam message',
        'is_scam': True,
        'scam_type': 'fake_job',
        'confidence': 0.92,
        'confidence_tier': 'HIGH',
        'detection_path': 'Overnight→Type',
        'latency_ms': 1850
    }
    
    monitor.log_detection(test_result)
    print("✅ Test detection logged")
    
    # Get stats
    dist = monitor.get_confidence_distribution()
    print(f"\nConfidence Distribution: {dist}")
    
    summary = monitor.get_daily_summary()
    print(f"\nToday's Summary: {summary}")
