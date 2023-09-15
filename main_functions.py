import ccxt
# from naoranaConfig import binanceAPI
import pandas as pd
import pandas_ta as ta
import numpy as np
import csv
import os
import time

def krakenActive():
    exchange = ccxt.binance({
        # 'apiKey': binanceAPI['apiKey'],
        # 'secret': binanceAPI['secretKey'],
        'enableRateLimit': True,
        'rateLimit': 10000,
        'options': {
            # 'recvWindow': 9000,  # replace with your desired recv_window value
            'test': False,  # use testnet (sandbox) environment
            # 'adjustForTimeDifference': True,
        },
        'futures': {
            'postOnly': False,  # Change to True if you want to use post-only orders
            'leverage': 10,     # Set your desired leverage value
            # You can add more futures-specific options here as needed
        }
    })

    # Uncomment the line below if you want to enable trading on the testnet (sandbox)
    # exchange.set_sandbox_mode(enable=True)

    return exchange

# Example usage

exchange = krakenActive()


def servertime():
    time = exchange.fetch_time()
    time = pd.to_datetime(time, unit ='ms')
    print(time)


def getqty(coin):
    params = {'type':'futures'}
    for item in exchange.fetch_balance(params=params)['info']['balances']:
        if item['asset'] == coin:
            qty = float(item['free'])
    return qty

# print(getqty('USDT'))

# exchange.fetch_balance()

# Define function to place buy order
def place_buy_order(symbol, size):
    try:
        buyId = exchange.create_market_buy_order(symbol, size, params={})
        return buyId
    except:
        return False
    


# Define function to place sell order
def place_sell_order(symbol, size):
    # try:
    sellId = exchange.create_market_sell_order(symbol, size)
    return sellId
    # except:
    #     return False
    
def calculate_order_size(symbol, usdt_amount):
    # Get the current market price of the coin
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']
    # Calculate the order size based on the USDT amount and the market price
    size = usdt_amount / price
    return size



# { ==========================================================================================
# Load historical price data from kraken exchange, but data is limited to 720 candles 

kraken = ccxt.kraken()
def start_time(days):
    timestamp = kraken.fetch_time() - days*86400*1000
    time = pd.to_datetime(timestamp, unit ='ms')
    print(time)
    return timestamp

def getdata_kraken(symbol, timeframe, days):
    df = pd.DataFrame(kraken.fetch_ohlcv(symbol, timeframe, since = start_time(days)))
    df = df[[0,1,2,3,4,5]]
    df.columns = ['timestamp','Open','High','Low','Close','Volume']
    df = df.set_index('timestamp')
    # Convert the datetime index to date+hh:mm:ss format
    df.index = pd.to_datetime(df.index, unit = 'ms') 
    df= df.astype(float)
    return df
# }============================================================================================

# Load historical price data from binance exchange 
from binance.client import Client
client = Client()
def getdata(ticker, timeframe, day):
    start_str = f"{int(timeframe[:-1]) * day * 3600}m"
    df = pd.DataFrame(client.futures_historical_klines(ticker, timeframe, start_str))
    df = df[[0,1,2,3,4,5]]
    df.columns = ['timestamp','Open','High','Low','Close','Volume']
    df = df.set_index('timestamp')
    # Convert the datetime index to date+hh:mm:ss format
    df.index = pd.to_datetime(df.index, unit = 'ms') 
    df= df.astype(float)
    return df 


def create_marker_trace(df, column_name, marker_symbol, y_offset, text_label, name, color):
    filtered_df = df[df[column_name]]
    
    markers = go.Scatter(
        x=filtered_df.index,
        y=filtered_df['High'] + y_offset,
        mode='markers+text',
        text=text_label,
        textposition='top center' if y_offset > 0 else 'bottom center',
        marker=dict(
            symbol=marker_symbol,
            size=10,
            color=color,
            line=dict(
                color=color,
                width=2,
            )
        ),
        visible=True,
        name=name,
    )
    
    return markers


def strategy1_Signals(ticker, timeframe, HL = 20, takeLong = True, takeShort = True, risk = 15):
    df = getdata(ticker, timeframe)
    df = pd.concat((df,ta.ha(df.Open, df.High, df.Low, df.Close)), axis = 1)
    df= df.astype(float)
    df['MinLow'] = df['HA_low'].shift(1).rolling(HL).min()
    df['MaxHigh'] = df['HA_high'].shift(1).rolling(HL).max()
    df['shifted_open'] = df.Open.shift(-1)
    df['buyrisk'] = (df['Close'] - df['MinLow'])/df['Close'] 
    df['sellrisk'] = (df['MaxHigh'] - df['Close'])/df['Close']
    # Apply the conditions for buySignal
    df['buySignal'] = np.where(
                        (df['HA_close'].shift(1) < df['HA_open'].shift(1)) &
                        (df['HA_low'] == df['HA_open']) &
                        (df['HA_low'].shift(1) == df['MinLow']) &
                        (takeLong == True) &
                        (df['buyrisk'] < risk/100),
                        1,
                        0
    )
    df['shortSignal'] = np.where(
                    (df['HA_close'].shift(1) > df['HA_open'].shift(1)) &
                    (df['HA_high'] == df['HA_open']) &
                    (df['HA_high'].shift(1) == df['MaxHigh']) &
                    (takeShort == True) &
                    (df['sellrisk'] < risk/100),
                    -1,
                    0
    )
    return df


# code for appending a new row to the trades CSV file
def csvlog(df, filename):
    headers = ['timestamp','Open','High','Low','Close','Volume', 'buySignal', 'shortSignal']
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)


    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = df.index[-1]
        row_to_write = [timestamp] + df.iloc[-2].tolist()
        writer.writerow(row_to_write)

# code for appending a new row to the trades CSV file
def buycsv(df, buyprice,filename):
    headers = ['timestamp', 'buyprice', 'sellprice', 'profit%']
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)


    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        buy_price = buyprice # replace with actual buy price
        sell_price =  "position still open"# replace with actual sell price
        profit_percentage = "nan" #((sell_price - buy_price) / buy_price) * 100
        timestamp = df.index[-1]
        writer.writerow([timestamp,buy_price,sell_price,profit_percentage])
        


def sellcsv(df, buyprice, sellprice, filename):
    headers = ['timestamp', 'buyprice', 'sellprice', 'profit%']
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        buy_price = buyprice # replace with actual buy price
        sell_price =  sellprice # replace with actual sell price
        profit_percentage = ((sell_price - buy_price) / buy_price) * 100
        timestamp = df.index[-1]
        writer.writerow([timestamp,buy_price,sell_price,profit_percentage])


# asset = 0
# balance = np.nan
def in_pos(coin):
    balance = exchange.fetch_balance()['info']['balances']
    try:
        asset = float([i['free'] for i in balance if i['asset'] == coin][0])
        if asset > 0:
            in_position = True
        else:
            in_position = False
    except Exception as e:
        print(e)
        in_position = False
        asset = 0
    return in_position, balance, asset


def read_buyprice(filename):
    try:
        trades = pd.read_csv(filename)
        buyprice = trades['buyprice'].iloc[-1]
    except:
        buyprice = np.nan
    return buyprice

import json

def update_dict_value(filename, key, value):
    with open(filename, 'r') as f:
        d = json.load(f)
    d[key] = value
    with open(filename, 'w') as f:
        json.dump(d, f)

# # update the json files
# pos = in_pos("BTC")
# in_position = pos[0]
# update_dict_value('pos.json', 'btc4h', in_position)

# qty = pos[2]
# update_dict_value('qty.json', 'btc4h', qty)

# trades = exchange.fetch_trades('ETHUSDT')[-2:]
# print(trades)


# async def get_qty(coin):
#     balance = exchange.fetch_balance()
#     qty = [float(item['free']) for item in balance['info']['balances'] if item['asset'] == coin][0]
#     return qty

# async def main():
#     qty_task = asyncio.create_task(get_qty(coin))
#     qty_task2 =  asyncio.create_task(getqty(coin))
#     qty = await qty_task
#     print(servertime())
#     qty2 = await qty_task2
#     print(servertime())
#     print(qty)
#     print(f"qty = {qty2}")


# asyncio.run(main())