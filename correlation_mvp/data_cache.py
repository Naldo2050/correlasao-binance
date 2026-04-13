"""
Sistema de Cache Inteligente - CORR-WATCH MVP
Cache com TTL para otimizar requisições de API
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

import time
from typing import Dict, Tuple, Optional, Any
import pandas as pd
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataCache:
    """
    Cache com Time-To-Live (TTL) para dados de mercado
    
    Funcionalidades:
    - Armazena DataFrames com timestamp de criação
    - Expira automaticamente após TTL
    - Estatísticas de hit/miss rate
    - Limpeza automática de itens expirados
    """
    
    def __init__(self, ttl_seconds: int = 300, max_items: int = 100):
        """
        Inicializa sistema de cache
        
        Args:
            ttl_seconds: Tempo de vida do cache em segundos (padrão: 5min)
            max_items: Número máximo de itens no cache
        """
        self.cache: Dict[str, Tuple[pd.DataFrame, float]] = {}
        self.ttl = ttl_seconds
        self.max_items = max_items
        
        # Estatísticas
        self.hits = 0
        self.misses = 0
        self.evictions = 0  # Itens removidos por limite
        
        logger.info(
            f"Cache inicializado: TTL={ttl_seconds}s, "
            f"Max={max_items} itens"
        )
    
    def _make_key(self, symbol: str, timeframe: str) -> str:
        """Cria chave única para cache"""
        return f"{symbol}_{timeframe}"
    
    def get(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Busca dados no cache
        
        Args:
            symbol: Símbolo do ativo (ex: 'BTC/USDT')
            timeframe: Timeframe (ex: '1h')
        
        Returns:
            DataFrame se válido, None se expirado ou não existe
        """
        key = self._make_key(symbol, timeframe)
        
        # Não está no cache
        if key not in self.cache:
            self.misses += 1
            logger.debug(f"Cache miss: {key}")
            return None
        
        data, timestamp = self.cache[key]
        
        # Verificar se expirou
        age = time.time() - timestamp
        if age > self.ttl:
            del self.cache[key]
            self.misses += 1
            logger.debug(f"Cache expirado: {key} (idade: {age:.1f}s)")
            return None
        
        # Cache hit!
        self.hits += 1
        logger.debug(f"Cache hit: {key} (idade: {age:.1f}s)")
        
        # Retornar cópia para evitar modificações
        return data.copy()
    
    def set(self, symbol: str, timeframe: str, data: pd.DataFrame):
        """
        Armazena dados no cache
        
        Args:
            symbol: Símbolo do ativo
            timeframe: Timeframe
            data: DataFrame com OHLCV
        """
        key = self._make_key(symbol, timeframe)
        
        # Verificar limite de itens
        if len(self.cache) >= self.max_items and key not in self.cache:
            self._evict_oldest()
        
        # Armazenar com timestamp atual
        self.cache[key] = (data.copy(), time.time())
        
        logger.debug(
            f"Cache set: {key} "
            f"({len(data)} candles, {len(self.cache)}/{self.max_items} itens)"
        )
    
    def _evict_oldest(self):
        """Remove item mais antigo do cache"""
        if not self.cache:
            return
        
        # Encontrar item mais antigo
        oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
        
        del self.cache[oldest_key]
        self.evictions += 1
        
        logger.debug(f"Cache eviction: {oldest_key}")
    
    def clear(self):
        """Limpa todo o cache"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache limpo: {count} itens removidos")
    
    def clean_expired(self) -> int:
        """
        Remove itens expirados do cache
        
        Returns:
            Número de itens removidos
        """
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp > self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Limpeza: {len(expired_keys)} itens expirados removidos")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dict com métricas de performance
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        # Calcular idade média dos itens
        if self.cache:
            now = time.time()
            ages = [now - timestamp for _, timestamp in self.cache.values()]
            avg_age = sum(ages) / len(ages)
        else:
            avg_age = 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate': round(hit_rate, 2),
            'cached_items': len(self.cache),
            'max_items': self.max_items,
            'ttl_seconds': self.ttl,
            'evictions': self.evictions,
            'avg_age_seconds': round(avg_age, 1)
        }
    
    def reset_stats(self):
        """Reseta estatísticas (mantém cache)"""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        logger.info("Estatísticas do cache resetadas")
    
    def get_item_info(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """
        Retorna informações sobre um item específico
        
        Returns:
            Dict com info do item ou None se não existe
        """
        key = self._make_key(symbol, timeframe)
        
        if key not in self.cache:
            return None
        
        data, timestamp = self.cache[key]
        age = time.time() - timestamp
        expires_in = self.ttl - age
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'candles': len(data),
            'age_seconds': round(age, 1),
            'expires_in_seconds': round(max(0, expires_in), 1),
            'is_valid': age < self.ttl,
            'cached_at': datetime.fromtimestamp(timestamp).isoformat()
        }


# Singleton para uso global
_data_cache = None

def get_cache(ttl_seconds: int = 300, max_items: int = 100) -> DataCache:
    """Factory function para obter instância singleton"""
    global _data_cache
    if _data_cache is None:
        _data_cache = DataCache(ttl_seconds, max_items)
    return _data_cache
