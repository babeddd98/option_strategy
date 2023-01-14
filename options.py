import pandas as pd
import numpy as np
from yahoo_fin import options
import matplotlib.pyplot as plt
from datetime import datetime

def get_expiration_date(ticker: str, code: str)->datetime:
    code = code.replace(f"{ticker}", "")
    year = int(code[0:2])
    month = int(code[2:4])
    day = int(code[4:6])
    return datetime(2000 + year, month, day)

ticker = "AAPL"
asset = options.get_options_chain(ticker)
calls = pd.DataFrame(asset["calls"])
puts = pd.DataFrame(asset["puts"])

calls["Implied Volatility"] = [float(str(i).replace("%","")) for i in calls["Implied Volatility"]]
calls["Expiration"] = [get_expiration_date(ticker, i) for i in calls["Contract Name"]]