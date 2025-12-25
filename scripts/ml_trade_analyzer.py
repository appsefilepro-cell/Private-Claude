#!/usr/bin/env python3
"""
Machine Learning Trade Analyzer
Analyzes winning trades and adapts trading strategies
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLTradeAnalyzer:
    """Machine Learning analyzer for trading patterns"""

    def __init__(self, data_path: str = '/home/user/Private-Claude'):
        self.data_path = data_path
        self.mt5_learning_file = os.path.join(data_path, 'mt5_ml_learning.json')
        self.okx_learning_file = os.path.join(data_path, 'okx_ml_learning.json')
        self.model_file = os.path.join(data_path, 'trade_ml_model.pkl')
        self.scaler_file = os.path.join(data_path, 'trade_scaler.pkl')

        self.model = None
        self.scaler = None
        self.trade_data = []
        self.winning_patterns = {}

        self.load_all_data()

    def load_all_data(self):
        """Load trading data from all sources"""
        logger.info("Loading ML training data...")

        # Load MT5 learning data
        if os.path.exists(self.mt5_learning_file):
            try:
                with open(self.mt5_learning_file, 'r') as f:
                    mt5_data = json.load(f)
                    self.merge_learning_data(mt5_data, 'MT5')
                logger.info("Loaded MT5 learning data")
            except Exception as e:
                logger.error(f"Error loading MT5 data: {e}")

        # Load OKX learning data
        if os.path.exists(self.okx_learning_file):
            try:
                with open(self.okx_learning_file, 'r') as f:
                    okx_data = json.load(f)
                    self.merge_learning_data(okx_data, 'OKX')
                logger.info("Loaded OKX learning data")
            except Exception as e:
                logger.error(f"Error loading OKX data: {e}")

        # Load existing model if available
        self.load_model()

    def merge_learning_data(self, data: Dict, source: str):
        """Merge learning data from different sources"""
        winning_patterns = data.get('winning_patterns', {})

        for symbol, pattern_data in winning_patterns.items():
            key = f"{source}_{symbol}"
            self.winning_patterns[key] = {
                'source': source,
                'symbol': symbol,
                'count': pattern_data.get('count', 0),
                'total_profit': pattern_data.get('total_profit', 0),
                'avg_profit': pattern_data.get('avg_profit', 0),
                'success_rate': pattern_data.get('success_rate', 0)
            }

    def extract_features_from_patterns(self) -> pd.DataFrame:
        """Extract features from winning patterns for ML training"""
        if not self.winning_patterns:
            logger.warning("No pattern data available for training")
            return pd.DataFrame()

        features_list = []

        for key, pattern in self.winning_patterns.items():
            feature = {
                'source_mt5': 1 if pattern['source'] == 'MT5' else 0,
                'source_okx': 1 if pattern['source'] == 'OKX' else 0,
                'trade_count': pattern['count'],
                'avg_profit': pattern['avg_profit'],
                'total_profit': pattern['total_profit'],
                'success_rate': pattern.get('success_rate', 0),
                'is_winner': 1 if pattern['avg_profit'] > 0 else 0
            }
            features_list.append(feature)

        df = pd.DataFrame(features_list)
        return df

    def train_model(self):
        """Train ML model on winning patterns"""
        logger.info("Training ML model on trading patterns...")

        df = self.extract_features_from_patterns()

        if df.empty or len(df) < 10:
            logger.warning("Not enough data to train model (need at least 10 samples)")
            return False

        # Prepare features and labels
        X = df.drop('is_winner', axis=1)
        y = df['is_winner']

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

        self.model.fit(X_scaled, y)

        # Calculate accuracy
        accuracy = self.model.score(X_scaled, y)
        logger.info(f"Model trained with accuracy: {accuracy:.2%}")

        # Save model
        self.save_model()

        return True

    def save_model(self):
        """Save trained model to file"""
        try:
            with open(self.model_file, 'wb') as f:
                pickle.dump(self.model, f)

            with open(self.scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)

            logger.info("ML model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def load_model(self):
        """Load trained model from file"""
        try:
            if os.path.exists(self.model_file) and os.path.exists(self.scaler_file):
                with open(self.model_file, 'rb') as f:
                    self.model = pickle.load(f)

                with open(self.scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)

                logger.info("ML model loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")

        return False

    def predict_trade_success(self, features: Dict) -> float:
        """Predict probability of trade success"""
        if self.model is None or self.scaler is None:
            logger.warning("Model not trained - training now...")
            if not self.train_model():
                return 0.5  # Default probability

        # Prepare features
        feature_vector = np.array([[
            features.get('source_mt5', 0),
            features.get('source_okx', 0),
            features.get('trade_count', 0),
            features.get('avg_profit', 0),
            features.get('total_profit', 0),
            features.get('success_rate', 0)
        ]])

        # Scale and predict
        feature_scaled = self.scaler.transform(feature_vector)
        probability = self.model.predict_proba(feature_scaled)[0][1]

        return probability

    def get_best_performing_symbols(self, top_n: int = 10) -> List[Dict]:
        """Get top performing symbols based on ML analysis"""
        if not self.winning_patterns:
            return []

        # Sort by average profit
        sorted_patterns = sorted(
            self.winning_patterns.items(),
            key=lambda x: x[1]['avg_profit'],
            reverse=True
        )

        best_symbols = []
        for key, pattern in sorted_patterns[:top_n]:
            best_symbols.append({
                'symbol': pattern['symbol'],
                'source': pattern['source'],
                'avg_profit': pattern['avg_profit'],
                'count': pattern['count'],
                'success_rate': pattern.get('success_rate', 0)
            })

        return best_symbols

    def get_recommendations(self) -> Dict:
        """Get trading recommendations based on ML analysis"""
        recommendations = {
            'best_symbols': self.get_best_performing_symbols(top_n=10),
            'total_patterns_analyzed': len(self.winning_patterns),
            'model_trained': self.model is not None,
            'timestamp': datetime.now().isoformat()
        }

        # Calculate overall statistics
        if self.winning_patterns:
            total_profit = sum(p['total_profit'] for p in self.winning_patterns.values())
            total_trades = sum(p['count'] for p in self.winning_patterns.values())
            avg_profit = total_profit / total_trades if total_trades > 0 else 0

            recommendations['overall_stats'] = {
                'total_profit': total_profit,
                'total_trades': total_trades,
                'average_profit_per_trade': avg_profit
            }

        return recommendations

    def generate_report(self) -> str:
        """Generate ML analysis report"""
        recommendations = self.get_recommendations()

        report = []
        report.append("=" * 60)
        report.append("MACHINE LEARNING TRADE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Total Patterns Analyzed: {recommendations['total_patterns_analyzed']}")
        report.append(f"Model Trained: {'Yes' if recommendations['model_trained'] else 'No'}")

        if 'overall_stats' in recommendations:
            stats = recommendations['overall_stats']
            report.append(f"\nOverall Statistics:")
            report.append(f"  Total Trades: {stats['total_trades']}")
            report.append(f"  Total Profit: ${stats['total_profit']:.2f}")
            report.append(f"  Average Profit/Trade: ${stats['average_profit_per_trade']:.2f}")

        report.append(f"\nTop 10 Best Performing Symbols:")
        for i, symbol_data in enumerate(recommendations['best_symbols'], 1):
            report.append(f"{i}. {symbol_data['symbol']} ({symbol_data['source']})")
            report.append(f"   Avg Profit: ${symbol_data['avg_profit']:.2f}, Trades: {symbol_data['count']}")

        report.append("=" * 60)

        report_text = "\n".join(report)
        logger.info(report_text)

        # Save report to file
        report_file = os.path.join(self.data_path, 'ml_analysis_report.txt')
        with open(report_file, 'w') as f:
            f.write(report_text)

        return report_text

    def continuous_learning(self, interval_minutes: int = 60):
        """Continuously analyze and retrain model"""
        import time

        logger.info(f"Starting continuous learning (retraining every {interval_minutes} minutes)...")

        while True:
            try:
                # Reload data
                self.load_all_data()

                # Retrain model
                if len(self.winning_patterns) >= 10:
                    self.train_model()
                    self.generate_report()
                else:
                    logger.info(f"Not enough data yet ({len(self.winning_patterns)} patterns, need 10)")

                # Wait
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("Stopping continuous learning...")
                break
            except Exception as e:
                logger.error(f"Error in continuous learning: {e}")
                time.sleep(60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='ML Trade Analyzer')
    parser.add_argument('--train', action='store_true', help='Train model')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--continuous', action='store_true', help='Continuous learning mode')
    parser.add_argument('--interval', type=int, default=60, help='Retraining interval (minutes)')
    args = parser.parse_args()

    analyzer = MLTradeAnalyzer()

    if args.train:
        analyzer.train_model()

    if args.report:
        analyzer.generate_report()

    if args.continuous:
        analyzer.continuous_learning(interval_minutes=args.interval)

    if not (args.train or args.report or args.continuous):
        # Default: generate report
        analyzer.generate_report()


if __name__ == "__main__":
    main()
