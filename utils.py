def forward_price(spot1, fwd_rate1, fwd_rate2, fwd_days) -> float:
    # return the forward price of a currency pair from spot price and forward rates
    swap_points = (spot1 * fwd_days / 365) * (fwd_rate1 - fwd_rate2)
    return spot1 + swap_points
