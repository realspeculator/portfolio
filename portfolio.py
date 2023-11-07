import yfinance as yf
from datetime import datetime
import pandas as pd

import pandas as pd
import os

def build_files_url(files_names):
    
    return "https://raw.githubusercontent.com/realspeculator/live_portfolio/main/2023/010_2023/" + files_names

def get_net_lq_value(url):
    
    df1 = pd.read_csv(url)
    net_lq = df1[df1["DATE"] == "Net Liquidating Value"].iloc[0,1]
    net_lq = float(net_lq.replace("$", "").replace(",", ""))
    
    return net_lq


def get_px(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    df['symbol'] = ticker
    return df 

def get_ret(df, symbol):
    
    df['returns'] = df['Adj Close'].pct_change()
    df[symbol+'_cr'] = (1 + df['returns']).cumprod()
    return df


files_list = os.listdir("../live_portfolio/2023/010_2023/")
files_list.remove(".DS_Store") # Remove Apple .DS_Store file.

urls = list(map(build_files_url, files_list))

orig_net_liq = [100000000] # This value will be the same as begining value for each month.
net_liq = list(map(get_net_lq_value, urls))
net_liq = orig_net_liq + net_liq


# Benchmark Calcs
tickers = ['QQQ', 'IWM', 'DIA', 'SPY']

tickers
inception_date = "2023-10-20"
todays_date = datetime.today().strftime('%Y-%m-%d')



data = [get_px(i, inception_date, todays_date) for i in tickers]
returns_df = [get_ret(data[i], tickers[i]) for i in range(0, len(tickers))]
tidy_returns_df = pd.concat(returns_df,axis=0)

cumul_ret = [returns_df[i].iloc[:,8] for i in range(len(tickers))]
cumul_ret = pd.concat(cumul_ret,axis=1)

net_liq_df = pd.DataFrame({'date': ['2023-10-20'] + [i[0:10] for i in files_list],
              'net_liq': net_liq})

net_liq_df['date'] = pd.to_datetime(net_liq_df['date'])
net_liq_df = net_liq_df.sort_values(by='date')

net_liq_df['port_daily_returns'] =  net_liq_df['net_liq'].pct_change()

net_liq_df['port_cumulative_returns'] = (net_liq_df['port_daily_returns'] + 1).cumprod()

net_liq_df = net_liq_df.set_index('date').join(cumul_ret)


net_liq_df.reset_index().to_csv("portfolio.csv", index=False)
tidy_returns_df.to_csv('benchmark_returns.csv', index=False)

