"""
CORR-WATCH System v2.0 — Matriz de Correlação NxN
==================================================
Calcula e gerencia a matriz de correlação entre todos os pares
monitorados. Suporte a múltiplas janelas e serialização.

Referência: CORRELAÇÃO BINANCE(copia).md — Seção 4.1 (Correlação Matrix)
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger("corr_watch.engine.correlation_matrix")


class CorrelationMatrix:
    """
    Gerencia a matriz NxN de correlações entre todos os ativos monitorados.
    
    Funcionalidades:
      - Calcula matriz de correlação para N ativos
      - Suporta múltiplas janelas rolling
      - Identifica top-N pares mais/menos correlacionados
      - Detecta mudanças significativas entre atualizações
      - Serializa para JSON/dict (para dashboard)
    
    Uso:
        matrix = CorrelationMatrix(symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"])
        matrix.update(aligned_data, window=50)
        
        print(matrix.get_correlation("BTCUSDT", "ETHUSDT"))
        top = matrix.get_top_pairs(n=5, highest=True)
        changes = matrix.get_significant_changes(threshold=0.10)
    """

    def __init__(self, symbols: Optional[List[str]] = None):
        self.symbols: List[str] = symbols or []
        self._matrices: Dict[int, pd.DataFrame] = {}  # window -> DataFrame NxN
        self._previous: Dict[int, pd.DataFrame] = {}   # Snapshot anterior
        self._last_update: Optional[datetime] = None

    @property
    def available_windows(self) -> List[int]:
        """Janelas disponíveis."""
        return list(self._matrices.keys())

    def update(
        self,
        aligned_data: pd.DataFrame,
        windows: Optional[List[int]] = None,
    ) -> None:
        """
        Atualiza a matriz de correlação com dados novos.
        
        Args:
            aligned_data: DataFrame com colunas returns_SYMBOL
            windows: Janelas a calcular [20, 50, 100]
        """
        windows = windows or [20, 50, 100]

        # Extrai colunas de retorno
        return_cols = [c for c in aligned_data.columns if c.startswith("returns_")]
        if not return_cols:
            logger.warning("Sem colunas de retornos nos dados alinhados")
            return

        # Atualiza lista de símbolos a partir dos dados
        self.symbols = [c.replace("returns_", "") for c in return_cols]

        returns_df = aligned_data[return_cols].copy()
        returns_df.columns = self.symbols

        for window in windows:
            # Salva snapshot anterior
            if window in self._matrices:
                self._previous[window] = self._matrices[window].copy()

            # Calcula correlação rolling com a janela
            if len(returns_df) >= window:
                # Usa os últimos `window` períodos
                recent = returns_df.iloc[-window:]
                corr_matrix = recent.corr(method="pearson")
            else:
                corr_matrix = returns_df.corr(method="pearson")

            self._matrices[window] = corr_matrix

        self._last_update = datetime.utcnow()
        logger.debug(
            f"Matriz atualizada: {len(self.symbols)} ativos × "
            f"{len(windows)} janelas"
        )

    def get_correlation(
        self,
        symbol_a: str,
        symbol_b: str,
        window: int = 50,
    ) -> Optional[float]:
        """Retorna a correlação entre dois símbolos para uma janela."""
        matrix = self._matrices.get(window)
        if matrix is None:
            return None
        if symbol_a not in matrix.columns or symbol_b not in matrix.columns:
            return None
        return float(matrix.loc[symbol_a, symbol_b])

    def get_matrix(self, window: int = 50) -> Optional[pd.DataFrame]:
        """Retorna a matriz completa para uma janela."""
        return self._matrices.get(window)

    def get_top_pairs(
        self,
        window: int = 50,
        n: int = 5,
        highest: bool = True,
    ) -> List[Tuple[str, str, float]]:
        """
        Retorna os top-N pares mais ou menos correlacionados.
        
        Args:
            window: Janela de correlação
            n: Número de pares
            highest: True = mais correlacionados, False = menos
            
        Returns:
            Lista de tuplas (symbol_a, symbol_b, correlation)
        """
        matrix = self._matrices.get(window)
        if matrix is None:
            return []

        pairs = []
        symbols = matrix.columns.tolist()

        for i, sym_a in enumerate(symbols):
            for j, sym_b in enumerate(symbols):
                if i >= j:  # Evita duplicatas e diagonal
                    continue
                corr = float(matrix.loc[sym_a, sym_b])
                if not np.isnan(corr):
                    pairs.append((sym_a, sym_b, corr))

        # Ordena
        pairs.sort(key=lambda x: x[2], reverse=highest)

        return pairs[:n]

    def get_significant_changes(
        self,
        window: int = 50,
        threshold: float = 0.10,
    ) -> List[Tuple[str, str, float, float, float]]:
        """
        Detecta mudanças significativas desde a última atualização.
        
        Args:
            window: Janela de correlação
            threshold: Mudança mínima para considerar significativa
            
        Returns:
            Lista de tuplas (sym_a, sym_b, old_corr, new_corr, delta)
        """
        current = self._matrices.get(window)
        previous = self._previous.get(window)

        if current is None or previous is None:
            return []

        changes = []
        symbols = current.columns.tolist()

        for i, sym_a in enumerate(symbols):
            for j, sym_b in enumerate(symbols):
                if i >= j:
                    continue
                if sym_a not in previous.columns or sym_b not in previous.columns:
                    continue

                old_val = float(previous.loc[sym_a, sym_b])
                new_val = float(current.loc[sym_a, sym_b])

                if np.isnan(old_val) or np.isnan(new_val):
                    continue

                delta = new_val - old_val
                if abs(delta) >= threshold:
                    changes.append((sym_a, sym_b, old_val, new_val, delta))

        changes.sort(key=lambda x: abs(x[4]), reverse=True)
        return changes

    def to_dict(self, window: int = 50) -> Dict:
        """
        Serializa a matriz para formato dict/JSON.
        Útil para envio ao dashboard via WebSocket.
        """
        matrix = self._matrices.get(window)
        if matrix is None:
            return {}

        return {
            "window": window,
            "symbols": self.symbols,
            "matrix": matrix.values.tolist(),
            "timestamp": self._last_update.isoformat() if self._last_update else None,
        }

    def format_table(self, window: int = 50) -> str:
        """
        Formata a matriz como tabela legível para console.
        """
        matrix = self._matrices.get(window)
        if matrix is None:
            return "Sem dados"

        # Header
        symbols = matrix.columns.tolist()
        # Abrevia símbolos
        short = [s.replace("USDT", "") for s in symbols]

        header = f"{'':>10}" + "".join(f"{s:>10}" for s in short)
        lines = [f"\n{'═' * len(header)}", f"  MATRIZ DE CORRELAÇÃO (Window={window})", f"{'═' * len(header)}", header, "─" * len(header)]

        for i, sym in enumerate(symbols):
            row = f"{short[i]:>10}"
            for j, sym2 in enumerate(symbols):
                val = matrix.iloc[i, j]
                if i == j:
                    row += f"{'1.00':>10}"
                elif np.isnan(val):
                    row += f"{'N/A':>10}"
                else:
                    row += f"{val:>10.4f}"
            lines.append(row)

        lines.append("─" * len(header))
        return "\n".join(lines)
