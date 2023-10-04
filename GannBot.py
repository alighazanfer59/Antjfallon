import datetime as dt
import time
import ccxt
from main_functions import *
import json
import os
import warnings
# import importlib
import kraken_config

# If you want to update the module:
importlib.reload(kraken_config)
from kraken_config import *

# Filter out the FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)
# krakenActive(mode, context="console")
# def krakenActive(mode):
#     st.write('mode passed to krakenActive: ', mode)
#     # Set sandbox mode based on the selected mode
#     if mode == "Demo":
#         sandbox_mode = True
#     else:
#         sandbox_mode = False
    
#     # Get the API key and secret based on the selected mode
#     config_path = 'kraken_config.py'
#     live_mode = mode == "Live"
#     api_key, secret_key = get_api_key_secret(config_path, live_mode=live_mode)

#     # Configure the ccxt.krakenfutures instance
#     exchange = ccxt.krakenfutures({
#         'apiKey': api_key,
#         'secret': secret_key,
#         'verbose': False,  # switch it to False if you don't want the HTTP log
#     })
#     st.write('Sandbox mode is set to: ', sandbox_mode)
#     # Enable or disable sandbox mode based on the selected mode
#     exchange.set_sandbox_mode(sandbox_mode)

#     return exchange

# st.write('mode is set to : ', mode)
exchange = krakenActive(mode, 'console')

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

# Define your trade records filename
tradesfile = 'agss_tradesHistory.csv'
logfile = "strategy1_log.csv"

# Load the JSON data from the file
# with open('qty.json', 'r') as f:
#     json_qty = f.read()
with open('optimized_params.json', 'r') as f:
    json_params = f.read()
with open('order_info.json', 'r') as f:
    json_order_info = f.read()

# Convert the JSON data back to a dictionary
# qty = json.loads(json_qty)
info = json.loads(json_order_info)
params = json.loads(json_params)

time.sleep(5)

for key, value in params.items():
    # Create variables with the key as the variable name using globals()
    globals()[key] = value
    print("%s : %s" % (key, value))

currency_code = 'USD'  # Replace with the desired currency code
amount_to_use, usd_free_balance, btc_free_balance = calculate_balance(exchange, currency_code)

interval = map_timeframe(timeframe, get_value=True)
symbol = symbol_mapping.get(symbol)
print('Symbol imported and mapped to Kraken Exchange: ', symbol)
ticker = symbol[:-4]
print('ticker: ', ticker)
# Define trading variables
usdt_amount = amount_to_use # 20% amount available balance of client account
print("Balance to Use: ", usdt_amount)
timeframe = interval
in_position = False

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
        'sell_pos': False
        }

in_position = state['in_position']
buy_pos = state['buy_pos']
sell_pos = state['sell_pos']

print('In Position', in_position)
print('LOng Position', buy_pos)
print('Short Position', sell_pos)


tp_perc = 0 if tp_exit == False else tp_value  # added
print('tp perc: ', tp_perc)

try:
    try:
        # Fetch the latest candlestick data
        df = getdata_kraken(ticker, timeframe, 1000)

    except Exception as e:
        # Handle exceptions raised by getdata_kraken
        print(f"An error occurred while fetching data: {e}")
        
    if len(df) > 0:
        # Get the latest closing price
        close_price = df['Close'].iloc[-1]

        df = calculate_gann_signals(df, max_sw_cnt, exit_perc = exit_perc/100)
        # Fetch the latest buy and sell signals, as well as stop loss levels, from your DataFrame 'df'
        row = df.iloc[-1]  # Assuming the last row contains the latest data

        # Inside the 'if in_position:' block
        if in_position:
            print("IN POSITION BLOCK")
            sl_long = row.tsl_long
            sl_short = row.tsl_short
            amount = info['amount']
            print('Side: ', amount)
            tp = info['tp']
            limit = info['limit']

            if buy_pos:
                print('Long Position Block')
                if row['Low'] <= sl_long:
                    close_position(symbol, amount, 'buy', 'Long', sl_long)
                    in_position = False
                    buy_pos = False
                    with open('order_info.json', 'r') as f:
                        json_order_info = f.read()
                    # Convert the JSON data back to a dictionary
                    info = json.loads(json_order_info)
                    sellcsv(df, buyprice=read_tradefile(tradesfile, 'long'), sellprice=info['price'], filename=tradesfile)
                elif row['High'] >= tp and tp_perc != 0:
                    close_position(symbol, amount, 'buy', 'Long', tp)
                    in_position = False
                    buy_pos = False
                    with open('order_info.json', 'r') as f:
                        json_order_info = f.read()
                    # Convert the JSON data back to a dictionary
                    info = json.loads(json_order_info)
                    sellcsv(df, buyprice=read_tradefile(tradesfile, 'long'), sellprice=info['price'], filename=tradesfile)
                elif row['Long_Exit'] > 0:
                    limit = row['Long_Exit']
                    if row['Low'] <= limit:
                        close_position(symbol, amount, 'buy', 'Long', row['Long_Exit'])
                        in_position = False
                        buy_pos = False
                        with open('order_info.json', 'r') as f:
                            json_order_info = f.read()
                        # Convert the JSON data back to a dictionary
                        info = json.loads(json_order_info)
                        sellcsv(df, buyprice=read_tradefile(tradesfile, 'long'), sellprice=info['price'], filename=tradesfile)
            elif sell_pos:
                print('Short Position Block')
                if row['High'] >= sl_short:
                    close_position(symbol, amount, 'sell', 'Short', sl_short)
                    in_position = False
                    sell_pos = False
                    with open('order_info.json', 'r') as f:
                        json_order_info = f.read()
                    # Convert the JSON data back to a dictionary
                    info = json.loads(json_order_info)
                    sellcsv(df, buyprice=info['price'], sellprice=read_tradefile(tradesfile, 'short'), filename=tradesfile)
                elif row['High'] <= tp and tp_perc != 0:
                    close_position(symbol, amount, 'sell', 'Short', tp)
                    in_position = False
                    sell_pos = False
                    with open('order_info.json', 'r') as f:
                        json_order_info = f.read()
                    # Convert the JSON data back to a dictionary
                    info = json.loads(json_order_info)
                    sellcsv(df, buyprice=info['price'], sellprice=read_tradefile(tradesfile, 'short'), filename=tradesfile)
                elif row['Short_Exit'] > 0:
                    limit = row['Short_Exit']
                    if row['High'] >= limit:
                        close_position(symbol, amount, 'sell', 'Short', row['Short_Exit'])
                        in_position = False
                        buy_pos = False
                        with open('order_info.json', 'r') as f:
                            json_order_info = f.read()
                        # Convert the JSON data back to a dictionary
                        info = json.loads(json_order_info)
                        sellcsv(df, buyprice=info['price'], sellprice=read_tradefile(tradesfile, 'short'), filename=tradesfile)

        # Inside the 'if not in_position:' block
        elif not in_position:
            print('In "Not In Position" Block')
            if row['LONG_Signal']:
                print('Get Long Signal, Taking Long Position')
                # Place a market buy order for a long position
                place_market_order(symbol, usdt_amount, tp_perc, 'buy', 'long')
                with open('order_info.json', 'r') as f:
                    json_order_info = f.read()

                # Convert the JSON data back to a dictionary
                info = json.loads(json_order_info)
                buyCSV(df, buyprice=info['buyprice'], sellprice=0, filename=tradesfile)
            elif row['SHORT_Signal']:
                print('Get Short Signal, Taking Short Position')
                # Place a market sell order for a short position
                place_market_order(symbol, usdt_amount, tp_perc, 'sell', 'short')
                with open('order_info.json', 'r') as f:
                    json_order_info = f.read()

                # Convert the JSON data back to a dictionary
                info = json.loads(json_order_info)
                buyCSV(df, buyprice=0, sellprice=info['sellprice'], filename=tradesfile)
            else:
                print('No Signals receive, Exiting')
        csvlog(df, logfile)
except Exception as ex:
    print("An error occurred:", ex)

# Save the updated state to JSON files at the end of the script
state = {
    'in_position': in_position,
    'buy_pos': buy_pos,
    'sell_pos': sell_pos
    }

with open('flag_status.json', 'w') as state_file:
    json.dump(state, state_file)
print("========================================== End of Code ============================================")