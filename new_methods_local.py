    def fetch_data(self, symbol, timeframe='1h', limit=200):
        \"\"\"Busca dados OHLCV - Suporta Binance e yFinance\"\"\"
        
        # Detectar se é Forex (yFinance)
        if symbol.endswith('=X'):
            return self._fetch_yfinance(symbol, timeframe, limit)
        else:
            return self._fetch_binance(symbol, timeframe, limit)

    def _fetch_binance(self, symbol, timeframe, limit):
        \"\"\"Busca de Binance (crypto)\"\"\"
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(
                ohlcv, 
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f\"Erro Binance ao buscar {symbol}: {e}\")
            return None

    def _fetch_yfinance(self, symbol, timeframe, limit):
        \"\"\"Busca de yFinance (forex, stocks, etc.)\"\"\"
        try:
            import yfinance as yf
            
            # Mapear timeframe para yFinance
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1h': '1h',
                '4h': '1h',  # yFinance não tem 4h, usar 1h
                '1d': '1d'
            }
            
            period_map = {
                '1m': '7d',
                '5m': '60d',
                '15m': '60d',
                '1h': '730d',  # 2 anos
                '4h': '730d',
                '1d': '730d'
            }
            
            interval = interval_map.get(timeframe, '1h')
            period = period_map.get(timeframe, '730d')
            
            # Download
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.error(f\"yFinance retornou dados vazios para {symbol}\")
                return None
            
            # Renomear colunas para padrão
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            
            # Ajustar nomes
            if 'date' in df.columns:
                df.rename(columns={'date': 'timestamp'}, inplace=True)
            elif 'datetime' in df.columns:
                df.rename(columns={'datetime': 'timestamp'}, inplace=True)
            
            # Garantir que tem timestamp
            if 'timestamp' not in df.columns:
                df['timestamp'] = df.index
            
            # Selecionar últimos N períodos
            df = df.tail(limit)
            
            # Colunas necessárias
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f\"Coluna {col} faltando em {symbol}\")
                    return None
            
            return df[required_cols]
            
        except Exception as e:
            logger.error(f\"Erro yFinance ao buscar {symbol}: {e}\")
            return None
