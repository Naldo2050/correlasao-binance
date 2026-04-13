"""
Testes Unitários — Detector de Mudança de Regime
=================================================
"""

import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.detector.regime_change_detector import CorrelationRegime, RegimeChangeDetector
from correlation.engine.pearson_engine import CorrelationResult
from correlation.engine.beta_rolling import BetaResult

class TestRegimeChangeDetector:
    def setup_method(self):
        self.detector = RegimeChangeDetector(
            trend_window=10,
            delta_threshold=0.15,
            volatility_threshold=0.20,
        )

    def _make_pearson_mock(self, corr_values: list, std: float = 0.05) -> CorrelationResult:
        result = CorrelationResult(pair_id="TEST")
        series = pd.Series(corr_values)
        result.correlations[50] = series
        result.current[50] = corr_values[-1]
        
        # Simula delta
        if len(corr_values) >= 5:
            result.delta[50] = corr_values[-1] - corr_values[-5]
        else:
            result.delta[50] = 0.0
            
        result.std[50] = std
        
        return result

    def test_stable_regime(self):
        """Correlação que flutua levemente é considerada STABLE."""
        corr_series = [0.80, 0.81, 0.79, 0.82, 0.80, 0.81, 0.79, 0.80, 0.81, 0.80]
        pearson = self._make_pearson_mock(corr_series)
        beta = BetaResult(pair_id="TEST")
        
        events = self.detector.detect("TEST", pearson, beta, expected_correlation=0.80)
        
        # Como o regime default ao iniciar é STABLE, e permanece STABLE, não deve emitir evento
        assert len(events) == 0
        assert self.detector.get_current_regime("TEST") == CorrelationRegime.STABLE

    def test_strengthening_regime(self):
        """Correlação se movendo forte na direção da correlação esperada."""
        # Esperado: 0.80, atual subindo rápido
        corr_series = [0.60, 0.62, 0.65, 0.68, 0.72, 0.75, 0.78, 0.81, 0.84, 0.86]
        pearson = self._make_pearson_mock(corr_series)
        
        # Δ atual (-1 a -5): 0.86 - 0.75 = 0.11
        # Com delta_threshold = 0.15 (0.5 * 0.15 = 0.075), deve disparar
        pearson.delta[50] = 0.86 - 0.75
        
        events = self.detector.detect("TEST", pearson, BetaResult("TEST"), expected_correlation=0.80)
        
        assert len(events) == 1
        assert events[0].current_regime == CorrelationRegime.STRENGTHENING

    def test_crisis_regime(self):
        """Correlação com volatilidade extrema."""
        # Oscilações extremas e aleatórias
        corr_series = [0.8, -0.2, 0.9, -0.8, 0.1, 0.7, -0.6, 0.9, -0.9, 0.5]
        pearson = self._make_pearson_mock(corr_series)
        # O mock usa o método std() da serie, que pra oscilar desse jeito será > 0.20
        
        events = self.detector.detect("TEST", pearson, BetaResult("TEST"), expected_correlation=0.80)
        
        assert len(events) == 1
        assert events[0].current_regime == CorrelationRegime.CRISIS

    def test_decoupling_regime(self):
        """Pares descolando e indo a zero."""
        corr_series = [0.30, 0.25, 0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.05, 0.01]
        pearson = self._make_pearson_mock(corr_series, std=0.10)
        
        events = self.detector.detect("TEST", pearson, BetaResult("TEST"), expected_correlation=0.80)
        
        assert len(events) == 1
        assert events[0].current_regime == CorrelationRegime.DECOUPLING

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
