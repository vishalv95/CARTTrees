import pandas as pd
import numpy as np
import urllib2 as ur
import os

lookbacks = {'target': 7, 'SMA': 5, 'LMA':50, 'ACR':5, 'RSI':50}

def scraper():
    f = open('indices.txt') 
    urls = f.read().splitlines()
    for url in urls:
        file = url[url.rindex('/') + 1:url.index('.csv') + 4]
        # file = file[:file.index('?')]
        response = ur.urlopen(url)
        lines = response.read().splitlines()
        f = open('./raw_indices/' + file, 'w')
        for line in lines:
            f.write(line + '\n')
        f.close(
)
def baker():
    for file in os.listdir('./raw_indices'):
        df = pd.read_csv('./raw_indices/' + file)
        df = df.sort(columns ='Date')
        target(df, lookbacks['target'])
        VOL(df, 'VOL', 20)
        MA(df, 'SMA', lookbacks['SMA'])
        MA(df, 'LMA',lookbacks['LMA'])
        ACR(df, 'ACR', lookbacks['ACR'])
        STR(df, 'STR')
        RSI(df, 'RSI', lookbacks['RSI'])
        df = df.drop(df.index[range(max(lookbacks.values()))])
        df.to_csv('./fixed_indices/' + file)

def VOL(df, var, lookback):
    low = np.array(df['Low'])
    high = np.array(df['High'])
    tr = high - low
    atr = []
    ma = []
    conditions = []
    for i in range(len(low)):
        if i >= lookback + 7:
            atr.append(np.mean(tr[i-lookback:i+1]))
            ma.append(np.mean(atr[i-7:i+1]))
            conditions.append(1 if atr[i] > ma[i] else -1)
        elif i >= lookback:
            atr.append(np.mean(tr[i-lookback:i+1]))
            ma.append('NA')
            conditions.append('NA')
        else:
            atr.append('NA')
            ma.append('NA')
            conditions.append('NA')
    df['tr'] = tr
    df['atr'] = atr
    df['ma'] = ma
    df['var' + var] = conditions

def MA(df, var, lookback):
    ma = []
    conditions = []
    close = np.array(df['Close'])
    for i in range(len(close)):
        if i >= lookback:
            ma.append(np.mean(close[i-lookback: i+1]))
            conditions.append(1 if close[i] > ma[i] else -1)
        else:
            ma.append('NA')
            conditions.append('NA')
    if var == 'SMA':
        df['s_moving_average'] = ma
    else:
        df['l_moving_average'] = ma
    df['var' + var] = conditions

def ACR(df, var, lookback):
    cor = []
    close = np.array(df['Close'])
    conditions = []
    for i in range(len(close)):
        if i >= lookback * 2 -1:
            cor.append(np.corrcoef(close[i - 2*lookback+1: i -lookback+1],
             close[i-lookback+1: i+1])[0,1])
            conditions.append(1 if cor[i] > .5 else -1)
        else:
            cor.append('NA')
            conditions.append('NA')

    df['autocorrelation'] = cor
    df['var' + var] = conditions

def STR(df, var):
    crtdr = []
    # df = df[pd.notnull(df['Close']) 
    # and pd.notnull(df['Low']) 
    # and pd.notnull(df['High'])]
    low = np.array(df['Low'])
    high = np.array(df['High'])
    close = np.array(df['Close'])
    df['CRTDR'] = (close - low) / (high- low)
    strcon = []
    for i in range(len(df['CRTDR'])):
        strcon.append(1 if df['CRTDR'][i] > .5 else -1)
    df['var' + var] = strcon

def RSI(df, var, lookback):
    delta = []
    rsi = []
    #df = df[pd.notnull(df['Open']) and pd.notnull(df['Close'])]
    close = np.array(df['Close'])
    open = np.array(df['Open'])
    delta = close - open
    var_binary = []
    var_tertiary = []
    for i in range(len(df['Close'])):
        if i >= lookback:
            b = delta[i-lookback: i+1]
            rsi.append(100 - 100 / (1 + 
                (np.mean(b[b>0]) / np.mean(b[b<=0]*-1)) ) )
        else:
            rsi.append('NA')

        if rsi[i] > 50:
            var_binary.append(1)
        elif rsi[i] < 50:
            var_binary.append(-1)
        else:
            var_binary.append(0)

        if rsi[i] > 60:
            var_tertiary.append(1)
        elif rsi[i] >= 40:
            var_tertiary.append(0)
        else:
            var_tertiary.append(-1)
    df['delta']  = delta
    df['rsi'] = rsi
    df['var' + var + 'binary'] = var_binary
    df['var' + var + 'tertiary'] = var_tertiary

def target(df, lookback):
    #df = df[pd.notnull(df['Open']) and pd.notnull(df['Close'])]
    target = []
    close = np.array(df['Close'])
    open = np.array(df['Open'])
    for i in range(len(df['Close'])):
        if i >= lookback:
            target.append(1 if close[i] > open[i - lookback] else -1)
        else:
            target.append('NA')
    df['target'] = target

scraper()
baker()