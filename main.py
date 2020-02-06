import copy
import numpy as np

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


class TradesContainer:
    def __init__(self, first_trade_ts, ms_in_candle):
        self.candle_open = first_trade_ts + (first_trade_ts % ms_in_candle)
        self.candle_close = self.candle_open + ms_in_candle
        self.ms_in_candle = ms_in_candle
        self.candles = []

    def move_to_next_candle(self):
        self.candle_open += self.ms_in_candle
        self.candle_close += self.ms_in_candle

    def add_candle(self, trades_in_candle):
        self.candles.append(Candle(self.candle_close, trades_in_candle))

    def get_candles(self):
        return self.candles
    
    def add_dummy(self):
        dummy_candle = copy.deepcopy(self.candles[-1])
        dummy_candle.close_time = self.candle_close
        dummy_candle.volume = 0
        self.candles.append(dummy_candle)

    def timestamp_in_candle_bounds(self, trade):
        if self.candle_open <= trade.time < self.candle_close:
            return True
        return False


# assumes all time given in ms timestamp format
def make_candles(trades, ms_in_candle):
    trades.sort(key=lambda x: x.time)

    tc = TradesContainer(trades[0].time, ms_in_candle)
    trades_in_candle = []

    # this method automatically ignores earliest candle as incomplete and does not make a candle until it's seen a trade outside of the candle's range.
    # Gaurenteeing intregrity of all candles.

    for idx, trade in enumerate(trades):
        if tc.timestamp_in_candle_bounds(trade):
            # add for current trades_in_candle
            trades_in_candle.append(Trade(trade.time, trade.qty, trade.price, trade.id))
        else:
            # create candle and add
            tc.add_candle(trades_in_candle)

            # move to next trades_in_candle
            tc.move_to_next_candle()

            # if trade doesn't fit in next consecutive candle (too far in futue), add a dummy candle and then open a new candle
            while not tc.timestamp_in_candle_bounds(trade):
                # add dummy candle
                tc.add_dummy()

                # move to next trades_in_candle
                tc.move_to_next_candle()

            # create new trades_in_candle with curr trade
            trades_in_candle = [Trade(trade.time, trade.qty, trade.price, trade.id)]
    return tc.get_candles()
