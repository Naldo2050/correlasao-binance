"""
CORR-WATCH System v2.0 — Detector de Anomalias de Correlação
==============================================================
Detecta desvios significativos no padrão de correlação entre pares.
Identifica quando a relação entre ativos sai do comportamento
esperado, sinalizando oportunidade ou risco.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.4

Tipos de anomalia detectados:
  1. CORRELATION_DEVIATION: Correlação desviou >2σ da média histórica
  2. SPREAD_EXTREME: Z-Score do spread ultrapassou threshold
  3. RAPID_CHANGE: Correlação mudou rapidamente (ΔCorr > 0.15 em 5p)
  4. COINTEGRATION_BREAK: Par perdeu cointegração
  5. BETA_INVERSION: Beta inverteu sinal (regime change)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from correlation.config import ThresholdConfig

logger = logging.getLogger("corr_watch.detector.anomaly")


class AnomalyType(Enum):
    """Tipos de anomalia de correlação."""
    CORRELATION_DEVIATION = "CORRELATION_DEVIATION"
    SPREAD_EXTREME = "SPREAD_EXTREME"
    RAPID_CHANGE = "RAPID_CHANGE"
    COINTEGRATION_BREAK = "COINTEGRATION_BREAK"
    BETA_INVERSION = "BETA_INVERSION"
    PEARSON_SPEARMAN_DIVERGENCE = "PEARSON_SPEARMAN_DIVERGENCE"


class AnomalySeverity(Enum):
    """Severidade da anomalia."""
    LOW = "LOW"           # Monitorar
    MEDIUM = "MEDIUM"     # Atenção
    HIGH = "HIGH"         # Alerta
    CRITICAL = "CRITICAL" # Ação imediata


@dataclass
class Anomaly:
    """Uma anomalia detectada."""
    pair_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    value: float             # Valor que causou a anomalia
    threshold: float         # Threshold que foi ultrapassado
    deviation_sigma: float   # Desvio em sigmas
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)

    @property
    def severity_icon(self) -> str:
        return {
            AnomalySeverity.LOW: "🟡",
            AnomalySeverity.MEDIUM: "🟠",
            AnomalySeverity.HIGH: "🔴",
            AnomalySeverity.CRITICAL: "⚡",
        }.get(self.severity, "❓")

    def __str__(self) -> str:
        return (
            f"{self.severity_icon} [{self.severity.value}] {self.pair_id}: "
            f"{self.anomaly_type.value} — {self.description} "
            f"(val={self.value:.4f}, σ={self.deviation_sigma:.1f})"
        )


class AnomalyDetector:
    """
    Detector de anomalias de correlação multi-critério.

    Analisa resultados de Pearson, Spearman, Spread, Beta e
    Cointegração para identificar desvios do comportamento normal.

    Pipeline de detecção:
      1. Verifica desvio de correlação vs média histórica
      2. Verifica Z-Score do spread vs thresholds
      3. Verifica velocidade de mudança (ΔCorr)
      4. Verifica quebra de cointegração
      5. Verifica inversão de beta
      6. Verifica divergência Pearson↔Spearman

    Uso:
        detector = AnomalyDetector(thresholds)
        anomalies = detector.detect_all(
            pair_id="BTC↔ETH",
            pearson_result=pearson,
            spread_result=spread,
            coint_result=coint,
            beta_result=beta,
            spearman_result=spearman,
            expected_correlation=0.80,
        )
        for a in anomalies:
            print(a)
    """

    def __init__(self, thresholds: Optional[ThresholdConfig] = None):
        self.thresholds = thresholds or ThresholdConfig()

    def detect_all(
        self,
        pair_id: str,
        expected_correlation: float = 0.0,
        pearson_result=None,
        spread_result=None,
        coint_result=None,
        beta_result=None,
        spearman_result=None,
    ) -> List[Anomaly]:
        """
        Executa todas as detecções de anomalia para um par.

        Returns:
            Lista de Anomaly detectadas (pode ser vazia)
        """
        anomalies = []

        if pearson_result:
            anomalies.extend(
                self._detect_correlation_deviation(
                    pair_id, pearson_result, expected_correlation
                )
            )
            anomalies.extend(
                self._detect_rapid_change(pair_id, pearson_result)
            )

        if spread_result:
            anomalies.extend(
                self._detect_spread_extreme(pair_id, spread_result)
            )

        if coint_result:
            anomalies.extend(
                self._detect_cointegration_break(pair_id, coint_result)
            )

        if beta_result:
            anomalies.extend(
                self._detect_beta_inversion(pair_id, beta_result)
            )

        if pearson_result and spearman_result:
            anomalies.extend(
                self._detect_pearson_spearman_divergence(
                    pair_id, pearson_result, spearman_result
                )
            )

        if anomalies:
            logger.info(
                f"Anomalias {pair_id}: {len(anomalies)} detectadas — "
                + ", ".join(a.anomaly_type.value for a in anomalies)
            )

        return anomalies

    def detect_batch(
        self,
        pairs_data: Dict[str, dict],
    ) -> Dict[str, List[Anomaly]]:
        """
        Detecta anomalias em batch para múltiplos pares.

        Args:
            pairs_data: Dict[pair_id, dict] com chaves:
                pearson, spread, coint, beta, spearman, expected_correlation
        """
        all_anomalies = {}

        for pair_id, data in pairs_data.items():
            anomalies = self.detect_all(
                pair_id=pair_id,
                expected_correlation=data.get("expected_correlation", 0.0),
                pearson_result=data.get("pearson"),
                spread_result=data.get("spread"),
                coint_result=data.get("coint"),
                beta_result=data.get("beta"),
                spearman_result=data.get("spearman"),
            )
            if anomalies:
                all_anomalies[pair_id] = anomalies

        total = sum(len(a) for a in all_anomalies.values())
        logger.info(f"Batch Anomalia: {total} anomalias em {len(all_anomalies)} pares")
        return all_anomalies

    # ────────────────────────────────────────────────────────────────
    # DETECTORES INDIVIDUAIS
    # ────────────────────────────────────────────────────────────────

    def _detect_correlation_deviation(
        self, pair_id: str, pearson, expected: float
    ) -> List[Anomaly]:
        """Detecta desvio da correlação vs valor esperado/histórico."""
        anomalies = []

        for window in [20, 50, 100]:
            current = pearson.current.get(window)
            std = pearson.std.get(window)

            if current is None or std is None or std == 0:
                continue

            mean = pearson.mean.get(window, expected)
            deviation = abs(current - expected)
            sigma = deviation / max(std, 0.01)

            if deviation >= self.thresholds.correlation_deviation_critical:
                anomalies.append(Anomaly(
                    pair_id=pair_id,
                    anomaly_type=AnomalyType.CORRELATION_DEVIATION,
                    severity=AnomalySeverity.HIGH if sigma > 2.5 else AnomalySeverity.MEDIUM,
                    description=(
                        f"Correlação W{window} desviou {deviation:.3f} do esperado "
                        f"({current:.4f} vs esperado {expected:.2f})"
                    ),
                    value=current,
                    threshold=expected,
                    deviation_sigma=sigma,
                    metadata={"window": window, "expected": expected, "mean": mean},
                ))
            elif deviation >= self.thresholds.correlation_deviation_alert:
                anomalies.append(Anomaly(
                    pair_id=pair_id,
                    anomaly_type=AnomalyType.CORRELATION_DEVIATION,
                    severity=AnomalySeverity.LOW,
                    description=f"Correlação W{window}: {current:.4f} (esperado ~{expected:.2f})",
                    value=current,
                    threshold=expected,
                    deviation_sigma=sigma,
                    metadata={"window": window},
                ))

        return anomalies

    def _detect_spread_extreme(
        self, pair_id: str, spread
    ) -> List[Anomaly]:
        """Detecta Z-Score do spread em zona extrema."""
        anomalies = []

        if spread.z_score_series is None:
            return anomalies

        z = abs(spread.z_score_current)

        if z >= self.thresholds.z_score_anomaly:
            anomalies.append(Anomaly(
                pair_id=pair_id,
                anomaly_type=AnomalyType.SPREAD_EXTREME,
                severity=AnomalySeverity.CRITICAL,
                description=(
                    f"Z-Score ANOMALIA: {spread.z_score_current:+.2f} "
                    f"(>{self.thresholds.z_score_anomaly})"
                ),
                value=spread.z_score_current,
                threshold=self.thresholds.z_score_anomaly,
                deviation_sigma=z,
                metadata={"zone": spread.zone.value, "half_life": spread.half_life},
            ))
        elif z >= self.thresholds.z_score_critical:
            anomalies.append(Anomaly(
                pair_id=pair_id,
                anomaly_type=AnomalyType.SPREAD_EXTREME,
                severity=AnomalySeverity.HIGH,
                description=f"Z-Score CRÍTICO: {spread.z_score_current:+.2f}",
                value=spread.z_score_current,
                threshold=self.thresholds.z_score_critical,
                deviation_sigma=z,
                metadata={"zone": spread.zone.value},
            ))
        elif z >= self.thresholds.z_score_alert:
            anomalies.append(Anomaly(
                pair_id=pair_id,
                anomaly_type=AnomalyType.SPREAD_EXTREME,
                severity=AnomalySeverity.MEDIUM,
                description=f"Z-Score em zona de alerta: {spread.z_score_current:+.2f}",
                value=spread.z_score_current,
                threshold=self.thresholds.z_score_alert,
                deviation_sigma=z,
            ))

        return anomalies

    def _detect_rapid_change(
        self, pair_id: str, pearson
    ) -> List[Anomaly]:
        """Detecta mudança rápida de correlação (ΔCorr > threshold)."""
        anomalies = []

        for window in [20, 50]:
            delta = pearson.delta.get(window)
            if delta is None:
                continue

            abs_delta = abs(delta)

            if abs_delta >= self.thresholds.delta_correlation_critical:
                anomalies.append(Anomaly(
                    pair_id=pair_id,
                    anomaly_type=AnomalyType.RAPID_CHANGE,
                    severity=AnomalySeverity.HIGH,
                    description=(
                        f"Mudança rápida W{window}: ΔCorr={delta:+.4f} em 5 períodos"
                    ),
                    value=delta,
                    threshold=self.thresholds.delta_correlation_critical,
                    deviation_sigma=abs_delta / max(self.thresholds.delta_correlation_alert, 0.01),
                    metadata={"window": window},
                ))
            elif abs_delta >= self.thresholds.delta_correlation_alert:
                anomalies.append(Anomaly(
                    pair_id=pair_id,
                    anomaly_type=AnomalyType.RAPID_CHANGE,
                    severity=AnomalySeverity.MEDIUM,
                    description=f"Correlação mudando W{window}: ΔCorr={delta:+.4f}",
                    value=delta,
                    threshold=self.thresholds.delta_correlation_alert,
                    deviation_sigma=abs_delta / max(self.thresholds.delta_correlation_alert, 0.01),
                ))

        return anomalies

    def _detect_cointegration_break(
        self, pair_id: str, coint
    ) -> List[Anomaly]:
        """Detecta perda de cointegração."""
        anomalies = []

        if coint.status.value == "NOT_COINTEGRATED":
            anomalies.append(Anomaly(
                pair_id=pair_id,
                anomaly_type=AnomalyType.COINTEGRATION_BREAK,
                severity=AnomalySeverity.HIGH,
                description=(
                    f"Par NÃO cointegrado: p={coint.engle_granger_pvalue:.4f} "
                    f"(threshold={self.thresholds.cointegration_pvalue_max})"
                ),
                value=coint.engle_granger_pvalue,
                threshold=self.thresholds.cointegration_pvalue_max,
                deviation_sigma=0.0,
                metadata={
                    "hedge_ratio": coint.hedge_ratio,
                    "half_life": coint.half_life,
                },
            ))
        elif coint.status.value == "MARGINAL":
            anomalies.append(Anomaly(
                pair_id=pair_id,
                anomaly_type=AnomalyType.COINTEGRATION_BREAK,
                severity=AnomalySeverity.MEDIUM,
                description=f"Cointegração MARGINAL: p={coint.engle_granger_pvalue:.4f}",
                value=coint.engle_granger_pvalue,
                threshold=self.thresholds.cointegration_pvalue_max,
                deviation_sigma=0.0,
            ))

        # Half-life muito alto
        if (
            coint.half_life is not None
            and coint.half_life > self.thresholds.halflife_max_periods
        ):
            anomalies.append(Anomaly(
                pair_id=pair_id,
                anomaly_type=AnomalyType.COINTEGRATION_BREAK,
                severity=AnomalySeverity.MEDIUM,
                description=(
                    f"Half-life muito alto: {coint.half_life:.0f} períodos "
                    f"(max={self.thresholds.halflife_max_periods})"
                ),
                value=coint.half_life,
                threshold=float(self.thresholds.halflife_max_periods),
                deviation_sigma=0.0,
            ))

        return anomalies

    def _detect_beta_inversion(
        self, pair_id: str, beta
    ) -> List[Anomaly]:
        """Detecta inversão de beta (mudança de regime)."""
        anomalies = []

        if beta.regime_change_signal:
            current_beta = beta.current.get(50, beta.current.get(20, 0))
            anomalies.append(Anomaly(
                pair_id=pair_id,
                anomaly_type=AnomalyType.BETA_INVERSION,
                severity=AnomalySeverity.HIGH,
                description=(
                    f"Sinal de REGIME CHANGE: β={current_beta:.4f}, "
                    f"estabilidade={beta.stability:.2f}"
                ),
                value=current_beta,
                threshold=0.0,
                deviation_sigma=0.0,
                metadata={"stability": beta.stability},
            ))

        return anomalies

    def _detect_pearson_spearman_divergence(
        self, pair_id: str, pearson, spearman
    ) -> List[Anomaly]:
        """
        Detecta divergência entre Pearson e Spearman.
        Indica possível relação não-linear ou manipulação.
        """
        anomalies = []

        for window in spearman.pearson_divergence:
            div = spearman.pearson_divergence[window]
            if abs(div) > 0.15:
                anomalies.append(Anomaly(
                    pair_id=pair_id,
                    anomaly_type=AnomalyType.PEARSON_SPEARMAN_DIVERGENCE,
                    severity=AnomalySeverity.MEDIUM,
                    description=(
                        f"Divergência Pearson↔Spearman W{window}: "
                        f"Δ={div:+.4f} (possível não-linearidade)"
                    ),
                    value=div,
                    threshold=0.15,
                    deviation_sigma=abs(div) / 0.15,
                    metadata={
                        "pearson": pearson.current.get(window),
                        "spearman": spearman.current.get(window),
                    },
                ))

        return anomalies
