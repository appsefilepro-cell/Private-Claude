#!/usr/bin/env python3
"""
Zapier Trading Notifier
Sends trading notifications and logs to Zapier webhooks for Google Sheets, Slack, Email
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZapierTradingNotifier:
    """Handles all Zapier webhook integrations for trading notifications"""

    def __init__(self, config_path: str = '/home/user/Private-Claude/MT5_AND_OKX_TRADING_CONFIG.json'):
        self.config_path = config_path
        self.webhooks = {}
        self.load_config()

    def load_config(self):
        """Load Zapier webhook configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            # Get webhook URLs
            zapier_config = config.get('zapier_integration', {})

            self.webhooks = {
                'mt5': zapier_config.get('metatrader_zapier_integration', {}).get('webhook_url'),
                'okx': zapier_config.get('okx_zapier_integration', {}).get('webhook_url')
            }

            logger.info("Zapier configuration loaded")

        except Exception as e:
            logger.error(f"Failed to load Zapier config: {e}")

    def send_webhook(self, webhook_url: str, data: Dict, retry_count: int = 3) -> bool:
        """Send data to Zapier webhook with retry logic"""
        if not webhook_url or webhook_url == "https://hooks.zapier.com/hooks/catch/YOUR_WEBHOOK_ID/mt5trades":
            logger.warning("Webhook URL not configured - skipping notification")
            return False

        for attempt in range(retry_count):
            try:
                response = requests.post(
                    webhook_url,
                    json=data,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    logger.info(f"✓ Sent to Zapier: {data.get('event_type', 'unknown')}")
                    return True
                else:
                    logger.warning(f"Zapier webhook returned status {response.status_code}")

            except requests.exceptions.Timeout:
                logger.warning(f"Zapier webhook timeout (attempt {attempt + 1}/{retry_count})")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error sending to Zapier: {e}")

        return False

    def notify_trade_executed(self, trade_data: Dict, account_type: str = 'MT5'):
        """Notify when a trade is executed"""
        webhook_url = self.webhooks.get(account_type.lower())

        payload = {
            'event_type': 'trade_executed',
            'account_type': account_type,
            'timestamp': datetime.now().isoformat(),
            'trade': {
                'symbol': trade_data.get('symbol'),
                'type': trade_data.get('type', trade_data.get('side')),
                'volume': trade_data.get('volume', trade_data.get('amount')),
                'price': trade_data.get('price'),
                'account': trade_data.get('account', trade_data.get('account_number')),
                'order_id': trade_data.get('order_id'),
                'sl': trade_data.get('sl'),
                'tp': trade_data.get('tp')
            },
            'notification_type': 'slack_email_sheets',
            'priority': 'normal'
        }

        return self.send_webhook(webhook_url, payload)

    def notify_position_closed(self, close_data: Dict, account_type: str = 'MT5'):
        """Notify when a position is closed"""
        webhook_url = self.webhooks.get(account_type.lower())

        is_winner = close_data.get('profit', 0) > 0

        payload = {
            'event_type': 'position_closed',
            'account_type': account_type,
            'timestamp': datetime.now().isoformat(),
            'position': {
                'symbol': close_data.get('symbol'),
                'ticket': close_data.get('ticket'),
                'profit': close_data.get('profit'),
                'pnl': close_data.get('pnl', close_data.get('profit')),
                'account': close_data.get('account'),
                'result': 'WIN' if is_winner else 'LOSS'
            },
            'notification_type': 'slack_email_sheets',
            'priority': 'high' if abs(close_data.get('profit', 0)) > 100 else 'normal',
            'ml_analyze': is_winner  # Trigger ML analysis for winning trades
        }

        return self.send_webhook(webhook_url, payload)

    def notify_hourly_summary(self, summary_data: Dict):
        """Send hourly trading summary"""
        # Send to both MT5 and OKX webhooks
        payload = {
            'event_type': 'hourly_summary',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_trades': summary_data.get('total_trades', 0),
                'mt5_trades': summary_data.get('mt5_trades', 0),
                'okx_trades': summary_data.get('okx_trades', 0),
                'total_profit': summary_data.get('total_profit', 0),
                'mt5_profit': summary_data.get('mt5_profit', 0),
                'okx_profit': summary_data.get('okx_profit', 0),
                'win_rate': summary_data.get('win_rate', 0),
                'open_positions': summary_data.get('open_positions', 0),
                'account_balances': summary_data.get('account_balances', {})
            },
            'notification_type': 'slack_email',
            'priority': 'normal'
        }

        # Send to both webhooks
        results = []
        for account_type in ['mt5', 'okx']:
            webhook_url = self.webhooks.get(account_type)
            if webhook_url:
                results.append(self.send_webhook(webhook_url, payload))

        return any(results)

    def notify_daily_report(self, report_data: Dict):
        """Send daily trading report"""
        payload = {
            'event_type': 'daily_report',
            'timestamp': datetime.now().isoformat(),
            'report': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_trades': report_data.get('total_trades', 0),
                'winning_trades': report_data.get('winning_trades', 0),
                'losing_trades': report_data.get('losing_trades', 0),
                'win_rate': report_data.get('win_rate', 0),
                'total_profit': report_data.get('total_profit', 0),
                'best_trade': report_data.get('best_trade', 0),
                'worst_trade': report_data.get('worst_trade', 0),
                'best_symbol': report_data.get('best_symbol', 'N/A'),
                'total_mt5_accounts': 3,
                'okx_account_status': 'active',
                'ml_patterns_learned': report_data.get('ml_patterns_learned', 0)
            },
            'notification_type': 'email_detailed',
            'priority': 'high'
        }

        # Send to all webhooks
        results = []
        for account_type in ['mt5', 'okx']:
            webhook_url = self.webhooks.get(account_type)
            if webhook_url:
                results.append(self.send_webhook(webhook_url, payload))

        return any(results)

    def notify_ml_pattern_detected(self, pattern_data: Dict):
        """Notify when ML detects a winning pattern"""
        payload = {
            'event_type': 'ml_pattern_detected',
            'timestamp': datetime.now().isoformat(),
            'pattern': {
                'symbol': pattern_data.get('symbol'),
                'pattern_type': pattern_data.get('pattern_type'),
                'confidence': pattern_data.get('confidence'),
                'success_rate': pattern_data.get('success_rate'),
                'avg_profit': pattern_data.get('avg_profit'),
                'total_occurrences': pattern_data.get('total_occurrences'),
                'recommendation': pattern_data.get('recommendation')
            },
            'notification_type': 'slack',
            'priority': 'high',
            'channel': '#ai-communication'
        }

        # Send to both webhooks
        results = []
        for account_type in ['mt5', 'okx']:
            webhook_url = self.webhooks.get(account_type)
            if webhook_url:
                results.append(self.send_webhook(webhook_url, payload))

        return any(results)

    def notify_risk_alert(self, alert_data: Dict):
        """Send risk management alerts"""
        payload = {
            'event_type': 'risk_alert',
            'timestamp': datetime.now().isoformat(),
            'alert': {
                'type': alert_data.get('alert_type'),
                'severity': alert_data.get('severity', 'warning'),
                'message': alert_data.get('message'),
                'account': alert_data.get('account'),
                'current_value': alert_data.get('current_value'),
                'threshold': alert_data.get('threshold'),
                'action_required': alert_data.get('action_required')
            },
            'notification_type': 'email_slack_urgent',
            'priority': 'urgent'
        }

        # Send to all webhooks immediately
        results = []
        for account_type in ['mt5', 'okx']:
            webhook_url = self.webhooks.get(account_type)
            if webhook_url:
                results.append(self.send_webhook(webhook_url, payload))

        return any(results)

    def notify_system_status(self, status_data: Dict):
        """Send system status updates"""
        payload = {
            'event_type': 'system_status',
            'timestamp': datetime.now().isoformat(),
            'status': {
                'mt5_account_1': status_data.get('mt5_1', 'unknown'),
                'mt5_account_2': status_data.get('mt5_2', 'unknown'),
                'mt5_account_3': status_data.get('mt5_3', 'unknown'),
                'okx_account': status_data.get('okx', 'unknown'),
                'ml_analyzer': status_data.get('ml_analyzer', 'unknown'),
                'total_uptime_hours': status_data.get('uptime_hours', 0),
                'errors_24h': status_data.get('errors_24h', 0)
            },
            'notification_type': 'slack',
            'priority': 'low'
        }

        # Send to MT5 webhook
        webhook_url = self.webhooks.get('mt5')
        if webhook_url:
            return self.send_webhook(webhook_url, payload)

        return False

    def log_to_google_sheets(self, trade_data: Dict, sheet_type: str = 'trades'):
        """Log trade data to Google Sheets via Zapier"""
        # Zapier will automatically route to Google Sheets
        # The webhook handlers in Zapier are configured to update specific sheets

        webhook_url = self.webhooks.get(trade_data.get('account_type', 'mt5').lower())

        payload = {
            'event_type': f'log_to_sheets_{sheet_type}',
            'timestamp': datetime.now().isoformat(),
            'sheet_type': sheet_type,
            'data': trade_data
        }

        return self.send_webhook(webhook_url, payload)


def main():
    """Test Zapier notifications"""
    logger.info("Testing Zapier Trading Notifier...")

    notifier = ZapierTradingNotifier()

    # Test trade executed notification
    test_trade = {
        'symbol': 'EURUSD',
        'type': 'BUY',
        'volume': 0.01,
        'price': 1.1234,
        'account_number': 1,
        'order_id': 'TEST123',
        'sl': 1.1200,
        'tp': 1.1300
    }

    notifier.notify_trade_executed(test_trade, 'MT5')

    # Test position closed notification
    test_close = {
        'symbol': 'BTCUSD',
        'ticket': 'TEST456',
        'profit': 25.50,
        'account': 'OKX'
    }

    notifier.notify_position_closed(test_close, 'OKX')

    # Test hourly summary
    test_summary = {
        'total_trades': 42,
        'mt5_trades': 30,
        'okx_trades': 12,
        'total_profit': 127.50,
        'win_rate': 65.0
    }

    notifier.notify_hourly_summary(test_summary)

    logger.info("Zapier notifications sent!")


if __name__ == "__main__":
    main()
