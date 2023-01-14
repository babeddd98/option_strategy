import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
from asset_classes import (
    Asset, 
    Currency,
    Equity,
    Option, 
    Option_FX, 
    OptionType
    )
from enum import Enum
from datetime import datetime, date

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"

class Position:

    def __init__(self, position_type: PositionType, asset: Asset, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.__position_type = position_type
        self.__asset = asset
        self.__quantity = quantity

    def get_asset(self):
        return self.__asset

    def get_position_type(self):
        return self.__position_type

    def get_position_size(self):
        return self.__quantity

    def get_payoff(self, St):
        if self.__position_type == PositionType.LONG:
            return self.__asset.get_payoff(St)
        else:
            return -self.__asset.get_payoff(St)
        
    def get_profit(self, St):
        if self.__position_type == PositionType.LONG:
            return self.get_payoff(St) - self.__asset.get_bs_pricing()
        else:
            return self.get_payoff(St) + self.__asset.get_bs_pricing()
    
    def __get_plot_title(self):
        if self.__position_type == PositionType.LONG:
            pos_type = "Long"
        else:
            pos_type = "Short"
        if self.__asset.get_option_type() == OptionType.CALL:
            op_type = "Call"
        else:
            op_type = "Put"
        return f"Payoff of a {pos_type} {op_type}"

    def plot_payoff(self):
        x = np.linspace(0, 2*self.__asset.get_strike(), 300)
        y1 = [self.get_payoff(i) for i in x]
        y2 = [self.get_profit(i) for i in x]
        plt.plot(x, y1, label="Payoff")
        plt.plot(x, y2, "r--", label="Profit")
        plt.xlabel("Underlying price")
        plt.ylabel("Payoff")
        plt.title(self.__get_plot_title())
        plt.grid()
        plt.legend()
        plt.show()

    def delta(self):
        if self.__position_type == PositionType.LONG:
            return self.__asset.delta()
        else: 
            return -self.__asset.delta()

    def gamma(self):
        if self.__position_type == PositionType.LONG:
            return self.__asset.gamma()
        else:
            return -self.__asset.gamma()



class Strangle:

    def __init__(self, option1: Option, option2: Option, size: int, pos_type: PositionType):
        if option1.get_maturity() != option2.get_maturity():
            raise AttributeError("Both options must have the same time to maturity")
        elif option1.get_strike() < option2.get_strike():
            raise AttributeError("Call's strike must be greater than put's one")
        elif option1.get_option_type() != OptionType.CALL or option2.get_option_type() != OptionType.PUT:
            raise AttributeError("The first option must be a CALL and the second one must be a PUT")
        else:
            self.__leg1 = Position(pos_type, option1, size)
            self.__leg2 = Position(pos_type, option2, size)
            self.__hedging = []
            self.__hedging_recap = []
    
    def get_leg1(self):
        return self.__leg1
    
    def get_leg2(self):
        return self.__leg2
    
    def update_spot(self, S) -> None:
        self.__leg1.get_asset().update_spot(S)
        self.__leg2.get_asset().update_spot(S)
        
    def get_delta_hedge(self):
        delta = 0
        for positions in self.__hedging:
            delta += positions.get_position_size()
        return delta
        
    def delta(self):
        if abs(self.__leg1.delta() + self.__leg2.delta() + self.get_delta_hedge()) < 0.01:
            return 0
        else:
            return round(self.__leg1.delta() + self.__leg2.delta() + self.get_delta_hedge(), 2)
        
    def gamma(self):
        return round(self.__leg1.gamma() + self.__leg2.gamma(),2)
        
    def __get_plot_title(self):
        if self.__leg1.get_position_type() == PositionType.LONG:
            pos_type = "Long"
        else:
            pos_type = "Short"
        return f"Profit of a {pos_type} Strangle"
    
    def plot_profit(self):
        if self.__leg1.get_asset().get_strike() - self.__leg2.get_asset().get_strike() == 0:
            end = 2*self.__leg1.get_asset().get_strike()
        else:
            xwindow = self.__leg2.get_asset().get_strike()
            end = self.__leg1.get_asset().get_strike() + xwindow
        x = np.linspace(0, end, 300)
        y = [self.__leg1.get_profit(i) + self.__leg2.get_profit(i) for i in x]
        plt.plot(x, y)
        plt.xlabel("Underlying price")
        plt.ylabel("Profit")
        plt.title(self.__get_plot_title())
        plt.grid()
        plt.show()
        
    def info(self) -> str:
        if self.__leg1.get_position_type() == PositionType.LONG:
            pos_type = "LONG"
        else:
            pos_type = "SHORT"
        size = int(self.get_leg1().get_position_size())
        headline = f"\n ======================= {pos_type} STRANGLE OF {size} OPTIONS PER LEG ======================= \n|\n"
        first_leg = f"| First leg :  {pos_type} on {size} {self.__leg1.get_asset().info()}\n"
        second_leg = f"| Second leg : {pos_type} on {size} {self.__leg2.get_asset().info()}\n|\n"
        greeks = f"| -------------------------------- GREEKS OF THE POSITION -------------------------------- \n| DELTA: {self.delta()}     |     GAMMA: {self.gamma()}\n|\n"
        bottom = " ========================================================================================="
        return headline + first_leg + second_leg + greeks + bottom

    def update_recap(self) -> None:
        now = datetime.now()
        spot_price = self.__leg1.get_asset().get_spot()
        delta_leg1 = self.__leg1.delta()
        delta_leg2 = self.__leg2.delta()
        delta_strangle = self.delta()
        delta_hedge = self.get_delta_hedge()
        delta_global = delta_strangle + delta_hedge
        recap = [now, round(spot_price, 4), delta_leg1, delta_leg2, delta_strangle, delta_hedge, delta_global]
        self.__hedging_recap.append(recap)
        
    def print_recap(self) -> None:
        recap_data = self.__hedging_recap
        col = ["Time", "Spot price", "DELTA leg1", "DELTA leg2", "DELTA strangle", "DELTA hedge", "DELTA global"]
        df = pd.DataFrame(recap_data, columns=col)
        print("\n =========================== RECAP OF THE DELTA HEDGING STRATEGY ===========================")
        print(df)
        
    def delta_hedging(self):
        self.update_recap()
        fx = isinstance(self.get_leg1().get_asset(), Option_FX)
        if fx:
            ticker = f"{self.get_leg1().get_asset().get_underlying_ticker()}=X"
        else:
            ticker = f"{self.get_leg1().get_asset().get_underlying_ticker()}"
       
        today = date.today()
        forex_data = yf.download(ticker, start=today, end=today)
        spot_price = float(forex_data["Close"])
        self.update_spot(spot_price)
        
        # update greeks to keep neutral delta and positive gamma
        delta_strangle = self.delta()
        if fx:
            asset = Currency(ticker, spot_price)
        else:
            asset = Equity(ticker, spot_price)
            
        if delta_strangle > 0:
            hedging_position = Position(PositionType.SHORT, asset, abs(delta_strangle))
        elif delta_strangle < 0:
            hedging_position = Position(PositionType.LONG, asset, abs(delta_strangle))
        else:
            return
    
        self.__hedging.append(hedging_position)
        self.update_recap()
        
        
            
    
        
        
