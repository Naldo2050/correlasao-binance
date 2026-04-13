"""
Testes Unitários — Cointegração Engine
=======================================
"""

import numpy as np
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.engine.cointegration import CointegrationTester, CointegrationStatus

def _make_cointegrated_pair(n: int = 300, beta: float = 1.5, seed: int = 42) -> tuple:
    np.random.seed(seed)
    
    # Preço base (random walk)
    log_prices_b = np.cumsum(np.random.randn(n) * 0.01) + np.log(3000)
    
    # Spread mean-reverting
    spread = np.zeros(n)
    for i in range(1, n):
        spread[i] = 0.9 * spread[i-1] + np.random.randn() * 0.01
    
    # Preço A = beta * B + spread
    log_prices_a = beta * log_prices_b + spread + np.log(50000 / (3000 ** beta))
    
    idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    return (
        pd.Series(np.exp(log_prices_a), index=idx, name="price_A"),
        pd.Series(np.exp(log_prices_b), index=idx, name="price_B"),
    )

def _make_trending_pair(n: int = 300, seed: int = 42) -> tuple:
    np.random.seed(seed)
    idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    
    # Ambos sobem mas com caminhos diferentes (não cointegrados)
    prices_a = 50000 * np.exp(np.cumsum(np.random.randn(n) * 0.01 + 0.001))
    prices_b = 3000 * np.exp(np.cumsum(np.random.randn(n) * 0.01 + 0.002))
    
    return (
        pd.Series(prices_a, index=idx),
        pd.Series(prices_b, index=idx),
    )

class TestCointegrationTester:
    def setup_method(self):
        self.tester = CointegrationTester()

    def test_cointegrated_pair(self):
        """Um par cointegrado deve ter p-value baixo e status COINTEGRATED."""
        prices_a, prices_b = _make_cointegrated_pair(n=300, beta=1.2)
        
        result = self.tester.test(prices_a, prices_b, pair_id="COINT")
        
        assert result.status == CointegrationStatus.COINTEGRATED
        assert result.engle_granger_pvalue < 0.05
        assert result.is_cointegrated is True
        assert result.is_tradeable is True
        assert abs(result.hedge_ratio - 1.2) < 0.2

    def test_divergent_pair(self):
        """Um par divergente deve falhar no teste de cointegração."""
        prices_a, prices_b = _make_trending_pair(n=300)
        
        result = self.tester.test(prices_a, prices_b, pair_id="N_COINT")
        
        assert result.status == CointegrationStatus.NOT_COINTEGRATED
        assert result.engle_granger_pvalue > 0.10
        assert result.is_cointegrated is False

    def test_insufficient_data(self):
        """Deve retornar status especial se os dados forem curtos demais."""
        prices_a, prices_b = _make_cointegrated_pair(n=30)  # Menor que 60
        
        result = self.tester.test(prices_a, prices_b, pair_id="SHORT")
        
        assert result.status == CointegrationStatus.INSUFFICIENT_DATA

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
