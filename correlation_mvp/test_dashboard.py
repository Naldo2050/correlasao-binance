"""
Teste do Dashboard Multi-Timeframe
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from dashboard_mtf import MultiTimeframeDashboard, create_simple_mtf_table
from correlation_visualizer import CorrelationVisualizer, print_correlation_summary
from data_cache import get_cache


def test_dashboard():
    """Testa dashboard com dados simulados"""
    print("\n" + "="*60)
    print("TESTE: Dashboard Multi-Timeframe")
    print("="*60)
    
    # Criar cache simulado
    cache = get_cache(ttl_seconds=300)
    
    # Simular dados
    df = pd.DataFrame({'close': [100]})
    for i in range(10):
        cache.set(f'ASSET{i}', '1h', df)
        cache.get(f'ASSET{i}', '1h')  # Criar alguns hits
    
    # Criar dashboard
    dashboard = MultiTimeframeDashboard(cache=cache)
    
    # Resultados simulados
    results = {
        'BTC↔ETH': {
            'correlations': {
                '5m': 0.85,
                '15m': 0.87,
                '1h': 0.89,
                '4h': 0.91,
                '1d': 0.88
            },
            'z_score': 2.3,
            'score': 75,
            'mtf_alignment': 0.8,
            'signal': '🔴 CONVERGÊNCIA',
            'style': 'bold red'
        },
        'BTC↔SOL': {
            'correlations': {
                '5m': 0.65,
                '15m': 0.70,
                '1h': 0.72,
                '4h': 0.75,
                '1d': 0.68
            },
            'z_score': 0.5,
            'score': 35,
            'mtf_alignment': 0.6,
            'signal': '🟢 NORMAL',
            'style': 'green'
        }
    }
    
    # Adicionar alguns alertas
    dashboard.add_alert('BTC↔ETH', 75, '🔴 CONVERGÊNCIA')
    dashboard.add_alert('EUR↔USD', 82, '🔴 ALERTA')
    
    # Exibir dashboard
    dashboard.print_dashboard(results)
    
    print("\n✅ Dashboard: OK")


def test_visualizer():
    """Testa visualizador"""
    print("\n" + "="*60)
    print("TESTE: Visualizador de Correlação")
    print("="*60)
    
    viz = CorrelationVisualizer()
    
    # Teste 1: Gráfico ASCII
    values = [0.85, 0.87, 0.89, 0.91, 0.88]
    labels = ['5m', '15m', '1h', '4h', '1d']
    
    chart = viz.create_ascii_chart(
        values,
        labels,
        title="BTC↔ETH Correlation"
    )
    
    print("\n📊 Gráfico ASCII:")
    print(chart)
    
    # Teste 2: Heatmap
    correlations = {
        'BTC↔ETH': {'5m': 0.85, '15m': 0.87, '1h': 0.89, '4h': 0.91, '1d': 0.88},
        'BTC↔SOL': {'5m': 0.65, '15m': 0.70, '1h': 0.72, '4h': 0.75, '1d': 0.68},
        'EUR↔USD': {'5m': -0.85, '15m': -0.87, '1h': -0.89, '4h': -0.91, '1d': -0.88}
    }
    
    heatmap = viz.create_correlation_heatmap(correlations)
    
    print("\n🔥 Heatmap:")
    print(heatmap)
    
    # Teste 3: Indicador de divergência
    corrs = {'5m': 0.65, '15m': 0.70, '1h': 0.72, '4h': 0.91, '1d': 0.88}
    
    indicator = viz.create_divergence_indicator(corrs, expected_corr=0.75)
    
    print("\n📍 Indicador de Divergência:")
    print(indicator)
    
    print("\n✅ Visualizador: OK")


def test_summary():
    """Testa print_correlation_summary"""
    print("\n" + "="*60)
    print("TESTE: Resumo Detalhado")
    print("="*60)
    
    print_correlation_summary(
        pair_name="BTC↔ETH",
        correlations={
            '5m': 0.85,
            '15m': 0.87,
            '1h': 0.89,
            '4h': 0.91,
            '1d': 0.88
        },
        z_score=2.3,
        score=75,
        mtf_alignment=0.8
    )
    
    print("\n✅ Resumo: OK")


if __name__ == "__main__":
    try:
        test_dashboard()
        time.sleep(2)
        
        test_visualizer()
        time.sleep(2)
        
        test_summary()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES DO DASHBOARD PASSARAM!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
