from bs4 import BeautifulSoup
import requests
import pandas as pd
from secrets import Data_Key
from scipy import stats
from statistics import mean
import math


# Functions used to determine maximum risk, and portfolio size
def risk_cutoff():
    try:
        risk = float(input('Enter maximum Beta: '))
        for index in range(0, len(df)):
            if df['Beta'][index] >= risk:
                df.drop([index], inplace=True)
    except ValueError:
        print('Enter numbers only, please try again')
        risk_cutoff()


def shares_tobuy():
    try:
        portfolio = float(input('Enter Portfolio Size: '))/len(df)
        for index in range(0, len(df)):
            df['Shares to buy'][index] = math.floor(portfolio/df['Price'][index])
    except ValueError:
        print('Enter numbers only, please try again')
        shares_tobuy()


# Fetching current S&P 500 Stocks
html_txt = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies').text
soup = BeautifulSoup(html_txt, 'lxml')
table = soup.find_all("tbody")
cells = table[0].find_all("a", class_="external text")
ticker_list = [v.text for i, v in enumerate(cells) if i % 2 == 0]


# Labels name for Dataframes
df = pd.DataFrame()
cols = ['Ticker',
        'Price',
        'Year Percent Change',
        '6-month Percent Change',
        '3-month Percent Change',
        '1-month Percent Change',
        'Year Percent Change Ranking',
        '6-month Percent Change Ranking',
        '3-month Percent Change Ranking',
        '1-month Percent Change Ranking',
        'Average Ranking',
        'Shares to buy',
        'Beta']

# Fetching values from API (API had maximum batch calls limit of 100)
for index in range(0, len(ticker_list), 100):
    symbol_batch = ",".join(ticker_list[index:index + 100])
    data_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_batch}&token={Data_Key}'
    data = requests.get(data_url).json()
    ticker = index
    while (ticker != len(ticker_list)) and (ticker >= index) and (ticker <= index+99):
        df = df.append(pd.Series(
            [ticker_list[ticker],
             data[ticker_list[ticker]]['quote']['latestPrice'],
             data[ticker_list[ticker]]['stats']['year1ChangePercent'],
             data[ticker_list[ticker]]['stats']['month6ChangePercent'],
             data[ticker_list[ticker]]['stats']['month3ChangePercent'],
             data[ticker_list[ticker]]['stats']['month1ChangePercent'],
             'N/A',
             'N/A',
             'N/A',
             'N/A',
             'N/A',
             'N/A',
             data[ticker_list[ticker]]['stats']['beta']
             ], index=cols
        ), ignore_index=True)
        ticker += 1

# Calculating ranking of stock per growth period
periods = ["Year Percent Change",
           "6-month Percent Change",
           "3-month Percent Change",
           "1-month Percent Change"]

for index in range(0, len(ticker_list)):
    for period in periods:
        df[f'{period} Ranking'][index] = stats.percentileofscore(df[f'{period}'], df[f'{period}'][index])

# Calling risk cutoff function
risk_cutoff()

# Calculating mean ranking per stock
df['Average Ranking'] = [mean(df[cols[6:9]].iloc[index]) for index in range(0, len(df))]
df = df.sort_values(by='Average Ranking', ascending=False)
df = df[:50].reset_index()

# Calling function to calculate shares to buy
shares_tobuy()
