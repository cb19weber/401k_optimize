'''Functions to analyze stock/investment data'''
import yfinance as yf

# get historical market data
def get_history(stock_symbol):
    filter = False
    if filter:
        history = stock_symbol.history(period="max")
        history = history.loc[:'2024-12-13']
        return history
    return stock_symbol.history(period="max")

def trend_analysis(stock):
    # Establish ticker information
    stock_symbol = yf.Ticker(stock)

    # Query stock data for each symbol into a dataframe
    long_trend = get_history(stock_symbol)

    # Calculate 50 and 200 day moving averages for symbol
    sma_200 = round(long_trend["Close"][-200:].sum() / 200, ndigits=3)
    sma_50 = round(long_trend["Close"][-50:].sum() / 50, ndigits=3)
    sma_20 = round(long_trend["Close"][-20:].sum() / 20, ndigits=3)
    entry_analysis = long_trend["Low"][-20:]
    exit_analysis = long_trend["Low"][-20:]
    entry_point = np.percentile(entry_analysis, 20)
    exit_point = np.percentile(exit_analysis, 80)
    signal_20d_low = long_trend["Close"].iloc[-1] <= entry_point
    signal_20d_high = long_trend["Close"].iloc[-1] >= exit_point

    # Get currnet market price
    current_price = round(long_trend["Close"].iloc[-1], ndigits=3)
    if current_price < sma_50 * 0.95:
        signal_20d_high = True

    if len(long_trend) >= 50:
        return current_price, sma_200, sma_50, sma_20, entry_point, signal_20d_low, exit_point, signal_20d_high
    
def technical_analysis(stock="NVDA", basis=0):
    # Retrieve all relevant data for investment analysis
    try:
        current_price, sma_200, sma_50, sma_20, entry_point, signal_20d_low, exit_point, signal_20d_high = trend_analysis(stock)
        # Caclulate exit and opportunity ranges
        death_cross = round(sma_50 - sma_200, ndigits=2) > 0
        exit_price = round(sma_50 * 0.95, ndigits=2)
        if exit_point > exit_price:
            exit_price = round(exit_point, ndigits=2)
        opportunity = round(sma_200 * 1.03, ndigits=2)
        if opportunity < entry_point:
            opportunity = round(entry_point, ndigits=2)
        
        desired_growth = 1.147
        exit_price = round(basis * desired_growth, ndigits=2)

        return current_price, sma_200, sma_50, sma_20, exit_point, entry_point, signal_20d_low, signal_20d_high
    except:
        return 0, 0, 0, 0, 0, 0, 0, 0
    
def build_analysis_table(fund_list, analyzed_df):
    current_prices = []
    sma_200_list = []
    sma_50_list = []
    sma_20_list = []
    exit_range = []
    entry_points = []
    buy_signals = []

    for item in fund_list:
        if "basis" in item:
            current_price, sma_200, sma_50, sma_20, exit_price, opportunity, signal_20d_low, signal_20d_high = technical_analysis(item['symbol'], item['basis'])
        else:
            current_price, sma_200, sma_50, sma_20, exit_price, opportunity, signal_20d_low, signal_20d_high = technical_analysis(item)
        current_prices.append(current_price)
        sma_200_list.append(sma_200)
        sma_50_list.append(sma_50)
        sma_20_list.append(sma_20)
        entry_points.append(round(opportunity, ndigits=2))
        exit_range.append(round(exit_price, ndigits=2))
        buy_signals.append(signal_20d_low)

        '''
        # Evaluate buy and sell opportunities
        if current_price < exit_price:
            signal_20d_high = False
        else:
            pass
        if signal_20d_high:
            exit_range.append(exit_price)
        else:
            exit_range.append(np.nan)
        '''

    # Create columns in data frame for analysis
    analyzed_df["market"] = current_prices
    analyzed_df["200d MA"] = sma_200_list
    analyzed_df["50d MA"] = sma_50_list
    analyzed_df["20d MA"] = sma_20_list
    analyzed_df["buy"] = entry_points
    analyzed_df["sell"] = exit_range

    # Filter list of opportunities
    if "basis" not in item:
        analyzed_df = analyzed_df.loc[analyzed_df["buy_signal"]==True]
    else:
        pass
    
    '''
    # Add profit taking analysis if asset is above such value
    if "basis" in item:
        analyzed_df["sell"] = exit_range
    else:
        pass

    # Remove unnecessary column
    analyzed_df.drop(["buy_signal"], axis=1, inplace=True)
    '''

    return analyzed_df

# Lookup requested stocks, ETFs, or funds
def one_asset_lookup(*args):
    dict_key = 'symbol'
    dict_value = 'basis'
    dataset = []
    for symbol in args:
        dataset.append({dict_key:symbol, dict_value: 1})
    df = pd.DataFrame(dataset)
    return build_analysis_table(dataset, df)