"""
CSV Handler for Agent 4.0 Advanced
Advanced CSV parsing, transformation, analysis, and export
"""

import csv
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVHandler:
    """Advanced CSV processing class"""
    
    def __init__(self):
        self.supported_operations = [
            'parse', 'transform', 'analyze', 'export',
            'validate', 'merge', 'filter', 'aggregate'
        ]
        self.loaded_data = []
        self.headers = []
    
    def parse(
        self,
        file_path: Optional[str] = None,
        csv_content: Optional[str] = None,
        delimiter: str = ',',
        has_header: bool = True
    ) -> Dict:
        """
        Parse CSV file or content
        
        Args:
            file_path: Path to CSV file
            csv_content: CSV content as string
            delimiter: Field delimiter
            has_header: Whether first row is header
            
        Returns:
            Dictionary with parsed data
        """
        try:
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    csv_data = f.read()
            elif csv_content:
                csv_data = csv_content
            else:
                return {'success': False, 'error': 'No input provided'}
            
            # Parse CSV
            csv_reader = csv.reader(io.StringIO(csv_data), delimiter=delimiter)
            rows = list(csv_reader)
            
            if not rows:
                return {'success': False, 'error': 'Empty CSV'}
            
            if has_header:
                self.headers = rows[0]
                data_rows = rows[1:]
            else:
                self.headers = [f'Column_{i+1}' for i in range(len(rows[0]))]
                data_rows = rows
            
            # Convert to list of dictionaries
            self.loaded_data = []
            for row in data_rows:
                if len(row) == len(self.headers):
                    row_dict = dict(zip(self.headers, row))
                    self.loaded_data.append(row_dict)
            
            return {
                'success': True,
                'rows': len(self.loaded_data),
                'columns': len(self.headers),
                'headers': self.headers,
                'sample': self.loaded_data[:5] if self.loaded_data else []
            }
            
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            return {'success': False, 'error': str(e)}
    
    def transform(self, operations: List[Dict]) -> Dict:
        """
        Apply transformations to loaded data
        
        Args:
            operations: List of transformation operations
                Example: [
                    {'type': 'rename', 'from': 'old_name', 'to': 'new_name'},
                    {'type': 'convert', 'column': 'price', 'to_type': 'float'},
                    {'type': 'calculate', 'name': 'total', 'formula': 'price * quantity'}
                ]
            
        Returns:
            Dictionary with transformation results
        """
        if not self.loaded_data:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            transformed_count = 0
            
            for operation in operations:
                op_type = operation.get('type')
                
                if op_type == 'rename':
                    old_name = operation.get('from')
                    new_name = operation.get('to')
                    if old_name in self.headers:
                        idx = self.headers.index(old_name)
                        self.headers[idx] = new_name
                        for row in self.loaded_data:
                            if old_name in row:
                                row[new_name] = row.pop(old_name)
                        transformed_count += 1
                
                elif op_type == 'convert':
                    column = operation.get('column')
                    to_type = operation.get('to_type', 'str')
                    if column in self.headers:
                        for row in self.loaded_data:
                            try:
                                if to_type == 'float':
                                    row[column] = float(row[column])
                                elif to_type == 'int':
                                    row[column] = int(row[column])
                                elif to_type == 'str':
                                    row[column] = str(row[column])
                            except (ValueError, TypeError):
                                pass
                        transformed_count += 1
                
                elif op_type == 'calculate':
                    name = operation.get('name')
                    formula = operation.get('formula')
                    if name and formula:
                        for row in self.loaded_data:
                            try:
                                # Safe evaluation with restricted operations
                                # Only allow basic arithmetic operations
                                allowed_ops = {
                                    '__builtins__': {},
                                    'abs': abs,
                                    'min': min,
                                    'max': max,
                                    'sum': sum,
                                    'round': round,
                                    'int': int,
                                    'float': float
                                }
                                # Combine allowed operations with row values
                                eval_context = {**allowed_ops, **row}
                                result = eval(formula, {"__builtins__": {}}, eval_context)
                                row[name] = result
                            except Exception:
                                row[name] = None
                        if name not in self.headers:
                            self.headers.append(name)
                        transformed_count += 1
            
            return {
                'success': True,
                'transformations_applied': transformed_count,
                'rows': len(self.loaded_data),
                'columns': len(self.headers)
            }
            
        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze(self, columns: Optional[List[str]] = None) -> Dict:
        """
        Analyze loaded data
        
        Args:
            columns: List of columns to analyze (None for all)
            
        Returns:
            Dictionary with analysis results
        """
        if not self.loaded_data:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            columns_to_analyze = columns if columns else self.headers
            analysis = {}
            
            for column in columns_to_analyze:
                if column not in self.headers:
                    continue
                
                values = [row.get(column) for row in self.loaded_data]
                non_null_values = [v for v in values if v is not None and v != '']
                
                column_analysis = {
                    'total_count': len(values),
                    'non_null_count': len(non_null_values),
                    'null_count': len(values) - len(non_null_values),
                    'unique_count': len(set(str(v) for v in non_null_values))
                }
                
                # Try numeric analysis
                try:
                    numeric_values = [float(v) for v in non_null_values if v != '']
                    if numeric_values:
                        column_analysis['min'] = min(numeric_values)
                        column_analysis['max'] = max(numeric_values)
                        column_analysis['mean'] = sum(numeric_values) / len(numeric_values)
                        column_analysis['sum'] = sum(numeric_values)
                except (ValueError, TypeError):
                    pass
                
                analysis[column] = column_analysis
            
            return {
                'success': True,
                'analysis': analysis,
                'total_rows': len(self.loaded_data),
                'total_columns': len(self.headers)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            return {'success': False, 'error': str(e)}
    
    def filter(self, conditions: List[Dict]) -> Dict:
        """
        Filter loaded data based on conditions
        
        Args:
            conditions: List of filter conditions
                Example: [
                    {'column': 'price', 'operator': '>', 'value': 100},
                    {'column': 'status', 'operator': '==', 'value': 'active'}
                ]
            
        Returns:
            Dictionary with filter results
        """
        if not self.loaded_data:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            filtered_data = self.loaded_data.copy()
            
            for condition in conditions:
                column = condition.get('column')
                operator = condition.get('operator', '==')
                value = condition.get('value')
                
                if column not in self.headers:
                    continue
                
                new_filtered = []
                for row in filtered_data:
                    row_value = row.get(column)
                    try:
                        # Convert to numbers if possible
                        try:
                            row_value = float(row_value)
                            value = float(value)
                        except (ValueError, TypeError):
                            pass
                        
                        if operator == '==':
                            if row_value == value:
                                new_filtered.append(row)
                        elif operator == '!=':
                            if row_value != value:
                                new_filtered.append(row)
                        elif operator == '>':
                            if row_value > value:
                                new_filtered.append(row)
                        elif operator == '<':
                            if row_value < value:
                                new_filtered.append(row)
                        elif operator == '>=':
                            if row_value >= value:
                                new_filtered.append(row)
                        elif operator == '<=':
                            if row_value <= value:
                                new_filtered.append(row)
                        elif operator == 'contains':
                            if str(value).lower() in str(row_value).lower():
                                new_filtered.append(row)
                    except Exception:
                        pass
                
                filtered_data = new_filtered
            
            self.loaded_data = filtered_data
            
            return {
                'success': True,
                'filtered_rows': len(filtered_data),
                'conditions_applied': len(conditions)
            }
            
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            return {'success': False, 'error': str(e)}
    
    def export(
        self,
        output_path: Optional[str] = None,
        format: str = 'csv',
        delimiter: str = ','
    ) -> Dict:
        """
        Export data to file
        
        Args:
            output_path: Path to save file
            format: Output format (csv, json, excel)
            delimiter: Field delimiter for CSV
            
        Returns:
            Dictionary with export results
        """
        if not self.loaded_data:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            if format == 'csv':
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=self.headers, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(self.loaded_data)
                
                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(output.getvalue())
                    return {
                        'success': True,
                        'output_path': output_path,
                        'format': format,
                        'rows': len(self.loaded_data)
                    }
                else:
                    return {
                        'success': True,
                        'content': output.getvalue(),
                        'format': format,
                        'rows': len(self.loaded_data)
                    }
            
            elif format == 'json':
                json_data = json.dumps(self.loaded_data, indent=2)
                
                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(json_data)
                    return {
                        'success': True,
                        'output_path': output_path,
                        'format': format,
                        'rows': len(self.loaded_data)
                    }
                else:
                    return {
                        'success': True,
                        'content': json_data,
                        'format': format,
                        'rows': len(self.loaded_data)
                    }
            
            else:
                return {'success': False, 'error': f'Unsupported format: {format}'}
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate(self, schema: Dict[str, Dict]) -> Dict:
        """
        Validate data against schema
        
        Args:
            schema: Column validation rules
                Example: {
                    'email': {'type': 'email', 'required': True},
                    'age': {'type': 'int', 'min': 0, 'max': 120}
                }
            
        Returns:
            Dictionary with validation results
        """
        if not self.loaded_data:
            return {'success': False, 'error': 'No data loaded'}
        
        try:
            errors = []
            
            for idx, row in enumerate(self.loaded_data):
                row_errors = []
                
                for column, rules in schema.items():
                    value = row.get(column)
                    
                    # Check required
                    if rules.get('required') and (value is None or value == ''):
                        row_errors.append(f"Column '{column}' is required")
                        continue
                    
                    if value is None or value == '':
                        continue
                    
                    # Check type
                    col_type = rules.get('type')
                    if col_type == 'int':
                        try:
                            int(value)
                        except (ValueError, TypeError):
                            row_errors.append(f"Column '{column}' must be integer")
                    elif col_type == 'float':
                        try:
                            float(value)
                        except (ValueError, TypeError):
                            row_errors.append(f"Column '{column}' must be number")
                    elif col_type == 'email':
                        if '@' not in str(value):
                            row_errors.append(f"Column '{column}' must be valid email")
                    
                    # Check range
                    if 'min' in rules:
                        try:
                            if float(value) < rules['min']:
                                row_errors.append(f"Column '{column}' below minimum {rules['min']}")
                        except (ValueError, TypeError):
                            pass
                    
                    if 'max' in rules:
                        try:
                            if float(value) > rules['max']:
                                row_errors.append(f"Column '{column}' above maximum {rules['max']}")
                        except (ValueError, TypeError):
                            pass
                
                if row_errors:
                    errors.append({
                        'row': idx + 1,
                        'errors': row_errors
                    })
            
            return {
                'success': True,
                'valid': len(errors) == 0,
                'total_rows': len(self.loaded_data),
                'error_rows': len(errors),
                'errors': errors[:100]  # Limit to first 100 errors
            }
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """Example usage"""
    handler = CSVHandler()
    
    print("=== CSV Handler Toolkit ===")
    print(f"Supported operations: {', '.join(handler.supported_operations)}")
    
    # Example: Parse CSV content
    csv_content = """name,price,quantity
Product A,10.50,100
Product B,25.00,50
Product C,15.75,75"""
    
    result = handler.parse(csv_content=csv_content)
    if result.get('success'):
        print(f"\n✓ Parsed {result['rows']} rows, {result['columns']} columns")
        print(f"Headers: {result['headers']}")
    
    # Example: Transform data
    transformations = [
        {'type': 'convert', 'column': 'price', 'to_type': 'float'},
        {'type': 'convert', 'column': 'quantity', 'to_type': 'int'},
        {'type': 'calculate', 'name': 'total', 'formula': 'price * quantity'}
    ]
    
    result = handler.transform(transformations)
    if result.get('success'):
        print(f"\n✓ Applied {result['transformations_applied']} transformations")
    
    # Example: Analyze data
    result = handler.analyze()
    if result.get('success'):
        print(f"\n✓ Analysis completed:")
        print(f"Total rows: {result['total_rows']}")
        print(f"Total columns: {result['total_columns']}")
    
    # Example: Export to JSON
    result = handler.export(format='json')
    if result.get('success'):
        print(f"\n✓ Exported {result['rows']} rows to JSON")


if __name__ == '__main__':
    main()
