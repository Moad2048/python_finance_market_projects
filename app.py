import MetaTrader5 as mt5 # to access historcal data
import pandas as pd # for data analysis and calculation of technical indcator
import tdclient as TDClient
import plotly.express as px # for data visualization
import plotly.graph_objects as go
from datetime import datetime, time ,timezone #to specify the date time range for historical data
from IPython.display import display, Markdown, Latex # to display result in python notebook


# Conecte mt5
mt5.initialize()
# logine mt5
login = 1052264766
password = 'xAsej1v8fg*'
server = 'FTMO-Demo'

mt5.login(login,password,server)

# this function retreives olhc data from mt5 account and return a data frame
def get_ohlc(symbol, timeframe, start_datetime, end_datetime):
    ohlc = mt5.copy_rates_range(symbol, timeframe, start_datetime, end_datetime)
    ohlc_df = pd.DataFrame(ohlc)
    ohlc_df['time'] = pd.to_datetime(ohlc_df['time'], unit= 's')
    return ohlc_df[['time', 'open', 'high', 'low', 'close']]
# 30minut df
symbol = 'EURUSD'
pos_size = 1
timeframe = mt5.TIMEFRAME_M30
start_datetime = datetime(2022,1,1)
end_datetime = datetime(2024,1,1)
ohlc_df = get_ohlc(symbol, timeframe, start_datetime, end_datetime)
ohlc_df

# hour4 df
timeframe4 = mt5.TIMEFRAME_H4
hourly_df = get_ohlc(symbol, timeframe4, start_datetime, end_datetime)

# daily df
timeframe1 = mt5.TIMEFRAME_D1
daily_df = get_ohlc(symbol, timeframe1, start_datetime, end_datetime)
# visualizing the ohlc data
fig = go.Figure(data=[go.Candlestick(x=ohlc_df['time'],
                                     open=ohlc_df['open'],
                                     high=ohlc_df['high'],
                                     low=ohlc_df['low'],
                                     close=ohlc_df['close'])])

# Update layout if necessary
fig.update_layout(height=600, xaxis_rangeslider_visible=False)

# Display the figure
fig.show()

# start b2 strategy
# Calculate Pivot Point, R1, R2, R3, stopeR4, S1, S2, S3, stopeS4 levels with Fibonacci retracement
daily_df["pivot"] = (daily_df["high"] + daily_df["low"] + daily_df["close"]) / 3
daily_df["prange"] = (daily_df["high"] - daily_df["low"])
ohlc_df["R1"] = daily_df["pivot"] + 0.382 * daily_df["prange"]
ohlc_df["R2"] = daily_df["pivot"] + 0.618 * daily_df["prange"]
ohlc_df["R3"] = daily_df["pivot"] + 1.000 * daily_df["prange"]

ohlc_df["S1"] = daily_df["pivot"] - 0.382 * daily_df["prange"]
ohlc_df["S2"] = daily_df["pivot"] - 0.618 * daily_df["prange"]
ohlc_df["S3"] = daily_df["pivot"] - 1.000 * daily_df["prange"]
ohlc_df

#setting the sma 1 and 14 periods
furst_sma_period = 1
second_sma_period = 14
# sma 1
ohlc_df['sma_1'] = hourly_df['close'].rolling(furst_sma_period).mean()
ohlc_df['prev_sma_1'] = ohlc_df['sma_1'].shift(1) #to find crossovers, previous sma value is necessary using shift()
# sma 14
ohlc_df['sma_14'] = hourly_df['close'].rolling(second_sma_period).mean()
ohlc_df

#setting the 11 and 114 sma periods
thurd_sma_period = 1
fourth_sma_period = 14
# sma 11
ohlc_df['sma_11'] = daily_df['close'].rolling(thurd_sma_period).mean()
ohlc_df['prev_sma_11'] = ohlc_df['sma_11'].shift(1) #to find crossovers, previous sma value is necessary using shift()
# sma 114
ohlc_df['sma_114'] = daily_df['close'].rolling(fourth_sma_period).mean()
ohlc_df

#setting entring and closing time and one trade a day
# Set the start and end times for your desired trading hours
start_time = datetime.strptime('07:00:00', '%H:%M:%S').time()
end_time = datetime.strptime('16:00:00', '%H:%M:%S').time()

# Filter the trade data for trades within the specified trading hours
trades_within_hours = ohlc_df[(ohlc_df['time'].dt.time >= start_time) & (ohlc_df['time'].dt.time <= end_time)]

# Close all open positions at 11:45 PM
first_trade_per_day = ohlc_df.groupby(ohlc_df['time'].dt.time).first()
end_trading_time = datetime.strptime('23:45:00', '%H:%M:%S').time()
open_positions = trades_within_hours[trades_within_hours['time'].dt.time == end_trading_time]
# function to trading
ohlc_df["stopeR4"] = ohlc_df["close"] >= ohlc_df["R2"] + 0.0001*40
ohlc_df["bearish_pivot"] = ohlc_df["close"] >= ohlc_df["R2"]
ohlc_df["stopeS4"] = ohlc_df["close"] <= ohlc_df["S2"] - 0.0001*40
ohlc_df["bullish_pivot"] = ohlc_df["close"] <= ohlc_df["S2"]
ohlc_df['profitR5'] = ohlc_df['close'] <= ohlc_df["R1"] - ohlc_df['R3'] + ohlc_df["R1"] - 0.0001*40
ohlc_df['profitS5'] = ohlc_df['close'] >= ohlc_df["S1"] - ohlc_df["S3"] + ohlc_df["S1"] + 0.0001*40
def entring_stoploss_profit () :
    bullish_crossover = ohlc_df['sma_1'] > ohlc_df['sma_14'] and ohlc_df['sma_11'] > ohlc_df['sma_114'] and ohlc_df['prev_sma_1'] < ['sma_14'] and ohlc_df['prev_sma_11'] < ['sma_114']
    bearish_crossover = ohlc_df['sma_1'] < ohlc_df['sma_14'] and ohlc_df['sma_11'] < ohlc_df['sma_114'] and ohlc_df['prev_sma_1'] > ['sma_14'] and ohlc_df['prev_sma_11'] > ['sma_114']
    buy_signals = bullish_crossover and ohlc_df["bullish_pivot"] and open_positions and first_trade_per_day 
    sell_signals = bearish_crossover and ohlc_df["bearish_pivot"] and open_positions and first_trade_per_day
    close_condition1 = ohlc_df["stopeS4"] or end_trading_time
    close_condition2 = ohlc_df["stopeR4"] or end_trading_time
    if buy_signals :
        return True
    
    elif sell_signals :
        return True
        
    else :
        return False
    # stop loss
    if buy_signals == 0 :
        return close_condition1
    elif sell_signals == 0 :
        return close_condition2
    
# take profit
    if buy_signals == 0 :
        return ohlc_df['profitS5']

    elif sell_signals == 0 :
        return ohlc_df['profitR5']

ohlc_df['entring_stoploss_profit'] = ohlc_df.apply(entring_stoploss_profit, axis=1)
ohlc_df