"""
Visualizador de Correlações - CORR-WATCH MVP
Gráficos ASCII e visualizações de correlação ao longo do tempo
Autor: Sistema CORR-WATCH
Versão: 2.1
"""

from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CorrelationVisualizer:
    """Gerador de gráficos ASCII para correlações"""
    
    @staticmethod
    def create_ascii_chart(
        values: List[float],
        labels: List[str] = None,
        width: int = 60,
        height: int = 15,
        title: str = "Correlation Chart"
    ) -> str:
        """
        Cria gráfico ASCII de correlação
        
        Args:
            values: Lista de valores de correlação (-1 a 1)
            labels: Labels para cada valor (opcional)
            width: Largura do gráfico em caracteres
            height: Altura do gráfico em linhas
            title: Título do gráfico
        
        Returns:
            String com gráfico ASCII
        """
        if not values:
            return "No data"
        
        # Normalizar valores para range 0-1
        normalized = [(v + 1) / 2 for v in values]  # -1,1 → 0,1
        
        # Criar canvas
        canvas = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Desenhar eixo Y (correlação)
        for i in range(height):
            canvas[i][0] = '│'
        
        # Desenhar eixo X
        for j in range(width):
            canvas[height - 1][j] = '─'
        canvas[height - 1][0] = '└'
        
        # Desenhar linha zero (correlação = 0)
        zero_line = height // 2
        for j in range(1, width):
            if j % 5 == 0:
                canvas[zero_line][j] = '┼'
            else:
                canvas[zero_line][j] = '─'
        
        # Plotar valores
        points_per_value = (width - 2) // len(values) if len(values) > 0 else 1
        
        for i, val in enumerate(normalized):
            x = 2 + i * points_per_value
            if x >= width:
                break
            
            y = int((1 - val) * (height - 2))
            y = max(0, min(height - 2, y))
            
            canvas[y][x] = '●'
            
            # Desenhar linha vertical até eixo
            for dy in range(y + 1, zero_line):
                if canvas[dy][x] == ' ':
                    canvas[dy][x] = '│'
        
        # Converter canvas para string
        result = [title.center(width)]
        result.append('─' * width)
        
        # Adicionar labels de correlação
        result.append(f"+1.0 │")
        
        for row in canvas:
            result.append(''.join(row))
        
        result.append(f"-1.0 │")
        result.append('─' * width)
        
        # Adicionar labels de timeframes se fornecidos
        if labels:
            label_line = "     "
            for i, label in enumerate(labels):
                x = 2 + i * points_per_value
                if x < width - len(label):
                    label_line += label.ljust(points_per_value)
            result.append(label_line)
        
        return '\n'.join(result)
    
    @staticmethod
    def create_correlation_heatmap(
        correlations: Dict[str, Dict[str, float]],
        timeframes: List[str] = None
    ) -> str:
        """
        Cria heatmap ASCII de correlações multi-timeframe
        
        Args:
            correlations: Dict {pair: {tf: corr_value}}
            timeframes: Lista de timeframes a exibir
        
        Returns:
            String com heatmap ASCII
        
        Exemplo:
            correlations = {
                'BTC↔ETH': {'5m': 0.85, '1h': 0.87, '4h': 0.89},
                'BTC↔SOL': {'5m': 0.65, '1h': 0.70, '4h': 0.72}
            }
        """
        if timeframes is None:
            timeframes = ['5m', '15m', '1h', '4h', '1d']
        
        # Símbolos para representar correlação
        # -1.0 a -0.5: ██ (vermelho escuro)
        # -0.5 a 0.0:  ▓▓ (vermelho claro)
        #  0.0 a 0.5:  ▒▒ (verde claro)
        #  0.5 a 1.0:  ░░ (verde escuro)
        
        def corr_to_symbol(corr):
            if pd.isna(corr):
                return "  "
            elif corr < -0.5:
                return "██"  # Negativo forte
            elif corr < 0.0:
                return "▓▓"  # Negativo fraco
            elif corr < 0.5:
                return "▒▒"  # Positivo fraco
            else:
                return "░░"  # Positivo forte
        
        # Criar header
        header = "Pair".ljust(14) + " │ "
        for tf in timeframes:
            header += tf.center(4) + " "
        
        lines = [
            "╔" + "═" * (len(header) - 2) + "╗",
            "║ " + "Correlation Heatmap".center(len(header) - 4) + " ║",
            "╠" + "═" * (len(header) - 2) + "╣",
            "║ " + header[:-1] + "║",
            "╠" + "═" * (len(header) - 2) + "╣"
        ]
        
        # Adicionar linhas de dados
        for pair, tf_corrs in correlations.items():
            line = f"║ {pair.ljust(14)} │ "
            for tf in timeframes:
                corr = tf_corrs.get(tf, np.nan)
                symbol = corr_to_symbol(corr)
                line += symbol + " "
            line += "║"
            lines.append(line)
        
        lines.append("╚" + "═" * (len(header) - 2) + "╝")
        
        # Legenda
        lines.append("")
        lines.append("Legenda:")
        lines.append("  ██ = Forte negativa (-1.0 a -0.5)")
        lines.append("  ▓▓ = Fraca negativa (-0.5 a 0.0)")
        lines.append("  ▒▒ = Fraca positiva (0.0 a 0.5)")
        lines.append("  ░░ = Forte positiva (0.5 a 1.0)")
        
        return '\n'.join(lines)
    
    @staticmethod
    def create_divergence_indicator(
        correlations: Dict[str, float],
        expected_corr: float = 0.0
    ) -> str:
        """
        Cria indicador visual de divergência entre timeframes
        
        Args:
            correlations: Dict {timeframe: correlation}
            expected_corr: Correlação esperada
        
        Returns:
            String com indicador visual
        """
        timeframes = ['5m', '15m', '1h', '4h', '1d']
        
        lines = ["Divergence Indicator:"]
        lines.append("─" * 50)
        
        for tf in timeframes:
            corr = correlations.get(tf)
            if corr is None or pd.isna(corr):
                lines.append(f"{tf.rjust(5)}: N/A")
                continue
            
            # Calcular desvio
            deviation = corr - expected_corr
            
            # Criar barra visual
            bar_length = 20
            zero_pos = bar_length // 2
            
            if deviation > 0:
                # Desvio positivo
                filled = min(int(abs(deviation) * bar_length / 2), bar_length // 2)
                bar = " " * zero_pos + "│" + "█" * filled + "░" * (bar_length // 2 - filled)
            else:
                # Desvio negativo
                filled = min(int(abs(deviation) * bar_length / 2), bar_length // 2)
                bar = "░" * (bar_length // 2 - filled) + "█" * filled + "│" + " " * zero_pos
            
            # Adicionar cor baseada em magnitude
            if abs(deviation) > 0.3:
                indicator = "🔴"  # Divergência crítica
            elif abs(deviation) > 0.2:
                indicator = "🟡"  # Divergência moderada
            else:
                indicator = "🟢"  # Alinhado
            
            lines.append(f"{tf.rjust(5)}: {bar} {corr:+.2f} {indicator}")
        
        # Adicionar linha de expectativa
        lines.append("─" * 50)
        lines.append(f"Expected: {expected_corr:+.2f}")
        
        return '\n'.join(lines)


import pandas as pd

def print_correlation_summary(
    pair_name: str,
    correlations: Dict[str, float],
    z_score: float,
    score: float,
    mtf_alignment: float
):
    """
    Imprime resumo detalhado de um par
    
    Args:
        pair_name: Nome do par
        correlations: Correlações por timeframe
        z_score: Z-Score do spread
        score: Score final
        mtf_alignment: Taxa de alinhamento MTF
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    # Criar visualizador
    viz = CorrelationVisualizer()
    
    # Criar conteúdo
    content = Text()
    
    # Header
    content.append(f"Par: {pair_name}\n", style="bold cyan")
    content.append("─" * 60 + "\n\n")
    
    # Correlações por timeframe
    content.append("Correlações:\n", style="bold")
    for tf in ['5m', '15m', '1h', '4h', '1d']:
        corr = correlations.get(tf)
        if corr is not None and not pd.isna(corr):
            # Barra visual
            bar_len = int(abs(corr) * 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            
            style = "green" if abs(corr) > 0.7 else "yellow" if abs(corr) > 0.5 else "dim"
            content.append(f"  {tf:>4}: {bar} {corr:+.3f}\n", style=style)
    
    content.append("\n")
    
    # Métricas adicionais
    content.append(f"Z-Score:        {z_score:+.2f}\n")
    content.append(f"Score Final:    {score:.0f}/100\n")
    content.append(f"MTF Alignment:  {mtf_alignment*100:.0f}%\n")
    
    # Status
    if score >= 70:
        status = "🔴 ALERTA CRÍTICO"
        style = "bold red"
    elif score >= 50:
        status = "🟡 ATENÇÃO"
        style = "yellow"
    else:
        status = "🟢 NORMAL"
        style = "green"
    
    content.append(f"\nStatus: {status}", style=style)
    
    # Criar painel
    panel = Panel(
        content,
        title=f"📊 Análise Detalhada",
        border_style="cyan"
    )
    
    console.print(panel)
