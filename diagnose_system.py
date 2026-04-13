"""
Script de Diagnóstico - CORR-WATCH MVP
Verifica quais componentes estão instalados e funcionando
"""

import os
import sys
from pathlib import Path

def check_file(filename):
    """Verifica se arquivo existe"""
    exists = Path(filename).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filename}")
    return exists

def check_import(module_name, display_name=None):
    """Verifica se módulo pode ser importado"""
    if display_name is None:
        display_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {display_name}")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - Erro: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {display_name} - Erro: {e}")
        return False

print("=" * 60)
print("DIAGNÓSTICO DO SISTEMA CORR-WATCH")
print("=" * 60)

print("\n📁 ARQUIVOS PRINCIPAIS:")
files_main = [
    'main.py',
    'config.yaml',
    'requirements.txt'
]

for f in files_main:
    check_file(f)

print("\n📦 COMPONENTES CORE (Prompt 1):")
files_core = [
    'multi_timeframe_engine.py',
    'data_cache.py',
    'cache_stats.py'
]

core_ok = all(check_file(f) for f in files_core)

print("\n📊 COMPONENTES DASHBOARD (Prompt 2):")
files_dashboard = [
    'dashboard_mtf.py',
    'correlation_visualizer.py'
]

dashboard_ok = all(check_file(f) for f in files_dashboard)

print("\n🎯 COMPONENTES DIVERGÊNCIA (Prompt 3):")
files_divergence = [
    'divergence_detector.py',
    'pattern_classifier.py',
    'smart_alerts.py',
    'regime_analyzer.py'
]

divergence_ok = all(check_file(f) for f in files_divergence)

print("\n📚 BIBLIOTECAS PYTHON:")
libs = [
    ('pandas', 'Pandas'),
    ('numpy', 'NumPy'),
    ('ccxt', 'CCXT'),
    ('rich', 'Rich'),
    ('yaml', 'PyYAML'),
    ('scipy', 'SciPy')
]

libs_ok = all(check_import(lib, name) for lib, name in libs)

print("\n🧪 TESTES DOS COMPONENTES:")
if core_ok:
    check_import('multi_timeframe_engine', 'Multi-Timeframe Engine')
    check_import('data_cache', 'Data Cache')
    check_import('cache_stats', 'Cache Stats')

if dashboard_ok:
    check_import('dashboard_mtf', 'Dashboard MTF')
    check_import('correlation_visualizer', 'Correlation Visualizer')

if divergence_ok:
    check_import('divergence_detector', 'Divergence Detector')
    check_import('pattern_classifier', 'Pattern Classifier')
    check_import('smart_alerts', 'Smart Alerts')
    check_import('regime_analyzer', 'Regime Analyzer')

print("\n" + "=" * 60)
print("RESUMO:")
print("=" * 60)

components = {
    'Core (Prompt 1)': core_ok,
    'Dashboard (Prompt 2)': dashboard_ok,
    'Divergência (Prompt 3)': divergence_ok,
    'Bibliotecas': libs_ok
}

all_ok = all(components.values())

for name, status in components.items():
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")

print("=" * 60)

if all_ok:
    print("✅ SISTEMA 100% COMPLETO E FUNCIONAL!")
    sys.exit(0)
else:
    print("⚠️  SISTEMA INCOMPLETO - Veja erros acima")
    sys.exit(1)
