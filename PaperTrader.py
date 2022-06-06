#import robin_stocks
from datetime import datetime, time
from time import sleep
import random
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


def pprint(a):
    return (datetime.utcfromtimestamp(a[0]).strftime('%Y-%m-%d %H:%M') + ":" + str(a[1]))

def dateConv(a):
    return (datetime.utcfromtimestamp(a).strftime('%Y-%m-%d %H:%M'))

print("Loading Sim Data...")
with open ("smaller_data.txt") as f:
    lines = f.read().split("\n")
    lines = [r.split(",") for r in lines]
    lines = [[int(a[0]), float(a[1])] for a in lines]

print(len(lines), "minutes of data to read") #Each line is 1 minute of price data
#1577836800 = 2020-01-01
#1496275200 = 2017-06-01
unix_start = 1526275200
simStart = int((unix_start - 1483228800) / 60) #convert unix time to data table row 

simLife = len(lines)-simStart-1 #PICK 1 OF 2 LINES: Run until the end of the dataset, the end of 2020
#simLife = (60*24*365)-1 #60*24*(number of days to simulate)

trial = lines[simStart:simStart+simLife]
date1 = lines[simStart]
date2 = lines[simStart+simLife]

def exponentialMovingAverage(periodEMA, data):
    #--- Exponential Moving Average
    # data: array, time series data e.g. daily close prices
    # periodEMA: integer, number of periods form time series array to include in calculation
     
    #--- import libraries
    import numpy as np
     
    #--- define variables
    p = periodEMA               # period value form self
    s = sum(data[:p])/p        # the first simple moving average
    m = 2/(p+1)                 # weighting factor
 
    #--- define output array
    out = np.zeros(len(data))
 
    #--- calculate EMA
    for i in range(len(data)):
        #--- where data item is the p'th item, use the SMA
        if i == p-1:
            out[i] = s
        elif i > p-1:
            #--- the EMA calculation
            out[i] = ((data[i] - out[i-1]) * m) + out[i-1]
            #--- mathematically equivalent
            #    out[i] = m * data[i] + (1-m) * out[i-1]
        elif i < p-1:
            out[i] = np.nan
 
    return out

def wait_start(runTime):
    startTime = time(*(map(int, runTime.split(':'))))
    while startTime > datetime.today().time(): # you can add here any additional variable to break loop if necessary
        sleep(1)# you can change 1 sec interval to any other
    return

#For Crypto
openingPrice = trial[0][1]
print("Starting Time / Price:", pprint(trial[0]))
dbg = 5 #Rounding len for printing long numbers less aanoyingly

lastPrice = openingPrice
currentPrice = []
currentPrice.append(openingPrice)

#Variables for the loop

#Set some to 0
i = 0
trend = 0
profit = 0
stockNum = 0
ownStock = 0
x = 0
timeboughtin = 0
highestBuyPrice  = 0

#Setup the Wallet
seedCap = date1[1] #Start with 1 BTC worth of cash on day 1
OGwallet = seedCap
wallet = OGwallet
lastWallet = OGwallet
emaNum =300
#averageWallet = OGwallet

#Setup the pool/net feature
percentPumper =20
poolAverage = openingPrice
averagePrice = openingPrice

#   Percent change limiter to determine the limit buy price in accordance with the 
# calculated daily average
percentLimit = 0.002
limitPrice = openingPrice + (percentLimit * openingPrice)
changelimit = 0.0001


def performanceCheck():
    print("Sim Start:           ", dateConv(date1[0]))
    print("Sim End:             ", dateConv(date2[0]))
    print("Held BTC Return:     ", round((date2[1] - date1[1])/date1[1], 5)*100, "%")
    print()
    print("Start balance:       ", seedCap)
    print("Cold Balance:        ", round(wallet, 2))
    print("Hot Balance:         ", round(stockNum*date2[1], 2))
    print("Return (USD Gross):  ", wallet+(stockNum*date2[1])-seedCap)
    g = wallet+(stockNum*date2[1])
    print("Return (Rate):       ", round(((g-seedCap)/seedCap), 5)*100, "%")

hist_balan = []

#function for if  price is postive or negative to be used later
def determineNegativeOrPositiveTrend(last, current):
    if last < current:
        trend = 1
    else:
        if lastPrice > currentPrice[i]:  
            trend = -1
        else:
            trend = 0
    return trend

def makeBuyPurchase(wallet, highestBuyPrice, lastWallet, j, ownStock, timeboughtin):
    highestBuyPrice = currentPrice[-1]
    lastWallet = wallet
    wallet = wallet/2
    j = 1
    ownStock = 1
    timeboughtin = 0
    print("buy")

while i < simLife:
    #print("Tick#: ", i)
    if (i %(60*24) == 0):
        print(" - Day ", i//(60*24), "-")



    #Determine if its the first trade of the day
    if i == 0:
        lastPrice = openingPrice
    else:
        lastPrice = currentPrice[i-1]

    #Some minutes are missing price data: this if stataement catches that and smoothes over those missinig moments. 
    if trial[i][1] != trial[i][1]: 
        i += 1
        currentPrice.append(currentPrice[-1])
        averagePrice = exponentialMovingAverage(emaNum, currentPrice[-emaNum:]) #this fix is CRUCIAL for runtime: don't pass in all of currentPrice
        limitPrice = averagePrice[-1] #- (averagePrice * percentLimit)
        hist_balan.append(wallet+(stockNum*currentPrice[i]))
        continue #Skips
    currentPrice.append(trial[i][1])
    averagePrice = exponentialMovingAverage(emaNum, currentPrice[-emaNum:])
    limitPrice = averagePrice[-1] #- (averagePrice * percentLimit)
    hist_balan.append(wallet+(stockNum*currentPrice[i]))



    #Determine if the trend is postive or negative
    trend = determineNegativeOrPositiveTrend(lastPrice, currentPrice[i])
    
    #Determine whether we should buy or sell the stock
    if trend == 1:
        if ownStock == 0:
            if currentPrice[-1] < limitPrice: #---> Buy at rising point
                stockAdded = ((wallet/2)/currentPrice[-1])   #Each move goes 50% in
                poolAverage = currentPrice[-1]
                stockNum = stockNum + stockAdded
                
                #buy stockNum amount of stock
                makeBuyPurchase(wallet)
                # highestBuyPrice = currentPrice[-1]
                # lastWallet = wallet
                # wallet = wallet/2
                # j = 1
                # ownStock = 1
                # timeboughtin = 0
                # print("buy")
                #print("BUY : Bought ", round(stockAdded, dbg), "for", round(highestBuyPrice, dbg))
        else: 
            
            if highestBuyPrice < currentPrice[i]: #---> Sell for Gain
                if (averagePrice[-1] + (averagePrice[-1]*percentLimit)) < currentPrice[-1]: #Aim for .2% gain on each trade
                    wallet = wallet + (stockNum * currentPrice[i])
                    profit = wallet - OGwallet
                    newprofit = wallet - lastWallet
                    ownStock = 0
                    stockNum = 0
                    #print("GAIN: Bought for", round(highestBuyPrice, dbg), ", Sold for", round(currentPrice[i], dbg), ", New Profit = ", round(newprofit, dbg), ", Total Profit = ", round(profit, dbg), ", Wallet Amount = ", round(wallet, dbg))
    
    if trend == -1:
        if ownStock == 1:
            if highestBuyPrice < currentPrice[i]: #---> Sell on Loss
                if(timeboughtin < 60):
                    if currentPrice[i] > (highestBuyPrice + highestBuyPrice*changelimit):
                        #sell stockNum at current stock price 
                        wallet = wallet + (stockNum * currentPrice[-1])
                        profit = wallet - OGwallet
                        newprofit = wallet - lastWallet
                        ownStock = 0
                        stockNum = 0
                        poolAverage = 0
                        j=0
                    #print("LOSS: Bought at", round(highestBuyPrice, dbg), "Sold for", round(currentPrice[i], dbg), ", New Profit = ", round(newprofit, dbg), ", Total Profit = ", round(profit, dbg), ", Wallet Amount = ", round(wallet, dbg))
                else:
                    #sell stockNum at current stock price 
                    wallet = wallet + (stockNum * currentPrice[-1])
                    profit = wallet - OGwallet
                    newprofit = wallet - lastWallet
                    ownStock = 0
                    stockNum = 0
                    poolAverage = 0
                    j=0


    if ownStock == 1:
        if currentPrice[i] < highestBuyPrice:
            if currentPrice[i] < poolAverage:
                if wallet > 1.0:
                    poolAverage = (poolAverage * j + currentPrice[-1])/(j+1)
                    ratio = (percentPumper)/((currentPrice[-1]/highestBuyPrice)*100)
                    stockAdded = (wallet * ratio)/currentPrice[-1]   
                    stockNum = stockNum + stockAdded
                    wallet = wallet * (1.0 - ratio)
                    j = j + 1   
        
        timeboughtin = timeboughtin + 1
    #Quiet this down a little bit
    #print("\nCurrent Price = ", currentPrice[i], "\nLast Buy in Price = ", highestBuyPrice, "\nAverage Pool Price = ", poolAverage, "\nLast Price = ", lastPrice, "\nTotal Profit = ", profit, "\nAverage Price during session = ", averagePrice[i], "\nWallet Price = ", wallet, "\nStock Currently Owned = ", stockNum, "\nTrend = ", trend, "\n")
    

    i = i + 1

#Check the sim returns
print()
performanceCheck()

plt.title("Botting v. Holding: " + dateConv(date1[0]) + " to " + dateConv(date2[0]))
plt.plot(currentPrice, label="BTC Price")
plt.plot(hist_balan, label="Tradebot Returns")
plt.legend()
plt.show()