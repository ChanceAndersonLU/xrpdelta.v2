import pandas as pd
from data_collector import XRPDataCollector

class ArbitrageAnalyzer:
    def __init__(self):
        # Typical exchange fees (trading fees + withdrawal fees)
        # These are estimates - you should check actual fees for your account tier
        self.exchange_fees = {
            'binance': 0.001,   # 0.1% trading fee
            'coinbase': 0.005,  # 0.5% trading fee  
            'kraken': 0.0026,   # 0.26% trading fee
            'bitstamp': 0.005   # 0.5% trading fee
        }
        
        # Minimum profit threshold (as percentage)
        self.min_profit_threshold = 0.002  # 0.2%
    
    def calculate_arbitrage_opportunities(self, prices_df):
        """Find arbitrage opportunities between exchanges"""
        if len(prices_df) < 2:
            print("Need at least 2 exchanges to find arbitrage opportunities")
            return pd.DataFrame()
        
        opportunities = []
        
        # Compare every exchange pair
        for i in range(len(prices_df)):
            for j in range(i + 1, len(prices_df)):
                buy_exchange = prices_df.iloc[i]
                sell_exchange = prices_df.iloc[j]
                
                # Scenario 1: Buy from exchange i, sell on exchange j
                opportunity1 = self._calculate_opportunity(buy_exchange, sell_exchange)
                if opportunity1:
                    opportunities.append(opportunity1)
                
                # Scenario 2: Buy from exchange j, sell on exchange i  
                opportunity2 = self._calculate_opportunity(sell_exchange, buy_exchange)
                if opportunity2:
                    opportunities.append(opportunity2)
        
        if opportunities:
            return pd.DataFrame(opportunities).sort_values('profit_percentage', ascending=False)
        else:
            return pd.DataFrame()
    
    def _calculate_opportunity(self, buy_exchange, sell_exchange):
        """Calculate profit for buying from one exchange and selling on another"""
        buy_price = buy_exchange['ask']  # Price to buy (ask price)
        sell_price = sell_exchange['bid']  # Price to sell (bid price)
        
        buy_fee = self.exchange_fees.get(buy_exchange['exchange'], 0.005)
        sell_fee = self.exchange_fees.get(sell_exchange['exchange'], 0.005)
        
        # Calculate costs
        buy_cost = buy_price * (1 + buy_fee)  # Price + trading fee
        sell_revenue = sell_price * (1 - sell_fee)  # Price - trading fee
        
        # Calculate profit
        profit_per_xrp = sell_revenue - buy_cost
        profit_percentage = (profit_per_xrp / buy_cost) * 100
        
        # Only return if profitable and above threshold
        if profit_percentage > (self.min_profit_threshold * 100):
            return {
                'buy_exchange': buy_exchange['exchange'],
                'sell_exchange': sell_exchange['exchange'],
                'buy_price': buy_price,
                'sell_price': sell_price,
                'buy_cost_with_fees': buy_cost,
                'sell_revenue_with_fees': sell_revenue,
                'profit_per_xrp': profit_per_xrp,
                'profit_percentage': profit_percentage,
                'potential_profit_100_xrp': profit_per_xrp * 100,
                'potential_profit_1000_xrp': profit_per_xrp * 1000
            }
        
        return None
    
    def display_opportunities(self, opportunities_df):
        """Display arbitrage opportunities in a readable format"""
        if opportunities_df.empty:
            print("No arbitrage opportunities found above the minimum threshold.")
            print(f"Minimum profit threshold: {self.min_profit_threshold * 100:.2f}%")
            return
        
        print("\n🚀 ARBITRAGE OPPORTUNITIES FOUND! 🚀")
        print("=" * 60)
        
        for idx, opp in opportunities_df.iterrows():
            print(f"\nOpportunity #{idx + 1}:")
            print(f"📈 Buy XRP on {opp['buy_exchange'].upper()} at ${opp['buy_cost_with_fees']:.4f}")
            print(f"📉 Sell XRP on {opp['sell_exchange'].upper()} at ${opp['sell_revenue_with_fees']:.4f}")
            print(f"💰 Profit: {opp['profit_percentage']:.3f}% per XRP")
            print(f"💵 With 100 XRP: ${opp['potential_profit_100_xrp']:.2f}")
            print(f"💵 With 1000 XRP: ${opp['potential_profit_1000_xrp']:.2f}")
            print("-" * 40)
    
    def analyze_market(self):
        """Main function to analyze the market for arbitrage"""
        print("Starting XRP Arbitrage Analysis...")
        
        # Fetch current prices
        collector = XRPDataCollector()
        prices = collector.fetch_all_prices()
        
        if prices.empty:
            print("Could not fetch prices from any exchanges.")
            return
        
        # Find arbitrage opportunities
        opportunities = self.calculate_arbitrage_opportunities(prices)
        
        # Display results
        self.display_opportunities(opportunities)
        
        # Show current market overview
        print("\n📊 CURRENT MARKET OVERVIEW:")
        print("=" * 40)
        prices_sorted = prices.sort_values('last')
        for idx, row in prices_sorted.iterrows():
            print(f"{row['exchange'].upper()}: ${row['last']:.4f}")
        
        lowest = prices_sorted.iloc[0]['last']
        highest = prices_sorted.iloc[-1]['last']
        spread = ((highest - lowest) / lowest) * 100
        print(f"\nPrice spread: {spread:.3f}%")

# Example usage
if __name__ == "__main__":
    analyzer = ArbitrageAnalyzer()
    analyzer.analyze_market() 
