#!/usr/bin/env python3
"""
PILLAR 1: FINANCIAL OPERATIONS
Complete financial automation including accounting, budgets, invoices, expenses, and reporting
Part of Agent 5.0 CFO Suite
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3


class TransactionType(Enum):
    """Transaction types"""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    REFUND = "refund"


class InvoiceStatus(Enum):
    """Invoice status"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


@dataclass
class Transaction:
    """Financial transaction"""
    id: Optional[str]
    date: str
    type: str
    category: str
    amount: float
    description: str
    account: str
    reference: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Invoice:
    """Invoice record"""
    id: str
    invoice_number: str
    client_name: str
    client_email: str
    issue_date: str
    due_date: str
    amount: float
    tax_amount: float
    total_amount: float
    status: str
    items: List[Dict[str, Any]]
    payment_terms: str
    notes: Optional[str] = None


@dataclass
class Budget:
    """Budget configuration"""
    id: str
    name: str
    category: str
    period: str  # monthly, quarterly, yearly
    allocated_amount: float
    spent_amount: float
    start_date: str
    end_date: str
    alerts_enabled: bool
    alert_threshold: float  # percentage


class FinancialOperations:
    """
    Complete financial operations management system
    Handles accounting, budgets, invoices, expenses, and financial reporting
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize financial operations"""
        if data_dir is None:
            self.base_dir = Path(__file__).parent
            self.data_dir = self.base_dir / 'data' / 'financial'
        else:
            self.data_dir = data_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.base_dir / 'logs' / 'financial'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self.logger = logging.getLogger('FinancialOps')
        handler = logging.FileHandler(
            self.logs_dir / f'financial_{datetime.now().strftime("%Y%m%d")}.log'
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Initialize database
        self.db_path = self.data_dir / 'financial.db'
        self.init_database()

        # Chart of accounts
        self.accounts = {
            'assets': ['cash', 'bank', 'investments', 'accounts_receivable'],
            'liabilities': ['accounts_payable', 'loans', 'credit_cards'],
            'equity': ['capital', 'retained_earnings'],
            'revenue': ['sales', 'services', 'interest', 'other_income'],
            'expenses': ['salaries', 'rent', 'utilities', 'supplies', 'marketing',
                        'legal', 'software', 'travel', 'insurance', 'taxes']
        }

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                account TEXT NOT NULL,
                reference TEXT,
                tags TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                invoice_number TEXT UNIQUE NOT NULL,
                client_name TEXT NOT NULL,
                client_email TEXT,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                amount REAL NOT NULL,
                tax_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL,
                items TEXT,
                payment_terms TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                period TEXT NOT NULL,
                allocated_amount REAL NOT NULL,
                spent_amount REAL DEFAULT 0,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                alerts_enabled INTEGER DEFAULT 1,
                alert_threshold REAL DEFAULT 80,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        self.logger.info("Database initialized successfully")

    # ==================== TRANSACTION MANAGEMENT ====================

    def add_transaction(self, transaction: Transaction) -> str:
        """Add a new transaction"""
        if transaction.id is None:
            transaction.id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO transactions
            (id, date, type, category, amount, description, account, reference, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.id,
            transaction.date,
            transaction.type,
            transaction.category,
            transaction.amount,
            transaction.description,
            transaction.account,
            transaction.reference,
            json.dumps(transaction.tags) if transaction.tags else None,
            json.dumps(transaction.metadata) if transaction.metadata else None
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Transaction added: {transaction.id} - {transaction.amount}")
        return transaction.id

    def get_transactions(self,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         category: Optional[str] = None,
                         account: Optional[str] = None) -> List[Transaction]:
        """Get transactions with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
        if account:
            query += " AND account = ?"
            params.append(account)

        query += " ORDER BY date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        transactions = []
        for row in rows:
            transactions.append(Transaction(
                id=row[0],
                date=row[1],
                type=row[2],
                category=row[3],
                amount=row[4],
                description=row[5],
                account=row[6],
                reference=row[7],
                tags=json.loads(row[8]) if row[8] else None,
                metadata=json.loads(row[9]) if row[9] else None
            ))

        return transactions

    # ==================== INVOICE MANAGEMENT ====================

    def create_invoice(self, invoice: Invoice) -> str:
        """Create a new invoice"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO invoices
            (id, invoice_number, client_name, client_email, issue_date, due_date,
             amount, tax_amount, total_amount, status, items, payment_terms, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice.id,
            invoice.invoice_number,
            invoice.client_name,
            invoice.client_email,
            invoice.issue_date,
            invoice.due_date,
            invoice.amount,
            invoice.tax_amount,
            invoice.total_amount,
            invoice.status,
            json.dumps(invoice.items),
            invoice.payment_terms,
            invoice.notes
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Invoice created: {invoice.invoice_number} - ${invoice.total_amount}")
        return invoice.id

    def update_invoice_status(self, invoice_id: str, status: InvoiceStatus) -> bool:
        """Update invoice status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE invoices SET status = ? WHERE id = ?",
            (status.value, invoice_id)
        )

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        if updated:
            self.logger.info(f"Invoice {invoice_id} status updated to {status.value}")

        return updated

    def get_overdue_invoices(self) -> List[Invoice]:
        """Get all overdue invoices"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT * FROM invoices WHERE due_date < ? AND status != 'paid'",
            (today,)
        )

        rows = cursor.fetchall()
        conn.close()

        invoices = []
        for row in rows:
            invoices.append(Invoice(
                id=row[0],
                invoice_number=row[1],
                client_name=row[2],
                client_email=row[3],
                issue_date=row[4],
                due_date=row[5],
                amount=row[6],
                tax_amount=row[7],
                total_amount=row[8],
                status=row[9],
                items=json.loads(row[10]),
                payment_terms=row[11],
                notes=row[12]
            ))

        return invoices

    # ==================== BUDGET MANAGEMENT ====================

    def create_budget(self, budget: Budget) -> str:
        """Create a new budget"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO budgets
            (id, name, category, period, allocated_amount, spent_amount,
             start_date, end_date, alerts_enabled, alert_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            budget.id,
            budget.name,
            budget.category,
            budget.period,
            budget.allocated_amount,
            budget.spent_amount,
            budget.start_date,
            budget.end_date,
            1 if budget.alerts_enabled else 0,
            budget.alert_threshold
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Budget created: {budget.name} - ${budget.allocated_amount}")
        return budget.id

    def update_budget_spending(self, budget_id: str, amount: float) -> bool:
        """Update budget spent amount"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE budgets SET spent_amount = spent_amount + ? WHERE id = ?",
            (amount, budget_id)
        )

        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()

        if updated:
            self.logger.info(f"Budget {budget_id} spending updated: +${amount}")

        return updated

    def get_budget_status(self, budget_id: str) -> Optional[Dict[str, Any]]:
        """Get budget status and alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM budgets WHERE id = ?", (budget_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        allocated = row[4]
        spent = row[5]
        threshold = row[9]

        percentage_used = (spent / allocated * 100) if allocated > 0 else 0
        remaining = allocated - spent

        return {
            'budget_id': budget_id,
            'name': row[1],
            'category': row[2],
            'allocated': allocated,
            'spent': spent,
            'remaining': remaining,
            'percentage_used': percentage_used,
            'alert_triggered': percentage_used >= threshold,
            'status': 'exceeded' if spent > allocated else 'on_track'
        }

    # ==================== FINANCIAL REPORTING ====================

    def generate_profit_loss_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate profit and loss statement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get income
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type = 'income' AND date BETWEEN ? AND ?
        ''', (start_date, end_date))
        total_income = cursor.fetchone()[0] or 0

        # Get expenses
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type = 'expense' AND date BETWEEN ? AND ?
        ''', (start_date, end_date))
        total_expenses = cursor.fetchone()[0] or 0

        # Get income by category
        cursor.execute('''
            SELECT category, SUM(amount) FROM transactions
            WHERE type = 'income' AND date BETWEEN ? AND ?
            GROUP BY category
        ''', (start_date, end_date))
        income_breakdown = dict(cursor.fetchall())

        # Get expenses by category
        cursor.execute('''
            SELECT category, SUM(amount) FROM transactions
            WHERE type = 'expense' AND date BETWEEN ? AND ?
            GROUP BY category
        ''', (start_date, end_date))
        expense_breakdown = dict(cursor.fetchall())

        conn.close()

        net_profit = total_income - total_expenses

        return {
            'report_type': 'profit_loss',
            'period': {'start': start_date, 'end': end_date},
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'profit_margin': (net_profit / total_income * 100) if total_income > 0 else 0,
            'income_breakdown': income_breakdown,
            'expense_breakdown': expense_breakdown,
            'generated_at': datetime.now().isoformat()
        }

    def generate_balance_sheet(self) -> Dict[str, Any]:
        """Generate balance sheet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        balance_sheet = {
            'assets': {},
            'liabilities': {},
            'equity': {}
        }

        for account_type in ['assets', 'liabilities', 'equity']:
            cursor.execute(
                "SELECT name, balance FROM accounts WHERE type = ?",
                (account_type,)
            )
            accounts = cursor.fetchall()
            balance_sheet[account_type] = {name: balance for name, balance in accounts}

        conn.close()

        total_assets = sum(balance_sheet['assets'].values())
        total_liabilities = sum(balance_sheet['liabilities'].values())
        total_equity = sum(balance_sheet['equity'].values())

        return {
            'report_type': 'balance_sheet',
            'assets': balance_sheet['assets'],
            'total_assets': total_assets,
            'liabilities': balance_sheet['liabilities'],
            'total_liabilities': total_liabilities,
            'equity': balance_sheet['equity'],
            'total_equity': total_equity,
            'balance_check': total_assets - (total_liabilities + total_equity),
            'generated_at': datetime.now().isoformat()
        }

    def generate_cashflow_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate cash flow statement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Operating activities
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type IN ('income', 'expense') AND date BETWEEN ? AND ?
        ''', (start_date, end_date))
        operating_cashflow = cursor.fetchone()[0] or 0

        # Investing activities
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type = 'investment' AND date BETWEEN ? AND ?
        ''', (start_date, end_date))
        investing_cashflow = cursor.fetchone()[0] or 0

        # Get detailed breakdown
        cursor.execute('''
            SELECT type, category, SUM(amount) FROM transactions
            WHERE date BETWEEN ? AND ?
            GROUP BY type, category
        ''', (start_date, end_date))
        breakdown = cursor.fetchall()

        conn.close()

        return {
            'report_type': 'cashflow',
            'period': {'start': start_date, 'end': end_date},
            'operating_activities': operating_cashflow,
            'investing_activities': investing_cashflow,
            'net_cashflow': operating_cashflow + investing_cashflow,
            'breakdown': [{'type': t, 'category': c, 'amount': a} for t, c, a in breakdown],
            'generated_at': datetime.now().isoformat()
        }

    def get_financial_summary(self) -> Dict[str, Any]:
        """Get comprehensive financial summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Current month
        current_month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        current_month_end = datetime.now().strftime('%Y-%m-%d')

        # Get current month income
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type = 'income' AND date >= ?
        ''', (current_month_start,))
        current_income = cursor.fetchone()[0] or 0

        # Get current month expenses
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE type = 'expense' AND date >= ?
        ''', (current_month_start,))
        current_expenses = cursor.fetchone()[0] or 0

        # Get total accounts receivable
        cursor.execute('''
            SELECT SUM(total_amount) FROM invoices
            WHERE status IN ('sent', 'overdue')
        ''')
        accounts_receivable = cursor.fetchone()[0] or 0

        # Get overdue count
        cursor.execute('''
            SELECT COUNT(*) FROM invoices
            WHERE status = 'overdue'
        ''')
        overdue_count = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'current_month': {
                'income': current_income,
                'expenses': current_expenses,
                'net': current_income - current_expenses
            },
            'accounts_receivable': accounts_receivable,
            'overdue_invoices': overdue_count,
            'summary_date': datetime.now().isoformat()
        }


def main():
    """Demo and testing"""
    print("\n" + "="*70)
    print("PILLAR 1: FINANCIAL OPERATIONS")
    print("="*70 + "\n")

    fin_ops = FinancialOperations()

    # Demo: Add sample transaction
    sample_txn = Transaction(
        id=None,
        date=datetime.now().strftime('%Y-%m-%d'),
        type=TransactionType.INCOME.value,
        category='sales',
        amount=5000.00,
        description='Client payment for services',
        account='bank',
        tags=['client_a', 'consulting']
    )
    txn_id = fin_ops.add_transaction(sample_txn)
    print(f"Sample transaction created: {txn_id}")

    # Demo: Create invoice
    sample_invoice = Invoice(
        id=f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-001",
        client_name="Acme Corporation",
        client_email="billing@acme.com",
        issue_date=datetime.now().strftime('%Y-%m-%d'),
        due_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        amount=10000.00,
        tax_amount=825.00,
        total_amount=10825.00,
        status=InvoiceStatus.SENT.value,
        items=[
            {'description': 'Consulting services', 'quantity': 40, 'rate': 250.00, 'amount': 10000.00}
        ],
        payment_terms="Net 30"
    )
    inv_id = fin_ops.create_invoice(sample_invoice)
    print(f"Sample invoice created: {sample_invoice.invoice_number}")

    # Generate reports
    print("\n" + "-"*70)
    print("FINANCIAL REPORTS")
    print("-"*70)

    summary = fin_ops.get_financial_summary()
    print(f"\nCurrent Month Summary:")
    print(f"  Income: ${summary['current_month']['income']:,.2f}")
    print(f"  Expenses: ${summary['current_month']['expenses']:,.2f}")
    print(f"  Net: ${summary['current_month']['net']:,.2f}")
    print(f"  Accounts Receivable: ${summary['accounts_receivable']:,.2f}")
    print(f"  Overdue Invoices: {summary['overdue_invoices']}")

    print("\n" + "="*70)
    print("Financial Operations Module Ready")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
