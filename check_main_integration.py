"""
Verifica se main.py está integrado corretamente com novos componentes
"""

import re
from pathlib import Path

print("=" * 70)
print("VERIFICAÇÃO DE INTEGRAÇÃO - main.py")
print("=" * 70)

# Ler main.py
main_py = Path('main.py')

if not main_py.exists():
    print("❌ main.py não encontrado!")
    exit(1)

content = main_py.read_text()

# Verificações
checks = {
    'Import Multi-Timeframe': 'from multi_timeframe_engine import',
    'Import Cache': 'from data_cache import',
    'Import Dashboard': 'from dashboard_mtf import',
    'Import Divergence': 'from divergence_detector import',
    'Import Pattern': 'from pattern_classifier import',
    'Import Alerts': 'from smart_alerts import',
    'Import Regime': 'from regime_analyzer import',
    'MTF Engine Instance': 'self.mtf_engine',
    'Cache Instance': 'self.cache',
    'Dashboard Instance': 'self.dashboard',
    'Alert System Instance': 'self.alert_system',
    'Method analyze_pair_multi_timeframe': 'def analyze_pair_multi_timeframe',
    'Method fetch_data_with_cache': 'def fetch_data_with_cache'
}

results = {}
for check_name, pattern in checks.items():
    found = pattern in content
    results[check_name] = found
    status = "✅" if found else "❌"
    print(f"{status} {check_name}")

print("\n" + "=" * 70)

total = len(results)
passed = sum(results.values())
percentage = (passed / total) * 100

print(f"Integração: {passed}/{total} ({percentage:.0f}%)")

if percentage == 100:
    print("✅ main.py TOTALMENTE INTEGRADO!")
elif percentage >= 80:
    print("⚠️  main.py PARCIALMENTE INTEGRADO - Faltam alguns componentes")
    print("\nFaltando:")
    for name, status in results.items():
        if not status:
            print(f"  ❌ {name}")
elif percentage >= 50:
    print("⚠️  main.py INTEGRAÇÃO INCOMPLETA")
    print("\nVocê precisa adicionar:")
    for name, status in results.items():
        if not status:
            print(f"  ❌ {name}")
else:
    print("❌ main.py NÃO INTEGRADO - Use o código abaixo")
    print("\n" + "="*70)
    print("CÓDIGO NECESSÁRIO PARA INTEGRAÇÃO:")
    print("="*70)
    print("""
# Adicionar no topo do main.py (após outros imports):

from multi_timeframe_engine import MultiTimeframeEngine, get_mtf_engine
from data_cache import DataCache, get_cache
from cache_stats import CacheMonitor
from dashboard_mtf import MultiTimeframeDashboard, create_simple_mtf_table
from correlation_visualizer import CorrelationVisualizer
from divergence_detector import TimeframeDivergenceDetector, DivergenceHistory
from pattern_classifier import PatternClassifier
from smart_alerts import SmartAlertSystem
from regime_analyzer import RegimeAnalyzer

# Adicionar no __init__ da classe principal:

def __init__(self, config_path='config.yaml'):
    # ... código existente ...
    
    # NOVOS componentes
    self.mtf_engine = get_mtf_engine(timeframes=['5m', '15m', '1h', '4h', '1d'])
    self.cache = get_cache(ttl_seconds=300, max_items=100)
    self.cache_monitor = CacheMonitor(self.cache)
    self.dashboard = MultiTimeframeDashboard(cache=self.cache)
    self.visualizer = CorrelationVisualizer()
    self.divergence_detector = TimeframeDivergenceDetector()
    self.pattern_classifier = PatternClassifier()
    self.alert_system = SmartAlertSystem(cooldown_minutes=5)
    self.regime_analyzer = RegimeAnalyzer()
    self.divergence_history = DivergenceHistory()
    self.correlation_history = {}
""")

print("\n" + "="*70)
