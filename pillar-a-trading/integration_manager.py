"""
Integration Manager
Handles integrations with Slack, Zapier, Google Sheets, webhooks, and Agent 5.0
Sends alerts, logs trades, and updates external systems
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('IntegrationManager')


class IntegrationManager:
    """
    Manages all external integrations for the trading bot
    """

    def __init__(self, mode: str = "paper", profile: str = "beginner"):
        """
        Initialize integration manager

        Args:
            mode: Trading mode
            profile: Risk profile
        """
        self.mode = mode
        self.profile = profile

        # Load configuration
        self.config = self.load_config()

        # Integration status
        self.integrations_enabled = {
            "slack": self.config.get('alerts', {}).get('slack', {}).get('enabled', False),
            "zapier": self.config.get('integrations', {}).get('zapier', {}).get('enabled', False),
            "google_sheets": self.config.get('integrations', {}).get('google_sheets', {}).get('enabled', False),
            "webhook": self.config.get('alerts', {}).get('webhook', {}).get('enabled', False),
            "agent_5_0": self.config.get('integrations', {}).get('agent_5_0', {}).get('enabled', False)
        }

        logger.info(f"Integration Manager initialized - Mode: {mode}, Profile: {profile}")
        logger.info(f"Enabled integrations: {[k for k, v in self.integrations_enabled.items() if v]}")

    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'trading_bot_24_7_config.json'

            if not config_path.exists():
                logger.warning("Config file not found, using defaults")
                return self.get_default_config()

            with open(config_path, 'r') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "alerts": {
                "slack": {"enabled": False},
                "webhook": {"enabled": False}
            },
            "integrations": {
                "zapier": {"enabled": False},
                "google_sheets": {"enabled": False},
                "agent_5_0": {"enabled": False}
            }
        }

    def send_slack_alert(self,
                        message: str,
                        alert_type: str = "info",
                        include_metrics: bool = False,
                        metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send alert to Slack

        Args:
            message: Alert message
            alert_type: Type of alert (info/success/warning/error)
            include_metrics: Include performance metrics
            metrics: Performance metrics dictionary

        Returns:
            Success status
        """
        if not self.integrations_enabled['slack']:
            logger.debug("Slack integration disabled, skipping alert")
            return False

        try:
            slack_config = self.config.get('alerts', {}).get('slack', {})
            webhook_url = slack_config.get('webhook_url', os.getenv('SLACK_WEBHOOK_URL'))

            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return False

            # Format message based on type
            emoji_map = {
                "info": ":information_source:",
                "success": ":white_check_mark:",
                "warning": ":warning:",
                "error": ":x:",
                "trade": ":chart_with_upwards_trend:",
                "profit": ":moneybag:",
                "loss": ":chart_with_downwards_trend:"
            }

            emoji = emoji_map.get(alert_type, ":robot_face:")

            # Build Slack message
            slack_message = {
                "text": f"{emoji} *Trading Bot Alert*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} Trading Bot Alert"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Mode:* {self.mode.upper()} | *Profile:* {self.profile.capitalize()} | *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }

            # Add metrics if requested
            if include_metrics and metrics:
                metrics_text = self.format_metrics_for_slack(metrics)
                slack_message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": metrics_text
                    }
                })

            # Send to Slack
            # Note: In paper mode, we just log it
            if self.mode == "paper":
                logger.info(f"[PAPER MODE] Would send to Slack: {message}")
                return True
            else:
                response = requests.post(webhook_url, json=slack_message, timeout=10)
                response.raise_for_status()
                logger.info("Slack alert sent successfully")
                return True

        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False

    def format_metrics_for_slack(self, metrics: Dict[str, Any]) -> str:
        """Format performance metrics for Slack"""
        return f"""
*Performance Metrics*
• Total Trades: {metrics.get('total_trades', 0)}
• Win Rate: {metrics.get('win_rate', 0):.2f}%
• Current Capital: ${metrics.get('current_capital', 0):,.2f}
• Net Profit: ${metrics.get('net_profit', 0):,.2f}
• ROI: {metrics.get('roi_percentage', 0):.2f}%
        """.strip()

    def log_trade_to_zapier(self, trade: Dict[str, Any]) -> bool:
        """
        Log trade to Zapier (which can forward to Google Sheets, etc.)

        Args:
            trade: Trade dictionary

        Returns:
            Success status
        """
        if not self.integrations_enabled['zapier']:
            logger.debug("Zapier integration disabled, skipping")
            return False

        try:
            # In paper mode, just log locally
            if self.mode == "paper":
                logger.info(f"[PAPER MODE] Would log to Zapier: Trade #{trade.get('id')}")
                self.log_trade_locally(trade)
                return True

            # For demo/live, would send to actual Zapier webhook
            zapier_webhook = os.getenv('ZAPIER_WEBHOOK_URL')
            if not zapier_webhook:
                logger.warning("Zapier webhook URL not configured")
                return False

            # Prepare trade data
            trade_data = {
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "profile": self.profile,
                "trade_id": trade.get('id'),
                "pair": trade.get('pair'),
                "type": trade.get('type'),
                "entry_price": trade.get('entry_price'),
                "exit_price": trade.get('exit_price'),
                "quantity": trade.get('quantity'),
                "profit_loss": trade.get('profit_loss'),
                "status": trade.get('status')
            }

            response = requests.post(zapier_webhook, json=trade_data, timeout=10)
            response.raise_for_status()
            logger.info("Trade logged to Zapier successfully")
            return True

        except Exception as e:
            logger.error(f"Error logging to Zapier: {e}")
            return False

    def log_trade_locally(self, trade: Dict[str, Any]):
        """Log trade to local CSV file (for paper mode)"""
        try:
            log_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'integrations'
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f'zapier_trades_{self.mode}_{self.profile}.jsonl'

            # Append trade as JSON line
            with open(log_file, 'a') as f:
                trade_log = {
                    "timestamp": datetime.now().isoformat(),
                    "trade": trade
                }
                f.write(json.dumps(trade_log, default=str) + '\n')

        except Exception as e:
            logger.error(f"Error logging trade locally: {e}")

    def update_google_sheets(self, data: Dict[str, Any]) -> bool:
        """
        Update Google Sheets with trading data

        Args:
            data: Data to update

        Returns:
            Success status
        """
        if not self.integrations_enabled['google_sheets']:
            logger.debug("Google Sheets integration disabled, skipping")
            return False

        try:
            # In paper mode, just log
            if self.mode == "paper":
                logger.info(f"[PAPER MODE] Would update Google Sheets")
                return True

            # For demo/live, would use Google Sheets API
            logger.info("Google Sheets update not fully implemented yet")
            return False

        except Exception as e:
            logger.error(f"Error updating Google Sheets: {e}")
            return False

    def trigger_webhook(self,
                       event_type: str,
                       data: Dict[str, Any]) -> bool:
        """
        Trigger external webhook

        Args:
            event_type: Type of event (trade_executed, signal_generated, etc.)
            data: Event data

        Returns:
            Success status
        """
        if not self.integrations_enabled['webhook']:
            logger.debug("Webhook integration disabled, skipping")
            return False

        try:
            webhook_config = self.config.get('alerts', {}).get('webhook', {})
            endpoints = webhook_config.get('endpoints', [])

            if not endpoints:
                logger.debug("No webhook endpoints configured")
                return False

            # In paper mode, just log
            if self.mode == "paper":
                logger.info(f"[PAPER MODE] Would trigger webhook: {event_type}")
                return True

            # For demo/live, send to configured endpoints
            webhook_data = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "mode": self.mode,
                "profile": self.profile,
                "data": data
            }

            success = True
            for endpoint in endpoints:
                try:
                    response = requests.post(endpoint, json=webhook_data, timeout=10)
                    response.raise_for_status()
                    logger.info(f"Webhook triggered successfully: {endpoint}")
                except Exception as e:
                    logger.error(f"Error triggering webhook {endpoint}: {e}")
                    success = False

            return success

        except Exception as e:
            logger.error(f"Error triggering webhooks: {e}")
            return False

    def update_agent_5_0_status(self,
                                status: str,
                                metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update Agent 5.0 system with bot status

        Args:
            status: Bot status
            metrics: Performance metrics

        Returns:
            Success status
        """
        if not self.integrations_enabled['agent_5_0']:
            logger.debug("Agent 5.0 integration disabled, skipping")
            return False

        try:
            # Prepare status update
            status_update = {
                "timestamp": datetime.now().isoformat(),
                "bot_name": "24/7 Trading Bot",
                "mode": self.mode,
                "profile": self.profile,
                "status": status,
                "metrics": metrics or {}
            }

            # In paper mode, save to local file
            if self.mode == "paper":
                logger.info(f"[PAPER MODE] Would update Agent 5.0 status: {status}")
                self.save_agent_status_locally(status_update)
                return True

            # For demo/live, would send to Agent 5.0 API
            agent_endpoint = os.getenv('AGENT_5_0_ENDPOINT')
            if not agent_endpoint:
                logger.debug("Agent 5.0 endpoint not configured")
                return False

            response = requests.post(f"{agent_endpoint}/status", json=status_update, timeout=10)
            response.raise_for_status()
            logger.info("Agent 5.0 status updated successfully")
            return True

        except Exception as e:
            logger.error(f"Error updating Agent 5.0 status: {e}")
            return False

    def save_agent_status_locally(self, status_update: Dict[str, Any]):
        """Save Agent 5.0 status update locally"""
        try:
            log_dir = Path(__file__).parent.parent / 'logs' / 'trading_bot' / 'integrations'
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f'agent_5_0_status_{self.mode}_{self.profile}.jsonl'

            with open(log_file, 'a') as f:
                f.write(json.dumps(status_update, default=str) + '\n')

        except Exception as e:
            logger.error(f"Error saving Agent status locally: {e}")

    def notify_trade_execution(self, trade: Dict[str, Any]) -> bool:
        """
        Send notifications when trade is executed

        Args:
            trade: Trade dictionary

        Returns:
            Success status
        """
        try:
            trade_type = trade.get('type', 'UNKNOWN')
            pair = trade.get('pair', 'UNKNOWN')
            price = trade.get('entry_price', 0)
            quantity = trade.get('quantity', 0)
            position_value = trade.get('position_value', 0)

            message = f"""
*Trade Executed*
• Type: {trade_type}
• Pair: {pair}
• Price: ${price:,.2f}
• Quantity: {quantity:.6f}
• Position Value: ${position_value:,.2f}
            """.strip()

            # Send to Slack
            self.send_slack_alert(message, alert_type="trade")

            # Log to Zapier
            self.log_trade_to_zapier(trade)

            # Trigger webhook
            self.trigger_webhook("trade_executed", trade)

            return True

        except Exception as e:
            logger.error(f"Error notifying trade execution: {e}")
            return False

    def notify_position_closed(self, trade: Dict[str, Any]) -> bool:
        """
        Send notifications when position is closed

        Args:
            trade: Trade dictionary

        Returns:
            Success status
        """
        try:
            pair = trade.get('pair', 'UNKNOWN')
            entry_price = trade.get('entry_price', 0)
            exit_price = trade.get('exit_price', 0)
            profit_loss = trade.get('profit_loss', 0)
            profit_loss_pct = trade.get('profit_loss_pct', 0)
            close_reason = trade.get('close_reason', 'UNKNOWN')

            alert_type = "profit" if profit_loss >= 0 else "loss"

            message = f"""
*Position Closed - {close_reason}*
• Pair: {pair}
• Entry: ${entry_price:,.2f}
• Exit: ${exit_price:,.2f}
• P/L: ${profit_loss:,.2f} ({profit_loss_pct:+.2f}%)
• Reason: {close_reason}
            """.strip()

            # Send to Slack
            self.send_slack_alert(message, alert_type=alert_type)

            # Update trade in Zapier
            self.log_trade_to_zapier(trade)

            # Trigger webhook
            self.trigger_webhook("position_closed", trade)

            return True

        except Exception as e:
            logger.error(f"Error notifying position closed: {e}")
            return False

    def send_performance_update(self, metrics: Dict[str, Any]) -> bool:
        """
        Send performance update

        Args:
            metrics: Performance metrics

        Returns:
            Success status
        """
        try:
            message = "*Performance Update*"

            # Send to Slack with metrics
            self.send_slack_alert(message, alert_type="info", include_metrics=True, metrics=metrics)

            # Update Agent 5.0
            self.update_agent_5_0_status("RUNNING", metrics)

            return True

        except Exception as e:
            logger.error(f"Error sending performance update: {e}")
            return False

    def send_error_alert(self, error_message: str, error_details: Optional[str] = None) -> bool:
        """
        Send error alert

        Args:
            error_message: Error message
            error_details: Additional error details

        Returns:
            Success status
        """
        try:
            message = f"*Error Alert*\n{error_message}"

            if error_details:
                message += f"\n\n```{error_details}```"

            # Send to Slack
            self.send_slack_alert(message, alert_type="error")

            # Update Agent 5.0
            self.update_agent_5_0_status("ERROR", {"error": error_message})

            return True

        except Exception as e:
            logger.error(f"Error sending error alert: {e}")
            return False


def main():
    """Test integration manager"""
    manager = IntegrationManager(mode="paper", profile="beginner")

    # Test Slack alert
    manager.send_slack_alert("Test alert from trading bot", alert_type="info")

    # Test trade notification
    test_trade = {
        "id": 1,
        "pair": "BTC/USD",
        "type": "BUY",
        "entry_price": 50000,
        "quantity": 0.02,
        "position_value": 1000
    }
    manager.notify_trade_execution(test_trade)

    # Test performance update
    test_metrics = {
        "total_trades": 10,
        "win_rate": 60.0,
        "current_capital": 10500,
        "net_profit": 500,
        "roi_percentage": 5.0
    }
    manager.send_performance_update(test_metrics)


if __name__ == "__main__":
    main()
