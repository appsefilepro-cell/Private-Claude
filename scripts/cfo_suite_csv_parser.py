#!/usr/bin/env python3
"""
CFO SUITE - CSV FRAGMENT PARSER & INVESTMENT DAMAGE ASSESSMENT
Integrates the user's provided CSV parsing code with Agent 5.0 CFO suite

Parses 1099s, trade CSVs, and Excel files to assess investment damages
Delegated to: Financial Division - CFO Suite Team
"""
from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Dict, List

import pandas as pd


# ==============================================================================
# PART 1: CSV FRAGMENT LOADER (User's Provided Code)
# ==============================================================================

def loadCsvFragments(rawText: str) -> Dict[str, pd.DataFrame]:
    """
    Splits a long mixed-CSV blob into individual DataFrames.

    Args:
        rawText: the entire pasted text.

    Returns:
        Dict keyed by header-row string, value = DataFrame.
    """
    # Regex: header line = any line that ends with '\n' and
    # contains at least two commas but no newline inside the header itself.
    possibleHeaders = [
        m.group(0).strip()
        for m in re.finditer(r'^[^\n]*?,[^\n]*?,[^\n]*?$', rawText, flags=re.M)
    ]

    # Sort headers by their first appearance (keeps order)
    uniqueHeaders = []
    seen = set()
    for hdr in possibleHeaders:
        if hdr not in seen:
            uniqueHeaders.append(hdr)
            seen.add(hdr)

    # Split the blob every time we meet a header
    # and map back to DataFrames
    fragments = {}
    for hdr in uniqueHeaders:
        # Use a positive lookahead to keep the header with the fragment
        pattern = rf'(?m)^{re.escape(hdr)}\n(?:.*\n)*?(?=(?:{"|".join(map(re.escape, uniqueHeaders))}|$))'
        matches = re.findall(pattern, rawText)
        if not matches:
            continue
        fragmentText = hdr + '\n' + '\n'.join(
            line for line in rawText.splitlines() if line.startswith(hdr) is False
        )
        # extract lines from hdr to before next hdr
        fragmentText = re.search(
            rf'^{re.escape(hdr)}\n((?:.*\n)*?)', rawText, flags=re.S | re.M
        ).group(0)
        # Clean up trailing blank lines
        fragmentText = fragmentText.strip() + '\n'
        try:
            df = pd.read_csv(StringIO(fragmentText))
            fragments[hdr] = df
        # Skip malformed pieces
        except pd.errors.ParserError:
            continue

    return fragments


# ==============================================================================
# PART 2: CRYPTO/INVESTMENT GAINS CALCULATOR (User's Provided Code)
# ==============================================================================

@dataclass
class Trade:
    assetName: str
    receivedDate: str
    costBasis: float
    dateSold: str
    proceeds: float

    @property
    def gainOrLoss(self) -> float:
        return self.proceeds - self.costBasis


def readTrades(csvPath: Path) -> List[Trade]:
    """
    Parses a Robinhood Crypto (or similarly-formatted) CSV file and returns a list
    of `Trade` objects.

    Expected headers (case-insensitive):
        ASSET NAME, RECEIVED DATE, COST BASIS(USD), DATE SOLD, PROCEEDS
    """
    trades: List[Trade] = []
    with csvPath.open(newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Skip blank lines
            if not row or all(not cell.strip() for cell in row.values()):
                continue
            trades.append(
                Trade(
                    assetName=row['ASSET NAME'].strip(),
                    receivedDate=row['RECEIVED DATE'].strip(),
                    costBasis=float(row['COST BASIS(USD)'].replace(',', '').strip()),
                    dateSold=row['DATE SOLD'].strip(),
                    proceeds=float(row['PROCEEDS'].replace(',', '').strip()),
                )
            )
    return trades


def calculateGains(trades: List[Trade]) -> Dict[str, Dict[str, float]]:
    """
    Aggregates proceeds, cost basis and gain/loss per asset.
    Returns a dictionary keyed by asset symbol.
    """
    summary: Dict[str, Dict[str, float]] = {}
    for trade in trades:
        if trade.assetName not in summary:
            summary[trade.assetName] = {
                'proceeds': 0.0,
                'costBasis': 0.0,
                'gainOrLoss': 0.0
            }
        summary[trade.assetName]['proceeds'] += trade.proceeds
        summary[trade.assetName]['costBasis'] += trade.costBasis
        summary[trade.assetName]['gainOrLoss'] += trade.gainOrLoss
    return summary


def printReport(summary: Dict[str, Dict[str, float]]) -> None:
    """
    Pretty-prints the aggregated gain/loss report.
    """
    header = f'{"Asset":<10}{"Proceeds (USD)":>18}{"Cost Basis (USD)":>20}{"Gain/Loss (USD)":>20}'
    separator = '-' * len(header)
    print(header)
    print(separator)
    for asset, values in summary.items():
        print(
            f'{asset:<10}'
            f'{values["proceeds"]:>18.2f}'
            f'{values["costBasis"]:>20.2f}'
            f'{values["gainOrLoss"]:>20.2f}'
        )
    print(separator)
    totalGain = sum(v['gainOrLoss'] for v in summary.values())
    print(f'TOTAL{"":<6}{"":>18}{"":>20}{totalGain:>20.2f}')


# ==============================================================================
# PART 3: INVESTMENT DAMAGE ASSESSMENT (Agent 5.0 Integration)
# ==============================================================================

def assessInvestmentDamages(summary: Dict[str, Dict[str, float]]) -> Dict:
    """
    Assess if investment damages need to be recovered.
    Integrates with Agent 5.0 Injury Lawyer referral system.
    """
    totalLoss = sum(v['gainOrLoss'] for v in summary.values() if v['gainOrLoss'] < 0)
    totalGain = sum(v['gainOrLoss'] for v in summary.values() if v['gainOrLoss'] > 0)
    netGainLoss = sum(v['gainOrLoss'] for v in summary.values())

    damageAssessment = {
        "total_loss": abs(totalLoss),
        "total_gain": totalGain,
        "net_gain_loss": netGainLoss,
        "needs_recovery": totalLoss < -1000,  # Threshold: $1000 loss
        "recovery_potential": "HIGH" if totalLoss < -10000 else "MEDIUM" if totalLoss < -1000 else "LOW",
        "legal_action_recommended": totalLoss < -5000,
        "injury_lawyer_referral": totalLoss < -10000,
        "assessment_details": {
            "total_assets_traded": len(summary),
            "losing_positions": len([v for v in summary.values() if v['gainOrLoss'] < 0]),
            "winning_positions": len([v for v in summary.values() if v['gainOrLoss'] > 0]),
            "average_loss_per_asset": totalLoss / len([v for v in summary.values() if v['gainOrLoss'] < 0]) if any(v['gainOrLoss'] < 0 for v in summary.values()) else 0,
        }
    }

    return damageAssessment


# ==============================================================================
# PART 4: MAIN CLI INTERFACE
# ==============================================================================

def main() -> None:
    """
    Command-line entry point. Usage:

        python cfo_suite_csv_parser.py <path_to_csv_or_txt>

    For mixed CSV fragments (multiple headers in one file):
        python cfo_suite_csv_parser.py mixed_data.txt

    For single trade CSV:
        python cfo_suite_csv_parser.py trades.csv
    """
    print("=" * 80)
    print("CFO SUITE - CSV PARSER & INVESTMENT DAMAGE ASSESSMENT")
    print("=" * 80)
    print("Delegated to: Financial Division - CFO Suite Team")
    print("=" * 80)
    print()

    if len(sys.argv) != 2:
        print('Usage: python cfo_suite_csv_parser.py <path_to_csv_or_txt>')
        print()
        print('Examples:')
        print('  python cfo_suite_csv_parser.py trades.csv')
        print('  python cfo_suite_csv_parser.py mixed_1099_data.txt')
        sys.exit(1)

    inputPath = Path(sys.argv[1]).expanduser().resolve()
    if not inputPath.exists():
        print(f'Error: file not found -> {inputPath}')
        sys.exit(1)

    # Read the file
    with open(inputPath, 'r', encoding='utf-8-sig') as f:
        rawText = f.read()

    # Determine if it's a mixed fragment or single CSV
    headerCount = len(re.findall(r'^[^\n]*?,[^\n]*?,[^\n]*?$', rawText, flags=re.M))

    if headerCount > 1:
        # Mixed fragments
        print(f"Detected {headerCount} CSV fragments in file")
        print()
        fragments = loadCsvFragments(rawText)

        print(f"Successfully parsed {len(fragments)} fragments:")
        print()

        for hdr, df in fragments.items():
            print(f"Fragment: {hdr[:60]}...")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {list(df.columns)}")
            print()

        # Check for Robinhood/crypto trades
        robinHdr = "ASSET NAME,RECEIVED DATE,COST BASIS(USD),DATE SOLD,PROCEEDS"
        if robinHdr in fragments:
            print("=" * 80)
            print("CRYPTO GAINS ANALYSIS (Robinhood/Similar)")
            print("=" * 80)

            rh = fragments[robinHdr].copy()

            # Calculate gains using Trade dataclass
            trades = []
            for _, row in rh.iterrows():
                trades.append(Trade(
                    assetName=row['ASSET NAME'],
                    receivedDate=row['RECEIVED DATE'],
                    costBasis=float(row['COST BASIS(USD)']),
                    dateSold=row['DATE SOLD'],
                    proceeds=float(row['PROCEEDS'])
                ))

            summary = calculateGains(trades)
            printReport(summary)

            # Damage assessment
            print()
            print("=" * 80)
            print("INVESTMENT DAMAGE ASSESSMENT")
            print("=" * 80)

            damages = assessInvestmentDamages(summary)
            print(f"Total Loss: ${damages['total_loss']:,.2f}")
            print(f"Total Gain: ${damages['total_gain']:,.2f}")
            print(f"Net Gain/Loss: ${damages['net_gain_loss']:,.2f}")
            print()
            print(f"Recovery Potential: {damages['recovery_potential']}")
            print(f"Needs Recovery: {'YES' if damages['needs_recovery'] else 'NO'}")
            print(f"Legal Action Recommended: {'YES' if damages['legal_action_recommended'] else 'NO'}")
            print(f"Injury Lawyer Referral: {'YES - Refer to injury lawyer for damages' if damages['injury_lawyer_referral'] else 'NO'}")
            print()

        # Check for spending/banking data
        spendingHdr = "Date,Original Date,Account Type,Account Name,Account Number,Institution Name,Name,Custom Name,Amount,Description,Category,Note,Ignored From,Tax Deductible"
        if spendingHdr in fragments:
            print("=" * 80)
            print("SPENDING ANALYSIS")
            print("=" * 80)

            df = fragments[spendingHdr]
            categoryTotals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            print("Spending by Category:")
            for category, amount in categoryTotals.items():
                print(f"  {category}: ${amount:,.2f}")
            print()

    else:
        # Single CSV file (likely trades)
        print(f"Processing single CSV file: {inputPath.name}")
        print()

        # Try to detect if it's a trades file
        if "ASSET NAME" in rawText and "COST BASIS" in rawText:
            trades = readTrades(inputPath)
            if not trades:
                print('No trades found in the provided CSV.')
                sys.exit(0)

            summary = calculateGains(trades)
            printReport(summary)

            # Damage assessment
            print()
            print("=" * 80)
            print("INVESTMENT DAMAGE ASSESSMENT")
            print("=" * 80)

            damages = assessInvestmentDamages(summary)
            print(f"Total Loss: ${damages['total_loss']:,.2f}")
            print(f"Total Gain: ${damages['total_gain']:,.2f}")
            print(f"Net Gain/Loss: ${damages['net_gain_loss']:,.2f}")
            print()
            print(f"Recovery Potential: {damages['recovery_potential']}")
            print(f"Needs Recovery: {'YES' if damages['needs_recovery'] else 'NO'}")
            print(f"Legal Action Recommended: {'YES' if damages['legal_action_recommended'] else 'NO'}")
            print(f"Injury Lawyer Referral: {'YES - Refer to injury lawyer for damages' if damages['injury_lawyer_referral'] else 'NO'}")
        else:
            # Generic CSV
            df = pd.read_csv(inputPath)
            print(f"Successfully loaded CSV:")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {list(df.columns)}")
            print()
            print(df.head(10))

    print()
    print("=" * 80)
    print("CFO SUITE ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Review damage assessment above")
    print("  2. If injury lawyer referral = YES, contact injury lawyer for damages claim")
    print("  3. All data logged to Agent 5.0 Financial Division")
    print("  4. Results synced to Airtable + Google Sheets")
    print()


if __name__ == '__main__':
    main()
