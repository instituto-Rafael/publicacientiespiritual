def compute_advanced_technical_indicators(df):
    # EMA 12 e 26
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # RSI (cálculo completo)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bandas de Bollinger
    df['BB_Mean'] = df['close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Mean'] + 2 * df['close'].rolling(window=20).std()
    df['BB_Lower'] = df['BB_Mean'] - 2 * df['close'].rolling(window=20).std()

    # VWAP (simplificado para exemplo)
    df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

    return df
