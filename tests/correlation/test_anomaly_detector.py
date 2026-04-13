"""
Testes Unitários — Detector de Anomalias
=========================================
"""

import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.detector.anomaly_detector import AnomalyDetector, AnomalyType, AnomalySeverity
from correlation.config import ThresholdConfig
from correlation.engine.pearson_engine import CorrelationResult
from correlation.engine.spread_analyzer import SpreadResult, SpreadZone
from correlation.engine.cointegration import CointegrationResult, CointegrationStatus

class TestAnomalyDetector:
    def setup_method(self):
        thresholds = ThresholdConfig(
            correlation_deviation_alert=0.20,
            correlation_deviation_critical=0.30,
            z_score_alert=2.0,
            z_score_critical=2.5,
            z_score_anomaly=3.0,
            cointegration_pvalue_max=0.10,
        )
        self.detector = AnomalyDetector(thresholds)

    def test_correlation_deviation(self):
        """Testa desvio da correlação Pearson vs valor esperado."""
        pearson = CorrelationResult(pair_id="TEST")
        # Valor 0.40, esperado 0.80 -> desvio = 0.40 (> 0.30)
        pearson.current[50] = 0.40
        pearson.std[50] = 0.05
        
        anomalies = self.detector.detect_all(
            "TEST", expected_correlation=0.80, pearson_result=pearson
        )
        
        assert len(anomalies) > 0
        anomaly = anomalies[0]
        assert anomaly.anomaly_type == AnomalyType.CORRELATION_DEVIATION
        
        # Sigma = desvio / std = 0.40 / 0.05 = 8.0 (> 2.5 -> HIGH)
        assert anomaly.severity == AnomalySeverity.HIGH

    def test_spread_extreme(self):
        """Testa captura de z-score extremo no spread."""
        spread = SpreadResult(pair_id="TEST")
        spread.z_score_series = pd.Series([1.0, 2.0, 3.2])
        spread.z_score_current = 3.2
        spread.zone = SpreadZone.ANOMALY
        
        anomalies = self.detector.detect_all("TEST", spread_result=spread)
        
        assert len(anomalies) > 0
        anomaly = anomalies[0]
        assert anomaly.anomaly_type == AnomalyType.SPREAD_EXTREME
        assert anomaly.severity == AnomalySeverity.CRITICAL

    def test_cointegration_break(self):
        """Testa alerta de quebra de cointegração."""
        coint = CointegrationResult(
            pair_id="TEST",
            engle_granger_pvalue=0.15,
            status=CointegrationStatus.NOT_COINTEGRATED,
        )
        
        anomalies = self.detector.detect_all("TEST", coint_result=coint)
        
        assert len(anomalies) > 0
        anomaly = anomalies[0]
        assert anomaly.anomaly_type == AnomalyType.COINTEGRATION_BREAK
        assert anomaly.severity == AnomalySeverity.HIGH

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
