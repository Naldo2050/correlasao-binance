"""
CORR-WATCH System v2.0 — Correlation Scorer e Extrator de Payload
==================================================================
Consolida os dados brutos de todos os motores analíticos em um
score único (0-100) e formata as informações num payload otimizado
para consumo por modelos de Inteligência Artificial (LLMs).

Referência: CORRELAÇÃO BINANCE(copia).md — Integração AI
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List

from correlation.engine.pearson_engine import CorrelationResult
from correlation.engine.spearman_engine import SpearmanResult
from correlation.engine.spread_analyzer import SpreadResult, SpreadZone
from correlation.engine.beta_rolling import BetaResult
from correlation.engine.cointegration import CointegrationResult, CointegrationStatus
from correlation.detector.anomaly_detector import Anomaly, AnomalySeverity
from correlation.detector.regime_change_detector import CorrelationRegime, RegimeChangeEvent

logger = logging.getLogger("corr_watch.scoring")


@dataclass
class CorrelationScore:
    """Consolidação da saúde e força da correlação de um par."""
    pair_id: str
    overall_score: float = 50.0       # 0 a 100
    stability_score: float = 50.0     # 0 a 100
    mean_reversion_score: float = 0.0 # 0 a 100
    is_tradable: bool = False
    warning_flags: List[str] = field(default_factory=list)


class CorrelationScorer:
    """
    Agregador que gera métricas unificadas e Payloads de IA.
    """

    def evaluate(
        self,
        pair_id: str,
        expected_correlation: float,
        pearson: CorrelationResult,
        spearman: SpearmanResult,
        beta: BetaResult,
        spread: SpreadResult,
        coint: CointegrationResult,
        anomalies: List[Anomaly],
        regime: List[RegimeChangeEvent],
        current_regime: CorrelationRegime,
    ) -> CorrelationScore:
        """
        Gera um score de viabilidade para trading de correlação.
        """
        score = CorrelationScore(pair_id=pair_id)

        # 1. Avaliação de Estabilidade (Stability Score)
        stability = 100.0
        if current_regime in (CorrelationRegime.CRISIS, CorrelationRegime.DECOUPLING):
            stability -= 60
        elif current_regime in (CorrelationRegime.INVERTING, CorrelationRegime.WEAKENING):
            stability -= 30
        
        if spearman and spearman.has_nonlinearity:
            stability -= 20
            score.warning_flags.append("NON_LINEAR")
            
        if beta and beta.regime_change_signal:
            stability -= 25
            score.warning_flags.append("BETA_INVERSION")
            
        stability -= len([a for a in anomalies if a.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL)]) * 15
        score.stability_score = max(0.0, min(100.0, stability))

        # 2. Avaliação de Mean Reversion (Para Pair Trading)
        mr_score = 0.0
        if coint and coint.is_cointegrated:
            mr_score += 50
            if coint.half_life and coint.half_life < 50:
                mr_score += 30  # Reversão rápida é bom
            elif coint.half_life and coint.half_life < 100:
                mr_score += 10
        elif coint and coint.status == CointegrationStatus.MARGINAL:
            mr_score += 30
        
        if spread and spread.zone in (SpreadZone.HIGH_PROB, SpreadZone.ANOMALY):
            mr_score += 20
            
        score.mean_reversion_score = max(0.0, min(100.0, mr_score))

        # 3. Overall Score
        score.overall_score = (score.stability_score * 0.4) + (score.mean_reversion_score * 0.6)
        
        # Define Tradabilidade
        if score.overall_score > 65 and score.stability_score > 40:
            score.is_tradable = True

        return score

    def build_ai_payload(
        self,
        pair_id: str,
        score: CorrelationScore,
        expected_correlation: float,
        pearson: CorrelationResult,
        spearman: SpearmanResult,
        beta: BetaResult,
        spread: SpreadResult,
        coint: CointegrationResult,
        anomalies: List[Anomaly],
        current_regime: CorrelationRegime,
    ) -> Dict[str, Any]:
        """
        Formata os dados técnicos em um JSON enxuto para envio à LLM.
        """
        payload = {
            "pair": pair_id,
            "system_scores": {
                "tradability_score": round(score.overall_score, 1),
                "stability_score": round(score.stability_score, 1),
                "mean_reversion_score": round(score.mean_reversion_score, 1),
                "is_tradable": score.is_tradable,
                "warnings": score.warning_flags,
            },
            "regime": {
                "current": current_regime.value,
                "expected_correlation": expected_correlation,
                "pearson_w50": round(pearson.current.get(50, 0), 4) if pearson else None,
                "spearman_w50": round(spearman.current.get(50, 0), 4) if spearman else None,
                "beta_w50": round(beta.current.get(50, 0), 4) if beta else None,
            },
            "mean_reversion": {
                "z_score": round(spread.z_score_current, 2) if spread else None,
                "spread_zone": spread.zone.value if spread else None,
                "is_cointegrated": coint.is_cointegrated if coint else False,
                "half_life": round(coint.half_life, 1) if coint and coint.half_life else None,
            },
            "anomalies": [
                {
                    "type": a.anomaly_type.value,
                    "severity": a.severity.value,
                    "value": round(a.value, 4)
                }
                for a in anomalies if a.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL)
            ]
        }
        return payload
