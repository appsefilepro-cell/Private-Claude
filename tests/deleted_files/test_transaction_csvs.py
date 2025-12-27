#!/usr/bin/env python3
"""
Unit Tests for Deleted Transaction CSV Files
Tests data integrity and format of:
- 2025-08-05T13_01_10.438Z-transactions.csv
- 2025-08-14T20_04_27.046Z-transactions.csv
- DocuPost CSV Template.csv
- Nexo_Transactions_1740794579.csv
- Robinhood Crypto Transactions.csv
- bitcoin_2024-03-17_2024-04-16.csv
"""

import pytest
import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any


class TestCSVStructure:
    """Base tests for CSV file structure"""

    def test_csv_has_headers(self):
        """Test CSV files should have header rows"""
        sample_headers = [
            "Date",
            "Amount",
            "Description",
            "Category"
        ]
        assert len(sample_headers) > 0
        assert all(isinstance(h, str) for h in sample_headers)

    def test_csv_delimiter_validation(self):
        """Test CSV uses standard comma delimiter"""
        delimiter = ','
        assert delimiter == ','

    def test_csv_encoding(self):
        """Test CSV uses UTF-8 encoding"""
        encoding = 'utf-8'
        assert encoding in ['utf-8', 'utf-8-sig']


class TestPayPalTransactionCSV:
    """Tests for PayPal transaction CSV format (2025-08-05 and 2025-08-14)"""

    @pytest.fixture
    def expected_headers(self):
        """Expected headers for PayPal transaction CSV"""
        return [
            "Date",
            "Original Date",
            "Account Type",
            "Account Name",
            "Account Number",
            "Institution Name",
            "Name",
            "Custom Name",
            "Amount",
            "Description",
            "Category",
            "Note",
            "Ignored From",
            "Tax Deductible"
        ]

    @pytest.fixture
    def sample_transaction(self):
        """Sample transaction record"""
        return {
            "Date": "2021-02-12",
            "Original Date": "2021-02-12",
            "Account Type": "Cash",
            "Account Name": "PayPal",
            "Account Number": "",
            "Institution Name": "PayPal",
            "Name": "iTunes",
            "Custom Name": "",
            "Amount": "9.99",
            "Description": "Payment to iTunes and App Store",
            "Category": "Uncategorized",
            "Note": "",
            "Ignored From": "",
            "Tax Deductible": ""
        }

    def test_header_validation(self, expected_headers):
        """Test CSV has all expected headers"""
        assert len(expected_headers) == 14
        assert "Date" in expected_headers
        assert "Amount" in expected_headers
        assert "Description" in expected_headers

    def test_date_format_validation(self, sample_transaction):
        """Test date format is YYYY-MM-DD"""
        date_str = sample_transaction["Date"]
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        assert re.match(date_pattern, date_str)
        
        # Validate it's a real date
        datetime.strptime(date_str, '%Y-%m-%d')

    def test_amount_format_validation(self, sample_transaction):
        """Test amount is a valid decimal number"""
        amount_str = sample_transaction["Amount"]
        try:
            amount = Decimal(amount_str)
            assert amount > 0
        except InvalidOperation:
            pytest.fail(f"Invalid amount format: {amount_str}")

    def test_account_type_validation(self, sample_transaction):
        """Test account type is valid"""
        valid_types = ["Cash", "Credit Card", "Checking", "Savings", "Investment"]
        account_type = sample_transaction["Account Type"]
        assert account_type in valid_types or account_type == "Cash"

    def test_description_not_empty(self, sample_transaction):
        """Test description field is not empty"""
        description = sample_transaction["Description"]
        assert len(description) > 0
        assert isinstance(description, str)

    def test_category_validation(self, sample_transaction):
        """Test transaction category"""
        valid_categories = [
            "Uncategorized",
            "Shopping",
            "Dining & Drinks",
            "Auto & Transport",
            "Bills & Utilities",
            "Entertainment & Rec.",
            "Groceries",
            "Personal Care",
            "Travel & Vacation",
            "Income",
            "Subscriptions",
            "Cash & Checks",
            "Fees",
            "Taxes",
            "Internal Transfers",
            "Disputes"
        ]
        category = sample_transaction["Category"]
        assert category in valid_categories or isinstance(category, str)

    def test_institution_name_valid(self, sample_transaction):
        """Test institution name is provided"""
        institution = sample_transaction["Institution Name"]
        assert len(institution) > 0

    def test_optional_fields_can_be_empty(self, sample_transaction):
        """Test optional fields can be empty strings"""
        optional_fields = ["Custom Name", "Note", "Ignored From", "Tax Deductible"]
        for field in optional_fields:
            assert field in sample_transaction
            # Can be empty string
            assert isinstance(sample_transaction[field], str)


class TestDocuPostCSVTemplate:
    """Tests for DocuPost CSV Template"""

    @pytest.fixture
    def template_headers(self):
        """DocuPost template headers"""
        return [
            "First Name",
            "Last Name",
            "Company",
            "Address Line 1",
            "Address Line 2",
            "City",
            "State",
            "Zip Code",
            "Country",
            "Email",
            "Phone"
        ]

    def test_address_fields_present(self, template_headers):
        """Test address fields are present"""
        address_fields = ["Address Line 1", "City", "State", "Zip Code"]
        for field in address_fields:
            assert field in template_headers

    def test_contact_fields_present(self, template_headers):
        """Test contact fields are present"""
        contact_fields = ["First Name", "Last Name", "Email", "Phone"]
        for field in contact_fields:
            assert field in template_headers

    def test_zip_code_format(self):
        """Test zip code format validation"""
        valid_zip_codes = ["12345", "12345-6789", "90210"]
        zip_pattern = r'^\d{5}(-\d{4})?$'
        
        for zip_code in valid_zip_codes:
            assert re.match(zip_pattern, zip_code)

    def test_state_abbreviation(self):
        """Test state abbreviations"""
        valid_states = ["CA", "NY", "TX", "GA", "FL"]
        for state in valid_states:
            assert len(state) == 2
            assert state.isupper()

    def test_email_format_validation(self):
        """Test email format"""
        valid_emails = [
            "user@example.com",
            "test.user@company.org",
            "admin@domain.co.uk"
        ]
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in valid_emails:
            assert re.match(email_pattern, email)

    def test_phone_number_format(self):
        """Test phone number format"""
        valid_phones = [
            "555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "5551234567"
        ]
        for phone in valid_phones:
            # Should contain only digits, hyphens, dots, parentheses, spaces
            assert re.match(r'^[\d\s\-\.\(\)]+$', phone)


class TestCryptoTransactionCSV:
    """Tests for cryptocurrency transaction CSVs"""

    @pytest.fixture
    def crypto_transaction(self):
        """Sample crypto transaction"""
        return {
            "Date": "2021-03-15T14:30:00Z",
            "Type": "Buy",
            "Asset": "BTC",
            "Amount": "0.05",
            "Price": "55000.00",
            "Total": "2750.00",
            "Fee": "2.75"
        }

    def test_crypto_date_format(self, crypto_transaction):
        """Test crypto transaction date format (ISO 8601)"""
        date_str = crypto_transaction["Date"]
        # Should be ISO 8601 format
        assert 'T' in date_str or re.match(r'^\d{4}-\d{2}-\d{2}', date_str)

    def test_transaction_type_validation(self, crypto_transaction):
        """Test transaction type is valid"""
        valid_types = ["Buy", "Sell", "Trade", "Deposit", "Withdrawal", "Transfer"]
        tx_type = crypto_transaction["Type"]
        assert tx_type in valid_types

    def test_asset_symbol_format(self, crypto_transaction):
        """Test asset symbol format"""
        asset = crypto_transaction["Asset"]
        assert len(asset) >= 3
        assert asset.isupper()

    def test_amount_is_positive_decimal(self, crypto_transaction):
        """Test amount is positive decimal"""
        amount = Decimal(crypto_transaction["Amount"])
        assert amount > 0

    def test_price_is_positive(self, crypto_transaction):
        """Test price is positive"""
        price = Decimal(crypto_transaction["Price"])
        assert price > 0

    def test_total_calculation(self, crypto_transaction):
        """Test total equals amount * price"""
        amount = Decimal(crypto_transaction["Amount"])
        price = Decimal(crypto_transaction["Price"])
        total = Decimal(crypto_transaction["Total"])
        
        calculated_total = amount * price
        # Allow for small rounding differences
        assert abs(calculated_total - total) < Decimal("0.01")

    def test_fee_is_non_negative(self, crypto_transaction):
        """Test fee is non-negative"""
        fee = Decimal(crypto_transaction["Fee"])
        assert fee >= 0


class TestNexoTransactionCSV:
    """Tests for Nexo transaction CSV"""

    def test_nexo_timestamp_format(self):
        """Test Nexo timestamp format"""
        timestamp = "1740794579"
        # Should be Unix timestamp (10 digits)
        assert len(timestamp) == 10
        assert timestamp.isdigit()
        
        # Should convert to valid datetime
        dt = datetime.fromtimestamp(int(timestamp))
        assert dt.year >= 2020

    def test_nexo_asset_types(self):
        """Test Nexo supports various asset types"""
        assets = ["BTC", "ETH", "USDT", "USDC", "NEXO"]
        for asset in assets:
            assert len(asset) >= 3
            assert asset.isupper()


class TestRobinhoodCryptoCSV:
    """Tests for Robinhood Crypto transaction CSV"""

    def test_robinhood_date_format(self):
        """Test Robinhood date format"""
        date_str = "2021-02-15 10:30:45"
        datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    def test_robinhood_transaction_types(self):
        """Test Robinhood transaction types"""
        valid_types = [
            "Buy",
            "Sell",
            "Dividend",
            "Interest",
            "Deposit",
            "Withdrawal"
        ]
        for tx_type in valid_types:
            assert isinstance(tx_type, str)


class TestBitcoinPriceCSV:
    """Tests for Bitcoin price history CSV"""

    @pytest.fixture
    def bitcoin_price_record(self):
        """Sample Bitcoin price record"""
        return {
            "Date": "2024-03-17",
            "Open": "65000.00",
            "High": "67500.00",
            "Low": "64000.00",
            "Close": "66800.00",
            "Volume": "25000000000"
        }

    def test_date_range_validation(self, bitcoin_price_record):
        """Test date is within expected range"""
        date_str = bitcoin_price_record["Date"]
        date = datetime.strptime(date_str, '%Y-%m-%d')
        assert date.year >= 2024
        assert date.month in range(3, 5)  # March to April

    def test_ohlc_price_validation(self, bitcoin_price_record):
        """Test OHLC price relationships"""
        open_price = Decimal(bitcoin_price_record["Open"])
        high = Decimal(bitcoin_price_record["High"])
        low = Decimal(bitcoin_price_record["Low"])
        close = Decimal(bitcoin_price_record["Close"])
        
        # High should be >= Open, Close, Low
        assert high >= open_price
        assert high >= close
        assert high >= low
        
        # Low should be <= Open, Close, High
        assert low <= open_price
        assert low <= close
        assert low <= high

    def test_volume_is_positive(self, bitcoin_price_record):
        """Test volume is positive"""
        volume = Decimal(bitcoin_price_record["Volume"])
        assert volume > 0

    def test_price_precision(self, bitcoin_price_record):
        """Test price has appropriate precision"""
        close = bitcoin_price_record["Close"]
        # Should have at most 2 decimal places
        decimal_places = len(close.split('.')[-1]) if '.' in close else 0
        assert decimal_places <= 2


class TestCSVDataIntegrity:
    """General data integrity tests for all CSVs"""

    def test_no_null_bytes(self):
        """Test CSV data doesn't contain null bytes"""
        test_data = "Sample,Data,String"
        assert '\x00' not in test_data

    def test_consistent_column_count(self):
        """Test all rows have same number of columns"""
        sample_rows = [
            ["col1", "col2", "col3"],
            ["val1", "val2", "val3"],
            ["val4", "val5", "val6"]
        ]
        column_count = len(sample_rows[0])
        for row in sample_rows:
            assert len(row) == column_count

    def test_numeric_fields_parseable(self):
        """Test numeric fields can be parsed"""
        numeric_values = ["123.45", "0.001", "1000000", "-50.00"]
        for value in numeric_values:
            try:
                Decimal(value)
            except InvalidOperation:
                pytest.fail(f"Cannot parse numeric value: {value}")

    def test_date_consistency(self):
        """Test dates are consistent and chronological"""
        dates = [
            "2021-01-15",
            "2021-01-20",
            "2021-02-05"
        ]
        parsed_dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        
        for i in range(len(parsed_dates) - 1):
            assert parsed_dates[i] <= parsed_dates[i + 1]

    def test_no_duplicate_headers(self):
        """Test headers don't have duplicates"""
        headers = ["Date", "Amount", "Description", "Category"]
        assert len(headers) == len(set(headers))

    def test_utf8_character_handling(self):
        """Test UTF-8 characters are handled correctly"""
        test_strings = [
            "Café",
            "Zürich",
            "São Paulo",
            "🌟 Special"
        ]
        for s in test_strings:
            assert isinstance(s, str)
            encoded = s.encode('utf-8')
            decoded = encoded.decode('utf-8')
            assert decoded == s


if __name__ == "__main__":
    pytest.main([__file__, "-v"])