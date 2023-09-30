import datetime as dt
import time
import ccxt
from kraken_config import *
from main_functions import *
import json
import os

exchange = ccxt.krakenfutures({
        'apiKey': apiKey,
        'secret': secret,
        'verbose': False,  # switch it to False if you don't want the HTTP log
    })
exchange.set_sandbox_mode(True)  # enable sandbox mode

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the current working directory to the script's directory
os.chdir(script_dir)

symbol_mapping = {
    'SANDUSDT': 'SAND/USD:USD',
    'BTCUSDT': 'BTC/USD:USD',
    'GALAUSDT': 'GALA/USD:USD',
    'AXSUSDT': 'AXS/USD:USD',
    'EOSUSDT': 'EOS/USD:USD',
    'LUNA2USDT': 'LUNA2/USD:USD',
    'APEUSDT': 'APE/USD:USD',
    'LDOUSDT': 'LDO/USD:USD',
    'OMGUSDT': 'OMG/USD:USD',
    'SOLUSDT': 'SOL/USD:USD',
    'YFIUSDT': 'YFI/USD:USD',
    'DOTUSDT': 'DOT/USD:USD',
    'LINKUSDT': 'LINK/USD:USD',
    'ETCUSDT': 'ETC/USD:USD',
    'ENJUSDT': 'ENJ/USD:USD',
    'ZECUSDT': 'ZEC/USD:USD',
    'KAVAUSDT': 'KAVA/USD:USD',
    'MATICUSDT': 'MATIC/USD:USD',
    'XRPUSDT': 'XRP/USD:XRP',
    'DOGEUSDT': 'DOGE/USD:USD',
    'AVAXUSDT': 'AVAX/USD:USD',
    'ARBUSDT': 'ARB/USD:USD',
    'WAVESUSDT': 'WAVES/USD:USD',
    'LRCUSDT': 'LRC/USD:USD',
    'SNXUSDT': 'SNX/USD:USD',
    'SUSHIUSDT': 'SUSHI/USD:USD',
    '1INCHUSDT': '1INCH/USD:USD',
    'ATOMUSDT': 'ATOM/USD:USD',
    'GRTUSDT': 'GRT/USD:USD',
    'ALGOUSDT': 'ALGO/USD:USD',
    'FLOWUSDT': 'FLOW/USD:USD',
    'BCHUSDT': 'BCH/USD:USD',
    'DASHUSDT': 'DASH/USD:USD',
    'GMTUSDT': 'GMT/USD:USD',
    'LTCUSDT': 'LTC/USD:USD',
    'OPUSDT': 'OP/USD:USD',
    'GMXUSDT': 'GMX/USD:USD',
    'DEFIUSDT': 'DEFI/USD:USD',
    'KSMUSDT': 'KSM/USD:USD',
    'CRVUSDT': 'CRV/USD:USD',
    'XLMUSDT': 'XLM/USD:USD',
    'FILUSDT': 'FIL/USD:USD',
    'AAVEUSDT': 'AAVE/USD:USD',
    'XTZUSDT': 'XTZ/USD:USD',
    'MANAUSDT': 'MANA/USD:USD',
    'QTUMUSDT': 'QTUM/USD:USD',
    'XMRUSDT': 'XMR/USD:USD',
    'COMPUSDT': 'COMP/USD:USD',
    'KNCUSDT': 'KNC/USD:USD',
    'CHZUSDT': 'CHZ/USD:USD',
    'UNIUSDT': 'UNI/USD:USD',
    'ETHUSDT': 'ETH/USD:USD',
    'OGNUSDT': 'OGN/USD:USD',
    'LPTUSDT': 'LPT/USD:USD',
    'APTUSDT': 'APT/USD:USD',
    'FTMUSDT': 'FTM/USD:USD',
    'TRXUSDT': 'TRX/USD:USD',
    'BATUSDT': 'BAT/USD:USD',
    'ADAUSDT': 'ADA/USD:USD',
    'NEARUSDT': 'NEAR/USD:USD'
}

# Load the JSON data from the file
with open('pos.json', 'r') as f:
    json_pos = f.read()
with open('qty.json', 'r') as f:
    json_qty = f.read()
with open('optimized_params.json', 'r') as f:
    json_params = f.read()
with open('order_info.json', 'r') as f:
    json_order_info = f.read()

# Convert the JSON data back to a dictionary
pos = json.loads(json_pos)
qty = json.loads(json_qty)
info = json.loads(json_order_info)
params = json.loads(json_params)

time.sleep(5)

for key, value in params.items():
    # Create variables with the key as the variable name using globals()
    globals()[key] = value
    print(key)

interval = map_timeframe(timeframe, get_value=True)
symbol = symbol_mapping.get(symbol)
ticker = symbol[:-4]
# Define trading variables
usdt_amount = 15 # whatever amount client wants
timeframe = interval
in_position = False
buy_price = 0
stop_loss_price = 0

# Check if the state file exists
if os.path.exists('flag_status.json'):
    # Load state from JSON files at the beginning of the script
    with open('flag_status.json', 'r') as state_file:
        state = json.load(state_file)
else:
    # Initialize default values if the file doesn't exist
    state = {
        'in_position': False,
        'buy_pos': False,
        'sell_pos': False,
        'order_triggered': None,
        'is_hit': None,
        }

in_position = state['in_position']
buy_pos = state['buy_pos']
buy_pos = state['buy_pos']
order_triggered = state['order_triggered']
is_hit = state['order_triggered']

print('In Position', in_position)
print('LOng Position', long_position)
print('Short Position', short_position)
print('Order Triggered', order_triggered)
print('is Hit?', is_hit)

tp_perc = 0 if tp_exit == False else tp_value  # added

while True:
    try:
        # Fetch the latest candlestick data
        df = getdata_kraken(ticker, timeframe, 1000)

        if len(df) > 0:
            # Get the latest closing price
            close_price = df['Close'].iloc[-1]

            df = calculate_gann_signals(df, max_sw_cnt, exit_perc = exit_perc)
            # Fetch the latest buy and sell signals, as well as stop loss levels, from your DataFrame 'df'
            row = df.iloc[-1]  # Assuming the last row contains the latest data

            if in_position:
                # Check for stop loss conditions
                sl_long = row.tsl_long
                sl_short = row.tsl_short
                position_size = info['amount']
                
                if buy_pos and row['Low'] <= sl_long:
                    # Execute a market sell order to close the long position
                    # Use the Kraken API to place a market sell order for the position_size
                    order_response =  exchange.create_market_sell_order(symbol, position_size)
                    # Extract the required information
                    order_id = order_response['info']['order_id']
                    price = float(order_response['price'])
                    amount = float(order_response['amount'])
                    side = order_response['side']

                    print(f"Order ID: {order_id}")
                    print(f"Price: {price}")
                    print(f"Amount: {amount}")
                    print(f"Side: {side}")
                    
                    in_position = False
                    buy_pos = False
                    print(f"Stop Loss Hit for Long Position. Position Closed at Market Price")

                    # Save the order information
                    order_info = {
                        'order_id': order_id,
                        'price': price,
                        'amount': amount,
                        'side': side
                    }
                    with open('order_info.json', 'w') as order_file:
                        json.dump(order_info, order_file)

                elif sell_pos and row['High'] >= sl_short:
                    # Execute a market buy order to close the short position
                    # Use the Kraken API to place a market buy order for the position_size
                    order_response =  exchange.create_market_buy_order(symbol, position_size)
                    # Extract the required information
                    order_id = order_response['info']['order_id']
                    price = float(order_response['price'])
                    amount = float(order_response['amount'])
                    side = order_response['side']

                    print(f"Order ID: {order_id}")
                    print(f"Price: {price}")
                    print(f"Amount: {amount}")
                    print(f"Side: {side}")
                    
                    in_position = False
                    sell_pos = False
                    print(f"Stop Loss Hit for Short Position. Position Closed at Market Price")

                    # Save the order information
                    order_info = {
                        'order_id': order_id,
                        'price': price,
                        'amount': amount,
                        'side': side
                    }
                    with open('order_info.json', 'w') as order_file:
                        json.dump(order_info, order_file)

            elif not in_position:
                if row['LONG_Signal']:
                    # Place a market buy order for a long position
                    position_size = calculate_order_size(ticker, usdt_amount)
                    # Use the Kraken API to place a market buy order for the position_size
                    order_response =  exchange.create_market_buy_order(symbol, position_size)
                    # Extract the required information
                    order_id = order_response['info']['order_id']
                    price = float(order_response['price'])
                    amount = float(order_response['amount'])
                    side = order_response['side']

                    print(f"Order ID: {order_id}")
                    print(f"Price: {price}")
                    print(f"Amount: {amount}")
                    print(f"Side: {side}")
                    
                    in_position = True
                    buy_pos = True
                    print(f"Market Buy Order Placed at Market Price")

                    # Save the order information
                    order_info = {
                        'order_id': order_id,
                        'price': price,
                        'amount': amount,
                        'side': side
                    }
                    with open('order_info.json', 'w') as order_file:
                        json.dump(order_info, order_file)

                elif row['SHORT_Signal']:
                    # Place a market sell order for a short position
                    position_size = calculate_order_size(ticker, usdt_amount)
                    # Use the Kraken API to place a market sell order for the position_size
                    order_response =  exchange.create_market_sell_order(symbol, position_size)
                    # Extract the required information
                    order_id = order_response['info']['order_id']
                    price = float(order_response['price'])
                    amount = float(order_response['amount'])
                    side = order_response['side']

                    print(f"Order ID: {order_id}")
                    print(f"Price: {price}")
                    print(f"Amount: {amount}")
                    print(f"Side: {side}")
                    
                    in_position = True
                    sell_pos = True
                    print(f"Market Sell Order Placed at Market Price")

                    # Save the order information
                    order_info = {
                        'order_id': order_id,
                        'price': price,
                        'amount': amount,
                        'side': side
                    }
                    with open('order_info.json', 'w') as order_file:
                        json.dump(order_info, order_file)

        time.sleep(60)  # Wait for the next candlestick update (adjust as needed)

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(60)  # Wait for the next iteration
    
    # Save the updated state to JSON files at the end of the script
    state = {
        'in_position': in_position,
        'buy_pos': buy_pos,
        'sell_pos': sell_pos,
        'order_triggered': None,
        'is_hit': None
    }

    with open('flag_status.json', 'w') as state_file:
        json.dump(state, state_file)