import ccxt
import streamlit as st
# from naoranaConfig import binanceAPI
import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot
import pandas as pd
import pandas_ta as ta
import numpy as np
import csv
import os
import time
import json

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

def plot_labels_high_low(df, label_params, fig):
    for label, params in label_params.items():
        label_data = pd.DataFrame()
        
        # Filter the DataFrame for 'sw_highs' and 'sw_lows' conditions
        high_mask = (df['sw_highs'] == label) & df['sw_top']
        low_mask = (df['sw_lows'] == label) & df['sw_bottom']
        
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
        elif row[sw_bottom_column]:
            current_trend = -1

        if current_trend != prev_trend:
            zigzag_x.append(index)
            zigzag_y.append(row['High'] if current_trend == 1 else row['Low'])
            zigzag_colors.append(zigzag_color)
            zigzag_color = uptrend_color if current_trend == 1 else downtrend_color

        prev_trend = current_trend

    zigzag_trace = go.Scatter(
        x=zigzag_x,
        y=zigzag_y,
        mode='lines',
        line=dict(width=2),
        name='Zigzag Line',
        hoverinfo='none',
        marker=dict(color=zigzag_colors)
    )

    return zigzag_trace

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

def calculate_gann_signals(df, max_sw_cnt):
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
        df['sw_cnt'] = p_cnt_values
    else:
        print("Length mismatch error between p_cnt_values and df.")

    # Initialize sw_trend with NaN
    df['sw_trend'] = np.nan

    # Create mask1 and mask2
    mask1 = (
        ((df['sw_cnt'] == -3) |
         ((df['sw_cnt'] == 1) & (df['candle_type'] == 'outside_dn_up'))) &
        (df['sw_cnt'].shift(1) == -2)  # & (df['sw_trend'].shift(1) != df['sw_trend'])
    )

    mask2 = (
        ((df['sw_cnt'] == 3) |
         ((df['sw_cnt'] == -1) & (df['candle_type'] == 'outside_up_dn'))) &
        (df['sw_cnt'].shift(1) == 2)  # & (df['sw_trend'].shift(1) != df['sw_trend'])
    )

    # Update sw_trend based on mask1 and mask2
    df.loc[mask1, 'sw_trend'] = -1
    df.loc[mask2, 'sw_trend'] = 1

    # Forward fill the sw_trend column to carry forward the last value
    df['sw_trend'].ffill(inplace=True)

    trend_cnt = [0]

    # Loop through the DataFrame index
    for i in range(1, len(df)):
        if df['sw_trend'].iloc[i - 1] == df['sw_trend'].iloc[i]:
            trend_cnt.append(trend_cnt[i - 1] + 1)
        else:
            trend_cnt.append(1)
    # Append a 0 at the beginning to match the length of the DataFrame
    trend_cnt.insert(0, 0)

    df['trend_cnt'] = trend_cnt[:-1]

    # Initialize sw_top column with False
    df['sw_top'] = False
    df['sw_bottom'] = False

    # Create mask1 and mask2
    # mask1 = ((df['sw_cnt'] == -3) & (df['sw_cnt'].shift(1) == -2) & (df['sw_trend'].shift(1) != df['sw_trend']))
    # mask2 = ((df['sw_cnt'] == 3) & (df['sw_cnt'].shift(1) == 2) & (df['sw_trend'].shift(1) != df['sw_trend']))
    # Calculate the maximum High value of past n candles when mask1 is true
    for i in range(len(df)):
        if mask1[i] & (df['sw_trend'].iloc[i - 1] != df['sw_trend'].iloc[i]):
            # Calculate the maximum High and its index
            high_range = df.loc[
                df.index[max(0, i - int(df['trend_cnt'][i]))]:df.index[i]]['High']
            max_high = high_range.max()
            max_high_index = high_range.idxmax()

            # Mark the row where max_high occurs as True
            df.at[max_high_index, 'sw_top'] = True

        elif mask2[i] & (df['sw_trend'].iloc[i - 1] != df['sw_trend'].iloc[i]):
            # Calculate the maximum High and its index
            low_range = df.loc[
                df.index[max(0, i - int(df['trend_cnt'][i]))]:df.index[i]]['Low']
            min_low = low_range.min()
            min_low_index = low_range.idxmin()

            # Mark the row where max_high occurs as True
            df.at[min_low_index, 'sw_bottom'] = True

    df['sw_high_price'] = np.where(
        df['sw_top'] == True, df['High'], np.nan)
    df['sw_high_price'].fillna(method='ffill', inplace=True)
    df['sw_low_price'] = np.where(
        df['sw_bottom'] == True, df['Low'], np.nan)
    df['sw_low_price'].fillna(method='ffill', inplace=True)

    # Filter rows where sw_top is True and calculate sw_highs
    df_tops = df[df['sw_top'] == True].copy()
    df_tops['sw_highs'] = np.where(
        df_tops['High'] > df_tops['High'].shift(1), "HH", "LH")

    # Filter rows where sw_bottom is True and calculate sw_lows
    df_bottoms = df[df['sw_bottom'] == True].copy()
    df_bottoms['sw_lows'] = np.where(
        df_bottoms['Low'] < df_bottoms['Low'].shift(1), "LL", "HL")

    # Concatenate the DataFrames and select the desired columns
    df_swings = pd.concat([df_tops, df_bottoms], axis=1)

    df_swings['trend'] = np.nan
    df_swings['trend'] = np.where(((df_swings['sw_highs'] == 'HH') & (df_swings['sw_lows'].shift(1) == 'HL')) |
                                  ((df_swings['sw_lows'] == 'HL') & (df_swings['sw_highs'].shift(1) == 'HH')),
                                   "UP",
                                   np.where(((df_swings['sw_lows'] == 'LL') & (df_swings['sw_highs'].shift(1) == 'LH')) |
                                            ((df_swings['sw_highs'] == 'LH') & (df_swings['sw_lows'].shift(1) == 'LL')),
                                            "DOWN",
                                            np.where(((df_swings['sw_lows'] == 'LL') & (df_swings['sw_highs'].shift(1) == 'HL')) |
                                                     ((df_swings['sw_lows'] == 'LL') & (df_swings['sw_highs'].shift(1) == 'HH')) |
                                                     ((df_swings['sw_lows'] == 'HL') & (df_swings['sw_highs'].shift(1) == 'LH')) |
                                                     ((df_swings['sw_highs'] == 'LH') & (df_swings['sw_lows'].shift(1) == 'HL')) |
                                                     ((df_swings['sw_highs'] == 'HH') & (df_swings['sw_lows'].shift(1) == 'LL')),
                                                     "UNCERTAIN",
                                                     np.nan
                                                    )
                                                 )
                                             )


    df_swings = df_swings[["sw_highs", "sw_lows", "trend"]]

    df_ffill = pd.concat([df, df_swings], axis=1)

    # Define the columns to be copied
    columns_to_copy = ["sw_highs", "sw_lows", "trend"]

    # Forward fill columns in df_ffill
    df_ffill[columns_to_copy] = df_ffill[columns_to_copy].fillna(method='ffill')

    # Drop the columns to be replaced from df
    for column in columns_to_copy:
        if column in df.columns:
            df.drop(columns=column, inplace=True)

    # Update the original DataFrame with the filled columns
    df = pd.concat([df, df_ffill[columns_to_copy]], axis=1)

    df['tsl_long'] = df['sw_low_price'].shift(1)
    df['tsl_short'] = df['sw_high_price'].shift(1)

    df["LONG_Signal"] = np.where((df['sw_lows'] == "HL") &
                                 (df['High'] > df['sw_high_price'].shift(1)) &
                                 (df['High'].shift(1) < df['sw_high_price']).shift(1) &
                                 (df['trend'].shift(1) == "UNCERTAIN"),
                                 True,
                                 False)

    df["SHORT_Signal"] = np.where((df['sw_highs'] == "LH") &
                                  (df['Low'] < df['sw_low_price'].shift(1)) &
                                  (df['Low'].shift(1) > df['sw_low_price'].shift(1)) &
                                  (df['trend'].shift(1) == "UNCERTAIN"),
                                  True,
                                  False)

    return df

def backtest(df, ticker, commission=0.04/100):
    in_position = False
    buy_pos = False
    sell_pos = False

    results_df = pd.DataFrame()
    buydates, buyprices = [], []
    selldates, sellprices = [], []

    for index, row in df.iterrows():
# ---------------------------------------------long position close check------------------------------
        if in_position and buy_pos:
            sl = row.tsl_long
            if (row.Low <= sl):
                selldates.append(index)
                sellprices.append(sl)
                in_position = False
                buy_pos = False
    #         elif in_position and (row.High >= tp):
    #             selldates.append(index)
    #             sellprices.append(tp)
    #             in_position = False
    #             buy_pos = False
    # ---------------------------------------------short position close check------------------------------
        elif in_position and sell_pos:
            sl = row.tsl_short
            if (row.High >= sl):
                buydates.append(index)
                buyprices.append(sl)
                in_position = False
                sell_pos = False
                
    # ---------------------------------------------long position entry check------------------------------

        elif not in_position and row.LONG_Signal == True:
            buyprice = row.tsl_short
            buydates.append(index)
            buyprices.append(buyprice)
            in_position = True
            buy_pos = True
    #         tp = row.longTP

    # --------------------------------------------short position entry check-------------------------------

            
        elif not in_position and row.SHORT_Signal == True:
            sellprice = row.tsl_long
            selldates.append(index)
            sellprices.append(sellprice)
            in_position = True
            sell_pos = True

    #         elif in_position and (row.Low <= tp):
    #             buydates.append(index)
    #             buyprices.append(tp)
    #             in_position = False
    #             sell_pos = False

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
        # Other results...
    }


def displayTrades(**kwargs):
    # Access the trade data and other results from kwargs
    buydates = kwargs['buydates']
    buyprices = kwargs['buyprices']
    selldates = kwargs['selldates']
    sellprices = kwargs['sellprices']
    profits = kwargs['profits']

    ct = min(len(buydates),len(selldates))
    dfr =pd.DataFrame()
    dfr['buydates']= buydates[:ct]
    dfr['buyprice']= buyprices[:ct]
    dfr['selldates'] = selldates[:ct]
    dfr['sellprice'] = sellprices[:ct]
    dfr['profits'] = (profits[:ct])
    dfr['commulative_returns'] = ((pd.Series(profits) + 1).cumprod())
    dfr['tradeSide'] = np.where(dfr['buydates'] < dfr['selldates'], 'Long', 'Short')
    return dfr

def plot_advanced_gann_swing_chart(df, dfr, visible_data_points=350):
    # Determine the desired y-axis range based on your data
    y_min = df['Low'].min()  # Replace 'Low' with the appropriate column name
    y_max = df['High'].max()  # Replace 'High' with the appropriate column name

    # Create a candlestick trace
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='Candles',
    )

    # Create text annotations for sw_cnt on top of each candle
    annotations = []

    # Create sw_top marker trace
    sw_top_markers = create_marker_trace(df, 'sw_top', 'triangle-up', 'High', 0.005, '', 'Trend Peaks', 'green')

    # Create sw_bottom marker trace
    sw_bottom_markers = create_marker_trace(df, 'sw_bottom', 'triangle-down', 'Low', -0.005, '', 'Trend Bottoms', 'red')

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
    background_shapes = create_background_shapes(df, 'trend', bg_colors)

    # Create the layout with a white background and the background shapes
    layout = go.Layout(
        shapes=background_shapes,
        showlegend=False,
        # xaxis=dict(showgrid=True, gridcolor='black'),  # Set gridcolor to 'black' for x-axis
        # yaxis=dict(showgrid=True, gridcolor='black'),  # Set gridcolor to 'black' for y-axis
        # plot_bgcolor='white'
    )

    # Define a button to toggle the visibility of background traces
    toggle_button = dict(
        type="buttons",
        showactive=False,
        buttons=[
            dict(label="Show Background Traces",
                 method="relayout",
                 args=["shapes", background_shapes]),
            dict(label="Hide Background Traces",
                 method="relayout",
                 args=["shapes", []]),  # Empty list to hide the shapes
        ],
        x=1.15,  # Adjust the x position to move the button to the right
        y=0.15,   # Adjust the y position to place it below the legends
    )
    layout["updatemenus"] = [toggle_button]

    # Define colors for uptrend and downtrend zigzag lines
    uptrend_color = 'green'
    downtrend_color = 'red'

    # Create the zigzag trace
    zigzag_trace = create_zigzag_trace(df, 'sw_top', 'sw_bottom', uptrend_color, downtrend_color)

    # Determine the number of data points to display by default
    num_data_points = min(len(df), visible_data_points)

    # Create the figure with the candlestick trace and markers (both top and bottom)
    fig = go.Figure(data=[candlestick, sw_top_markers, sw_bottom_markers, zigzag_trace], layout=layout)

    # Set the x-axis range to display the most recent data points by default
    fig.update_xaxes(range=[df.index[-num_data_points], df.index[-1]])

    # Define parameters for each label
    label_params = {
        'HH': {'color': 'green', 'textposition': 'bottom center'},
        'LH': {'color': 'red', 'textposition': 'bottom center'},
        'LL': {'color': 'blue', 'textposition': 'top center'},
        'HL': {'color': 'purple', 'textposition': 'top center'},
    }

    plot_labels_high_low(df, label_params, fig)

    # Plot the Long signals as green arrows
    long_signals = df[df['LONG_Signal']]
    fig.add_trace(go.Scatter(
        x=long_signals.index,
        y=df['sw_high_price'][long_signals.index],
        mode='markers',
        marker=dict(
            symbol='arrow-bar-right',
            size=20,
            color='green',
        ),
        name='Long Signals',
    ))

    # Plot the Short signals as red arrows
    short_signals = df[df['SHORT_Signal']]
    fig.add_trace(go.Scatter(
        x=short_signals.index,
        y=df['sw_low_price'][short_signals.index],
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

        # Set the condition for y values based on tradeSide
        if row['tradeSide'] == 'Long':
            x_values = [row['buydates'], row['selldates'], row['selldates'], row['buydates']]
            y_values = [row['buyprice'], row['buyprice'], tsl, tsl]
            fillcolor = 'rgba(255, 0, 0, 0.3)'  # Red fill for Long
        else:
            x_values = [row['selldates'], row['buydates'], row['buydates'], row['selldates']]
            y_values = [row['sellprice'], row['sellprice'], tsl, tsl]
            fillcolor = 'rgba(255, 0, 0, 0.3)'  # Red fill for Short

        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            fill='toself',
            fillcolor=fillcolor,
            name=name,
            mode='none',
            showlegend=False  # Exclude legend for this trace
        ))

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
                yy_entry = [high + y_percentage_offset_entry * price_range, tsl - 100]
            else:  # Short
                y_percentage_offset_entry = data['y_percentage_offset']
                yy_entry = [low - y_percentage_offset_entry * price_range, tsl - 100]

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

    # Enable or disable auto-scaling
    fig.update_layout(autosize=True)  # Auto-scaling enabled (default)

    # Add the text annotations to the figure
    fig.update_layout(annotations=annotations)

    fig.update_layout(xaxis_rangeslider_visible=False)

    # Update layout to customize the appearance (optional)
    fig.update_layout(
        yaxis=dict(
        range=[y_min, y_max],  # Set the desired y-axis range
        ),
        height=600,  # Set the desired height in pixels
        width=800,
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

# def plot_labels(df, label_params, fig):
#     label_data = pd.DataFrame()

#     for label, params in label_params.items():
#         label_df = df[(df['sw_highs'] == label) & df['sw_top']]
#         label_df.loc[:, 'sw_lows'] = None
#         label_data = pd.concat([label_data, label_df])

#         label_df = df[(df['sw_lows'] == label) & df['sw_bottom']]
#         label_df.loc[:, 'sw_highs'] = None
#         label_data = pd.concat([label_data, label_df])

#     label_data.sort_index(inplace=True)

#     for label, params in label_params.items():
#         label_data['y_position'] = None

#         label_data.loc[label_data['sw_highs'] == label, 'y_position'] = label_data['High'] + 1800
#         label_data.loc[label_data['sw_lows'] == label, 'y_position'] = label_data['Low'] - 1800

#         scatter = go.Scatter(
#             x=label_data.index,
#             y=label_data['y_position'],
#             mode='text',
#             text=label.upper(),
#             textfont=dict(color=params['color'], size=12),
#             name=label.upper(),
#             textposition=params['textposition']
#         )

#         fig.add_trace(scatter)

#     label_data.drop(columns=['y_position'], inplace=True)
