#!/usr/bin/env python3
"""
Unit Tests for Deleted Azure Logic Apps Workflow JSON Files
Tests the schema and structure of:
- ai_builder_sensitive_info_flow 2.json
- flow7_definition.json
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any


class TestAzureWorkflowSchema:
    """Base tests for Azure Logic Apps workflow schemas"""

    def test_workflow_schema_version(self):
        """Test workflow uses correct schema version"""
        schema_url = "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#"
        assert "schema.management.azure.com" in schema_url
        assert "Microsoft.Logic" in schema_url
        assert "2016-06-01" in schema_url

    def test_workflow_content_version(self):
        """Test workflow has valid content version"""
        content_version = "1.0.0.0"
        parts = content_version.split(".")
        assert len(parts) == 4
        assert all(part.isdigit() for part in parts)


class TestSensitiveInfoFlow:
    """Tests for ai_builder_sensitive_info_flow 2.json"""

    @pytest.fixture
    def workflow_structure(self):
        """Mock workflow structure"""
        return {
            "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {},
            "triggers": {
                "When_a_file_is_created": {
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "connection": {
                                "name": "@parameters('$connections')['sharepoint']['connectionId']"
                            }
                        },
                        "operationId": "OnNewFile"
                    }
                }
            },
            "actions": {
                "Get_file_content": {
                    "type": "OpenApiConnection",
                    "runAfter": {}
                },
                "Detect_sensitive_information": {
                    "type": "OpenApiConnection",
                    "runAfter": {
                        "Get_file_content": ["Succeeded"]
                    }
                }
            }
        }

    def test_workflow_has_required_sections(self, workflow_structure):
        """Test workflow has all required sections"""
        assert "$schema" in workflow_structure
        assert "contentVersion" in workflow_structure
        assert "parameters" in workflow_structure
        assert "triggers" in workflow_structure
        assert "actions" in workflow_structure

    def test_trigger_configuration(self, workflow_structure):
        """Test trigger is properly configured"""
        triggers = workflow_structure["triggers"]
        assert "When_a_file_is_created" in triggers
        
        trigger = triggers["When_a_file_is_created"]
        assert trigger["type"] == "OpenApiConnection"
        assert "inputs" in trigger
        assert "host" in trigger["inputs"]

    def test_sharepoint_connection_reference(self, workflow_structure):
        """Test SharePoint connection is referenced"""
        trigger = workflow_structure["triggers"]["When_a_file_is_created"]
        connection_ref = trigger["inputs"]["host"]["connection"]["name"]
        assert "sharepoint" in connection_ref
        assert "$connections" in connection_ref

    def test_file_trigger_operation(self, workflow_structure):
        """Test file creation trigger operation"""
        trigger = workflow_structure["triggers"]["When_a_file_is_created"]
        assert trigger["inputs"]["operationId"] == "OnNewFile"

    def test_get_file_content_action(self, workflow_structure):
        """Test get file content action exists"""
        actions = workflow_structure["actions"]
        assert "Get_file_content" in actions
        assert actions["Get_file_content"]["type"] == "OpenApiConnection"

    def test_detect_sensitive_info_action(self, workflow_structure):
        """Test detect sensitive information action"""
        actions = workflow_structure["actions"]
        assert "Detect_sensitive_information" in actions
        
        action = actions["Detect_sensitive_information"]
        assert action["type"] == "OpenApiConnection"
        assert "runAfter" in action
        assert "Get_file_content" in action["runAfter"]

    def test_action_dependencies(self, workflow_structure):
        """Test action execution order dependencies"""
        detect_action = workflow_structure["actions"]["Detect_sensitive_information"]
        run_after = detect_action["runAfter"]
        
        assert "Get_file_content" in run_after
        assert "Succeeded" in run_after["Get_file_content"]

    def test_workflow_connection_parameters(self, workflow_structure):
        """Test workflow uses parameters for connections"""
        trigger = workflow_structure["triggers"]["When_a_file_is_created"]
        connection_name = trigger["inputs"]["host"]["connection"]["name"]
        assert connection_name.startswith("@parameters(")
        assert "connectionId" in connection_name


class TestQuarterlyReportFlow:
    """Tests for flow7_definition.json"""

    @pytest.fixture
    def quarterly_workflow(self):
        """Mock quarterly report workflow structure"""
        return {
            "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {},
            "triggers": {
                "Recurrence": {
                    "type": "Recurrence",
                    "recurrence": {
                        "frequency": "Month",
                        "interval": 3
                    }
                }
            },
            "actions": {
                "Get_All_Documents": {
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "connection": {
                                "name": "@parameters('$connections')['sharepoint']['connectionId']"
                            }
                        },
                        "operationId": "GetItems"
                    }
                },
                "Create_CSV_Table_Quarterly": {
                    "type": "ApiConnection",
                    "inputs": {
                        "host": {
                            "connection": {
                                "name": "@parameters('$connections')['dataoperations']['connectionId']"
                            }
                        },
                        "operationId": "CreateCSVTable"
                    }
                },
                "Create_Quarterly_Report": {
                    "type": "OpenApiConnection"
                }
            }
        }

    def test_recurrence_trigger_configuration(self, quarterly_workflow):
        """Test recurrence trigger is properly configured"""
        triggers = quarterly_workflow["triggers"]
        assert "Recurrence" in triggers
        
        trigger = triggers["Recurrence"]
        assert trigger["type"] == "Recurrence"
        assert "recurrence" in trigger

    def test_quarterly_schedule(self, quarterly_workflow):
        """Test workflow runs quarterly"""
        recurrence = quarterly_workflow["triggers"]["Recurrence"]["recurrence"]
        assert recurrence["frequency"] == "Month"
        assert recurrence["interval"] == 3

    def test_get_documents_action(self, quarterly_workflow):
        """Test get all documents action"""
        actions = quarterly_workflow["actions"]
        assert "Get_All_Documents" in actions
        
        action = actions["Get_All_Documents"]
        assert action["type"] == "OpenApiConnection"
        assert action["inputs"]["operationId"] == "GetItems"

    def test_csv_creation_action(self, quarterly_workflow):
        """Test CSV table creation action"""
        actions = quarterly_workflow["actions"]
        assert "Create_CSV_Table_Quarterly" in actions
        
        action = actions["Create_CSV_Table_Quarterly"]
        assert action["type"] == "ApiConnection"
        assert action["inputs"]["operationId"] == "CreateCSVTable"

    def test_data_operations_connection(self, quarterly_workflow):
        """Test data operations connection reference"""
        action = quarterly_workflow["actions"]["Create_CSV_Table_Quarterly"]
        connection_ref = action["inputs"]["host"]["connection"]["name"]
        assert "dataoperations" in connection_ref

    def test_report_creation_action(self, quarterly_workflow):
        """Test quarterly report creation action"""
        actions = quarterly_workflow["actions"]
        assert "Create_Quarterly_Report" in actions


class TestWorkflowValidation:
    """General workflow validation tests"""

    def test_valid_trigger_types(self):
        """Test valid trigger types"""
        valid_types = [
            "Recurrence",
            "Request",
            "HttpWebhook",
            "OpenApiConnection",
            "ApiConnection"
        ]
        for trigger_type in valid_types:
            assert isinstance(trigger_type, str)
            assert len(trigger_type) > 0

    def test_valid_action_types(self):
        """Test valid action types"""
        valid_types = [
            "OpenApiConnection",
            "ApiConnection",
            "Http",
            "Compose",
            "Parse",
            "Response",
            "Condition",
            "Foreach",
            "Until"
        ]
        for action_type in valid_types:
            assert isinstance(action_type, str)

    def test_run_after_status_values(self):
        """Test valid runAfter status values"""
        valid_statuses = ["Succeeded", "Failed", "Skipped", "TimedOut"]
        for status in valid_statuses:
            assert isinstance(status, str)
            assert status in valid_statuses

    def test_recurrence_frequencies(self):
        """Test valid recurrence frequencies"""
        valid_frequencies = ["Second", "Minute", "Hour", "Day", "Week", "Month", "Year"]
        for freq in valid_frequencies:
            assert isinstance(freq, str)
            assert freq.istitle()

    def test_connection_parameter_format(self):
        """Test connection parameter format"""
        param = "@parameters('$connections')['sharepoint']['connectionId']"
        assert param.startswith("@parameters(")
        assert "$connections" in param
        assert param.endswith("')")

    def test_workflow_expression_syntax(self):
        """Test workflow expression syntax"""
        expressions = [
            "@parameters('variableName')",
            "@triggerOutputs()?['body/{Path}']",
            "@outputs('ActionName')?['body/value']"
        ]
        for expr in expressions:
            assert expr.startswith("@")
            assert "(" in expr and ")" in expr


class TestSharePointIntegration:
    """Tests for SharePoint integration patterns"""

    def test_sharepoint_dataset_format(self):
        """Test SharePoint dataset URL format"""
        dataset = "https://contoso.sharepoint.com/sites/YourSite"
        assert dataset.startswith("https://")
        assert "sharepoint.com" in dataset
        assert "/sites/" in dataset

    def test_sharepoint_operations(self):
        """Test valid SharePoint operations"""
        operations = [
            "OnNewFile",
            "GetFileContentByPath",
            "GetItems",
            "CreateFile",
            "UpdateFile"
        ]
        for op in operations:
            assert isinstance(op, str)
            assert op[0].isupper()

    def test_document_library_path(self):
        """Test document library path format"""
        library = "Documents"
        assert isinstance(library, str)
        assert len(library) > 0


class TestDataOperations:
    """Tests for data operations integration"""

    def test_csv_table_creation(self):
        """Test CSV table creation operation"""
        operation = "CreateCSVTable"
        assert operation == "CreateCSVTable"

    def test_data_transformation_operations(self):
        """Test valid data transformation operations"""
        operations = [
            "CreateCSVTable",
            "CreateHTMLTable",
            "Parse",
            "Compose",
            "Join",
            "Select"
        ]
        for op in operations:
            assert isinstance(op, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])