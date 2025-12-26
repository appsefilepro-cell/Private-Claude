"""
COMPLETE TEST SUITE FOR BINANCE LIVE TRADER
Comprehensive pytest tests with mocking
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pillar_a_trading.crypto.binance_live_trader import BinanceLiveTrader, SIDE_BUY, SIDE_SELL


@pytest.fixture
def trader():
    """Create trader instance for testing"""
    return BinanceLiveTrader(
        api_key="test_key",
        api_secret="test_secret",
        testnet=True
    )


@pytest.mark.asyncio
async def test_get_account_balance_success(trader):
    """Test successful balance retrieval"""
    with patch.object(trader.client, 'get_account') as mock_account:
        mock_account.return_value = {
            'balances': [
                {'asset': 'BTC', 'free': '1.5', 'locked': '0'},
                {'asset': 'USDT', 'free': '10000.0', 'locked': '0'},
                {'asset': 'ETH', 'free': '0', 'locked': '0'}
            ]
        }

        balance = await trader.get_account_balance()

        assert 'BTC' in balance
        assert balance['BTC'] == 1.5
        assert 'USDT' in balance
        assert balance['USDT'] == 10000.0
        assert 'ETH' not in balance  # Zero balance excluded


@pytest.mark.asyncio
async def test_execute_market_order_buy(trader):
    """Test market buy order"""
    with patch.object(trader.client, 'create_order') as mock_order:
        mock_order.return_value = {
            'orderId': 12345,
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'executedQty': '0.1',
            'status': 'FILLED'
        }

        order = await trader.execute_market_order('BTCUSDT', SIDE_BUY, 0.1)

        assert order is not None
        assert order['orderId'] == 12345
        assert order['symbol'] == 'BTCUSDT'
        assert trader.orders[12345] == order


@pytest.mark.asyncio
async def test_execute_market_order_failure(trader):
    """Test failed market order"""
    with patch.object(trader.client, 'create_order') as mock_order:
        mock_order.side_effect = Exception("Insufficient balance")

        order = await trader.execute_market_order('BTCUSDT', SIDE_BUY, 10.0)

        assert order is None


@pytest.mark.asyncio
async def test_execute_limit_order(trader):
    """Test limit order placement"""
    with patch.object(trader.client, 'create_order') as mock_order:
        mock_order.return_value = {
            'orderId': 12346,
            'symbol': 'ETHUSDT',
            'side': 'SELL',
            'type': 'LIMIT',
            'price': '2000.0',
            'executedQty': '1.0',
            'status': 'NEW'
        }

        order = await trader.execute_limit_order('ETHUSDT', SIDE_SELL, 1.0, 2000.0)

        assert order is not None
        assert order['type'] == 'LIMIT'
        assert float(order['price']) == 2000.0


def test_calculate_position_size(trader):
    """Test position size calculation"""
    balance = 10000.0
    entry_price = 50000.0
    stop_loss_price = 49000.0

    position_size = trader.calculate_position_size(balance, entry_price, stop_loss_price)

    # Risk = 10000 * 0.02 = 200
    # Price diff = 1000
    # Position = 200 / 1000 = 0.2
    assert position_size == pytest.approx(0.2)


def test_calculate_position_size_different_risk(trader):
    """Test position size with different risk percentage"""
    trader.risk_percent = 0.01  # 1% risk

    balance = 5000.0
    entry_price = 1000.0
    stop_loss_price = 950.0

    position_size = trader.calculate_position_size(balance, entry_price, stop_loss_price)

    # Risk = 5000 * 0.01 = 50
    # Price diff = 50
    # Position = 50 / 50 = 1.0
    assert position_size == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_rebalance_portfolio(trader):
    """Test portfolio rebalancing"""
    with patch.object(trader, 'get_account_balance') as mock_balance, \
         patch.object(trader, 'execute_market_order') as mock_order:

        mock_balance.return_value = {'BTC': 6000.0, 'ETH': 4000.0}  # Total: 10000
        mock_order.return_value = {'orderId': 999, 'status': 'FILLED'}

        target_allocation = {'BTC': 0.5, 'ETH': 0.5}  # 50/50

        await trader.rebalance_portfolio(target_allocation)

        # BTC should sell 1000 (from 6000 to 5000)
        # ETH should buy 1000 (from 4000 to 5000)
        assert mock_order.call_count >= 1


@pytest.mark.asyncio
async def test_track_tax_lots(trader):
    """Test tax lot tracking"""
    trader.orders = {
        1: {'symbol': 'BTCUSDT', 'side': 'BUY', 'executedQty': '0.5',
            'price': '40000', 'transactTime': 1609459200000, 'status': 'FILLED'},
        2: {'symbol': 'BTCUSDT', 'side': 'SELL', 'executedQty': '0.3',
            'price': '45000', 'transactTime': 1612137600000, 'status': 'FILLED'}
    }

    df = await trader.track_tax_lots()

    assert len(df) == 2
    assert df['symbol'].iloc[0] == 'BTCUSDT'
    assert float(df['quantity'].iloc[0]) == 0.5


@pytest.mark.asyncio
async def test_get_staking_rewards_success(trader):
    """Test staking rewards retrieval"""
    with patch.object(trader.client, 'get_staking_history') as mock_staking:
        mock_staking.return_value = [
            {'amount': '0.5', 'asset': 'ETH'},
            {'amount': '0.3', 'asset': 'ETH'}
        ]

        rewards = await trader.get_staking_rewards()

        assert rewards['total_rewards'] == pytest.approx(0.8)
        assert len(rewards['details']) == 2


@pytest.mark.asyncio
async def test_get_staking_rewards_failure(trader):
    """Test staking rewards error handling"""
    with patch.object(trader.client, 'get_staking_history') as mock_staking:
        mock_staking.side_effect = Exception("API error")

        rewards = await trader.get_staking_rewards()

        assert rewards['total_rewards'] == 0
        assert len(rewards['details']) == 0


def test_stop_all_streams(trader):
    """Test stopping all WebSocket streams"""
    trader.active_streams = ['conn1', 'conn2', 'conn3']

    with patch.object(trader.bm, 'stop_socket') as mock_stop, \
         patch.object(trader.bm, 'close') as mock_close:

        trader.stop_all_streams()

        assert mock_stop.call_count == 3
        mock_close.assert_called_once()


# Integration tests
@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_trading_workflow(trader):
    """Test complete trading workflow"""
    with patch.object(trader.client, 'get_account') as mock_account, \
         patch.object(trader.client, 'create_order') as mock_order, \
         patch.object(trader.client, 'get_symbol_ticker') as mock_ticker:

        # Mock account balance
        mock_account.return_value = {
            'balances': [{'asset': 'USDT', 'free': '10000.0', 'locked': '0'}]
        }

        # Mock price
        mock_ticker.return_value = {'symbol': 'BTCUSDT', 'price': '50000.0'}

        # Mock order
        mock_order.return_value = {
            'orderId': 12345,
            'symbol': 'BTCUSDT',
            'side': 'BUY',
            'executedQty': '0.1',
            'status': 'FILLED'
        }

        # Get balance
        balance = await trader.get_account_balance()
        assert balance['USDT'] == 10000.0

        # Calculate position size
        position_size = trader.calculate_position_size(10000.0, 50000.0, 49000.0)

        # Execute order
        order = await trader.execute_market_order('BTCUSDT', SIDE_BUY, position_size)

        assert order is not None
        assert order['status'] == 'FILLED'


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--cov=pillar_a_trading.crypto.binance_live_trader'])
