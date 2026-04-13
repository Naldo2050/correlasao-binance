"""
Testes do Sistema Multi-Timeframe + Cache
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from multi_timeframe_engine import MultiTimeframeEngine
from data_cache import DataCache
from cache_stats import CacheMonitor


def test_mtf_engine():
    """Testa motor multi-timeframe"""
    print("\n" + "="*60)
    print("TESTE 1: Motor Multi-Timeframe")
    print("="*60)
    
    # Criar dados simulados de 5min
    timestamps = [
        datetime.now() - timedelta(minutes=5*i)
        for i in range(100, 0, -1)
    ]
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 5000, 100)
    })
    
    print(f"✅ Dados 5min criados: {len(df)} candles")
    
    # Inicializar motor
    mtf = MultiTimeframeEngine()
    
    # Reamostrar para 1h
    df_1h = mtf.resample_ohlcv(df, '1h')
    print(f"✅ Reamostrado para 1h: {len(df_1h)} candles")
    
    # Reamostrar para 4h
    df_4h = mtf.resample_ohlcv(df, '4h')
    print(f"✅ Reamostrado para 4h: {len(df_4h)} candles")
    
    print("\n✅ Motor MTF: OK")


def test_cache():
    """Testa sistema de cache"""
    print("\n" + "="*60)
    print("TESTE 2: Sistema de Cache")
    print("="*60)
    
    # Criar cache com TTL curto para teste
    cache = DataCache(ttl_seconds=2, max_items=10)
    
    # Criar dados de teste
    df = pd.DataFrame({
        'timestamp': [datetime.now()],
        'close': [100]
    })
    
    # Test 1: Set e Get
    cache.set('BTC/USDT', '1h', df)
    result = cache.get('BTC/USDT', '1h')
    assert result is not None, "Erro: cache.get retornou None"
    print("✅ Set/Get: OK")
    
    # Test 2: Cache miss
    result = cache.get('ETH/USDT', '1h')
    assert result is None, "Erro: deveria ser cache miss"
    print("✅ Cache miss: OK")
    
    # Test 3: Expiração
    print("⏳ Aguardando expiração (2s)...")
    time.sleep(2.5)
    result = cache.get('BTC/USDT', '1h')
    assert result is None, "Erro: cache deveria ter expirado"
    print("✅ Expiração: OK")
    
    # Test 4: Estatísticas
    stats = cache.get_stats()
    print(f"\n📊 Estatísticas:")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit rate: {stats['hit_rate']:.1f}%")
    
    print("\n✅ Sistema de Cache: OK")


def test_cache_monitor():
    """Testa monitor de cache"""
    print("\n" + "="*60)
    print("TESTE 3: Monitor de Cache")
    print("="*60)
    
    cache = DataCache(ttl_seconds=300)
    monitor = CacheMonitor(cache)
    
    # Simular atividade
    df = pd.DataFrame({'close': [100]})
    
    for i in range(10):
        cache.set(f'ASSET{i}', '1h', df)
        cache.get(f'ASSET{i}', '1h')
    
    # Gerar relatório
    summary = monitor.get_performance_summary()
    print(summary)
    
    rating = monitor.get_efficiency_rating()
    print(f"\n📈 Rating: {rating}")
    
    recommendations = monitor.get_recommendations()
    print("\n💡 Recomendações:")
    for rec in recommendations:
        print(f"   {rec}")
    
    print("\n✅ Monitor de Cache: OK")


if __name__ == "__main__":
    try:
        test_mtf_engine()
        test_cache()
        test_cache_monitor()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
