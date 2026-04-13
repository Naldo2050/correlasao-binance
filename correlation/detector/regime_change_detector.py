"""
CORR-WATCH System v2.0 — Detector de Mudança de Regime de Correlação
======================================================================
Identifica quando o regime de correlação entre pares está mudando,
permitindo ajuste proativo de estratégias e thresholds.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.6

Regimes detectados:
  - STABLE: Correlação estável, dentro do esperado
  - STRENGTHENING: Correlação ficando mais forte
  - WEAKENING: Correlação enfraquecendo
  - INVERTING: Correlação invertendo sinal
  - DECOUPLING: Pares se descorrelando (→ 0)
  - CRISIS: Correlações extremas/instáveis
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger("corr_watch.detector.regime_change")


class CorrelationRegime(Enum):
    """Regime de correlação entre um par."""
    STABLE = "STABLE"               # Sem mudança significativa
    STRENGTHENING = "STRENGTHENING" # Correlação ficando mais forte
    WEAKENING = "WEAKENING"         # Correlação enfraquecendo
    INVERTING = "INVERTING"         # Sinal da correlação invertendo
    DECOUPLING = "DECOUPLING"       # Convergindo para zero
    CRISIS = "CRISIS"               # Instabilidade extrema


@dataclass
class RegimeChangeEvent:
    """Evento de mudança de regime detectado."""
    pair_id: str
    previous_regime: CorrelationRegime
    current_regime: CorrelationRegime
    confidence: float      # 0-1, quão confiante é a detecção
    description: str
    evidence: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_significant(self) -> bool:
        return self.confidence >= 0.6

    def __str__(self) -> str:
        return (
            f"🔄 {self.pair_id}: {self.previous_regime.value} → "
            f"{self.current_regime.value} (conf={self.confidence:.0%}) — "
            f"{self.description}"
        )


class RegimeChangeDetector:
    """
    Detecta mudanças de regime de correlação entre pares.

    Indicadores analisados:
      1. Tendência da correlação (últimos N períodos)
      2. Velocidade de mudança (ΔCorr)
      3. Volatilidade da correlação (σ)
      4. Sinal do beta (inversão)
      5. Comparação curto vs longo prazo

    Uso:
        detector = RegimeChangeDetector()
        events = detector.detect(
            pair_id="BTC↔ETH",
            pearson_result=pearson,
            beta_result=beta,
            expected_correlation=0.80,
        )
        for event in events:
            print(event)
    """

    def __init__(
        self,
        trend_window: int = 10,
        delta_threshold: float = 0.15,
        volatility_threshold: float = 0.20,
        inversion_lookback: int = 20,
    ):
        self.trend_window = trend_window
        self.delta_threshold = delta_threshold
        self.volatility_threshold = volatility_threshold
        self.inversion_lookback = inversion_lookback

        # Histórico de regimes para tracking
        self._regime_history: Dict[str, List[CorrelationRegime]] = {}

    def detect(
        self,
        pair_id: str,
        pearson_result=None,
        beta_result=None,
        expected_correlation: float = 0.0,
    ) -> List[RegimeChangeEvent]:
        """
        Detecta mudanças de regime para um par.

        Returns:
            Lista de RegimeChangeEvent (pode ser vazia se estável)
        """
        events = []
        current_regime = CorrelationRegime.STABLE
        confidence = 0.0
        evidence = {}

        if pearson_result is None:
            return events

        # Seleciona janela principal (50 ou a menor disponível)
        main_window = 50 if 50 in pearson_result.correlations else (
            min(pearson_result.correlations.keys())
            if pearson_result.correlations else None
        )

        if main_window is None:
            return events

        corr_series = pearson_result.correlations[main_window]
        if len(corr_series) < self.trend_window:
            return events

        current_corr = pearson_result.current.get(main_window, 0)
        delta = pearson_result.delta.get(main_window, 0)

        # ─────────────────────────────────────────
        # 1. Análise de TENDÊNCIA
        # ─────────────────────────────────────────
        recent = corr_series.iloc[-self.trend_window:]
        trend_slope = self._calculate_trend(recent)
        evidence["trend_slope"] = trend_slope

        # ─────────────────────────────────────────
        # 2. Análise de VOLATILIDADE da correlação
        # ─────────────────────────────────────────
        corr_std = recent.std()
        evidence["correlation_volatility"] = float(corr_std)

        # ─────────────────────────────────────────
        # 3. Comparação curto vs longo prazo
        # ─────────────────────────────────────────
        short_corr = pearson_result.current.get(20)
        long_corr = pearson_result.current.get(100)

        if short_corr is not None and long_corr is not None:
            short_long_diff = short_corr - long_corr
            evidence["short_long_diff"] = short_long_diff
        else:
            short_long_diff = 0.0

        # ─────────────────────────────────────────
        # 4. DETECTA REGIME
        # ─────────────────────────────────────────

        # CRISIS: volatilidade de correlação muito alta
        if corr_std > self.volatility_threshold:
            current_regime = CorrelationRegime.CRISIS
            confidence = min(1.0, corr_std / self.volatility_threshold * 0.7)
            description = (
                f"Correlação instável: σ={corr_std:.4f} "
                f"(threshold={self.volatility_threshold})"
            )

        # INVERTING: sinal da correlação mudando
        elif self._is_inverting(corr_series):
            current_regime = CorrelationRegime.INVERTING
            confidence = 0.8
            description = (
                f"Correlação invertendo sinal: {current_corr:+.4f} "
                f"(esperado ~{expected_correlation:+.2f})"
            )

        # DECOUPLING: correlação convergindo para zero
        elif abs(current_corr) < 0.20 and abs(expected_correlation) > 0.40:
            current_regime = CorrelationRegime.DECOUPLING
            confidence = 1.0 - abs(current_corr) / abs(expected_correlation)
            description = (
                f"Pares descorrelando: {current_corr:+.4f} "
                f"(esperado ~{expected_correlation:+.2f})"
            )

        # STRENGTHENING: correlação ficando mais forte
        elif trend_slope > 0.003 and abs(delta) > self.delta_threshold * 0.5:
            if expected_correlation > 0:
                if current_corr > expected_correlation:
                    current_regime = CorrelationRegime.STRENGTHENING
                else:
                    current_regime = CorrelationRegime.WEAKENING
            else:
                if current_corr < expected_correlation:
                    current_regime = CorrelationRegime.STRENGTHENING
                else:
                    current_regime = CorrelationRegime.WEAKENING

            confidence = min(1.0, abs(delta) / self.delta_threshold)
            direction = "fortalecendo" if current_regime == CorrelationRegime.STRENGTHENING else "enfraquecendo"
            description = f"Correlação {direction}: Δ={delta:+.4f}, tendência={trend_slope:+.6f}"

        # WEAKENING via short vs long divergence
        elif abs(short_long_diff) > 0.15 and short_long_diff * expected_correlation < 0:
            current_regime = CorrelationRegime.WEAKENING
            confidence = min(1.0, abs(short_long_diff) / 0.30)
            description = (
                f"Divergência curto/longo: short={short_corr:+.4f} "
                f"vs long={long_corr:+.4f}"
            )

        else:
            # STABLE
            current_regime = CorrelationRegime.STABLE
            confidence = 1.0 - min(1.0, abs(delta) / self.delta_threshold)
            description = f"Regime estável: corr={current_corr:+.4f}"

        # ─────────────────────────────────────────
        # 5. Verifica se houve MUDANÇA de regime
        # ─────────────────────────────────────────
        previous_regime = self._get_previous_regime(pair_id)

        if current_regime != previous_regime and current_regime != CorrelationRegime.STABLE:
            event = RegimeChangeEvent(
                pair_id=pair_id,
                previous_regime=previous_regime,
                current_regime=current_regime,
                confidence=confidence,
                description=description,
                evidence=evidence,
            )
            events.append(event)

        # Atualiza histórico
        self._update_history(pair_id, current_regime)

        if events:
            logger.info(f"Regime {pair_id}: {events[0]}")

        return events

    def detect_batch(
        self,
        pairs_data: Dict[str, dict],
    ) -> Dict[str, List[RegimeChangeEvent]]:
        """
        Detecta mudanças de regime em batch.

        Args:
            pairs_data: Dict[pair_id, dict] com:
                pearson, beta, expected_correlation
        """
        all_events = {}

        for pair_id, data in pairs_data.items():
            events = self.detect(
                pair_id=pair_id,
                pearson_result=data.get("pearson"),
                beta_result=data.get("beta"),
                expected_correlation=data.get("expected_correlation", 0.0),
            )
            if events:
                all_events[pair_id] = events

        return all_events

    def get_current_regime(self, pair_id: str) -> CorrelationRegime:
        """Retorna o regime atual de um par."""
        return self._get_previous_regime(pair_id)

    # ────────────────────────────────────────────────────────────────
    # INTERNOS
    # ────────────────────────────────────────────────────────────────

    def _calculate_trend(self, series: pd.Series) -> float:
        """Calcula slope linear da série (regressão simples)."""
        if len(series) < 3:
            return 0.0
        x = np.arange(len(series))
        y = series.values

        # Ignora NaN
        mask = ~np.isnan(y)
        if mask.sum() < 3:
            return 0.0

        coeffs = np.polyfit(x[mask], y[mask], 1)
        return float(coeffs[0])  # slope

    def _is_inverting(self, corr_series: pd.Series) -> bool:
        """Detecta se a correlação está invertendo sinal."""
        if len(corr_series) < self.inversion_lookback:
            return False

        # Sinal nos primeiros vs últimos N/2 períodos
        half = self.inversion_lookback // 2
        old_mean = corr_series.iloc[-self.inversion_lookback:-half].mean()
        new_mean = corr_series.iloc[-half:].mean()

        # Inversão: sinais diferentes
        return np.sign(old_mean) != np.sign(new_mean) and (
            abs(old_mean) > 0.15 and abs(new_mean) > 0.15
        )

    def _get_previous_regime(self, pair_id: str) -> CorrelationRegime:
        """Retorna o último regime conhecido."""
        history = self._regime_history.get(pair_id, [])
        return history[-1] if history else CorrelationRegime.STABLE

    def _update_history(self, pair_id: str, regime: CorrelationRegime) -> None:
        """Atualiza histórico de regimes."""
        if pair_id not in self._regime_history:
            self._regime_history[pair_id] = []

        history = self._regime_history[pair_id]
        history.append(regime)

        # Mantém últimos 100 estados
        if len(history) > 100:
            self._regime_history[pair_id] = history[-100:]
