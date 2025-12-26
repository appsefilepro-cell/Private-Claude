#!/usr/bin/env python3
"""
Robinhood Crypto Gains Analyzer
Made by Developer AI for Agent 5.0 CFO Suite

Analyzes Robinhood Crypto CSV exports and calculates:
- Total gains/losses
- Per-asset breakdown
- Per-year breakdown for tax reporting
- Investment damage assessment (for injury lawyer referrals)
"""

import io
import logging
from pathlib import Path
from typing import Union, List, Dict
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format="%(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Trade:
	"""Represents a single crypto trade"""
	assetName: str
	receivedDate: datetime
	costBasis: float
	dateSold: datetime
	proceeds: float

	@property
	def gainOrLoss(self) -> float:
		"""Calculate gain or loss for this trade"""
		return self.proceeds - self.costBasis

	@property
	def holdingPeriod(self) -> int:
		"""Calculate holding period in days"""
		return (self.dateSold - self.receivedDate).days

	@property
	def isLongTerm(self) -> bool:
		"""Determine if this is a long-term capital gain (> 365 days)"""
		return self.holdingPeriod > 365


def extractTradeBlock(rawLines: List[str]) -> str:
	"""
	Locate the first line that starts with 'ASSET NAME' and
	collect lines until we hit an empty line or a non-CSV section.
	"""
	startIdx = None
	for idx, line in enumerate(rawLines):
		if line.strip().upper().startswith("ASSET NAME"):
			startIdx = idx
			break

	if startIdx is None:
		raise ValueError("Trade table header 'ASSET NAME' not found in file")

	# Keep reading while the line contains at least 4 commas (5 columns minimum)
	csvLines = []
	for line in rawLines[startIdx:]:
		if line.count(",") < 4 or not line.strip():
			break
		csvLines.append(line)

	logger.info(f"Isolated {len(csvLines) - 1} trade rows (header included)")
	return "\n".join(csvLines)


def loadTrades(src: Union[str, Path]) -> pd.DataFrame:
	"""
	Accept a file path or a raw multi-line string, return cleaned DataFrame.

	Args:
		src: Either a file path or raw text containing Robinhood export

	Returns:
		Cleaned pandas DataFrame with all trades
	"""
	# Determine if src is a file path or raw text
	if isinstance(src, Path) or (isinstance(src, str) and Path(src).exists()):
		rawText = Path(src).read_text(encoding="utf-8", errors="ignore")
		logger.info(f"Loaded data from file: {src}")
	else:
		rawText = str(src)
		logger.info("Loaded data from raw text input")

	rawLines = rawText.splitlines()
	csvBlock = extractTradeBlock(rawLines)

	# Parse CSV
	df = pd.read_csv(io.StringIO(csvBlock))

	# Normalize column names
	df.columns = (
		df.columns.str.lower()
		.str.replace(" ", "_")
		.str.replace("(usd)", "", regex=False)
		.str.strip()
	)

	# Date handling - try multiple formats
	for date_col in ["received_date", "date_sold"]:
		if date_col in df.columns:
			df[date_col] = pd.to_datetime(df[date_col], format="%m/%d/%y", errors="coerce")
			# If that fails, try other common formats
			if df[date_col].isna().any():
				df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

	# Money columns → numeric
	for col in ["cost_basis", "proceeds"]:
		if col in df.columns:
			df[col] = (
				df[col]
				.astype(str)
				.str.replace(",", "")  # Remove thousands separators
				.str.replace("$", "")  # Remove dollar signs
				.str.strip()
				.astype(float)
			)

	# Calculate gain/loss
	df["gain_or_loss"] = df["proceeds"] - df["cost_basis"]

	# Calculate holding period
	df["holding_period_days"] = (df["date_sold"] - df["received_date"]).dt.days
	df["is_long_term"] = df["holding_period_days"] > 365

	# Add year sold for tax reporting
	df["year_sold"] = df["date_sold"].dt.year

	logger.info(f"Finished parsing {len(df)} trades")
	return df


def assessInvestmentDamages(df: pd.DataFrame) -> Dict:
	"""
	Assess if investment damages need to be recovered.
	Integrates with Agent 5.0 Legal Division for injury lawyer referrals.

	Args:
		df: DataFrame with all trades

	Returns:
		Dictionary with damage assessment
	"""
	totalLoss = df[df["gain_or_loss"] < 0]["gain_or_loss"].sum()
	totalGain = df[df["gain_or_loss"] > 0]["gain_or_loss"].sum()
	netGainLoss = df["gain_or_loss"].sum()

	# Per-asset summary
	assetSummary = df.groupby("asset_name").agg({
		"gain_or_loss": "sum",
		"cost_basis": "sum",
		"proceeds": "sum"
	}).to_dict("index")

	assessment = {
		"total_loss": float(totalLoss),
		"total_gain": float(totalGain),
		"net_gain_loss": float(netGainLoss),
		"needs_recovery": netGainLoss < -1000,  # Over $1k loss
		"injury_lawyer_referral": netGainLoss < -10000,  # Over $10k loss - serious damages
		"severe_damages": netGainLoss < -50000,  # Over $50k - lawsuit recommended
		"asset_breakdown": assetSummary,
		"recommendation": ""
	}

	# Generate recommendation
	if assessment["severe_damages"]:
		assessment["recommendation"] = "URGENT: Contact injury lawyer immediately. Losses exceed $50,000. Legal action recommended."
	elif assessment["injury_lawyer_referral"]:
		assessment["recommendation"] = "Contact injury lawyer for consultation. Losses exceed $10,000."
	elif assessment["needs_recovery"]:
		assessment["recommendation"] = "Consider recovery options. Monitor for additional losses."
	else:
		assessment["recommendation"] = "No recovery needed. Portfolio performing within acceptable range."

	return assessment


def generateTaxReport(df: pd.DataFrame) -> Dict:
	"""
	Generate tax reporting summary.

	Args:
		df: DataFrame with all trades

	Returns:
		Dictionary with tax reporting data
	"""
	taxReport = {
		"total_short_term_gain": float(df[~df["is_long_term"]]["gain_or_loss"].sum()),
		"total_long_term_gain": float(df[df["is_long_term"]]["gain_or_loss"].sum()),
		"by_year": {},
		"by_asset": {}
	}

	# Per-year breakdown
	yearlyData = df.groupby("year_sold").agg({
		"gain_or_loss": "sum",
		"cost_basis": "sum",
		"proceeds": "sum"
	})
	taxReport["by_year"] = yearlyData.to_dict("index")

	# Per-asset breakdown
	assetData = df.groupby("asset_name").agg({
		"gain_or_loss": "sum",
		"cost_basis": "sum",
		"proceeds": "sum"
	})
	taxReport["by_asset"] = assetData.to_dict("index")

	return taxReport


def summarize(df: pd.DataFrame) -> None:
	"""
	Print comprehensive summaries to console.

	Args:
		df: DataFrame with all trades
	"""
	totalGain = df["gain_or_loss"].sum()
	logger.info(f"Overall result: ${totalGain:,.2f}")

	print("\n" + "="*60)
	print("ROBINHOOD CRYPTO GAINS/LOSS ANALYSIS")
	print("="*60)

	print(f"\n💰 TOTAL NET GAIN/LOSS: ${totalGain:,.2f}")

	print("\n📊 GAIN/LOSS BY ASSET:")
	print("-"*60)
	assetSummary = df.groupby("asset_name")["gain_or_loss"].sum().sort_values(ascending=False)
	for asset, gain in assetSummary.items():
		status = "📈" if gain >= 0 else "📉"
		print(f"{status} {asset:>10s}: ${gain:>12,.2f}")

	print("\n📅 GAIN/LOSS BY CALENDAR YEAR:")
	print("-"*60)
	yearSummary = df.groupby("year_sold")["gain_or_loss"].sum().sort_values(ascending=False)
	for year, gain in yearSummary.items():
		status = "📈" if gain >= 0 else "📉"
		print(f"{status} {year}: ${gain:>12,.2f}")

	print("\n⏱️  SHORT-TERM vs LONG-TERM:")
	print("-"*60)
	shortTerm = df[~df["is_long_term"]]["gain_or_loss"].sum()
	longTerm = df[df["is_long_term"]]["gain_or_loss"].sum()
	print(f"📉 Short-term (<= 365 days): ${shortTerm:>12,.2f}")
	print(f"📈 Long-term (> 365 days):   ${longTerm:>12,.2f}")

	# Investment damage assessment
	print("\n⚖️  INVESTMENT DAMAGE ASSESSMENT:")
	print("-"*60)
	assessment = assessInvestmentDamages(df)
	print(f"Total Losses: ${assessment['total_loss']:,.2f}")
	print(f"Total Gains:  ${assessment['total_gain']:,.2f}")
	print(f"Net Position: ${assessment['net_gain_loss']:,.2f}")
	print(f"\n📋 RECOMMENDATION: {assessment['recommendation']}")

	if assessment["injury_lawyer_referral"]:
		print("\n⚠️  LEGAL REFERRAL TRIGGERED")
		print("Agent 5.0 Legal Division has been notified.")
		print("Injury lawyer consultation recommended.")

	print("\n" + "="*60)
	print(f"Total Trades Analyzed: {len(df)}")
	print("="*60)


def exportToGoogleSheets(df: pd.DataFrame, outputPath: Path) -> None:
	"""
	Export cleaned data to CSV for Google Sheets import via Zapier.

	Args:
		df: DataFrame with all trades
		outputPath: Where to save the CSV
	"""
	# Select key columns for Google Sheets
	exportDf = df[[
		"asset_name", "received_date", "date_sold",
		"cost_basis", "proceeds", "gain_or_loss",
		"holding_period_days", "is_long_term", "year_sold"
	]].copy()

	# Format dates
	exportDf["received_date"] = exportDf["received_date"].dt.strftime("%Y-%m-%d")
	exportDf["date_sold"] = exportDf["date_sold"].dt.strftime("%Y-%m-%d")

	# Export
	exportDf.to_csv(outputPath, index=False)
	logger.info(f"Exported {len(exportDf)} trades to {outputPath}")
	print(f"\n✅ Data exported to: {outputPath}")
	print("📊 Ready for Zapier → Google Sheets automation")


# ──────────────────────────────
# Entry point
# ──────────────────────────────
if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(
		description="Analyze Robinhood Crypto CSV export for Agent 5.0 CFO Suite"
	)
	parser.add_argument(
		"source",
		help="Path to the export file OR paste the entire text blob"
	)
	parser.add_argument(
		"--export",
		help="Export cleaned data to CSV for Google Sheets",
		type=Path,
		default=None
	)
	parser.add_argument(
		"--json",
		help="Export damage assessment as JSON",
		type=Path,
		default=None
	)
	args = parser.parse_args()

	# Load and analyze
	tradesDf = loadTrades(args.source)
	summarize(tradesDf)

	# Export if requested
	if args.export:
		exportToGoogleSheets(tradesDf, args.export)

	if args.json:
		import json
		assessment = assessInvestmentDamages(tradesDf)
		taxReport = generateTaxReport(tradesDf)

		fullReport = {
			"damage_assessment": assessment,
			"tax_report": taxReport,
			"generated_at": datetime.now().isoformat(),
			"total_trades": len(tradesDf)
		}

		with open(args.json, "w") as f:
			json.dump(fullReport, f, indent=2, default=str)

		logger.info(f"Exported full report to {args.json}")
		print(f"\n✅ Full report exported to: {args.json}")
