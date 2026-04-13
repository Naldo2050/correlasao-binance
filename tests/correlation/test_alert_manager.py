"""
Testes Unitários — Alert Manager
=================================
"""

import time
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from correlation.config import AlertConfig
from correlation.alerts.alert_manager import AlertManager
from correlation.detector.anomaly_detector import Anomaly, AnomalyType, AnomalySeverity
from correlation.detector.regime_change_detector import RegimeChangeEvent, CorrelationRegime

class TestAlertManager:
    def setup_method(self):
        config = AlertConfig(cooldown_seconds=60, notification_channels=["log"])
        self.manager = AlertManager(config)

    def test_alert_processing(self):
        """Testa se anomalias CRITICAL geram alerta."""
        anomaly = Anomaly(
            pair_id="BTC↔ETH",
            anomaly_type=AnomalyType.SPREAD_EXTREME,
            severity=AnomalySeverity.CRITICAL,
            description="Boom",
            value=3.5, threshold=3.0, deviation_sigma=3.5
        )
        
        alerts = self.manager.process([anomaly], [])
        assert len(alerts) == 1
        assert alerts[0].pair_id == "BTC↔ETH"

    def test_alert_cooldown(self):
        """Testa se o rate limiting bloqueia alertas repetidos."""
        anomaly = Anomaly(
            pair_id="BTC↔ETH",
            anomaly_type=AnomalyType.SPREAD_EXTREME,
            severity=AnomalySeverity.CRITICAL,
            description="Boom",
            value=3.5, threshold=3.0, deviation_sigma=3.5
        )
        
        # Pela primeira vez, passa
        alerts1 = self.manager.process([anomaly], [])
        assert len(alerts1) == 1
        
        # Imediatamente depois, bloqueado pelo cooldown (60s)
        alerts2 = self.manager.process([anomaly], [])
        assert len(alerts2) == 0
        
        # Outra anomalia de tipo diferente passa
        anomaly2 = Anomaly(
            pair_id="BTC↔ETH",
            anomaly_type=AnomalyType.COINTEGRATION_BREAK,
            severity=AnomalySeverity.CRITICAL,
            description="Boom2",
            value=1.5, threshold=1.0, deviation_sigma=1.0
        )
        alerts3 = self.manager.process([anomaly2], [])
        assert len(alerts3) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
