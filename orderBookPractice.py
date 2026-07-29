from inputimeout import inputimeout
from time import sleep
from pprint import pprint
import numpy as np
rng = np.random.default_rng()

def generateSpreadMarket():
    # generates a market in three assets:
    # A and B, two normal futures
    # AB, the spread between A and B at expiry
    # Returns a dictionary with three tuples
    # each tuple contains the bid and ask for one of the three assets
    bids = np.sort(rng.integers(1, 21, size = 2)) # sorted so A > B
    asks = bids + rng.integers(2, 6, size = 2)
    aBidAsk = (bids[1], asks[1])
    bBidAsk = (bids[0], asks[0])

    # equals 0 if cheap, 1 if expensive, 2 if priced correctly
    cheapOrExpensive = None 

    draw = rng.integers(5)
    if draw < 2:
        # AB is too expensive
        # we should be able to buy the synth AB and sell actual AB for a profit
        # So, (bBid - aAsk) + abBid > 0
        # abBid > -(bBid - aAsk) = aAsk - bBid
        abBid = aBidAsk[1] - bBidAsk[0] + rng.integers(1,4)
        abAsk = abBid + rng.integers(2,5)
        cheapOrExpensive = 1
    elif draw < 4:
        # AB is too cheap
        # we should be able to buy AB and sell synth AB for a profit
        # so, -abAsk + (aBid - bAsk) > 0
        # abAsk < aBid - bAsk
        abAsk = aBidAsk[0] - bBidAsk[1] - rng.integers(1,4)
        abBid = abAsk - rng.integers(2,5)
        cheapOrExpensive = 0
    else:
        # AB is priced correctly
        # market maker will price the AB bid like the A bid minus the B ask
        # and they'll price the AB offer like the A ask minus the B bid
        abAsk = aBidAsk[1] - bBidAsk[0]
        abBid = aBidAsk[0] - bBidAsk[1]
        cheapOrExpensive = 2

    abBidAsk = (abBid, abAsk)
    market = {"A Market": aBidAsk,
              "B Market": bBidAsk,
              "Spread AB Market": abBidAsk}
    
    # convert to regular ints instead of np.int64 to print prettier
    market = {k: (int(v1), int(v2)) for k, (v1, v2) in market.items()}
    return market, cheapOrExpensive

