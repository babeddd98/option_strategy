import pandas as pd
from openpyxl import load_workbook

def forward_price(spot1, fwd_rate1, fwd_rate2, fwd_days) -> float:
    # return the forward price of a currency pair from spot price and forward rates
    swap_points = (spot1 * fwd_days / 365) * (fwd_rate1 - fwd_rate2)
    return spot1 + swap_points

# def load_hedging_data():
#     path = r"option_book_greeks_data.xlsx" 
#     df = pd.read_excel(path, engine="openpyxl")
#     row = [i for i in df]
#     return row

def export_hedging_data(df1: pd.DataFrame) -> None:

    path = r"option_book_greeks_data.xlsx"
        
    df2 = pd.read_excel(path, engine="openpyxl")
    df2 = pd.concat([df2, df1])
    df2 = df2.reset_index(drop=True)
    df2.to_excel(path, sheet_name='Sheet1', index_label=False)
