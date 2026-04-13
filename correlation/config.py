"""
CORR-WATCH System v2.0 — Configuração Central
==============================================
Carrega e valida a configuração YAML do sistema.
Fornece dataclasses tipadas para acesso seguro aos parâmetros.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 7
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import yaml

logger = logging.getLogger("corr_watch.config")

# ============================================================================
# DATACLASSES DE CONFIGURAÇÃO
# ============================================================================


@dataclass
class PairConfig:
    """Configuração de um par monitorado."""
    symbol_a: str
    symbol_b: str
    expected_correlation: float
    correlation_type: str  # "positive" ou "negative"
    priority: int
    source_b: str = "binance"  # "binance" ou "yfinance"
    yfinance_ticker: Optional[str] = None

    @property
    def pair_id(self) -> str:
        """Identificador único do par: 'BTCUSDT↔ETHUSDT'."""
        return f"{self.symbol_a}↔{self.symbol_b}"

    @property
    def is_crypto_crypto(self) -> bool:
        return self.source_b == "binance"

    @property
    def is_crypto_macro(self) -> bool:
        return self.source_b != "binance"


@dataclass
class TimeframeConfig:
    """Configuração de timeframes monitorados."""
    primary: str
    all: List[str]
    weights: Dict[str, float]


@dataclass
class WindowConfig:
    """Janelas de cálculo rolling."""
    short: int = 20
    medium: int = 50
    long: int = 100

    @property
    def all_windows(self) -> List[int]:
        return [self.short, self.medium, self.long]


@dataclass
class ThresholdConfig:
    """Thresholds de alerta do sistema."""
    # Z-Score do Spread
    z_score_alert: float = 2.0
    z_score_critical: float = 2.5
    z_score_anomaly: float = 3.0

    # Desvio de Correlação
    correlation_deviation_alert: float = 0.20
    correlation_deviation_critical: float = 0.30

    # Delta de Correlação
    delta_correlation_alert: float = 0.15
    delta_correlation_critical: float = 0.25

    # Cointegração
    cointegration_pvalue_max: float = 0.10
    halflife_max_periods: int = 100

    # Filtros
    min_volume_ratio: float = 0.80
    min_score_for_alert: int = 60
    min_quality_score: int = 75


@dataclass
class AlertConfig:
    """Configuração do sistema de alertas."""
    cooldown_seconds: int = 300
    max_simultaneous: int = 5
    notification_channels: List[str] = field(default_factory=lambda: ["console", "log"])


@dataclass
class BinanceConfig:
    """Configuração da API Binance."""
    base_url: str = "https://api.binance.com"
    klines_endpoint: str = "/api/v3/klines"
    ticker_endpoint: str = "/api/v3/ticker/price"
    max_klines_limit: int = 1000
    request_timeout_seconds: int = 10
    cache_ttl_seconds: int = 30


@dataclass
class YFinanceConfig:
    """Configuração do yFinance para dados macro."""
    cache_ttl_seconds: int = 300
    max_retries: int = 3
    timeout_seconds: int = 15


# ============================================================================
# TIMEFRAME MAPPING — Binance interval strings
# ============================================================================

TIMEFRAME_TO_BINANCE = {
    "1m": "1m",
    "3m": "3m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "1w": "1w",
}

TIMEFRAME_TO_MINUTES = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
    "1w": 10080,
}


# ============================================================================
# CLASSE PRINCIPAL DE CONFIGURAÇÃO
# ============================================================================

class CorrWatchConfig:
    """
    Configuração central do CORR-WATCH System.
    
    Carrega o correlation_config.yaml e fornece acesso tipado
    a todos os parâmetros do sistema.
    
    Uso:
        config = CorrWatchConfig()                         # auto-detect
        config = CorrWatchConfig("path/to/config.yaml")    # caminho explícito
    """

    def __init__(self, config_path: Optional[str] = None):
        self._raw: dict = {}
        self._config_path = self._resolve_config_path(config_path)
        self._load()

    # ────────────────────────────────────────────────────────────────
    # PROPRIEDADES PÚBLICAS
    # ────────────────────────────────────────────────────────────────

    @property
    def system_name(self) -> str:
        return self._raw.get("system", {}).get("name", "CORR-WATCH")

    @property
    def system_version(self) -> str:
        return self._raw.get("system", {}).get("version", "2.0")

    @property
    def update_interval(self) -> int:
        return self._raw.get("system", {}).get("update_interval_seconds", 5)

    @property
    def log_level(self) -> str:
        return self._raw.get("system", {}).get("log_level", "INFO")

    @property
    def pairs(self) -> List[PairConfig]:
        """Retorna todos os pares configurados (crypto + macro)."""
        if not hasattr(self, "_pairs_cache"):
            self._pairs_cache = self._parse_pairs()
        return self._pairs_cache

    @property
    def crypto_pairs(self) -> List[PairConfig]:
        """Apenas pares crypto-crypto."""
        return [p for p in self.pairs if p.is_crypto_crypto]

    @property
    def macro_pairs(self) -> List[PairConfig]:
        """Apenas pares crypto-macro."""
        return [p for p in self.pairs if p.is_crypto_macro]

    @property
    def all_symbols(self) -> List[str]:
        """Todos os símbolos Binance únicos necessários."""
        symbols = set()
        for pair in self.pairs:
            symbols.add(pair.symbol_a)
            if pair.is_crypto_crypto:
                symbols.add(pair.symbol_b)
        return sorted(symbols)

    @property
    def timeframes(self) -> TimeframeConfig:
        tf = self._raw.get("timeframes", {})
        return TimeframeConfig(
            primary=tf.get("primary", "1h"),
            all=tf.get("all", ["5m", "15m", "1h", "4h", "1d"]),
            weights=tf.get("weights", {"1h": 1.0}),
        )

    @property
    def windows(self) -> WindowConfig:
        w = self._raw.get("windows", {})
        return WindowConfig(
            short=w.get("short", 20),
            medium=w.get("medium", 50),
            long=w.get("long", 100),
        )

    @property
    def thresholds(self) -> ThresholdConfig:
        t = self._raw.get("thresholds", {})
        return ThresholdConfig(**{k: v for k, v in t.items() if k in ThresholdConfig.__dataclass_fields__})

    @property
    def alerts(self) -> AlertConfig:
        a = self._raw.get("alerts", {})
        return AlertConfig(
            cooldown_seconds=a.get("cooldown_seconds", 300),
            max_simultaneous=a.get("max_simultaneous", 5),
            notification_channels=a.get("notification_channels", ["console", "log"]),
        )

    @property
    def binance(self) -> BinanceConfig:
        b = self._raw.get("binance", {})
        return BinanceConfig(**{k: v for k, v in b.items() if k in BinanceConfig.__dataclass_fields__})

    @property
    def yfinance(self) -> YFinanceConfig:
        y = self._raw.get("yfinance", {})
        return YFinanceConfig(**{k: v for k, v in y.items() if k in YFinanceConfig.__dataclass_fields__})

    # ────────────────────────────────────────────────────────────────
    # REGIME ADJUSTMENTS
    # ────────────────────────────────────────────────────────────────

    def get_thresholds_for_regime(self, regime: str) -> ThresholdConfig:
        """
        Retorna thresholds ajustados para o regime de mercado atual.
        
        Args:
            regime: "ranging", "bull", "bear", "high_volatility"
        
        Returns:
            ThresholdConfig com valores ajustados
        """
        base = self.thresholds
        adjustments = self._raw.get("regime_adjustments", {}).get(regime, {})

        if not adjustments:
            return base

        # Aplica overlays do regime sobre os thresholds base
        adjusted_dict = {k: getattr(base, k) for k in ThresholdConfig.__dataclass_fields__}
        for key, value in adjustments.items():
            if key in adjusted_dict:
                adjusted_dict[key] = value

        return ThresholdConfig(**adjusted_dict)

    # ────────────────────────────────────────────────────────────────
    # INTERNOS
    # ────────────────────────────────────────────────────────────────

    def _resolve_config_path(self, config_path: Optional[str]) -> str:
        """Resolve o caminho do arquivo de configuração."""
        if config_path and os.path.exists(config_path):
            return config_path

        # Auto-detect: busca subindo da pasta atual
        search_paths = [
            os.path.join(os.path.dirname(__file__), "..", "config", "correlation_config.yaml"),
            os.path.join(os.path.dirname(__file__), "config", "correlation_config.yaml"),
            os.path.join(os.getcwd(), "config", "correlation_config.yaml"),
        ]

        for path in search_paths:
            resolved = os.path.abspath(path)
            if os.path.exists(resolved):
                return resolved

        raise FileNotFoundError(
            f"correlation_config.yaml não encontrado. "
            f"Buscou em: {[os.path.abspath(p) for p in search_paths]}"
        )

    def _load(self) -> None:
        """Carrega e valida o YAML."""
        logger.info(f"Carregando configuração de: {self._config_path}")
        with open(self._config_path, "r", encoding="utf-8") as f:
            self._raw = yaml.safe_load(f)

        if not self._raw:
            raise ValueError("Arquivo de configuração vazio ou inválido")

        logger.info(
            f"Configuração carregada: {self.system_name} v{self.system_version} "
            f"| {len(self.pairs)} pares | {len(self.timeframes.all)} timeframes"
        )

    def _parse_pairs(self) -> List[PairConfig]:
        """Converte a configuração YAML em lista de PairConfig."""
        pairs = []
        pairs_cfg = self._raw.get("pairs", {})

        for category in ["crypto_crypto", "crypto_macro"]:
            for entry in pairs_cfg.get(category, []):
                pair_symbols = entry.get("pair", [])
                if len(pair_symbols) != 2:
                    logger.warning(f"Par inválido ignorado: {entry}")
                    continue

                pairs.append(PairConfig(
                    symbol_a=pair_symbols[0],
                    symbol_b=pair_symbols[1],
                    expected_correlation=entry.get("expected_correlation", 0.0),
                    correlation_type=entry.get("correlation_type", "positive"),
                    priority=entry.get("priority", 99),
                    source_b=entry.get("source_b", "binance"),
                    yfinance_ticker=entry.get("yfinance_ticker"),
                ))

        # Ordena por prioridade
        pairs.sort(key=lambda p: p.priority)
        return pairs

    def __repr__(self) -> str:
        return (
            f"CorrWatchConfig(name={self.system_name!r}, version={self.system_version!r}, "
            f"pairs={len(self.pairs)}, timeframes={self.timeframes.all})"
        )
