#!/usr/bin/env python3
from logger import TradingBotLogger
import sys, json
from decimal import Decimal, ROUND_DOWN
from typing import Dict

try:
    from binance import Client
    from binance.exceptions import BinanceAPIException, BinanceOrderException
except ImportError:
    print("Error: python-binance library not installed.")
    print("Install it using: pip install python-binance")
    sys.exit(1)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet = True):
        self.logger = TradingBotLogger().get_logger()
        
        try:
            self.client = Client(
                api_key=api_key,
                api_secret=api_secret,
                testnet=testnet
            )
            
            self.client.futures_api_url = 'https://testnet.binancefuture.com'
            self.logger.info(f"Bot initialized {'on TESTNET' if testnet else 'on MAINNET'}")
            self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {e}")
            raise
    
    def _test_connection(self):
        try:
            server_time = self.client.futures_time()
            self.logger.info(f"Connected to Binance Futures. Server time: {server_time}")
            
            account_info = self.client.futures_account()
            balance = float(account_info['totalWalletBalance'])
            self.logger.info(f"Account balance: {balance} USDT")
            
        except BinanceAPIException as e:
            self.logger.error(f"API connection failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            raise
    
    def get_symbol_info(self, symbol: str):
        try:
            exchange_info = self.client.futures_exchange_info()
            
            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] == symbol.upper():
                    return symbol_info
            
            raise ValueError(f"Symbol {symbol} not found")
            
        except Exception as e:
            self.logger.error(f"Failed to get symbol info for {symbol}: {e}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            price = float(ticker['price'])
            self.logger.debug(f"Current price for {symbol}: {price}")
            return price
            
        except Exception as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            raise
    
    def format_quantity(self, symbol: str, quantity: float) -> str:
        try:
            symbol_info = self.get_symbol_info(symbol)
            
            lot_size_filter = None
            for filter_info in symbol_info['filters']:
                if filter_info['filterType'] == 'LOT_SIZE':
                    lot_size_filter = filter_info
                    break
            
            if not lot_size_filter:
                return str(quantity)
            
            step_size = float(lot_size_filter['stepSize'])
            precision = len(str(step_size).split('.')[-1]) if '.' in str(step_size) else 0
            
            # Round down to nearest step size
            rounded_qty = float(Decimal(str(quantity)).quantize(
                Decimal(str(step_size)), rounding=ROUND_DOWN
            ))
            
            return f"{rounded_qty:.{precision}f}".rstrip('0').rstrip('.')
            
        except Exception as e:
            self.logger.error(f"Failed to format quantity: {e}")
            return str(quantity)
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """
        Place a market order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            
        Returns:
            Order response dictionary
        """
        try:
            symbol = symbol.upper()
            side = side.upper()
            
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            formatted_qty = self.format_quantity(symbol, quantity)
            
            self.logger.info(f"Placing MARKET {side} order: {formatted_qty} {symbol}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=formatted_qty
            )
            
            self.logger.info(f"Market order placed successfully: {order['orderId']}")
            self.logger.debug(f"Order details: {json.dumps(order, indent=2)}")
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error placing market order: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to place market order: {e}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, 
                         time_in_force: str = 'GTC') -> Dict:
        """
        Place a limit order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response dictionary
        """
        try:
            symbol = symbol.upper()
            side = side.upper()
            
            # Validate inputs
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            formatted_qty = self.format_quantity(symbol, quantity)
            
            self.logger.info(f"Placing LIMIT {side} order: {formatted_qty} {symbol} @ {price}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=formatted_qty,
                price=str(price),
                timeInForce=time_in_force
            )
            
            self.logger.info(f"Limit order placed successfully: {order['orderId']}")
            self.logger.debug(f"Order details: {json.dumps(order, indent=2)}")
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error placing limit order: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to place limit order: {e}")
            raise
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, 
                              price: float, stop_price: float, 
                              time_in_force: str = 'GTC') -> Dict:
        """
        Place a stop-limit order
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            stop_price: Stop price
            time_in_force: Time in force
            
        Returns:
            Order response dictionary
        """
        try:
            symbol = symbol.upper()
            side = side.upper()
            
            formatted_qty = self.format_quantity(symbol, quantity)
            
            self.logger.info(f"Placing STOP_MARKET {side} order: {formatted_qty} {symbol} @ stop: {stop_price}, limit: {price}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                quantity=formatted_qty,
                price=str(price),
                stopPrice=str(stop_price),
                timeInForce=time_in_force
            )
            
            self.logger.info(f"Stop-limit order placed successfully: {order['orderId']}")
            self.logger.debug(f"Order details: {json.dumps(order, indent=2)}")
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error placing stop-limit order: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to place stop-limit order: {e}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an open order"""
        try:
            result = self.client.futures_cancel_order(
                symbol=symbol.upper(),
                orderId=order_id
            )
            
            self.logger.info(f"Order {order_id} cancelled successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            raise
    
    def get_open_orders(self, symbol: str = None) -> list:
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            self.logger.info(f"Retrieved {len(orders)} open orders")
            return orders
            
        except Exception as e:
            self.logger.error(f"Failed to get open orders: {e}")
            raise
    
    def get_account_balance(self) -> Dict:
        try:
            account = self.client.futures_account()
            balances = {asset['asset']: float(asset['walletBalance']) 
                       for asset in account['assets'] 
                       if float(asset['walletBalance']) > 0}
            
            self.logger.info(f"Account balances: {balances}")
            return {
                'totalBalance': float(account['totalWalletBalance']),
                'availableBalance': float(account['availableBalance']),
                'balances': balances
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get account balance: {e}")
            raise