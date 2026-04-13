"""
CORR-WATCH System v2.0 — Motor de Correlação Pearson
=====================================================
Cálculo de correlação de Pearson rolling multi-par com 
janelas configuráveis (20, 50, 100 períodos).

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.1 (Motor de Correlação)
Fórmula: r = Σ[(Xi - X̄)(Yi - Ȳ)] / √[Σ(Xi-X̄)² × Σ(Yi-Ȳ)²]
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger("corr_watch.engine.pearson")


@dataclass
class CorrelationResult:
    """
    Resultado do cálculo de correlação para um par.
    
    Campos:
      - pair_id: Identificador do par (ex: "BTCUSDT↔ETHUSDT")
      - correlations: Dict[window_size, Series] com correlação rolling
      - current: Dict[window_size, float] com valor atual de cada janela
      - delta: Dict[window_size, float] com variação em 5 períodos
      - mean: Dict[window_size, float] com média histórica da correlação
      - std: Dict[window_size, float] com desvio padrão da correlação
    """
    pair_id: str
    correlations: Dict[int, pd.Series] = field(default_factory=dict)
    current: Dict[int, float] = field(default_factory=dict)
    delta: Dict[int, float] = field(default_factory=dict)
    mean: Dict[int, float] = field(default_factory=dict)
    std: Dict[int, float] = field(default_factory=dict)
    timestamp: Optional[pd.Timestamp] = None

    def get_deviation_sigma(self, window: int) -> float:
        """
        Calcula quantos sigmas o valor atual desvia da média.
        Usado para coloração da tabela de monitoramento.
        """
        if window not in self.current or window not in self.mean:
            return 0.0
        std = self.std.get(window, 1.0)
        if std == 0:
            return 0.0
        return abs(self.current[window] - self.mean[window]) / std

    def is_anomaly(self, window: int, threshold_sigma: float = 2.5) -> bool:
        """Verifica se a correlação está em nível anômalo."""
        return self.get_deviation_sigma(window) > threshold_sigma


class PearsonEngine:
    """
    Motor de Correlação de Pearson Rolling Multi-Par.
    
    Core do sistema CORR-WATCH. Calcula correlações de Pearson
    com janelas rolling para pares de retornos de preço.
    
    Janelas padrão:
      - 20 períodos: curto prazo (ruído alto, reação rápida)
      - 50 períodos: médio prazo (equilíbrio ruído/sinal)
      - 100 períodos: longo prazo (tendência estrutural)
    
    Cálculos adicionais:
      - Delta de correlação (velocidade de mudança)
      - Desvio da média histórica (em sigmas)
      - Classificação de intensidade (forte/moderada/fraca/neutra)
    
    Uso:
        engine = PearsonEngine(windows=[20, 50, 100])
        result = engine.calculate(returns_a, returns_b, pair_id="BTCUSDT↔ETHUSDT")
        print(f"Corr 20p: {result.current[20]:.4f}")
        print(f"Delta 5p: {result.delta[20]:.4f}")
    """

    # Classificação de intensidade de correlação
    THRESHOLDS = {
        "strong_positive": 0.70,
        "moderate_positive": 0.40,
        "weak": 0.40,  # |r| < 0.40
        "moderate_negative": -0.40,
        "strong_negative": -0.70,
    }

    def __init__(self, windows: Optional[List[int]] = None, delta_lookback: int = 5):
        """
        Args:
            windows: Lista de janelas rolling [20, 50, 100]
            delta_lookback: Períodos para calcular ΔCorr (padrão: 5)
        """
        self.windows = windows or [20, 50, 100]
        self.delta_lookback = delta_lookback

    def calculate(
        self,
        returns_a: pd.Series,
        returns_b: pd.Series,
        pair_id: str = "A↔B",
    ) -> CorrelationResult:
        """
        Calcula correlação de Pearson rolling para um par.
        
        Args:
            returns_a: Série de retornos logarítmicos do ativo A
            returns_b: Série de retornos logarítmicos do ativo B
            pair_id: Identificador do par
            
        Returns:
            CorrelationResult com correlações, delta, desvio, etc.
        """
        if returns_a is None or returns_b is None:
            logger.warning(f"Dados nulos para {pair_id}")
            return CorrelationResult(pair_id=pair_id)

        # Alinha séries (garante mesmo index)
        combined = pd.DataFrame({"a": returns_a, "b": returns_b}).dropna()

        if len(combined) < min(self.windows):
            logger.warning(
                f"Dados insuficientes para {pair_id}: "
                f"{len(combined)} < {min(self.windows)} (janela mínima)"
            )
            return CorrelationResult(pair_id=pair_id)

        result = CorrelationResult(
            pair_id=pair_id,
            timestamp=combined.index[-1] if not combined.empty else None,
        )

        for window in self.windows:
            if len(combined) < window:
                logger.debug(f"Janela {window} > dados disponíveis ({len(combined)}) para {pair_id}")
                continue

            # Correlação rolling
            corr_series = combined["a"].rolling(window=window).corr(combined["b"])
            corr_series = corr_series.dropna()

            if corr_series.empty:
                continue

            result.correlations[window] = corr_series

            # Valor atual
            result.current[window] = float(corr_series.iloc[-1])

            # Média e desvio padrão históricos
            result.mean[window] = float(corr_series.mean())
            result.std[window] = float(corr_series.std())

            # Delta de correlação (velocidade de mudança)
            if len(corr_series) > self.delta_lookback:
                delta = float(
                    corr_series.iloc[-1] - corr_series.iloc[-1 - self.delta_lookback]
                )
            else:
                delta = 0.0
            result.delta[window] = delta

        logger.debug(
            f"Pearson {pair_id}: "
            + " | ".join(
                f"W{w}={result.current.get(w, float('nan')):.4f} "
                f"(Δ={result.delta.get(w, 0):.4f})"
                for w in self.windows
            )
        )

        return result

    def calculate_from_prices(
        self,
        prices_a: pd.Series,
        prices_b: pd.Series,
        pair_id: str = "A↔B",
    ) -> CorrelationResult:
        """
        Calcula correlação a partir de séries de preço (calcula retornos internamente).
        
        Args:
            prices_a: Série de preços de fechamento do ativo A
            prices_b: Série de preços de fechamento do ativo B
            pair_id: Identificador do par
        """
        returns_a = np.log(prices_a / prices_a.shift(1)).dropna()
        returns_b = np.log(prices_b / prices_b.shift(1)).dropna()
        return self.calculate(returns_a, returns_b, pair_id)

    def classify_correlation(self, value: float) -> str:
        """
        Classifica a intensidade da correlação.
        
        Returns:
            "STRONG_POS", "MODERATE_POS", "WEAK/NEUTRAL", 
            "MODERATE_NEG", "STRONG_NEG"
        """
        if value >= self.THRESHOLDS["strong_positive"]:
            return "STRONG_POS"
        elif value >= self.THRESHOLDS["moderate_positive"]:
            return "MODERATE_POS"
        elif value <= self.THRESHOLDS["strong_negative"]:
            return "STRONG_NEG"
        elif value <= self.THRESHOLDS["moderate_negative"]:
            return "MODERATE_NEG"
        else:
            return "WEAK/NEUTRAL"

    def get_color_code(self, value: float, expected: float, std: float) -> str:
        """
        Retorna código de cor baseado em desvio da correlação esperada.
        
        🟢 Dentro do padrão (±1σ)
        🟡 Atenção (1-2σ)
        🟠 Alerta (2-2.5σ)
        🔴 Crítico (>2.5σ)
        
        Args:
            value: Correlação atual
            expected: Correlação esperada do par
            std: Desvio padrão histórico
        """
        if std == 0:
            return "🟢"

        deviation = abs(value - expected) / std

        if deviation <= 1.0:
            return "🟢"
        elif deviation <= 2.0:
            return "🟡"
        elif deviation <= 2.5:
            return "🟠"
        else:
            return "🔴"

    def calculate_batch(
        self,
        aligned_data: pd.DataFrame,
        pairs: List[Tuple[str, str]],
    ) -> Dict[str, CorrelationResult]:
        """
        Calcula correlação para múltiplos pares a partir de dados alinhados.
        
        Args:
            aligned_data: DataFrame com colunas returns_SYMBOL
            pairs: Lista de tuplas (symbol_a, symbol_b)
            
        Returns:
            Dict[pair_id, CorrelationResult]
        """
        results = {}

        for sym_a, sym_b in pairs:
            col_a = f"returns_{sym_a}"
            col_b = f"returns_{sym_b}"

            if col_a not in aligned_data.columns or col_b not in aligned_data.columns:
                logger.warning(f"Colunas faltando para {sym_a}↔{sym_b}: {aligned_data.columns.tolist()}")
                continue

            pair_id = f"{sym_a}↔{sym_b}"
            result = self.calculate(
                aligned_data[col_a],
                aligned_data[col_b],
                pair_id=pair_id,
            )
            results[pair_id] = result

        logger.info(f"Batch Pearson: {len(results)} pares calculados")
        return results
