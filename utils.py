from ast import List
import pandas as pd
from openpyxl import load_workbook
import yfinance as yf
from datetime import date, datetime

def forward_price(spot1, fwd_rate1, fwd_rate2, fwd_days) -> float:
    # return the forward price of a currency pair from spot price and forward rates
    swap_points = (spot1 * fwd_days / 365) * (fwd_rate1 - fwd_rate2)
    return spot1 + swap_points

def load_hedging_data():
    path = r"option_book_greeks_data.xlsx" 
    df = pd.read_excel(path, engine="openpyxl")
    # df = df.drop(columns=["Unnamed: 0"])
    return df

def export_hedging_data(df1: pd.DataFrame) -> None:

    path = r"option_book_greeks_data.xlsx"
        
    df2 = pd.read_excel(path, engine="openpyxl")
    df2 = pd.concat([df2, df1])
    df2 = df2.reset_index(drop=True)
    df2.to_excel(path, sheet_name='Sheet1', index=False)
    
def get_last_stock_price(ticker: str, fx=True) -> list [datetime, float]:
    now = datetime.now()
    yesterday = datetime(now.year, now.month, now.day - 3)
    if fx:
        ticker = f"{ticker}=X"
    else:
        ticker = f"{ticker}"
    forex_data = yf.download(ticker, start=yesterday, end=now, interval="1m")
    stock_price = float(forex_data.iloc[-1:]["Close"])
    time = forex_data.iloc[-1:]["Close"].index.to_pydatetime()[0]
    return [time, stock_price]

