#!/usr/bin/env python3
"""
Download IRS forms using Python requests library
Alternative to curl when network restrictions exist
"""
import os
import requests
from pathlib import Path

# Create directory
os.makedirs("data/legal_documents/irs_forms", exist_ok=True)

irs_forms = {
    "Form_1023-EZ.pdf": "https://www.irs.gov/pub/irs-pdf/f1023ez.pdf",
    "Form_1023.pdf": "https://www.irs.gov/pub/irs-pdf/f1023.pdf",
    "Form_990.pdf": "https://www.irs.gov/pub/irs-pdf/f990.pdf",
    "Form_990-EZ.pdf": "https://www.irs.gov/pub/irs-pdf/f990ez.pdf",
    "Form_W-9.pdf": "https://www.irs.gov/pub/irs-pdf/fw9.pdf",
    "Form_SS-4.pdf": "https://www.irs.gov/pub/irs-pdf/fss4.pdf"
}

print("=" * 80)
print("IRS FORMS DOWNLOAD (Python Requests)")
print("=" * 80)

success_count = 0
fail_count = 0

for filename, url in irs_forms.items():
    try:
        print(f"\nDownloading {filename}...")

        # Try to download with timeout
        response = requests.get(url, timeout=30, allow_redirects=True)

        if response.status_code == 200:
            filepath = f"data/legal_documents/irs_forms/{filename}"
            with open(filepath, 'wb') as f:
                f.write(response.content)

            size_kb = len(response.content) / 1024
            print(f"  SUCCESS: {filename} ({size_kb:.1f} KB)")
            success_count += 1
        else:
            print(f"  FAILED: {filename} (HTTP {response.status_code})")
            fail_count += 1

    except requests.exceptions.RequestException as e:
        print(f"  ERROR: {filename} - {str(e)[:100]}")
        fail_count += 1
    except Exception as e:
        print(f"  UNEXPECTED ERROR: {filename} - {str(e)[:100]}")
        fail_count += 1

print("\n" + "=" * 80)
print(f"DOWNLOAD SUMMARY")
print("=" * 80)
print(f"Success: {success_count}/{len(irs_forms)}")
print(f"Failed:  {fail_count}/{len(irs_forms)}")
print("=" * 80)
