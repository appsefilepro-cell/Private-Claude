"""
Configuration Manager for E2B Sandbox Integration
Handles loading, validation, and management of configuration settings
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import re


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class E2BConfig:
    """E2B API configuration"""
    api_key: str
    webhook_id: str
    webhook_secret: Optional[str]
    base_url: str


@dataclass
class WebhookServerConfig:
    """Webhook server configuration"""
    host: str
    port: int
    debug: bool
    enable_signature_verification: bool


@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    default_template: str
    default_timeout: int
    default_memory_limit: int
    default_cpu_limit: float
    enable_network: bool
    enable_filesystem: bool
    pool_enabled: bool
    pool_size: int
    auto_cleanup: bool


@dataclass
class GitHubConfig:
    """GitHub integration configuration"""
    token: Optional[str]
    default_branch: str
    auto_deploy_branches: list
    entry_file: str
    default_language: str
    run_tests_before_deploy: bool
    test_command: str
    webhook_events: list


@dataclass
class ZapierConfig:
    """Zapier integration configuration"""
    webhooks: Dict[str, str]
    enabled: bool
    default_level: str
    default_channels: list
    rules: Dict[str, Dict]


class ConfigurationManager:
    """
    Configuration manager for E2B integration
    Loads configuration from YAML/JSON files and environment variables
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = config_path or self._find_default_config()
        self.config_data: Dict[str, Any] = {}
        self._load_config()
        logger.info(f"Configuration loaded from: {self.config_path}")

    def _find_default_config(self) -> str:
        """
        Find default configuration file

        Returns:
            Path to configuration file
        """
        # Try multiple locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "config", "config.yaml"),
            os.path.join(os.path.dirname(__file__), "config", "config.json"),
            os.path.join(os.getcwd(), "config.yaml"),
            os.path.join(os.getcwd(), "config.json"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Return default path even if it doesn't exist yet
        return possible_paths[0]

    def _load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            logger.warning(f"Configuration file not found: {self.config_path}")
            logger.info("Using default configuration")
            self._load_defaults()
            return

        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    self.config_data = yaml.safe_load(f)
                elif self.config_path.endswith('.json'):
                    self.config_data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {self.config_path}")

            # Resolve environment variables
            self._resolve_env_vars()

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._load_defaults()

    def _resolve_env_vars(self):
        """Resolve environment variable references in configuration"""
        def resolve_value(value):
            if isinstance(value, str):
                # Match ${VAR_NAME} or $VAR_NAME pattern
                pattern = r'\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)'
                matches = re.findall(pattern, value)

                for match in matches:
                    var_name = match[0] or match[1]
                    env_value = os.getenv(var_name, '')

                    if match[0]:  # ${VAR} format
                        value = value.replace(f'${{{var_name}}}', env_value)
                    else:  # $VAR format
                        value = value.replace(f'${var_name}', env_value)

                return value

            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}

            elif isinstance(value, list):
                return [resolve_value(item) for item in value]

            return value

        self.config_data = resolve_value(self.config_data)

    def _load_defaults(self):
        """Load default configuration"""
        self.config_data = {
            "e2b": {
                "api_key": os.getenv("E2B_API_KEY", ""),
                "webhook_id": os.getenv("E2B_WEBHOOK_ID", ""),
                "webhook_secret": os.getenv("E2B_WEBHOOK_SECRET"),
                "base_url": "https://api.e2b.dev/v1"
            },
            "webhook_server": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False,
                "enable_signature_verification": True
            },
            "sandbox": {
                "default_template": "base",
                "default_timeout": 300,
                "default_memory_limit": 512,
                "default_cpu_limit": 1.0,
                "enable_network": True,
                "enable_filesystem": True,
                "pool": {
                    "enabled": True,
                    "size": 5,
                    "auto_cleanup": True
                }
            },
            "github": {
                "token": os.getenv("GITHUB_TOKEN"),
                "default_branch": "main",
                "auto_deploy_branches": ["main", "master", "develop"],
                "deployment": {
                    "entry_file": "main.py",
                    "default_language": "python",
                    "run_tests_before_deploy": True,
                    "test_command": "pytest"
                },
                "webhook": {
                    "events": ["push", "pull_request", "deployment"]
                }
            },
            "zapier": {
                "webhooks": {},
                "notifications": {
                    "enabled": True,
                    "default_level": "info",
                    "default_channels": ["email", "slack"],
                    "rules": {}
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/e2b_integration.log",
                "console_output": True
            },
            "features": {
                "enable_webhook_handling": True,
                "enable_github_integration": True,
                "enable_zapier_integration": True,
                "enable_sandbox_pooling": True
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key

        Args:
            key: Dot-separated key path (e.g., "e2b.api_key")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value

        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split('.')
        data = self.config_data

        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value
        logger.debug(f"Set configuration: {key} = {value}")

    def get_e2b_config(self) -> E2BConfig:
        """
        Get E2B configuration

        Returns:
            E2BConfig instance
        """
        return E2BConfig(
            api_key=self.get("e2b.api_key", ""),
            webhook_id=self.get("e2b.webhook_id", ""),
            webhook_secret=self.get("e2b.webhook_secret"),
            base_url=self.get("e2b.base_url", "https://api.e2b.dev/v1")
        )

    def get_webhook_server_config(self) -> WebhookServerConfig:
        """
        Get webhook server configuration

        Returns:
            WebhookServerConfig instance
        """
        return WebhookServerConfig(
            host=self.get("webhook_server.host", "0.0.0.0"),
            port=self.get("webhook_server.port", 5000),
            debug=self.get("webhook_server.debug", False),
            enable_signature_verification=self.get("webhook_server.enable_signature_verification", True)
        )

    def get_sandbox_config(self) -> SandboxConfig:
        """
        Get sandbox configuration

        Returns:
            SandboxConfig instance
        """
        return SandboxConfig(
            default_template=self.get("sandbox.default_template", "base"),
            default_timeout=self.get("sandbox.default_timeout", 300),
            default_memory_limit=self.get("sandbox.default_memory_limit", 512),
            default_cpu_limit=self.get("sandbox.default_cpu_limit", 1.0),
            enable_network=self.get("sandbox.enable_network", True),
            enable_filesystem=self.get("sandbox.enable_filesystem", True),
            pool_enabled=self.get("sandbox.pool.enabled", True),
            pool_size=self.get("sandbox.pool.size", 5),
            auto_cleanup=self.get("sandbox.pool.auto_cleanup", True)
        )

    def get_github_config(self) -> GitHubConfig:
        """
        Get GitHub configuration

        Returns:
            GitHubConfig instance
        """
        return GitHubConfig(
            token=self.get("github.token"),
            default_branch=self.get("github.default_branch", "main"),
            auto_deploy_branches=self.get("github.auto_deploy_branches", ["main"]),
            entry_file=self.get("github.deployment.entry_file", "main.py"),
            default_language=self.get("github.deployment.default_language", "python"),
            run_tests_before_deploy=self.get("github.deployment.run_tests_before_deploy", True),
            test_command=self.get("github.deployment.test_command", "pytest"),
            webhook_events=self.get("github.webhook.events", ["push"])
        )

    def get_zapier_config(self) -> ZapierConfig:
        """
        Get Zapier configuration

        Returns:
            ZapierConfig instance
        """
        return ZapierConfig(
            webhooks=self.get("zapier.webhooks", {}),
            enabled=self.get("zapier.notifications.enabled", True),
            default_level=self.get("zapier.notifications.default_level", "info"),
            default_channels=self.get("zapier.notifications.default_channels", []),
            rules=self.get("zapier.notifications.rules", {})
        )

    def save(self, output_path: Optional[str] = None):
        """
        Save configuration to file

        Args:
            output_path: Output file path (uses original path if not specified)
        """
        output_path = output_path or self.config_path

        try:
            with open(output_path, 'w') as f:
                if output_path.endswith('.yaml') or output_path.endswith('.yml'):
                    yaml.dump(self.config_data, f, default_flow_style=False)
                elif output_path.endswith('.json'):
                    json.dump(self.config_data, f, indent=2)
                else:
                    raise ValueError(f"Unsupported output format: {output_path}")

            logger.info(f"Configuration saved to: {output_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate E2B configuration
        if not self.get("e2b.api_key"):
            errors.append("E2B API key is missing")

        if not self.get("e2b.webhook_id"):
            errors.append("E2B webhook ID is missing")

        # Validate webhook server configuration
        port = self.get("webhook_server.port")
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append(f"Invalid webhook server port: {port}")

        # Validate sandbox configuration
        timeout = self.get("sandbox.default_timeout")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append(f"Invalid sandbox timeout: {timeout}")

        # Validate GitHub configuration (if enabled)
        if self.get("features.enable_github_integration"):
            if not self.get("github.token"):
                errors.append("GitHub token is missing (required when GitHub integration is enabled)")

        is_valid = len(errors) == 0

        if is_valid:
            logger.info("Configuration validation passed")
        else:
            logger.error(f"Configuration validation failed with {len(errors)} errors")

        return is_valid, errors

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary

        Returns:
            Configuration dictionary
        """
        return self.config_data.copy()

    def reload(self):
        """Reload configuration from file"""
        self._load_config()
        logger.info("Configuration reloaded")


# Global configuration instance
_global_config: Optional[ConfigurationManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigurationManager:
    """
    Get global configuration instance

    Args:
        config_path: Path to configuration file (only used on first call)

    Returns:
        ConfigurationManager instance
    """
    global _global_config

    if _global_config is None:
        _global_config = ConfigurationManager(config_path)

    return _global_config


def main():
    """Example usage"""
    # Load configuration
    config = ConfigurationManager()

    # Validate configuration
    is_valid, errors = config.validate()

    if not is_valid:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")

    # Get specific configurations
    e2b_config = config.get_e2b_config()
    print(f"\nE2B Configuration:")
    print(f"  API Key: {e2b_config.api_key[:20]}...")
    print(f"  Webhook ID: {e2b_config.webhook_id}")
    print(f"  Base URL: {e2b_config.base_url}")

    sandbox_config = config.get_sandbox_config()
    print(f"\nSandbox Configuration:")
    print(f"  Template: {sandbox_config.default_template}")
    print(f"  Timeout: {sandbox_config.default_timeout}s")
    print(f"  Pool Size: {sandbox_config.pool_size}")

    # Get individual values
    print(f"\nIndividual Values:")
    print(f"  Webhook Port: {config.get('webhook_server.port')}")
    print(f"  Default Branch: {config.get('github.default_branch')}")


if __name__ == "__main__":
    main()
