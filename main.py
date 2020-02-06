
# structure of trades used by this script
class Trade:
    def __init__(self, time, qty, price):
        self.time = int(time)
        self.qty = float(qty)
        self.price = float(price)


class Candle:
    def __init__(self, close_time, trades_in_candle):
        self.close_time = close_time
        price_arr = [trade.price for trade in trades_in_candle]
        qty_arr = [trade.qty for trade in trades_in_candle]
        shares = np.sum(qty_arr)
        volume = np.sum([trade * qty_arr[idx] for idx, trade in enumerate(price_arr)])
        weighted_avg = volume / shares
        self.volume = volume
        self.weighted_avg = weighted_avg


def next_candle(candle_open_timestamp, candle_close_timestamp, ms_in_candle):
    candle_open_timestamp += ms_in_candle
    candle_close_timestamp += ms_in_candle
    return candle_open_timestamp, candle_close_timestamp


def timestamp_in_candle_bounds(trade_timestamp, candle_open_timestamp, candle_close_timestamp):
    if trade_timestamp >= candle_open_timestamp and trade_timestamp < candle_close_timestamp:
        return True
    return False

#assumes all time given in ms timestamp format
def make_candles(trades, ms_in_candle):
    candle_open = trades[0].time
    candle_open -= candle_open % ms_in_candle
    candle_close = candle_open + ms_in_candle
    candles, trades_in_candle = [], []
    
    trades.sort(key=lambda x: x.time)
    
    # this method automatically ignores earliest candle as incomplete and does not make a candle until it's seen a trade outside of the candle's range.
    # Gaurenteeing intregrity of all candles.


    for idx, trade in enumerate(trades):
        if timestamp_in_candle_bounds(trade.time, candle_open, candle_close):
            # add for current trades_in_candle
            trades_in_candle.append(Trade(trade.time, trade.qty, trade.price, trade.id))
        else:
            # create candle and add
            candles.append(Candle(candle_close, trades_in_candle))

            # move to next trades_in_candle
            candle_open, candle_close = next_candle(candle_open, candle_close, ms_in_candle)

            # if trade doesn't fit in next consecutive candle (too far in futue), add a dummy candle and then open a new candle
            while not timestamp_in_candle_bounds(trade.time, candle_open, candle_close):
                # add dummy candle
                dummy_candle = copy.deepcopy(candles[-1])
                dummy_candle.close_time = candle_close
                dummy_candle.volume = 0
                candles.append(dummy_candle)

                # move to next trades_in_candle
                candle_open, candle_close = next_candle(candle_open, candle_close, ms_in_candle)

            # create new trades_in_candle with curr trade
            trades_in_candle = [Trade(trade.time, trade.qty, trade.price, trade.id)]
    return candles
