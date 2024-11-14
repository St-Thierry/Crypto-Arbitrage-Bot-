import requests

TEXTBELT_API_KEY = 'your_textbelt_api_key'
TO_PHONE_NUMBER = 'your_mobile_phone_number'
cryptos = ['BTC', 'ETH', 'SOL', 'USDT']
EXCHANGE_APIS = {
    'Binance': 'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT',
    'Kraken': 'https://api.kraken.com/0/public/Ticker?pair={symbol}USDT',
    'Coinbase': 'https://api.coinbase.com/v2/prices/{symbol}-USD/spot'
}

def get_price(exchange, symbol):
    url = EXCHANGE_APIS[exchange].format(symbol=symbol)
    response = requests.get(url)
    data = response.json()
    if exchange == 'Binance':
        return float(data['price'])
    elif exchange == 'Kraken':
        key = list(data['result'].keys())[0]
        return float(data['result'][key]['c'][0])
    elif exchange == 'Coinbase':
        return float(data['data']['amount'])
    return None

def send_sms_alert(message):
    response = requests.post('https://textbelt.com/text', {
        'phone': TO_PHONE_NUMBER,
        'message': message,
        'key': TEXTBELT_API_KEY,
    })
    result = response.json()
    if not result.get('success'):
        print("Failed to send SMS:", result.get("error"))

def check_price_discrepancies(threshold=1.0):
    price_data = {crypto: {} for crypto in cryptos}
    for crypto in cryptos:
        for exchange in EXCHANGE_APIS.keys():
            try:
                price = get_price(exchange, crypto)
                if price:
                    price_data[crypto][exchange] = price
            except Exception as e:
                print(f"Error fetching {crypto} price from {exchange}: {e}")

    for crypto, prices in price_data.items():
        if len(prices) == len(EXCHANGE_APIS):
            min_price = min(prices.values())
            max_price = max(prices.values())
            diff_percentage = ((max_price - min_price) / min_price) * 100
            if diff_percentage >= threshold:
                message = (f"Price discrepancy for {crypto}: "
                           f"{min_price} - {max_price} USD "
                           f"({diff_percentage:.2f}% difference) "
                           f"across exchanges.")
                print(message)
                send_sms_alert(message)
        else:
            print(f"Not enough data for {crypto}")

check_price_discrepancies(threshold=2.0)
