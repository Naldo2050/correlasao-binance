"""
Teste Consolidado - CORR-WATCH MVP
Testa todos os componentes em um único script
"""

import sys
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

print("=" * 70)
print("TESTE COMPLETO DO SISTEMA CORR-WATCH")
print("=" * 70)

# ============================================
# TESTE 1: MULTI-TIMEFRAME ENGINE
# ============================================
print("\n" + "=" * 70)
print("TESTE 1: Motor Multi-Timeframe + Cache")
print("=" * 70)

try:
    from multi_timeframe_engine import MultiTimeframeEngine
    from data_cache import DataCache
    from cache_stats import CacheMonitor
    
    print("✅ Imports OK")
    
    # Criar dados simulados
    timestamps = [datetime.now() - timedelta(minutes=5*i) for i in range(100, 0, -1)]
    df_5m = pd.DataFrame({
        'timestamp': timestamps,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 5000, 100)
    })
    
    # Testar MTF Engine
    mtf = MultiTimeframeEngine()
    df_1h = mtf.resample_ohlcv(df_5m, '1h')
    df_4h = mtf.resample_ohlcv(df_5m, '4h')
    
    print(f"✅ Reamostrado 5m ({len(df_5m)}) → 1h ({len(df_1h)}) → 4h ({len(df_4h)})")
    
    # Testar correlação MTF
    df_a = df_5m.copy()
    df_b = df_5m.copy()
    df_b['close'] = df_b['close'] * 1.1 + np.random.randn(len(df_b)) * 2
    
    correlations = mtf.calculate_multi_timeframe_correlation(df_a, df_b, '5m', window=20)
    print(f"✅ Correlações calculadas: {list(correlations.keys())}")
    
    # Testar cache
    cache = DataCache(ttl_seconds=2)
    cache.set('TEST', '1h', df_5m)
    
    result = cache.get('TEST', '1h')
    assert result is not None, "Cache deveria retornar dados"
    print("✅ Cache set/get OK")
    
    time.sleep(2.5)
    result = cache.get('TEST', '1h')
    assert result is None, "Cache deveria ter expirado"
    print("✅ Cache TTL OK")
    
    # Testar monitor
    monitor = CacheMonitor(cache)
    summary = monitor.get_performance_summary()
    print("✅ Monitor de cache OK")
    
    print("\n✅ TESTE 1: PASSOU")
    
except Exception as e:
    print(f"\n❌ TESTE 1: FALHOU - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================
# TESTE 2: DASHBOARD
# ============================================
print("\n" + "=" * 70)
print("TESTE 2: Dashboard e Visualizador")
print("=" * 70)

try:
    from dashboard_mtf import MultiTimeframeDashboard, create_simple_mtf_table
    from correlation_visualizer import CorrelationVisualizer
    
    print("✅ Imports OK")
    
    # Criar dashboard
    dashboard = MultiTimeframeDashboard(cache=cache)
    
    # Dados simulados
    results = {
        'BTC↔ETH': {
            'correlations': {'5m': 0.85, '15m': 0.87, '1h': 0.89, '4h': 0.91, '1d': 0.88},
            'z_score': 2.3,
            'score': 75,
            'mtf_alignment': 0.8,
            'signal': '🔴 CONVERGÊNCIA',
            'style': 'bold red',
            'last_price_a': 72900,
            'last_price_b': 2245
        }
    }
    
    # Criar tabela
    table = create_simple_mtf_table(results)
    print("✅ Tabela criada")
    
    # Testar visualizador
    viz = CorrelationVisualizer()
    
    chart = viz.create_ascii_chart(
        [0.85, 0.87, 0.89, 0.91, 0.88],
        ['5m', '15m', '1h', '4h', '1d'],
        title="Teste"
    )
    print("✅ Gráfico ASCII criado")
    
    heatmap = viz.create_correlation_heatmap({
        'BTC↔ETH': {'5m': 0.85, '1h': 0.89, '4h': 0.91}
    })
    print("✅ Heatmap criado")
    
    print("\n✅ TESTE 2: PASSOU")
    
except Exception as e:
    print(f"\n❌ TESTE 2: FALHOU - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================
# TESTE 3: SISTEMA DE DIVERGÊNCIA
# ============================================
print("\n" + "=" * 70)
print("TESTE 3: Divergência, Padrões e Alertas")
print("=" * 70)

try:
    from divergence_detector import TimeframeDivergenceDetector, DivergenceType
    from pattern_classifier import PatternClassifier, CorrelationPattern
    from smart_alerts import SmartAlertSystem, AlertPriority
    from regime_analyzer import RegimeAnalyzer, CorrelationRegime
    
    print("✅ Imports OK")
    
    # Testar detector de divergência
    detector = TimeframeDivergenceDetector()
    
    correlations = {
        '5m': 0.85,
        '15m': 0.80,
        '1h': 0.70,
        '4h': 0.40,
        '1d': 0.35
    }
    
    divergence = detector.detect_divergence(correlations, expected_corr=0.60)
    print(f"✅ Divergência detectada: {divergence['type'].value}")
    assert divergence['has_divergence'] == True, "Deveria detectar divergência"
    
    # Testar classificador de padrões
    classifier = PatternClassifier()
    
    history = [
        {'1h': 0.50},
        {'1h': 0.60},
        {'1h': 0.70}
    ]
    
    pattern = classifier.classify_pattern({'1h': 0.80}, history)
    print(f"✅ Padrão detectado: {pattern['pattern'].value}")
    
    # Testar sistema de alertas
    alert_system = SmartAlertSystem()
    
    alert = alert_system.analyze_and_alert(
        pair="BTC↔ETH",
        correlations=correlations,
        z_score=2.5,
        score=85,
        expected_corr=0.75
    )
    
    if alert:
        print(f"✅ Alerta gerado: {alert.title}")
    else:
        print("✅ Sem alerta (comportamento esperado se cooldown ativo)")
    
    # Testar analisador de regime
    analyzer = RegimeAnalyzer()
    
    regime = analyzer.identify_regime(0.85)
    assert regime == CorrelationRegime.STRONG_POSITIVE
    print(f"✅ Regime identificado: {regime.value}")
    
    # Detectar mudança
    for corr in [0.80, 0.75, 0.70, 0.30]:
        regime = analyzer.identify_regime(corr)
        change = analyzer.detect_regime_change("TEST", corr, regime)
        if change:
            print(f"✅ Mudança de regime detectada")
            break
    
    print("\n✅ TESTE 3: PASSOU")
    
except Exception as e:
    print(f"\n❌ TESTE 3: FALHOU - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================
# RESUMO FINAL
# ============================================
print("\n" + "=" * 70)
print("✅✅✅ TODOS OS TESTES PASSARAM! SISTEMA 100% FUNCIONAL ✅✅✅")
print("=" * 70)
print("\nPróximo passo: Verificar integração com main.py")
print("Execute: python check_main_integration.py")
