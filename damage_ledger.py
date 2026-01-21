#!/usr/bin/env python3
'''
COMPREHENSIVE DAMAGE LEDGER SYSTEM
===================================
Links all damages to receipts, bank statements, transactions, disputes
Verifies all amounts for lawsuit preparation
'''

import json
from datetime import datetime
from decimal import Decimal
from typing import List, Dict

class DamageLedger:
    def __init__(self):
        self.entries = []
        self.verification_status = {}

    def add_damage(self, category: str, amount: float, description: str,
                   receipt: str = "", bank_statement: str = "",
                   transaction: str = "", dispute_email: str = ""):
        '''Add damage entry with all supporting documents'''

        entry = {
            "id": len(self.entries) + 1,
            "date": datetime.now().isoformat(),
            "category": category,
            "amount": Decimal(str(amount)),
            "description": description,
            "evidence": {
                "receipt": receipt,
                "bank_statement": bank_statement,
                "transaction": transaction,
                "dispute_email": dispute_email
            },
            "verified": False,
            "verification_notes": []
        }

        self.entries.append(entry)
        return entry

    def verify_damage(self, damage_id: int, verified_by: str, notes: str = ""):
        '''Verify damage against supporting documents'''

        if damage_id <= len(self.entries):
            entry = self.entries[damage_id - 1]
            entry["verified"] = True
            entry["verification_notes"].append({
                "verified_by": verified_by,
                "date": datetime.now().isoformat(),
                "notes": notes
            })

            self.verification_status[damage_id] = "VERIFIED"

    def calculate_total_damages(self) -> Dict:
        '''Calculate total damages by category'''

        totals = {}
        grand_total = Decimal("0")
        verified_total = Decimal("0")

        for entry in self.entries:
            category = entry["category"]
            amount = entry["amount"]

            if category not in totals:
                totals[category] = {
                    "total": Decimal("0"),
                    "verified": Decimal("0"),
                    "count": 0
                }

            totals[category]["total"] += amount
            totals[category]["count"] += 1
            grand_total += amount

            if entry["verified"]:
                totals[category]["verified"] += amount
                verified_total += amount

        return {
            "by_category": {k: {"total": float(v["total"]),
                                "verified": float(v["verified"]),
                                "count": v["count"]}
                           for k, v in totals.items()},
            "grand_total": float(grand_total),
            "verified_total": float(verified_total),
            "verification_rate": float(verified_total / grand_total * 100) if grand_total > 0 else 0
        }

    def generate_lawsuit_report(self, output_file="lawsuit_damages_report.txt"):
        '''Generate comprehensive report for lawsuit'''

        report = "COMPREHENSIVE DAMAGE REPORT FOR LAWSUIT\n"
        report += "=" * 80 + "\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        totals = self.calculate_total_damages()

        report += "SUMMARY:\n"
        report += f"  Grand Total: ${totals['grand_total']:,.2f}\n"
        report += f"  Verified Total: ${totals['verified_total']:,.2f}\n"
        report += f"  Verification Rate: {totals['verification_rate']:.1f}%\n\n"

        report += "BREAKDOWN BY CATEGORY:\n"
        for category, data in totals['by_category'].items():
            report += f"\n  {category}:\n"
            report += f"    Total: ${data['total']:,.2f}\n"
            report += f"    Verified: ${data['verified']:,.2f}\n"
            report += f"    Entries: {data['count']}\n"

        report += "\n\n" + "=" * 80 + "\n"
        report += "DETAILED ENTRIES:\n\n"

        for entry in self.entries:
            report += f"Entry #{entry['id']}:\n"
            report += f"  Category: {entry['category']}\n"
            report += f"  Amount: ${entry['amount']:,.2f}\n"
            report += f"  Description: {entry['description']}\n"
            report += f"  Date: {entry['date']}\n"
            report += f"  Verified: {'✓' if entry['verified'] else '○'}\n"

            report += f"  Evidence:\n"
            for key, value in entry['evidence'].items():
                if value:
                    report += f"    {key}: {value}\n"

            if entry['verification_notes']:
                report += f"  Verification Notes:\n"
                for note in entry['verification_notes']:
                    report += f"    - {note['verified_by']}: {note['notes']}\n"

            report += "\n"

        with open(output_file, 'w') as f:
            f.write(report)

        print(f"✅ Lawsuit report generated: {output_file}")
        return output_file

    def save_ledger(self, filename="damage_ledger.json"):
        '''Save complete ledger'''

        data = {
            "entries": [
                {**entry, "amount": str(entry["amount"])}
                for entry in self.entries
            ],
            "totals": self.calculate_total_damages(),
            "last_updated": datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Ledger saved: {filename}")


if __name__ == "__main__":
    ledger = DamageLedger()

    # Example entries
    ledger.add_damage(
        category="Unauthorized Bank Charges",
        amount=1234.56,
        description="Fraudulent charge XYZ Merchant",
        receipt="receipts/fraud_001.png",
        bank_statement="statements/jan_2025.pdf",
        transaction="Transaction ID: 12345",
        dispute_email="disputes/fraud_dispute_001.eml"
    )

    ledger.verify_damage(1, "Forensic CPA", "Verified against bank statement")

    totals = ledger.calculate_total_damages()
    print("\nDamage Totals:")
    print(json.dumps(totals, indent=2))

    ledger.generate_lawsuit_report()
    ledger.save_ledger()

    print("\n✅ Damage ledger system ready!")
