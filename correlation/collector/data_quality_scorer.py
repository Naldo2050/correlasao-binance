"""
CORR-WATCH System v2.0 — Score de Qualidade de Dados
=====================================================
Avalia a qualidade das séries de dados coletadas.
Score 0 a 100 baseado em completude, gaps, outliers, volume.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 2.1 (Sistema de Qualidade)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("corr_watch.collector.data_quality")


class QualityLevel(Enum):
    """Níveis de confiança dos dados."""
    HIGH = "HIGH"           # Score 80-100: dados excelentes
    MEDIUM = "MEDIUM"       # Score 60-79: dados aceitáveis
    LOW = "LOW"             # Score 40-59: dados com ressalvas
    CRITICAL = "CRITICAL"   # Score 0-39: dados não confiáveis


@dataclass
class QualityReport:
    """Relatório de qualidade de uma série de dados."""
    symbol: str
    score: float                # 0-100
    level: QualityLevel
    completeness: float         # % de dados presentes (0-1)
    gap_count: int              # Número de gaps detectados
    max_gap_size: int           # Maior gap em períodos
    outlier_count: int          # Outliers detectados (Z > 3)
    volume_adequacy: float      # Volume vs média histórica (ratio)
    staleness_seconds: float    # Idade do dado mais recente
    details: Dict[str, float]   # Scores individuais dos componentes

    @property
    def is_usable(self) -> bool:
        """Indica se os dados são utilizáveis para cálculos."""
        return self.level in (QualityLevel.HIGH, QualityLevel.MEDIUM)


class DataQualityScorer:
    """
    Avalia qualidade de séries de dados para cálculo de correlação.
    
    Componentes do Score (0-100):
      1. Completude (peso 30%):  % de dados presentes sem gaps
      2. Gaps (peso 25%):        Penaliza por gaps grandes
      3. Outliers (peso 20%):    Penaliza dados anômalos (Z > 3)
      4. Volume (peso 15%):      Volume suficiente para confiabilidade
      5. Frescor (peso 10%):     Quão recente é o último dado
    
    Uso:
        scorer = DataQualityScorer()
        report = scorer.evaluate(df, symbol="BTCUSDT")
        print(f"Score: {report.score} | Level: {report.level}")
    """

    # Pesos dos componentes
    WEIGHT_COMPLETENESS = 0.30
    WEIGHT_GAPS = 0.25
    WEIGHT_OUTLIERS = 0.20
    WEIGHT_VOLUME = 0.15
    WEIGHT_FRESHNESS = 0.10

    # Thresholds
    OUTLIER_ZSCORE = 3.0        # Z-Score para considerar outlier
    MAX_STALENESS_MINUTES = 10  # Máximo de minutos para dado "fresco"
    MIN_ROWS = 20               # Mínimo de linhas para avaliação

    def evaluate(
        self,
        df: pd.DataFrame,
        symbol: str = "UNKNOWN",
        expected_freq_minutes: Optional[float] = None,
    ) -> QualityReport:
        """
        Avalia a qualidade de uma série de dados.
        
        Args:
            df: DataFrame com index=timestamp, colunas: close, volume, etc.
            symbol: Nome do símbolo para logging
            expected_freq_minutes: Frequência esperada em minutos (auto-detect se None)
            
        Returns:
            QualityReport com score e detalhes
        """
        if df is None or df.empty or len(df) < 2:
            return QualityReport(
                symbol=symbol,
                score=0.0,
                level=QualityLevel.CRITICAL,
                completeness=0.0,
                gap_count=0,
                max_gap_size=0,
                outlier_count=0,
                volume_adequacy=0.0,
                staleness_seconds=float("inf"),
                details={},
            )

        # Auto-detect frequência se não fornecida
        if expected_freq_minutes is None:
            diffs = pd.Series(df.index).diff().dropna()
            if not diffs.empty:
                expected_freq_minutes = diffs.median().total_seconds() / 60.0
            else:
                expected_freq_minutes = 60.0

        # Calcula cada componente
        completeness_score, completeness, gap_count, max_gap = self._score_completeness(
            df, expected_freq_minutes
        )
        gap_score = self._score_gaps(gap_count, max_gap, len(df))
        outlier_score, outlier_count = self._score_outliers(df)
        volume_score, volume_adequacy = self._score_volume(df)
        freshness_score, staleness = self._score_freshness(df)

        # Score composto
        total_score = (
            completeness_score * self.WEIGHT_COMPLETENESS
            + gap_score * self.WEIGHT_GAPS
            + outlier_score * self.WEIGHT_OUTLIERS
            + volume_score * self.WEIGHT_VOLUME
            + freshness_score * self.WEIGHT_FRESHNESS
        )

        # Clamp 0-100
        total_score = max(0.0, min(100.0, total_score))

        # Determina nível
        if total_score >= 80:
            level = QualityLevel.HIGH
        elif total_score >= 60:
            level = QualityLevel.MEDIUM
        elif total_score >= 40:
            level = QualityLevel.LOW
        else:
            level = QualityLevel.CRITICAL

        report = QualityReport(
            symbol=symbol,
            score=round(total_score, 1),
            level=level,
            completeness=round(completeness, 4),
            gap_count=gap_count,
            max_gap_size=max_gap,
            outlier_count=outlier_count,
            volume_adequacy=round(volume_adequacy, 2),
            staleness_seconds=staleness,
            details={
                "completeness_score": round(completeness_score, 1),
                "gap_score": round(gap_score, 1),
                "outlier_score": round(outlier_score, 1),
                "volume_score": round(volume_score, 1),
                "freshness_score": round(freshness_score, 1),
            },
        )

        logger.debug(
            f"Quality {symbol}: {report.score}/100 ({report.level.value}) | "
            f"completeness={completeness:.2%} gaps={gap_count} "
            f"outliers={outlier_count} staleness={staleness:.0f}s"
        )
        return report

    def evaluate_batch(
        self,
        data: Dict[str, pd.DataFrame],
        expected_freq_minutes: Optional[float] = None,
    ) -> Dict[str, QualityReport]:
        """Avalia qualidade de múltiplas séries."""
        return {
            symbol: self.evaluate(df, symbol, expected_freq_minutes)
            for symbol, df in data.items()
        }

    # ────────────────────────────────────────────────────────────────
    # COMPONENTES DE SCORE
    # ────────────────────────────────────────────────────────────────

    def _score_completeness(
        self,
        df: pd.DataFrame,
        expected_freq_minutes: float,
    ) -> tuple:
        """
        Avalia completude da série.
        
        Returns:
            (score, completeness_ratio, gap_count, max_gap_size)
        """
        if len(df) < self.MIN_ROWS:
            return 50.0, len(df) / self.MIN_ROWS, 0, 0

        # Calcula gaps (períodos faltantes)
        diffs = pd.Series(df.index).diff().dropna()
        expected_td = pd.Timedelta(minutes=expected_freq_minutes)
        tolerance = expected_td * 1.5  # 50% de tolerância

        gaps = diffs[diffs > tolerance]
        gap_count = len(gaps)
        max_gap = 0

        if gap_count > 0:
            max_gap = int(round(gaps.max() / expected_td))

        # Completude = períodos presentes / períodos esperados
        time_range = (df.index[-1] - df.index[0]).total_seconds() / 60.0
        expected_rows = max(1, time_range / expected_freq_minutes)
        completeness = min(1.0, len(df) / expected_rows)

        # Score: 100 se completo, decresce linearmente
        score = completeness * 100.0

        return score, completeness, gap_count, max_gap

    def _score_gaps(self, gap_count: int, max_gap: int, total_rows: int) -> float:
        """
        Penaliza por número e tamanho de gaps.
        """
        if gap_count == 0:
            return 100.0

        # Penaliza por número de gaps (cada gap = -5 pontos, mínimo 0)
        count_penalty = min(gap_count * 5, 50)

        # Penaliza por tamanho do maior gap
        if max_gap <= 2:
            size_penalty = 0
        elif max_gap <= 5:
            size_penalty = 15
        elif max_gap <= 10:
            size_penalty = 30
        else:
            size_penalty = 50

        return max(0.0, 100.0 - count_penalty - size_penalty)

    def _score_outliers(self, df: pd.DataFrame) -> tuple:
        """
        Detecta e penaliza outliers usando Z-Score.
        
        Returns:
            (score, outlier_count)
        """
        if "close" not in df.columns or len(df) < 10:
            return 100.0, 0

        # Retornos log
        returns = np.log(df["close"] / df["close"].shift(1)).dropna()

        if returns.std() == 0:
            return 100.0, 0

        z_scores = np.abs((returns - returns.mean()) / returns.std())
        outlier_count = int((z_scores > self.OUTLIER_ZSCORE).sum())

        # Ratio de outliers
        outlier_ratio = outlier_count / len(returns) if len(returns) > 0 else 0

        # Score: penaliza conforme ratio (até 10% de outliers = score 50)
        if outlier_ratio == 0:
            score = 100.0
        elif outlier_ratio < 0.02:
            score = 90.0
        elif outlier_ratio < 0.05:
            score = 70.0
        elif outlier_ratio < 0.10:
            score = 50.0
        else:
            score = 20.0

        return score, outlier_count

    def _score_volume(self, df: pd.DataFrame) -> tuple:
        """
        Avalia se o volume é suficiente.
        
        Returns:
            (score, volume_adequacy_ratio)
        """
        if "volume" not in df.columns or len(df) < 20:
            return 80.0, 1.0  # Dados macro podem não ter volume

        vol = df["volume"]

        # Volume recente vs média 20 períodos
        if len(vol) >= 20:
            recent_vol = vol.iloc[-5:].mean()
            avg_vol = vol.iloc[-20:].mean()
            ratio = recent_vol / avg_vol if avg_vol > 0 else 0
        else:
            ratio = 1.0

        # Score
        if ratio >= 0.8:
            score = 100.0
        elif ratio >= 0.5:
            score = 70.0
        elif ratio >= 0.2:
            score = 40.0
        else:
            score = 10.0

        return score, ratio

    def _score_freshness(self, df: pd.DataFrame) -> tuple:
        """
        Avalia quão recente é o último dado.
        
        Returns:
            (score, staleness_seconds)
        """
        if df.index.empty:
            return 0.0, float("inf")

        last_ts = df.index[-1]

        # Calcula staleness
        now = pd.Timestamp.now(tz="UTC")
        if last_ts.tz is None:
            last_ts = last_ts.tz_localize("UTC")

        staleness = (now - last_ts).total_seconds()

        # Score baseado em staleness
        max_staleness = self.MAX_STALENESS_MINUTES * 60
        if staleness <= max_staleness:
            score = 100.0
        elif staleness <= max_staleness * 3:
            score = 70.0
        elif staleness <= max_staleness * 10:
            score = 40.0
        else:
            score = 10.0

        return score, staleness
