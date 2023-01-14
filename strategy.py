from option_classes import Option, OptionType
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"

class Position:

    def __init__(self, position_type: PositionType, asset: Option, quantity: int):
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
        x = np.linspace(0, 2*self.__asset.get_strike(), 200)
        y = [self.get_payoff(i) for i in x]
        plt.plot(x, y, label="Position payoff")
        plt.xlabel("Underlying price")
        plt.ylabel("Payoff")
        plt.title(self.__get_plot_title())
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

    def update_spot(self, S) -> None:
        self.__leg1.get_asset().update_spot(S)
        self.__leg2.get_asset().update_spot(S)
        
    def delta(self):
        if self.__leg1.delta() + self.__leg2.delta() < 0.01:
            return 0
        else:
            return round(self.__leg1.delta() + self.__leg2.delta(), 2)
        
    def gamma(self):
        return round(self.__leg1.gamma() + self.__leg2.gamma(),2)