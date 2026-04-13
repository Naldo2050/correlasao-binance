"""
CORR-WATCH System v2.0 — Motor de Correlação Spearman (Rank)
=============================================================
Correlação de Spearman rank-based, robusta contra outliers e
capaz de detectar relações não-lineares que Pearson ignora.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.1, item 2

Fórmula: ρ = 1 - [6·Σ(di²)] / [n(n²-1)]
  onde di = rank(Xi) - rank(Yi)

Vantagens sobre Pearson:
  - Robusta contra outliers e movimentos extremos
  - Captura relações não-lineares (monotônicas)
  - Menos sensível a manipulações de preço
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger("corr_watch.engine.spearman")


@dataclass
class SpearmanResult:
    """
    Resultado do cálculo de correlação Spearman para um par.

    Campos:
      - pair_id: Identificador do par
      - correlations: Dict[window, Series] com correlação rolling
      - current: Dict[window, float] com valor atual
      - pvalues: Dict[window, float] com p-value da correlação atual
      - delta: Dict[window, float] com variação em N períodos
      - pearson_divergence: Dict[window, float] diferença Spearman - Pearson
    """
    pair_id: str
    correlations: Dict[int, pd.Series] = field(default_factory=dict)
    current: Dict[int, float] = field(default_factory=dict)
    pvalues: Dict[int, float] = field(default_factory=dict)
    delta: Dict[int, float] = field(default_factory=dict)
    mean: Dict[int, float] = field(default_factory=dict)
    std: Dict[int, float] = field(default_factory=dict)
    pearson_divergence: Dict[int, float] = field(default_factory=dict)
    timestamp: Optional[pd.Timestamp] = None

    @property
    def has_nonlinearity(self) -> bool:
        """
        Detecta possível relação não-linear:
        Se |Spearman - Pearson| > 0.10, há componente não-linear.
        """
        for w, div in self.pearson_divergence.items():
            if abs(div) > 0.10:
                return True
        return False

    def is_significant(self, window: int, alpha: float = 0.05) -> bool:
        """Verifica se a correlação é estatisticamente significativa."""
        return self.pvalues.get(window, 1.0) < alpha


class SpearmanEngine:
    """
    Motor de Correlação de Spearman Rolling Multi-Par.

    Complementa o PearsonEngine com análise rank-based.
    Especialmente útil em crypto onde outliers e manipulações
    podem distorcer a correlação de Pearson.

    Uso:
        engine = SpearmanEngine(windows=[20, 50])
        result = engine.calculate(returns_a, returns_b, pair_id="BTC↔ETH")
        print(f"Spearman 50p: {result.current[50]:.4f}")
        print(f"Não-linearidade: {result.has_nonlinearity}")
    """

    def __init__(
        self,
        windows: Optional[List[int]] = None,
        delta_lookback: int = 5,
    ):
        """
        Args:
            windows: Janelas rolling (padrão: [50] — Spearman é mais estável)
            delta_lookback: Períodos para delta
        """
        self.windows = windows or [50]
        self.delta_lookback = delta_lookback

    def calculate(
        self,
        returns_a: pd.Series,
        returns_b: pd.Series,
        pair_id: str = "A↔B",
        pearson_current: Optional[Dict[int, float]] = None,
    ) -> SpearmanResult:
        """
        Calcula correlação de Spearman rolling.

        Args:
            returns_a: Retornos do ativo A
            returns_b: Retornos do ativo B
            pair_id: Identificador do par
            pearson_current: Correlações Pearson atuais para calcular divergência
        """
        if returns_a is None or returns_b is None:
            return SpearmanResult(pair_id=pair_id)

        combined = pd.DataFrame({"a": returns_a, "b": returns_b}).dropna()

        if len(combined) < min(self.windows):
            logger.warning(
                f"Dados insuficientes para Spearman {pair_id}: "
                f"{len(combined)} < {min(self.windows)}"
            )
            return SpearmanResult(pair_id=pair_id)

        result = SpearmanResult(
            pair_id=pair_id,
            timestamp=combined.index[-1] if not combined.empty else None,
        )

        for window in self.windows:
            if len(combined) < window:
                continue

            # Calcula Spearman rolling
            spearman_series = self._rolling_spearman(
                combined["a"], combined["b"], window
            )

            if spearman_series.empty:
                continue

            result.correlations[window] = spearman_series
            result.current[window] = float(spearman_series.iloc[-1])
            result.mean[window] = float(spearman_series.mean())
            result.std[window] = float(spearman_series.std())

            # P-value do ponto atual
            recent_a = combined["a"].iloc[-window:]
            recent_b = combined["b"].iloc[-window:]
            _, pval = stats.spearmanr(recent_a, recent_b)
            result.pvalues[window] = float(pval)

            # Delta
            if len(spearman_series) > self.delta_lookback:
                result.delta[window] = float(
                    spearman_series.iloc[-1]
                    - spearman_series.iloc[-1 - self.delta_lookback]
                )
            else:
                result.delta[window] = 0.0

            # Divergência com Pearson
            if pearson_current and window in pearson_current:
                result.pearson_divergence[window] = (
                    result.current[window] - pearson_current[window]
                )

        logger.debug(
            f"Spearman {pair_id}: "
            + " | ".join(
                f"W{w}={result.current.get(w, float('nan')):.4f} "
                f"(p={result.pvalues.get(w, 1.0):.4f})"
                for w in self.windows
            )
        )

        return result

    def calculate_from_prices(
        self,
        prices_a: pd.Series,
        prices_b: pd.Series,
        pair_id: str = "A↔B",
        pearson_current: Optional[Dict[int, float]] = None,
    ) -> SpearmanResult:
        """Calcula a partir de séries de preços."""
        returns_a = np.log(prices_a / prices_a.shift(1)).dropna()
        returns_b = np.log(prices_b / prices_b.shift(1)).dropna()
        return self.calculate(returns_a, returns_b, pair_id, pearson_current)

    def calculate_batch(
        self,
        aligned_data: pd.DataFrame,
        pairs: List[Tuple[str, str]],
        pearson_results: Optional[dict] = None,
    ) -> Dict[str, SpearmanResult]:
        """
        Calcula Spearman para múltiplos pares.

        Args:
            aligned_data: DataFrame com colunas returns_SYMBOL
            pairs: Lista de tuplas (symbol_a, symbol_b)
            pearson_results: Dict[pair_id, PearsonResult] para divergência
        """
        results = {}

        for sym_a, sym_b in pairs:
            col_a = f"returns_{sym_a}"
            col_b = f"returns_{sym_b}"

            if col_a not in aligned_data.columns or col_b not in aligned_data.columns:
                continue

            pair_id = f"{sym_a}↔{sym_b}"

            # Extrai Pearson current se disponível
            p_current = None
            if pearson_results and pair_id in pearson_results:
                p_current = pearson_results[pair_id].current

            result = self.calculate(
                aligned_data[col_a],
                aligned_data[col_b],
                pair_id=pair_id,
                pearson_current=p_current,
            )
            results[pair_id] = result

        logger.info(f"Batch Spearman: {len(results)} pares calculados")
        return results

    # ────────────────────────────────────────────────────────────────
    # ROLLING SPEARMAN
    # ────────────────────────────────────────────────────────────────

    def _rolling_spearman(
        self,
        series_a: pd.Series,
        series_b: pd.Series,
        window: int,
    ) -> pd.Series:
        """
        Calcula correlação de Spearman rolling.

        Usa scipy.stats.spearmanr para cada janela.
        """
        n = len(series_a)
        if n < window:
            return pd.Series(dtype=float)

        correlations = []
        indices = []

        for i in range(window, n + 1):
            chunk_a = series_a.iloc[i - window : i]
            chunk_b = series_b.iloc[i - window : i]

            rho, _ = stats.spearmanr(chunk_a, chunk_b)
            correlations.append(rho)
            indices.append(series_a.index[i - 1])

        return pd.Series(correlations, index=indices, name="spearman")
