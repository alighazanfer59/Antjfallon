import streamlit as st
import pandas_ta as ta
import pandas as pd
import numpy as np
from datetime import datetime
import main_functions
import kraken_config
import plotly.graph_objects as go
import importlib
from io import BytesIO
import subprocess
import warnings

# from session_state import init
# init()  # Initialize session state
def init_session_state():
    if not hasattr(st, 'session_state'):
        st.session_state.my_session_state = None


# Filter out the FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)

# If you want to update the module:
importlib.reload(main_functions)
from main_functions import *

# If you want to update the module:
importlib.reload(kraken_config)
from kraken_config import *

# exchange = krakenActive(mode)

# Create a session state variable to track the Streamlit message display
if 'streamlit_message_displayed' not in st.session_state:
    st.session_state.streamlit_message_displayed = False

pd.set_option('display.max_rows', 400)  # Set the maximum number of rows to display

fut_tickers = ['SANDUSDT', 'DGBUSDT', 'EGLDUSDT', 'BTCUSDT', 'GALAUSDT', 'TUSDT', 'AXSUSDT', 'CTKUSDT', 'SPELLUSDT', 'EOSUSDT', 'AGIXUSDT', 
               'DYDXUSDT', 'LUNA2USDT', 'RENUSDT', 'APEUSDT', 'CHRUSDT', 'FLMUSDT', 'BTCDOMUSDT', 'LDOUSDT', 'ZILUSDT', 'OMGUSDT', '1000XECUSDT', 
               'SOLUSDT', 'LINAUSDT', 'SFPUSDT', 'PEOPLEUSDT', 'VETUSDT', 'BAKEUSDT', 'MINAUSDT', 'STORJUSDT', 'HIGHUSDT', 'RSRUSDT', 'YFIUSDT', 
               'MAGICUSDT', 'IDEXUSDT', 'LQTYUSDT', 'DOTUSDT', 'ASTRUSDT', 'XEMUSDT', 'UMAUSDT', 'IOTAUSDT', 'LINKUSDT', 'ALICEUSDT', 'WOOUSDT', 
               'ETCUSDT', 'DUSKUSDT', 'SKLUSDT', 'ENJUSDT', 'HOOKUSDT', 'ARKMUSDT', 'NKNUSDT', 'XVGUSDT', 'COCOSUSDT', 'HOTUSDT', 'LEVERUSDT', 
               'MDTUSDT', 'ZECUSDT', 'KAVAUSDT', '1000SHIBUSDT', 'PHBUSDT', 'OCEANUSDT', 'TOMOUSDT', 'ICXUSDT', 'FETUSDT', 'MATICUSDT', 'BALUSDT', 
               'IOSTUSDT', 'THETAUSDT', 'XRPUSDT', 'RADUSDT', 'CELOUSDT', '1000PEPEUSDT', 'API3USDT', 'DOGEUSDT', 'AVAXUSDT', 'HFTUSDT', 'ZRXUSDT', 
               'CFXUSDT', 'BLURUSDT', 'ARBUSDT', 'WAVESUSDT', 'UNFIUSDT', 'LRCUSDT', 'TRBUSDT', 'SSVUSDT', 'IOTXUSDT', 'MASKUSDT', 'ARPAUSDT', 'ANTUSDT', 
               'HBARUSDT', 'SNXUSDT', 'USDCUSDT', 'ENSUSDT', 'SUSHIUSDT', 'STXUSDT', '1INCHUSDT', 'ATOMUSDT', 'GRTUSDT', 'AMBUSDT', '1000FLOKIUSDT', 'ALGOUSDT', 
               'IMXUSDT', 'BANDUSDT', 'RNDRUSDT', 'FLOWUSDT', 'FOOTBALLUSDT', 'BCHUSDT', 'NEOUSDT', 'REEFUSDT', 'ARUSDT', 'DARUSDT', 'BELUSDT', 'DASHUSDT', 
               'MKRUSDT', 'BLUEBIRDUSDT', 'DENTUSDT', 'ATAUSDT', 'C98USDT', 'GMTUSDT', 'LTCUSDT', 'INJUSDT', 'RDNTUSDT', 'OPUSDT', 'ZENUSDT', 'GMXUSDT', 
               'JOEUSDT', 'QNTUSDT', 'COMBOUSDT', 'BNXUSDT', 'WLDUSDT', 'XVSUSDT', 'DEFIUSDT', 'KSMUSDT', 'SXPUSDT', 'CRVUSDT', 'AGLDUSDT', 'XLMUSDT', 
               'CVXUSDT', 'FILUSDT', 'RLCUSDT', 'ALPHAUSDT', 'AAVEUSDT', 'RUNEUSDT', 'ANKRUSDT', 'KEYUSDT', 'XTZUSDT', 'MANAUSDT', 'QTUMUSDT', 'PENDLEUSDT', 
               'XMRUSDT', 'COMPUSDT', 'ONEUSDT', 'KNCUSDT', 'CHZUSDT', 'EDUUSDT', 'CELRUSDT', 'TLMUSDT', 'ONTUSDT', 'GALUSDT', 'LITUSDT', 'UNIUSDT', 
               'JASMYUSDT', 'CKBUSDT', 'ETHUSDT', 'BLZUSDT', '1000LUNCUSDT', 'CTSIUSDT', 'MAVUSDT', 'OGNUSDT', 'MTLUSDT', 'LPTUSDT', 'FXSUSDT', 'RVNUSDT', 
               'PERPUSDT', 'NMRUSDT', 'COTIUSDT', 'APTUSDT', 'IDUSDT', 'BNBUSDT', 'FTMUSDT', 'AUDIOUSDT', 'TRXUSDT', 'GTCUSDT', 'BATUSDT', 'ACHUSDT', 'STGUSDT', 
               'SUIUSDT', 'ICPUSDT', 'STMXUSDT', 'KLAYUSDT', 'TRUUSDT', 'ADAUSDT', 'ROSEUSDT', 'NEARUSDT']

# # Initialize session state
# if 'max_sw_cnt_l' not in st.session_state:
#     st.session_state.max_sw_cnt_l = 3
#     st.session_state.max_sw_cnt_s = 3
#     st.session_state.tp_exit_long = False
#     st.session_state.tp_value_long = 15
#     st.session_state.tsl_offset_long_en = True
#     st.session_state.tsl_offset_pct_long = 0.1
#     st.session_state.exit_limit_long_en = True
#     st.session_state.exit_perc_long_input = 80.0
#     st.session_state.pi_exit = True
#     st.session_state.tp_exit_short = True
#     st.session_state.tp_value_short = 38
#     st.session_state.tsl_offset_short_en = True
#     st.session_state.tsl_offset_pct_short = 0.1
#     st.session_state.exit_limit_short_en = True
#     st.session_state.exit_perc_short_input = 80.0
initial_capital = 10000
# Constants for position size types and price types
pos_size_types = ['Fixed', 'Dynamic']
pos_size_price = ['Quote', 'Base', 'Percentage']

# Define tooltips
tooltip_base = "Position size value is specified in base currency (e.g. BTC)."
tooltip_quote = "Position size value is specified in quote currency (i.e. USD)."
tooltip_percentage = "Position size value is specified as a percentage of available equity."
tt_method_type = """Fixed P/S: $1K, or 0.1 BTC
Dynamic P/S: Max Risk [%]"""
# Define the category label text
swing_label = "Swing"
setting_label_long = "Settings Long"
setting_label_short = "Settings Short"
authen_label = "Login info"
pos_label = "Position Size Calculator" 

# Streamlit App Title
st.title("Advanced Gann Swing Strategy")
# Sidebar
with st.sidebar:
    # Toggle button to show/hide log file
    if st.button("Show/Hide Log File"):
        st.session_state.show_log = not st.session_state.get("show_log", False)
    
    st.title("Strategy Parameters")
    st.markdown(category_label(pos_label))
    direction = st.radio("Select Direction:", ["Both", "Short", "Long"], index=0)  # "Both" is the default value
    # Strategy inputs
    method_type = st.selectbox("Position Size", pos_size_types, index=1, help=tt_method_type)
    
    if method_type == "Dynamic":
        price_type = st.selectbox("Price Type", pos_size_price, index=2, help=tooltip_percentage)
        value_label = "Percentage"
        value = st.number_input("Position Size Value (%)", value=20, help="Enter the percentage value for position size.")
    else:
        price_type = st.selectbox("Price Type", pos_size_price, index=0, help=tooltip_quote)
        if price_type == "Quote":
            value_label = "$1000"
            value = st.number_input("Position Size Value (USD)", value=1000.0, help="Enter the position size value in quote currency (USD).")
        elif price_type == "Base":
            value_label = "0.1 BTC"
            value = st.number_input("Position Size Value (BTC)", value=0.1, help="Enter the position size value in base currency (BTC).")
        else:
            value_label = "Percentage"
            value = st.number_input("Position Size Value (%)", value=20, help="Enter the percentage value for position size.")
    
    # Create the centered category label
    st.markdown(category_label(swing_label))

    # Input Parameter for max_sw_cnt
    max_sw_cnt_l = st.number_input("Long Swing Count", min_value=1, value=3)
    max_sw_cnt_s = st.number_input("Short Swing Count", min_value=1, value=4)

    # Create a dictionary to map options to values
    side_mapping = {
        "Long": "long",
        "Short": "short"
    }

    # Create a selectbox for the user to choose the side
    selected_option = st.selectbox("Show Swing", list(side_mapping.keys()))
    # Get the corresponding value based on the selected option
    showSide = side_mapping[selected_option]
    # st.write("showSide Selected for Chart: ", showSide)
    
    # Create the centered category label
    st.markdown(category_label(setting_label_long))
    
    init_sl_offset_long_input = st.number_input("Initial SL Offset [%]", min_value=0.0, max_value=100.0, step=0.1, value=0.1, key='i_sl_offset_pct_long')
    init_sl_offset_long = init_sl_offset_long_input * 0.01
    
    # Take Profit Exit Checkbox and Value
    tp_exit_long = st.checkbox("Take Profit Exit", False, key='tpl')
    tp_value_long = st.number_input("Take Profit [%]", min_value=0, max_value=100, value=15, key='tp_value_long')
    tp_perc_long = 0 if tp_exit_long == False else tp_value_long*0.01

    # Trailing offset Exit Checkbox and Value
    tsl_offset_long_en = st.checkbox("Trailing SL offset Enable/Disable", True, key='tsl_offset_long')
    tsl_offset_pct_long = st.number_input("Trailing SL Offset [%]", min_value=0.0, max_value=100.0, step=0.1, value=0.1, key='tsl_offset_pct_long')
    tsl_offset_long = tsl_offset_pct_long * 0.01
    
    # Exit Percentage
    exit_limit_long_en = st.checkbox("Check For Signs Of Trend Reversal", True, key='exit_long')
    exit_perc_long_input = st.number_input("Percentage For Limit Order Price Calculation", min_value=0.0, max_value=100.0, value=80.0, key='exit_perc_long_input')
    exit_perc_long = 0 if exit_limit_long_en == False else exit_perc_long_input*0.01
    
    pi_exit_long = st.checkbox("Exit On Pi Cycle", True, key='pi_exit_lonng')
    
    # Create the centered category label
    st.markdown(category_label(setting_label_short))
    
    init_sl_offset_short_input = st.number_input("Initial SL Offset [%]", min_value=0.0, max_value=100.0, step=0.1, value=0.1, key='i_sl_offset_pct_short')
    init_sl_offset_short = init_sl_offset_short_input * 0.01
    
    # Take Profit Exit Checkbox and Value
    tp_exit_short = st.checkbox("Take Profit Exit", True, key="tps")
    tp_value_short = st.number_input("Take Profit [%]", min_value=0, max_value=100, value=38, key='tp_value_short')
    tp_perc_short = 0 if tp_exit_short == False else tp_value_short*0.01

    # Trailing offset Exit Checkbox and Value
    tsl_offset_short_en = st.checkbox("Trailing SL offset Enable/Disable", True, key='tsl_offset_short')
    tsl_offset_pct_short = st.number_input("Trailing SL Offset [%]", min_value=0.0, max_value=100.0, step=0.1, value=0.1, key='tsl_offset_pct_short')
    tsl_offset_short = tsl_offset_pct_short * 0.01
    
    # Exit Percentage
    exit_limit_short_en = st.checkbox("Check For Signs Of Trend Reversal", False, key='exit_short')
    exit_perc_short_input = st.number_input("Percentage For Limit Order Price Calculation", min_value=0.0, max_value=100.0, value=80.0, key='exit_perc_short_input')
    exit_perc_short = 0 if exit_limit_short_en == False else exit_perc_short_input*0.01
    
    pi_exit_short = st.checkbox("Exit On Pi Cycle", False, key='pi_exit_short')
    
    # Reset button to set all input values to their defaults
    # if st.button("Reset to Defaults"):
    #     max_sw_cnt_l = 3
    #     max_sw_cnt_s = 3
    #     tp_exit_long = False
    #     tp_value_long = 15
    #     tsl_offset_long_en = True
    #     tsl_offset_pct_long = 0.1
    #     exit_limit_long_en = True
    #     exit_perc_long_input = 80.0
    #     tp_exit_short = True
    #     tp_value_short = 38
    #     tsl_offset_short_en = True
    #     tsl_offset_pct_short = 0.1
    #     exit_limit_short_en = True
    #     exit_perc_short_input = 80.0
    #     pi_exit = True

    # Create the centered category label
    st.markdown(category_label(authen_label))
    # Check the value of sandbox_mode in kraken_config.py
    mode = kraken_config.sandbox_mode
    # Radio button to choose mode (sandbox/demo or live)
    mode_options = ["Sandbox/Demo", "Live"]

    # Check if mode_choice is in session state and set the mode accordingly
    init_session_state()
    # Initialize session state
    if 'mode_choice' not in st.session_state:
        # Set the initial mode_choice based on the value in kraken_config.py
        st.session_state.mode_choice = "Sandbox/Demo" if mode else "Live"

    # Get the selected mode_choice from session state
    mode_choice = st.radio("Select Mode:", mode_options, index=mode_options.index(st.session_state.mode_choice))

    # Set the mode_choice in session state
    st.session_state.mode_choice = mode_choice
    # Call check_authentication_and_display when mode_choice changes
    exchange = check_authentication_and_display(st.session_state.mode_choice)

    # Set sandbox_mode based on mode_choice and update it in kraken_config.py
    sandbox_mode = (mode_choice == "Sandbox/Demo")
    set_sandbox_mode(sandbox_mode)
    # Print the updated mode for debugging
    st.write("Updated SandBox Mode to: ", sandbox_mode)
    
    # Get the existing API key and secret from config file
    config_path = 'kraken_config.py'
    live_mode = mode_choice == "Live"  # Check the mode from kraken_config.py
    api_key, secret_key = get_api_key_secret(config_path, live_mode=live_mode)

    if mode_choice == "Sandbox/Demo":
        st.write("Using Sandbox/Demo Mode")
    elif mode_choice == "Live":
        if not api_key or not secret_key:
            st.warning("Please provide your API key and secret for Live Mode below.")
            api_key = st.text_input("Enter Live API Key:")
            secret_key = st.text_input("Enter Live Secret Key:")
            if st.button("Save Live API Key and Secret"):
                set_api_key_secret(api_key, secret_key, config_path, live_mode=True)
                st.success("Live API Key and Secret saved successfully.")
        else:
            st.write("Using Live Mode")
            
            # Option to change API key and secret for Live Mode
            if st.checkbox("Change Live API Key and Secret"):
                st.warning("You can change your Live API key and secret below.")
                new_api_key = st.text_input("Enter New Live API Key:")
                new_secret_key = st.text_input("Enter New Live Secret Key:")
                if st.button("Update Live API Key and Secret"):
                    set_api_key_secret(new_api_key, new_secret_key, config_path, live_mode=True)
                    st.success("Live API Key and Secret updated successfully.")

# Main window
main_display = st.empty()

# Initialize session state
if 'show_log' not in st.session_state:
    st.session_state.show_log = False  # Set it to False by default to hide the log file

# Toggle button to open/close the log file
if st.session_state.show_log:
    open_log_file(main_display)

# # Print input values for debugging
# st.write("Long Swing Count (max_sw_cnt_l):", max_sw_cnt_l)
# st.write("Short Swing Count (max_sw_cnt_s):", max_sw_cnt_s)
# st.write("Take Profit Exit Long (tp_exit_long):", tp_exit_long)
# st.write("Take Profit % Long (tp_value_long):", tp_perc_long)
# st.write("Trailing SL Offset Long Enable/Disable (tsl_offset_long_en):", tsl_offset_long_en)
# st.write("Trailing SL Offset % Long (tsl_offset_pct_long):", tsl_offset_long)
# st.write("Exit Percentage Long Enable (exit_limit_long_en):", exit_limit_long_en)
# st.write("Percentage for Limit Order Price Calculation Long (exit_perc_long_input):", exit_perc_long)

# st.write("Take Profit Exit Short (tp_exit_short):", tp_exit_short)
# st.write("Take Profit % Short (tp_value_short):", tp_perc_short)
# st.write("Trailing SL Offset Short Enable/Disable (tsl_offset_short_en):", tsl_offset_short_en)
# st.write("Trailing SL Offset % Short (tsl_offset_pct_short):", tsl_offset_short)
# st.write("Exit Percentage Short Enable (exit_limit_short_en):", exit_limit_short_en)
# st.write("Percentage for Limit Order Price Calculation Short (exit_perc_short_input):", exit_perc_short)

# st.write("Exit on Pi Cycle (pi_exit):", pi_exit)

# # Toggle button to open/close the log file
# if st.session_state.show_log:
#     open_log_file(main_display)
# st.write("Selected Method Type:", method_type)
# st.write("Selected Price Type:", price_type)
# st.write("Selected Value Label:", value_label)
# st.write("Value:", value)

# Input Parameters
sel_ticker = st.selectbox("Select Ticker Symbol:", fut_tickers, index=fut_tickers.index("BTCUSDT"))
# st.write(f"Selected Ticker: {sel_ticker}")

# You can use a date input widget for the start date
start_date_input = str(st.date_input("Select Start Date:", datetime(2019, 9, 8)))
start_date = datetime.strptime(start_date_input, "%Y-%m-%d")

current_date = str(datetime.now())

# Input the timeframe as a selectbox
tf = ['1min', '5min', '15min', '30min', '1hour', '4hour', '12hour', '1day', '1week']  # Add more timeframes as needed

sel_tf = st.selectbox("Select Timeframe:", tf, index=tf.index('1day'))
# Map the selected timeframe to its value
mapped_timeframe = map_timeframe(sel_tf)

# Print the mapped value
print("Mapped Value:", mapped_timeframe)

# Calculate the difference in days
day = (datetime.now() - start_date).days

# Display the calculated day difference
st.write(f"Number of days since start date: {day} days")

# Create a dictionary for the optimized parameters
final_params_dict = {
    "symbol": sel_ticker,
    "timeframe": sel_tf,
    "max_sw_cnt_l": max_sw_cnt_l,
    "max_sw_cnt_s": max_sw_cnt_s,
    "init_sl_offset_long": init_sl_offset_long,
    "tp_perc_long": tp_perc_long,
    "tsl_offset_long": tsl_offset_long,
    "exit_perc_long": exit_perc_long,
    "pi_exit_long": pi_exit_long,
    "init_sl_offset_short": init_sl_offset_short,
    "tp_perc_short": tp_perc_short,
    "tsl_offset_short": tsl_offset_short,
    "exit_perc_short": exit_perc_short,
    "pi_exit_short": pi_exit_short,
    "direction": direction,  # Add the "direction" parameter to the dictionary
    "method_type": method_type,
    "price_type": price_type,
    "pos_size_value": value,
}

# Define a function to initialize the session state
def initialize_session_state():
    if 'dfs' not in st.session_state:
        st.session_state.dfs = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'dfr' not in st.session_state:
        st.session_state.dfr = None
    if 'dfr_display' not in st.session_state:
        st.session_state.dfr_display = None
    if 'result_df' not in st.session_state:
        st.session_state.result_df = None
    if 'fig' not in st.session_state:
        st.session_state.fig = None
    if 'optimized_params_dict' not in st.session_state:
        st.session_state.optimized_params_dict = None

# Function to generate Excel file as BytesIO object
def download_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Sheet1', index=False)
    output.seek(0)
    return output

# Create a "Calculate" button
calculate_button = st.button("Backtest and Display Trades")
initialize_session_state()

if calculate_button:
    df = getdata(sel_ticker, mapped_timeframe, day)
    st.session_state.df = df
    # # Calculate Signals:
    # calculate_candle_type(df)
    dfl = calculate_gann_signals(df, max_sw_cnt = max_sw_cnt_l, exit_perc = exit_perc_long, side = "long")
    dfsh = calculate_gann_signals(df, max_sw_cnt = max_sw_cnt_s, exit_perc = exit_perc_short, side = "short")
    unique_columns = dfsh.columns.difference(dfl.columns)
    dfs = pd.concat([dfl, dfsh[unique_columns]], axis=1)
    st.session_state.dfs = dfs
    # st.write(dfs)
    # tp_perc = 0 if tp_exit == False else tp_value
    results_data, result_df = backtest(exchange, dfs, sel_ticker, direction, tp_perc_long=tp_perc_long, tp_perc_short=tp_perc_short, 
                                   pi_exit_long=pi_exit_long, pi_exit_short=pi_exit_short, tsl_offset_long_en=tsl_offset_long_en, tsl_offset_short_en=tsl_offset_short_en, 
                                   tsl_offset_long_pct=tsl_offset_long, tsl_offset_short_pct=tsl_offset_short, init_sl_offset_long=init_sl_offset_long, 
                                   init_sl_offset_short=init_sl_offset_short, initial_capital=initial_capital, method_type=method_type, price_type=price_type,value=value,
                                   )
    st.session_state.result_df = result_df
    # st.write(results_data)
    dfr, dfr_display = displayTrades(direction, **results_data)
    st.session_state.dfr = dfr
    st.session_state.dfr_display = dfr_display
    st.subheader('Trades Data')
    st.dataframe(dfr_display)
    
    # Plot the chart
    # fig = plot_advanced_gann_swing_chart(dfs, dfr)
    # st.session_state.fig = fig
    # # Display the chart in Streamlit
    # st.plotly_chart(fig)
# Create a button to toggle the chart's fullscreen mode
if st.button("Open Fullscreen Chart"):
    # st.write('showSide Selected: ', showSide)
    st.write(st.session_state.result_df)
    st.subheader('Trades Data')
    st.dataframe(st.session_state.dfr_display)
    with st.expander("Fullscreen Chart", expanded=True):
        # Create a Plotly Go figure with your chart data
        try:
            fig = plot_advanced_gann_swing_chart(st.session_state.dfs, st.session_state.dfr, side= showSide)
            st.session_state.fig = fig
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Check if 'fig' exists in session state and initialize it if not
if 'fig' not in st.session_state:
    st.session_state.fig = None
    
# Create a button to copy the parameters to a JSON file
if st.button("Copy Optimized Parameters to Bot"):
    # Display the stored data
    if st.session_state.result_df is not None:
        st.subheader("Backtest Results:")
        st.session_state.result_df
    if st.session_state.dfr_display is not None:
        st.subheader("Trades History")
        st.dataframe(st.session_state.dfr_display)
    if st.session_state.fig is not None:
        st.subheader("Plot Chart:")
        st.plotly_chart(st.session_state.fig, use_container_width=True)

    # Save the optimized parameters to JSON file with pretty formatting
    json_file_path = "optimized_params.json"
    with open(json_file_path, 'w') as f:
        json.dump(final_params_dict, f, indent=4)  # Set indent to 4 for 4 spaces of indentation

    # Display a success message
    st.success("Optimized parameters copied to the Bot Successfully!")
    st.write(final_params_dict)

# if st.session_state.dfr_display is not None:
#     # Add a download button to save the DataFrame as an Excel file
#     excel_data = download_excel(st.session_state.dfr_display)
#     if excel_data:
#         if st.download_button(
#             label="Download Excel File",
#             data=excel_data,
#             key="download-excel-button",
#             file_name="output.xlsx",  # The default file name for the downloaded file
#         ):
#             st.success("Excel file saved successfully!")
#     st.write("You can click the 'Download Excel File' button above to save the DataFrame as an Excel file.")
# # Toggle button to open/close the log file
# if st.session_state.show_log:
#     open_log_file(main_display)   