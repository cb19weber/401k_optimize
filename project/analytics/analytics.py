def summarize_portfolio(df, reference_date=None):
    """
    Creates a summary DataFrame by aggregating transaction data for each company (TICKER),
    including a weighted average purchase date based on total cost (quantity * purchase price).

    The summary includes:
    - TICKER: The company ticker.
    - ASSET_CLASS: The asset class (assumed consistent per TICKER, takes the first occurrence).
    - SECTOR: The sector (assumed consistent per TICKER, takes the first occurrence).
    - WEIGHTED_AVG_PURCHASE_DATE: The cost-weighted average purchase date.
    - TOTAL_COST: The total cost of all purchases.
    - TOTAL_QUANTITY: The total quantity of shares purchased.
    - AVG_PURCHASE_PRICE: The weighted average purchase price (total cost / total quantity).

    Parameters:
    df (pd.DataFrame): The input DataFrame with columns: ID, TICKER, ASSET_CLASS, SECTOR,
                      ACQUIRED, PURCHASE_PRICE, QUANTITY.
    reference_date (str): Reference date for date-to-numeric conversion (default: '2025-01-01').

    Returns:
    pd.DataFrame: The summary DataFrame with aggregated data per TICKER, including weighted purchase date.
    """
    # Set reference_date to current date if None
    if reference_date is None:
        reference_date = datetime.now().date()

    # Ensure ACQUIRED is in datetime format
    df['ACQUIRED'] = pd.to_datetime(df['ACQUIRED'])
    
    # Calculate the cost for each transaction
    df['COST'] = df['PURCHASE_PRICE'] * df['QUANTITY']
    
    # Convert ACQUIRED date to numeric (days since reference_date)
    reference_date = pd.to_datetime(reference_date)
    df['DAYS_SINCE_REF'] = (df['ACQUIRED'] - reference_date).dt.days
    
    # Calculate weighted days (cost * days since reference)
    df['WEIGHTED_DAYS'] = df['COST'] * df['DAYS_SINCE_REF']
    
    # Group by TICKER and aggregate
    summary_df = df.groupby('TICKER').agg({
        'ASSET_CLASS': 'first',
        'ALPHA_PICKED': 'first',
        'QUANT_RATING': 'first',
        'SECTOR': 'first',
        'ACQUIRED': 'min',
        'QUANTITY': 'sum',
        'COST': 'sum',
        'WEIGHTED_DAYS': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    summary_df = summary_df.rename(columns={
        'ACQUIRED': 'FIRST_ACQUIRED',
        'QUANTITY': 'TOTAL_QUANTITY',
        'COST': 'TOTAL_COST'
    })
    
    # Calculate weighted average purchase price
    summary_df['AVG_PURCHASE_PRICE'] = round(summary_df['TOTAL_COST'] / summary_df['TOTAL_QUANTITY'], ndigits=3)
    
    # Calculate weighted average days
    summary_df['WEIGHTED_AVG_DAYS'] = summary_df['WEIGHTED_DAYS'] / summary_df['TOTAL_COST']
    
    # Convert weighted average days back to a datetime
    summary_df['WEIGHTED_AVG_PURCHASE_DATE'] = reference_date + pd.to_timedelta(summary_df['WEIGHTED_AVG_DAYS'], unit='D')
    
    # Round the weighted average date to the nearest day for clarity
    summary_df['WEIGHTED_AVG_PURCHASE_DATE'] = summary_df['WEIGHTED_AVG_PURCHASE_DATE'].dt.round('D')
    
    # Reorder columns as requested
    columns_order = [
        'TICKER', 'ALPHA_PICKED', 'QUANT_RATING', 'ASSET_CLASS', 'SECTOR', 'WEIGHTED_AVG_PURCHASE_DATE',
        'TOTAL_COST', 'TOTAL_QUANTITY', 'AVG_PURCHASE_PRICE'
    ]
    summary_df = summary_df[columns_order]
    
    # Drop temporary columns from input DataFrame
    df.drop(['COST', 'DAYS_SINCE_REF', 'WEIGHTED_DAYS'], axis=1, inplace=True)
    
    return summary_df

def get_history(symbol, api_key, days=252):  # ~1 year default
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full&entitlement=delayed"
    try:
        response = requests.get(url).json()
        if "Time Series (Daily)" not in response:
            error_msg = response.get('Note', response.get('Information', 'Unknown error'))
            print(f"Error fetching price data for {symbol}: {error_msg}")
            print(f"Response keys: {list(response.keys())}")
            return None
        
        time_series = response["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
        
        # Debug: Print available columns
        # print(f"Columns for {symbol}: {list(df.columns)}")
        
        # Rename columns dynamically
        column_map = {
            col: name for col, name in [
                ("1. open", "Open"), ("2. high", "High"), ("3. low", "Low"),
                ("4. close", "Close"), ("5. volume", "Volume"), ("6. volume", "Volume"),
                ("7. adjusted close", "Adjusted Close"), ("8. dividend amount", "Dividend")
            ] if col in df.columns
        }
        if "5. volume" not in df.columns and "6. volume" not in df.columns:
            print(f"No volume data for {symbol}")
            return None
        
        df = df.rename(columns=column_map)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index().tail(days)
        return df
    except Exception as e:
        print(f"Exception fetching price data for {symbol}: {str(e)}")
        return None

def get_fundamentals(symbol, api_key, current_price):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}&entitlement=delayed"
    try:
        response = requests.get(url).json()
        if not response or "Symbol" not in response:
            error_msg = response.get('Note', response.get('Information', 'No data'))
            print(f"Error fetching fundamentals for {symbol}: {error_msg}")
            print(f"Full response: {response}")
            return None
        
        def safe_float(value, default):
            if value in [None, 'None', '']:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        pe_ratio = safe_float(response.get('PERatio'), float('inf'))
        pb_ratio = safe_float(response.get('PriceToBookRatio'), float('inf'))
        
        # Calculate EPS and Book Value
        eps = current_price / pe_ratio if pe_ratio != float('inf') and pe_ratio != 0 else 0
        book_value = current_price / pb_ratio if pb_ratio != float('inf') and pb_ratio != 0 else 0
        
        fundamentals = {
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            'dividend_yield': safe_float(response.get('DividendYield'), 0),
            'debt_to_equity': safe_float(response.get('DebtToEquityRatio'), float('inf')),
            'eps': eps,
            'book_value': book_value
        }
        
        return fundamentals
    except Exception as e:
        print(f"Exception fetching fundamentals for {symbol}: {str(e)}")
        return None

def calculate_vwap(df, days=126):  # ~2 quarters
    if 'Volume' not in df.columns:
        print("Missing Volume column in DataFrame")
        return None
    
    vwap_analysis = df[-days:].copy()
    vwap_analysis['Cumulative_LTPV'] = (vwap_analysis['Low'] * vwap_analysis['Volume']).cumsum()
    vwap_analysis['Cumulative_HTPV'] = (vwap_analysis['High'] * vwap_analysis['Volume']).cumsum()
    vwap_analysis['Cumulative_Volume'] = vwap_analysis['Volume'].cumsum()
    vwap_analysis['Entry'] = round(vwap_analysis['Cumulative_LTPV'] / vwap_analysis['Cumulative_Volume'], 2)
    vwap_analysis['Exit'] = round(vwap_analysis['Cumulative_HTPV'] / vwap_analysis['Cumulative_Volume'], 2)
    return vwap_analysis[-1:].copy()

def build_analysis_table(summary_df, api_key, margin_of_safety=0.9, vwap_days=126, graham_margin=0.95):
    """
    Builds a portfolio analysis table using financial data from Alpha Vantage API,
    with ticker symbols extracted from the provided summary DataFrame.

    Parameters:
    summary_df (pd.DataFrame): Summary DataFrame with at least a 'TICKER' column.
    api_key (str): Alpha Vantage API key for fetching financial data.
    margin_of_safety (float): Margin of safety for VWAP buy threshold (default: 0.9).
    vwap_days (int): Number of days for VWAP calculation (default: 126).
    graham_margin (float): Margin for Graham buy threshold (default: 0.95).

    Returns:
    list: List of lists containing analysis data for each ticker:
          [symbol, market_price, buy_threshold, graham_buy_threshold, exit_price,
           pe_ratio, pb_ratio, dividend_yield, decision]
    """
    # Extract unique tickers from summary_df
    ticker_symbols = [{'symbol': ticker, 'is_etf': False} for ticker in summary_df['TICKER'].unique()]
    
    portfolio = []
    etf_list = ['FBTC', 'ITA', 'SCHF', 'SCHE','SCHX', 'AOA', 'AOK', 'AOM',
                'AOR', 'BLV', 'SCHA', 'SCHD', 'SCHH', 'SCHM', 'SCHP', 'SCHR',
                'SCHZ']
    
    for ticker in ticker_symbols:
        symbol = ticker['symbol']
        is_etf = symbol in etf_list
        
        # Get price data
        raw_data = get_history(symbol, api_key)
        if raw_data is None:
            portfolio.append([symbol, None, None, None, None, None, None, None, "Error"])
            continue
        
        # Get fundamentals (skip for ETFs)
        current_price = raw_data['Close'].iloc[-1]  # Use Close for fundamental calcs
        fundamentals = None if is_etf else get_fundamentals(symbol, api_key, current_price)
        if not is_etf and fundamentals is None:
            portfolio.append([symbol, None, None, None, None, None, None, None, "Error"])
            continue
        
        # Calculate VWAP
        vwap_data = calculate_vwap(raw_data, days=vwap_days)
        if vwap_data is None:
            portfolio.append([symbol, None, None, None, None, None, None, None, "Error"])
            continue
        
        # Extract data
        market_price = round(raw_data['Close'].iloc[-1], 2)  # Use Close for buys
        entry_price = round(vwap_data['Entry'].iloc[0], 2)
        exit_price = round(vwap_data['Exit'].iloc[0], 2)
        buy_threshold = round(entry_price * margin_of_safety, 2)  # 10% margin

        # Graham buy threshold (for stocks only)
        graham_buy_threshold = None
        if not is_etf:
            if fundamentals['eps'] > 0 and fundamentals['book_value'] > 0:
                # Calculate desired price where P/E × P/B = 38
                desired_price = math.sqrt(38 * fundamentals['eps'] * fundamentals['book_value'])
                graham_buy_threshold = round(desired_price * graham_margin, 2)  # 5% margin
            else:
                graham_buy_threshold = buy_threshold  # Default to VWAP threshold
        
        # Volume filter: 20% of 21-day average
        avg_volume = raw_data['Volume'][-21:].mean()
        today_volume = raw_data['Volume'].iloc[-1]
        volume_ok = today_volume >= avg_volume * 0.2
        
        # Graham's fundamental checks (for stocks only)
        graham_ok = True
        if not is_etf:
            graham_ok = (
                (fundamentals['pe_ratio'] < 19 and fundamentals['pb_ratio'] < 2.0) or
                (fundamentals['pe_ratio'] * fundamentals['pb_ratio'] < 38 and 
                 fundamentals['pe_ratio'] < 100 and fundamentals['pb_ratio'] < 10)
                 ) and fundamentals['dividend_yield'] >= 0 and fundamentals['debt_to_equity'] < 2
        
        # Decision logic
        decision = "Hold"
        if market_price <= min(buy_threshold, graham_buy_threshold or float('inf')) and volume_ok and graham_ok:
            decision = "Buy"
        elif market_price >= exit_price and volume_ok:
            decision = "Sell"
        
        # Prepare fundamentals for output
        pe_ratio = None if is_etf else fundamentals['pe_ratio']
        pb_ratio = None if is_etf else fundamentals['pb_ratio']
        dividend_yield = None if is_etf else fundamentals['dividend_yield']
        
        portfolio.append([
            symbol, market_price, buy_threshold, graham_buy_threshold, exit_price,
            pe_ratio, pb_ratio, dividend_yield, decision
        ])

        # Convert portfolio list to DataFrame with specified column names
        portfolio_df = pd.DataFrame(portfolio, columns=[
            'ticker', 'price', 'entry_low', 'entry_val', 'exit',
            'P/E', 'P/B', 'DivYield', 'rating'
            ])
        
        # Minimal delay for server stability (75 calls/minute = ~0.8 seconds/call)
        time.sleep(0.1)
    
    return portfolio_df

def build_portfolio_df(portfolio_df, portfolio_price_data, 
                       historical_return, inception_date, 
                       desired_total_exposure=0.9, cash_pos=0,
                       run_date=None):
    quant_rankings = list(portfolio_df['QUANT_RATING'])
    quant_rankings.sort(reverse=True)
    quant_threshold = quant_rankings[19]
    portfolio_df_filtered = portfolio_df[(portfolio_df['TOTAL_QUANTITY'] > 0) | (portfolio_df['QUANT_RATING'] > quant_rankings[9])]
    portfolio_df_sorted = portfolio_df_filtered.sort_values(by='QUANT_RATING', ascending=False).reset_index(drop=True)

    if run_date is None:
        run_date = datetime.now().date()
    run_date = pd.to_datetime(run_date)

    # Merge portfolio holdings with price data for each position
    final_portfolio_df = pd.merge(
            portfolio_df_sorted,
            portfolio_price_data, 
            left_on='TICKER',
            right_on='ticker',
            how='left'
        )
    final_portfolio_df.drop(columns=['ticker'], inplace=True) # remove duplicated column

    # Calculate total value of each held position
    final_portfolio_df['VALUE'] = round(final_portfolio_df['TOTAL_QUANTITY'] * final_portfolio_df['price'], ndigits=2)

    # Calculate value of portfolio, portfolio weights, total return and CAGR for each position
    portfolio_total = final_portfolio_df['VALUE'].sum() + cash_pos
    final_portfolio_df['PW%'] = round(final_portfolio_df['VALUE'] / portfolio_total * 100, ndigits=2)
    final_portfolio_df.loc[final_portfolio_df['TOTAL_COST'] < 0, 'AVG_PURCHASE_PRICE'] = 0.01
    final_portfolio_df['TOTAL_RETURN'] = final_portfolio_df['VALUE'] - final_portfolio_df['TOTAL_COST']
    final_portfolio_df['ROI'] = round(final_portfolio_df['TOTAL_RETURN'] / final_portfolio_df['TOTAL_COST'] * 100, ndigits=4)

    # Calculate desired target price to optimize return
    portfolio_days_held = (run_date - inception_date).days
    portfolio_years_held = portfolio_days_held / 360
    portfolio_cagr = (1+historical_return)**(1/portfolio_years_held)-1
    alpha_age = (run_date.date() - pd.to_datetime("07-01-2022", format="%m-%d-%Y").date()).days / 360
    alpha_return = (1+2.0451)**(1/alpha_age)-1
    desired_return = min(portfolio_cagr, alpha_return)
    final_portfolio_df['YEARS_HELD'] = ((run_date - final_portfolio_df['WEIGHTED_AVG_PURCHASE_DATE']).dt.days) / 360
    final_portfolio_df['TARGET'] = round(final_portfolio_df['AVG_PURCHASE_PRICE'] * (1+desired_return)**final_portfolio_df['YEARS_HELD'], ndigits=2)
    final_portfolio_df['CAGR'] = round(((1+final_portfolio_df['ROI']/100) ** (1/final_portfolio_df['YEARS_HELD']) - 1) * 100, ndigits=2)

    # Calculate quant-based portfolio allocation and position adjustments to meet desired allocation
    desired_position_size = portfolio_total * desired_total_exposure * (1/20)
    final_portfolio_df['DESIRED_POS'] = desired_position_size * final_portfolio_df['QUANT_RATING'] / 5
    final_portfolio_df.loc[final_portfolio_df['QUANT_RATING'] < quant_threshold, 'DESIRED_POS'] = 0
    final_portfolio_df['POS_ADJUSTMENT'] = round((final_portfolio_df['DESIRED_POS'] - final_portfolio_df['VALUE']) / final_portfolio_df['price'], ndigits=0)

    # Sorta final portfolio table
    final_portfolio_df = final_portfolio_df.sort_values(by='PW%', ascending=False).reset_index(drop=True)

    return final_portfolio_df

def buys_and_sells_tables(portfolio_df):
    actions_df = portfolio_df[['TICKER', 'TOTAL_QUANTITY', 'POS_ADJUSTMENT', 
                               'price', 'entry_low', 'entry_val', 'exit', 'TARGET', 'rating']].copy()
    actions_df['ACTION'] = abs(actions_df['POS_ADJUSTMENT'] / actions_df['TOTAL_QUANTITY']) > 0.2
    buys_df = actions_df[(actions_df['POS_ADJUSTMENT'] > 0) & (actions_df['ACTION'] == True)]
    sells_df = actions_df[(actions_df['POS_ADJUSTMENT'] < 0) & (actions_df['ACTION'] == True)]
    buys_columns = ['TICKER', 'POS_ADJUSTMENT', 'price', 'entry_low', 'entry_val', 'rating']
    sells_columns = ['TICKER', 'POS_ADJUSTMENT', 'price', 'exit', 'TARGET', 'rating']
    buys_final = buys_df[buys_columns].copy()
    sells_final = sells_df[sells_columns].copy()

    return buys_final, sells_final