from enum import Enum
from abc import ABC, abstractmethod
from scipy.stats import norm
import numpy as np

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class OptionState(Enum):
    ATM = "ATM"
    ITM = "ITM"
    OTM = "OTM"

class Asset(ABC):
    
    @abstractmethod
    def get_payoff(self):
        pass

class Spot(Asset):
    
    def __init__(self, ticker, spot_price):
        self._ticker = ticker
        self._spot_price = spot_price
        
    def get_ticker(self):
        return self.__ticker
    
    def get_payoff(self, St):
        return St - self.__spot_price
    
    def delta(self):
        return 1
    
class Currency(Spot):
    
    def __init__(self, ticker, spot_price):
        super().__init__(ticker, spot_price)
        
class Equity(Spot):
    
    def __init__(self, ticker, spot_price):
        super().__init__(ticker, spot_price)
        
class Option(Asset):

    def __init__(self, 
                 S: float,
                 K: float, 
                 T: float,
                 r: float,
                 sigma: float,
                 option_type: OptionType,
                 underlying_ticker: str):
        
        self._S = S # spot
        self._K = K # strike
        self._T = T # time to maturity
        self._r = r # free risk rate
        self._sigma = sigma # volatility
        self._option_type = option_type # CALL or PUT
        self._underlying_ticker = underlying_ticker # ticker of the underlying

    def ATM_ITM_OTM(self, spot):
        if spot == self._K:
            return OptionState.ATM
        elif self._option_type == OptionType.CALL and spot > self._K:
            return OptionState.ITM
        elif self._option_type == OptionType.CALL and spot < self._K:
            return OptionState.OTM
        elif self._option_type == OptionType.PUT and spot > self._K:
            return OptionState.OTM
        elif self._option_type == OptionType.PUT and spot < self._K:
            return OptionState.ITM
        else:
            raise ValueError("Spot error ...")

    def get_spot(self):
        return self._S
    
    def get_maturity(self):
        return self._T

    def get_strike(self):
        return self._K

    def get_option_type(self):
        return self._option_type
    
    def get_underlying_ticker(self):
        return self._underlying_ticker

    def update_spot(self, S) -> None:
        self._S = S

    def _d1(self):
        return (1/self._sigma*np.sqrt(self._T))*(np.log(self._S/self._K) + (self._r + self._sigma**2/2)*self._T)

    def _d2(self):
        return self._d1() - self._sigma*np.sqrt(self._T)

    def get_bs_pricing(self) -> float:
        d1 = self._d1()
        d2 = self._d2()

        if self._option_type == OptionType.CALL:
            return self._S*norm.cdf(d1) - self._K*np.exp(-self._r*self._T)*norm.cdf(d2)

        elif self._option_type == OptionType.PUT:
            return - self._S*norm.cdf(-d1) + self._K*np.exp(-self._r*self._T)*norm.cdf(-d2)
        
        else:
            raise ValueError("Option type can only be 'call' or 'put'" )

    def get_payoff(self, St):
        # return the option's payoff depending on spot price and option type
        if self._option_type == OptionType.CALL:
            if St > self._K:
                return St - self._K
            else:
                return 0
        else:
            if St >= self._K:
                return 0
            else:
                return self._K - St
            
    def info(self) -> str:
        return f"{self._option_type.name} maturity {int(self._T*12)} months, strike {round(self._K, 4)}"

    # greeks return functions
    def delta(self) -> float:
        if self._option_type == OptionType.CALL:
            return norm.cdf(self._d1())
        else:
            return norm.cdf(- self._d1())
        
    def gamma(self) -> float:
        if self._option_type == OptionType.CALL:
            return norm.cdf(self._d1())/self._S*self._sigma*np.sqrt(self._T)
        else:
            return self._K*np.exp(- self._r*self._T)*norm.cdf(self._d2())/(self._S)**2*self._sigma*np.sqrt(self._T)

class Option_FX(Option):

    def __init__(self, 
                 S: float,           # Spot exchange rate
                 K: float,           # Strike exchange rate
                 T: float,           # Time to maturity
                 rd: float,          # domestic interest rate
                 rf: float,          # foreign interest rate
                 sigma: float,       # exchange rate volatility
                 option_type: str,    # 'call' or 'put'
                 underlying_ticker: str
                 ):
        super().__init__(S, K, T, rd, sigma, option_type, underlying_ticker)
        self._rd = rd
        self._rf = rf
    
    def _d1(self):
        return (1/self._sigma*np.sqrt(self._T))*(np.log(self._S/self._K) + (self._rd - self._rf + self._sigma**2/2)*self._T)

    def _d2(self):
        return self._d1() - self._sigma*np.sqrt(self._T)

    def get_bs_pricing(self) -> float:
        d1 = self._d1()
        d2 = self._d2()

        if self._option_type == OptionType.CALL:
            return self._S*np.exp(-self._rf*self._T)*norm.cdf(d1) - self._K*np.exp(-self._rd*self._T)*norm.cdf(d2)

        elif self._option_type == OptionType.PUT:
            return - self._S*np.exp(-self._rf*self._T)*norm.cdf(-d1) + self._K*np.exp(-self._rd*self._T)*norm.cdf(-d2)
        
        else:
            raise ValueError("Option type can only be 'call' or 'put'" )

    # greeks return functions
    def delta(self) -> float:
        if self._option_type == OptionType.CALL:
            return np.exp(-self._rf*self._T)*norm.cdf(self._d1())
        else:
            return - np.exp(-self._rf*self._T)*norm.cdf(-self._d1())
        
    def gamma(self) -> float:
        return np.exp(-self._rf*self._T)*norm.cdf(self._d1())/self._S*self._sigma*np.sqrt(self._T)

