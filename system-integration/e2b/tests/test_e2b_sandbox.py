"""
Comprehensive Test Suite for E2B Sandbox Integration
Tests all core functionality of the E2B sandbox client
"""

import os
import sys
import unittest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from e2b_sandbox import (
    E2BSandboxClient,
    Language,
    SandboxStatus,
    ExecutionResult,
    SandboxConfig,
    SandboxPool
)


class TestE2BSandboxClient(unittest.TestCase):
    """Test cases for E2BSandboxClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("E2B_API_KEY", "test_api_key")
        self.client = E2BSandboxClient(self.api_key)

    def tearDown(self):
        """Clean up after tests"""
        self.client.close()

    @patch('requests.Session.post')
    def test_create_sandbox(self, mock_post):
        """Test sandbox creation"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"sandboxId": "test_sandbox_123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Create sandbox
        sandbox_id = self.client.create_sandbox()

        # Assertions
        self.assertIsNotNone(sandbox_id)
        self.assertEqual(sandbox_id, "test_sandbox_123")
        mock_post.assert_called_once()

    @patch('requests.Session.post')
    def test_execute_python_code(self, mock_post):
        """Test Python code execution"""
        # Mock responses
        create_response = Mock()
        create_response.json.return_value = {"sandboxId": "test_sandbox_123"}
        create_response.raise_for_status = Mock()

        execute_response = Mock()
        execute_response.json.return_value = {
            "stdout": "Hello, World!",
            "stderr": "",
            "exitCode": 0,
            "metadata": {}
        }
        execute_response.raise_for_status = Mock()

        mock_post.side_effect = [create_response, execute_response]

        # Execute code
        code = "print('Hello, World!')"
        result = self.client.execute_code(code, Language.PYTHON)

        # Assertions
        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.status, SandboxStatus.COMPLETED)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "Hello, World!")
        self.assertTrue(result.is_success())

    @patch('requests.Session.post')
    def test_execute_code_failure(self, mock_post):
        """Test code execution failure"""
        # Mock responses
        create_response = Mock()
        create_response.json.return_value = {"sandboxId": "test_sandbox_123"}
        create_response.raise_for_status = Mock()

        execute_response = Mock()
        execute_response.json.return_value = {
            "stdout": "",
            "stderr": "NameError: name 'undefined_var' is not defined",
            "exitCode": 1,
            "metadata": {}
        }
        execute_response.raise_for_status = Mock()

        mock_post.side_effect = [create_response, execute_response]

        # Execute code with error
        code = "print(undefined_var)"
        result = self.client.execute_code(code, Language.PYTHON)

        # Assertions
        self.assertEqual(result.status, SandboxStatus.COMPLETED)
        self.assertEqual(result.exit_code, 1)
        self.assertFalse(result.is_success())
        self.assertIn("NameError", result.stderr)

    @patch('requests.Session.post')
    def test_execute_code_timeout(self, mock_post):
        """Test code execution timeout"""
        import requests

        # Mock timeout exception
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        # Execute code with short timeout
        config = SandboxConfig(timeout=1)
        result = self.client.execute_code("time.sleep(100)", Language.PYTHON, config=config)

        # Assertions
        self.assertEqual(result.status, SandboxStatus.TIMEOUT)
        self.assertEqual(result.exit_code, -1)

    @patch('requests.Session.delete')
    def test_delete_sandbox(self, mock_delete):
        """Test sandbox deletion"""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        # Delete sandbox
        success = self.client.delete_sandbox("test_sandbox_123")

        # Assertions
        self.assertTrue(success)
        mock_delete.assert_called_once()

    @patch('requests.Session.get')
    def test_get_sandbox_status(self, mock_get):
        """Test getting sandbox status"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "sandboxId": "test_sandbox_123",
            "status": "running",
            "template": "python"
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Get status
        status = self.client.get_sandbox_status("test_sandbox_123")

        # Assertions
        self.assertIsInstance(status, dict)
        self.assertEqual(status["sandboxId"], "test_sandbox_123")
        self.assertEqual(status["status"], "running")

    @patch('requests.Session.get')
    def test_list_sandboxes(self, mock_get):
        """Test listing all sandboxes"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "sandboxes": [
                {"sandboxId": "sandbox_1", "status": "running"},
                {"sandboxId": "sandbox_2", "status": "stopped"}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # List sandboxes
        sandboxes = self.client.list_sandboxes()

        # Assertions
        self.assertIsInstance(sandboxes, list)
        self.assertEqual(len(sandboxes), 2)
        self.assertEqual(sandboxes[0]["sandboxId"], "sandbox_1")

    def test_execution_result_to_dict(self):
        """Test ExecutionResult serialization"""
        result = ExecutionResult(
            sandbox_id="test_123",
            status=SandboxStatus.COMPLETED,
            stdout="output",
            stderr="",
            exit_code=0,
            execution_time=1.5,
            timestamp=datetime.now(),
            language=Language.PYTHON,
            metadata={"test": True}
        )

        result_dict = result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["sandbox_id"], "test_123")
        self.assertEqual(result_dict["status"], "completed")
        self.assertEqual(result_dict["language"], "python")

    def test_sandbox_config_defaults(self):
        """Test SandboxConfig default values"""
        config = SandboxConfig()

        self.assertEqual(config.timeout, 300)
        self.assertEqual(config.memory_limit, 512)
        self.assertEqual(config.cpu_limit, 1.0)
        self.assertTrue(config.network_enabled)
        self.assertTrue(config.filesystem_enabled)
        self.assertIsInstance(config.environment_vars, dict)


class TestSandboxPool(unittest.TestCase):
    """Test cases for SandboxPool"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("E2B_API_KEY", "test_api_key")
        self.client = E2BSandboxClient(self.api_key)

    def tearDown(self):
        """Clean up after tests"""
        self.client.close()

    @patch('e2b_sandbox.E2BSandboxClient.create_sandbox')
    async def test_pool_initialization(self, mock_create):
        """Test pool initialization"""
        # Mock sandbox creation
        mock_create.side_effect = [f"sandbox_{i}" for i in range(5)]

        # Create pool
        pool = SandboxPool(self.client, pool_size=5)
        await pool.initialize()

        # Assertions
        self.assertEqual(len(pool.available), 5)
        self.assertEqual(mock_create.call_count, 5)

    @patch('e2b_sandbox.E2BSandboxClient.create_sandbox')
    async def test_acquire_release_sandbox(self, mock_create):
        """Test acquiring and releasing sandboxes"""
        mock_create.return_value = "sandbox_1"

        pool = SandboxPool(self.client, pool_size=2)
        await pool.initialize()

        # Acquire sandbox
        sandbox_id = await pool.acquire()
        self.assertIsNotNone(sandbox_id)
        self.assertIn(sandbox_id, pool.in_use)

        # Release sandbox
        await pool.release(sandbox_id)
        self.assertNotIn(sandbox_id, pool.in_use)
        self.assertIn(sandbox_id, pool.available)


class TestLanguageSupport(unittest.TestCase):
    """Test cases for different programming languages"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("E2B_API_KEY", "test_api_key")
        self.client = E2BSandboxClient(self.api_key)

    def tearDown(self):
        """Clean up after tests"""
        self.client.close()

    def test_language_enum_values(self):
        """Test Language enum values"""
        self.assertEqual(Language.PYTHON.value, "python")
        self.assertEqual(Language.JAVASCRIPT.value, "javascript")
        self.assertEqual(Language.TYPESCRIPT.value, "typescript")
        self.assertEqual(Language.BASH.value, "bash")
        self.assertEqual(Language.GO.value, "go")
        self.assertEqual(Language.RUST.value, "rust")

    @patch('requests.Session.post')
    def test_javascript_execution(self, mock_post):
        """Test JavaScript code execution"""
        create_response = Mock()
        create_response.json.return_value = {"sandboxId": "js_sandbox"}
        create_response.raise_for_status = Mock()

        execute_response = Mock()
        execute_response.json.return_value = {
            "stdout": "Hello from JavaScript",
            "stderr": "",
            "exitCode": 0,
            "metadata": {}
        }
        execute_response.raise_for_status = Mock()

        mock_post.side_effect = [create_response, execute_response]

        code = "console.log('Hello from JavaScript');"
        result = self.client.execute_code(code, Language.JAVASCRIPT)

        self.assertEqual(result.language, Language.JAVASCRIPT)
        self.assertTrue(result.is_success())


class TestFileOperations(unittest.TestCase):
    """Test cases for file operations"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("E2B_API_KEY", "test_api_key")
        self.client = E2BSandboxClient(self.api_key)

    def tearDown(self):
        """Clean up after tests"""
        self.client.close()

    @patch('requests.Session.post')
    @patch('builtins.open', create=True)
    def test_upload_file(self, mock_open, mock_post):
        """Test file upload to sandbox"""
        # Mock file and response
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Upload file
        success = self.client.upload_file(
            sandbox_id="test_sandbox",
            local_path="/tmp/test.txt",
            remote_path="/sandbox/test.txt"
        )

        self.assertTrue(success)
        mock_post.assert_called_once()

    @patch('requests.Session.get')
    def test_list_files(self, mock_get):
        """Test listing files in sandbox"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "files": [
                {"name": "file1.py", "size": 1024},
                {"name": "file2.txt", "size": 512}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # List files
        files = self.client.list_files("test_sandbox", "/")

        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["name"], "file1.py")


class IntegrationTests(unittest.TestCase):
    """
    Integration tests - only run if E2B_API_KEY is set
    These tests make actual API calls
    """

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures"""
        cls.api_key = os.getenv("E2B_API_KEY")
        if cls.api_key and not cls.api_key.startswith("test_"):
            cls.run_integration = True
            cls.client = E2BSandboxClient(cls.api_key)
        else:
            cls.run_integration = False

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures"""
        if cls.run_integration:
            cls.client.close()

    def test_real_sandbox_creation(self):
        """Test real sandbox creation (requires valid API key)"""
        if not self.run_integration:
            self.skipTest("Integration tests disabled (no valid API key)")

        try:
            sandbox_id = self.client.create_sandbox()
            self.assertIsNotNone(sandbox_id)
            self.assertIsInstance(sandbox_id, str)

            # Clean up
            self.client.delete_sandbox(sandbox_id)
        except Exception as e:
            self.fail(f"Real sandbox creation failed: {e}")

    def test_real_code_execution(self):
        """Test real code execution (requires valid API key)"""
        if not self.run_integration:
            self.skipTest("Integration tests disabled (no valid API key)")

        try:
            code = """
import sys
print("Python version:", sys.version)
print("Hello from E2B!")
"""
            result = self.client.execute_code(code, Language.PYTHON)

            self.assertEqual(result.status, SandboxStatus.COMPLETED)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Hello from E2B!", result.stdout)

            # Clean up
            self.client.delete_sandbox(result.sandbox_id)
        except Exception as e:
            self.fail(f"Real code execution failed: {e}")


def run_tests(verbosity=2):
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestE2BSandboxClient))
    suite.addTests(loader.loadTestsFromTestCase(TestSandboxPool))
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTests))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
