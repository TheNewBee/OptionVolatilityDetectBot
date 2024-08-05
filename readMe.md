# High IV Stock Alert

## Description

This Python program automatically monitors the stock market for high implied volatility (IV) opportunities. It scans stocks with a price over $10 and options with an IV over 150%, sending email alerts when such opportunities are found.

## Features

- Asynchronous processing for efficient data fetching
- Hourly checks of the entire S&P 500 list (customizable)
- Email alerts for stocks meeting the criteria
- Continuous operation with hourly updates

## Requirements

- Python 3.7+
- aiohttp
- pandas
- Access to a stock market data API

## Installation

1. Clone this repository:

2. Install required packages:
   pip install aiohttp pandaspip install aiohttp pandas

3. Set up your stock market data API (e.g., Alpha Vantage, IEX Cloud, etc.)

## Configuration

1. Open `high_iv_alert.py` in a text editor.

2. Replace the placeholder API details:

```python
API_KEY = 'your_api_key_here'
BASE_URL = 'https://api.example.com/v1'  # Replace with actual API endpoint

3. Update the email configuration in the send_email_alert function:
sender_email = "your_email@gmail.com"
sender_password = "your_app_password"
receiver_email = "your_email@example.com"
```

Usage
Run the script:
python high_iv_alert.py

The program will start monitoring stocks and send email alerts when it finds stocks meeting the criteria.

**_Customization_**

- To monitor a different set of stocks, modify the fetch_high_iv_stocks function.
- Adjust the price and IV thresholds in the process_stock function.
- Change the check frequency by modifying the asyncio.sleep(3600) call in the main function.

**_Notes_**

- Ensure you comply with the terms of service of your chosen stock data API.
- Be aware of rate limits and adjust the code if necessary to avoid exceeding them.
- This program is for educational purposes only and should not be considered financial advice.

**_Contributing_**
Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.

License
MIT
https://choosealicense.com/licenses/mit/
