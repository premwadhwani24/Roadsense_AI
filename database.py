"""
Database initialization and models for RoadSense AI system
Handles users, alerts, work orders, and road condition history
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "roadsense.db"

def init_database():
    """Initialize database schema with all required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            city TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            assigned_to INTEGER REFERENCES users(id),
            notification_sent BOOLEAN DEFAULT 0
        )
    ''')
    
    # Work Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            work_type TEXT NOT NULL,
            contractor TEXT,
            estimated_cost REAL,
            actual_cost REAL,
            status TEXT DEFAULT 'pending',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            before_photo TEXT,
            after_photo TEXT,
            notes TEXT
        )
    ''')
    
    # Road History (for trending)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS road_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            condition_status TEXT,
            traffic_level REAL,
            weather_condition TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Citizen Reports (crowdsourced)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citizen_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT,
            road_name TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            issue_type TEXT NOT NULL,
            description TEXT,
            image_path TEXT,
            verified BOOLEAN DEFAULT 0,
            verification_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Budget Tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            year INTEGER NOT NULL,
            allocated_budget REAL,
            spent REAL DEFAULT 0,
            remaining REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # IoT Telemetry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iot_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            vibration_level REAL,
            temperature REAL,
            traffic_load_index REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Vehicle Crowd-Sensing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_crowdsense (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL,
            road_id TEXT,
            latitude REAL,
            longitude REAL,
            anomaly_type TEXT,
            confidence REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Blockchain Ledger
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_hash TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            transaction_type TEXT,
            payload TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nonce INTEGER
        )
    ''')
    
    # Digital Twin States
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digital_twin_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            road_id TEXT NOT NULL,
            simulated_age_days INTEGER,
            stress_level REAL,
            weather_impact_factor REAL,
            overall_health_score REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

class DatabaseManager:
    """Manager for all database operations"""
    
    @staticmethod
    def add_user(username: str, email: str, password_hash: str, role: str = 'viewer', 
                 city: str = None, phone: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, role, city, phone) VALUES (?, ?, ?, ?, ?, ?)',
                (username, email, password_hash, role, city, phone)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        finally:
            conn.close()
    
    @staticmethod
    def get_user(username: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    @staticmethod
    def add_alert(road_id: str, road_name: str, severity: str, description: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO alerts (road_id, road_name, severity, description) VALUES (?, ?, ?, ?)',
                (road_id, road_name, severity, description)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def get_alerts(status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('SELECT * FROM alerts WHERE status = ? ORDER BY created_at DESC LIMIT ?', 
                             (status, limit))
            else:
                cursor.execute('SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def add_work_order(road_id: str, road_name: str, work_type: str, created_by: int,
                      contractor: str = None, estimated_cost: float = None, notes: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO work_orders (road_id, road_name, work_type, created_by, contractor, estimated_cost, notes) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (road_id, road_name, work_type, created_by, contractor, estimated_cost, notes)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def get_work_orders(status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('SELECT * FROM work_orders WHERE status = ? ORDER BY created_at DESC LIMIT ?',
                             (status, limit))
            else:
                cursor.execute('SELECT * FROM work_orders ORDER BY created_at DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def update_work_order_cost(work_order_id: int, actual_cost: float):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE work_orders SET actual_cost = ? WHERE id = ?', 
                         (actual_cost, work_order_id))
            conn.commit()
        finally:
            conn.close()
    
    @staticmethod
    def add_road_history(road_id: str, road_name: str, condition_status: str, 
                        traffic_level: float = None, weather_condition: str = None):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO road_history (road_id, road_name, condition_status, traffic_level, weather_condition) '
                'VALUES (?, ?, ?, ?, ?)',
                (road_id, road_name, condition_status, traffic_level, weather_condition)
            )
            conn.commit()
        finally:
            conn.close()
    
    @staticmethod
    def get_road_history(road_id: str, days: int = 30) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(
                'SELECT * FROM road_history WHERE road_id = ? AND recorded_at > datetime("now", "-' + str(days) + ' days") '
                'ORDER BY recorded_at DESC',
                (road_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    @staticmethod
    def add_citizen_report(latitude: float, longitude: float, issue_type: str, 
                          description: str = None, road_id: str = None, road_name: str = None) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO citizen_reports (road_id, road_name, latitude, longitude, issue_type, description) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (road_id, road_name, latitude, longitude, issue_type, description)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    @staticmethod
    def get_citizen_reports(status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute('SELECT * FROM citizen_reports WHERE status = ? ORDER BY created_at DESC LIMIT ?',
                             (status, limit))
            else:
                cursor.execute('SELECT * FROM citizen_reports ORDER BY created_at DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def add_iot_telemetry(road_id: str, vibration_level: float, temperature: float, traffic_load_index: float) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO iot_telemetry (road_id, vibration_level, temperature, traffic_load_index) VALUES (?, ?, ?, ?)',
                (road_id, vibration_level, temperature, traffic_load_index)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def get_iot_telemetry(road_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM iot_telemetry WHERE road_id = ? ORDER BY recorded_at DESC LIMIT ?', (road_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def add_vehicle_anomaly(vehicle_id: str, road_id: str, latitude: float, longitude: float, anomaly_type: str, confidence: float) -> int:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO vehicle_crowdsense (vehicle_id, road_id, latitude, longitude, anomaly_type, confidence) VALUES (?, ?, ?, ?, ?, ?)',
                (vehicle_id, road_id, latitude, longitude, anomaly_type, confidence)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

if __name__ == "__main__":
    init_database()
