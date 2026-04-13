"""
Detector de Divergências entre Timeframes - CORR-WATCH MVP
Identifica divergências significativas que podem indicar reversão
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DivergenceType(Enum):
    """Tipos de divergência detectados"""
    BULLISH = "BULLISH"           # Short > Long (fortalecendo)
    BEARISH = "BEARISH"           # Short < Long (enfraquecendo)
    NEUTRAL = "NEUTRAL"           # Alinhados
    CRITICAL = "CRITICAL"         # Divergência extrema
    REVERSAL = "REVERSAL"         # Possível reversão de tendência


class DivergenceSignificance(Enum):
    """Significância da divergência"""
    LOW = "LOW"                   # <20% de diferença
    MODERATE = "MODERATE"         # 20-40% de diferença
    HIGH = "HIGH"                 # 40-60% de diferença
    CRITICAL = "CRITICAL"         # >60% de diferença


class TimeframeDivergenceDetector:
    """
    Detector de divergências entre timeframes
    
    Conceito:
    - Timeframes curtos (5m, 15m) reagem primeiro a mudanças
    - Timeframes longos (4h, 1d) mostram tendência estabelecida
    - Divergência significativa = possível mudança de regime
    
    Exemplo:
    - 5m: Correlação = +0.85 (forte positiva)
    - 4h: Correlação = +0.30 (fraca positiva)
    - Divergência: 0.55 (55%)
    - Sinal: Curto prazo está MAIS correlacionado que longo prazo
    - Interpretação: Correlação está AUMENTANDO (bullish)
    """
    
    # Grupos de timeframes
    SHORT_TERM = ['5m', '15m']
    MEDIUM_TERM = ['1h']
    LONG_TERM = ['4h', '1d']
    
    def __init__(
        self,
        moderate_threshold: float = 0.20,
        high_threshold: float = 0.40,
        critical_threshold: float = 0.60
    ):
        """
        Args:
            moderate_threshold: Threshold para divergência moderada
            high_threshold: Threshold para divergência alta
            critical_threshold: Threshold para divergência crítica
        """
        self.moderate_threshold = moderate_threshold
        self.high_threshold = high_threshold
        self.critical_threshold = critical_threshold
        
        logger.info(
            f"Divergence Detector inicializado: "
            f"thresholds={moderate_threshold}/{high_threshold}/{critical_threshold}"
        )
    
    def detect_divergence(
        self,
        correlations: Dict[str, float],
        expected_corr: float = 0.0
    ) -> Dict:
        """
        Detecta divergência entre timeframes curtos e longos
        
        Args:
            correlations: Dict {timeframe: correlation_value}
            expected_corr: Correlação esperada do par
        
        Returns:
            Dict com análise completa de divergência:
            {
                'has_divergence': bool,
                'short_term_avg': float,
                'long_term_avg': float,
                'divergence_value': float,
                'divergence_pct': float,
                'type': DivergenceType,
                'significance': DivergenceSignificance,
                'direction': str,
                'interpretation': str,
                'strength': float (0-1),
                'timestamp': str
            }
        """
        # Separar correlações por grupo
        short_values = [
            correlations[tf] for tf in self.SHORT_TERM
            if tf in correlations and not pd.isna(correlations[tf])
        ]
        
        medium_values = [
            correlations[tf] for tf in self.MEDIUM_TERM
            if tf in correlations and not pd.isna(correlations[tf])
        ]
        
        long_values = [
            correlations[tf] for tf in self.LONG_TERM
            if tf in correlations and not pd.isna(correlations[tf])
        ]
        
        # Verificar se temos dados suficientes
        if not short_values or not long_values:
            return {
                'has_divergence': False,
                'short_term_avg': np.nan,
                'long_term_avg': np.nan,
                'divergence_value': 0,
                'divergence_pct': 0,
                'type': DivergenceType.NEUTRAL,
                'significance': DivergenceSignificance.LOW,
                'direction': 'NO_DATA',
                'interpretation': 'Dados insuficientes',
                'strength': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        # Calcular médias
        short_avg = np.mean(short_values)
        long_avg = np.mean(long_values)
        medium_avg = np.mean(medium_values) if medium_values else (short_avg + long_avg) / 2
        
        # Calcular divergência absoluta
        divergence_value = short_avg - long_avg
        divergence_pct = abs(divergence_value)
        
        # Determinar significância
        if divergence_pct > self.critical_threshold:
            significance = DivergenceSignificance.CRITICAL
        elif divergence_pct > self.high_threshold:
            significance = DivergenceSignificance.HIGH
        elif divergence_pct > self.moderate_threshold:
            significance = DivergenceSignificance.MODERATE
        else:
            significance = DivergenceSignificance.LOW
        
        # Determinar tipo de divergência
        divergence_type = self._classify_divergence_type(
            short_avg, medium_avg, long_avg, expected_corr
        )
        
        # Determinar direção
        if abs(divergence_value) < 0.10:
            direction = 'ALIGNED'
        elif divergence_value > 0:
            direction = 'SHORT_STRONGER'  # Curto prazo mais correlacionado
        else:
            direction = 'LONG_STRONGER'   # Longo prazo mais correlacionado
        
        # Gerar interpretação
        interpretation = self._generate_interpretation(
            divergence_type, direction, significance, short_avg, long_avg
        )
        
        # Calcular strength (0-1)
        strength = min(divergence_pct / self.critical_threshold, 1.0)
        
        # Determinar se tem divergência significativa
        has_divergence = divergence_pct > self.moderate_threshold
        
        result = {
            'has_divergence': has_divergence,
            'short_term_avg': round(short_avg, 3),
            'medium_term_avg': round(medium_avg, 3),
            'long_term_avg': round(long_avg, 3),
            'divergence_value': round(divergence_value, 3),
            'divergence_pct': round(divergence_pct, 3),
            'type': divergence_type,
            'significance': significance,
            'direction': direction,
            'interpretation': interpretation,
            'strength': round(strength, 3),
            'timestamp': datetime.now().isoformat()
        }
        
        if has_divergence:
            logger.warning(
                f"Divergência detectada: {divergence_pct:.1%} "
                f"({significance.value}, {divergence_type.value})"
            )
        
        return result
    
    def _classify_divergence_type(
        self,
        short_avg: float,
        medium_avg: float,
        long_avg: float,
        expected_corr: float
    ) -> DivergenceType:
        """
        Classifica o tipo de divergência
        
        Args:
            short_avg: Correlação média de curto prazo
            medium_avg: Correlação média de médio prazo
            long_avg: Correlação média de longo prazo
            expected_corr: Correlação esperada
        
        Returns:
            DivergenceType
        """
        # Calcular tendência
        trend = short_avg - long_avg
        
        # Verificar se está revertendo
        is_reversing = (
            (expected_corr > 0 and short_avg < 0 and long_avg > 0) or
            (expected_corr < 0 and short_avg > 0 and long_avg < 0)
        )
        
        if is_reversing:
            return DivergenceType.REVERSAL
        
        # Verificar divergência extrema
        if abs(trend) > 0.60:
            return DivergenceType.CRITICAL
        
        # Classificar baseado em tendência
        if trend > 0.20:
            return DivergenceType.BULLISH   # Fortalecendo
        elif trend < -0.20:
            return DivergenceType.BEARISH   # Enfraquecendo
        else:
            return DivergenceType.NEUTRAL   # Alinhado
    
    def _generate_interpretation(
        self,
        div_type: DivergenceType,
        direction: str,
        significance: DivergenceSignificance,
        short_avg: float,
        long_avg: float
    ) -> str:
        """Gera interpretação textual da divergência"""
        
        base = f"Curto: {short_avg:+.2f}, Longo: {long_avg:+.2f}"
        
        if div_type == DivergenceType.BULLISH:
            return (
                f"{base}. Correlação FORTALECENDO no curto prazo. "
                "Possível início de nova tendência ou reforço da atual."
            )
        
        elif div_type == DivergenceType.BEARISH:
            return (
                f"{base}. Correlação ENFRAQUECENDO no curto prazo. "
                "Possível fim de tendência ou reversão iminente."
            )
        
        elif div_type == DivergenceType.REVERSAL:
            return (
                f"{base}. REVERSÃO DETECTADA! "
                "Correlação mudou de sinal entre curto e longo prazo. "
                "Alta probabilidade de mudança de regime."
            )
        
        elif div_type == DivergenceType.CRITICAL:
            return (
                f"{base}. Divergência EXTREMA detectada. "
                "Timeframes completamente desalinhados. "
                "Aguardar confirmação antes de operar."
            )
        
        else:  # NEUTRAL
            return (
                f"{base}. Timeframes ALINHADOS. "
                "Tendência consistente em todos os períodos."
            )
    
    def detect_multiple_pairs(
        self,
        pairs_data: Dict[str, Dict[str, float]],
        expected_correlations: Dict[str, float] = None
    ) -> Dict[str, Dict]:
        """
        Detecta divergências em múltiplos pares
        
        Args:
            pairs_data: Dict {pair_name: {tf: corr}}
            expected_correlations: Dict {pair_name: expected_corr}
        
        Returns:
            Dict {pair_name: divergence_result}
        """
        results = {}
        
        for pair_name, correlations in pairs_data.items():
            expected = 0.0
            if expected_correlations and pair_name in expected_correlations:
                expected = expected_correlations[pair_name]
            
            divergence = self.detect_divergence(correlations, expected)
            results[pair_name] = divergence
        
        return results
    
    def get_top_divergences(
        self,
        divergences: Dict[str, Dict],
        top_n: int = 5,
        min_significance: DivergenceSignificance = DivergenceSignificance.MODERATE
    ) -> List[Tuple[str, Dict]]:
        """
        Retorna top N divergências mais significativas
        
        Args:
            divergences: Resultados de detect_multiple_pairs
            top_n: Número de divergências a retornar
            min_significance: Significância mínima
        
        Returns:
            Lista de tuplas (pair_name, divergence_data) ordenadas por strength
        """
        # Filtrar por significância
        filtered = [
            (pair, div) for pair, div in divergences.items()
            if div['has_divergence'] and 
            self._is_significant_enough(div['significance'], min_significance)
        ]
        
        # Ordenar por strength
        sorted_divs = sorted(
            filtered,
            key=lambda x: x[1]['strength'],
            reverse=True
        )
        
        return sorted_divs[:top_n]
    
    def _is_significant_enough(
        self,
        current: DivergenceSignificance,
        minimum: DivergenceSignificance
    ) -> bool:
        """Verifica se significância é suficiente"""
        significance_order = {
            DivergenceSignificance.LOW: 0,
            DivergenceSignificance.MODERATE: 1,
            DivergenceSignificance.HIGH: 2,
            DivergenceSignificance.CRITICAL: 3
        }
        
        return significance_order[current] >= significance_order[minimum]


class DivergenceHistory:
    """Mantém histórico de divergências para análise de padrões"""
    
    def __init__(self, max_history: int = 100):
        """
        Args:
            max_history: Número máximo de divergências a armazenar
        """
        self.history: List[Dict] = []
        self.max_history = max_history
    
    def add(self, pair: str, divergence: Dict):
        """Adiciona divergência ao histórico"""
        entry = {
            'pair': pair,
            'timestamp': datetime.now().isoformat(),
            **divergence
        }
        
        self.history.append(entry)
        
        # Manter limite
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_pair_history(
        self,
        pair: str,
        last_n: int = 10
    ) -> List[Dict]:
        """Retorna histórico de um par específico"""
        pair_history = [
            entry for entry in self.history
            if entry['pair'] == pair
        ]
        return pair_history[-last_n:]
    
    def get_recent_divergences(
        self,
        minutes: int = 60,
        min_significance: DivergenceSignificance = DivergenceSignificance.MODERATE
    ) -> List[Dict]:
        """Retorna divergências recentes"""
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        recent = [
            entry for entry in self.history
            if (datetime.fromisoformat(entry['timestamp']) > cutoff and
                entry.get('has_divergence', False))
        ]
        
        return recent
    
    def count_by_type(self, last_n: int = 50) -> Dict[str, int]:
        """Conta divergências por tipo"""
        recent = self.history[-last_n:] if len(self.history) > last_n else self.history
        
        counts = {}
        for entry in recent:
            div_type = entry.get('type')
            if div_type:
                type_name = div_type.value if isinstance(div_type, DivergenceType) else str(div_type)
                counts[type_name] = counts.get(type_name, 0) + 1
        
        return counts
