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

symbol = 'EURUSD'
pos_size = 1
timeframe = mt5.TIMEFRAME_M30
start_datetime = datetime(2022,1,1)
end_datetime = datetime(2024,1,1)
ohlc_df = get_ohlc(symbol, timeframe, start_datetime, end_datetime)
ohlc_df
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
# Get daily high, low, and close prices
dailyHigh = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_D1, 0, 1)[0][2]
dailyLow = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_D1, 0, 1)[0][3]
dailyClose = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_D1, 0, 1)[0][4]

# Calculate Pivot Point, R1, R2, R3, stopeR4, S1, S2, S3, stopeS4 levels with Fibonacci retracement
pivot = ohlc_df[ohlc_df['dailyHigh'] + ohlc_df['dailyLow'] + ohlc_df['dailyClose'] / 3]
prange = ohlc_df[ohlc_df['dailyHigh'] - ohlc_df['dailyLow']]

R1 = pivot + 0.382 * prange
R2 = ohlc_df[ohlc_df['pivot'] + ohlc_df['0.618'] * ohlc_df['prange']]
R3 = pivot + 1.000 * prange
stopeR4 = ohlc_df[ohlc_df['close'] >= ohlc_df['R2'] + ohlc_df['0.0001*40']]
profitR5 = ohlc_df[ohlc_df['close'] <= ohlc_df['R1'] - ohlc_df['R3'] + ohlc_df['R1'] - ohlc_df['0.0001*40']]
bearish_pivot = ohlc_df[ohlc_df['close'] >= ohlc_df['R2']]
S1 = pivot - 0.382 * prange
S2 = ohlc_df[ohlc_df['pivot'] - ohlc_df['0.618'] * ohlc_df['prange']]
S3 = pivot - 1.000 * prange
stopeS4 = ohlc_df[ohlc_df['close'] <= ohlc_df['S2'] - ohlc_df['0.0001*40']]
profitS5 = ohlc_df[ohlc_df['close'] >= ohlc_df['S1'] - ohlc_df['S3'] + ohlc_df['S1'] + ohlc_df['0.0001*40']]
bullish_pivot = ohlc_df[ohlc_df['close'] <= ohlc_df['S2']]

#setting entring and closing time and one trade a day

# Set the start and end times for your desired trading hours
start_time = datetime.strptime('07:00:00', '%H:%M:%S').time()
end_time = datetime.strptime('16:00:00', '%H:%M:%S').time()

# Filter the trade data for trades within the specified trading hours
trades_within_hours = ohlc_df[(ohlc_df['time'].dt.time >= start_time) & (ohlc_df['time'].dt.time <= end_time)]

# Close all open positions at 11:45 PM
first_trade_per_day = ohlc_df.groupby('date').first()
end_trading_time = datetime.strptime('23:45:00', '%H:%M:%S').time()
open_positions = trades_within_hours[trades_within_hours['time'].dt.time == end_trading_time]

#setting the sma periods
furst_sma_period = 1
second_sma_period = 14
thurd_sma_period = 1
fourth_sma_period = 14
sma_timeframe = '4H'
second_sma_timeframe = '1D'
# sma 1
ohlc_df['sma_1'] = ohlc_df['close'].rolling(furst_sma_period, sma_timeframe).mean()

ohlc_df['prev_sma_1'] = ohlc_df['sma_1'].shift(1) #to find crossovers, previous sma value is necessary using shift()
# sma 14
ohlc_df['sma_14'] = ohlc_df['close'].rolling(second_sma_period, sma_timeframe).mean()
# sma 11
ohlc_df['sma_11'] = ohlc_df['close'].rolling(thurd_sma_period, second_sma_timeframe).mean()
ohlc_df['prev_sma_11'] = ohlc_df['sma_11'].shift(1) #to find crossovers, previous sma value is necessary using shift()
# sma 114
ohlc_df['sma_114'] = ohlc_df['close'].rolling(fourth_sma_period, second_sma_timeframe).mean()
# trades
trades = pd.ohlc_df(coluns=['state', 'order_type', 'open_time', 'open_price', 'close_time', 'close_prise'])
trades
# function to trading
def entring_stoploss_profit (row) :
      bullish_crossover = row['sma_1'] > row['sma_14'] and row['sma_11'] > row['sma_114'] and row['prev_sma_1'] < ['sma_14'] and row['prev_sma_11'] < ['sma_114']
      bearish_crossover = row['sma_1'] < row['sma_14'] and row['sma_11'] < row['sma_114'] and row['prev_sma_1'] > ['sma_14'] and row['prev_sma_11'] > ['sma_114']
      buy_signals = bullish_crossover and bullish_pivot and open_positions and first_trade_per_day 
      sell_signals = bearish_crossover and bearish_pivot and open_positions and first_trade_per_day
      num_open_trades = trades[trades['state'] == 'open'].shape[0]
      close_condition1 = stopeS4 or end_trading_time
      close_condition2 = stopeR4 or end_trading_time
      if buy_signals :
          trades.loc[len(trades),trades.coluns] = ['open', 'buy', ohlc_df['time'], ohlc_df['open'], None, None]
          print('make a buy to open order ...')
        
      elif sell_signals :
          trades.loc[len(trades),trades.coluns] = ['open', 'sell', ohlc_df['time'], ohlc_df['open'], None, None]
          print('make a sell to open order ...')
        
      else :
        print('not making an order ...')

# stop loss
      if buy_signals == 0 :
          return close_condition1
          trades.loc[trades['state'] == 'open',['state', 'close_time', 'close_price']] = ['close', ohlc_df['time'], ohlc_df['open']]
      elif sell_signals == 0 :
          return close_condition2
          trades.loc[trades['state'] == 'open',['state', 'close_time', 'close_price']] = ['close', ohlc_df['time'], ohlc_df['stop_loss']]
# take profit
      if buy_signals == 0 :
          return profitS5

      elif sell_signals == 0 :
          return profitR5
      
trades

# applying function to dataframe
fig['entring_stoploss_profit'] = ohlc_df.apply(entring_stoploss_profit, axis=1)
# ploting moving averages and pivot
fig_entring_stoploss_profit = px.line(ohlc_df, x='time', y=['close', 'sma_1', 'sma_11', 'sma_14', 'sma_114', 'S2', 'R2', 'stopeR4', 'profitS5', 'stopeS4', 'profitR5'], title='sma crossover and pivot')
#plotting crossovers
for i, row in ohlc_df[ohlc_df['entring_stoploss_profit'] == True].iterrows():
    fig_entring_stoploss_profit.add_vline(x=row['time'], opacity=0.2)

display(fig_entring_stoploss_profit)
