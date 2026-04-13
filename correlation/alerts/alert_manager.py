"""
CORR-WATCH System v2.0 — Alert Manager
========================================
Roteia anomalias e mudanças de regime para notificações
com capacidade de rate-limiting (cooldown) para não afogar
o canal de alertas (ex: Telegram).
"""

import logging
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

from correlation.config import AlertConfig
from correlation.detector.anomaly_detector import Anomaly, AnomalySeverity
from correlation.detector.regime_change_detector import RegimeChangeEvent

logger = logging.getLogger("corr_watch.alerts")

@dataclass
class AlertMessage:
    pair_id: str
    severity: str
    title: str
    details: str
    timestamp: float

class AlertManager:
    def __init__(self, config: AlertConfig):
        self.config = config
        self._last_alert_time: Dict[str, float] = {}
        
    def process(
        self, 
        anomalies: List[Anomaly], 
        regime_events: List[RegimeChangeEvent]
    ) -> List[AlertMessage]:
        """Processa anomalias e gera mensagens filtradas por cooldown."""
        alerts = []
        now = time.time()
        
        # Filtra apenas anomalias severas
        critical_anomalies = [
            a for a in anomalies 
            if a.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL)
        ]
        
        for a in critical_anomalies:
            alert_key = f"anomaly_{a.pair_id}_{a.anomaly_type.name}"
            
            if self._can_alert(alert_key, now):
                alerts.append(
                    AlertMessage(
                        pair_id=a.pair_id,
                        severity=a.severity.value,
                        title=f"{a.severity_icon} {a.pair_id} | {a.anomaly_type.value}",
                        details=a.description,
                        timestamp=now
                    )
                )
                self._update_cooldown(alert_key, now)
                
        # Mudanças de Regime significativas
        for r in regime_events:
            alert_key = f"regime_{r.pair_id}"
            
            if self._can_alert(alert_key, now) and r.is_significant:
                alerts.append(
                    AlertMessage(
                        pair_id=r.pair_id,
                        severity="HIGH",
                        title=f"🔄 {r.pair_id} | Mudança de Regime",
                        details=f"{r.previous_regime.value} → {r.current_regime.value}\n{r.description}",
                        timestamp=now
                    )
                )
                self._update_cooldown(alert_key, now)
                
        self._dispatch(alerts)
        return alerts

    def _can_alert(self, key: str, current_time: float) -> bool:
        last_time = self._last_alert_time.get(key, 0.0)
        return (current_time - last_time) >= self.config.cooldown_seconds
        
    def _update_cooldown(self, key: str, current_time: float):
        self._last_alert_time[key] = current_time

    def _dispatch(self, alerts: List[AlertMessage]):
        if not alerts:
            return
            
        for channel in self.config.notification_channels:
            if channel == "log":
                for a in alerts:
                    logger.warning(f"ALERT [{a.severity}] {a.title}: {a.details}")
            elif channel == "console":
                print("\n" + "═" * 60)
                print(f"  🔔 {len(alerts)} NOVOS ALERTAS CRÍTICOS")
                print("═" * 60)
                for a in alerts:
                    print(f"  {a.title}")
                    print(f"  └─ {a.details}")
                print("═" * 60 + "\n")
