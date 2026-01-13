"""
Pricing Tools for Agent 4.0 Advanced
Calculate, compare, optimize, and forecast pricing
"""

import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PricingCalculator:
    """Advanced pricing calculation and management"""
    
    def __init__(self):
        self.supported_operations = [
            'calculate', 'compare', 'optimize', 'forecast',
            'discount', 'markup', 'margin', 'tax'
        ]
        self.pricing_history = []
    
    def calculate_base_price(
        self,
        cost: float,
        markup_percent: float = 50.0,
        fixed_overhead: float = 0.0
    ) -> Dict:
        """
        Calculate base price from cost
        
        Args:
            cost: Base cost
            markup_percent: Markup percentage
            fixed_overhead: Fixed overhead cost
            
        Returns:
            Dictionary with price calculations
        """
        try:
            cost = Decimal(str(cost))
            markup_percent = Decimal(str(markup_percent))
            fixed_overhead = Decimal(str(fixed_overhead))
            
            markup_amount = (cost * markup_percent / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            base_price = (cost + markup_amount + fixed_overhead).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            margin_percent = ((base_price - cost) / base_price * 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            return {
                'success': True,
                'cost': float(cost),
                'markup_percent': float(markup_percent),
                'markup_amount': float(markup_amount),
                'fixed_overhead': float(fixed_overhead),
                'base_price': float(base_price),
                'margin_percent': float(margin_percent)
            }
            
        except Exception as e:
            logger.error(f"Error calculating base price: {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_discount(
        self,
        price: float,
        discount_percent: Optional[float] = None,
        discount_amount: Optional[float] = None
    ) -> Dict:
        """
        Calculate discounted price
        
        Args:
            price: Original price
            discount_percent: Discount as percentage
            discount_amount: Discount as fixed amount
            
        Returns:
            Dictionary with discount calculations
        """
        try:
            price = Decimal(str(price))
            
            if discount_percent is not None:
                discount_percent = Decimal(str(discount_percent))
                discount_amount_calc = (price * discount_percent / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            elif discount_amount is not None:
                discount_amount_calc = Decimal(str(discount_amount))
                discount_percent = (discount_amount_calc / price * 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            else:
                return {'success': False, 'error': 'Must provide discount_percent or discount_amount'}
            
            final_price = (price - discount_amount_calc).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            return {
                'success': True,
                'original_price': float(price),
                'discount_percent': float(discount_percent),
                'discount_amount': float(discount_amount_calc),
                'final_price': float(final_price),
                'savings': float(discount_amount_calc)
            }
            
        except Exception as e:
            logger.error(f"Error calculating discount: {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_tax(
        self,
        price: float,
        tax_rate: float,
        include_tax: bool = False
    ) -> Dict:
        """
        Calculate price with tax
        
        Args:
            price: Base price
            tax_rate: Tax rate as percentage
            include_tax: Whether price already includes tax
            
        Returns:
            Dictionary with tax calculations
        """
        try:
            price = Decimal(str(price))
            tax_rate = Decimal(str(tax_rate))
            
            if include_tax:
                # Extract tax from price
                base_price = (price / (1 + tax_rate / 100)).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                tax_amount = (price - base_price).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                total_price = price
            else:
                # Add tax to price
                base_price = price
                tax_amount = (price * tax_rate / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                total_price = (price + tax_amount).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            
            return {
                'success': True,
                'base_price': float(base_price),
                'tax_rate': float(tax_rate),
                'tax_amount': float(tax_amount),
                'total_price': float(total_price)
            }
            
        except Exception as e:
            logger.error(f"Error calculating tax: {e}")
            return {'success': False, 'error': str(e)}
    
    def calculate_tiered_pricing(
        self,
        quantity: int,
        tiers: List[Dict]
    ) -> Dict:
        """
        Calculate price based on quantity tiers
        
        Args:
            quantity: Quantity to price
            tiers: List of pricing tiers
                Example: [
                    {'min': 1, 'max': 10, 'price': 10.00},
                    {'min': 11, 'max': 50, 'price': 9.00},
                    {'min': 51, 'max': None, 'price': 8.00}
                ]
            
        Returns:
            Dictionary with tiered pricing
        """
        try:
            applicable_tier = None
            for tier in tiers:
                min_qty = tier.get('min', 0)
                max_qty = tier.get('max')
                
                if max_qty is None:
                    if quantity >= min_qty:
                        applicable_tier = tier
                        break
                elif min_qty <= quantity <= max_qty:
                    applicable_tier = tier
                    break
            
            if not applicable_tier:
                return {'success': False, 'error': 'No applicable tier found'}
            
            unit_price = Decimal(str(applicable_tier['price']))
            total_price = (unit_price * quantity).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            return {
                'success': True,
                'quantity': quantity,
                'unit_price': float(unit_price),
                'total_price': float(total_price),
                'tier': applicable_tier
            }
            
        except Exception as e:
            logger.error(f"Error calculating tiered pricing: {e}")
            return {'success': False, 'error': str(e)}
    
    def compare_prices(
        self,
        prices: List[Dict],
        sort_by: str = 'total_price'
    ) -> Dict:
        """
        Compare multiple pricing options
        
        Args:
            prices: List of pricing dictionaries
            sort_by: Field to sort by
            
        Returns:
            Dictionary with comparison results
        """
        try:
            if not prices:
                return {'success': False, 'error': 'No prices to compare'}
            
            # Sort prices
            sorted_prices = sorted(
                prices,
                key=lambda x: x.get(sort_by, float('inf'))
            )
            
            best_price = sorted_prices[0]
            worst_price = sorted_prices[-1]
            
            total_values = [p.get(sort_by, 0) for p in prices]
            average = sum(total_values) / len(total_values) if total_values else 0
            
            return {
                'success': True,
                'total_options': len(prices),
                'best_option': best_price,
                'worst_option': worst_price,
                'average_price': round(average, 2),
                'all_options': sorted_prices
            }
            
        except Exception as e:
            logger.error(f"Error comparing prices: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_pricing(
        self,
        cost: float,
        target_margin_percent: float,
        market_price: Optional[float] = None,
        competitor_prices: Optional[List[float]] = None
    ) -> Dict:
        """
        Optimize pricing based on multiple factors
        
        Args:
            cost: Base cost
            target_margin_percent: Desired profit margin
            market_price: Average market price
            competitor_prices: List of competitor prices
            
        Returns:
            Dictionary with optimized pricing
        """
        try:
            cost = Decimal(str(cost))
            target_margin = Decimal(str(target_margin_percent))
            
            # Calculate price for target margin
            # margin = (price - cost) / price
            # price = cost / (1 - margin/100)
            target_price = (cost / (1 - target_margin / 100)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            recommendations = {
                'target_margin_price': float(target_price)
            }
            
            # Consider market price
            if market_price:
                market_price = Decimal(str(market_price))
                market_margin = ((market_price - cost) / market_price * 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                recommendations['market_price'] = float(market_price)
                recommendations['market_margin_percent'] = float(market_margin)
            
            # Consider competitor prices
            if competitor_prices:
                comp_avg = Decimal(str(sum(competitor_prices) / len(competitor_prices)))
                comp_min = Decimal(str(min(competitor_prices)))
                comp_max = Decimal(str(max(competitor_prices)))
                
                # Suggest competitive price (slightly below average)
                competitive_price = (comp_avg * Decimal('0.95')).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                competitive_margin = ((competitive_price - cost) / competitive_price * 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                
                recommendations['competitor_avg'] = float(comp_avg)
                recommendations['competitor_min'] = float(comp_min)
                recommendations['competitor_max'] = float(comp_max)
                recommendations['competitive_price'] = float(competitive_price)
                recommendations['competitive_margin_percent'] = float(competitive_margin)
            
            # Overall recommendation
            all_prices = [target_price]
            if market_price:
                all_prices.append(market_price)
            if competitor_prices:
                all_prices.append(competitive_price)
            
            recommended_price = sum(all_prices) / len(all_prices)
            recommended_price = recommended_price.quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            recommended_margin = ((recommended_price - cost) / recommended_price * 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            return {
                'success': True,
                'cost': float(cost),
                'target_margin_percent': float(target_margin),
                'recommended_price': float(recommended_price),
                'recommended_margin_percent': float(recommended_margin),
                'analysis': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error optimizing pricing: {e}")
            return {'success': False, 'error': str(e)}
    
    def forecast_revenue(
        self,
        price: float,
        estimated_units: int,
        time_period_days: int = 30,
        growth_rate_percent: float = 0.0
    ) -> Dict:
        """
        Forecast revenue based on pricing and estimates
        
        Args:
            price: Unit price
            estimated_units: Estimated units sold
            time_period_days: Forecast period in days
            growth_rate_percent: Expected growth rate
            
        Returns:
            Dictionary with revenue forecast
        """
        try:
            price = Decimal(str(price))
            growth_rate = Decimal(str(growth_rate_percent))
            
            # Calculate base revenue
            base_revenue = (price * estimated_units).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            # Generate forecast
            forecast = []
            current_date = datetime.now()
            current_units = estimated_units
            
            for day in range(time_period_days):
                date = current_date + timedelta(days=day)
                
                # Apply growth
                if growth_rate != 0:
                    daily_growth = (1 + growth_rate / 100 / 365)  # Daily compounding
                    current_units = int(estimated_units * (daily_growth ** day))
                
                daily_revenue = (price * current_units).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                
                forecast.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'day': day + 1,
                    'estimated_units': current_units,
                    'daily_revenue': float(daily_revenue)
                })
            
            total_revenue = sum(Decimal(str(f['daily_revenue'])) for f in forecast)
            
            return {
                'success': True,
                'price': float(price),
                'initial_units': estimated_units,
                'time_period_days': time_period_days,
                'growth_rate_percent': float(growth_rate),
                'total_revenue': float(total_revenue),
                'average_daily_revenue': float(total_revenue / time_period_days),
                'forecast': forecast[:7]  # Return first week as sample
            }
            
        except Exception as e:
            logger.error(f"Error forecasting revenue: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """Example usage"""
    calculator = PricingCalculator()
    
    print("=== Pricing Calculator ===")
    print(f"Supported operations: {', '.join(calculator.supported_operations)}\n")
    
    # Example 1: Calculate base price
    result = calculator.calculate_base_price(
        cost=50.00,
        markup_percent=60.0,
        fixed_overhead=5.00
    )
    if result.get('success'):
        print(f"✓ Base Price Calculation:")
        print(f"  Cost: ${result['cost']}")
        print(f"  Markup: {result['markup_percent']}% (${result['markup_amount']})")
        print(f"  Base Price: ${result['base_price']}")
        print(f"  Margin: {result['margin_percent']}%\n")
    
    # Example 2: Optimize pricing
    result = calculator.optimize_pricing(
        cost=50.00,
        target_margin_percent=40.0,
        market_price=95.00,
        competitor_prices=[89.99, 92.50, 87.99, 94.99]
    )
    if result.get('success'):
        print(f"✓ Optimized Pricing:")
        print(f"  Recommended Price: ${result['recommended_price']}")
        print(f"  Recommended Margin: {result['recommended_margin_percent']}%")
        print(f"  Target Margin Price: ${result['analysis']['target_margin_price']}")
        print(f"  Competitive Price: ${result['analysis']['competitive_price']}\n")
    
    # Example 3: Forecast revenue
    result = calculator.forecast_revenue(
        price=95.00,
        estimated_units=100,
        time_period_days=30,
        growth_rate_percent=10.0
    )
    if result.get('success'):
        print(f"✓ Revenue Forecast (30 days):")
        print(f"  Total Revenue: ${result['total_revenue']:,.2f}")
        print(f"  Average Daily: ${result['average_daily_revenue']:,.2f}")
        print(f"  Growth Rate: {result['growth_rate_percent']}%")


if __name__ == '__main__':
    main()
