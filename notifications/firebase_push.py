#!/usr/bin/env python3
"""
FIREBASE PUSH NOTIFICATION SYSTEM
Real-time iPhone notifications for AgentX5 trading alerts

Features:
- Push notifications to iPhone
- Email notifications
- SMS via Twilio
- Multi-channel delivery
- Priority levels
"""

import os
import asyncio
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from enum import Enum

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  Firebase Admin SDK not installed. Run: pip install firebase-admin")

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed. Run: pip install twilio")

from dotenv import load_dotenv
load_dotenv()


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Available notification channels"""
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    ALL = "all"


class FirebasePushNotification:
    """
    Multi-channel notification system for AgentX5

    Sends notifications via:
    - Firebase Cloud Messaging (iPhone/Android push)
    - Email (Gmail SMTP)
    - SMS (Twilio)
    """

    def __init__(self):
        # Email configuration
        self.email_address = os.getenv("EMAIL_ADDRESS", "terobinsony@gmail.com")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")

        # Twilio configuration
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "")
        self.user_phone = os.getenv("USER_PHONE_NUMBER", "")

        # Firebase configuration
        self.firebase_server_key = os.getenv("FIREBASE_SERVER_KEY", "")
        self.firebase_project_id = os.getenv("FIREBASE_PROJECT_ID", "")

        # Initialize Firebase (if configured)
        self.firebase_initialized = False
        if FIREBASE_AVAILABLE and self.firebase_server_key:
            try:
                self._initialize_firebase()
            except Exception as e:
                print(f"⚠️  Firebase initialization failed: {e}")

        # Initialize Twilio (if configured)
        self.twilio_client = None
        if TWILIO_AVAILABLE and self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = TwilioClient(self.twilio_sid, self.twilio_token)
                print("✅ Twilio SMS initialized")
            except Exception as e:
                print(f"⚠️  Twilio initialization failed: {e}")

        self.notification_log = []

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if not self.firebase_initialized:
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": self.firebase_project_id,
                    "private_key": self.firebase_server_key.replace('\\n', '\n'),
                    # Add other required Firebase credentials here
                })
                firebase_admin.initialize_app(cred)
                self.firebase_initialized = True
                print("✅ Firebase Cloud Messaging initialized")
        except Exception as e:
            print(f"⚠️  Firebase setup: {e}")
            print("   Configure FIREBASE_SERVER_KEY and FIREBASE_PROJECT_ID in .env")

    async def send_push_notification(
        self,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> bool:
        """
        Send push notification via Firebase Cloud Messaging

        Args:
            title: Notification title
            body: Notification body
            data: Additional data payload
            priority: Notification priority

        Returns:
            bool: Success status
        """
        if not self.firebase_initialized:
            print("📱 Push notification (Firebase not configured):")
            print(f"   Title: {title}")
            print(f"   Body: {body[:100]}...")
            return False

        try:
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                android=messaging.AndroidConfig(
                    priority='high' if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else 'normal'
                ),
                apns=messaging.APNSConfig(
                    headers={
                        'apns-priority': '10' if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else '5'
                    },
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )

            # Send to topic or device token
            # For production, you'd send to specific device tokens
            response = messaging.send(message)
            print(f"✅ Push notification sent: {response}")
            return True

        except Exception as e:
            print(f"❌ Push notification failed: {e}")
            return False

    async def send_email_notification(
        self,
        subject: str,
        body: str,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> bool:
        """
        Send email notification via Gmail SMTP

        Args:
            subject: Email subject
            body: Email body
            priority: Email priority

        Returns:
            bool: Success status
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.email_address
            msg['Subject'] = f"[{priority.value.upper()}] AgentX5: {subject}"

            # Add priority headers
            if priority == NotificationPriority.CRITICAL:
                msg['X-Priority'] = '1'
                msg['Importance'] = 'high'

            email_body = f"""
AgentX5 Trading System Notification
{'='*60}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Priority: {priority.value.upper()}

{body}

{'='*60}
This is an automated notification from AgentX5.
            """

            msg.attach(MIMEText(email_body, 'plain'))

            if self.email_password:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(self.email_address, self.email_password)
                    server.send_message(msg)
                    print(f"✅ Email sent: {subject}")
                    return True
            else:
                print(f"📧 Email (no password configured): {subject}")
                print(f"   To enable: Add EMAIL_PASSWORD to .env")
                print(f"   Body preview: {body[:100]}...")
                return False

        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

    async def send_sms_notification(
        self,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> bool:
        """
        Send SMS notification via Twilio

        Args:
            message: SMS message (max 160 characters)
            priority: Message priority

        Returns:
            bool: Success status
        """
        if not self.twilio_client:
            print(f"📱 SMS (Twilio not configured): {message[:50]}...")
            return False

        try:
            # Truncate message to 160 characters
            sms_body = message[:160]

            sms = self.twilio_client.messages.create(
                body=sms_body,
                from_=self.twilio_phone,
                to=self.user_phone
            )

            print(f"✅ SMS sent: {sms.sid}")
            return True

        except Exception as e:
            print(f"❌ SMS failed: {e}")
            return False

    async def send_notification(
        self,
        title: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.ALL,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Optional[Dict] = None
    ) -> Dict[str, bool]:
        """
        Send notification across specified channels

        Args:
            title: Notification title
            message: Notification message
            channel: Delivery channel(s)
            priority: Notification priority
            data: Additional data

        Returns:
            Dict of channel: success status
        """
        results = {}

        # Log notification
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "channel": channel.value,
            "priority": priority.value
        }
        self.notification_log.append(log_entry)

        # Send via requested channels
        if channel in [NotificationChannel.PUSH, NotificationChannel.ALL]:
            results['push'] = await self.send_push_notification(title, message, data, priority)

        if channel in [NotificationChannel.EMAIL, NotificationChannel.ALL]:
            results['email'] = await self.send_email_notification(title, message, priority)

        if channel in [NotificationChannel.SMS, NotificationChannel.ALL]:
            sms_message = f"{title}: {message}"
            results['sms'] = await self.send_sms_notification(sms_message, priority)

        return results

    async def notify_trade_executed(self, trade: Dict):
        """Send notification when trade is executed"""
        title = f"Trade Executed: {trade.get('pair', 'Unknown')}"
        message = f"""
Pattern: {trade.get('pattern', 'N/A')} ({trade.get('accuracy', 0)}% accuracy)
Entry: {trade.get('entry_price', 0)}
Stop Loss: {trade.get('stop_loss', 0)}
Take Profit: {trade.get('take_profit', 0)}
Position: ${trade.get('position_size', 0):.2f}
        """

        await self.send_notification(
            title,
            message,
            NotificationChannel.ALL,
            NotificationPriority.HIGH,
            data=trade
        )

    async def notify_trade_closed(self, trade: Dict):
        """Send notification when trade closes"""
        outcome = trade.get('outcome', 'UNKNOWN')
        profit = trade.get('profit', 0)

        if outcome == "WIN":
            priority = NotificationPriority.CRITICAL
            emoji = "✅"
        else:
            priority = NotificationPriority.HIGH
            emoji = "❌"

        title = f"{emoji} Trade {outcome}: {trade.get('pair', 'Unknown')}"
        message = f"""
Profit/Loss: ${profit:.2f}
Exit Price: {trade.get('exit_price', 'N/A')}
Duration: {trade.get('duration', 'N/A')}
        """

        await self.send_notification(
            title,
            message,
            NotificationChannel.ALL,
            priority,
            data=trade
        )

    async def notify_pattern_detected(self, pair: str, pattern: str, accuracy: int):
        """Send notification when high-probability pattern is detected"""
        title = f"Pattern Detected: {pair}"
        message = f"""
Pattern: {pattern}
Accuracy: {accuracy}%
Status: Analyzing entry point...
        """

        await self.send_notification(
            title,
            message,
            NotificationChannel.ALL,
            NotificationPriority.NORMAL,
            data={"pair": pair, "pattern": pattern, "accuracy": accuracy}
        )

    async def notify_system_alert(self, alert_type: str, alert_message: str):
        """Send system alert notification"""
        title = f"System Alert: {alert_type}"

        await self.send_notification(
            title,
            alert_message,
            NotificationChannel.ALL,
            NotificationPriority.CRITICAL
        )

    async def notify_daily_summary(self, summary: Dict):
        """Send daily trading summary"""
        title = "Daily Trading Summary"
        message = f"""
Total Trades: {summary.get('total_trades', 0)}
Wins: {summary.get('wins', 0)}
Losses: {summary.get('losses', 0)}
Win Rate: {summary.get('win_rate', 0):.1f}%
Total P/L: ${summary.get('total_profit', 0):.2f}
        """

        await self.send_notification(
            title,
            message,
            NotificationChannel.ALL,
            NotificationPriority.NORMAL,
            data=summary
        )


async def test_notifications():
    """Test all notification channels"""
    print("="*80)
    print("TESTING AGENTX5 NOTIFICATION SYSTEM")
    print("="*80)

    notifier = FirebasePushNotification()

    # Test 1: Email notification
    print("\n📧 Testing email notification...")
    await notifier.send_notification(
        "Test Email",
        "This is a test email notification from AgentX5",
        NotificationChannel.EMAIL,
        NotificationPriority.NORMAL
    )

    await asyncio.sleep(2)

    # Test 2: SMS notification
    print("\n📱 Testing SMS notification...")
    await notifier.send_notification(
        "Test SMS",
        "This is a test SMS from AgentX5",
        NotificationChannel.SMS,
        NotificationPriority.NORMAL
    )

    await asyncio.sleep(2)

    # Test 3: Push notification
    print("\n🔔 Testing push notification...")
    await notifier.send_notification(
        "Test Push",
        "This is a test push notification from AgentX5",
        NotificationChannel.PUSH,
        NotificationPriority.NORMAL
    )

    await asyncio.sleep(2)

    # Test 4: All channels (trade executed)
    print("\n🚀 Testing trade executed notification (all channels)...")
    test_trade = {
        "pair": "GBPJPY",
        "pattern": "Inverse H&S",
        "accuracy": 94,
        "entry_price": 185.432,
        "stop_loss": 185.232,
        "take_profit": 186.132,
        "position_size": 200.00
    }
    await notifier.notify_trade_executed(test_trade)

    print("\n" + "="*80)
    print("NOTIFICATION TESTS COMPLETE")
    print("="*80)
    print(f"\nTotal notifications sent: {len(notifier.notification_log)}")


if __name__ == "__main__":
    print("\n🔔 AgentX5 Notification System")
    print("Testing all notification channels...\n")

    asyncio.run(test_notifications())
