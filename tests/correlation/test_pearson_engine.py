"""
Testes Unitários — Motor de Correlação Pearson
===============================================
Testa cálculos de correlação com dados sintéticos de correlação conhecida.
"""

import numpy as np
import pandas as pd
import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.engine.pearson_engine import PearsonEngine, CorrelationResult


# ============================================================================
# FIXTURES — DADOS SINTÉTICOS
# ============================================================================

def _make_correlated_series(
    n: int = 200,
    correlation: float = 0.85,
    seed: int = 42,
) -> tuple:
    """
    Gera duas séries de retornos com correlação conhecida.
    
    Usa decomposição de Cholesky para criar séries com correlação exata.
    """
    np.random.seed(seed)
    
    # Gera independentes
    z1 = np.random.randn(n)
    z2 = np.random.randn(n)
    
    # Combina para atingir correlação alvo
    returns_a = z1
    returns_b = correlation * z1 + np.sqrt(1 - correlation**2) * z2
    
    # Cria Series com index temporal
    idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    series_a = pd.Series(returns_a, index=idx, name="returns_A")
    series_b = pd.Series(returns_b, index=idx, name="returns_B")
    
    return series_a, series_b


def _make_prices_from_returns(returns: pd.Series, start_price: float = 100.0) -> pd.Series:
    """Converte retornos log em série de preços."""
    log_prices = np.cumsum(returns) + np.log(start_price)
    prices = np.exp(log_prices)
    return pd.Series(prices, index=returns.index)


# ============================================================================
# TESTES DO PEARSON ENGINE
# ============================================================================

class TestPearsonEngine:
    """Testes do motor de correlação Pearson."""

    def setup_method(self):
        """Setup para cada teste."""
        self.engine = PearsonEngine(windows=[20, 50, 100])

    def test_basic_positive_correlation(self):
        """Testa correlação positiva forte com dados sintéticos."""
        returns_a, returns_b = _make_correlated_series(n=200, correlation=0.85)
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="TEST_POS")
        
        assert isinstance(result, CorrelationResult)
        assert result.pair_id == "TEST_POS"
        
        # Correlação de 100p deve estar próxima de 0.85
        corr_100 = result.current[100]
        assert abs(corr_100 - 0.85) < 0.15, f"Correlação 100p={corr_100:.4f}, esperada ~0.85"
        
        # Todas as janelas devem ter valores
        for w in [20, 50, 100]:
            assert w in result.current
            assert w in result.delta
            assert w in result.mean

    def test_negative_correlation(self):
        """Testa correlação negativa forte."""
        returns_a, returns_b = _make_correlated_series(n=200, correlation=-0.80)
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="TEST_NEG")
        
        corr_100 = result.current[100]
        assert corr_100 < -0.6, f"Esperava correlação negativa forte, obteve {corr_100:.4f}"

    def test_zero_correlation(self):
        """Testa séries descorrelacionadas."""
        returns_a, returns_b = _make_correlated_series(n=200, correlation=0.0)
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="TEST_ZERO")
        
        corr_100 = result.current[100]
        assert abs(corr_100) < 0.25, f"Esperava ~0, obteve {corr_100:.4f}"

    def test_delta_correlation(self):
        """Testa cálculo de delta (velocidade de mudança)."""
        returns_a, returns_b = _make_correlated_series(n=200, correlation=0.80)
        
        result = self.engine.calculate(returns_a, returns_b)
        
        # Delta deve existir e ser finito
        for w in self.engine.windows:
            if w in result.delta:
                assert np.isfinite(result.delta[w]), f"Delta W{w} não é finito"

    def test_insufficient_data(self):
        """Testa com dados insuficientes (< menor janela)."""
        returns_a, returns_b = _make_correlated_series(n=10, correlation=0.80)
        
        result = self.engine.calculate(returns_a, returns_b, pair_id="SHORT")
        
        # Deve retornar resultado vazio ou parcial
        assert result.pair_id == "SHORT"
        # Janela de 100 não deve existir com 10 dados
        assert 100 not in result.current

    def test_deviation_sigma(self):
        """Testa cálculo de desvio em sigmas."""
        returns_a, returns_b = _make_correlated_series(n=200, correlation=0.85)
        
        result = self.engine.calculate(returns_a, returns_b)
        
        sigma = result.get_deviation_sigma(50)
        assert sigma >= 0, "Sigma deve ser não-negativo"
        assert np.isfinite(sigma), "Sigma deve ser finito"

    def test_classify_correlation(self):
        """Testa classificação de intensidade."""
        assert self.engine.classify_correlation(0.90) == "STRONG_POS"
        assert self.engine.classify_correlation(0.55) == "MODERATE_POS"
        assert self.engine.classify_correlation(0.10) == "WEAK/NEUTRAL"
        assert self.engine.classify_correlation(-0.55) == "MODERATE_NEG"
        assert self.engine.classify_correlation(-0.85) == "STRONG_NEG"

    def test_color_code(self):
        """Testa atribuição de cor baseada em desvio."""
        # Dentro do padrão
        assert self.engine.get_color_code(0.80, 0.80, 0.10) == "🟢"
        # Atenção (1-2σ)
        assert self.engine.get_color_code(0.65, 0.80, 0.10) == "🟡"
        # Alerta (2-2.5σ)
        assert self.engine.get_color_code(0.56, 0.80, 0.10) == "🟠"
        # Crítico (>2.5σ)
        assert self.engine.get_color_code(0.50, 0.80, 0.10) == "🔴"

    def test_from_prices(self):
        """Testa cálculo a partir de séries de preços."""
        returns_a, returns_b = _make_correlated_series(n=200, correlation=0.85)
        prices_a = _make_prices_from_returns(returns_a, start_price=50000)
        prices_b = _make_prices_from_returns(returns_b, start_price=3000)
        
        result = self.engine.calculate_from_prices(prices_a, prices_b, pair_id="PRICES")
        
        assert result.pair_id == "PRICES"
        assert 50 in result.current
        # Correlação deve ser similar à dos retornos
        corr = result.current[50]
        assert abs(corr) > 0.5, f"Correlação a partir de preços muito baixa: {corr:.4f}"

    def test_batch_calculation(self):
        """Testa cálculo em batch para múltiplos pares."""
        # Gera dados alinhados
        n = 200
        idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
        np.random.seed(42)
        
        aligned = pd.DataFrame({
            "returns_BTCUSDT": np.random.randn(n) * 0.02,
            "returns_ETHUSDT": np.random.randn(n) * 0.03,
            "returns_SOLUSDT": np.random.randn(n) * 0.04,
        }, index=idx)
        
        # Correlaciona ETH com BTC
        aligned["returns_ETHUSDT"] += aligned["returns_BTCUSDT"] * 0.8
        
        pairs = [("BTCUSDT", "ETHUSDT"), ("BTCUSDT", "SOLUSDT")]
        results = self.engine.calculate_batch(aligned, pairs)
        
        assert len(results) == 2
        assert "BTCUSDT↔ETHUSDT" in results
        assert "BTCUSDT↔SOLUSDT" in results

    def test_is_anomaly(self):
        """Testa detecção de anomalia via sigma."""
        result = CorrelationResult(pair_id="TEST")
        result.current[50] = 0.30
        result.mean[50] = 0.80
        result.std[50] = 0.10
        
        # Desvio de 5σ → deve ser anomalia
        assert result.is_anomaly(50, threshold_sigma=2.5)
        
        # Dentro do normal
        result2 = CorrelationResult(pair_id="TEST2")
        result2.current[50] = 0.78
        result2.mean[50] = 0.80
        result2.std[50] = 0.10
        assert not result2.is_anomaly(50, threshold_sigma=2.5)


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
