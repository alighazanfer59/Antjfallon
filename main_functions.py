import ccxt
import streamlit as st
import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot
import pandas as pd
import pandas_ta as ta
import numpy as np
import csv
import os
import time
import json
import subprocess
import importlib
import kraken_config

# If you want to update the module:
importlib.reload(kraken_config)
from kraken_config import *
# def krakenActive():
#     exchange = ccxt.krakenfutures({
#         'apiKey': apiKey,
#         'secret': secret,
#         'verbose': False,  # switch it to False if you don't want the HTTP log
#     })
#     exchange.set_sandbox_mode(True)  # enable sandbox mode for testnet otherwise set to False
#     #     'enableRateLimit': True,
#     #     'rateLimit': 10000,
#     #     'options': {
#     #         # 'recvWindow': 9000,  # replace with your desired recv_window value
#     #         'test': False,  # use testnet (sandbox) environment
#     #         # 'adjustForTimeDifference': True,
#     #     },
#     #     'futures': {
#     #         'postOnly': False,  # Change to True if you want to use post-only orders
#     #         'leverage': 10,     # Set your desired leverage value
#     #         # You can add more futures-specific options here as needed
#     #     }
#     # })

#     # Uncomment the line below if you want to enable trading on the testnet (sandbox)
#     # exchange.set_sandbox_mode(enable=True)

#     return exchange
# Function to set API key and secret in kraken_config.py

# Function to set sandbox_mode in kraken_config.py
def set_sandbox_mode(sandbox_mode):
    # Path to your kraken_config.py file
    config_path = 'kraken_config.py'
    with open(config_path, 'r') as config_file:
        config_lines = config_file.readlines()

    with open(config_path, 'w') as config_file:
        for line in config_lines:
            if line.startswith('sandbox_mode'):
                config_file.write(f'sandbox_mode = {sandbox_mode}\n')
            else:
                config_file.write(line)


def set_api_key_secret(api_key, secret_key, config_path, live_mode=False):
    with open(config_path, 'r') as config_file:
        config_lines = config_file.readlines()

    with open(config_path, 'w') as config_file:
        for line in config_lines:
            if line.startswith('sandbox_mode'):
                if live_mode:
                    config_file.write(f'sandbox_mode = False\n')
                else:
                    config_file.write(f'sandbox_mode = True\n')
            elif line.startswith('live_apiKey'):
                if live_mode:
                    config_file.write(f'live_apiKey = \'{api_key}\'\n')
                else:
                    config_file.write(f'demo_apiKey = \'{api_key}\'\n')
            elif line.startswith('live_secret'):
                if live_mode:
                    config_file.write(f'live_secret = \'{secret_key}\'\n')
                else:
                    config_file.write(f'demo_secret = \'{secret_key}\'\n')
            else:
                config_file.write(line)

def get_api_key_secret(config_path, live_mode=False):
    with open(config_path, 'r') as config_file:
        config_lines = config_file.readlines()
        for line in config_lines:
            if live_mode and line.startswith('live_apiKey'):
                api_key = line.split('=')[1].strip()
            elif not live_mode and line.startswith('demo_apiKey'):
                api_key = line.split('=')[1].strip()
            if live_mode and line.startswith('live_secret'):
                secret_key = line.split('=')[1].strip()
            elif not live_mode and line.startswith('demo_secret'):
                secret_key = line.split('=')[1].strip()
    
    return api_key, secret_key

def check_authentication(exchange):
    try:
        balance = exchange.fetch_balance()  # Replace with an actual API request
        # If the request succeeds, the authentication is correct
        return True

    except ccxt.AuthenticationError as e:
        # Handle authentication errors
        return False

    except ccxt.NetworkError as e:
        # Handle network errors
        return False

    except Exception as e:
        # Handle other exceptions
        return False

def krakenActive(mode):
    # Set sandbox mode based on the selected mode
    if mode == "Sandbox/Demo":
        sandbox_mode = True
    else:
        sandbox_mode = False

    # Get the API key and secret based on the selected mode
    config_path = 'kraken_config.py'
    live_mode = mode == "Live"
    api_key, secret_key = get_api_key_secret(config_path, live_mode=live_mode)

    # Configure the ccxt.krakenfutures instance
    exchange = ccxt.krakenfutures({
        'apiKey': api_key.strip("'"),
        'secret': secret_key.strip("'"),
        'verbose': False,  # switch it to False if you don't want the HTTP log
    })

    # Enable or disable sandbox mode based on the selected mode
    exchange.set_sandbox_mode(sandbox_mode)

    # Check if the API key and secret are authenticated
    if check_authentication(exchange):
        # Authentication successful
        _message = ('Authentication Successful')
        print(_message)  # Print the error to the console
            
        return exchange

    else:
        # Authentication failed
        e_message = "Authentication failed due to invalid key or secret."
        print(e_message)  # Print the error to the console
        
        return None

# Function to check authentication and display messages
def check_authentication_and_display(mode_choice):
    # Create a new instance of the Kraken exchange
    exchange = krakenActive(mode_choice)

    if exchange:
        # Authentication successful
        _message = 'Authentication Successful'
        success_message = st.success(_message)
        time.sleep(5)  # Wait for 5 seconds
        success_message.empty()  # Clear the success message
    else:
        # Authentication failed
        error_message = "Authentication failed due to invalid key or secret."
        error_message = st.error(error_message)
        time.sleep(5)  # Wait for 5 seconds
        error_message.empty()  # Clear the error message
    
    return exchange


# st.write('mode is set to : ', mode)
# exchange = krakenActive(mode)


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
    print(size)
    amount = round(size, 3)  # Round to 8 decimal places

    print('Order Size:', amount)
    
    return amount



# { ==========================================================================================
# Load historical price data from kraken exchange, but data is limited to 720 candles 

kraken = ccxt.kraken()
def start_time(days):
    timestamp = kraken.fetch_time() - days*86400*1000
    time = pd.to_datetime(timestamp, unit ='ms')
    print('Start Time', time)
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


def create_marker_trace(df, column_name, marker_symbol, y_column, y_percentage_offset, text_label, name, color):
    filtered_df = df[df[column_name]]
    
    # Calculate the vertical offset based on the percentage of the price range
    price_range = df['High'].max() - df['Low'].min()
    y_offset = y_percentage_offset * price_range

    markers = go.Scatter(
        x=filtered_df.index,
        y=filtered_df[y_column] + y_offset,
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


def create_background_shapes(df, trend_column, bg_colors):
    background_shapes = []
    current_trend = None  # Set an initial default trend
    start_index = None

    for index, row in df.iterrows():
        trend = row[trend_column]
        
        # Check if trend is not 'nan' and not equal to the current trend
        if not pd.isna(trend) and trend != current_trend:
            if current_trend is not None:
                end_index = index
                bg_color = bg_colors.get(current_trend, 'gray')  # Use 'gray' for unknown trends
                shape = {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': start_index,
                    'x1': end_index,
                    'y0': 0,
                    'y1': 1,
                    'fillcolor': bg_color,
                    'opacity': 0.15,  # Adjust opacity as needed
                    'line': {
                        'width': 0,
                    }
                }
                background_shapes.append(shape)
            
            start_index = index
            current_trend = trend

    # Add the last shape
    if start_index is not None:
        end_index = df.index[-1]
        bg_color = bg_colors.get(current_trend, 'gray')  # Use 'gray' for unknown trends
        shape = {
            'type': 'rect',
            'xref': 'x',
            'yref': 'paper',
            'x0': start_index,
            'x1': end_index,
            'y0': 0,
            'y1': 1,
            'fillcolor': bg_color,
            'opacity': 0.15,  # Adjust opacity as needed
            'line': {
                'width': 0,
            }
        }
        background_shapes.append(shape)

    return background_shapes

def plot_labels_high_low(df, label_params, fig, side):
    variables = get_variables(side, df)
    # Create variables with keys as variable names and values as column names
    for variable_name, column_name in variables.items():
        globals()[variable_name] = column_name
        
    for label, params in label_params.items():
        label_data = pd.DataFrame()
        
        # Filter the DataFrame for 'sw_highs' and 'sw_lows' conditions
        high_mask = (df[sw_highs] == label) & df[sw_top]
        low_mask = (df[sw_lows] == label) & df[sw_bottom]
        
        label_data = pd.concat([df[high_mask], df[low_mask]])

        if not label_data.empty:
            # Calculate the price range percentage offset
            price_range = df['High'].max() - df['Low'].min()
            y_percentage_offset = 0.02  # Adjust this percentage as needed

            # Calculate the vertical offset based on the percentage of the price range
            label_data['y_position'] = label_data['Low'] - (y_percentage_offset * price_range)
            label_data.loc[high_mask, 'y_position'] = label_data['High'] + (y_percentage_offset * price_range)

            scatter = go.Scatter(
                x=label_data.index,
                y=label_data['y_position'],
                mode='text',
                text=label.upper(),
                textfont=dict(color=params['color'], size=12),
                name=label.upper(),
                textposition=params['textposition']
            )

            fig.add_trace(scatter)
            


def create_zigzag_trace(df, sw_top_column, sw_bottom_column, uptrend_color, downtrend_color):
    zigzag_x = []
    zigzag_y = []
    zigzag_colors = []
    current_trend = None
    prev_trend = None
    zigzag_color = uptrend_color

    for index, row in df.iterrows():
        if row[sw_top_column]:
            current_trend = 1
            zigzag_color = uptrend_color
        elif row[sw_bottom_column]:
            current_trend = -1
            zigzag_color = downtrend_color

        if current_trend != prev_trend:
            zigzag_x.append(index)
            zigzag_y.append(row['High'] if current_trend == 1 else row['Low'])

        prev_trend = current_trend

    zigzag_trace = go.Scatter(
        x=zigzag_x,
        y=zigzag_y,
        mode='lines',
        line=dict(width=2, color=zigzag_color),  # Set the color of the zigzag line based on the current trend
        name='Zigzag Line',
        hoverinfo='none'
    )

    return zigzag_trace

# code for appending a new row to the trades CSV file
def csvlog(df, filename):
    headers = df.columns.tolist()
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = df.index[-1]
        row_to_write = [timestamp] + [df[column].iloc[-1] for column in headers]
        writer.writerow(row_to_write)

# code for appending a new row to the trades CSV file
def buycsv(df, buyprice, sellprice, filename):
    headers = ['timestamp', 'buyprice', 'sellprice', 'profit%']
    
    if not os.path.isfile(filename):
        with open(filename, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)


    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        buy_price = buyprice # replace with actual buy price
        sell_price =  sellprice# replace with actual sell price
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


def read_tradefile(filename, position_type):
    try:
        trades = pd.read_csv(filename)
        if position_type == 'long':
            price_column = 'buyprice'
        elif position_type == 'short':
            price_column = 'sellprice'
        else:
            raise ValueError("Invalid position_type. Use 'long' or 'short'.")

        price = trades[price_column].iloc[-1]
    except:
        price = np.nan
    return price


def update_dict_value(filename, key, value):
    with open(filename, 'r') as f:
        d = json.load(f)
    d[key] = value
    with open(filename, 'w') as f:
        json.dump(d, f)

# Define the map_timeframe function (you've already provided this)
def map_timeframe(resolution, get_value=True):
    tf_mapping = {
        '1min': '1m',
        '2min': '2m',
        '3min': '3m',
        '5min': '5m',
        '15min': '15m',
        '30min': '30m',
        '45min': '45m',
        '1hour': '1h',
        '4hour': '4h',
        '6hour': '6h',
        '12hour': '12h',
        '1day': '1d',
        '1week': '1w'
    }
    
    if get_value:
        return tf_mapping.get(resolution, '1d')  # Default to '1d' if not found
    else:
        # If you want to reverse map from value to resolution, you can do this:
        reverse_mapping = {v: k for k, v in tf_mapping.items()}
        return reverse_mapping.get(resolution, '1day')  # Default to '1day' if not found

def calculate_balance(exchange, currency_code, percentage=0.20):
    try:
        # Fetch the balance from the exchange
        balance = exchange.fetch_balance()
        # Extract the free balance for the specified currency
        free_balance = balance[currency_code]['free']
        # Calculate the amount to use (20% of free balance)
        amount_to_use = free_balance * percentage
        # Extract the BTC free balance
        btc_free_balance = balance['BTC']['free']
        # Return the results
        return amount_to_use, free_balance, btc_free_balance

    except (KeyError, ccxt.BaseError) as e:
        # Handle errors, such as currency code not found or exchange fetch_balance error
        print(f"An error occurred: {e}")
        return None, None, None

def place_market_order(symbol, amount, tp_perc, order_type, position_type):
    global in_position, buy_pos, sell_pos  # Ensure we modify the global variables

    # # Determine position size
    # amount = calculate_order_size(symbol, usdt_amount)
    # # amount = round(position_size, 3)

    try:
        if order_type == 'buy':
            response = exchange.create_market_buy_order(
                symbol=symbol,
                amount=amount
            )
            buy_pos = True  # Set buy_pos to True for Long
        else:
            response = exchange.create_market_sell_order(
                symbol=symbol,
                amount=amount
            )
            sell_pos = True  # Set sell_pos to True for Short

        # Extract order information
        order_id = response['info']['order_id']
        price = float(response['price'])
        amount = float(response['amount'])
        side = response['side']

        print(f"Order ID: {order_id}")
        print(f"{order_type.capitalize()} Price: {price}")
        print(f"Amount: {amount}")
        print(f"Side: {side}")

        in_position = True
        tp = price * (1 + tp_perc) if order_type == 'buy' else price * (1 - tp_perc)
        limit = np.nan
        status = "In Position"
        
        print(f"Market {order_type.capitalize()} Order Placed at Market Price")
        print(response)

        # Save the order information
        order_info = {
            'order_id': order_id,
            'buyprice' if order_type == 'buy' else 'sellprice': price,
            'amount': amount,
            'side': side,
            'tp': tp,
            'limit': limit,
            'status': status,
            'position_type': position_type
        }
        with open('order_info.json', 'w') as order_file:
            json.dump(order_info, order_file)
    except ccxt.BaseError as e:
        print("An error occurred:", e)

# Define a function to close a position
def close_position(symbol, amount, order_type, position_type, limit=None):
    try:
        if order_type == 'buy':
            response = exchange.create_market_sell_order(
                symbol=symbol,
                amount=amount
            )
        else:
            response = exchange.create_market_buy_order(
                symbol=symbol,
                amount=amount
            )

        # Extract the required information
        order_id = response['info']['order_id']
        price = float(response['price'])
        amount = float(response['amount'])
        side = response['side']

        print(f"Order ID: {order_id}")
        print(f"Price: {price}")
        print(f"Amount: {amount}")
        print(f"Side: {side}")

        print(f"{position_type.capitalize()} Position Closed at Market Price")

        # Save the order information
        order_info = {
            'order_id': order_id,
            'price': price,
            'amount': amount,
            'side': side,
            'status': 'Closed',
            'position_type': position_type
        }
        with open('order_info.json', 'w') as order_file:
            json.dump(order_info, order_file)
    except ccxt.BaseError as e:
        print("An error occurred:", e)

def calculate_candle_type(df):
    df['candle_type'] = np.where(
        (df['High'] > df['High'].shift(1)) &
        (df['Low'] > df['Low'].shift(1)),
        "up_bar",
        np.where(
            (df['High'] < df['High'].shift(1)) &
            (df['Low'] < df['Low'].shift(1)),
            "down_bar",
            np.where(
                (df['High'] > df['High'].shift(1)) &
                (df['Low'] < df['Low'].shift(1)) &
                (df['Open'] > df['Close']),
                "outside_up_dn",
                np.where(
                    (df['High'] > df['High'].shift(1)) &
                    (df['Low'] < df['Low'].shift(1)) &
                    (df['Open'] < df['Close']),
                    "outside_dn_up",
                    ""
                )
            )
        )
    )

def calculate_gann_signals(df, max_sw_cnt = 3, exit_perc = (80*0.01), side = "long"):
    # print(f'Exit percentage {side}: {exit_perc}')
    calculate_candle_type(df)
    
    # Initialize p_cnt with a list containing the initial value (0) for the first row
    p_cnt_values = [0]

    # Iterate over the rows of the DataFrame starting from the second row (index 1)
    for i in range(1, len(df)):
        # Get the current candlestick type for the current row
        current_candle_type = df['candle_type'].iloc[i]

        # Get the previous sw_cnt value (p_cnt) for the current row
        previous_sw_cnt = p_cnt_values[i - 1]

        # Initialize a variable to store the new sw_cnt value
        new_sw_cnt = None

        # Check various conditions to determine the new sw_cnt value
        if (current_candle_type == "up_bar" and previous_sw_cnt < 0) or (current_candle_type == "outside_dn_up" and previous_sw_cnt < 0):
            new_sw_cnt = 1
        elif current_candle_type == "up_bar" and previous_sw_cnt < max_sw_cnt:
            new_sw_cnt = previous_sw_cnt + 1
        elif current_candle_type == "up_bar" and previous_sw_cnt == max_sw_cnt:
            new_sw_cnt = max_sw_cnt
        elif (current_candle_type == "down_bar" and previous_sw_cnt > 0) or (current_candle_type == "outside_up_dn" and previous_sw_cnt > 0):
            new_sw_cnt = -1
        elif current_candle_type == "down_bar" and previous_sw_cnt > -max_sw_cnt:
            new_sw_cnt = previous_sw_cnt - 1
        elif current_candle_type == "down_bar" and previous_sw_cnt == -max_sw_cnt:
            new_sw_cnt = -max_sw_cnt
        elif current_candle_type == "outside_dn_up" and previous_sw_cnt > 0:
            new_sw_cnt = previous_sw_cnt
        elif current_candle_type == "outside_up_dn" and previous_sw_cnt < 0:
            new_sw_cnt = previous_sw_cnt
        else:
            # If none of the conditions are met, keep the sw_cnt unchanged
            new_sw_cnt = previous_sw_cnt

        # Append the new sw_cnt value to the list of sw_cnt values
        p_cnt_values.append(new_sw_cnt)

    # Check if the length of sw_cnt values matches the number of rows in df
    if len(p_cnt_values) == len(df):
        # Assign the list of sw_cnt values to a new column 'sw_cnt' in df
        df[f'sw_cnt_{side}'] = p_cnt_values
    else:
        print("Length mismatch error between p_cnt_values and df.")

    # Initialize sw_trend with NaN
    df[f'sw_trend_{side}'] = np.nan

    # Create mask1 and mask2
    mask1 = (
        ((df[f'sw_cnt_{side}'] == -(max_sw_cnt)) |
         ((df[f'sw_cnt_{side}'] == 1) & (df['candle_type'] == 'outside_dn_up'))) &
        (df[f'sw_cnt_{side}'].shift(1) == -(max_sw_cnt-1))  # & (df['sw_trend'].shift(1) != df['sw_trend'])
    )

    mask2 = (
        ((df[f'sw_cnt_{side}'] == (max_sw_cnt)) |
         ((df[f'sw_cnt_{side}'] == -1) & (df['candle_type'] == 'outside_up_dn'))) &
        (df[f'sw_cnt_{side}'].shift(1) == (max_sw_cnt-1))  # & (df['sw_trend'].shift(1) != df['sw_trend'])
    )

    # Update sw_trend based on mask1 and mask2
    df.loc[mask1, f'sw_trend_{side}'] = -1
    df.loc[mask2, f'sw_trend_{side}'] = 1

    # Forward fill the sw_trend column to carry forward the last value
#     df[f'sw_trend_{side}'].ffill(inplace=True)

    trend_cnt = [0]

    # Initialize sw_top column with False
    df[f'sw_top_{side}'] = False
    df[f'sw_bottom_{side}'] = False

    prev_high = float('inf')
    prev_low = 0

    # Calculate the maximum High value of past n candles when mask1 is true
    for i in range(len(df)):
        
        df[f'sw_trend_{side}'].iloc[:i+1] = df[f'sw_trend_{side}'].iloc[:i+1].ffill()
        if i == 0:
            trend_cnt.append(1)
    #         print(i, "first candle ", trend_cnt[i])
        elif df[f'sw_trend_{side}'].iloc[i - 1] == df[f'sw_trend_{side}'].iloc[i]:
            trend_cnt.append((trend_cnt[-1]) + 1)
    #         print(i, "trend continues ", trend_cnt[i], trend_cnt[i - 1], df.index[i])
        else:
            trend_cnt.append(1)
    #         print(i, "trend reverses ", trend_cnt[i])
        
        if i <= len(df):
            if mask1[i] & (df[f'sw_trend_{side}'].iloc[i - 1] != df[f'sw_trend_{side}'].iloc[i]):
                # Calculate the maximum High and its index
                high_range = df.loc[
                    df.index[max(0, i - int(trend_cnt[i]))]:df.index[i - 1]]['High']
                max_high = high_range.max()
                if not high_range.empty:
                    max_high_index = high_range.idxmax()
                    prev_high = max_high
                    # Mark the row where max_high occurs as True
                    df.at[max_high_index, f'sw_top_{side}'] = True
                else:
                    pass
                # print(df.index[i], "logic 1")

            elif mask2[i] & (df[f'sw_trend_{side}'].iloc[i - 1] != df[f'sw_trend_{side}'].iloc[i]):
                # Calculate the maximum High and its index
                low_range = df.loc[
                    df.index[max(0, i - int(trend_cnt[i]))]:df.index[i - 1]]['Low']
                min_low = low_range.min()
                if not high_range.empty:
                    min_low_index = low_range.idxmin()
                    prev_low = min_low
                    # Mark the row where max_high occurs as True
                    df.at[min_low_index, f'sw_bottom_{side}'] = True
                else:
                    pass
                # print(df.index[i], "logic 2")

            elif (df['High'][i] > prev_high) & (df[f'sw_trend_{side}'].iloc[i] == -1):
                low_range = df.loc[
                    df.index[max(0, i - int(trend_cnt[i]))]:df.index[i]]['Low']
                min_low = low_range.min()
                min_low_index = low_range.idxmin()
                prev_low = min_low
                df.at[min_low_index, f'sw_bottom_{side}'] = True
                df[f'sw_trend_{side}'].iloc[i] = 1
                # print(df.index[i], "logic 3")

            elif (df['Low'][i] < prev_low) & (df[f'sw_trend_{side}'].iloc[i] == 1):
                high_range = df.loc[
                    df.index[max(0, i - int(trend_cnt[i]))]:df.index[i]]['High']
                max_high = high_range.max()
                max_high_index = high_range.idxmax()
                prev_high = max_high
                # Mark the row where max_high occurs as True
                df.at[max_high_index, f'sw_top_{side}'] = True
                df[f'sw_trend_{side}'].iloc[i] = -1
                # print(df.index[i], "logic 4")
            # print(df.index[i], prev_high, prev_low, df[f'sw_trend_{side}'][i])

# Append a 0 at the beginning to match the length of the DataFrame
# trend_cnt.insert(0, 0)

    df[f'trend_cnt_{side}'] = trend_cnt[:-1]

    df[f'sw_high_price_{side}'] = np.where(
        df[f'sw_top_{side}'] == True, df['High'], np.nan)
    df[f'sw_high_price_{side}'].fillna(method='ffill', inplace=True)
    df[f'sw_low_price_{side}'] = np.where(
        df[f'sw_bottom_{side}'] == True, df['Low'], np.nan)
    df[f'sw_low_price_{side}'].fillna(method='ffill', inplace=True)

    # Filter rows where sw_top is True and calculate sw_highs
    df_tops = df[df[f'sw_top_{side}'] == True].copy()
    df_tops[f'sw_highs_{side}'] = np.where(
        df_tops['High'] > df_tops['High'].shift(1), "HH", "LH")

    # Filter rows where sw_bottom is True and calculate sw_lows
    df_bottoms = df[df[f'sw_bottom_{side}'] == True].copy()
    df_bottoms[f'sw_lows_{side}'] = np.where(
        df_bottoms['Low'] < df_bottoms['Low'].shift(1), "LL", "HL")

    # Concatenate the DataFrames and select the desired columns
    df_swings = pd.concat([df_tops, df_bottoms], axis=1)
#     print(df_swings)
    df_swings[f'trend_{side}'] = np.nan
    df_swings[f'trend_{side}'] = np.where(((df_swings[f'sw_highs_{side}'] == 'HH') & (df_swings[f'sw_lows_{side}'].shift(1) == 'HL')) |
                                  ((df_swings[f'sw_lows_{side}'] == 'HL') & (df_swings[f'sw_highs_{side}'].shift(1) == 'HH')),
                                   "UP",
                                   np.where(((df_swings[f'sw_lows_{side}'] == 'LL') & (df_swings[f'sw_highs_{side}'].shift(1) == 'LH')) |
                                            ((df_swings[f'sw_highs_{side}'] == 'LH') & (df_swings[f'sw_lows_{side}'].shift(1) == 'LL')),
                                            "DOWN",
                                            np.where(((df_swings[f'sw_lows_{side}'] == 'LL') & (df_swings[f'sw_highs_{side}'].shift(1) == 'HL')) |
                                                     ((df_swings[f'sw_lows_{side}'] == 'LL') & (df_swings[f'sw_highs_{side}'].shift(1) == 'HH')) |
                                                     ((df_swings[f'sw_lows_{side}'] == 'HL') & (df_swings[f'sw_highs_{side}'].shift(1) == 'LH')) |
                                                     ((df_swings[f'sw_highs_{side}'] == 'LH') & (df_swings[f'sw_lows_{side}'].shift(1) == 'HL')) |
                                                     ((df_swings[f'sw_highs_{side}'] == 'HH') & (df_swings[f'sw_lows_{side}'].shift(1) == 'LL')),
                                                     "UNCERTAIN",
                                                     np.nan
                                                    )
                                                 )
                                             )


    df_swings = df_swings[[f"sw_highs_{side}", f"sw_lows_{side}", f"trend_{side}"]]

    df_ffill = pd.concat([df, df_swings], axis=1)

    # Define the columns to be copied
    columns_to_copy = [f"sw_highs_{side}", f"sw_lows_{side}", f"trend_{side}"]

    # Forward fill columns in df_ffill
    df_ffill[columns_to_copy] = df_ffill[columns_to_copy].fillna(method='ffill')

    # Drop the columns to be replaced from df
    for column in columns_to_copy:
        if column in df.columns:
            df.drop(columns=column, inplace=True)

    # Update the original DataFrame with the filled columns
    df = pd.concat([df, df_ffill[columns_to_copy]], axis=1)

    df[f'trend_{side}'] = np.where(
                            ((df[f'sw_lows_{side}'] == 'HL') & (df['High'] > df[f'sw_high_price_{side}'])),
                               "UP",
                               np.where(((df[f'sw_highs_{side}'] == 'LH') & (df['Low'] < df[f'sw_low_price_{side}'])),
                                        "DOWN",
                                        df[f'trend_{side}']
                                       )
                            )
    # df['trend'].fillna(method='ffill', inplace=True)
    if side == "long":
        df[f'tsl_{side}'] = df[f'sw_low_price_{side}'].shift(1)
        df[f'{side}_entry'] = df[f'sw_high_price_{side}'].shift(1)
        
        df[f"{side}_Signal"] = np.where(
                            ((df[f'sw_lows_{side}'] == "HL") | ((df[f'sw_highs_{side}'] == "HH") & (df[f'sw_lows_{side}'] == "HL"))) & 
                            ((df['High'] > df[f'sw_high_price_{side}'].shift(1)) &
                            (df['High'].shift(1) < df[f'sw_high_price_{side}'].shift(1)) &
                            ((df[f'trend_{side}'].shift(1) == "UNCERTAIN") | (df[f'trend_{side}'] == "UP"))),
                            True,
                            False
                            )
        
        df[f"{side}_Exit"] = np.where((df[f'sw_highs_{side}'] == "LH") & 
                            (df[f'sw_trend_{side}'].shift(2) == 1.0) &
                            (df[f'sw_trend_{side}'].shift(1) == -1.0) & (df[f'sw_trend_{side}'] == -1.0) &
                            (df[f'trend_{side}'] == "UNCERTAIN"),  
                            ((df[f'sw_high_price_{side}'] - df[f'sw_low_price_{side}'])*exit_perc + df[f'sw_low_price_{side}']), 
                                np.nan)
        
        df["pi_top"] = np.where(
                            (df['Open'].rolling(window=111).mean()) > (df['Open'].rolling(window=350).mean() * 2), 
                            True, 
                            False
                            )
    
        
    else:
        df[f'tsl_{side}'] = df[f'sw_high_price_{side}'].shift(1)
        df[f'{side}_entry'] = df[f'sw_low_price_{side}'].shift(1)
        
        df[f"{side}_Signal"] = np.where(
                            ((df[f'sw_highs_{side}'] == "LH") | ((df[f'sw_lows_{side}'] == "LL") & (df[f'sw_highs_{side}'] == "LH"))) & 
                            (df['Low'] < df[f'sw_low_price_{side}'].shift(1)) &
                            (df['Low'].shift(1) > df[f'sw_low_price_{side}'].shift(1)) &
                            ((df[f'trend_{side}'].shift(1) == "UNCERTAIN") | (df[f'trend_{side}'] == "DOWN")),  
                            True, 
                            False
                            )

        df[f"{side}_Exit"] = np.where((df[f'sw_lows_{side}'] == "HL") & 
                            (df[f'sw_trend_{side}'].shift(2) == -1.0) &
                            (df[f'sw_trend_{side}'].shift(1) == 1.0) & (df[f'sw_trend_{side}'] == 1.0) &
                            (df[f'trend_{side}'] == "UNCERTAIN"),  
                            (df[f'sw_high_price_{side}'] - (df[f'sw_high_price_{side}'] - df[f'sw_low_price_{side}'])*exit_perc), 
                                np.nan)    

        df["pi_bottom"] = np.where(
                            (df['Close'].rolling(window=550).mean() > df['Close'].rolling(window=250).mean()), 
                            True, 
                            False
                            )
#     for i in range(len(df)):
#         if df[f'sw_trend_{side}'][i] == np.nan:
#             df[f'sw_top_{side}'][i] = False
#             df[f'sw_bottom_{side}'][i] = False
#         else:
#             pass
    
#     st.write(df[300:500])
    
    return df

def backtest(exchange, df, ticker, direction='Both', commission=0.04/100, tp_perc_long=0, tp_perc_short=0, pi_exit_long=True, pi_exit_short=False, 
             tsl_offset_long_en=True, tsl_offset_short_en=True, tsl_offset_long_pct=0.1/100, tsl_offset_short_pct=0.1/100, 
             init_sl_offset_long=0.1/100, init_sl_offset_short=0.1/100, initial_capital=10000, method_type='Fixed', price_type='Percentage', value=20):
    
    in_position = False
    buy_pos = False
    sell_pos = False
    is_hit_buy_pos = False
    is_hit_sell_pos = False
    # Initialize current_balance as a list with the initial capital
    current_balance = [initial_capital]
    position_sizes = []
    profit_or_loss = []
    balance_in_use = 0  # Initialize profit_or_loss to 0

    results_df = pd.DataFrame()
    buydates, buyprices = [], []
    selldates, sellprices = [], []
    exit_types = []

    for index, row in df.iterrows():
        balance_in_use = 0  # Reset balance_in_use to 0 before calculating for new trades
        # profit_or_loss = 0
# ---------------------------------------------long position close check------------------------------
        if in_position and buy_pos:
            
            tsl = row.tsl_long*(1-tsl_offset_long)
            sl = max(init_sl, tsl)
            if (row.Low <= sl):
                selldates.append(index)
                sellprices.append(sl)
                in_position = False
                buy_pos = False
                is_hit_buy_pos = True
                exit_types.append("SL Hit")
            elif (row.High >= tp) and (tp_perc_long != 0):
                selldates.append(index)
                sellprices.append(tp)
                in_position = False
                buy_pos = False
                is_hit_buy_pos = True
                exit_types.append("TP Hit")
            elif (row.pi_top) and (pi_exit_long):
                selldates.append(index)
                sellprices.append(row.Close)
                in_position = False
                buy_pos = False
                is_hit_buy_pos = True
                exit_types.append("Pi Cycle")
            elif row.long_Exit > 0:
                limit = row.long_Exit
                if row.Low <= limit:
                    selldates.append(index)
                    sellprices.append(limit)
                    in_position = False
                    buy_pos = False
                    is_hit_buy_pos = True
                    exit_types.append("Limit price Hit due to uncertain trend")
            if is_hit_buy_pos:
                pnl = sellprices[-1] - buyprices[-1]
                pnl *= position_sizes[-1]
                profit_or_loss.append(pnl)
                current_balance.append(current_balance[-2] + pnl)
                balance_in_use = 0
    # ---------------------------------------------short position close check------------------------------
        elif in_position and sell_pos:
            tsl = row.tsl_short*(1+tsl_offset_short)
            sl = min(init_sl, tsl)
            if (row.High >= sl):
                buydates.append(index)
                buyprices.append(sl)
                in_position = False
                sell_pos = False
                is_hit_sell_pos = True
                exit_types.append("SL Hit")
                
            elif (row.Low <= tp) and (tp_perc_short != 0):
                buydates.append(index)
                buyprices.append(tp)
                in_position = False
                buy_pos = False
                is_hit_sell_pos = True
                exit_types.append("TP Hit")
            elif (row.pi_bottom) and (pi_exit_short):
                buydates.append(index)
                buyprices.append(row.Close)
                in_position = False
                buy_pos = False
                is_hit_sell_pos = True
                exit_types.append("Pi Cycle")
            elif row.short_Exit > 0:
                limit = row.short_Exit
                if row.High >= limit:
                    buydates.append(index)
                    buyprices.append(limit)
                    in_position = False
                    buy_pos = False
                    is_hit_sell_pos = True
                    exit_types.append("Limit price Hit due to uncertain trend")
            if is_hit_sell_pos:
                pnl = sellprices[-1] - buyprices[-1]
                pnl *= position_sizes[-1]
                profit_or_loss.append(pnl)
                current_balance.append(current_balance[-2] + pnl)
                balance_in_use = 0
            
            # print(limit, in_position)
    # ======================================================================================================              
                
    # ---------------------------------------------long position entry check------------------------------
        position_size = None
        buyprice = 0
        sellprice = 0  
        if not in_position:
            if direction in ("Both", "Long") and row.long_Signal and not row.pi_top:
                buyprice = row.long_entry
                buydates.append(index)
                buyprices.append(buyprice)
                in_position = True
                buy_pos = True
                is_hit_buy_pos = False
                tp = buyprice * (1 + tp_perc_long)
                limit = np.nan
                init_sl = row.tsl_long*(1-init_sl_offset_long)
                tsl_offset_long = tsl_offset_long_pct if tsl_offset_long_en == True else 0
                position_size = calculate_position_size(method_type, price_type, value, init_sl, ticker, exchange, 
                                                        backtest=True, 
                                                        current_balance=current_balance[-1],  # Your current balance during backtest
                                                        entry_price=buyprice
                                                        )
                position_sizes.append(position_size)
                # Calculate the amount in use based on the position size
                balance_in_use = position_size * buyprice
                current_balance.append(current_balance[-1] - balance_in_use)  # Deduct the amount in use
            elif direction in ("Both", "Short") and row.short_Signal and not row.pi_bottom:
                sellprice = row.short_entry
                selldates.append(index)
                sellprices.append(sellprice)
                in_position = True
                sell_pos = True
                is_hit_sell_pos = False
                tp = sellprice / (1 + tp_perc_short)
                limit = np.nan
                init_sl = row.tsl_short*(1+init_sl_offset_short)
                tsl_offset_short = tsl_offset_short_pct if tsl_offset_short_en == True else 0
                position_size = calculate_position_size(method_type, price_type, value, init_sl, ticker, exchange, 
                                                        backtest=True, 
                                                        current_balance=current_balance[-1],  # Your current balance during backtest
                                                        entry_price=sellprice
                                                        )
                position_sizes.append(position_size)
                # Calculate the amount in use based on the position size
                balance_in_use = position_size * sellprice
                current_balance.append(current_balance[-1] - balance_in_use)  # Deduct the amount in use
                
            
    if len(buydates) == 0:
        print(f"No trades were made for {ticker}.")
    else:
        profits = [(sell - buy) / buy - commission for sell, buy in zip(sellprices, buyprices)]
        returns = ((pd.Series(profits, dtype=float) + 1).prod() - 1) * 100
        wins = 0
        for i in profits:
            if i > 0:
                wins += 1
            i += 1
        winrate = round((wins / len(buydates)) * 100, 2)
        ct = min(len(buydates), len(selldates))

        # BTCUSDT buy and hold returns during the same period
        buy_hold_ret = (df['Close'][-1] - df['Open'][0]) / df['Open'][0] * 100

        results_df = pd.concat([results_df, pd.DataFrame({'ticker': f'{ticker}', 'returns': [returns], 'winrate': [winrate], 'trades': [ct], 'buy&hold_ret%': [buy_hold_ret]})])
        st.subheader('Backtest Results')
        st.write(f'{ticker}, winrate={winrate}%, returns={round(returns, 2)}%, no. of trades = {ct}, buy&hold_ret = {round(buy_hold_ret, 2)}%')
    # Return the trade data along with other results
    return {
        'buydates': buydates,
        'buyprices': buyprices,
        'selldates': selldates,
        'sellprices': sellprices,
        'profits': profits,
        'Exit Type' : exit_types,
        'Position Size': position_sizes,
        'pnl': profit_or_loss,
        'current_balance': current_balance,
        # Other results...
    }, results_df

def displayTrades(direction="Both", **kwargs):
    # st.write('Direction: ', direction)
    # Access the trade data and other results from kwargs
    buydates = kwargs['buydates']
    buyprices = kwargs['buyprices']
    selldates = kwargs['selldates']
    sellprices = kwargs['sellprices']
    profits = kwargs['profits']
    exit_type = kwargs['Exit Type']
    position_sizes = kwargs['Position Size']
    profit_or_loss = kwargs['pnl']
    current_balance = kwargs['current_balance']

    ct = min(len(buydates), len(selldates))
    
    # Assuming current_balance is your list of balances
    exit_current_balances = current_balance[2::2]
    
    # Create a DataFrame to store the trades
    dfr = pd.DataFrame()
    dfr['buydates'] = buydates[:ct]
    dfr['buyprice'] = buyprices[:ct]
    dfr['selldates'] = selldates[:ct]
    dfr['sellprice'] = sellprices[:ct]
    dfr['profits'] = (profits[:ct])
    dfr['commulative_returns'] = ((pd.Series(profits) + 1).cumprod())
    dfr['Exit Type'] = exit_type[:ct]
    dfr['Position Size'] = position_sizes[:ct]
    dfr['Current Balance'] = exit_current_balances  # Add current_balance for each trade
    dfr['Profit/Loss'] = profit_or_loss
    
    # Add a column to indicate the trade side
    dfr['tradeSide'] = np.where(dfr['buydates'] < dfr['selldates'], 'Long', 'Short')
    dfr['Entry Date'] = np.where(dfr['tradeSide'] == 'Long', dfr['buydates'], dfr['selldates'])
    dfr['Exit Date'] = np.where(dfr['tradeSide'] == 'Long', dfr['selldates'], dfr['buydates'])

    dfr['Entry Price'] = np.where(dfr['tradeSide'] == 'Long', dfr['buyprice'], dfr['sellprice'])
    dfr['Exit Price'] = np.where(dfr['tradeSide'] == 'Long', dfr['sellprice'], dfr['buyprice'])
    
    # Create a list of column names with the desired display order
    display_order = ['Entry Date', 'Entry Price', 'Exit Date', 'Exit Price', 'profits', 'commulative_returns', 'Exit Type', 'Position Size', 'Current Balance', 'Profit/Loss', 'tradeSide']
    
    # Create a copy of the DataFrame with only the columns to be displayed
    dfr_display = dfr[display_order].copy()

    return dfr, dfr_display

def get_variables(side, df):
    # Initialize a dictionary to store variable names and corresponding column names
    variables = {}

    # Loop through the DataFrame columns
    for col in df.columns:
        if f'_{side}' in col:
            # Remove the side from the column name
            name_without_side = col.replace(f'_{side}', '')
            variables[name_without_side] = col

    return variables

def plot_advanced_gann_swing_chart(df, dfr, visible_data_points=250, side="long"):
    # Get the variables dictionary
    variables = get_variables(side, df)
    # Create variables with keys as variable names and values as column names
    for variable_name, column_name in variables.items():
        globals()[variable_name] = column_name
    
    # Determine the desired y-axis range based on your data
    y_min = df['Low'].min()  # Replace 'Low' with the appropriate column name
    y_max = df['High'].max()  # Replace 'High' with the appropriate column name

    bull_candle = '#e7bf4f'
    bearish_candle = '#497ad2'
    # Create a candlestick trace
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color=bull_candle,  # Bull candle outline color
        decreasing_line_color=bearish_candle,    # Bear candle outline color
        increasing_fillcolor=bull_candle,  # Bull candle fill color
        decreasing_fillcolor=bearish_candle,  # Bear candle fill color
        name='Candles',
    )

# Create text annotations for sw_cnt on top of each candle
    annotations = []

    # Create sw_top marker trace
    sw_top_markers = create_marker_trace(df, sw_top, 'triangle-up', 'High', 0.005, '', 'Trend Peaks', '#FF9800')

    # Create sw_bottom marker trace
    sw_bottom_markers = create_marker_trace(df, sw_bottom, 'triangle-down', 'Low', -0.005, '', 'Trend Bottoms', '#2962ff')

    # Define colors for each trend type
    bg_colors = {
        'UP': 'green',
        'DOWN': 'red',
        'UNCERTAIN': 'yellow'
    }

    opacity_up = 0.2
    opacity_down = 0.15
    opacity_uncertain = 0.15

    # Create background shapes based on the "trend" column
    background_shapes = create_background_shapes(df, trend, bg_colors)

    # Initially set the shapes property to an empty list to hide the background traces
    layout = go.Layout(
        shapes=[],  # Initially empty to hide the background traces
        showlegend=False,
    )

    # Define a button to toggle the visibility of background traces
    toggle_button = dict(
        type="buttons",
        showactive=True,
        buttons=[
            dict(label="Show Background Traces",
                    method="relayout",
                    args=["shapes", background_shapes]),
            dict(label="Hide Background Traces",
                    method="relayout",
                    args=["shapes", []]),  # Empty list to hide the shapes
        ],
        x=1.15,
        y=0.15,
    )
    layout["updatemenus"] = [toggle_button]

    # Define colors for uptrend and downtrend zigzag lines
    uptrend_color = '#FF9800'
    downtrend_color = '#FF9800'

    # Create the zigzag trace
    zigzag_trace = create_zigzag_trace(df, sw_top, sw_bottom, uptrend_color, downtrend_color)

    # Determine the number of data points to display by default
    num_data_points = min(len(df), visible_data_points)

    # Create a separate list for trailing stop loss shapes
    tsl_shapes = []

    # Plot trades and trailing stop-loss
    for _, trade in dfr.iterrows():
        side = trade['tradeSide']
        entry_date = trade['buydates'] if side == 'Long' else trade['selldates']
        exit_date = trade['selldates'] if side == 'Long' else trade['buydates']
        # print(f'Entry Date :{entry_date} | Exit Date : {exit_date} | Position: {side}')
        
        tsl_data = df.loc[(df.index >= entry_date) & (df.index <= exit_date)]
        tsl_values = tsl_data['tsl_long'] if side == 'Long' else tsl_data['tsl_short']
        prev_tsl_value = None  # To track the previous value of tsl
        is_first_polygon = True  # Flag to track the first polygon for each trade
        
        # Initialize fillcolor to red for the first polygon
        fillcolor = 'rgba(255, 0, 0, 0.3)'
        y0 = trade['buyprice'] if side == 'Long' else trade['sellprice']
        y1 = None  # Initialize y1
        
        # Initialize polygon number for this trade position
        number = 1
        
        # Create a list to store individual TSL polygons for this trade
        trade_tsl_shapes = []

        for date, tsl_value in tsl_values.items():
            y_cord = ({'entry price' : y0 , 'tsl value' : tsl_value})
            # print(f'Polygon no: {number} | Date: {date} | {y_cord}')
            
            if prev_tsl_value is None:
                prev_tsl_value = tsl_value
                y1 = tsl_value  # Initialize y1 with the first tsl_value
                # print('first y1 value:', y1)
                # Add the initial polygon to the trade_tsl_shapes list
                trade_tsl_shapes.append(
                    go.Scatter(
                        x=[entry_date, date, date, entry_date],
                        y=[y0, y0, y1, y1],
                        fill='toself',
                        fillcolor=fillcolor,
                        line=dict(color=fillcolor),
                        mode='lines',
                        showlegend=False,
                    )
                )
                continue
            
            if tsl_value != prev_tsl_value:
                # There's a change in tsl_value, end the current polygon
                trade_tsl_shapes.append(
                    go.Scatter(
                        x=[entry_date, date, date, entry_date],
                        y=[y0, y0, y1, y1],
                        fill='toself',
                        fillcolor=fillcolor,
                        line=dict(color=fillcolor),
                        mode='lines',
                        showlegend=False,
                    )
                )
                
                entry_date = date  # Start a new polygon from the new date
                prev_tsl_value = tsl_value
                initial_sl = tsl_value  # Update initial SL for subsequent polygons
                
                # Set fillcolor to green for subsequent polygons
                if is_first_polygon:
                    fillcolor = 'rgba(0, 255, 0, 0.3)'
                    is_first_polygon = False
            
                number += 1  # Increment polygon number

            y1 = tsl_value  # Update y1 with the current tsl_value

        # After the loop ends, check if the last polygon for entry position needs to be added
        if y0 != y1:
            trade_tsl_shapes.append(
                go.Scatter(
                    x=[entry_date, exit_date, exit_date, entry_date],
                    y=[y0, y0, y1, y1],
                    fill='toself',
                    fillcolor=fillcolor,
                    line=dict(color=fillcolor),
                    mode='lines',
                    showlegend=False,
                )
            )

        # Add the trade_tsl_shapes to tsl_shapes
        tsl_shapes.extend(trade_tsl_shapes)

    fig = go.Figure(
        data=tsl_shapes + [candlestick, sw_top_markers, sw_bottom_markers, zigzag_trace],  # Include TSL shapes first
        layout=layout,
    )


    # Define parameters for each label
    label_params = {
        'HH': {'color': '#FF9800', 'textposition': 'bottom center'},
        'LH': {'color': '#2962ff', 'textposition': 'bottom center'},
        'LL': {'color': '#2962ff', 'textposition': 'top center'},
        'HL': {'color': '#FF9800', 'textposition': 'top center'},
    }

    plot_labels_high_low(df, label_params, fig, side)
    
    entry_dates = {"Long": [], "Short": []}

    for index, row in dfr.iterrows():
        if row["tradeSide"] == "Long":
            entry_dates["Long"].append(row['buydates'])
        else:
            entry_dates["Short"].append(row['selldates'])

    # Plot the Long signals as green arrows
    fig.add_trace(go.Scatter(
        x=entry_dates["Long"],
        y=df['long_entry'].loc[entry_dates["Long"]],
        mode='markers',
        marker=dict(
            symbol='arrow-bar-right',
            size=20,
            color='green',
        ),
        name='Long Signals',
    ))

    # Plot the Short signals as red arrows
    fig.add_trace(go.Scatter(
        x=entry_dates["Short"],
        y=df['short_entry'].loc[entry_dates["Short"]],
        mode='markers',
        marker=dict(
            symbol='arrow-bar-right',
            size=20,
            color='red',
        ),
        name='Short Signals',
    ))
    
    # Plot the trailing stop loss levels for each trade
    for _, row in dfr.iterrows():
        high = df.loc[row.iloc[0], 'High']
        low = df.loc[row.iloc[0], 'Low']
        long_entry = df.loc[row.iloc[0], 'long_entry']
        short_entry = df.loc[row.iloc[0], 'short_entry']
        long_exit = df.loc[row.iloc[0], 'long_Exit']
        short_exit = df.loc[row.iloc[0], 'short_Exit']
        
        if row['tradeSide'] == 'Long':
            tsl = df.loc[row.iloc[0], 'tsl_long']  # Stop loss for Long position from df
            name = 'Long Trailing Stop Loss'
            color = 'red'
            entry_label = 'LONG ENTRY'
        else:
            tsl = df.loc[row.iloc[0], 'tsl_short']  # Stop loss for Short position from df
            name = 'Short Trailing Stop Loss'
            color = 'blue'
            entry_label = 'SHORT ENTRY'

        entry_exit_data = {
            'Long': {
                'xx_values': [row['buydates'], row['selldates']],
                'y_percentage_offset': 0.05,  # Adjust this percentage as needed
                'text_position_entry': 'top left',  # Text position for Long entry_label
                'text_position_exit': 'top right',  # Text position for Long EXIT
            },
            'Short': {
                'xx_values': [row['selldates'], row['buydates']],
                'y_percentage_offset': 0.05,  # Adjust this percentage as needed
                'text_position_entry': 'top left',  # Text position for Short entry_label
                'text_position_exit': 'top right',  # Text position for Short EXIT
            },
        }
        
        data = entry_exit_data.get(row['tradeSide'])

        if data:
            xx_values = data['xx_values']
            text_position_entry = data['text_position_entry']
            text_position_exit = data['text_position_exit']
            
            # Calculate the vertical offset based on the price range percentage
            price_range = high - low  # Assuming high and low are defined
            if row['tradeSide'] == 'Long':
                y_percentage_offset_entry = data['y_percentage_offset']
                yy_entry = [long_entry + 50, tsl]
            else:  # Short
                y_percentage_offset_entry = data['y_percentage_offset']
                yy_entry = [short_entry, tsl]

            # Adjust the vertical offset for the EXIT similarly
            y_percentage_offset_exit = data['y_percentage_offset']
            yy_exit = [row['buyprice'] + y_percentage_offset_exit * price_range, tsl - 500]

            fig.add_trace(go.Scatter(
                x=[xx_values[0]],
                y=yy_entry,
                mode='text',
                text=[entry_label],
                textposition=text_position_entry,
                showlegend=False  # Exclude legend for this trace
            ))

            fig.add_trace(go.Scatter(
                x=[xx_values[1]],
                y=yy_exit,
                mode='text',
                text=['EXIT'],
                textposition=text_position_exit,
                showlegend=False  # Exclude legend for this trace
            ))

    # Set the x-axis range to display the most recent data points by default
    fig.update_xaxes(range=[df.index[-num_data_points], df.index[-1]])

    # Add the text annotations to the figure
    fig.update_layout(annotations=annotations)

    fig.update_layout(xaxis_rangeslider_visible=False)

    # Update layout to customize the appearance (optional)
    fig.update_layout(
        yaxis=dict(
            # Remove the 'range' parameter to let Plotly automatically determine the y-axis range
            range=[y_min, y_max],  # adjust scaling at y-axis
            # autorange=True,  # Set autorange to True to enable autoscaling
        ),
        height=600,  # Set the desired height in pixels
        title='Advanced Gann Swing Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        showlegend=True,
        # autosize=True,
        # yaxis=dict(type='auto'),  # Automatically determine y-axis scale based on data
        # updatemenus=update_menus,  # Add the update menus for marker color selection
        # updatemenus=[dict(type="buttons", showactive=False, buttons=[])]
    )

    return fig


# Define a function to open the log file and display its contents
def open_log_file(log_display):
    log_file_path = '/home/ubuntu/output_log.txt'
    try:
        if st.session_state.show_log:
            with open(log_file_path, 'r') as log_file:
                log_contents = log_file.read()
            log_display.text_area(
                "Log File Contents:",
                log_contents,
                height=400  # Adjust the height as needed
            )
        else:
            log_display.empty()
    except Exception as e:
        st.error(f"Error: {e}")


# Function to calculate position size
def calculate_position_size(
    method_type, price_type, value, sl_price, 
    symbol, exchange, backtest=False, current_balance=None, 
    entry_price=None
    ):
    if not backtest:
        # Get the current ticker for the symbol
        ticker = exchange.fetch_ticker(symbol)
    
    entry_price = entry_price if backtest else ticker['last']  # Use provided entry_price during backtest
    sym_quote = symbol[-3:]
    total_bal = current_balance if backtest else exchange.fetch_balance()['total'][sym_quote]  # Use provided total_bal during backtest
    print('Entry Price: ', entry_price)
    print('SL Price: ', sl_price)
    print('Total Balance: ', total_bal)
    # print('Symbol: ', symbol)
    # print('Qoote for Symbol is: ', sym_quote)
    # Calculate position size
    
    if method_type == 'Fixed':
        if price_type == 'Quote':
            qty_ = (value / entry_price)
        elif price_type == 'Base':
            qty_ = value
        elif price_type == 'Percentage':
            qty_ = (total_bal * (value * 0.01)) / entry_price
    elif method_type == 'Dynamic':
        if price_type == 'Quote':
            qty_quote = (entry_price / ((abs(entry_price - sl_price)) / value))
            qty_ = qty_quote / entry_price
        elif price_type == 'Base':
            qty_ = (entry_price / ((abs(entry_price - sl_price)) / (value * entry_price))) / entry_price
        elif price_type == 'Percentage':
            qty_quote = (entry_price / ((abs(entry_price - sl_price)) / (total_bal * (value * 0.01))))
            qty_ = qty_quote / entry_price

    qty = round(qty_, 3)
    print('Quantity Calculated: ', qty)
    # Calculate money needed
    money_needed = qty * entry_price
    print(f"Money ${money_needed} is needed to buy qty : {qty}")

    # Check if position size exceeds available equity and adjust if needed
    if money_needed > total_bal:
        qty_ = total_bal / entry_price
        qty = round(qty_, 3)
        print(f"Money needed to buy quantity Exceeded Total Balance, So Adjusting Qty : {qty}")
    print('--------------------------------------------------------------------------\n')
    return qty

# Function to generate a centered category label
def category_label(category_name, total_width=50, dash_character="-"):
    # Calculate the number of dashes required to center the text
    num_dashes = (total_width - len(category_name)) // 2
    dashes = dash_character * num_dashes

    # Create the centered category label
    return f"{dashes} {category_name} {dashes}"