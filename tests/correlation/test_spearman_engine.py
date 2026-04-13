"""
Testes Unitários — Motor de Correlação Spearman
================================================
Testa cálculos de Spearman, detecção de não-linearidade e p-values.
"""

import numpy as np
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.engine.spearman_engine import SpearmanEngine, SpearmanResult


def _make_nonlinear_series(n: int = 200, seed: int = 42) -> tuple:
    """Gera duas séries com relação exponencial perfeitamente monotônica."""
    np.random.seed(seed)
    
    # x uniforme entre 1 e 10
    returns_a = np.random.uniform(1, 10, n)
    # y é exponencial (monotônico, rank preservation) mas não linear
    returns_b = np.exp(returns_a) + np.random.randn(n) * 0.1
    
    idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    return (
        pd.Series(returns_a, index=idx),
        pd.Series(returns_b, index=idx),
    )


class TestSpearmanEngine:
    """Testes do motor Spearman."""

    def setup_method(self):
        self.engine = SpearmanEngine(windows=[20, 50])

    def test_nonlinear_correlation(self):
        """Spearman deve ser próximo de 1.0 para relação exponencial perfeitamente monotônica, Pearson seria menor."""
        returns_a, returns_b = _make_nonlinear_series(n=200)
        
        # Simula pearson baixo (diferença)
        pearson_mock = {50: 0.85}
        
        result = self.engine.calculate(
            returns_a, returns_b, pair_id="TEST", pearson_current=pearson_mock
        )
        
        assert isinstance(result, SpearmanResult)
        assert 50 in result.current
        
        # Spearman deve ser altíssimo pois a relação ranks é quase 1:1
        assert result.current[50] > 0.95
        
        # Deve ter calculado divergência
        assert 50 in result.pearson_divergence
        assert result.pearson_divergence[50] > 0.10
        
        assert result.has_nonlinearity is True

    def test_pvalue_significance(self):
        """Testa se p-value é pequeno para séries correlacionadas."""
        returns_a, returns_b = _make_nonlinear_series(n=200)
        
        result = self.engine.calculate(returns_a, returns_b)
        
        assert result.is_significant(50, alpha=0.01) is True
        assert result.pvalues[50] < 0.01

    def test_uncorrelated(self):
        """Testa com séries aleatórias."""
        np.random.seed(42)
        returns_a = pd.Series(np.random.randn(200))
        returns_b = pd.Series(np.random.randn(200))
        
        result = self.engine.calculate(returns_a, returns_b)
        
        assert abs(result.current[50]) < 0.3
        assert result.is_significant(50, alpha=0.05) is False

    def test_insufficient_data(self):
        """Testa com menos dados que a janela mínima."""
        returns_a = pd.Series(np.random.randn(10))
        returns_b = pd.Series(np.random.randn(10))
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="SHORT")
        assert result.pair_id == "SHORT"
        assert 50 not in result.current

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
