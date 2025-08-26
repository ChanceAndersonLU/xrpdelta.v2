import ccxt
import pandas as pd
import time
from datetime import datetime

class XRPDataCollector:
    def __init__(self):
        # Initialize exchanges (these don't require API keys for public data)
        self.exchanges = {
            'binance': ccxt.binance(),
            'coinbase': ccxt.coinbase(),
            'kraken': ccxt.kraken(),
            'bitstamp': ccxt.bitstamp()
        }
        
        # XRP trading pairs to check
        self.symbol = 'XRP/USDT'
        self.symbol_alt = 'XRP/USD'  # Some exchanges use USD instead of USDT
    
    def get_price_from_exchange(self, exchange_name, exchange_obj):
        """Get XRP price from a single exchange"""
        try:
            # Try USDT first, then USD
            ticker = None
            symbol_used = None
            
            try:
                ticker = exchange_obj.fetch_ticker(self.symbol)
                symbol_used = self.symbol
            except:
                try:
                    ticker = exchange_obj.fetch_ticker(self.symbol_alt)
                    symbol_used = self.symbol_alt
                except:
                    return None
            
            return {
                'exchange': exchange_name,
                'symbol': symbol_used,
                'bid': ticker['bid'],  # Highest price buyers are willing to pay
                'ask': ticker['ask'],  # Lowest price sellers are willing to accept
                'last': ticker['last'],  # Last traded price
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error fetching from {exchange_name}: {str(e)}")
            return None
    
    def fetch_all_prices(self):
        """Fetch XRP prices from all exchanges"""
        prices = []
        
        print("Fetching XRP prices from exchanges...")
        
        for name, exchange in self.exchanges.items():
            print(f"Checking {name}...")
            price_data = self.get_price_from_exchange(name, exchange)
            
            if price_data:
                prices.append(price_data)
                print(f"✓ {name}: ${price_data['last']:.4f}")
            else:
                print(f"✗ {name}: Failed to fetch")
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        return pd.DataFrame(prices)
    
    def save_prices(self, prices_df, filename=None):
        """Save prices to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xrp_prices_{timestamp}.csv"
        
        prices_df.to_csv(filename, index=False)
        print(f"Prices saved to {filename}")

# Example usage
if __name__ == "__main__":
    collector = XRPDataCollector()
    prices = collector.fetch_all_prices()
    
    if not prices.empty:
        print("\n--- Price Summary ---")
        print(prices[['exchange', 'last', 'bid', 'ask']])
        collector.save_prices(prices)
    else:
        print("No prices were fetched successfully.")