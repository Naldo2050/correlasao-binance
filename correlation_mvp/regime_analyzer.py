"""
Analisador de Mudança de Regime - CORR-WATCH MVP
Detecta mudanças significativas no comportamento de correlação
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

from typing import Dict, List, Optional
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CorrelationRegime(Enum):
    """Regimes de correlação"""
    STRONG_POSITIVE = "STRONG_POSITIVE"       # >0.7
    MODERATE_POSITIVE = "MODERATE_POSITIVE"   # 0.3-0.7
    NEUTRAL = "NEUTRAL"                       # -0.3-0.3
    MODERATE_NEGATIVE = "MODERATE_NEGATIVE"   # -0.7--0.3
    STRONG_NEGATIVE = "STRONG_NEGATIVE"       # <-0.7
    UNSTABLE = "UNSTABLE"                     # Alta variação


class RegimeAnalyzer:
    """
    Analisador de regime de correlação
    
    Identifica em qual regime o par está operando e
    detecta mudanças significativas
    """
    
    def __init__(
        self,
        history_size: int = 50,
        change_threshold: float = 0.30
    ):
        """
        Args:
            history_size: Tamanho do histórico a manter
            change_threshold: Threshold para detectar mudança de regime
        """
        self.history_size = history_size
        self.change_threshold = change_threshold
        
        # Histórico por par
        self.regime_history: Dict[str, List[Dict]] = {}
    
    def identify_regime(
        self,
        correlation: float,
        volatility: float = None
    ) -> CorrelationRegime:
        """
        Identifica regime atual baseado na correlação
        
        Args:
            correlation: Correlação atual
            volatility: Volatilidade da correlação (opcional)
        
        Returns:
            CorrelationRegime
        """
        # Se alta volatilidade, regime instável
        if volatility and volatility > 0.3:
            return CorrelationRegime.UNSTABLE
        
        # Classificar baseado em correlação
        if correlation > 0.7:
            return CorrelationRegime.STRONG_POSITIVE
        elif correlation > 0.3:
            return CorrelationRegime.MODERATE_POSITIVE
        elif correlation > -0.3:
            return CorrelationRegime.NEUTRAL
        elif correlation > -0.7:
            return CorrelationRegime.MODERATE_NEGATIVE
        else:
            return CorrelationRegime.STRONG_NEGATIVE
    
    def detect_regime_change(
        self,
        pair: str,
        current_correlation: float,
        current_regime: CorrelationRegime
    ) -> Optional[Dict]:
        """
        Detecta mudança de regime
        
        Args:
            pair: Nome do par
            current_correlation: Correlação atual
            current_regime: Regime atual
        
        Returns:
            Dict com detalhes da mudança ou None
        """
        # Obter histórico
        if pair not in self.regime_history:
            self.regime_history[pair] = []
        
        history = self.regime_history[pair]
        
        # Se não tem histórico suficiente, adicionar e retornar
        if len(history) < 5:
            self._add_to_history(pair, current_correlation, current_regime)
            return None
        
        # Obter regime anterior
        previous_regime = history[-1]['regime']
        previous_corr = history[-1]['correlation']
        
        # Calcular mudança
        corr_change = abs(current_correlation - previous_corr)
        
        # Detectar mudança
        regime_changed = previous_regime != current_regime
        significant_change = corr_change > self.change_threshold
        
        if regime_changed or significant_change:
            change_info = {
                'pair': pair,
                'timestamp': datetime.now().isoformat(),
                'previous_regime': previous_regime,
                'current_regime': current_regime,
                'previous_correlation': round(previous_corr, 3),
                'current_correlation': round(current_correlation, 3),
                'change': round(corr_change, 3),
                'is_regime_change': regime_changed,
                'is_significant': significant_change,
                'direction': 'STRENGTHENING' if current_correlation > previous_corr else 'WEAKENING'
            }
            
            logger.warning(
                f"Mudança de regime detectada em {pair}: "
                f"{previous_regime.value} → {current_regime.value} "
                f"(Δ={corr_change:.2f})"
            )
            
            # Adicionar ao histórico
            self._add_to_history(pair, current_correlation, current_regime)
            
            return change_info
        
        # Sem mudança, apenas atualizar histórico
        self._add_to_history(pair, current_correlation, current_regime)
        return None
    
    def _add_to_history(
        self,
        pair: str,
        correlation: float,
        regime: CorrelationRegime
    ):
        """Adiciona entrada ao histórico"""
        if pair not in self.regime_history:
            self.regime_history[pair] = []
        
        entry = {
            'timestamp': datetime.now(),
            'correlation': correlation,
            'regime': regime
        }
        
        self.regime_history[pair].append(entry)
        
        # Manter limite
        if len(self.regime_history[pair]) > self.history_size:
            self.regime_history[pair] = self.regime_history[pair][-self.history_size:]
    
    def get_regime_stability(self, pair: str) -> float:
        """
        Calcula estabilidade do regime (0-1)
        
        Returns:
            0 = muito instável, 1 = muito estável
        """
        if pair not in self.regime_history or len(self.regime_history[pair]) < 10:
            return 0.5  # Neutro se não tem dados
        
        history = self.regime_history[pair][-20:]  # Últimos 20 períodos
        
        # Contar mudanças de regime
        changes = 0
        for i in range(1, len(history)):
            if history[i]['regime'] != history[i-1]['regime']:
                changes += 1
        
        # Calcular estabilidade (menos mudanças = mais estável)
        stability = 1 - (changes / len(history))
        
        return round(stability, 3)
    
    def get_regime_duration(self, pair: str) -> Optional[int]:
        """
        Retorna há quantos períodos está no regime atual
        
        Returns:
            Número de períodos ou None
        """
        if pair not in self.regime_history or not self.regime_history[pair]:
            return None
        
        history = self.regime_history[pair]
        current_regime = history[-1]['regime']
        
        duration = 1
        for i in range(len(history) - 2, -1, -1):
            if history[i]['regime'] == current_regime:
                duration += 1
            else:
                break
        
        return duration
