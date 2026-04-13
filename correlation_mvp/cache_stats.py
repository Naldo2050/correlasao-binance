"""
Estatísticas e Monitoramento de Cache - CORR-WATCH MVP
Ferramentas para visualizar performance do cache
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CacheMonitor:
    """Monitor de performance do cache em tempo real"""
    
    def __init__(self, cache):
        """
        Args:
            cache: Instância do DataCache
        """
        self.cache = cache
        self.history: List[Dict] = []
        self.snapshot_interval = 300  # Snapshot a cada 300s (5m)
        self.last_snapshot = 0
    
    def take_snapshot(self):
        """Registra snapshot das estatísticas atuais"""
        import time
        
        now = time.time()
        if now - self.last_snapshot < self.snapshot_interval:
            return
        
        stats = self.cache.get_stats()
        stats['timestamp'] = datetime.now().isoformat()
        
        self.history.append(stats)
        self.last_snapshot = now
        
        # Manter apenas últimas 100 snapshots
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def get_performance_summary(self) -> str:
        """
        Gera resumo de performance do cache
        
        Returns:
            String formatada com estatísticas
        """
        stats = self.cache.get_stats()
        
        summary = f"""
╔══════════════════════════════════════════════════════════╗
║              CACHE PERFORMANCE SUMMARY                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  📊 Requisições                                          ║
║     Total:           {stats['total_requests']:>6}                       ║
║     Hits:            {stats['hits']:>6} ({stats['hit_rate']:>5.1f}%)              ║
║     Misses:          {stats['misses']:>6}                       ║
║                                                          ║
║  💾 Armazenamento                                        ║
║     Itens cached:    {stats['cached_items']:>3}/{stats['max_items']:<3}                     ║
║     Evictions:       {stats['evictions']:>6}                       ║
║     Idade média:     {stats['avg_age_seconds']:>6.1f}s                    ║
║                                                          ║
║  ⚙️  Configuração                                         ║
║     TTL:             {stats['ttl_seconds']:>6}s                      ║
║     Max items:       {stats['max_items']:>6}                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """
        
        return summary.strip()
    
    def get_efficiency_rating(self) -> str:
        """
        Avalia eficiência do cache
        
        Returns:
            Rating: EXCELLENT, GOOD, FAIR, POOR
        """
        stats = self.cache.get_stats()
        hit_rate = stats['hit_rate']
        
        if hit_rate >= 85:
            return "🟢 EXCELLENT"
        elif hit_rate >= 70:
            return "🟡 GOOD"
        elif hit_rate >= 50:
            return "🟠 FAIR"
        else:
            return "🔴 POOR"
    
    def get_recommendations(self) -> List[str]:
        """
        Gera recomendações baseadas nas estatísticas
        
        Returns:
            Lista de recomendações
        """
        stats = self.cache.get_stats()
        recommendations = []
        
        # Hit rate baixo
        if stats['hit_rate'] < 70:
            recommendations.append(
                f"⚠️  Hit rate baixo ({stats['hit_rate']:.1f}%): "
                "Considere aumentar TTL ou reduzir intervalo de atualização"
            )
        
        # Cache muito cheio
        usage = stats['cached_items'] / stats['max_items']
        if usage > 0.9:
            recommendations.append(
                f"⚠️  Cache quase cheio ({usage*100:.0f}%): "
                "Considere aumentar max_items"
            )
        
        # Muitas evictions
        if stats['evictions'] > stats['hits'] * 0.1:
            recommendations.append(
                "⚠️  Muitas evictions: Cache muito pequeno ou TTL muito longo"
            )
        
        # Ótimo!
        if not recommendations and stats['hit_rate'] >= 85:
            recommendations.append(
                f"✅ Cache operando de forma excelente! "
                f"Hit rate: {stats['hit_rate']:.1f}%"
            )
        
        return recommendations


def format_cache_line(cache) -> str:
    """
    Formata linha resumida de cache para footer de tabelas
    
    Args:
        cache: Instância do DataCache
    
    Returns:
        String formatada (ex: "Cache: 87.5% hit | 24 items | 3.2s avg age")
    """
    stats = cache.get_stats()
    
    return (
        f"Cache: {stats['hit_rate']:.1f}% hit | "
        f"{stats['cached_items']} items | "
        f"{stats['avg_age_seconds']:.1f}s avg age"
    )
