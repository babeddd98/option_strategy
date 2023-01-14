from scipy.stats import norm
from enum import Enum
import numpy as np

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class OptionState(Enum):
    ATM = "ATM"
    ITM = "ITM"
    OTM = "OTM"

class Option:

    def __init__(self, 
                 S: float,
                 K: float, 
                 T: float,
                 r: float,
                 sigma: float,
                 option_type: OptionType):
        
        self._S = S # spot
        self._K = K # strike
        self._T = T # time to maturity
        self._r = r # free risk rate
        self._sigma = sigma # volatility
        self._option_type = option_type # CALL or PUT

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

    def get_maturity(self):
        return self._T

    def get_strike(self):
        return self._K

    def get_option_type(self):
        return self._option_type

    def update_spot(self, S):
        self._S = S
        return

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
                 option_type: str    # 'call' or 'put'
                 ):
        super().__init__(S, K, T, rd, sigma, option_type)
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

