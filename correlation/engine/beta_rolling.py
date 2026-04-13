"""
CORR-WATCH System v2.0 — Beta Rolling entre Pares
===================================================
Monitora a sensibilidade (beta/hedge ratio) entre pares ao longo
do tempo. Mudanças bruscas no beta sinalizam mudança de regime.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.1, item 4

Fórmula: β = Cov(R_A, R_B) / Var(R_B)

Interpretação:
  β > 1.0: A é mais sensível que B (amplifica movimentos)
  β = 1.0: Movem-se na mesma proporção
  β < 1.0: A é menos sensível que B (amortece movimentos)
  β < 0.0: Movem-se em direções opostas
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger("corr_watch.engine.beta_rolling")


@dataclass
class BetaResult:
    """
    Resultado do cálculo de beta rolling para um par.

    Campos:
      - pair_id: Identificador do par
      - betas: Dict[window, Series] com beta rolling
      - current: Dict[window, float] com beta atual
      - delta: Dict[window, float] com variação em N períodos
      - stability: float (0-1) estabilidade do beta (1 = muito estável)
      - regime_change_signal: bool — True se beta mudou de sinal
    """
    pair_id: str
    betas: Dict[int, pd.Series] = field(default_factory=dict)
    current: Dict[int, float] = field(default_factory=dict)
    delta: Dict[int, float] = field(default_factory=dict)
    mean: Dict[int, float] = field(default_factory=dict)
    std: Dict[int, float] = field(default_factory=dict)
    stability: float = 1.0
    regime_change_signal: bool = False
    timestamp: Optional[pd.Timestamp] = None

    @property
    def is_amplifier(self) -> bool:
        """Ativo A amplifica movimentos de B (β > 1)."""
        beta = self.current.get(50) or self.current.get(
            min(self.current.keys()) if self.current else 50
        )
        return beta is not None and beta > 1.0

    @property
    def is_inverse(self) -> bool:
        """Ativos movem-se em direções opostas (β < 0)."""
        beta = self.current.get(50) or self.current.get(
            min(self.current.keys()) if self.current else 50
        )
        return beta is not None and beta < 0.0


class BetaRolling:
    """
    Motor de Beta Rolling entre pares de ativos.

    O beta mede a sensibilidade entre dois ativos:
    quanto se espera que A mova quando B move 1%.
    Monitorar mudanças no beta ajuda a detectar:
      - Mudanças de regime de correlação
      - Desacoplamento entre ativos
      - Mudança na dinâmica de hedge

    Uso:
        beta_engine = BetaRolling(windows=[20, 50, 100])
        result = beta_engine.calculate(returns_btc, returns_eth, pair_id="BTC↔ETH")
        print(f"Beta 50p: {result.current[50]:.4f}")
        print(f"Regime change: {result.regime_change_signal}")
    """

    def __init__(
        self,
        windows: Optional[List[int]] = None,
        delta_lookback: int = 5,
        regime_change_threshold: float = 0.30,
    ):
        """
        Args:
            windows: Janelas rolling [20, 50, 100]
            delta_lookback: Períodos para delta
            regime_change_threshold: |Δβ| mínimo para sinal de regime change
        """
        self.windows = windows or [20, 50, 100]
        self.delta_lookback = delta_lookback
        self.regime_threshold = regime_change_threshold

    def calculate(
        self,
        returns_a: pd.Series,
        returns_b: pd.Series,
        pair_id: str = "A↔B",
    ) -> BetaResult:
        """
        Calcula beta rolling para um par.

        Args:
            returns_a: Retornos do ativo A (dependente)
            returns_b: Retornos do ativo B (independente/benchmark)
            pair_id: Identificador do par

        Returns:
            BetaResult com betas rolling, delta, estabilidade
        """
        if returns_a is None or returns_b is None:
            return BetaResult(pair_id=pair_id)

        combined = pd.DataFrame({"a": returns_a, "b": returns_b}).dropna()

        if len(combined) < min(self.windows):
            logger.warning(
                f"Dados insuficientes para Beta {pair_id}: {len(combined)}"
            )
            return BetaResult(pair_id=pair_id)

        result = BetaResult(
            pair_id=pair_id,
            timestamp=combined.index[-1] if not combined.empty else None,
        )

        for window in self.windows:
            if len(combined) < window:
                continue

            # Beta rolling: β = Cov(A,B) / Var(B)
            cov_series = combined["a"].rolling(window).cov(combined["b"])
            var_series = combined["b"].rolling(window).var()

            # Evita divisão por zero
            var_series = var_series.replace(0, np.nan)
            beta_series = (cov_series / var_series).dropna()

            if beta_series.empty:
                continue

            result.betas[window] = beta_series
            result.current[window] = float(beta_series.iloc[-1])
            result.mean[window] = float(beta_series.mean())
            result.std[window] = float(beta_series.std())

            # Delta
            if len(beta_series) > self.delta_lookback:
                result.delta[window] = float(
                    beta_series.iloc[-1]
                    - beta_series.iloc[-1 - self.delta_lookback]
                )
            else:
                result.delta[window] = 0.0

        # Estabilidade (coeficiente de variação invertido, normalizado 0-1)
        if 50 in result.betas and result.mean.get(50) and result.std.get(50):
            cv = abs(result.std[50] / result.mean[50]) if result.mean[50] != 0 else 1.0
            result.stability = max(0.0, min(1.0, 1.0 - cv))
        else:
            result.stability = 0.5

        # Sinal de regime change: beta mudou significativamente
        for w in self.windows:
            if w in result.delta and abs(result.delta[w]) > self.regime_threshold:
                result.regime_change_signal = True
                break

        # Também detecta inversão de sinal no beta
        if 50 in result.betas:
            bs = result.betas[50]
            if len(bs) >= 10:
                recent_sign = np.sign(bs.iloc[-1])
                past_sign = np.sign(bs.iloc[-10])
                if recent_sign != past_sign and recent_sign != 0 and past_sign != 0:
                    result.regime_change_signal = True

        logger.debug(
            f"Beta {pair_id}: "
            + " | ".join(
                f"W{w}={result.current.get(w, float('nan')):.4f}"
                for w in self.windows
            )
            + f" | stability={result.stability:.2f}"
            + (f" | ⚠ REGIME_CHANGE" if result.regime_change_signal else "")
        )

        return result

    def calculate_from_prices(
        self,
        prices_a: pd.Series,
        prices_b: pd.Series,
        pair_id: str = "A↔B",
    ) -> BetaResult:
        """Calcula beta a partir de preços."""
        returns_a = np.log(prices_a / prices_a.shift(1)).dropna()
        returns_b = np.log(prices_b / prices_b.shift(1)).dropna()
        return self.calculate(returns_a, returns_b, pair_id)

    def calculate_batch(
        self,
        aligned_data: pd.DataFrame,
        pairs: List[Tuple[str, str]],
    ) -> Dict[str, BetaResult]:
        """Calcula beta para múltiplos pares."""
        results = {}

        for sym_a, sym_b in pairs:
            col_a = f"returns_{sym_a}"
            col_b = f"returns_{sym_b}"

            if col_a not in aligned_data.columns or col_b not in aligned_data.columns:
                continue

            pair_id = f"{sym_a}↔{sym_b}"
            result = self.calculate(
                aligned_data[col_a], aligned_data[col_b], pair_id=pair_id
            )
            results[pair_id] = result

        logger.info(f"Batch Beta: {len(results)} pares calculados")
        return results
