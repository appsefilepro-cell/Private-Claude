#!/usr/bin/env python3
'''
EXHIBIT MANAGEMENT SYSTEM
=========================
Airtable-like system for organizing exhibits for legal cases
Automatically arranges exhibits and files for public display
'''

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class ExhibitManager:
    def __init__(self, exhibits_folder="organized_exhibits"):
        self.folder = Path(exhibits_folder)
        self.exhibits = []
        self.ledger = {
            "total_damages": 0.0,
            "categories": {},
            "receipts": [],
            "bank_statements": [],
            "transactions": []
        }

    def create_exhibit(self, file_path: str, category: str, amount: float = 0,
                      description: str = "", date: str = ""):
        '''Create new exhibit entry'''

        exhibit_number = len(self.exhibits) + 1

        exhibit = {
            "exhibit_number": f"Exhibit {exhibit_number}",
            "file": file_path,
            "category": category,
            "amount": amount,
            "description": description,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "verified": False,
            "linked_documents": []
        }

        self.exhibits.append(exhibit)

        if amount > 0:
            self.ledger["total_damages"] += amount
            if category not in self.ledger["categories"]:
                self.ledger["categories"][category] = 0
            self.ledger["categories"][category] += amount

        return exhibit

    def link_to_bank_statement(self, exhibit_number: int, bank_statement: str):
        '''Link exhibit to bank statement for verification'''

        if exhibit_number <= len(self.exhibits):
            self.exhibits[exhibit_number - 1]["linked_documents"].append({
                "type": "bank_statement",
                "file": bank_statement,
                "verified": True
            })
            self.exhibits[exhibit_number - 1]["verified"] = True

    def generate_exhibit_list(self) -> str:
        '''Generate formatted exhibit list for court'''

        output = "EXHIBIT LIST FOR LEGAL PROCEEDINGS\n"
        output += "=" * 80 + "\n\n"

        for exhibit in self.exhibits:
            output += f"{exhibit['exhibit_number']}:\n"
            output += f"  Description: {exhibit['description']}\n"
            output += f"  Category: {exhibit['category']}\n"
            output += f"  Amount: ${exhibit['amount']:,.2f}\n"
            output += f"  Date: {exhibit['date']}\n"
            output += f"  Verified: {'✓' if exhibit['verified'] else '○'}\n"
            output += f"  File: {exhibit['file']}\n"

            if exhibit['linked_documents']:
                output += f"  Linked Documents:\n"
                for doc in exhibit['linked_documents']:
                    output += f"    - {doc['type']}: {doc['file']}\n"

            output += "\n"

        output += "\n" + "=" * 80 + "\n"
        output += f"TOTAL DAMAGES: ${self.ledger['total_damages']:,.2f}\n"
        output += "\nBREAKDOWN BY CATEGORY:\n"
        for category, amount in self.ledger['categories'].items():
            output += f"  {category}: ${amount:,.2f}\n"

        return output

    def export_for_public_display(self, output_file="public_exhibit_index.html"):
        '''Export exhibit list as HTML for public display'''

        html = '''<!DOCTYPE html>
<html>
<head>
    <title>Legal Exhibits - Public Display</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .exhibit { border: 1px solid #ccc; padding: 20px; margin: 20px 0; }
        .verified { color: green; font-weight: bold; }
        .amount { font-size: 1.2em; color: #007bff; }
        .total { background: #f8f9fa; padding: 20px; font-size: 1.3em; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Legal Exhibits - Public Display</h1>
    <p>Generated: ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</p>
'''

        for exhibit in self.exhibits:
            html += f'''
    <div class="exhibit">
        <h2>{exhibit['exhibit_number']}</h2>
        <p><strong>Description:</strong> {exhibit['description']}</p>
        <p><strong>Category:</strong> {exhibit['category']}</p>
        <p class="amount"><strong>Amount:</strong> ${exhibit['amount']:,.2f}</p>
        <p><strong>Date:</strong> {exhibit['date']}</p>
        <p class="{'verified' if exhibit['verified'] else ''}">
            <strong>Verified:</strong> {'✓ YES' if exhibit['verified'] else '○ Pending'}
        </p>
    </div>
'''

        html += f'''
    <div class="total">
        TOTAL DAMAGES: ${self.ledger['total_damages']:,.2f}
    </div>
</body>
</html>
'''

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"✅ Public display generated: {output_file}")
        print(f"   Open in browser to view")

        return output_file

    def save_database(self, filename="exhibits_database.json"):
        '''Save exhibit database'''

        data = {
            "exhibits": self.exhibits,
            "ledger": self.ledger,
            "last_updated": datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Database saved: {filename}")


# Example usage
if __name__ == "__main__":
    manager = ExhibitManager()

    # Example exhibits
    manager.create_exhibit(
        file_path="receipts/bank_charge_001.png",
        category="Unauthorized Bank Charges",
        amount=1234.56,
        description="Unauthorized charge from XYZ Merchant",
        date="2025-01-15"
    )

    manager.create_exhibit(
        file_path="receipts/medical_bill_001.pdf",
        category="Medical Bills",
        amount=5678.90,
        description="Emergency room visit - stress-related",
        date="2025-02-01"
    )

    # Link to bank statement
    manager.link_to_bank_statement(1, "bank_statements/january_2025.pdf")

    # Generate outputs
    exhibit_list = manager.generate_exhibit_list()
    print(exhibit_list)

    manager.export_for_public_display()
    manager.save_database()

    print("\n✅ Exhibit management system ready!")
