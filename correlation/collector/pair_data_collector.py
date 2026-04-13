"""
CORR-WATCH System v2.0 — Coleta de Dados Multi-Par
===================================================
Coleta klines de N pares simultâneos via Binance REST API e yFinance.
Suporte assíncrono com cache TTL para evitar rate limiting.

Referência: CORRELAÇÃO BINANCE(copia).md — Camada 1 (Ingestão de Dados)
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import aiohttp
import numpy as np
import pandas as pd

from correlation.config import (
    CorrWatchConfig,
    PairConfig,
    TIMEFRAME_TO_BINANCE,
    TIMEFRAME_TO_MINUTES,
)

logger = logging.getLogger("corr_watch.collector")


# ============================================================================
# CACHE SIMPLES COM TTL
# ============================================================================

class TTLCache:
    """Cache in-memory com TTL por chave."""

    def __init__(self, default_ttl: int = 30):
        self._store: Dict[str, Tuple[float, object]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[object]:
        if key in self._store:
            ts, value = self._store[key]
            if time.time() - ts < self._default_ttl:
                return value
            del self._store[key]
        return None

    def set(self, key: str, value: object, ttl: Optional[int] = None) -> None:
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)


# ============================================================================
# COLETOR DE DADOS MULTI-PAR
# ============================================================================

class PairDataCollector:
    """
    Coleta dados de preço de N pares em paralelo.
    
    Fontes:
      - Binance REST API: pares crypto-crypto (BTCUSDT, ETHUSDT, etc.)
      - yFinance: dados macro (DXY, SPX, VIX, Gold)
    
    Pipeline:
      1. Identifica símbolos únicos necessários
      2. Coleta klines em paralelo (async)
      3. Converte para DataFrames com colunas OHLCV padrão
      4. Cache com TTL para evitar rate limiting
    
    Uso:
        config = CorrWatchConfig()
        collector = PairDataCollector(config)
        data = await collector.fetch_all_pairs("1h", limit=100)
        # data = {"BTCUSDT": DataFrame, "ETHUSDT": DataFrame, ...}
    """

    def __init__(self, config: CorrWatchConfig):
        self.config = config
        self._cache = TTLCache(default_ttl=config.binance.cache_ttl_seconds)
        self._yf_cache = TTLCache(default_ttl=config.yfinance.cache_ttl_seconds)
        self._session: Optional[aiohttp.ClientSession] = None

    # ────────────────────────────────────────────────────────────────
    # API PÚBLICA
    # ────────────────────────────────────────────────────────────────

    async def fetch_all_pairs(
        self,
        timeframe: str = "1h",
        limit: int = 200,
    ) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados de TODOS os símbolos necessários para os pares configurados.
        
        Args:
            timeframe: Intervalo (ex: "1h", "5m", "4h")
            limit: Número de candles a coletar
            
        Returns:
            Dict[symbol, DataFrame] com colunas: 
              timestamp, open, high, low, close, volume, trades
        """
        results: Dict[str, pd.DataFrame] = {}

        # 1. Coleta pares Binance (async paralelo)
        binance_symbols = self.config.all_symbols
        if binance_symbols:
            binance_data = await self._fetch_binance_batch(binance_symbols, timeframe, limit)
            results.update(binance_data)

        # 2. Coleta dados macro (yfinance — síncrono em thread)
        macro_pairs = self.config.macro_pairs
        if macro_pairs:
            macro_data = await self._fetch_yfinance_batch(macro_pairs, timeframe, limit)
            results.update(macro_data)

        logger.info(
            f"Coleta concluída: {len(results)} séries | "
            f"timeframe={timeframe} | limit={limit}"
        )
        return results

    async def fetch_pair_klines(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 200,
    ) -> Optional[pd.DataFrame]:
        """Coleta klines de um único símbolo Binance."""
        cache_key = f"binance:{symbol}:{timeframe}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit: {cache_key}")
            return cached

        df = await self._fetch_binance_klines(symbol, timeframe, limit)
        if df is not None and not df.empty:
            self._cache.set(cache_key, df)
        return df

    async def close(self) -> None:
        """Fecha a sessão HTTP."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    # ────────────────────────────────────────────────────────────────
    # BINANCE REST API
    # ────────────────────────────────────────────────────────────────

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria a sessão HTTP."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self.config.binance.request_timeout_seconds
            )
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def _fetch_binance_batch(
        self,
        symbols: List[str],
        timeframe: str,
        limit: int,
    ) -> Dict[str, pd.DataFrame]:
        """Coleta klines de múltiplos símbolos Binance em paralelo."""
        tasks = []
        for symbol in symbols:
            tasks.append(self._fetch_binance_klines(symbol, timeframe, limit))

        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        data = {}
        for symbol, result in zip(symbols, results_list):
            if isinstance(result, Exception):
                logger.error(f"Erro coletando {symbol}: {result}")
                continue
            if result is not None and not result.empty:
                data[symbol] = result
                self._cache.set(f"binance:{symbol}:{timeframe}", result)

        return data

    async def _fetch_binance_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> Optional[pd.DataFrame]:
        """
        Coleta klines de um símbolo via Binance REST API.
        
        Endpoint: GET /api/v3/klines
        Retorna DataFrame com: timestamp, open, high, low, close, volume, trades
        """
        session = await self._get_session()
        interval = TIMEFRAME_TO_BINANCE.get(timeframe, timeframe)
        url = f"{self.config.binance.base_url}{self.config.binance.klines_endpoint}"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, self.config.binance.max_klines_limit),
        }

        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"Binance API error {resp.status} para {symbol}: {text}")
                    return None

                raw_data = await resp.json()

            if not raw_data:
                logger.warning(f"Sem dados para {symbol} {timeframe}")
                return None

            # Converte para DataFrame
            df = pd.DataFrame(raw_data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades",
                "taker_buy_volume", "taker_buy_quote_volume", "ignore",
            ])

            # Tipagem e limpeza
            df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
            for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
                df[col] = df[col].astype(float)
            df["trades"] = df["trades"].astype(int)

            # Seleciona colunas relevantes
            df = df[["timestamp", "open", "high", "low", "close", "volume", "trades"]].copy()
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)

            logger.debug(
                f"Binance klines: {symbol} {timeframe} → {len(df)} candles "
                f"[{df.index[0]} → {df.index[-1]}]"
            )
            return df

        except asyncio.TimeoutError:
            logger.error(f"Timeout coletando {symbol} {timeframe}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado coletando {symbol}: {e}")
            return None

    # ────────────────────────────────────────────────────────────────
    # yFINANCE (Dados Macro)
    # ────────────────────────────────────────────────────────────────

    async def _fetch_yfinance_batch(
        self,
        macro_pairs: List[PairConfig],
        timeframe: str,
        limit: int,
    ) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados macro via yfinance em thread separada.
        yfinance é síncrono, executamos em executor.
        """
        results = {}
        loop = asyncio.get_event_loop()

        for pair in macro_pairs:
            if not pair.yfinance_ticker:
                continue

            cache_key = f"yf:{pair.symbol_b}:{timeframe}"
            cached = self._yf_cache.get(cache_key)
            if cached is not None:
                results[pair.symbol_b] = cached
                continue

            try:
                df = await loop.run_in_executor(
                    None,
                    self._fetch_yfinance_sync,
                    pair.yfinance_ticker,
                    pair.symbol_b,
                    timeframe,
                    limit,
                )
                if df is not None and not df.empty:
                    results[pair.symbol_b] = df
                    self._yf_cache.set(cache_key, df)
            except Exception as e:
                logger.error(f"Erro yFinance {pair.symbol_b}: {e}")

        return results

    def _fetch_yfinance_sync(
        self,
        ticker: str,
        label: str,
        timeframe: str,
        limit: int,
    ) -> Optional[pd.DataFrame]:
        """Coleta síncrona de dados via yfinance."""
        try:
            import yfinance as yf
        except ImportError:
            logger.warning("yfinance não instalado. Dados macro indisponíveis.")
            return None

        # Mapeia timeframe para yfinance interval e period
        yf_interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "1h",  # yfinance não tem 4h, usamos 1h
            "1d": "1d",
        }

        interval = yf_interval_map.get(timeframe, "1h")

        # Calcula período baseado no limit
        minutes = TIMEFRAME_TO_MINUTES.get(timeframe, 60)
        total_minutes = minutes * limit
        days_needed = max(1, total_minutes // 1440 + 1)

        # yfinance tem limites de período por intervalo
        if interval in ("1m", "5m", "15m", "30m"):
            period = f"{min(days_needed, 7)}d"
        elif interval == "1h":
            period = f"{min(days_needed, 730)}d"
        else:
            period = f"{min(days_needed, 3650)}d"

        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period=period, interval=interval)

            if hist.empty:
                logger.warning(f"yFinance: sem dados para {ticker}")
                return None

            # Normaliza para formato padrão
            df = pd.DataFrame({
                "open": hist["Open"],
                "high": hist["High"],
                "low": hist["Low"],
                "close": hist["Close"],
                "volume": hist["Volume"],
                "trades": 0,  # yfinance não fornece trades
            })

            # Garante timezone-aware
            if df.index.tz is None:
                df.index = df.index.tz_localize("UTC")
            else:
                df.index = df.index.tz_convert("UTC")

            df.index.name = "timestamp"
            df.sort_index(inplace=True)

            # Limita ao número solicitado
            df = df.tail(limit)

            logger.debug(
                f"yFinance: {label} ({ticker}) {timeframe} → {len(df)} candles "
                f"[{df.index[0]} → {df.index[-1]}]"
            )
            return df

        except Exception as e:
            logger.error(f"yFinance error {ticker}: {e}")
            return None

    # ────────────────────────────────────────────────────────────────
    # CONTEXT MANAGER
    # ────────────────────────────────────────────────────────────────

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
