from utils import forward_price
from option_classes import Option_FX, OptionType
from strategy import Strangle, PositionType, Position

S = 1.07 # spot
K = forward_price(1.07, 0.0476, 0.0225, 90) # ATMF
T = 0.25 # 3 month
rd = 0.0476 # fwd rate 3 months EUR
rf = 0.0225 # fwd rate 3 months USD
sigma = 0.1 # volatility

call = Option_FX(S, K, T, rd, rf, sigma, OptionType.CALL)
put = Option_FX(S, K, T, rd, rf, sigma, OptionType.PUT)

pos = Strangle(call, put, 10e5, PositionType.LONG)
print(f"Delta strangle: {pos.delta()}")
print(f"Gamma strangle: {pos.gamma()}")

pos.update_spot(1.08)
print(f"Delta strangle: {pos.delta()}")
print(f"Gamma strangle: {pos.gamma()}")
p1 = Position(PositionType.LONG,call,1)
# p1.plot_payoff()
print(call.get_bs_pricing())

