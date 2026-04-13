import yfinance as yf

# Testar alguns pares
symbols = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X']

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='5d', interval='1h')
        if not data.empty:
            print(f"✅ {symbol}: {len(data)} candles, último preço: {data['Close'].iloc[-1]:.5f}")
        else:
            print(f"❌ {symbol}: Sem dados")
    except Exception as e:
        print(f"❌ {symbol}: Erro - {e}")
