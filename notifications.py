"""
Notification system for RoadSense AI
Handles email, SMS, and in-app alerts
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
from database import DatabaseManager

SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'your-email@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-password')
SMS_API_KEY = os.environ.get('SMS_API_KEY', '')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')

class NotificationManager:
    """Centralized notification system"""
    
    @staticmethod
    def send_email(recipient: str, subject: str, body: str, html: str = None) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_SENDER
            msg['To'] = recipient
            
            msg.attach(MIMEText(body, 'plain'))
            if html:
                msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"Email sent to {recipient}")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_sms(phone: str, message: str) -> bool:
        """Send SMS notification via Twilio"""
        try:
            if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
                print("Twilio credentials not configured")
                return False
            
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=message,
                from_=os.environ.get('TWILIO_PHONE_NUMBER', ''),
                to=phone
            )
            print(f"SMS sent: {message.sid}")
            return True
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False
    
    @staticmethod
    def alert_critical_road(road_id: str, road_name: str, severity: str, description: str):
        """Create alert for critical road condition"""
        alert_id = DatabaseManager.add_alert(road_id, road_name, severity, description)
        
        # Get all engineers/admins
        import sqlite3
        conn = sqlite3.connect('roadsense.db')
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE role IN ("admin", "engineer")')
            engineers = [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
        
        # Notify each
        for engineer in engineers:
            subject = f"RoadSense Alert: {severity} condition on {road_name}"
            body = f"Road: {road_name} (ID: {road_id})\nSeverity: {severity}\nDescription: {description}"
            
            if engineer.get('email'):
                NotificationManager.send_email(engineer['email'], subject, body)
            
            if engineer.get('phone') and severity == 'RED':
                NotificationManager.send_sms(engineer['phone'], f"ALERT: {road_name} is {severity}")
        
        return alert_id
    
    @staticmethod
    def send_daily_summary(user_email: str, summary_data: Dict[str, Any]) -> bool:
        """Send daily dashboard summary"""
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>RoadSense Daily Summary</h2>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                
                <h3>Status Overview</h3>
                <ul>
                    <li>Green Roads: {summary_data.get('green', 0)}</li>
                    <li>Yellow Roads: {summary_data.get('yellow', 0)}</li>
                    <li>Red Roads: {summary_data.get('red', 0)}</li>
                </ul>
                
                <h3>Pending Work Orders</h3>
                <p>{summary_data.get('pending_work_orders', 0)} pending repairs</p>
                
                <h3>Open Alerts</h3>
                <p>{summary_data.get('open_alerts', 0)} unresolved alerts</p>
                
                <hr>
                <p><em>This is an automated message from RoadSense AI System</em></p>
            </body>
        </html>
        """
        
        subject = f"RoadSense Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
        body = f"Green: {summary_data.get('green', 0)}, Yellow: {summary_data.get('yellow', 0)}, Red: {summary_data.get('red', 0)}"
        
        return NotificationManager.send_email(user_email, subject, body, html)
    
    @staticmethod
    def notify_repair_completion(work_order_id: int, user_id: int):
        """Notify stakeholders of repair completion"""
        import sqlite3
        conn = sqlite3.connect('roadsense.db')
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM work_orders WHERE id = ?', (work_order_id,))
            work_order_row = cursor.fetchone()
            work_order = dict(work_order_row) if work_order_row else None
            
            cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
        finally:
            conn.close()
        
        if user and work_order:
            subject = f"Repair Completed: {work_order['road_name']}"
            body = f"""
            Repair work on {work_order['road_name']} has been completed.
            Work Type: {work_order['work_type']}
            Actual Cost: {work_order['actual_cost']}
            """
            NotificationManager.send_email(user['email'], subject, body)
            return True
        
        return False
