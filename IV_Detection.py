import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage
from ib_insync import *
import numpy as np
import time

# Connect to Interactive Brokers TWS or IB Gateway
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)  # Use 7496 for IB Gateway

def fetch_stock_and_options_data(symbol):
    try:
        # Create contract
        stock = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(stock)
        
        # Get stock price
        ticker = ib.reqMktData(stock)
        ib.sleep(1)  # Wait for data to arrive
        if not ticker.marketPrice():
            return None
        
        price = ticker.marketPrice()
        
        # Get options chains
        chains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
        if not chains:
            return None
            
        chain = next(c for c in chains if c.exchange == 'SMART')
        
        # Get strikes near the money
        strikes = [strike for strike in chain.strikes
                  if 0.8 * price <= strike <= 1.2 * price]
                  
        expirations = sorted(exp for exp in chain.expirations)[:3]  # Next 3 expirations
        
        contracts = []
        for expiration in expirations:
            for strike in strikes:
                contracts.append(Option(symbol, expiration, strike, 'C', 'SMART'))
                contracts.append(Option(symbol, expiration, strike, 'P', 'SMART'))
        
        ib.qualifyContracts(*contracts)
        
        # Get market data for all contracts
        tickers = ib.reqTickers(*contracts)
        ib.sleep(1)  # Wait for data
        
        # Find highest IV
        max_iv = 0
        for ticker in tickers:
            if ticker.modelGreeks and ticker.modelGreeks.impliedVol:
                iv = ticker.modelGreeks.impliedVol
                max_iv = max(max_iv, iv)
        
        if price > 10 and max_iv > 1.5:  # IV > 150%
            return f"{symbol}: Price ${price:.2f}, Max IV {max_iv*100:.1f}%"
            
    except Exception as e:
        print(f"Error processing {symbol}: {str(e)}")
        
    return None

def fetch_high_iv_stocks():
    # Get S&P 500 symbols
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    symbols = sp500['Symbol'].tolist()
    
    high_iv_stocks = []
    for symbol in symbols:
        result = fetch_stock_and_options_data(symbol)
        if result:
            high_iv_stocks.append(result)
            print(f"Found high IV: {result}")
        ib.sleep(0.1)  # Rate limiting
            
    return high_iv_stocks

def send_email_alert(alerts):
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"
    receiver_email = "your_email@example.com"

    msg = EmailMessage()
    msg.set_content("\n".join(alerts))
    msg['Subject'] = "High IV Stock Alert"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

def main():
    while True:
        try:
            print(f"Checking market data at {datetime.now()}")
            if not ib.isConnected():
                ib.connect('127.0.0.1', 7497, clientId=1)
                
            high_iv_stocks = fetch_high_iv_stocks()
            if high_iv_stocks:
                send_email_alert(high_iv_stocks)
                print(f"Alert sent for {len(high_iv_stocks)} stocks")
            else:
                print("No stocks meeting the criteria found")
                
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            if ib.isConnected():
                ib.disconnect()
            time.sleep(10)  # Wait before reconnecting
            continue
            
        # Wait for an hour before the next check
        time.sleep(3600)

if __name__ == "__main__":
    try:
        util.startLoop()  # This will start IB's event loop
        main()
    finally:
        if ib.isConnected():
            ib.disconnect()
