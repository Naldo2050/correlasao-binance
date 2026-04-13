"""
Sistema de Alertas Inteligentes - CORR-WATCH MVP
Gera alertas contextualizados baseados em divergências e padrões
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

from divergence_detector import (
    DivergenceType,
    DivergenceSignificance,
    TimeframeDivergenceDetector
)
from pattern_classifier import CorrelationPattern, PatternClassifier

logger = logging.getLogger(__name__)


class AlertPriority(Enum):
    """Prioridade do alerta"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Tipo de alerta"""
    DIVERGENCE = "DIVERGENCE"
    PATTERN = "PATTERN"
    THRESHOLD = "THRESHOLD"
    REGIME_CHANGE = "REGIME_CHANGE"
    ANOMALY = "ANOMALY"


class SmartAlert:
    """Representação de um alerta inteligente"""
    
    def __init__(
        self,
        pair: str,
        alert_type: AlertType,
        priority: AlertPriority,
        title: str,
        message: str,
        data: Dict,
        timestamp: datetime = None
    ):
        self.pair = pair
        self.alert_type = alert_type
        self.priority = priority
        self.title = title
        self.message = message
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.id = f"{pair}_{alert_type.value}_{self.timestamp.timestamp()}"
    
    def to_dict(self) -> Dict:
        """Converte alerta para dicionário"""
        return {
            'id': self.id,
            'pair': self.pair,
            'type': self.alert_type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }
    
    def format_notification(self) -> str:
        """Formata alerta para notificação (Telegram, etc)"""
        priority_emoji = {
            AlertPriority.LOW: "🟢",
            AlertPriority.MEDIUM: "🟡",
            AlertPriority.HIGH: "🟠",
            AlertPriority.CRITICAL: "🔴"
        }
        
        emoji = priority_emoji.get(self.priority, "⚪")
        
        notification = f"{emoji} **{self.title}**\n"
        notification += f"Par: `{self.pair}`\n"
        notification += f"Tipo: {self.alert_type.value}\n"
        notification += f"Prioridade: {self.priority.value}\n\n"
        notification += f"{self.message}\n\n"
        notification += f"🕐 {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return notification


class SmartAlertSystem:
    """
    Sistema de alertas inteligentes
    
    Gera alertas contextualizados baseados em:
    - Divergências entre timeframes
    - Padrões de correlação
    - Thresholds de score
    - Mudanças de regime
    """
    
    def __init__(
        self,
        cooldown_minutes: int = 5,
        max_alerts_per_pair: int = 3
    ):
        """
        Args:
            cooldown_minutes: Minutos de cooldown entre alertas do mesmo par
            max_alerts_per_pair: Máximo de alertas ativos por par
        """
        self.cooldown_minutes = cooldown_minutes
        self.max_alerts_per_pair = max_alerts_per_pair
        
        self.active_alerts: List[SmartAlert] = []
        self.alert_history: List[SmartAlert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Componentes
        self.divergence_detector = TimeframeDivergenceDetector()
        self.pattern_classifier = PatternClassifier()
        
        logger.info(
            f"Smart Alert System inicializado: "
            f"cooldown={cooldown_minutes}min, max_per_pair={max_alerts_per_pair}"
        )
    
    def analyze_and_alert(
        self,
        pair: str,
        correlations: Dict[str, float],
        z_score: float,
        score: float,
        expected_corr: float = 0.0,
        correlation_history: List[Dict] = None
    ) -> Optional[SmartAlert]:
        """
        Analisa dados e gera alerta se necessário
        
        Args:
            pair: Nome do par
            correlations: Correlações por timeframe
            z_score: Z-Score do spread
            score: Score final
            expected_corr: Correlação esperada
            correlation_history: Histórico de correlações
        
        Returns:
            SmartAlert se alerta gerado, None caso contrário
        """
        # Verificar cooldown
        if not self._check_cooldown(pair):
            logger.debug(f"Cooldown ativo para {pair}, ignorando análise")
            return None
        
        # Verificar limite de alertas
        if self._count_active_alerts(pair) >= self.max_alerts_per_pair:
            logger.debug(f"Limite de alertas atingido para {pair}")
            return None
        
        # Detectar divergência
        divergence = self.divergence_detector.detect_divergence(
            correlations, expected_corr
        )
        
        # Classificar padrão
        pattern_result = self.pattern_classifier.classify_pattern(
            correlations, correlation_history
        )
        
        # Decidir se gera alerta
        alert = self._generate_alert_if_needed(
            pair, correlations, z_score, score,
            divergence, pattern_result
        )
        
        if alert:
            self._add_alert(alert)
            logger.info(f"Alerta gerado: {alert.title} ({alert.priority.value})")
        
        return alert
    
    def _generate_alert_if_needed(
        self,
        pair: str,
        correlations: Dict[str, float],
        z_score: float,
        score: float,
        divergence: Dict,
        pattern: Dict
    ) -> Optional[SmartAlert]:
        """Decide se deve gerar alerta e qual tipo"""
        
        # Prioridade 1: Divergência crítica
        if (divergence['has_divergence'] and
            divergence['significance'] == DivergenceSignificance.CRITICAL):
            
            return SmartAlert(
                pair=pair,
                alert_type=AlertType.DIVERGENCE,
                priority=AlertPriority.CRITICAL,
                title="🚨 Divergência Crítica Detectada",
                message=(
                    f"Divergência extrema entre timeframes!\n"
                    f"{divergence['interpretation']}\n\n"
                    f"📊 Detalhes:\n"
                    f"• Curto prazo: {divergence['short_term_avg']:+.2f}\n"
                    f"• Longo prazo: {divergence['long_term_avg']:+.2f}\n"
                    f"• Divergência: {divergence['divergence_pct']:.1%}\n"
                    f"• Tipo: {divergence['type'].value}\n"
                    f"• Z-Score: {z_score:+.2f}\n"
                    f"• Score: {score:.0f}/100"
                ),
                data={
                    'correlations': correlations,
                    'divergence': divergence,
                    'pattern': pattern,
                    'z_score': z_score,
                    'score': score
                }
            )
        
        # Prioridade 2: Reversão detectada
        if divergence['type'] == DivergenceType.REVERSAL:
            return SmartAlert(
                pair=pair,
                alert_type=AlertType.REGIME_CHANGE,
                priority=AlertPriority.HIGH,
                title="⚠️ Reversão de Correlação",
                message=(
                    f"Possível reversão de tendência detectada!\n"
                    f"{divergence['interpretation']}\n\n"
                    f"📊 Padrão: {pattern['pattern'].value}\n"
                    f"🎯 Confiança: {pattern['confidence']:.0%}\n"
                    f"📈 Score: {score:.0f}/100"
                ),
                data={
                    'correlations': correlations,
                    'divergence': divergence,
                    'pattern': pattern,
                    'z_score': z_score,
                    'score': score
                }
            )
        
        # Prioridade 3: Padrão de breakout
        if (pattern['pattern'] == CorrelationPattern.BREAKOUT and
            pattern['confidence'] > 0.7):
            
            return SmartAlert(
                pair=pair,
                alert_type=AlertType.PATTERN,
                priority=AlertPriority.HIGH,
                title="📈 Breakout Detectado",
                message=(
                    f"Quebra de padrão anterior!\n"
                    f"{pattern['description']}\n\n"
                    f"🎯 Confiança: {pattern['confidence']:.0%}\n"
                    f"📊 Direção: {pattern['trend_direction']}\n"
                    f"💪 Força: {pattern['strength']:.2f}\n"
                    f"📈 Score: {score:.0f}/100"
                ),
                data={
                    'correlations': correlations,
                    'pattern': pattern,
                    'z_score': z_score,
                    'score': score
                }
            )
        
        # Prioridade 4: Score alto
        if score >= 70:
            priority = AlertPriority.HIGH if score >= 80 else AlertPriority.MEDIUM
            
            return SmartAlert(
                pair=pair,
                alert_type=AlertType.THRESHOLD,
                priority=priority,
                title=f"🎯 Score Alto: {score:.0f}/100",
                message=(
                    f"Score de correlação atingiu {score:.0f}/100\n\n"
                    f"📊 Correlação 1h: {correlations.get('1h', 0):+.2f}\n"
                    f"📈 Z-Score: {z_score:+.2f}\n"
                    f"🔄 Padrão: {pattern['pattern'].value}\n"
                    f"🎯 Confiança padrão: {pattern['confidence']:.0%}"
                ),
                data={
                    'correlations': correlations,
                    'pattern': pattern,
                    'z_score': z_score,
                    'score': score
                }
            )
        
        # Prioridade 5: Divergência moderada
        if (divergence['has_divergence'] and
            divergence['significance'] in [DivergenceSignificance.MODERATE, DivergenceSignificance.HIGH]):
            
            return SmartAlert(
                pair=pair,
                alert_type=AlertType.DIVERGENCE,
                priority=AlertPriority.MEDIUM,
                title="📊 Divergência Detectada",
                message=(
                    f"{divergence['interpretation']}\n\n"
                    f"📊 Significância: {divergence['significance'].value}\n"
                    f"🔄 Tipo: {divergence['type'].value}\n"
                    f"📈 Score: {score:.0f}/100"
                ),
                data={
                    'correlations': correlations,
                    'divergence': divergence,
                    'z_score': z_score,
                    'score': score
                }
            )
        
        return None
    
    def _check_cooldown(self, pair: str) -> bool:
        """Verifica se cooldown já passou"""
        if pair not in self.last_alert_time:
            return True
        
        elapsed = datetime.now() - self.last_alert_time[pair]
        return elapsed.total_seconds() > (self.cooldown_minutes * 60)
    
    def _count_active_alerts(self, pair: str) -> int:
        """Conta alertas ativos para um par"""
        return sum(1 for alert in self.active_alerts if alert.pair == pair)
    
    def _add_alert(self, alert: SmartAlert):
        """Adiciona alerta ao sistema"""
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        self.last_alert_time[alert.pair] = alert.timestamp
        
        # Manter limite de histórico
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def dismiss_alert(self, alert_id: str):
        """Remove alerta da lista de ativos"""
        self.active_alerts = [
            a for a in self.active_alerts
            if a.id != alert_id
        ]
    
    def get_active_alerts(
        self,
        pair: str = None,
        priority: AlertPriority = None
    ) -> List[SmartAlert]:
        """Retorna alertas ativos com filtros opcionais"""
        filtered = self.active_alerts
        
        if pair:
            filtered = [a for a in filtered if a.pair == pair]
        
        if priority:
            filtered = [a for a in filtered if a.priority == priority]
        
        return filtered
    
    def get_recent_alerts(
        self,
        minutes: int = 60,
        pair: str = None
    ) -> List[SmartAlert]:
        """Retorna alertas recentes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        recent = [
            a for a in self.alert_history
            if a.timestamp > cutoff
        ]
        
        if pair:
            recent = [a for a in recent if a.pair == pair]
        
        return recent
    
    def clear_old_alerts(self, hours: int = 24):
        """Remove alertas antigos da lista ativa"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        self.active_alerts = [
            a for a in self.active_alerts
            if a.timestamp > cutoff
        ]
