import streamlit as st
import pandas_ta as ta
import pandas as pd
import numpy as np
from datetime import datetime
import main_functions
import kraken_config
import plotly.graph_objects as go
import importlib
import subprocess
import warnings

# Filter out the FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)

# If you want to update the module:
importlib.reload(main_functions)
from main_functions import *

# If you want to update the module:
importlib.reload(kraken_config)
from kraken_config import *


exchange = krakenActive(mode)

# Initialize notebook mode
# init_notebook_mode(connected=True)

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

# Streamlit App Title
st.title("Advanced Gann Swing Strategy")
# Sidebar
with st.sidebar:
    st.subheader('Input Parameters')
    
    # Input Parameter for Direction
    direction = st.radio("Select Direction:", ["Both", "Short", "Long"], index=0)  # "Both" is the default value

    # Input Parameter for max_sw_cnt
    max_sw_cnt = st.number_input("Enter max_sw_cnt:", min_value=1, value=3)

    # Exit Percentage
    exit_perc = st.number_input("Uncertain Trend Exit Limit Percentage:", min_value=0.0, max_value=100.0, value=80.0)

    # Take Profit Exit Checkbox and Value
    tp_exit = st.checkbox("Take Profit Exit")
    pi_exit = st.checkbox("Enable/ Disable Pi Exit", True)
    tp_value = 0.38  # Default value
    if tp_exit:
        tp_value = st.number_input("Take Profit Percentage:", min_value=0.0, max_value=1.0, value=0.38)
    else:
        tp_value = 0  # No take profit

    # Toggle button to show/hide log file
    if st.button("Show/Hide Log File"):
        st.session_state.show_log = not st.session_state.get("show_log", False)

    # Radio button to choose mode (sandbox/demo or live)
    mode_options = ["Sandbox/Demo", "Live"]
    mode_choice = st.radio("Select Mode:", mode_options, index=0 if mode == "True" else 1)

    # Example in your Streamlit app
    if mode_choice == "Sandbox/Demo":
        set_sandbox_mode(True)
    elif mode_choice == "Live":
        set_sandbox_mode(False)


    # Get the existing API key and secret from config file
    config_path = 'kraken_config.py'
    live_mode = mode_choice == "Live"
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

# # Toggle button to open/close the log file
# if st.session_state.show_log:
#     open_log_file(main_display)


# Input Parameters
sel_ticker = st.selectbox("Select Ticker Symbol:", fut_tickers, index=fut_tickers.index("BTCUSDT"))
st.write(f"Selected Ticker: {sel_ticker}")

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
    "max_sw_cnt": max_sw_cnt,
    "exit_perc": exit_perc,
    "tp_exit": tp_exit,
    "tp_value": tp_value,
    "direction": direction,  # Add the "direction" parameter to the dictionary
    "pi_exit": True
}

# Define a function to initialize the session state
def initialize_session_state():
    if 'dfs' not in st.session_state:
        st.session_state.dfs = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'dfr' not in st.session_state:
        st.session_state.dfr = None
    if 'result_df' not in st.session_state:
        st.session_state.result_df = None
    if 'fig' not in st.session_state:
        st.session_state.fig = None
    if 'optimized_params_dict' not in st.session_state:
        st.session_state.optimized_params_dict = None
    
# Create a "Calculate" button
calculate_button = st.button("Backtest and Display Trades")

if calculate_button:
    df = getdata(sel_ticker, mapped_timeframe, day)
    st.session_state.df = df
    # Calculate Signals:
    calculate_candle_type(df)
    dfs = calculate_gann_signals(df, max_sw_cnt, exit_perc = exit_perc/100, pi_exit = pi_exit)
    st.session_state.dfs = dfs
    # st.write(dfs)
    results_data, result_df = backtest(dfs, sel_ticker, commission=0.04/100, tp_perc = tp_value, direction = direction)
    st.session_state.result_df = result_df
    # st.write(results_data)
    dfr = displayTrades(direction, **results_data)
    st.session_state.dfr = dfr
    st.subheader('Trades Data')
    st.write(dfr)

    # Plot the chart
    fig = plot_advanced_gann_swing_chart(dfs, dfr)
    st.session_state.fig = fig
    # Display the chart in Streamlit
    st.plotly_chart(fig)

# Create a button to copy the parameters to a JSON file
if st.button("Copy Optimized Parameters to Bot"):
    # Display the stored data
    if st.session_state.result_df is not None:
        st.subheader("Backtest Results:")
        st.session_state.result_df
    if st.session_state.dfr is not None:
        st.subheader("Trades History")
        st.write(st.session_state.dfr)
    if st.session_state.fig is not None:
        st.subheader("Plot Chart:")
        st.plotly_chart(st.session_state.fig)

    # Save the optimized parameters to JSON file
    json_file_path = "optimized_params.json"
    with open(json_file_path, 'w') as f:
        json.dump(final_params_dict, f)

    # Display a success message
    st.success("Optimized parameters copied to the Bot Successfully!")
    st.write(final_params_dict)

# # Toggle button to open/close the log file
# if st.session_state.show_log:
#     open_log_file(main_display)