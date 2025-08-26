import ccxt
import pandas as pd
import time
from datetime import datetime

class XRPDataCollector:
    def __init__(self):
        # Initialize exchanges with proper configurations
        # Using more reliable exchanges with good API access
        self.exchanges = {
            'kraken': ccxt.kraken({
                'rateLimit': 3000,
                'enableRateLimit': True,
            }),
            'bitstamp': ccxt.bitstamp({
                'rateLimit': 1000,
                'enableRateLimit': True,
            }),
            'bitfinex': ccxt.bitfinex({
                'rateLimit': 1500,
                'enableRateLimit': True,
            }),
            'gemini': ccxt.gemini({
                'rateLimit': 1000,
                'enableRateLimit': True,
            }),
            'huobi': ccxt.huobi({
                'rateLimit': 2000,
                'enableRateLimit': True,
            }),
            'okx': ccxt.okx({
                'rateLimit': 1000,
                'enableRateLimit': True,
            }),
            'kucoin': ccxt.kucoin({
                'rateLimit': 1000,
                'enableRateLimit': True,
            })
        }
        
        # XRP trading pairs to check - different exchanges use different symbols
        self.exchange_symbols = {
            'kraken': ['XRP/USD', 'XRP/USDT'],
            'bitstamp': ['XRP/USD', 'XRP/EUR'],
            'bitfinex': ['XRP/USD', 'XRP/USDT'],
            'gemini': ['XRP/USD'],
            'huobi': ['XRP/USDT', 'XRP/USD'],
            'okx': ['XRP/USDT', 'XRP/USD'],
            'kucoin': ['XRP/USDT', 'XRP/USD']
        }
    
    def get_price_from_exchange(self, exchange_name, exchange_obj):
        """Get XRP price from a single exchange"""
        try:
            # Get available symbols for this exchange
            symbols_to_try = self.exchange_symbols.get(exchange_name, ['XRP/USDT', 'XRP/USD'])
            
            ticker = None
            symbol_used = None
            
            # Try each symbol until one works
            for symbol in symbols_to_try:
                try:
                    # Load markets first to ensure symbol exists
                    exchange_obj.load_markets()
                    
                    if symbol in exchange_obj.markets:
                        ticker = exchange_obj.fetch_ticker(symbol)
                        symbol_used = symbol
                        break
                except Exception as e:
                    print(f"  Failed to fetch {symbol} from {exchange_name}: {str(e)[:50]}...")
                    continue
            
            if ticker is None:
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
            print(f"Error fetching from {exchange_name}: {str(e)[:100]}...")
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
