"""
Multi-Timeframe Engine - CORR-WATCH MVP
Reamostra dados de timeframe granular para múltiplos timeframes maiores
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MultiTimeframeEngine:
    """
    Motor de análise multi-timeframe otimizado
    
    Estratégia:
    - Busca dados em timeframe granular (5m ou 15m)
    - Reamostra localmente para timeframes maiores
    - Reduz requisições de API em até 80%
    """
    
    # Mapeamento de timeframes para pandas resample
    RESAMPLE_MAP = {
        '1m': '1min',
        '5m': '5min',
        '15m': '15min',
        '30m': '30min',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d',
        '1w': '1W'
    }
    
    # Timeframes suportados
    SUPPORTED_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
    
    def __init__(self, timeframes: List[str] = None):
        """
        Inicializa motor multi-timeframe
        
        Args:
            timeframes: Lista de timeframes a monitorar
                       Default: ['5m', '15m', '1h', '4h', '1d']
        """
        self.timeframes = timeframes or ['5m', '15m', '1h', '4h', '1d']
        
        # Validar timeframes
        for tf in self.timeframes:
            if tf not in self.SUPPORTED_TIMEFRAMES:
                logger.warning(f"Timeframe {tf} não suportado, ignorando")
                self.timeframes.remove(tf)
        
        logger.info(f"Motor MTF inicializado: {len(self.timeframes)} timeframes")
    
    def resample_ohlcv(
        self, 
        df: pd.DataFrame, 
        target_timeframe: str
    ) -> pd.DataFrame:
        """
        Reamostra dados OHLCV para timeframe maior
        
        Args:
            df: DataFrame com colunas [timestamp, open, high, low, close, volume]
            target_timeframe: Timeframe alvo (ex: '1h', '4h', '1d')
        
        Returns:
            DataFrame reamostrado com mesma estrutura
        
        Raises:
            ValueError: Se timeframe não suportado
        """
        if target_timeframe not in self.RESAMPLE_MAP:
            raise ValueError(
                f"Timeframe {target_timeframe} não suportado. "
                f"Use um de: {', '.join(self.SUPPORTED_TIMEFRAMES)}"
            )
        
        # Criar cópia para não modificar original
        df_copy = df.copy()
        
        # Garantir que timestamp é index
        if 'timestamp' in df_copy.columns:
            df_copy = df_copy.set_index('timestamp')
        
        # Garantir que index é datetime
        if not isinstance(df_copy.index, pd.DatetimeIndex):
            df_copy.index = pd.to_datetime(df_copy.index)
        
        # Regra de reamostração
        rule = self.RESAMPLE_MAP[target_timeframe]
        
        # Reamostrar
        try:
            resampled = df_copy.resample(rule).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            # Resetar index para manter consistência
            result = resampled.reset_index()
            
            logger.debug(
                f"Reamostrado {len(df_copy)} → {len(result)} candles "
                f"para {target_timeframe}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao reamostrar para {target_timeframe}: {e}")
            return pd.DataFrame()
    
    def calculate_multi_timeframe_correlation(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame,
        base_timeframe: str = '5m',
        window: int = 50
    ) -> Dict[str, float]:
        """
        Calcula correlação em múltiplos timeframes a partir de dados base
        
        Args:
            df_a: DataFrame do ativo A (timeframe base)
            df_b: DataFrame do ativo B (timeframe base)
            base_timeframe: Timeframe dos dados de entrada
            window: Janela de correlação (número de períodos)
        
        Returns:
            Dict {timeframe: correlação} para cada TF monitorado
        
        Exemplo:
            {
                '5m': 0.85,
                '15m': 0.87,
                '1h': 0.89,
                '4h': 0.91,
                '1d': 0.88
            }
        """
        results = {}
        
        for tf in self.timeframes:
            try:
                # Se timeframe é o mesmo da base, usar direto
                if tf == base_timeframe:
                    df_a_tf = df_a.copy()
                    df_b_tf = df_b.copy()
                else:
                    # Reamostrar para timeframe maior
                    df_a_tf = self.resample_ohlcv(df_a.copy(), tf)
                    df_b_tf = self.resample_ohlcv(df_b.copy(), tf)
                
                # Verificar se tem dados suficientes
                if len(df_a_tf) < 2 or len(df_b_tf) < 2:
                    logger.warning(
                        f"Timeframe {tf}: dados insuficientes "
                        f"(A={len(df_a_tf)}, B={len(df_b_tf)})"
                    )
                    results[tf] = np.nan
                    continue
                
                # Sincronizar timestamps
                df_a_tf = df_a_tf.set_index('timestamp') if 'timestamp' in df_a_tf.columns else df_a_tf
                df_b_tf = df_b_tf.set_index('timestamp') if 'timestamp' in df_b_tf.columns else df_b_tf
                
                # Merge por timestamp (inner join = apenas comuns)
                merged = pd.merge(
                    df_a_tf[['close']],
                    df_b_tf[['close']],
                    left_index=True,
                    right_index=True,
                    suffixes=('_a', '_b')
                )
                
                # Verificar janela mínima
                if len(merged) < window:
                    logger.warning(
                        f"Timeframe {tf}: apenas {len(merged)} períodos "
                        f"(mínimo: {window})"
                    )
                    results[tf] = np.nan
                    continue
                
                # Calcular correlação dos últimos N períodos
                close_a = merged['close_a'].tail(window).values
                close_b = merged['close_b'].tail(window).values
                
                # Correlação de Pearson
                if len(close_a) < 2:
                    results[tf] = np.nan
                else:
                    corr = np.corrcoef(close_a, close_b)[0, 1]
                    results[tf] = corr
                    
                    logger.debug(f"Correlação {tf}: {corr:.3f}")
                
            except Exception as e:
                logger.error(f"Erro ao calcular correlação {tf}: {e}")
                results[tf] = np.nan
        
        return results
    
    def calculate_mtf_score(
        self,
        correlations: Dict[str, float],
        expected_corr: float,
        weights: Dict[str, float] = None
    ) -> Dict:
        """
        Calcula score de alinhamento multi-timeframe
        
        Args:
            correlations: Dict de correlações por timeframe
            expected_corr: Correlação esperada do par
            weights: Pesos por timeframe (opcional)
        
        Returns:
            Dict com:
                - score: Score final 0-100
                - aligned_count: Quantos TFs estão alinhados
                - total_timeframes: Total de TFs válidos
                - alignment_rate: Taxa de alinhamento (0-1)
                - avg_deviation: Desvio médio ponderado
                - status: 'ALIGNED', 'PARTIAL', 'DIVERGENT'
        """
        # Pesos padrão por timeframe (maior peso para TF principal)
        if weights is None:
            weights = {
                '5m': 0.10,
                '15m': 0.15,
                '1h': 0.30,   # Timeframe principal
                '4h': 0.25,
                '1d': 0.20
            }
        
        # Métricas
        aligned_count = 0
        total_valid = 0
        weighted_deviation = 0
        
        # Threshold de alinhamento (20% de desvio aceitável)
        ALIGNMENT_THRESHOLD = 0.20
        
        for tf, corr in correlations.items():
            # Ignorar valores inválidos
            if pd.isna(corr):
                continue
            
            total_valid += 1
            
            # Calcular desvio da expectativa
            deviation = abs(corr - expected_corr)
            weight = weights.get(tf, 0.10)
            
            # Considerar alinhado se desvio < threshold
            if deviation < ALIGNMENT_THRESHOLD:
                aligned_count += 1
            
            # Acumular desvio ponderado
            weighted_deviation += deviation * weight
        
        # Calcular scores
        if total_valid == 0:
            return {
                'score': 0,
                'aligned_count': 0,
                'total_timeframes': 0,
                'alignment_rate': 0,
                'avg_deviation': 0,
                'status': 'NO_DATA'
            }
        
        # Score baseado em alinhamento (quantos TFs concordam)
        alignment_score = (aligned_count / total_valid) * 100
        
        # Score baseado em desvio (quão próximo da expectativa)
        deviation_score = max(0, 100 - (weighted_deviation * 100))
        
        # Score final (média ponderada)
        # 60% pelo alinhamento, 40% pela precisão
        final_score = (alignment_score * 0.6) + (deviation_score * 0.4)
        
        # Taxa de alinhamento
        alignment_rate = aligned_count / total_valid
        
        # Determinar status
        if alignment_rate >= 0.8:
            status = 'ALIGNED'      # >= 80% alinhados
        elif alignment_rate >= 0.5:
            status = 'PARTIAL'      # 50-79% alinhados
        else:
            status = 'DIVERGENT'    # < 50% alinhados
        
        return {
            'score': round(final_score, 2),
            'aligned_count': aligned_count,
            'total_timeframes': total_valid,
            'alignment_rate': round(alignment_rate, 3),
            'avg_deviation': round(weighted_deviation, 3),
            'status': status
        }
    
    def detect_timeframe_divergence(
        self,
        correlations: Dict[str, float],
        threshold: float = 0.30
    ) -> Tuple[bool, Dict]:
        """
        Detecta divergências significativas entre timeframes
        
        Uma divergência ocorre quando:
        - Timeframes curtos (5m, 15m) têm correlação diferente de longos (4h, 1d)
        - Diferença > threshold (padrão: 30%)
        
        Args:
            correlations: Dict de correlações por timeframe
            threshold: Threshold de divergência (0-1)
        
        Returns:
            Tuple (has_divergence, details)
            
            has_divergence: bool
            details: {
                'short_term_avg': float,
                'long_term_avg': float,
                'divergence': float,
                'direction': 'SHORT_STRONGER' | 'LONG_STRONGER' | 'ALIGNED',
                'significance': 'CRITICAL' | 'MODERATE' | 'LOW'
            }
        """
        # Separar timeframes curtos e longos
        short_term_tfs = ['5m', '15m']
        long_term_tfs = ['4h', '1d']
        
        # Calcular médias
        short_values = [correlations[tf] for tf in short_term_tfs if tf in correlations and not pd.isna(correlations[tf])]
        long_values = [correlations[tf] for tf in long_term_tfs if tf in correlations and not pd.isna(correlations[tf])]
        
        if not short_values or not long_values:
            return False, {
                'short_term_avg': np.nan,
                'long_term_avg': np.nan,
                'divergence': 0,
                'direction': 'NO_DATA',
                'significance': 'LOW'
            }
        
        short_avg = np.mean(short_values)
        long_avg = np.mean(long_values)
        divergence = abs(short_avg - long_avg)
        
        # Determinar direção
        if divergence < 0.10:
            direction = 'ALIGNED'
        elif abs(short_avg) > abs(long_avg):
            direction = 'SHORT_STRONGER'
        else:
            direction = 'LONG_STRONGER'
        
        # Significância
        if divergence > 0.50:
            significance = 'CRITICAL'   # >50% de diferença
        elif divergence > threshold:
            significance = 'MODERATE'   # >30% de diferença
        else:
            significance = 'LOW'        # <30% de diferença
        
        has_divergence = divergence > threshold
        
        details = {
            'short_term_avg': round(short_avg, 3),
            'long_term_avg': round(long_avg, 3),
            'divergence': round(divergence, 3),
            'direction': direction,
            'significance': significance
        }
        
        if has_divergence:
            logger.warning(
                f"Divergência detectada: {divergence:.1%} "
                f"(Short: {short_avg:.2f}, Long: {long_avg:.2f})"
            )
        
        return has_divergence, details


# Singleton para uso global
_mtf_engine = None

def get_mtf_engine(timeframes: List[str] = None) -> MultiTimeframeEngine:
    """Factory function para obter instância singleton"""
    global _mtf_engine
    if _mtf_engine is None:
        _mtf_engine = MultiTimeframeEngine(timeframes)
    return _mtf_engine
