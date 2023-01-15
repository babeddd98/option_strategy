from utils import forward_price, get_last_stock_price, load_hedging_data, export_hedging_data
from asset_classes import Option_FX, OptionType
from strategy import Strangle, PositionType, Position
import pandas as pd

S = get_last_stock_price("EURUSD")[1] # spot
# S = 1.07
K = forward_price(1, 0.0476, 0.0225, 90) # ATMF
T = 0.25 # 3 month
rd = 0.0476 # fwd rate 3 months EUR
rf = 0.0225 # fwd rate 3 months USD
sigma = 0.1 # volatility

call = Option_FX(S, K, T, rd, rf, sigma, OptionType.CALL, "EURUSD")
put = Option_FX(S, K, T, rd, rf, sigma, OptionType.PUT, "EURUSD")

pos = Strangle(call, put, 10e5, PositionType.SHORT)
# hedging_historical_data = load_hedging_data()
# pos.set_hedging_data(hedging_historical_data)

# pos.plot_profit()
# print(pos.info())
col = ["Time", "Spot price", "DELTA leg1", "DELTA leg2", "DELTA strangle", "DELTA hedge", "DELTA global"]
data = pd.DataFrame([[1200,0,0,0,0,0,0]], columns=col)
export_hedging_data(data)
pos.update_recap()
# pos.delta_hedging()
print(pos.get_recap())
# print(pos.get_recap())


