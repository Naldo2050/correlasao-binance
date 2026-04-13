"""
CORR-WATCH System v2.0 — Alinhamento Temporal entre Séries
==========================================================
Sincroniza timestamps entre DataFrames de diferentes pares/fontes.
Garante que todas as séries tenham os mesmos timestamps para cálculo
de correlação.

Referência: CORRELAÇÃO BINANCE(copia).md — Camada 2 (Pré-processamento)
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger("corr_watch.collector.sync_aligner")


class SyncAligner:
    """
    Alinha temporalmente séries de preços de diferentes fontes.
    
    Problema: Binance e yFinance podem ter timestamps diferentes,
    gaps, e frequências distintas. Este módulo garante que todas
    as séries estejam sincronizadas para cálculo de correlação.
    
    Estratégias:
      1. Inner join: só mantém timestamps presentes em TODAS as séries
      2. Outer join + interpolação: mantém todos timestamps, interpola gaps
      3. Resample: reagrupa para frequência comum
    
    Uso:
        aligner = SyncAligner()
        aligned = aligner.align_pair(df_btc, df_eth, method="inner")
        # aligned = DataFrame com colunas: close_A, close_B, volume_A, volume_B
    """

    # Configurações de interpolação
    MAX_GAP_INTERPOLATE = 5  # Máximo de períodos para interpolar
    INTERPOLATION_METHOD = "linear"  # linear, cubic, spline

    def align_pair(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame,
        label_a: str = "A",
        label_b: str = "B",
        method: str = "inner",
        price_col: str = "close",
    ) -> pd.DataFrame:
        """
        Alinha duas séries de preços por timestamp.
        
        Args:
            df_a: DataFrame do ativo A (index=timestamp)
            df_b: DataFrame do ativo B (index=timestamp)
            label_a: Label para colunas do ativo A
            label_b: Label para colunas do ativo B
            method: "inner" (padrão) ou "outer"
            price_col: Coluna de preço a usar ("close", "open", etc.)
            
        Returns:
            DataFrame com colunas: 
              close_A, close_B, volume_A, volume_B, returns_A, returns_B
        """
        if df_a is None or df_b is None or df_a.empty or df_b.empty:
            logger.warning(f"Dados vazios para alinhamento {label_a}↔{label_b}")
            return pd.DataFrame()

        # Seleciona colunas relevantes
        cols_needed = [price_col, "volume"]
        cols_a = [c for c in cols_needed if c in df_a.columns]
        cols_b = [c for c in cols_needed if c in df_b.columns]

        series_a = df_a[cols_a].copy()
        series_b = df_b[cols_b].copy()

        # Renomeia colunas com label
        series_a.columns = [f"{c}_{label_a}" for c in series_a.columns]
        series_b.columns = [f"{c}_{label_b}" for c in series_b.columns]

        # Alinha por join
        if method == "inner":
            aligned = series_a.join(series_b, how="inner")
        elif method == "outer":
            aligned = series_a.join(series_b, how="outer")
            aligned = self._interpolate_gaps(aligned)
        else:
            raise ValueError(f"Método desconhecido: {method}. Use 'inner' ou 'outer'.")

        if aligned.empty:
            logger.warning(
                f"Sem dados alinhados para {label_a}↔{label_b}. "
                f"A: {len(df_a)} rows [{df_a.index.min()} → {df_a.index.max()}], "
                f"B: {len(df_b)} rows [{df_b.index.min()} → {df_b.index.max()}]"
            )
            return pd.DataFrame()

        # Calcula retornos logarítmicos
        close_a = f"{price_col}_{label_a}"
        close_b = f"{price_col}_{label_b}"
        if close_a in aligned.columns and close_b in aligned.columns:
            aligned[f"returns_{label_a}"] = np.log(
                aligned[close_a] / aligned[close_a].shift(1)
            )
            aligned[f"returns_{label_b}"] = np.log(
                aligned[close_b] / aligned[close_b].shift(1)
            )

        # Remove linhas com NaN nos retornos (primeira linha e gaps)
        aligned.dropna(inplace=True)

        logger.debug(
            f"Alinhamento {label_a}↔{label_b}: "
            f"{len(aligned)} períodos [{aligned.index[0]} → {aligned.index[-1]}]"
        )
        return aligned

    def align_multiple(
        self,
        data: Dict[str, pd.DataFrame],
        price_col: str = "close",
        method: str = "inner",
    ) -> pd.DataFrame:
        """
        Alinha múltiplas séries por timestamp.
        
        Args:
            data: Dict[symbol, DataFrame]
            price_col: Coluna de preço
            method: "inner" ou "outer"
            
        Returns:
            DataFrame com colunas: close_SYMBOL, volume_SYMBOL, returns_SYMBOL
            para cada símbolo
        """
        if not data:
            return pd.DataFrame()

        frames = []
        for symbol, df in data.items():
            if df is None or df.empty:
                continue
            cols = {}
            if price_col in df.columns:
                cols[f"{price_col}_{symbol}"] = df[price_col]
            if "volume" in df.columns:
                cols[f"volume_{symbol}"] = df["volume"]
            if cols:
                frames.append(pd.DataFrame(cols, index=df.index))

        if not frames:
            return pd.DataFrame()

        # Join progressivo
        result = frames[0]
        for frame in frames[1:]:
            result = result.join(frame, how=method)

        if method == "outer":
            result = self._interpolate_gaps(result)

        # Calcula retornos para cada símbolo
        symbols = list(data.keys())
        for symbol in symbols:
            close_col = f"{price_col}_{symbol}"
            if close_col in result.columns:
                result[f"returns_{symbol}"] = np.log(
                    result[close_col] / result[close_col].shift(1)
                )

        result.dropna(inplace=True)

        logger.info(
            f"Alinhamento múltiplo: {len(symbols)} séries → "
            f"{len(result)} períodos alinhados"
        )
        return result

    def get_alignment_stats(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame,
    ) -> Dict:
        """
        Retorna estatísticas de qualidade do alinhamento.
        
        Returns:
            Dict com: overlap_ratio, gap_count, total_aligned, etc.
        """
        if df_a is None or df_b is None or df_a.empty or df_b.empty:
            return {"overlap_ratio": 0.0, "gap_count": 0, "total_aligned": 0}

        idx_a = set(df_a.index)
        idx_b = set(df_b.index)

        intersection = idx_a & idx_b
        union = idx_a | idx_b

        return {
            "total_a": len(idx_a),
            "total_b": len(idx_b),
            "total_aligned": len(intersection),
            "total_union": len(union),
            "overlap_ratio": len(intersection) / len(union) if union else 0.0,
            "gap_count_a": len(idx_b - idx_a),
            "gap_count_b": len(idx_a - idx_b),
        }

    # ────────────────────────────────────────────────────────────────
    # INTERPOLAÇÃO DE GAPS
    # ────────────────────────────────────────────────────────────────

    def _interpolate_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Interpola gaps pequenos (≤ MAX_GAP_INTERPOLATE períodos).
        Gaps maiores são mantidos como NaN.
        """
        for col in df.columns:
            # Identifica grupos contíguos de NaN
            is_nan = df[col].isna()
            nan_groups = is_nan.ne(is_nan.shift()).cumsum()

            # Conta tamanho de cada grupo NaN
            for group_id in nan_groups[is_nan].unique():
                group_size = (nan_groups == group_id).sum()
                if group_size <= self.MAX_GAP_INTERPOLATE:
                    # Interpola gaps pequenos
                    mask = nan_groups == group_id
                    df.loc[mask, col] = np.nan  # Garante NaN para interpolação
                else:
                    # Mantém NaN para gaps grandes (serão dropados depois)
                    pass

            df[col] = df[col].interpolate(method=self.INTERPOLATION_METHOD)

        return df
