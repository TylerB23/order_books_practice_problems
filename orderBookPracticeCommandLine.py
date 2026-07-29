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

def game(numRounds=1, roundTimer=60):
    result = [0,0]
    for i in range(numRounds):
        market, cheapOrExpensive = generateSpreadMarket()
        pprint(market, width=30)
        try: 
            response = inputimeout(prompt="Type 0 if AB is too cheap, "
                                          "1 if too expensive, "
                                          "or 2 if priced correctly:\t",
                                   timeout=roundTimer)
            if int(response) == cheapOrExpensive:
                print("Correct!\n")
                result[0] += 1
            else:
                print("Incorrect :(")
                if cheapOrExpensive == 1: # Expensive
                    abBid = market["Spread AB Market"][0]
                    bBid = market["B Market"][0]
                    aAsk = market["A Market"][1]
                    print(f"Sell AB for {abBid}, buy A for {aAsk}, and sell B "
                          f"for {bBid} for an arb worth {abBid + bBid - aAsk}\n")
                elif cheapOrExpensive == 0: # Cheap
                    abAsk = market["Spread AB Market"][1]
                    aBid = market["A Market"][0]
                    bAsk = market["B Market"][1]
                    print(f"Buy AB for {abAsk}, sell A for {aBid}, and buy B "
                          f"for {bAsk} for an arb worth {aBid - abAsk - bAsk}\n")
                else: # priced correctly
                    longSynthAB =  (str(market["A Market"][1]) + 
                                    " - " +
                                    str(market["B Market"][0])
                                    )
                    shortSynthAB = (str(market["A Market"][0]) +
                                    " - " +
                                    str(market["B Market"][1])
                                    )
                    print("AB is priced correctly. The market in synthetic AB is "
                          f"({shortSynthAB}, {longSynthAB}).")
                result[1] += 1
        except Exception:
            print("Too Slow!")
            result[1] += 1
        sleep(1)

    print(f"Finished! You got {result[0]} correct and {result[1]} incorrect.")
    return None

