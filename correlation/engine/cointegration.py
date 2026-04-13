"""
CORR-WATCH System v2.0 — Teste de Cointegração
=================================================
Testa se dois ativos compartilham tendência de longo prazo
(cointegração), validando a viabilidade de pair trading.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.1, item 5

Métodos implementados:
  1. Engle-Granger (two-step): regressão + ADF nos resíduos
  2. ADF direto no spread (complementar)

Interpretação:
  p-value < 0.05  → Cointegrados (pair trading viável) ✅
  p-value 0.05-0.10 → Marginal (cautela) ⚠
  p-value > 0.10  → Não cointegrados (mean reversion arriscado) ❌
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint

logger = logging.getLogger("corr_watch.engine.cointegration")


class CointegrationStatus(Enum):
    """Status de cointegração do par."""
    COINTEGRATED = "COINTEGRATED"         # p < 0.05 — pair trading viável
    MARGINAL = "MARGINAL"                 # 0.05 ≤ p < 0.10 — cautela
    NOT_COINTEGRATED = "NOT_COINTEGRATED" # p ≥ 0.10 — mean reversion arriscado
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    ERROR = "ERROR"


@dataclass
class CointegrationResult:
    """
    Resultado do teste de cointegração para um par.

    Campos:
      - pair_id: Identificador do par
      - engle_granger_pvalue: p-value do teste Engle-Granger
      - engle_granger_stat: Estatística do teste
      - adf_spread_pvalue: p-value do ADF direto no spread
      - adf_spread_stat: Estatística ADF
      - critical_values: Valores críticos do teste
      - status: Classificação (COINTEGRATED, MARGINAL, NOT_COINTEGRATED)
      - hedge_ratio: β estimado da regressão de cointegração
      - half_life: Half-life estimado a partir dos resíduos
    """
    pair_id: str
    engle_granger_pvalue: float = 1.0
    engle_granger_stat: float = 0.0
    adf_spread_pvalue: float = 1.0
    adf_spread_stat: float = 0.0
    critical_values: Dict[str, float] = None
    status: CointegrationStatus = CointegrationStatus.INSUFFICIENT_DATA
    hedge_ratio: float = 1.0
    half_life: Optional[float] = None
    residuals: Optional[pd.Series] = None

    def __post_init__(self):
        if self.critical_values is None:
            self.critical_values = {}

    @property
    def is_cointegrated(self) -> bool:
        return self.status == CointegrationStatus.COINTEGRATED

    @property
    def is_tradeable(self) -> bool:
        """Par é operável (cointegrado ou marginal com cautela)."""
        return self.status in (
            CointegrationStatus.COINTEGRATED,
            CointegrationStatus.MARGINAL,
        )

    @property
    def status_icon(self) -> str:
        icons = {
            CointegrationStatus.COINTEGRATED: "✅",
            CointegrationStatus.MARGINAL: "⚠️",
            CointegrationStatus.NOT_COINTEGRATED: "❌",
            CointegrationStatus.INSUFFICIENT_DATA: "❓",
            CointegrationStatus.ERROR: "💥",
        }
        return icons.get(self.status, "❓")


class CointegrationTester:
    """
    Testador de Cointegração entre pares de ativos.

    Verifica se dois ativos compartilham uma tendência de longo prazo,
    o que é pré-requisito para estratégias de mean reversion / pair trading.

    Métodos:
      1. Engle-Granger: Regressão OLS + ADF nos resíduos
         - Mais robusto e padrão da indústria
         - Fornece hedge ratio diretamente

      2. ADF no Spread: Testa estacionariedade do spread diretamente
         - Mais simples, confirma resultado do Engle-Granger

    Uso:
        tester = CointegrationTester()
        result = tester.test(prices_btc, prices_eth, pair_id="BTC↔ETH")
        print(f"Status: {result.status.value} (p={result.engle_granger_pvalue:.4f})")
        print(f"Hedge ratio: {result.hedge_ratio:.4f}")
    """

    # Thresholds de p-value
    PVALUE_COINTEGRATED = 0.05
    PVALUE_MARGINAL = 0.10

    # Mínimo de observações para teste confiável
    MIN_OBSERVATIONS = 60

    def test(
        self,
        prices_a: pd.Series,
        prices_b: pd.Series,
        pair_id: str = "A↔B",
    ) -> CointegrationResult:
        """
        Executa teste completo de cointegração.

        Args:
            prices_a: Série de preços do ativo A
            prices_b: Série de preços do ativo B
            pair_id: Identificador do par

        Returns:
            CointegrationResult com p-values, status, hedge ratio
        """
        if prices_a is None or prices_b is None:
            return CointegrationResult(pair_id=pair_id)

        # Alinha e limpa
        combined = pd.DataFrame({"a": prices_a, "b": prices_b}).dropna()

        if len(combined) < self.MIN_OBSERVATIONS:
            logger.warning(
                f"Dados insuficientes para cointegração {pair_id}: "
                f"{len(combined)} < {self.MIN_OBSERVATIONS}"
            )
            return CointegrationResult(
                pair_id=pair_id,
                status=CointegrationStatus.INSUFFICIENT_DATA,
            )

        try:
            # 1. Teste Engle-Granger via statsmodels.coint
            eg_stat, eg_pvalue, eg_crit = coint(
                combined["a"], combined["b"], trend="c"
            )

            # 2. Estima hedge ratio via OLS
            log_a = np.log(combined["a"])
            log_b = np.log(combined["b"])
            beta = self._estimate_hedge_ratio(log_a, log_b)

            # 3. Calcula resíduos (spread cointegrado)
            residuals = log_a - beta * log_b
            residuals = residuals - residuals.mean()  # demeaning

            # 4. ADF nos resíduos para confirmação
            adf_result = adfuller(residuals, maxlag=None, autolag="AIC")
            adf_stat = float(adf_result[0])
            adf_pvalue = float(adf_result[1])
            adf_crit = {k: float(v) for k, v in adf_result[4].items()}

            # 5. Half-life dos resíduos
            half_life = self._calculate_half_life(residuals)

            # 6. Classificação
            # Usa o menor p-value entre EG e ADF como decisão final
            best_pvalue = min(eg_pvalue, adf_pvalue)
            status = self._classify(best_pvalue)

            result = CointegrationResult(
                pair_id=pair_id,
                engle_granger_pvalue=float(eg_pvalue),
                engle_granger_stat=float(eg_stat),
                adf_spread_pvalue=adf_pvalue,
                adf_spread_stat=adf_stat,
                critical_values=adf_crit,
                status=status,
                hedge_ratio=beta,
                half_life=half_life,
                residuals=residuals,
            )

            logger.debug(
                f"Cointegração {pair_id}: EG p={eg_pvalue:.4f} | "
                f"ADF p={adf_pvalue:.4f} | β={beta:.4f} | "
                f"HL={half_life:.1f} | {status.value}"
            )

            return result

        except Exception as e:
            logger.error(f"Erro no teste de cointegração {pair_id}: {e}")
            return CointegrationResult(
                pair_id=pair_id,
                status=CointegrationStatus.ERROR,
            )

    def test_from_aligned(
        self,
        aligned_data: pd.DataFrame,
        symbol_a: str,
        symbol_b: str,
    ) -> CointegrationResult:
        """Testa cointegração a partir de dados alinhados."""
        close_a = f"close_{symbol_a}"
        close_b = f"close_{symbol_b}"

        if close_a not in aligned_data.columns or close_b not in aligned_data.columns:
            return CointegrationResult(pair_id=f"{symbol_a}↔{symbol_b}")

        return self.test(
            aligned_data[close_a],
            aligned_data[close_b],
            pair_id=f"{symbol_a}↔{symbol_b}",
        )

    def test_batch(
        self,
        aligned_data: pd.DataFrame,
        pairs: List[Tuple[str, str]],
    ) -> Dict[str, CointegrationResult]:
        """Testa cointegração para múltiplos pares."""
        results = {}

        for sym_a, sym_b in pairs:
            pair_id = f"{sym_a}↔{sym_b}"
            result = self.test_from_aligned(aligned_data, sym_a, sym_b)
            results[pair_id] = result

        n_coint = sum(1 for r in results.values() if r.is_cointegrated)
        logger.info(
            f"Batch Cointegração: {len(results)} pares testados, "
            f"{n_coint} cointegrados"
        )
        return results

    # ────────────────────────────────────────────────────────────────
    # INTERNOS
    # ────────────────────────────────────────────────────────────────

    def _estimate_hedge_ratio(
        self, log_a: pd.Series, log_b: pd.Series
    ) -> float:
        """Estima hedge ratio via OLS: ln(A) = β·ln(B) + c + ε."""
        cov = np.cov(log_a, log_b)
        if cov.shape == (2, 2) and cov[1, 1] != 0:
            return float(cov[0, 1] / cov[1, 1])
        return 1.0

    def _calculate_half_life(self, residuals: pd.Series) -> float:
        """
        Half-life de mean reversion dos resíduos.
        ΔR_t = θ·R_{t-1} + ε  →  HL = -ln(2)/θ
        """
        res = residuals.dropna()
        if len(res) < 20:
            return 999.0

        delta = res.diff().dropna()
        lagged = res.shift(1).dropna()

        common = delta.index.intersection(lagged.index)
        delta = delta.loc[common]
        lagged = lagged.loc[common]

        if len(delta) < 10:
            return 999.0

        num = (lagged * delta).sum()
        den = (lagged ** 2).sum()

        if den == 0:
            return 999.0

        theta = num / den
        if theta >= 0:
            return 999.0

        hl = -np.log(2) / theta
        return float(max(1.0, min(999.0, hl)))

    def _classify(self, pvalue: float) -> CointegrationStatus:
        """Classifica com base no p-value."""
        if pvalue < self.PVALUE_COINTEGRATED:
            return CointegrationStatus.COINTEGRATED
        elif pvalue < self.PVALUE_MARGINAL:
            return CointegrationStatus.MARGINAL
        else:
            return CointegrationStatus.NOT_COINTEGRATED
