#!/usr/bin/env python3
from bot import BasicBot
import argparse, logging, sys

class CommandLineInterface:
    
    def __init__(self, bot: BasicBot):
        self.bot = bot
        self.logger = bot.logger
    
    def run_interactive_mode(self):
        print("\n=== Binance Futures Trading Bot ===")
        print("Available commands:")
        print("1. market - Place market order")
        print("2. limit - Place limit order") 
        print("3. stop - Place stop-limit order")
        print("4. cancel - Cancel order")
        print("5. orders - Show open orders")
        print("6. balance - Show account balance")
        print("7. price - Get current price")
        print("8. quit - Exit")
        print("=" * 40)
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'quit':
                    print("Goodbye!")
                    break
                elif command == 'market':
                    self._handle_market_order()
                elif command == 'limit':
                    self._handle_limit_order()
                elif command == 'stop':
                    self._handle_stop_order()
                elif command == 'cancel':
                    self._handle_cancel_order()
                elif command == 'orders':
                    self._handle_show_orders()
                elif command == 'balance':
                    self._handle_show_balance()
                elif command == 'price':
                    self._handle_get_price()
                else:
                    print("Unknown command. Try again.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _handle_market_order(self):
        try:
            symbol = input("Symbol (e.g., BTCUSDT): ").strip()
            side = input("Side (BUY/SELL): ").strip().upper()
            quantity = float(input("Quantity: "))
            
            result = self.bot.place_market_order(symbol, side, quantity)
            print(f"Market order placed: {result['orderId']}")
            
        except Exception as e:
            print(f"Failed to place market order: {e}")
    
    def _handle_limit_order(self):
        try:
            symbol = input("Symbol (e.g., BTCUSDT): ").strip()
            side = input("Side (BUY/SELL): ").strip().upper()
            quantity = float(input("Quantity: "))
            price = float(input("Price: "))
            
            result = self.bot.place_limit_order(symbol, side, quantity, price)
            print(f"Limit order placed: {result['orderId']}")
            
        except Exception as e:
            print(f"Failed to place limit order: {e}")
    
    def _handle_stop_order(self):
        try:
            symbol = input("Symbol (e.g., BTCUSDT): ").strip()
            side = input("Side (BUY/SELL): ").strip().upper()
            quantity = float(input("Quantity: "))
            stop_price = float(input("Stop price: "))
            limit_price = float(input("Limit price: "))
            
            result = self.bot.place_stop_limit_order(symbol, side, quantity, limit_price, stop_price)
            print(f"Stop-limit order placed: {result['orderId']}")
            
        except Exception as e:
            print(f"Failed to place stop-limit order: {e}")
    
    def _handle_cancel_order(self):
        try:
            symbol = input("Symbol: ").strip()
            order_id = int(input("Order ID: "))
            
            result = self.bot.cancel_order(symbol, order_id)
            print(f"Order {order_id} cancelled successfully")
            
        except Exception as e:
            print(f"Failed to cancel order: {e}")
    
    def _handle_show_orders(self):
        try:
            symbol = input("Symbol (or press Enter for all): ").strip()
            if not symbol:
                symbol = None
                
            orders = self.bot.get_open_orders(symbol)
            
            if not orders:
                print("No open orders")
                return
                
            print(f"\nOpen orders ({len(orders)}):")
            for order in orders:
                print(f"ID: {order['orderId']}, Symbol: {order['symbol']}, "
                      f"Side: {order['side']}, Type: {order['type']}, "
                      f"Quantity: {order['origQty']}, Price: {order['price']}")
                      
        except Exception as e:
            print(f"Failed to get orders: {e}")
    
    def _handle_show_balance(self):
        try:
            balance_info = self.bot.get_account_balance()
            
            print(f"\nTotal Balance: {balance_info['totalBalance']} USDT")
            print(f"Available Balance: {balance_info['availableBalance']} USDT")
            
            if balance_info['balances']:
                print("\nAsset Balances:")
                for asset, balance in balance_info['balances'].items():
                    print(f"{asset}: {balance}")
                    
        except Exception as e:
            print(f"Failed to get balance: {e}")
    
    def _handle_get_price(self):
        try:
            symbol = input("Symbol (e.g., BTCUSDT): ").strip()
            price = self.bot.get_current_price(symbol)
            print(f"Current price for {symbol}: {price}")
            
        except Exception as e:
            print(f"Failed to get price: {e}")


def main():
    parser = argparse.ArgumentParser(description='Binance Futures Trading Bot')
    parser.add_argument('--api-key', required=True, help='Binance API Key')
    parser.add_argument('--api-secret', required=True, help='Binance API Secret')
    parser.add_argument('--mainnet', action='store_true', help='Use mainnet instead of testnet')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    log_level = getattr(logging, args.log_level.upper())
    
    try:
        bot = BasicBot(
            api_key=args.api_key,
            api_secret=args.api_secret,
            testnet=not args.mainnet
        )
        
        cli = CommandLineInterface(bot)
        cli.run_interactive_mode()
        
    except Exception as e:
        print(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()