#!/usr/bin/env python3
"""
Robinhood 1099 and CSV Transaction Parser
Part 2 Implementation - Pillar A (Trading)

Parses Robinhood 1099 documents and transaction CSVs for integration
with the Integer Watchdog cashflow monitoring system.
"""

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json


class RobinhoodParser:
    """Parser for Robinhood 1099 tax documents and transaction CSVs."""
    
    def __init__(self):
        self.transactions = []
        self.tax_data = {}
        self.cashflow_spikes = []
        
    def parse_1099_text(self, file_path: str) -> Dict:
        """
        Parse Robinhood 1099 tax document.
        
        Args:
            file_path: Path to 1099 document (text or PDF extracted text)
            
        Returns:
            Dictionary containing parsed tax information
        """
        tax_info = {
            'document_type': '1099',
            'year': None,
            'total_proceeds': 0.0,
            'cost_basis': 0.0,
            'gains_losses': 0.0,
            'dividend_income': 0.0,
            'interest_income': 0.0,
            'parsed_date': datetime.now().isoformat()
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract year from 1099 document
            year_match = re.search(r'(?:tax year|year)\s*(\d{4})', content, re.IGNORECASE)
            if year_match:
                tax_info['year'] = int(year_match.group(1))
            
            # Extract proceeds (box 1d)
            proceeds_match = re.search(r'proceeds.*?[\$]?\s*([\d,]+(?:\.\d+)?)', content, re.IGNORECASE)
            if proceeds_match:
                tax_info['total_proceeds'] = float(proceeds_match.group(1).replace(',', ''))
            
            # Extract cost basis (box 1e)
            basis_match = re.search(r'(?:cost|basis).*?[\$]?\s*([\d,]+(?:\.\d+)?)', content, re.IGNORECASE)
            if basis_match:
                tax_info['cost_basis'] = float(basis_match.group(1).replace(',', ''))
            
            # Calculate gains/losses
            if tax_info['total_proceeds'] and tax_info['cost_basis']:
                tax_info['gains_losses'] = tax_info['total_proceeds'] - tax_info['cost_basis']
            
            # Extract dividend income (box 1a)
            dividend_match = re.search(r'dividend.*?[\$]?\s*([\d,]+(?:\.\d+)?)', content, re.IGNORECASE)
            if dividend_match:
                tax_info['dividend_income'] = float(dividend_match.group(1).replace(',', ''))
            
            # Extract interest income
            interest_match = re.search(r'interest.*?[\$]?\s*([\d,]+(?:\.\d+)?)', content, re.IGNORECASE)
            if interest_match:
                tax_info['interest_income'] = float(interest_match.group(1).replace(',', ''))
            
            self.tax_data = tax_info
            return tax_info
            
        except Exception as e:
            print(f"Error parsing 1099: {e}")
            return tax_info
    
    def parse_transaction_csv(self, file_path: str) -> List[Dict]:
        """
        Parse Robinhood transaction CSV export.
        
        Expected CSV columns: Date, Description, Symbol, Quantity, Price, Amount, etc.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    transaction = {
                        'date': row.get('Date', ''),
                        'description': row.get('Description', ''),
                        'symbol': row.get('Symbol', ''),
                        'quantity': float(row.get('Quantity', 0) or 0),
                        'price': float(row.get('Price', 0) or 0),
                        'amount': float(row.get('Amount', 0) or 0),
                        'transaction_type': self._classify_transaction(row.get('Description', '')),
                        'parsed_date': datetime.now().isoformat()
                    }
                    
                    transactions.append(transaction)
            
            self.transactions = transactions
            return transactions
            
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return transactions
    
    def _classify_transaction(self, description: str) -> str:
        """Classify transaction type based on description."""
        description_lower = description.lower()
        
        if 'buy' in description_lower:
            return 'BUY'
        elif 'sell' in description_lower:
            return 'SELL'
        elif 'dividend' in description_lower:
            return 'DIVIDEND'
        elif 'deposit' in description_lower:
            return 'DEPOSIT'
        elif 'withdrawal' in description_lower:
            return 'WITHDRAWAL'
        elif 'transfer' in description_lower:
            return 'TRANSFER'
        else:
            return 'OTHER'
    
    def detect_cashflow_spikes(self, threshold: float = 10000.0) -> List[Dict]:
        """
        Detect significant cashflow spikes for Integer Watchdog monitoring.
        
        Args:
            threshold: Minimum amount to consider as a spike (default $10,000)
            
        Returns:
            List of spike events with details
        """
        spikes = []
        
        # Group transactions by month
        monthly_cashflow = {}
        
        for txn in self.transactions:
            try:
                date_obj = datetime.strptime(txn['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                if month_key not in monthly_cashflow:
                    monthly_cashflow[month_key] = {
                        'inflow': 0.0,
                        'outflow': 0.0,
                        'transactions': []
                    }
                
                amount = txn['amount']
                if amount > 0:
                    monthly_cashflow[month_key]['inflow'] += amount
                else:
                    monthly_cashflow[month_key]['outflow'] += abs(amount)
                
                monthly_cashflow[month_key]['transactions'].append(txn)
                
            except Exception as e:
                print(f"Error processing transaction date: {e}")
                continue
        
        # Identify spikes
        for month, data in monthly_cashflow.items():
            net_flow = data['inflow'] - data['outflow']
            
            if abs(net_flow) >= threshold or data['inflow'] >= threshold:
                spike = {
                    'month': month,
                    'inflow': data['inflow'],
                    'outflow': data['outflow'],
                    'net_flow': net_flow,
                    'transaction_count': len(data['transactions']),
                    'flagged_for_review': True,
                    'threshold': threshold,
                    'detected_date': datetime.now().isoformat()
                }
                spikes.append(spike)
        
        self.cashflow_spikes = spikes
        return spikes
    
    def export_to_integer_watchdog(self, output_path: str) -> bool:
        """
        Export parsed data in format for Integer Watchdog system.
        
        Args:
            output_path: Path to save JSON export
            
        Returns:
            True if successful
        """
        try:
            watchdog_data = {
                'source': 'robinhood',
                'export_date': datetime.now().isoformat(),
                'tax_summary': self.tax_data,
                'transactions': self.transactions,
                'cashflow_spikes': self.cashflow_spikes,
                'statistics': {
                    'total_transactions': len(self.transactions),
                    'spike_count': len(self.cashflow_spikes),
                    'total_gains_losses': self.tax_data.get('gains_losses', 0)
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(watchdog_data, f, indent=2)
            
            print(f"Successfully exported to Integer Watchdog format: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        report_lines = [
            "=" * 60,
            "ROBINHOOD DATA ANALYSIS SUMMARY",
            "=" * 60,
            "",
            "TAX INFORMATION:",
            f"  Year: {self.tax_data.get('year', 'N/A')}",
            f"  Total Proceeds: ${self.tax_data.get('total_proceeds', 0):,.2f}",
            f"  Cost Basis: ${self.tax_data.get('cost_basis', 0):,.2f}",
            f"  Gains/Losses: ${self.tax_data.get('gains_losses', 0):,.2f}",
            f"  Dividend Income: ${self.tax_data.get('dividend_income', 0):,.2f}",
            "",
            "TRANSACTION SUMMARY:",
            f"  Total Transactions: {len(self.transactions)}",
            "",
            "CASHFLOW SPIKES DETECTED:",
            f"  Total Spikes: {len(self.cashflow_spikes)}",
            ""
        ]
        
        if self.cashflow_spikes:
            report_lines.append("  Details:")
            for spike in self.cashflow_spikes:
                report_lines.append(f"    • {spike['month']}: Inflow ${spike['inflow']:,.2f}, "
                                  f"Net ${spike['net_flow']:,.2f}")
        else:
            report_lines.append("  No significant spikes detected.")
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)


def main():
    """Example usage of RobinhoodParser."""
    parser = RobinhoodParser()
    
    print("Robinhood Parser - Part 2 Implementation")
    print("This parser processes Robinhood 1099 and CSV files for Integer Watchdog integration.")
    print("\nUsage:")
    print("  parser = RobinhoodParser()")
    print("  parser.parse_1099_text('path/to/1099.txt')")
    print("  parser.parse_transaction_csv('path/to/transactions.csv')")
    print("  spikes = parser.detect_cashflow_spikes(threshold=10000)")
    print("  parser.export_to_integer_watchdog('output.json')")
    print("  print(parser.generate_summary_report())")


if __name__ == "__main__":
    main()
