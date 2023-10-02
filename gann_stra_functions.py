# Function to calculate Pi Cycle signals
def calculate_pi_cycle_signals(df):
    pi_ema1 = df['open'].rolling(window=350).mean() * 2
    pi_ema2 = df['open'].rolling(window=111).mean()
    pi_ema3 = df['close'].rolling(window=250).mean()
    pi_ema4 = df['close'].rolling(window=550).mean()

    pi_top = (pi_ema2 > pi_ema1).astype(float)
    pi_bot = (pi_ema4 > pi_ema3).astype(float)

    return pi_top, pi_bot

# Function to calculate Swing Highs and Lows
def calculate_swing_highs_lows(data):
    swing_highs = []
    swing_lows = []
    count = 0

    # Initialize variables for tracking trend periods
    prev_trend = None
    trend_periods = []

    for i in range(2, len(data) - 2):
        if (
            data['High'][i] > max(data['High'][i - 2], data['High'][i - 1], data['High'][i + 1], data['High'][i + 2]) and
            data['High'][i] > data['High'][i - 1]
        ):
            swing_highs.append((data.index[i], data['High'][i]))
            count += 1
            if count == 2:
                count = 0
                swing_lows.append((data.index[i - 1], data['Low'][i - 1]))

                # Determine the trend during this period (Up, Down, or Uncertain)
                if prev_trend is None:
                    prev_trend = 'Up'
                elif prev_trend == 'Uncertain':
                    if data['High'][i] > data['High'][i - 2] and data['Low'][i] > data['Low'][i - 2]:
                        prev_trend = 'Up (1)'
                    else:
                        prev_trend = 'Up (2)'
                trend_periods.append((data.index[i - 1], data.index[i], prev_trend))
                prev_trend = 'Down' if prev_trend.startswith('Up') else 'Uncertain'

        elif (
            data['Low'][i] < min(data['Low'][i - 2], data['Low'][i - 1], data['Low'][i + 1], data['Low'][i + 2]) and
            data['Low'][i] < data['Low'][i - 1]
        ):
            swing_lows.append((data.index[i], data['Low'][i]))
            count += 1
            if count == 2:
                count = 0
                swing_highs.append((data.index[i - 1], data['High'][i - 1]))

                # Determine the trend during this period (Up, Down, or Uncertain)
                if prev_trend is None:
                    prev_trend = 'Down'
                elif prev_trend == 'Uncertain':
                    if data['High'][i] < data['High'][i - 2] and data['Low'][i] < data['Low'][i - 2]:
                        prev_trend = 'Down (1)'
                    else:
                        prev_trend = 'Down (2)'
                trend_periods.append((data.index[i - 1], data.index[i], prev_trend))
                prev_trend = 'Up' if prev_trend.startswith('Down') else 'Uncertain'

    return swing_highs, swing_lows, trend_periods

# Function to identify Swing Trends
def identify_swing_trends(data, swing_highs, swing_lows):
    trends = []
    count = 0

    for i in range(len(data)):
        if (data.index[i], data['High'][i]) in swing_highs:
            count += 1
        elif (data.index[i], data['Low'][i]) in swing_lows:
            count -= 1

        if count == 2:
            trends.append('Up')
            count = 0
        elif count == -2:
            trends.append('Down')
            count = 0
        else:
            trends.append('Uncertain')

    return trends

# Function to generate SMA signals
def generate_sma_signals(data, sma_period):
    data['SMA'] = data['Close'].rolling(sma_period).mean()
    data['SMA_Long_Signal'] = data['Close'] > data['SMA']
    data['SMA_Short_Signal'] = data['Close'] < data['SMA']

def generate_entry_exit_signals(df, trends, sma_period, percent_to_move_stop_loss=0.1, percent_to_place_sell_limit=0.8):
    generate_sma_signals(df, sma_period)  # Generate SMA signals

    entry_signals = []
    exit_signals = []
    in_position = False
    buy_pos = False
    sell_pos = False
    swing_high = None
    swing_low = None
    stop_loss = None
    confirmed_up_trend = False
    last_stop_loss = None

    for index, row in df.iterrows():
        if trends[index] == 'Up':
            # Check for HH and HL for "BREAK" entry
            if swing_high is not None and swing_low is not None and row['High'] > swing_high and row['Low'] > swing_low:
                entry_signals.append(('BREAK', index, row['Close']))
                in_position = True
                buy_pos = True

                # Initial stop loss logic
                initial_stop_loss = swing_low - (swing_low * percent_to_move_stop_loss)
                stop_loss = initial_stop_loss
                last_stop_loss = stop_loss
                confirmed_up_trend = True
            else:
                confirmed_up_trend = False

            # Check for "HL" entry
            if row['Low'] < swing_low and trends[index + 1] == 'Up':
                entry_signals.append(('HL', index, row['Close']))
                in_position = True
                buy_pos = True

                # Initial stop loss logic
                initial_stop_loss = swing_low - (swing_low * percent_to_move_stop_loss)
                stop_loss = initial_stop_loss
                last_stop_loss = stop_loss

        elif trends[index] == 'Down':
            if not in_position and row['SMA_Short_Signal']:
                entry_signals.append(('Sell', index, row['Close']))
                in_position = True
                sell_pos = True
                stop_loss = row['High'] + (row['High'] * percent_to_move_stop_loss)
            else:
                if in_position and sell_pos and row['High'] >= stop_loss:
                    entry_signals.append(('Buy', index, stop_loss))
                    in_position = False
                    sell_pos = False
                elif in_position and row['Low'] <= stop_loss:
                    entry_signals.append(('Buy', index, stop_loss))
                    in_position = False
                    sell_pos = False
                elif not in_position and confirmed_up_trend and row['High'] < row['High'].shift(1):
                    # Check for a LOWER HIGH indicating a potential trend reversal
                    sell_price = max(row['Close'], stop_loss) + (row['Close'] - max(row['Close'], stop_loss)) * percent_to_place_sell_limit
                    entry_signals.append(('Sell', index, sell_price))
                    in_position = True
                    sell_pos = True

        # Update swing high and low
        if trends[index] == 'Up':
            if swing_high is None or row['High'] > swing_high:
                swing_high = row['High']
            if swing_low is None or row['Low'] < swing_low:
                swing_low = row['Low']

    # Check for an open position at the end of the data
    if in_position:
        if buy_pos:
            exit_signals.append(('Sell', df.index[-1], df['Close'][-1]))
        else:
            exit_signals.append(('Buy', df.index[-1], df['Close'][-1]))

    return entry_signals, exit_signals


def backtest(df, HL, takeLong, takeShort, risk, mult, commission=0.0):
    in_position = False
    buy_pos = False
    sell_pos = False

    global buydates, buyprices, selldates, sellprices, profits
    results_df = pd.DataFrame()
    buydates, buyprices = [], []
    selldates, sellprices = [], []

    for index, row in df.iterrows():
        # Check for entry signals
        if row['EntrySignal'] == 'Buy' and not in_position:
            buyprice = row['Open']
            buydates.append(index)
            buyprices.append(buyprice)
            in_position = True
            buy_pos = True
            sl = row['Low']
            tp = (row['Close'] - sl) * mult + row['Close']
        elif row['EntrySignal'] == 'Sell' and not in_position:
            sellprice = row['Open']
            selldates.append(index)
            sellprices.append(sellprice)
            in_position = True
            sell_pos = True
            sl = row['High']
            tp = row['Close'] - ((sl - row['Close']) * mult)

        # Check for exit signals
        if in_position:
            if buy_pos:
                if row['Low'] <= sl:
                    selldates.append(index)
                    sellprices.append(sl)
                    in_position = False
                    buy_pos = False
                elif row['High'] >= tp:
                    selldates.append(index)
                    sellprices.append(tp)
                    in_position = False
                    buy_pos = False
            elif sell_pos:
                if row['High'] >= sl:
                    buydates.append(index)
                    buyprices.append(sl)
                    in_position = False
                    sell_pos = False
                elif row['Low'] <= tp:
                    buydates.append(index)
                    buyprices.append(tp)
                    in_position = False
                    sell_pos = False

    try:
        if len(buydates) == 0:
            print("No trades were made.")
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
            results_df = pd.concat([results_df, pd.DataFrame({'ticker': f'{ticker}', 'returns': [returns], 'winrate': [winrate], 'trades': [ct], 'buy&hold_ret%': [buy_hold_ret], 'mult': [mult], 'No. of H/L previous Candles': [HL], 'Max Risk%': [risk]})])
            print(f'{ticker}, winrate={winrate}%, returns={round(returns, 2)}%, no. of trades = {ct}, buy&hold_ret = {round(buy_hold_ret, 2)}%, mult = {mult}, No. of H/L previous Candles : {HL}, Max Risk% : {risk}')
    except:
        print(f'Invalid input')

    return results_df