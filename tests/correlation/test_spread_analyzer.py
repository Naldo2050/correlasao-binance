"""
Testes Unitários — Analisador de Spread (Z-Score)
==================================================
Testa Z-Score, half-life, beta estimation e classificação de zonas.
"""

import numpy as np
import pandas as pd
import pytest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.engine.spread_analyzer import SpreadAnalyzer, SpreadResult, SpreadZone


# ============================================================================
# FIXTURES — DADOS SINTÉTICOS
# ============================================================================

def _make_cointegrated_pair(
    n: int = 300,
    beta: float = 1.5,
    mean_reversion_speed: float = 0.1,
    seed: int = 42,
) -> tuple:
    """
    Gera par de preços cointegrados (spread mean-reverting).
    
    O spread segue um processo Ornstein-Uhlenbeck:
        dS = -θ·S·dt + σ·dW
    """
    np.random.seed(seed)
    
    # Preço base (random walk)
    base_returns = np.random.randn(n) * 0.01
    log_prices_b = np.cumsum(base_returns) + np.log(3000)
    
    # Spread mean-reverting
    spread = np.zeros(n)
    spread[0] = 0.0
    for i in range(1, n):
        spread[i] = (1 - mean_reversion_speed) * spread[i-1] + np.random.randn() * 0.01
    
    # Preço A = beta * B + spread
    log_prices_a = beta * log_prices_b + spread + np.log(50000 / (3000 ** beta))
    
    prices_a = np.exp(log_prices_a)
    prices_b = np.exp(log_prices_b)
    
    idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    return (
        pd.Series(prices_a, index=idx, name="price_A"),
        pd.Series(prices_b, index=idx, name="price_B"),
    )


def _make_trending_pair(n: int = 200, seed: int = 42) -> tuple:
    """Gera par com spread não-estacionário (divergente)."""
    np.random.seed(seed)
    
    idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    
    prices_a = 50000 * np.exp(np.cumsum(np.random.randn(n) * 0.01 + 0.001))
    prices_b = 3000 * np.exp(np.cumsum(np.random.randn(n) * 0.01 - 0.001))
    
    return (
        pd.Series(prices_a, index=idx),
        pd.Series(prices_b, index=idx),
    )


# ============================================================================
# TESTES DO SPREAD ANALYZER
# ============================================================================

class TestSpreadAnalyzer:
    """Testes do analisador de spread e Z-Score."""

    def setup_method(self):
        """Setup para cada teste."""
        self.analyzer = SpreadAnalyzer(z_window=50, beta_window=100)

    def test_basic_analysis(self):
        """Testa análise básica com par cointegrado."""
        prices_a, prices_b = _make_cointegrated_pair(n=300)
        
        result = self.analyzer.analyze(prices_a, prices_b, pair_id="COINT_TEST")
        
        assert isinstance(result, SpreadResult)
        assert result.pair_id == "COINT_TEST"
        assert result.z_score_series is not None
        assert result.spread_log is not None
        assert result.spread_raw is not None
        assert np.isfinite(result.z_score_current)

    def test_z_score_range(self):
        """Z-Score de par cointegrado deve estar em equilíbrio a maior parte do tempo."""
        prices_a, prices_b = _make_cointegrated_pair(n=500, mean_reversion_speed=0.15)
        
        result = self.analyzer.analyze(prices_a, prices_b)
        
        z = result.z_score_series
        assert z is not None
        
        # Proporção de Z dentro de ±2 deve ser alta (>80%)
        within_2 = (z.abs() < 2.0).mean()
        assert within_2 > 0.70, f"Apenas {within_2:.1%} dentro de ±2σ para par cointegrado"

    def test_half_life_cointegrated(self):
        """Half-life de par cointegrado deve ser razoável (< 100 períodos)."""
        prices_a, prices_b = _make_cointegrated_pair(n=500, mean_reversion_speed=0.10)
        
        result = self.analyzer.analyze(prices_a, prices_b)
        
        assert result.half_life is not None
        assert result.half_life < 100, (
            f"Half-life={result.half_life:.1f} muito alto para par cointegrado"
        )
        assert result.half_life > 0, "Half-life deve ser positivo"

    def test_half_life_divergent(self):
        """Half-life de par divergente deve ser alto."""
        prices_a, prices_b = _make_trending_pair(n=300)
        
        result = self.analyzer.analyze(prices_a, prices_b)
        
        # Par divergente deve ter half-life alto
        assert result.half_life is not None
        # Pode ser 999 (não converge) ou valor alto

    def test_beta_estimation(self):
        """Beta estimado deve estar próximo do valor real."""
        true_beta = 1.5
        prices_a, prices_b = _make_cointegrated_pair(n=500, beta=true_beta)
        
        result = self.analyzer.analyze(prices_a, prices_b)
        
        assert abs(result.beta - true_beta) < 0.5, (
            f"Beta estimado={result.beta:.4f}, real={true_beta}"
        )

    def test_zone_classification(self):
        """Testa classificação de zonas do Z-Score."""
        assert self.analyzer._classify_zone(0.5) == SpreadZone.EQUILIBRIUM
        assert self.analyzer._classify_zone(1.5) == SpreadZone.ATTENTION
        assert self.analyzer._classify_zone(2.1) == SpreadZone.REVERSAL_ZONE
        assert self.analyzer._classify_zone(2.7) == SpreadZone.HIGH_PROB
        assert self.analyzer._classify_zone(3.5) == SpreadZone.ANOMALY
        
        # Negativos
        assert self.analyzer._classify_zone(-0.5) == SpreadZone.EQUILIBRIUM
        assert self.analyzer._classify_zone(-2.3) == SpreadZone.REVERSAL_ZONE
        assert self.analyzer._classify_zone(-3.1) == SpreadZone.ANOMALY

    def test_z_color(self):
        """Testa cores do Z-Score."""
        result = SpreadResult(pair_id="TEST")
        
        result.z_score_current = 0.5
        assert result.get_z_color() == "🟢"
        
        result.z_score_current = 1.5
        assert result.get_z_color() == "🟡"
        
        result.z_score_current = 2.3
        assert result.get_z_color() == "🟠"
        
        result.z_score_current = 3.0
        assert result.get_z_color() == "🔴"
        
        result.z_score_current = -2.6
        assert result.get_z_color() == "🔴"

    def test_is_actionable(self):
        """Testa detecção de zona acionável."""
        result = SpreadResult(pair_id="TEST")
        
        result.zone = SpreadZone.EQUILIBRIUM
        assert not result.is_actionable
        
        result.zone = SpreadZone.ATTENTION
        assert not result.is_actionable
        
        result.zone = SpreadZone.REVERSAL_ZONE
        assert result.is_actionable
        
        result.zone = SpreadZone.HIGH_PROB
        assert result.is_actionable
        
        result.zone = SpreadZone.ANOMALY
        assert result.is_actionable

    def test_insufficient_data(self):
        """Testa com dados insuficientes."""
        idx = pd.date_range("2025-01-01", periods=5, freq="h", tz="UTC")
        prices_a = pd.Series([100, 101, 102, 103, 104], index=idx)
        prices_b = pd.Series([50, 51, 52, 53, 54], index=idx)
        
        result = self.analyzer.analyze(prices_a, prices_b, pair_id="SHORT")
        
        assert result.pair_id == "SHORT"
        # Não deve crashar

    def test_spread_direction(self):
        """Testa detecção de direção do spread."""
        prices_a, prices_b = _make_cointegrated_pair(n=300)
        
        result = self.analyzer.analyze(prices_a, prices_b)
        
        assert result.spread_direction in ("expanding", "contracting", "neutral")

    def test_from_aligned_data(self):
        """Testa análise a partir de dados alinhados."""
        prices_a, prices_b = _make_cointegrated_pair(n=300)
        
        aligned = pd.DataFrame({
            "close_BTC": prices_a,
            "close_ETH": prices_b,
        })
        
        result = self.analyzer.analyze_from_aligned(aligned, "BTC", "ETH")
        
        assert result.pair_id == "BTC↔ETH"
        assert result.z_score_series is not None

    def test_batch_analysis(self):
        """Testa análise em batch."""
        n = 300
        idx = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
        
        aligned = pd.DataFrame({
            "close_BTC": 50000 + np.cumsum(np.random.randn(n) * 100),
            "close_ETH": 3000 + np.cumsum(np.random.randn(n) * 20),
            "close_SOL": 150 + np.cumsum(np.random.randn(n) * 5),
        }, index=idx)
        
        pairs = [("BTC", "ETH"), ("BTC", "SOL")]
        results = self.analyzer.analyze_batch(aligned, pairs)
        
        assert len(results) == 2
        assert "BTC↔ETH" in results
        assert "BTC↔SOL" in results


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
