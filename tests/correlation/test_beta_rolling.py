"""
Testes Unitários — Beta Rolling Engine
=======================================
"""

import numpy as np
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.engine.beta_rolling import BetaRolling, BetaResult

class TestBetaRolling:
    def setup_method(self):
        self.engine = BetaRolling(windows=[20, 50], delta_lookback=5)

    def test_amplifier_beta(self):
        """Testa se o beta detecta corretamente um amplificador (A move 2x B)."""
        np.random.seed(42)
        n = 200
        returns_b = pd.Series(np.random.randn(n) * 0.01)
        returns_a = returns_b * 2.0 + (np.random.randn(n) * 0.001)
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="TEST")
        
        assert isinstance(result, BetaResult)
        assert 50 in result.current
        # Beta deveria estar muito próximo de 2.0
        assert abs(result.current[50] - 2.0) < 0.1
        assert result.is_amplifier is True

    def test_inverse_beta(self):
        """Testa se o beta detecta corretamente relação inversa."""
        np.random.seed(42)
        n = 200
        returns_b = pd.Series(np.random.randn(n) * 0.01)
        returns_a = returns_b * -1.5 + (np.random.randn(n) * 0.001)
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="TEST_INV")
        
        assert abs(result.current[50] - (-1.5)) < 0.1
        assert result.is_inverse is True

    def test_regime_change_inversion(self):
        """Testa se o sinal de mudança de regime dispara na inversão de beta."""
        np.random.seed(42)
        n = 200
        returns_b = pd.Series(np.random.randn(n) * 0.01)
        
        # Primeira metade: positivo. Segunda metade: negativo
        returns_a = returns_b.copy()
        returns_a.iloc[:195] = returns_a.iloc[:195] * 1.5
        returns_a.iloc[195:] = returns_a.iloc[195:] * -1.5
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="INVERT")
        
        assert result.regime_change_signal is True

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
