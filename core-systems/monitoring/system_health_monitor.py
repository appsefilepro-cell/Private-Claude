"""
System Health Monitor for Agent 5.0
====================================

Real-time health monitoring for all services including:
- Resource usage monitoring (CPU, memory, disk)
- API endpoint health checks
- Database connection health
- External dependency monitoring
- Automated multi-channel alerts

Author: Agent 5.0 System
Version: 1.0.0
"""

import time
import asyncio
import logging
import json
import threading
import psutil
import socket
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertChannel(Enum):
    """Alert notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"
    LOG = "log"


class ResourceMonitor:
    """
    Monitors system resource usage (CPU, memory, disk, network).
    """

    def __init__(self,
                 cpu_warning_threshold: float = 70.0,
                 cpu_critical_threshold: float = 90.0,
                 memory_warning_threshold: float = 75.0,
                 memory_critical_threshold: float = 90.0,
                 disk_warning_threshold: float = 80.0,
                 disk_critical_threshold: float = 95.0):
        self.cpu_warning = cpu_warning_threshold
        self.cpu_critical = cpu_critical_threshold
        self.memory_warning = memory_warning_threshold
        self.memory_critical = memory_critical_threshold
        self.disk_warning = disk_warning_threshold
        self.disk_critical = disk_critical_threshold

        self.history = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'disk': deque(maxlen=100)
        }

    def get_cpu_usage(self) -> Dict[str, Any]:
        """Get CPU usage statistics."""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        status = HealthStatus.HEALTHY
        if cpu_percent >= self.cpu_critical:
            status = HealthStatus.CRITICAL
        elif cpu_percent >= self.cpu_warning:
            status = HealthStatus.WARNING

        result = {
            'percent': cpu_percent,
            'count': cpu_count,
            'frequency_mhz': cpu_freq.current if cpu_freq else None,
            'status': status.value,
            'timestamp': datetime.now().isoformat()
        }

        self.history['cpu'].append(result)
        return result

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        memory = psutil.virtual_memory()

        status = HealthStatus.HEALTHY
        if memory.percent >= self.memory_critical:
            status = HealthStatus.CRITICAL
        elif memory.percent >= self.memory_warning:
            status = HealthStatus.WARNING

        result = {
            'total_gb': round(memory.total / (1024 ** 3), 2),
            'available_gb': round(memory.available / (1024 ** 3), 2),
            'used_gb': round(memory.used / (1024 ** 3), 2),
            'percent': memory.percent,
            'status': status.value,
            'timestamp': datetime.now().isoformat()
        }

        self.history['memory'].append(result)
        return result

    def get_disk_usage(self, path: str = '/') -> Dict[str, Any]:
        """Get disk usage statistics."""
        try:
            disk = psutil.disk_usage(path)

            status = HealthStatus.HEALTHY
            if disk.percent >= self.disk_critical:
                status = HealthStatus.CRITICAL
            elif disk.percent >= self.disk_warning:
                status = HealthStatus.WARNING

            result = {
                'path': path,
                'total_gb': round(disk.total / (1024 ** 3), 2),
                'used_gb': round(disk.used / (1024 ** 3), 2),
                'free_gb': round(disk.free / (1024 ** 3), 2),
                'percent': disk.percent,
                'status': status.value,
                'timestamp': datetime.now().isoformat()
            }

            self.history['disk'].append(result)
            return result
        except Exception as e:
            logger.error(f"Error getting disk usage for {path}: {e}")
            return {
                'path': path,
                'error': str(e),
                'status': HealthStatus.UNKNOWN.value,
                'timestamp': datetime.now().isoformat()
            }

    def get_network_stats(self) -> Dict[str, Any]:
        """Get network I/O statistics."""
        try:
            net_io = psutil.net_io_counters()

            result = {
                'bytes_sent_mb': round(net_io.bytes_sent / (1024 ** 2), 2),
                'bytes_recv_mb': round(net_io.bytes_recv / (1024 ** 2), 2),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'drops_in': net_io.dropin,
                'drops_out': net_io.dropout,
                'timestamp': datetime.now().isoformat()
            }

            return result
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

    def get_full_report(self) -> Dict[str, Any]:
        """Get comprehensive resource usage report."""
        return {
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage(),
            'network': self.get_network_stats()
        }


class EndpointHealthChecker:
    """
    Monitors health of API endpoints and services.
    """

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.endpoints = {}
        self.check_history = defaultdict(lambda: deque(maxlen=50))

    def register_endpoint(self, name: str, url: str, method: str = 'GET',
                         headers: Optional[Dict] = None,
                         expected_status: int = 200,
                         check_interval: int = 60) -> None:
        """Register an endpoint for health monitoring."""
        self.endpoints[name] = {
            'url': url,
            'method': method,
            'headers': headers or {},
            'expected_status': expected_status,
            'check_interval': check_interval,
            'last_check': None
        }
        logger.info(f"Registered endpoint '{name}' for health monitoring")

    def check_endpoint(self, name: str) -> Dict[str, Any]:
        """Check health of a specific endpoint."""
        if name not in self.endpoints:
            return {
                'name': name,
                'status': HealthStatus.UNKNOWN.value,
                'error': 'Endpoint not registered',
                'timestamp': datetime.now().isoformat()
            }

        endpoint = self.endpoints[name]
        start_time = time.time()

        try:
            response = requests.request(
                method=endpoint['method'],
                url=endpoint['url'],
                headers=endpoint['headers'],
                timeout=self.timeout
            )

            response_time = (time.time() - start_time) * 1000  # Convert to ms

            is_healthy = response.status_code == endpoint['expected_status']
            status = HealthStatus.HEALTHY if is_healthy else HealthStatus.WARNING

            result = {
                'name': name,
                'url': endpoint['url'],
                'status': status.value,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'is_healthy': is_healthy,
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.Timeout:
            result = {
                'name': name,
                'url': endpoint['url'],
                'status': HealthStatus.CRITICAL.value,
                'error': 'Timeout',
                'is_healthy': False,
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.ConnectionError as e:
            result = {
                'name': name,
                'url': endpoint['url'],
                'status': HealthStatus.CRITICAL.value,
                'error': f'Connection error: {str(e)[:100]}',
                'is_healthy': False,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            result = {
                'name': name,
                'url': endpoint['url'],
                'status': HealthStatus.CRITICAL.value,
                'error': str(e)[:100],
                'is_healthy': False,
                'timestamp': datetime.now().isoformat()
            }

        self.endpoints[name]['last_check'] = time.time()
        self.check_history[name].append(result)

        return result

    def check_all_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all registered endpoints."""
        results = {}
        for name in self.endpoints:
            results[name] = self.check_endpoint(name)
        return results

    def get_endpoint_uptime(self, name: str) -> Dict[str, Any]:
        """Calculate uptime statistics for an endpoint."""
        if name not in self.check_history or not self.check_history[name]:
            return {'error': 'No check history available'}

        history = list(self.check_history[name])
        total_checks = len(history)
        successful_checks = sum(1 for check in history if check.get('is_healthy', False))

        uptime_percentage = (successful_checks / total_checks * 100) if total_checks > 0 else 0

        # Calculate average response time for successful checks
        response_times = [
            check.get('response_time_ms', 0)
            for check in history
            if check.get('is_healthy', False) and 'response_time_ms' in check
        ]

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            'name': name,
            'total_checks': total_checks,
            'successful_checks': successful_checks,
            'failed_checks': total_checks - successful_checks,
            'uptime_percentage': round(uptime_percentage, 2),
            'avg_response_time_ms': round(avg_response_time, 2)
        }


class DatabaseHealthChecker:
    """
    Monitors database connection health and performance.
    """

    def __init__(self):
        self.databases = {}
        self.check_history = defaultdict(lambda: deque(maxlen=50))

    def register_database(self, name: str, connection_func: Callable,
                         health_check_query: str = "SELECT 1") -> None:
        """
        Register a database for health monitoring.

        Args:
            name: Database identifier
            connection_func: Function that returns a database connection
            health_check_query: Query to execute for health check
        """
        self.databases[name] = {
            'connection_func': connection_func,
            'health_check_query': health_check_query,
            'last_check': None
        }
        logger.info(f"Registered database '{name}' for health monitoring")

    def check_database(self, name: str) -> Dict[str, Any]:
        """Check health of a specific database."""
        if name not in self.databases:
            return {
                'name': name,
                'status': HealthStatus.UNKNOWN.value,
                'error': 'Database not registered',
                'timestamp': datetime.now().isoformat()
            }

        db_config = self.databases[name]
        start_time = time.time()

        try:
            # Get connection
            connection = db_config['connection_func']()

            # Execute health check query
            cursor = connection.cursor()
            cursor.execute(db_config['health_check_query'])
            cursor.fetchone()
            cursor.close()

            query_time = (time.time() - start_time) * 1000  # ms

            # Close connection
            if hasattr(connection, 'close'):
                connection.close()

            result = {
                'name': name,
                'status': HealthStatus.HEALTHY.value,
                'query_time_ms': round(query_time, 2),
                'is_healthy': True,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            result = {
                'name': name,
                'status': HealthStatus.CRITICAL.value,
                'error': str(e)[:200],
                'is_healthy': False,
                'timestamp': datetime.now().isoformat()
            }

        self.databases[name]['last_check'] = time.time()
        self.check_history[name].append(result)

        return result

    def check_all_databases(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all registered databases."""
        results = {}
        for name in self.databases:
            results[name] = self.check_database(name)
        return results


class AlertManager:
    """
    Manages health alerts and notifications across multiple channels.
    """

    def __init__(self):
        self.channels = {}
        self.alert_history = deque(maxlen=1000)
        self.alert_throttle = {}  # Prevent alert spam
        self.throttle_period = 300  # 5 minutes

    def register_channel(self, channel: AlertChannel, handler: Callable) -> None:
        """
        Register an alert channel.

        Args:
            channel: Alert channel type
            handler: Function to handle alert (receives alert dict)
        """
        self.channels[channel] = handler
        logger.info(f"Registered alert channel: {channel.value}")

    def send_alert(self, severity: HealthStatus, title: str, message: str,
                   context: Optional[Dict[str, Any]] = None,
                   channels: Optional[List[AlertChannel]] = None) -> bool:
        """
        Send an alert through specified channels.

        Args:
            severity: Alert severity level
            title: Alert title
            message: Alert message
            context: Additional context data
            channels: List of channels to use (None = all channels)

        Returns:
            True if alert was sent, False if throttled
        """
        # Check throttle
        alert_key = f"{severity.value}:{title}"
        current_time = time.time()

        if alert_key in self.alert_throttle:
            last_sent = self.alert_throttle[alert_key]
            if current_time - last_sent < self.throttle_period:
                logger.debug(f"Alert throttled: {alert_key}")
                return False

        # Create alert
        alert = {
            'severity': severity.value,
            'title': title,
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }

        # Send to channels
        channels_to_use = channels or list(self.channels.keys())
        sent_count = 0

        for channel in channels_to_use:
            if channel in self.channels:
                try:
                    self.channels[channel](alert)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending alert to {channel.value}: {e}")

        # Record alert
        self.alert_history.append(alert)
        self.alert_throttle[alert_key] = current_time

        logger.info(f"Sent alert '{title}' to {sent_count} channels")
        return True

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alert history."""
        return list(self.alert_history)[-limit:]


class SystemHealthMonitor:
    """
    Main system health monitoring orchestrator.
    Coordinates all health checks and alerting.
    """

    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.endpoint_checker = EndpointHealthChecker()
        self.database_checker = DatabaseHealthChecker()
        self.alert_manager = AlertManager()

        self.monitoring_active = False
        self.monitoring_thread = None
        self.check_interval = 30  # seconds

        # Register default log alert channel
        self.alert_manager.register_channel(
            AlertChannel.LOG,
            self._log_alert_handler
        )

    def _log_alert_handler(self, alert: Dict[str, Any]) -> None:
        """Default alert handler that logs to console."""
        log_level = {
            'healthy': logging.INFO,
            'warning': logging.WARNING,
            'critical': logging.ERROR,
            'unknown': logging.WARNING
        }.get(alert['severity'], logging.INFO)

        logger.log(
            log_level,
            f"ALERT [{alert['severity'].upper()}] {alert['title']}: {alert['message']}"
        )

    def register_endpoint(self, name: str, url: str, **kwargs) -> None:
        """Register an endpoint for monitoring."""
        self.endpoint_checker.register_endpoint(name, url, **kwargs)

    def register_database(self, name: str, connection_func: Callable, **kwargs) -> None:
        """Register a database for monitoring."""
        self.database_checker.register_database(name, connection_func, **kwargs)

    def register_alert_channel(self, channel: AlertChannel, handler: Callable) -> None:
        """Register an alert channel."""
        self.alert_manager.register_channel(channel, handler)

    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'resources': self.resource_monitor.get_full_report(),
            'endpoints': self.endpoint_checker.check_all_endpoints(),
            'databases': self.database_checker.check_all_databases()
        }

        # Determine overall health status
        overall_status = self._determine_overall_status(health_report)
        health_report['overall_status'] = overall_status.value

        # Check for alerts
        self._check_and_send_alerts(health_report)

        return health_report

    def _determine_overall_status(self, health_report: Dict[str, Any]) -> HealthStatus:
        """Determine overall system health status."""
        # Check resources
        resource_statuses = [
            health_report['resources']['cpu']['status'],
            health_report['resources']['memory']['status'],
            health_report['resources']['disk']['status']
        ]

        # Check endpoints
        endpoint_statuses = [
            check['status']
            for check in health_report['endpoints'].values()
        ]

        # Check databases
        database_statuses = [
            check['status']
            for check in health_report['databases'].values()
        ]

        all_statuses = resource_statuses + endpoint_statuses + database_statuses

        # Critical if any component is critical
        if HealthStatus.CRITICAL.value in all_statuses:
            return HealthStatus.CRITICAL

        # Warning if any component is warning
        if HealthStatus.WARNING.value in all_statuses:
            return HealthStatus.WARNING

        # Healthy otherwise
        return HealthStatus.HEALTHY

    def _check_and_send_alerts(self, health_report: Dict[str, Any]) -> None:
        """Check health report and send alerts if needed."""
        # Check resource alerts
        cpu = health_report['resources']['cpu']
        if cpu['status'] == HealthStatus.CRITICAL.value:
            self.alert_manager.send_alert(
                HealthStatus.CRITICAL,
                "Critical CPU Usage",
                f"CPU usage at {cpu['percent']}%",
                context={'cpu': cpu}
            )

        memory = health_report['resources']['memory']
        if memory['status'] == HealthStatus.CRITICAL.value:
            self.alert_manager.send_alert(
                HealthStatus.CRITICAL,
                "Critical Memory Usage",
                f"Memory usage at {memory['percent']}%",
                context={'memory': memory}
            )

        # Check endpoint alerts
        for name, check in health_report['endpoints'].items():
            if not check.get('is_healthy', False):
                self.alert_manager.send_alert(
                    HealthStatus.CRITICAL,
                    f"Endpoint Down: {name}",
                    f"Endpoint {name} is not responding",
                    context={'endpoint': check}
                )

        # Check database alerts
        for name, check in health_report['databases'].items():
            if not check.get('is_healthy', False):
                self.alert_manager.send_alert(
                    HealthStatus.CRITICAL,
                    f"Database Unavailable: {name}",
                    f"Database {name} health check failed",
                    context={'database': check}
                )

    def start_monitoring(self, interval: int = 30) -> None:
        """Start continuous health monitoring."""
        self.check_interval = interval
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info(f"Health monitoring started with {interval}s interval")

    def stop_monitoring(self) -> None:
        """Stop continuous health monitoring."""
        self.monitoring_active = False
        logger.info("Health monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        while self.monitoring_active:
            try:
                self.perform_health_check()
            except Exception as e:
                logger.error(f"Error during health check: {e}")

            time.sleep(self.check_interval)


# Global instance
health_monitor = SystemHealthMonitor()


if __name__ == "__main__":
    # Example usage and testing
    print("System Health Monitor - Example Usage")
    print("=" * 50)

    # Test resource monitoring
    print("\n1. Resource Monitoring:")
    resources = health_monitor.resource_monitor.get_full_report()
    print(json.dumps(resources, indent=2))

    # Register and test endpoint
    print("\n2. Endpoint Health Check:")
    health_monitor.register_endpoint(
        'google',
        'https://www.google.com',
        method='GET',
        expected_status=200
    )
    endpoint_result = health_monitor.endpoint_checker.check_endpoint('google')
    print(json.dumps(endpoint_result, indent=2))

    # Perform full health check
    print("\n3. Full Health Check:")
    full_report = health_monitor.perform_health_check()
    print(f"Overall Status: {full_report['overall_status']}")

    print("\nAll tests completed successfully!")
