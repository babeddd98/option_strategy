from utils import forward_price, load_hedging_data, export_hedging_data
from asset_classes import Option_FX, OptionType
from strategy import Strangle, PositionType, Position

S = 1.0700 # spot
K = forward_price(1.07, 0.0476, 0.0225, 90) # ATMF
T = 0.25 # 3 month
rd = 0.0476 # fwd rate 3 months EUR
rf = 0.0225 # fwd rate 3 months USD
sigma = 0.1 # volatility

call = Option_FX(S, K, T, rd, rf, sigma, OptionType.CALL, "EURUSD")
put = Option_FX(S, K, T, rd, rf, sigma, OptionType.PUT, "EURUSD")

pos = Strangle(call, put, 10e5, PositionType.SHORT)
hedging_historical_data = load_hedging_data()
pos.set_hedging_data(hedging_historical_data)

# pos.plot_profit()
print(pos.info())
pos.delta_hedging()
recap = pos.get_recap()
print(recap)
export_hedging_data(recap)


