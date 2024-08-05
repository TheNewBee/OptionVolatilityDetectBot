import asyncio
import aiohttp
import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage

# Replace with a real API key from a stock data provider
API_KEY = 'your_api_key_here'
BASE_URL = 'https://api.example.com/v1'  # Replace with actual API endpoint

async def fetch_stock_data(session, symbol):
    url = f"{BASE_URL}/stock/{symbol}/quote?token={API_KEY}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return symbol, data['latestPrice']
    return symbol, None

async def fetch_option_data(session, symbol):
    url = f"{BASE_URL}/stock/{symbol}/options?token={API_KEY}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return symbol, data
    return symbol, None

async def process_stock(session, symbol):
    stock_price, option_data = await asyncio.gather(
        fetch_stock_data(session, symbol),
        fetch_option_data(session, symbol)
    )
    
    if stock_price[1] is None or option_data[1] is None:
        return None

    price = stock_price[1]
    options = option_data[1]

    if price > 10:
        high_iv_options = [opt for opt in options if opt['impliedVolatility'] > 1.5]
        if high_iv_options:
            return f"{symbol}: Price ${price:.2f}, IV > 150%"
    
    return None

async def fetch_high_iv_stocks():
    # Get S&P 500 symbols (you can replace this with any list of stocks)
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    symbols = sp500['Symbol'].tolist()

    high_iv_stocks = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [process_stock(session, symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        high_iv_stocks = [result for result in results if result is not None]

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

async def main():
    while True:
        print(f"Checking market data at {datetime.now()}")
        high_iv_stocks = await fetch_high_iv_stocks()
        if high_iv_stocks:
            send_email_alert(high_iv_stocks)
            print(f"Alert sent for {len(high_iv_stocks)} stocks")
        else:
            print("No stocks meeting the criteria found")
        
        # Wait for an hour before the next check
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
