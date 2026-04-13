"""
Dashboard Multi-Timeframe Interativo - CORR-WATCH MVP
Exibição rica de correlações, cache e estatísticas
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich import box
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class MultiTimeframeDashboard:
    """
    Dashboard interativo para visualização multi-timeframe
    
    Layout:
    ┌────────────────────────────────────┐
    │        HEADER (Título + Stats)     │
    ├────────────────────────────────────┤
    │   TABELA DE CORRELAÇÕES MTF        │
    ├────────────────────────────────────┤
    │   CACHE STATS │ ALERTAS RECENTES  │
    └────────────────────────────────────┘
    """
    
    def __init__(self, cache=None, mtf_engine=None):
        """
        Args:
            cache: Instância do DataCache (opcional)
            mtf_engine: Instância do MultiTimeframeEngine (opcional)
        """
        self.console = Console()
        self.cache = cache
        self.mtf_engine = mtf_engine
        self.recent_alerts = []  # Últimos alertas
        
    def create_header(self) -> Panel:
        """Cria header com título e timestamp"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        header_text = Text()
        header_text.append("🔍 CORR-WATCH ", style="bold cyan")
        header_text.append("Multi-Timeframe Dashboard", style="bold white")
        header_text.append(f"\n{now}", style="dim")
        
        return Panel(
            header_text,
            box=box.DOUBLE,
            style="cyan"
        )
    
    def create_mtf_table(self, results: Dict[str, Dict]) -> Table:
        """
        Cria tabela de correlações multi-timeframe
        
        Args:
            results: Dict {pair_name: {
                'correlations': {'5m': 0.85, '15m': 0.87, ...},
                'z_score': 2.3,
                'score': 75,
                'mtf_alignment': 0.8,
                ...
            }}
        
        Returns:
            Table formatada
        """
        table = Table(
            title="📊 Correlações Multi-Timeframe",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        # Colunas
        table.add_column("Par", style="cyan", no_wrap=True, width=14)
        table.add_column("5m", justify="right", width=6)
        table.add_column("15m", justify="right", width=6)
        table.add_column("1h", justify="right", width=6)
        table.add_column("4h", justify="right", width=6)
        table.add_column("1d", justify="right", width=6)
        table.add_column("Z", justify="right", width=7)
        table.add_column("Align", justify="center", width=6)
        table.add_column("Score", justify="right", width=5)
        table.add_column("Status", justify="center", width=12)
        
        # Adicionar linhas
        for pair_name, data in results.items():
            if data is None:
                continue
            
            # Extrair correlações
            corrs = data.get('correlations', {})
            
            # Formatar correlações com cores
            def format_corr(tf_key):
                val = corrs.get(tf_key)
                if val is None or pd.isna(val):
                    return "[dim]N/A[/dim]"
                
                val_str = f"{val:.2f}"
                
                # Colorir baseado na força
                if abs(val) > 0.8:
                    return f"[bold green]{val_str}[/bold green]"
                elif abs(val) > 0.5:
                    return f"[yellow]{val_str}[/yellow]"
                else:
                    return f"[dim]{val_str}[/dim]"
            
            corr_5m = format_corr('5m')
            corr_15m = format_corr('15m')
            corr_1h = format_corr('1h')
            corr_4h = format_corr('4h')
            corr_1d = format_corr('1d')
            
            # Z-Score
            z = data.get('z_score', 0)
            z_str = f"{z:+.2f}"
            if abs(z) > 2.5:
                z_str = f"[bold red]{z_str}[/bold red]"
            elif abs(z) > 2.0:
                z_str = f"[yellow]{z_str}[/yellow]"
            
            # Alinhamento
            align = data.get('mtf_alignment', 0)
            align_str = f"{align*100:.0f}%"
            if align >= 0.8:
                align_str = f"[bold green]{align_str}[/bold green]"
            elif align >= 0.5:
                align_str = f"[yellow]{align_str}[/yellow]"
            else:
                align_str = f"[red]{align_str}[/red]"
            
            # Score e Status
            score = data.get('score', 0)
            score_str = f"{score:.0f}"
            
            signal = data.get('signal', 'NORMAL')
            style = data.get('style', 'white')
            
            # Adicionar linha
            table.add_row(
                pair_name,
                corr_5m,
                corr_15m,
                corr_1h,
                corr_4h,
                corr_1d,
                z_str,
                align_str,
                score_str,
                signal,
                style=style
            )
        
        return table
    
    def create_cache_panel(self) -> Panel:
        """Cria painel de estatísticas de cache"""
        if self.cache is None:
            return Panel(
                "[dim]Cache não disponível[/dim]",
                title="💾 Cache Stats",
                border_style="dim"
            )
        
        stats = self.cache.get_stats()
        
        # Criar conteúdo
        content = Text()
        
        # Hit rate com barra visual
        hit_rate = stats['hit_rate']
        bar_length = 20
        filled = int(bar_length * hit_rate / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        if hit_rate >= 85:
            bar_style = "bold green"
            rating = "🟢 EXCELLENT"
        elif hit_rate >= 70:
            bar_style = "yellow"
            rating = "🟡 GOOD"
        elif hit_rate >= 50:
            bar_style = "orange1"
            rating = "🟠 FAIR"
        else:
            bar_style = "red"
            rating = "🔴 POOR"
        
        content.append(f"Hit Rate: {hit_rate:.1f}%\n", style="bold")
        content.append(f"{bar} {rating}\n\n", style=bar_style)
        
        content.append(f"Requests:   {stats['total_requests']:>6}\n")
        content.append(f"Hits:       {stats['hits']:>6}\n")
        content.append(f"Misses:     {stats['misses']:>6}\n\n")
        
        content.append(f"Items:      {stats['cached_items']:>3}/{stats['max_items']:<3}\n")
        content.append(f"Evictions:  {stats['evictions']:>6}\n")
        content.append(f"Avg Age:    {stats['avg_age_seconds']:>6.1f}s\n")
        content.append(f"TTL:        {stats['ttl_seconds']:>6}s\n")
        
        return Panel(
            content,
            title="💾 Cache Performance",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def create_alerts_panel(self, alerts: List[Dict] = None) -> Panel:
        """
        Cria painel de alertas recentes
        
        Args:
            alerts: Lista de dicts com alertas
        """
        if alerts is None or len(alerts) == 0:
            return Panel(
                "[dim]Nenhum alerta recente[/dim]",
                title="🔔 Alertas Recentes",
                border_style="dim"
            )
        
        content = Text()
        
        # Mostrar últimos 5 alertas
        for alert in alerts[-5:]:
            timestamp = alert.get('timestamp', 'N/A')
            pair = alert.get('pair', 'N/A')
            score = alert.get('score', 0)
            signal = alert.get('signal', 'N/A')
            
            # Estilo baseado no score
            if score >= 80:
                style = "bold red"
                icon = "🔴"
            elif score >= 60:
                style = "yellow"
                icon = "🟡"
            else:
                style = "white"
                icon = "🟢"
            
            content.append(
                f"{icon} {timestamp} | {pair} | {signal} | Score: {score}\n",
                style=style
            )
        
        return Panel(
            content,
            title="🔔 Alertas Recentes",
            border_style="yellow",
            box=box.ROUNDED
        )
    
    def create_full_dashboard(
        self,
        results: Dict[str, Dict],
        alerts: List[Dict] = None
    ) -> Layout:
        """
        Cria dashboard completo
        
        Args:
            results: Resultados de análise multi-timeframe
            alerts: Lista de alertas recentes
        
        Returns:
            Layout completo
        """
        # Criar layout
        layout = Layout()
        
        # Dividir em seções
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=12)
        )
        
        # Footer dividido em 2 colunas
        layout["footer"].split_row(
            Layout(name="cache"),
            Layout(name="alerts")
        )
        
        # Preencher seções
        layout["header"].update(self.create_header())
        layout["main"].update(self.create_mtf_table(results))
        layout["cache"].update(self.create_cache_panel())
        layout["alerts"].update(self.create_alerts_panel(alerts))
        
        return layout
    
    def add_alert(self, pair: str, score: float, signal: str):
        """Adiciona alerta à lista de recentes"""
        alert = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'pair': pair,
            'score': score,
            'signal': signal
        }
        
        self.recent_alerts.append(alert)
        
        # Manter apenas últimos 20
        if len(self.recent_alerts) > 20:
            self.recent_alerts = self.recent_alerts[-20:]
    
    def print_dashboard(self, results: Dict[str, Dict]):
        """
        Imprime dashboard uma vez (não interativo)
        
        Args:
            results: Resultados de análise
        """
        layout = self.create_full_dashboard(results, self.recent_alerts)
        self.console.print(layout)
    
    def run_live_dashboard(
        self,
        update_function,
        update_interval: float = 2.0
    ):
        """
        Roda dashboard em modo live (atualização contínua)
        
        Args:
            update_function: Função que retorna (results, alerts) atualizados
            update_interval: Intervalo de atualização em segundos
        
        Exemplo:
            def get_latest_data():
                results = analyze_all_pairs()
                alerts = get_recent_alerts()
                return results, alerts
            
            dashboard.run_live_dashboard(get_latest_data, update_interval=5)
        """
        import time
        
        try:
            with Live(
                self.create_full_dashboard({}, []),
                refresh_per_second=1,
                screen=True
            ) as live:
                while True:
                    # Obter dados atualizados
                    results, alerts = update_function()
                    
                    # Atualizar recent_alerts se fornecidos
                    if alerts:
                        self.recent_alerts = alerts
                    
                    # Criar novo layout
                    layout = self.create_full_dashboard(results, self.recent_alerts)
                    
                    # Atualizar display
                    live.update(layout)
                    
                    # Aguardar próximo ciclo
                    time.sleep(update_interval)
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard encerrado pelo usuário[/yellow]")


# Utilitários para formatação
import pandas as pd

def format_cache_footer(cache) -> str:
    """
    Formata linha de cache para footer de tabelas
    
    Args:
        cache: Instância do DataCache
    
    Returns:
        String formatada
    """
    if cache is None:
        return "Cache: N/A"
    
    stats = cache.get_stats()
    
    return (
        f"💾 Cache: {stats['hit_rate']:.1f}% hit | "
        f"{stats['cached_items']}/{stats['max_items']} items | "
        f"{stats['avg_age_seconds']:.1f}s avg age"
    )


def create_simple_mtf_table(results: Dict[str, Dict]) -> Table:
    """
    Cria tabela simples de correlações multi-timeframe
    (sem dependência de classe)
    
    Args:
        results: Resultados de análise
    
    Returns:
        Table do rich
    """
    table = Table(
        title="🔍 CORR-WATCH Multi-Timeframe",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    # Colunas principais
    table.add_column("Par", style="cyan", width=14)
    table.add_column("5m", justify="right", width=6)
    table.add_column("15m", justify="right", width=6)
    table.add_column("1h", justify="right", width=6)
    table.add_column("4h", justify="right", width=6)
    table.add_column("1d", justify="right", width=6)
    table.add_column("Z", justify="right", width=7)
    table.add_column("Score", justify="right", width=5)
    table.add_column("Status", justify="center", width=12)
    
    for pair_name, data in results.items():
        if data is None:
            continue
        
        corrs = data.get('correlations', {})
        
        # Formatar correlações
        def fmt(tf):
            v = corrs.get(tf)
            if v is None or pd.isna(v):
                return "N/A"
            return f"{v:.2f}"
        
        table.add_row(
            pair_name,
            fmt('5m'),
            fmt('15m'),
            fmt('1h'),
            fmt('4h'),
            fmt('1d'),
            f"{data.get('z_score', 0):+.2f}",
            f"{data.get('score', 0):.0f}",
            data.get('signal', 'N/A'),
            style=data.get('style', 'white')
        )
    
    return table
