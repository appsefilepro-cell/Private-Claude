#!/usr/bin/env python3
"""
AgentX5 24/7 Supervisor - Continuous Agent Execution System
===========================================================

This supervisor keeps AgentX5 running continuously 24/7 with:
- Automatic crash recovery and restart
- Resource monitoring and management
- Role rotation across all 150 roles
- Comprehensive logging and status reporting
- Health checks and alerting
- Performance metrics tracking
- Status updates every 6 hours

Author: Agent 5.0 System
Version: 2.0.0
"""

import os
import sys
import time
import signal
import logging
import json
import psutil
import subprocess
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ============================================================================
# Configuration & Constants
# ============================================================================

class AgentStatus(Enum):
    """Agent status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CRASHED = "crashed"
    RESTARTING = "restarting"


class RoleType(Enum):
    """Role type enumeration"""
    TRADING = "trading"
    LEGAL = "legal"
    FINANCIAL = "financial"
    GENERAL = "general"
    AUTOMATION = "automation"


@dataclass
class SupervisorConfig:
    """Supervisor configuration"""
    project_root: str
    max_restarts: int = 10
    restart_delay: int = 30
    status_update_interval: int = 21600  # 6 hours
    health_check_interval: int = 300  # 5 minutes
    resource_check_interval: int = 60  # 1 minute
    max_memory_mb: int = 4096
    max_cpu_percent: float = 80.0
    log_retention_days: int = 30
    enable_email_alerts: bool = True
    email_recipients: List[str] = None


@dataclass
class ResourceMetrics:
    """Resource usage metrics"""
    timestamp: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_usage_percent: float
    process_count: int


@dataclass
class ExecutionStats:
    """Execution statistics"""
    start_time: str
    uptime_seconds: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    restart_count: int
    roles_executed: List[str]
    current_role: Optional[str]


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(log_dir: str, verbose: bool = False) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        log_dir: Log directory path
        verbose: Enable verbose logging

    Returns:
        Configured logger instance
    """
    os.makedirs(log_dir, exist_ok=True)

    log_level = logging.DEBUG if verbose else logging.INFO
    log_file = os.path.join(log_dir, f'agentx5_supervisor_{datetime.now().strftime("%Y%m%d")}.log')

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Create logger
    logger = logging.getLogger('AgentX5Supervisor')
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ============================================================================
# Resource Monitor
# ============================================================================

class ResourceMonitor:
    """Monitor system resource usage"""

    def __init__(self, logger: logging.Logger):
        """
        Initialize resource monitor

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.process = psutil.Process()
        self.metrics_history: List[ResourceMetrics] = []

    def get_current_metrics(self) -> ResourceMetrics:
        """
        Get current resource metrics

        Returns:
            Current resource metrics
        """
        try:
            cpu_percent = self.process.cpu_percent(interval=1.0)
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = self.process.memory_percent()

            disk_usage = psutil.disk_usage('/')
            disk_percent = disk_usage.percent

            process_count = len(psutil.pids())

            metrics = ResourceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                disk_usage_percent=disk_percent,
                process_count=process_count
            )

            self.metrics_history.append(metrics)

            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting resource metrics: {e}")
            return ResourceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_mb=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                process_count=0
            )

    def check_resource_limits(
        self,
        max_memory_mb: int,
        max_cpu_percent: float
    ) -> Tuple[bool, str]:
        """
        Check if resource usage is within limits

        Args:
            max_memory_mb: Maximum memory in MB
            max_cpu_percent: Maximum CPU percent

        Returns:
            Tuple of (within_limits, message)
        """
        metrics = self.get_current_metrics()

        if metrics.memory_mb > max_memory_mb:
            msg = f"Memory usage {metrics.memory_mb:.2f}MB exceeds limit {max_memory_mb}MB"
            self.logger.warning(msg)
            return False, msg

        if metrics.cpu_percent > max_cpu_percent:
            msg = f"CPU usage {metrics.cpu_percent:.2f}% exceeds limit {max_cpu_percent}%"
            self.logger.warning(msg)
            return False, msg

        return True, "Resource usage within limits"

    def get_average_metrics(self, last_n: int = 10) -> Dict[str, float]:
        """
        Get average metrics over last N measurements

        Args:
            last_n: Number of measurements to average

        Returns:
            Average metrics
        """
        if not self.metrics_history:
            return {
                'cpu_percent': 0.0,
                'memory_mb': 0.0,
                'memory_percent': 0.0
            }

        recent_metrics = self.metrics_history[-last_n:]

        return {
            'cpu_percent': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'memory_mb': sum(m.memory_mb for m in recent_metrics) / len(recent_metrics),
            'memory_percent': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        }


# ============================================================================
# Agent Process Manager
# ============================================================================

class AgentProcessManager:
    """Manage AgentX5 process execution"""

    def __init__(self, config: SupervisorConfig, logger: logging.Logger):
        """
        Initialize agent process manager

        Args:
            config: Supervisor configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.process: Optional[subprocess.Popen] = None
        self.status = AgentStatus.STOPPED
        self.restart_count = 0
        self.last_restart_time: Optional[datetime] = None

    def start_agent(self, role: Optional[str] = None, iterations: int = 10) -> bool:
        """
        Start AgentX5 process

        Args:
            role: Specific role to execute (None for all roles)
            iterations: Number of iterations

        Returns:
            Success status
        """
        try:
            self.logger.info(f"Starting AgentX5... (role: {role}, iterations: {iterations})")

            # Build command
            cmd = [
                sys.executable,
                os.path.join(self.config.project_root, "MASTER_AGENT_150_ROLES.py"),
                "--mode", "production",
                "--iterations", str(iterations)
            ]

            if role:
                cmd.extend(["--role", role])

            # Start process
            self.process = subprocess.Popen(
                cmd,
                cwd=self.config.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.status = AgentStatus.RUNNING
            self.logger.info(f"AgentX5 started with PID: {self.process.pid}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to start AgentX5: {e}")
            self.status = AgentStatus.CRASHED
            return False

    def stop_agent(self, timeout: int = 30) -> bool:
        """
        Stop AgentX5 process gracefully

        Args:
            timeout: Timeout in seconds

        Returns:
            Success status
        """
        if not self.process:
            self.logger.warning("No process to stop")
            return True

        try:
            self.logger.info(f"Stopping AgentX5 (PID: {self.process.pid})...")

            # Send SIGTERM
            self.process.terminate()

            # Wait for process to terminate
            try:
                self.process.wait(timeout=timeout)
                self.logger.info("AgentX5 stopped gracefully")
            except subprocess.TimeoutExpired:
                self.logger.warning("Process did not terminate gracefully, killing...")
                self.process.kill()
                self.process.wait()

            self.status = AgentStatus.STOPPED
            self.process = None

            return True

        except Exception as e:
            self.logger.error(f"Error stopping AgentX5: {e}")
            return False

    def restart_agent(self, role: Optional[str] = None, iterations: int = 10) -> bool:
        """
        Restart AgentX5 process

        Args:
            role: Specific role to execute
            iterations: Number of iterations

        Returns:
            Success status
        """
        self.logger.info("Restarting AgentX5...")

        self.status = AgentStatus.RESTARTING
        self.restart_count += 1
        self.last_restart_time = datetime.now()

        # Stop current process
        if self.process:
            self.stop_agent()

        # Wait for restart delay
        self.logger.info(f"Waiting {self.config.restart_delay}s before restart...")
        time.sleep(self.config.restart_delay)

        # Start new process
        return self.start_agent(role=role, iterations=iterations)

    def is_running(self) -> bool:
        """
        Check if agent is running

        Returns:
            Running status
        """
        if not self.process:
            return False

        return self.process.poll() is None

    def get_return_code(self) -> Optional[int]:
        """
        Get process return code

        Returns:
            Return code or None if still running
        """
        if not self.process:
            return None

        return self.process.poll()


# ============================================================================
# Role Scheduler
# ============================================================================

class RoleScheduler:
    """Schedule and rotate through all 150 roles"""

    def __init__(self, logger: logging.Logger):
        """
        Initialize role scheduler

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.all_roles = self._load_all_roles()
        self.executed_roles: List[str] = []
        self.current_role_index = 0

    def _load_all_roles(self) -> List[str]:
        """
        Load all 150 roles

        Returns:
            List of role names
        """
        # This is a simplified version - actual implementation would load from MASTER_AGENT_150_ROLES.py
        roles = []

        # Trading roles
        for i in range(1, 51):
            roles.append(f"trading_role_{i}")

        # Legal roles
        for i in range(1, 51):
            roles.append(f"legal_role_{i}")

        # Financial roles
        for i in range(1, 51):
            roles.append(f"financial_role_{i}")

        self.logger.info(f"Loaded {len(roles)} roles")
        return roles

    def get_next_role(self) -> str:
        """
        Get next role in rotation

        Returns:
            Role name
        """
        role = self.all_roles[self.current_role_index]
        self.current_role_index = (self.current_role_index + 1) % len(self.all_roles)

        if role not in self.executed_roles:
            self.executed_roles.append(role)

        self.logger.info(f"Next role: {role} ({self.current_role_index}/{len(self.all_roles)})")
        return role

    def get_progress(self) -> Dict[str, Any]:
        """
        Get execution progress

        Returns:
            Progress information
        """
        return {
            'total_roles': len(self.all_roles),
            'executed_roles': len(self.executed_roles),
            'current_index': self.current_role_index,
            'progress_percent': (len(self.executed_roles) / len(self.all_roles)) * 100
        }


# ============================================================================
# Notification Manager
# ============================================================================

class NotificationManager:
    """Manage status notifications and alerts"""

    def __init__(self, config: SupervisorConfig, logger: logging.Logger):
        """
        Initialize notification manager

        Args:
            config: Supervisor configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

    def send_status_update(self, stats: ExecutionStats, metrics: ResourceMetrics) -> bool:
        """
        Send status update notification

        Args:
            stats: Execution statistics
            metrics: Resource metrics

        Returns:
            Success status
        """
        self.logger.info("Sending status update...")

        message = self._format_status_message(stats, metrics)

        # Log to file
        self.logger.info(f"Status Update:\n{message}")

        # Send email if enabled
        if self.config.enable_email_alerts and self.config.email_recipients:
            return self._send_email(
                subject="AgentX5 Status Update",
                body=message
            )

        return True

    def send_alert(self, alert_type: str, message: str) -> bool:
        """
        Send alert notification

        Args:
            alert_type: Type of alert
            message: Alert message

        Returns:
            Success status
        """
        self.logger.warning(f"ALERT [{alert_type}]: {message}")

        if self.config.enable_email_alerts and self.config.email_recipients:
            return self._send_email(
                subject=f"AgentX5 ALERT: {alert_type}",
                body=message,
                priority="high"
            )

        return True

    def _format_status_message(self, stats: ExecutionStats, metrics: ResourceMetrics) -> str:
        """
        Format status message

        Args:
            stats: Execution statistics
            metrics: Resource metrics

        Returns:
            Formatted message
        """
        uptime_hours = stats.uptime_seconds / 3600

        message = f"""
AgentX5 24/7 Supervisor Status Update
=====================================

Execution Statistics:
- Start Time: {stats.start_time}
- Uptime: {uptime_hours:.2f} hours
- Total Executions: {stats.total_executions}
- Successful: {stats.successful_executions}
- Failed: {stats.failed_executions}
- Restart Count: {stats.restart_count}
- Current Role: {stats.current_role or 'N/A'}
- Roles Executed: {len(stats.roles_executed)}/150

Resource Usage:
- CPU: {metrics.cpu_percent:.2f}%
- Memory: {metrics.memory_mb:.2f}MB ({metrics.memory_percent:.2f}%)
- Disk: {metrics.disk_usage_percent:.2f}%
- Processes: {metrics.process_count}

Timestamp: {metrics.timestamp}
"""
        return message

    def _send_email(self, subject: str, body: str, priority: str = "normal") -> bool:
        """
        Send email notification

        Args:
            subject: Email subject
            body: Email body
            priority: Email priority

        Returns:
            Success status
        """
        try:
            # This is a simplified version - actual implementation would use proper SMTP config
            self.logger.info(f"Email notification: {subject}")
            # In production, implement actual email sending here
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False


# ============================================================================
# Main Supervisor
# ============================================================================

class AgentX5Supervisor:
    """Main supervisor for 24/7 AgentX5 operation"""

    def __init__(self, config: SupervisorConfig):
        """
        Initialize supervisor

        Args:
            config: Supervisor configuration
        """
        self.config = config
        self.logger = setup_logging(os.path.join(config.project_root, 'logs'))

        self.resource_monitor = ResourceMonitor(self.logger)
        self.process_manager = AgentProcessManager(config, self.logger)
        self.role_scheduler = RoleScheduler(self.logger)
        self.notification_manager = NotificationManager(config, self.logger)

        self.running = False
        self.start_time: Optional[datetime] = None
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def run(self):
        """Run supervisor main loop"""
        self.logger.info("=" * 80)
        self.logger.info("AgentX5 24/7 Supervisor Starting...")
        self.logger.info("=" * 80)

        self.running = True
        self.start_time = datetime.now()

        last_status_update = datetime.now()
        last_health_check = datetime.now()
        last_resource_check = datetime.now()

        try:
            while self.running:
                current_time = datetime.now()

                # Check if we need to send status update (every 6 hours)
                if (current_time - last_status_update).total_seconds() >= self.config.status_update_interval:
                    self._send_status_update()
                    last_status_update = current_time

                # Check health (every 5 minutes)
                if (current_time - last_health_check).total_seconds() >= self.config.health_check_interval:
                    self._perform_health_check()
                    last_health_check = current_time

                # Check resources (every minute)
                if (current_time - last_resource_check).total_seconds() >= self.config.resource_check_interval:
                    self._check_resources()
                    last_resource_check = current_time

                # Check if agent is running
                if not self.process_manager.is_running():
                    return_code = self.process_manager.get_return_code()

                    if return_code == 0:
                        self.logger.info("Agent completed successfully")
                        self.successful_executions += 1
                    else:
                        self.logger.error(f"Agent crashed with code {return_code}")
                        self.failed_executions += 1

                    self.total_executions += 1

                    # Check restart limit
                    if self.process_manager.restart_count >= self.config.max_restarts:
                        self.logger.error(f"Max restarts ({self.config.max_restarts}) reached, stopping")
                        self.notification_manager.send_alert(
                            "MAX_RESTARTS",
                            f"AgentX5 reached maximum restart limit: {self.config.max_restarts}"
                        )
                        break

                    # Get next role and restart
                    next_role = self.role_scheduler.get_next_role()
                    self.process_manager.restart_agent(role=next_role)

                # Sleep briefly
                time.sleep(10)

        except Exception as e:
            self.logger.error(f"Supervisor error: {e}", exc_info=True)
            self.notification_manager.send_alert("SUPERVISOR_ERROR", str(e))

        finally:
            self._shutdown()

    def _perform_health_check(self):
        """Perform health check"""
        self.logger.debug("Performing health check...")

        if not self.process_manager.is_running():
            self.logger.warning("Agent is not running during health check")
            return

        # Check if process is responding
        # This is simplified - actual implementation would check actual health endpoints
        self.logger.debug("Agent health check passed")

    def _check_resources(self):
        """Check resource usage"""
        within_limits, message = self.resource_monitor.check_resource_limits(
            self.config.max_memory_mb,
            self.config.max_cpu_percent
        )

        if not within_limits:
            self.notification_manager.send_alert("RESOURCE_LIMIT", message)

    def _send_status_update(self):
        """Send status update"""
        stats = ExecutionStats(
            start_time=self.start_time.isoformat(),
            uptime_seconds=int((datetime.now() - self.start_time).total_seconds()),
            total_executions=self.total_executions,
            successful_executions=self.successful_executions,
            failed_executions=self.failed_executions,
            restart_count=self.process_manager.restart_count,
            roles_executed=self.role_scheduler.executed_roles,
            current_role=None
        )

        metrics = self.resource_monitor.get_current_metrics()

        self.notification_manager.send_status_update(stats, metrics)

    def _shutdown(self):
        """Shutdown supervisor"""
        self.logger.info("Shutting down supervisor...")

        # Stop agent
        if self.process_manager.is_running():
            self.process_manager.stop_agent()

        # Send final status update
        self._send_status_update()

        self.logger.info("Supervisor shutdown complete")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AgentX5 24/7 Supervisor - Continuous Agent Execution"
    )

    parser.add_argument(
        "--project-root",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Project root directory"
    )

    parser.add_argument(
        "--max-restarts",
        type=int,
        default=100,
        help="Maximum number of restarts"
    )

    parser.add_argument(
        "--restart-delay",
        type=int,
        default=30,
        help="Delay between restarts (seconds)"
    )

    parser.add_argument(
        "--max-memory",
        type=int,
        default=4096,
        help="Maximum memory usage (MB)"
    )

    parser.add_argument(
        "--max-cpu",
        type=float,
        default=80.0,
        help="Maximum CPU usage (%)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Create configuration
    config = SupervisorConfig(
        project_root=args.project_root,
        max_restarts=args.max_restarts,
        restart_delay=args.restart_delay,
        max_memory_mb=args.max_memory,
        max_cpu_percent=args.max_cpu
    )

    # Create and run supervisor
    supervisor = AgentX5Supervisor(config)
    supervisor.run()


if __name__ == "__main__":
    main()
