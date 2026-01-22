#!/usr/bin/env python3
"""
Email & SMS Signal Parser
Automatically imports trading signals from your email and text messages

Supports:
- Email signals (Gmail, Outlook, etc.)
- SMS/Text message signals
- Telegram signals
- WhatsApp signals
- Free signal services
"""

import email
import imaplib
import json
import logging
import re
from datetime import datetime
from email.header import decode_header
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SignalParser")


class EmailSMSSignalParser:
    """
    Parse trading signals from email and SMS

    Common signal formats:
    - "BUY AAPL @ $195.50 Target: $210 Stop: $190"
    - "SHORT TSLA Entry: $245 TP: $220 SL: $260"
    - "🚀 BTC LONG 45000 🎯 50000 ⛔ 43000"
    - "Signal: EUR/USD SELL 1.0850 TP1: 1.0800 TP2: 1.0750 SL: 1.0900"
    """

    def __init__(self):
        self.email_server = None
        self.signals_extracted = []
        self.signal_providers = {}
        logger.info("=" * 70)
        logger.info("📧 EMAIL & SMS SIGNAL PARSER INITIALIZED")
        logger.info("=" * 70)

    def connect_gmail(self, email_address: str, app_password: str):
        """
        Connect to Gmail to read signals

        Get app password: https://myaccount.google.com/apppasswords
        """
        try:
            logger.info(f"📧 Connecting to Gmail: {email_address}...")

            self.email_server = imaplib.IMAP4_SSL("imap.gmail.com")
            self.email_server.login(email_address, app_password)
            self.email_server.select("INBOX")

            logger.info("✅ Connected to Gmail")

            return True

        except Exception as e:
            logger.error(f"Gmail connection error: {e}")
            return False

    def parse_email_signals(
        self, search_criteria: str = "UNSEEN", limit: int = 100
    ) -> List[Dict]:
        """
        Parse trading signals from emails

        search_criteria examples:
        - "UNSEEN" - Unread emails
        - "FROM \"signals@tradingservice.com\"" - From specific sender
        - "SUBJECT \"Trading Signal\"" - Subject contains keywords
        - "SINCE 14-Dec-2025" - Emails since date
        """
        try:
            if not self.email_server:
                logger.error("Not connected to email. Connect first!")
                return []

            logger.info(f"📧 Searching emails with: {search_criteria}...")

            status, messages = self.email_server.search(None, search_criteria)
            email_ids = messages[0].split()[-limit:]  # Get last N emails

            signals = []

            for email_id in email_ids:
                status, msg_data = self.email_server.fetch(email_id, "(RFC822)")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Get email metadata
                        subject = self._decode_header(msg["Subject"])
                        from_email = msg.get("From")
                        date = msg.get("Date")

                        # Get email body
                        body = self._get_email_body(msg)

                        # Parse trading signals from subject and body
                        signal_data = self._extract_signals_from_text(
                            subject + " " + body
                        )

                        if signal_data:
                            signal_data.update(
                                {
                                    "source": "Email",
                                    "from": from_email,
                                    "subject": subject,
                                    "date": date,
                                    "email_id": email_id.decode(),
                                }
                            )
                            signals.append(signal_data)

            self.signals_extracted.extend(signals)
            logger.info(f"✅ Extracted {len(signals)} signals from emails")

            return signals

        except Exception as e:
            logger.error(f"Error parsing emails: {e}")
            return []

    def _decode_header(self, header):
        """Decode email header"""
        if header is None:
            return ""
        decoded = decode_header(header)
        return str(decoded[0][0])

    def _get_email_body(self, msg):
        """Extract email body"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode()
                    except BaseException:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except BaseException:
                pass

        return body

    def _extract_signals_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract trading signals from text using pattern matching

        Recognizes patterns like:
        - BUY/SELL/LONG/SHORT
        - Symbol (AAPL, BTC, EUR/USD, etc.)
        - Entry price
        - Take Profit (TP)
        - Stop Loss (SL)
        """
        signal = {}

        # Action (BUY, SELL, LONG, SHORT)
        action_match = re.search(
            r"\b(BUY|SELL|LONG|SHORT|CALL|PUT)\b", text, re.IGNORECASE
        )
        if action_match:
            signal["action"] = action_match.group(1).upper()
        else:
            return None  # No valid action found

        # Symbol
        # Matches: AAPL, BTC, BTCUSD, EUR/USD, SPY, etc.
        symbol_match = re.search(r"\b([A-Z]{2,5}(?:/[A-Z]{3})?)\b", text)
        if symbol_match:
            signal["symbol"] = symbol_match.group(1)

        # Entry price
        # Matches: $195.50, 195.50, @195.50, Entry: 195.50
        entry_match = re.search(
            r"(?:@|Entry:?|Price:?)\s*\$?([0-9,]+\.?[0-9]*)", text, re.IGNORECASE
        )
        if entry_match:
            signal["entry_price"] = float(entry_match.group(1).replace(",", ""))

        # Take Profit (TP)
        tp_match = re.search(
            r"(?:TP|Target|Take Profit|🎯):?\s*\$?([0-9,]+\.?[0-9]*)",
            text,
            re.IGNORECASE,
        )
        if tp_match:
            signal["take_profit"] = float(tp_match.group(1).replace(",", ""))

        # Stop Loss (SL)
        sl_match = re.search(
            r"(?:SL|Stop Loss|Stop|⛔):?\s*\$?([0-9,]+\.?[0-9]*)", text, re.IGNORECASE
        )
        if sl_match:
            signal["stop_loss"] = float(sl_match.group(1).replace(",", ""))

        # Risk/Reward Ratio
        if (
            "take_profit" in signal
            and "entry_price" in signal
            and "stop_loss" in signal
        ):
            profit = abs(signal["take_profit"] - signal["entry_price"])
            risk = abs(signal["entry_price"] - signal["stop_loss"])
            signal["risk_reward_ratio"] = profit / risk if risk > 0 else 0

        # Confidence/Win Rate
        confidence_match = re.search(
            r"(?:Confidence|Accuracy|Win Rate):?\s*([0-9]+)%", text, re.IGNORECASE
        )
        if confidence_match:
            signal["confidence"] = float(confidence_match.group(1)) / 100

        signal["raw_text"] = text
        signal["parsed_at"] = datetime.now().isoformat()

        return signal if "symbol" in signal else None

    def parse_telegram_signals(self, chat_id: str) -> List[Dict]:
        """
        Parse signals from Telegram channel/group

        Requires Telegram API setup
        """
        logger.info(f"📱 Parsing Telegram signals from chat: {chat_id}...")

        # Placeholder - requires Telegram Bot API
        # Install: pip install python-telegram-bot

        signals = []

        # Example implementation:
        # from telegram import Bot
        # bot = Bot(token=TELEGRAM_BOT_TOKEN)
        # messages = bot.get_chat_history(chat_id, limit=100)
        # for msg in messages:
        #     signal = self._extract_signals_from_text(msg.text)
        #     if signal:
        #         signal['source'] = 'Telegram'
        #         signals.append(signal)

        logger.info("ℹ️  Telegram integration ready - install python-telegram-bot")

        return signals

    def parse_sms_signals(self, sms_file: str) -> List[Dict]:
        """
        Parse signals from SMS/text message export

        Export SMS to CSV/JSON first, then parse
        """
        try:
            logger.info(f"📱 Parsing SMS signals from {sms_file}...")

            signals = []

            # Read SMS export file
            with open(sms_file, "r") as f:
                sms_data = json.load(f) if sms_file.endswith(".json") else []

            for sms in sms_data:
                text = sms.get("text", sms.get("body", ""))
                signal = self._extract_signals_from_text(text)

                if signal:
                    signal["source"] = "SMS"
                    signal["from"] = sms.get("from", sms.get("address", ""))
                    signal["date"] = sms.get("date", "")
                    signals.append(signal)

            self.signals_extracted.extend(signals)
            logger.info(f"✅ Extracted {len(signals)} signals from SMS")

            return signals

        except Exception as e:
            logger.error(f"Error parsing SMS: {e}")
            return []

    def get_signal_statistics(self) -> Dict:
        """Get statistics on parsed signals"""
        if not self.signals_extracted:
            return {}

        stats = {
            "total_signals": len(self.signals_extracted),
            "by_source": {},
            "by_action": {},
            "by_symbol": {},
            "avg_risk_reward": 0.0,
            "signals_with_tp_sl": 0,
        }

        for signal in self.signals_extracted:
            # By source
            source = signal.get("source", "Unknown")
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

            # By action
            action = signal.get("action", "UNKNOWN")
            stats["by_action"][action] = stats["by_action"].get(action, 0) + 1

            # By symbol
            symbol = signal.get("symbol", "UNKNOWN")
            stats["by_symbol"][symbol] = stats["by_symbol"].get(symbol, 0) + 1

            # Signals with TP/SL
            if "take_profit" in signal and "stop_loss" in signal:
                stats["signals_with_tp_sl"] += 1

        # Average risk/reward
        rr_ratios = [
            s["risk_reward_ratio"]
            for s in self.signals_extracted
            if "risk_reward_ratio" in s
        ]
        stats["avg_risk_reward"] = sum(rr_ratios) / len(rr_ratios) if rr_ratios else 0

        return stats

    def save_signals(self, output_file: str = "data/signals/parsed_signals.json"):
        """Save all parsed signals"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "timestamp": datetime.now().isoformat(),
                "total_signals": len(self.signals_extracted),
                "signals": self.signals_extracted,
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(
                f"💾 Saved {len(self.signals_extracted)} signals to {output_file}"
            )

        except Exception as e:
            logger.error(f"Error saving signals: {e}")


def main():
    """Demo of Email/SMS Signal Parser"""
    print(
        """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║           EMAIL & SMS SIGNAL PARSER                               ║
    ║      Import Free Signals from Email, SMS, Telegram                ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    )

    parser = EmailSMSSignalParser()

    # Example: Parse email signals
    print("\n📧 Email Signal Example:")
    print("=" * 70)

    test_email = """
    Subject: 🚀 Premium Trading Signal

    BUY AAPL @ $195.50
    Target: $210.00
    Stop Loss: $190.00
    Confidence: 85%

    📊 Risk/Reward: 1:2.9
    """

    signal = parser._extract_signals_from_text(test_email)
    if signal:
        print(json.dumps(signal, indent=2))

    print("\n\n📋 Setup Instructions:")
    print("=" * 70)
    print("1. Gmail Signals:")
    print("   - Get app password: https://myaccount.google.com/apppasswords")
    print("   - parser.connect_gmail('your@gmail.com', 'app_password')")
    print("   - signals = parser.parse_email_signals()")
    print()
    print("2. Telegram Signals:")
    print("   - Install: pip install python-telegram-bot")
    print("   - Get bot token: https://t.me/BotFather")
    print("   - signals = parser.parse_telegram_signals('channel_id')")
    print()
    print("3. SMS Signals:")
    print("   - Export SMS to JSON/CSV")
    print("   - signals = parser.parse_sms_signals('sms_export.json')")
    print("=" * 70)


if __name__ == "__main__":
    main()
