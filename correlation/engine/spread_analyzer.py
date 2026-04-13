"""
CORR-WATCH System v2.0 — Analisador de Spread (Z-Score)
========================================================
Calcula e monitora o spread entre pares de ativos com normalização
Z-Score para detecção de oportunidades de convergência/divergência.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.1, item 3 (Z-Score do Spread)

Fórmulas:
  Spread Absoluto:    S = Preço_A - Preço_B
  Spread Logarítmico: S = ln(Preço_A) - β·ln(Preço_B)
  Z-Score:            Z = (S - μ_S) / σ_S
  Half-Life:          HL = -ln(2) / θ  (θ from ΔS_t = θ·S_{t-1} + ε_t)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("corr_watch.engine.spread")


class SpreadZone(Enum):
    """Zonas de Z-Score do spread."""
    EQUILIBRIUM = "EQUILIBRIUM"       # |Z| < 1.0 — sem sinal
    ATTENTION = "ATTENTION"           # 1.0 ≤ |Z| < 2.0 — atenção
    REVERSAL_ZONE = "REVERSAL_ZONE"   # 2.0 ≤ |Z| < 2.5 — possível reversão
    HIGH_PROB = "HIGH_PROB"           # 2.5 ≤ |Z| < 3.0 — alta prob. reversão
    ANOMALY = "ANOMALY"               # |Z| ≥ 3.0 — anomalia, investigar


@dataclass
class SpreadResult:
    """
    Resultado da análise de spread entre um par de ativos.
    
    Campos principais:
      - pair_id: Identificador do par
      - spread_raw: Série do spread absoluto
      - spread_log: Série do spread logarítmico
      - z_score_series: Série do Z-Score
      - z_score_current: Z-Score atual
      - half_life: Half-life de mean reversion em períodos
      - zone: Zona atual do Z-Score
      - beta: Beta estimado entre os ativos
    """
    pair_id: str
    spread_raw: Optional[pd.Series] = None
    spread_log: Optional[pd.Series] = None
    z_score_series: Optional[pd.Series] = None
    z_score_current: float = 0.0
    z_score_mean: float = 0.0
    z_score_std: float = 1.0
    half_life: Optional[float] = None
    zone: SpreadZone = SpreadZone.EQUILIBRIUM
    beta: float = 1.0
    spread_direction: str = "neutral"  # "expanding", "contracting", "neutral"
    timestamp: Optional[pd.Timestamp] = None

    @property
    def is_actionable(self) -> bool:
        """Se o Z-Score está em zona de possível ação."""
        return self.zone in (
            SpreadZone.REVERSAL_ZONE,
            SpreadZone.HIGH_PROB,
            SpreadZone.ANOMALY,
        )

    def get_z_color(self) -> str:
        """Cor para a tabela de monitoramento."""
        z = abs(self.z_score_current)
        if z < 1.0:
            return "🟢"
        elif z < 2.0:
            return "🟡"
        elif z < 2.5:
            return "🟠"
        else:
            return "🔴"


class SpreadAnalyzer:
    """
    Analisador de Spread e Z-Score entre pares de ativos.
    
    Core do pair trading: identifica quando o spread entre dois
    ativos cointegrados se desvia da média, sinalizando
    oportunidades de convergência.
    
    Pipeline:
      1. Calcula spread absoluto e logarítmico
      2. Estima beta (hedge ratio) via regressão OLS
      3. Calcula Z-Score normalizado do spread
      4. Estima half-life de mean reversion
      5. Classifica em zonas de ação
    
    Z-Score Interpretation:
      Z > +2.0  → Spread expandido → possível CONVERGÊNCIA
      Z < -2.0  → Spread contraído → possível DIVERGÊNCIA
      Z → 0     → Equilíbrio → sem sinal
      |Z| > 3.0 → ANOMALIA → investigar quebra estrutural
    
    Uso:
        analyzer = SpreadAnalyzer()
        result = analyzer.analyze(prices_btc, prices_eth, pair_id="BTCUSDT↔ETHUSDT")
        print(f"Z-Score: {result.z_score_current:.2f} | Zone: {result.zone}")
        print(f"Half-life: {result.half_life:.1f} períodos")
    """

    def __init__(
        self,
        z_window: int = 50,
        beta_window: int = 100,
        z_thresholds: Optional[Dict[str, float]] = None,
    ):
        """
        Args:
            z_window: Janela para média/desvio do Z-Score (padrão: 50)
            beta_window: Janela para estimativa do beta (padrão: 100)
            z_thresholds: Thresholds customizados {zone: value}
        """
        self.z_window = z_window
        self.beta_window = beta_window
        self.z_thresholds = z_thresholds or {
            "attention": 1.0,
            "reversal": 2.0,
            "high_prob": 2.5,
            "anomaly": 3.0,
        }

    def analyze(
        self,
        prices_a: pd.Series,
        prices_b: pd.Series,
        pair_id: str = "A↔B",
        use_log_spread: bool = True,
    ) -> SpreadResult:
        """
        Análise completa de spread entre dois ativos.
        
        Args:
            prices_a: Série de preços do ativo A
            prices_b: Série de preços do ativo B
            pair_id: Identificador do par
            use_log_spread: Usar spread logarítmico (recomendado)
            
        Returns:
            SpreadResult com Z-Score, half-life, zona, etc.
        """
        if prices_a is None or prices_b is None:
            return SpreadResult(pair_id=pair_id)

        # Alinha séries
        combined = pd.DataFrame({"a": prices_a, "b": prices_b}).dropna()

        if len(combined) < 20:
            logger.warning(f"Dados insuficientes para spread de {pair_id}: {len(combined)} < 20")
            return SpreadResult(pair_id=pair_id)

        # 1. Estima Beta (hedge ratio) via OLS rolling
        beta = self._estimate_beta(combined["a"], combined["b"])

        # 2. Calcula spreads
        spread_raw = combined["a"] - combined["b"]
        spread_log = np.log(combined["a"]) - beta * np.log(combined["b"])

        # Seleciona spread para análise
        spread = spread_log if use_log_spread else spread_raw

        # 3. Calcula Z-Score
        z_mean = spread.rolling(window=self.z_window).mean()
        z_std = spread.rolling(window=self.z_window).std()

        # Previne divisão por zero
        z_std = z_std.replace(0, np.nan)

        z_score = (spread - z_mean) / z_std
        z_score = z_score.dropna()

        if z_score.empty:
            return SpreadResult(pair_id=pair_id, beta=beta)

        z_current = float(z_score.iloc[-1])

        # 4. Half-life de mean reversion
        half_life = self._calculate_half_life(spread)

        # 5. Direção do spread
        if len(z_score) >= 5:
            z_delta = z_score.iloc[-1] - z_score.iloc[-5]
            if z_delta > 0.3:
                direction = "expanding"
            elif z_delta < -0.3:
                direction = "contracting"
            else:
                direction = "neutral"
        else:
            direction = "neutral"

        # 6. Classifica zona
        zone = self._classify_zone(z_current)

        result = SpreadResult(
            pair_id=pair_id,
            spread_raw=spread_raw,
            spread_log=spread_log,
            z_score_series=z_score,
            z_score_current=z_current,
            z_score_mean=float(z_mean.iloc[-1]) if not z_mean.empty else 0.0,
            z_score_std=float(z_std.iloc[-1]) if not z_std.dropna().empty else 1.0,
            half_life=half_life,
            zone=zone,
            beta=beta,
            spread_direction=direction,
            timestamp=z_score.index[-1] if not z_score.empty else None,
        )

        logger.debug(
            f"Spread {pair_id}: Z={z_current:+.2f} | "
            f"Zone={zone.value} | β={beta:.4f} | "
            f"HL={half_life:.1f}p | Dir={direction}"
        )

        return result

    def analyze_from_aligned(
        self,
        aligned_data: pd.DataFrame,
        symbol_a: str,
        symbol_b: str,
    ) -> SpreadResult:
        """
        Analisa spread a partir de dados já alinhados pelo SyncAligner.
        
        Args:
            aligned_data: DataFrame com colunas close_A, close_B
            symbol_a: Símbolo do ativo A
            symbol_b: Símbolo do ativo B
        """
        close_a = f"close_{symbol_a}"
        close_b = f"close_{symbol_b}"

        if close_a not in aligned_data.columns or close_b not in aligned_data.columns:
            logger.warning(f"Colunas faltando: {close_a}, {close_b}")
            return SpreadResult(pair_id=f"{symbol_a}↔{symbol_b}")

        return self.analyze(
            aligned_data[close_a],
            aligned_data[close_b],
            pair_id=f"{symbol_a}↔{symbol_b}",
        )

    # ────────────────────────────────────────────────────────────────
    # CÁLCULOS INTERNOS
    # ────────────────────────────────────────────────────────────────

    def _estimate_beta(self, prices_a: pd.Series, prices_b: pd.Series) -> float:
        """
        Estima o hedge ratio (β) via regressão OLS.
        β = Cov(ln(A), ln(B)) / Var(ln(B))
        
        Indica quantas unidades de B precisa para hedgear 1 unidade de A.
        """
        log_a = np.log(prices_a)
        log_b = np.log(prices_b)

        # Usa últimos beta_window pontos
        if len(log_a) > self.beta_window:
            log_a = log_a.iloc[-self.beta_window:]
            log_b = log_b.iloc[-self.beta_window:]

        cov = np.cov(log_a, log_b)
        if cov.shape == (2, 2) and cov[1, 1] != 0:
            beta = cov[0, 1] / cov[1, 1]
        else:
            beta = 1.0

        return float(beta)

    def _calculate_half_life(self, spread: pd.Series) -> float:
        """
        Calcula o half-life de mean reversion do spread.
        
        O spread é primeiro demeanoado (S - μ) para que a regressão
        ΔS_t = θ·(S_{t-1} - μ) + ε_t funcione corretamente.
        Half-life = -ln(2) / θ
        
        HL < 10 períodos: reversion rápida (bom para scalping)
        HL > 50 períodos: reversion lenta (posição)
        
        Returns:
            Half-life em períodos. Retorna 999.0 se não converge.
        """
        spread_clean = spread.dropna()
        if len(spread_clean) < 20:
            return 999.0

        # Demean o spread (centra em zero para AR(1) correto)
        spread_demeaned = spread_clean - spread_clean.mean()

        # ΔS = S_t - S_{t-1}
        delta_spread = spread_demeaned.diff().dropna()
        lagged_spread = spread_demeaned.shift(1).dropna()

        # Alinha
        common_idx = delta_spread.index.intersection(lagged_spread.index)
        delta_spread = delta_spread.loc[common_idx]
        lagged_spread = lagged_spread.loc[common_idx]

        if len(delta_spread) < 10:
            return 999.0

        # Regressão OLS: ΔS = θ·S_{t-1} (com spread demeanoado)
        # θ = Σ(S_{t-1} · ΔS) / Σ(S_{t-1}²)
        numerator = (lagged_spread * delta_spread).sum()
        denominator = (lagged_spread ** 2).sum()

        if denominator == 0:
            return 999.0

        theta = numerator / denominator

        if theta >= 0:
            # θ positivo = spread divergente, não mean-reverting
            return 999.0

        half_life = -np.log(2) / theta

        # Clamp a valores razoáveis
        half_life = max(1.0, min(999.0, half_life))

        return float(half_life)

    def _classify_zone(self, z: float) -> SpreadZone:
        """Classifica o Z-Score em zonas de ação."""
        abs_z = abs(z)

        if abs_z >= self.z_thresholds["anomaly"]:
            return SpreadZone.ANOMALY
        elif abs_z >= self.z_thresholds["high_prob"]:
            return SpreadZone.HIGH_PROB
        elif abs_z >= self.z_thresholds["reversal"]:
            return SpreadZone.REVERSAL_ZONE
        elif abs_z >= self.z_thresholds["attention"]:
            return SpreadZone.ATTENTION
        else:
            return SpreadZone.EQUILIBRIUM

    # ────────────────────────────────────────────────────────────────
    # BATCH
    # ────────────────────────────────────────────────────────────────

    def analyze_batch(
        self,
        aligned_data: pd.DataFrame,
        pairs: list,
    ) -> Dict[str, SpreadResult]:
        """
        Analisa spread de múltiplos pares.
        
        Args:
            aligned_data: DataFrame com colunas close_SYMBOL
            pairs: Lista de tuplas (symbol_a, symbol_b)
            
        Returns:
            Dict[pair_id, SpreadResult]
        """
        results = {}
        for sym_a, sym_b in pairs:
            pair_id = f"{sym_a}↔{sym_b}"
            result = self.analyze_from_aligned(aligned_data, sym_a, sym_b)
            results[pair_id] = result

        logger.info(f"Batch Spread: {len(results)} pares analisados")
        return results
