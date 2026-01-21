#!/usr/bin/env python3
'''
SCREENSHOT EVIDENCE PROCESSOR
==============================
Processes 80,000 screenshots to extract:
- Receipts
- Bank statements
- Transaction history
- Email disputes
- Evidence photos
'''

import os
from pathlib import Path
from datetime import datetime
import json
import shutil

class ScreenshotProcessor:
    def __init__(self, source_folder="screenshots", output_folder="organized_exhibits"):
        self.source = Path(source_folder)
        self.output = Path(output_folder)
        self.categories = {
            "receipts": [],
            "bank_statements": [],
            "transactions": [],
            "email_disputes": [],
            "evidence_photos": [],
            "uncategorized": []
        }

    def organize_screenshots(self):
        '''Organize 80K screenshots into exhibit folders'''

        print(f"🔍 Scanning screenshots folder...")

        if not self.source.exists():
            print(f"⚠️  Create folder: {self.source}")
            print(f"   Move your 80,000 screenshots there")
            self.source.mkdir(parents=True, exist_ok=True)
            return

        # Create output structure
        for category in self.categories.keys():
            (self.output / category).mkdir(parents=True, exist_ok=True)

        # Process files
        screenshots = list(self.source.glob("**/*.*"))
        total = len(screenshots)

        print(f"📊 Found {total} files to process")

        for i, file in enumerate(screenshots, 1):
            if i % 1000 == 0:
                print(f"   Progress: {i}/{total} ({i/total*100:.1f}%)")

            # Categorize by filename/metadata
            category = self._categorize_file(file)

            # Copy to organized folder
            dest = self.output / category / file.name
            try:
                shutil.copy2(file, dest)
                self.categories[category].append({
                    "original": str(file),
                    "organized": str(dest),
                    "date": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
            except Exception as e:
                print(f"   ⚠️  Error copying {file.name}: {e}")

        # Save organization report
        report = {
            "total_files": total,
            "processed": datetime.now().isoformat(),
            "categories": {k: len(v) for k, v in self.categories.items()},
            "files": self.categories
        }

        with open(self.output / "organization_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Organization complete!")
        print(f"   Output: {self.output}")
        print(f"   Report: {self.output}/organization_report.json")

        for category, files in self.categories.items():
            print(f"   {category}: {len(files)} files")

    def _categorize_file(self, file: Path) -> str:
        '''Categorize file based on name and content'''
        name_lower = file.name.lower()

        # Keyword matching
        if any(word in name_lower for word in ["receipt", "invoice", "bill"]):
            return "receipts"
        elif any(word in name_lower for word in ["bank", "statement", "account"]):
            return "bank_statements"
        elif any(word in name_lower for word in ["transaction", "payment", "transfer"]):
            return "transactions"
        elif any(word in name_lower for word in ["email", "dispute", "complaint", "sent"]):
            return "email_disputes"
        elif any(word in name_lower for word in ["photo", "evidence", "screenshot"]):
            return "evidence_photos"
        else:
            return "uncategorized"


if __name__ == "__main__":
    processor = ScreenshotProcessor()
    processor.organize_screenshots()
    print("\n🎉 Ready for exhibit creation!")
