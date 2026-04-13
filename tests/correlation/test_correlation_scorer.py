"""
Testes Unitários — Correlation Scorer
======================================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.scoring.correlation_scorer import CorrelationScorer, CorrelationScore
from correlation.engine.pearson_engine import CorrelationResult
from correlation.engine.spearman_engine import SpearmanResult
from correlation.engine.beta_rolling import BetaResult
from correlation.engine.spread_analyzer import SpreadResult, SpreadZone
from correlation.engine.cointegration import CointegrationResult, CointegrationStatus
from correlation.detector.anomaly_detector import Anomaly, AnomalyType, AnomalySeverity
from correlation.detector.regime_change_detector import CorrelationRegime

class TestCorrelationScorer:
    def setup_method(self):
        self.scorer = CorrelationScorer()
        self.pearson = CorrelationResult("TEST")
        self.spearman = SpearmanResult("TEST")
        self.beta = BetaResult("TEST")
        self.spread = SpreadResult("TEST")
        self.coint = CointegrationResult("TEST")

    def test_ideal_scoring(self):
        """Um par idealmente cointegrado, sem anomalias, no spread."""
        self.coint.status = CointegrationStatus.COINTEGRATED
        self.coint.half_life = 20
        self.spread.zone = SpreadZone.HIGH_PROB
        
        score = self.scorer.evaluate(
            "TEST", 0.8, self.pearson, self.spearman, self.beta, 
            self.spread, self.coint, [], [], CorrelationRegime.STABLE
        )
        
        assert score.stability_score == 100.0
        # mr_score: coint(+50), hl<50 (+30), zone(+20) = 100
        assert score.mean_reversion_score == 100.0
        assert score.overall_score == 100.0
        assert score.is_tradable is True

    def test_decoupled_scoring(self):
        """Um par desencolante e sem cointegração."""
        self.coint.status = CointegrationStatus.NOT_COINTEGRATED
        self.spread.zone = SpreadZone.EQUILIBRIUM
        
        score = self.scorer.evaluate(
            "TEST", 0.8, self.pearson, self.spearman, self.beta, 
            self.spread, self.coint, [], [], CorrelationRegime.DECOUPLING
        )
        
        assert score.stability_score == 40.0  # -60 por DECOUPLING
        assert score.mean_reversion_score == 0.0
        assert score.overall_score == 16.0    # 40*0.4 + 0*0.6
        assert score.is_tradable is False

    def test_anomaly_penalty(self):
        """Anomalias críticas devem derrubar a estabilidade."""
        anomaly = Anomaly(
            pair_id="TEST", 
            anomaly_type=AnomalyType.SPREAD_EXTREME,
            severity=AnomalySeverity.CRITICAL,
            description="Z-Score Boom",
            value=4.0, threshold=3.0, deviation_sigma=4.0
        )
        # Seta a speaman com não-linear
        self.spearman.pearson_divergence[50] = 0.20
        
        score = self.scorer.evaluate(
            "TEST", 0.8, self.pearson, self.spearman, self.beta, 
            self.spread, self.coint, [anomaly], [], CorrelationRegime.STABLE
        )
        
        # -15 pela anomalia CRITICAL, -20 pela não linearidade
        assert score.stability_score == 65.0
        assert "NON_LINEAR" in score.warning_flags

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
