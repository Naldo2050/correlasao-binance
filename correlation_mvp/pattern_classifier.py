"""
Classificador de Padrões de Correlação - CORR-WATCH MVP
Identifica padrões conhecidos em dados de correlação multi-timeframe
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CorrelationPattern(Enum):
    """Padrões de correlação identificáveis"""
    STRENGTHENING = "STRENGTHENING"           # Correlação aumentando
    WEAKENING = "WEAKENING"                   # Correlação diminuindo
    BREAKOUT = "BREAKOUT"                     # Quebra de padrão estabelecido
    REVERSAL = "REVERSAL"                     # Reversão de direção
    CONSOLIDATION = "CONSOLIDATION"           # Consolidação/lateralização
    V_SHAPE = "V_SHAPE"                       # Recuperação rápida
    INVERSE_V = "INVERSE_V"                   # Queda rápida
    DIVERGENCE_WIDENING = "DIVERGENCE_WIDENING"  # Divergência aumentando
    CONVERGENCE = "CONVERGENCE"               # Timeframes convergindo


class PatternClassifier:
    """
    Classificador de padrões em correlações multi-timeframe
    
    Analisa sequências de correlações para identificar padrões
    que podem indicar oportunidades de trading ou mudanças de regime
    """
    
    def __init__(self, lookback_periods: int = 5):
        """
        Args:
            lookback_periods: Número de períodos para análise de padrão
        """
        self.lookback_periods = lookback_periods
        
    def classify_pattern(
        self,
        correlations: Dict[str, float],
        history: List[Dict[str, float]] = None
    ) -> Dict:
        """
        Classifica padrão atual de correlação
        
        Args:
            correlations: Correlações atuais {tf: corr}
            history: Histórico de correlações [
                {tf: corr, timestamp: ...},
                ...
            ]
        
        Returns:
            Dict com classificação:
            {
                'pattern': CorrelationPattern,
                'confidence': float (0-1),
                'description': str,
                'timeframe_consistency': float,
                'trend_direction': str,
                'strength': float
            }
        """
        # Se não tem histórico, apenas análise instantânea
        if not history or len(history) < 2:
            return self._analyze_instant_pattern(correlations)
        
        # Análise com histórico
        return self._analyze_pattern_with_history(correlations, history)
    
    def _analyze_instant_pattern(
        self,
        correlations: Dict[str, float]
    ) -> Dict:
        """Análise de padrão instantâneo (sem histórico)"""
        
        timeframes = ['5m', '15m', '1h', '4h', '1d']
        values = [
            correlations.get(tf, np.nan)
            for tf in timeframes
            if tf in correlations
        ]
        
        # Remover NaN
        values = [v for v in values if not pd.isna(v)]
        
        if len(values) < 3:
            return {
                'pattern': CorrelationPattern.CONSOLIDATION,
                'confidence': 0.0,
                'description': 'Dados insuficientes',
                'timeframe_consistency': 0.0,
                'trend_direction': 'UNKNOWN',
                'strength': 0.0
            }
        
        # Calcular tendência (linear regression simples)
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # Calcular consistência (desvio padrão)
        std = np.std(values)
        consistency = max(0, 1 - std)
        
        # Determinar padrão baseado em slope e consistência
        if abs(slope) < 0.05:
            pattern = CorrelationPattern.CONSOLIDATION
            direction = 'NEUTRAL'
        elif slope > 0.15:
            pattern = CorrelationPattern.STRENGTHENING
            direction = 'UP'
        elif slope < -0.15:
            pattern = CorrelationPattern.WEAKENING
            direction = 'DOWN'
        elif slope > 0:
            pattern = CorrelationPattern.STRENGTHENING
            direction = 'SLIGHT_UP'
        else:
            pattern = CorrelationPattern.WEAKENING
            direction = 'SLIGHT_DOWN'
        
        confidence = min(abs(slope) * 2, 1.0) * consistency
        
        return {
            'pattern': pattern,
            'confidence': round(confidence, 3),
            'description': self._pattern_description(pattern),
            'timeframe_consistency': round(consistency, 3),
            'trend_direction': direction,
            'strength': round(abs(slope), 3)
        }
    
    def _analyze_pattern_with_history(
        self,
        current: Dict[str, float],
        history: List[Dict[str, float]]
    ) -> Dict:
        """Análise de padrão com histórico"""
        
        # Pegar timeframe principal (1h)
        tf_key = '1h'
        
        # Extrair série temporal
        series = []
        for hist_entry in history[-self.lookback_periods:]:
            val = hist_entry.get(tf_key)
            if val is not None and not pd.isna(val):
                series.append(val)
        
        # Adicionar valor atual
        current_val = current.get(tf_key)
        if current_val is not None and not pd.isna(current_val):
            series.append(current_val)
        
        if len(series) < 3:
            return self._analyze_instant_pattern(current)
        
        # Detectar padrões específicos
        pattern, confidence = self._detect_specific_pattern(series)
        
        # Calcular direção de tendência
        slope = np.polyfit(range(len(series)), series, 1)[0]
        
        if slope > 0.1:
            direction = 'UP'
        elif slope < -0.1:
            direction = 'DOWN'
        else:
            direction = 'NEUTRAL'
        
        # Consistência entre timeframes
        consistency = self._calculate_mtf_consistency(current)
        
        return {
            'pattern': pattern,
            'confidence': round(confidence, 3),
            'description': self._pattern_description(pattern),
            'timeframe_consistency': round(consistency, 3),
            'trend_direction': direction,
            'strength': round(abs(slope), 3)
        }
    
    def _detect_specific_pattern(
        self,
        series: List[float]
    ) -> Tuple[CorrelationPattern, float]:
        """
        Detecta padrões específicos na série
        
        Returns:
            (pattern, confidence)
        """
        if len(series) < 3:
            return CorrelationPattern.CONSOLIDATION, 0.0
        
        # Calcular derivadas (mudanças)
        changes = np.diff(series)
        
        # Padrão V (queda seguida de recuperação)
        if (len(changes) >= 4 and
            changes[0] < -0.1 and changes[1] < -0.1 and
            changes[-2] > 0.1 and changes[-1] > 0.1):
            return CorrelationPattern.V_SHAPE, 0.8
        
        # Padrão V invertido (subida seguida de queda)
        if (len(changes) >= 4 and
            changes[0] > 0.1 and changes[1] > 0.1 and
            changes[-2] < -0.1 and changes[-1] < -0.1):
            return CorrelationPattern.INVERSE_V, 0.8
        
        # Reversão (mudança de direção clara)
        if len(changes) >= 2:
            early_trend = np.mean(changes[:len(changes)//2])
            late_trend = np.mean(changes[len(changes)//2:])
            
            if early_trend > 0.1 and late_trend < -0.1:
                return CorrelationPattern.REVERSAL, 0.7
            elif early_trend < -0.1 and late_trend > 0.1:
                return CorrelationPattern.REVERSAL, 0.7
        
        # Breakout (mudança súbita)
        if any(abs(change) > 0.3 for change in changes):
            return CorrelationPattern.BREAKOUT, 0.9
        
        # Tendências
        overall_change = series[-1] - series[0]
        
        if overall_change > 0.2:
            return CorrelationPattern.STRENGTHENING, 0.6
        elif overall_change < -0.2:
            return CorrelationPattern.WEAKENING, 0.6
        else:
            return CorrelationPattern.CONSOLIDATION, 0.5
    
    def _calculate_mtf_consistency(
        self,
        correlations: Dict[str, float]
    ) -> float:
        """
        Calcula consistência entre timeframes
        
        Returns:
            0-1, onde 1 = perfeitamente consistente
        """
        values = [
            v for v in correlations.values()
            if not pd.isna(v)
        ]
        
        if len(values) < 2:
            return 0.0
        
        # Desvio padrão normalizado
        std = np.std(values)
        
        # Consistência inversa ao desvio
        # std=0 → consistency=1
        # std=1 → consistency=0
        consistency = max(0, 1 - std)
        
        return consistency
    
    def _pattern_description(self, pattern: CorrelationPattern) -> str:
        """Retorna descrição do padrão"""
        descriptions = {
            CorrelationPattern.STRENGTHENING: "Correlação está se fortalecendo progressivamente",
            CorrelationPattern.WEAKENING: "Correlação está enfraquecendo",
            CorrelationPattern.BREAKOUT: "Quebra de padrão anterior detectada",
            CorrelationPattern.REVERSAL: "Reversão de tendência em andamento",
            CorrelationPattern.CONSOLIDATION: "Correlação consolidando em faixa estreita",
            CorrelationPattern.V_SHAPE: "Recuperação rápida após queda (V-shape)",
            CorrelationPattern.INVERSE_V: "Queda rápida após alta (V invertido)",
            CorrelationPattern.DIVERGENCE_WIDENING: "Divergência entre timeframes aumentando",
            CorrelationPattern.CONVERGENCE: "Timeframes convergindo para mesma correlação"
        }
        
        return descriptions.get(pattern, "Padrão desconhecido")
    
    def get_trading_implication(
        self,
        pattern: CorrelationPattern,
        confidence: float
    ) -> str:
        """
        Retorna implicação para trading baseado no padrão
        
        Args:
            pattern: Padrão detectado
            confidence: Confiança na detecção
        
        Returns:
            String com implicação
        """
        if confidence < 0.5:
            return "Confiança baixa, aguardar confirmação"
        
        implications = {
            CorrelationPattern.STRENGTHENING: "Possível início de tendência forte, considerar posição alinhada",
            CorrelationPattern.WEAKENING: "Possível fim de tendência, considerar reduzir exposição",
            CorrelationPattern.BREAKOUT: "Movimento forte iniciando, atenção para entrada",
            CorrelationPattern.REVERSAL: "Reversão detectada, considerar operação contrária",
            CorrelationPattern.CONSOLIDATION: "Aguardar breakout, evitar operar na lateral",
            CorrelationPattern.V_SHAPE: "Recuperação forte, possível entrada long",
            CorrelationPattern.INVERSE_V: "Correção forte, possível entrada short"
        }
        
        return implications.get(pattern, "Padrão neutro, sem ação clara")
