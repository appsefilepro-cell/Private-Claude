#!/usr/bin/env python3
"""
Simple Crypto Capital Gains Calculator
Made by Developer AI for Agent 5.0

Simplified version for quick analysis.
"""

import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
)


def parseCsv(filePath: Path) -> List[Dict[str, str]]:
	"""
	Parse a CSV file containing crypto transactions and return
	a list of dictionaries (one per row).

	:param filePath: Path to the CSV file.
	:return: List of row dictionaries.
	"""
	logging.info(f"Reading CSV data from {filePath.resolve()}")
	with filePath.open(newline="", encoding="utf-8-sig") as csvFile:
		reader = csv.DictReader(csvFile)
		rows = [row for row in reader]
	logging.debug(f"Parsed {len(rows)} rows")
	return rows


def calculateGains(rows: List[Dict[str, str]]) -> Tuple[Dict[str, float], float]:
	"""
	Calculate gains per asset and the grand total.

	:param rows: List of parsed CSV rows.
	:return: Tuple containing (assetGains, totalGain).
	"""
	assetGains: Dict[str, float] = defaultdict(float)

	for row in rows:
		assetName = row.get("ASSET NAME", row.get("asset_name", "UNKNOWN")).strip()
		try:
			costBasis = float(row.get("COST BASIS(USD)", row.get("cost_basis", "0")).replace(",", "").replace("$", ""))
			proceeds = float(row.get("PROCEEDS", row.get("proceeds", "0")).replace(",", "").replace("$", ""))
		except ValueError as exc:
			logging.warning(f"Skipping row with invalid numbers: {row} ({exc})")
			continue

		gain = proceeds - costBasis
		assetGains[assetName] += gain
		logging.debug(
			f"{assetName}: Cost={costBasis:.2f} Proceeds={proceeds:.2f} "
			f"Gain={gain:.2f}"
		)

	totalGain = sum(assetGains.values())
	return assetGains, totalGain


def printReport(assetGains: Dict[str, float], totalGain: float) -> None:
	"""
	Print a formatted gain/loss report to stdout.

	:param assetGains: Dictionary with gains per asset.
	:param totalGain: Grand-total gain/loss.
	"""
	print("=" * 40)
	print(" Crypto Capital Gains Report")
	print("=" * 40)
	for asset, gain in sorted(assetGains.items(), key=lambda x: x[1], reverse=True):
		status = "Gain ✅" if gain >= 0 else "Loss ❌"
		print(f"{asset:>4}: {gain:12.2f} USD  ({status})")
	print("-" * 40)
	grandStatus = "Gain ✅" if totalGain >= 0 else "Loss ❌"
	print(f"Total: {totalGain:12.2f} USD  ({grandStatus})")
	print("=" * 40)


def main() -> None:
	"""
	Main entry point. Expects a single argument pointing to the CSV file.
	"""
	if len(sys.argv) != 2:
		logging.error("Usage: python crypto_gains_simple.py <path_to_csv>")
		sys.exit(1)

	filePath = Path(sys.argv[1])
	if not filePath.exists():
		logging.error(f"File not found: {filePath}")
		sys.exit(1)

	rows = parseCsv(filePath)
	assetGains, totalGain = calculateGains(rows)
	printReport(assetGains, totalGain)


if __name__ == "__main__":
	main()
