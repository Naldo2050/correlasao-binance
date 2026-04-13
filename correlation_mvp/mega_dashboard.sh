#!/bin/bash

# Dashboard Mega Visual com Gráficos ASCII

cd "$(dirname "$0")"
LOG_FILE="logs/corr_watch.log"

draw_bar() {
    local value=$1
    local max=$2
    local width=50
    
    if [ $max -eq 0 ]; then
        echo ""
        return
    fi
    
    local filled=$(awk "BEGIN {printf \"%.0f\", ($value / $max) * $width}")
    local empty=$((width - filled))
    
    printf "["
    printf "█%.0s" $(seq 1 $filled)
    printf "░%.0s" $(seq 1 $empty)
    printf "] %d/%d\n" $value $max
}

while true; do
    clear
    
    cat << 'BANNER'
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗ ██████╗ ██████╗ ██████╗       ██╗    ██╗ █████╗      ║
║  ██╔════╝██╔═══██╗██╔══██╗██╔══██╗      ██║    ██║██╔══██╗     ║
║  ██║     ██║   ██║██████╔╝██████╔╝█████╗██║ █╗ ██║███████║     ║
║  ██║     ██║   ██║██╔══██╗██╔══██╗╚════╝██║███╗██║██╔══██║     ║
║  ╚██████╗╚██████╔╝██║  ██║██║  ██║      ╚███╔███╔╝██║  ██║     ║
║   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝       ╚══╝╚══╝ ╚═╝  ╚═╝     ║
║                                                                  ║
║              SISTEMA DE MONITORAMENTO EM PRODUÇÃO                ║
╚══════════════════════════════════════════════════════════════════╝
BANNER
    
    echo "        $(date '+%Y-%m-%d %H:%M:%S') | Atualiza a cada 3s"
    echo ""
    
    # Métricas
    total=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    alertas=$(grep -c "Alerta gerado" "$LOG_FILE" 2>/dev/null || echo "0")
    divergencias=$(grep -c "Divergência" "$LOG_FILE" 2>/dev/null || echo "0")
    cache_hits=$(grep -c "Cache hit" "$LOG_FILE" 2>/dev/null || echo "0")
    cache_misses=$(grep -c "Cache miss" "$LOG_FILE" 2>/dev/null || echo "0")
    
    total_cache=$((cache_hits + cache_misses))
    
    echo "┌────────────────────────────────────────────────────────────────┐"
    echo "│ MÉTRICAS PRINCIPAIS                                            │"
    echo "├────────────────────────────────────────────────────────────────┤"
    
    printf "│ Alertas Gerados:     "
    draw_bar $alertas 100
    
    printf "│ Divergências:        "
    draw_bar $divergencias 50
    
    if [ $total_cache -gt 0 ]; then
        printf "│ Cache Hit Rate:      "
        draw_bar $cache_hits $total_cache
    fi
    
    echo "└────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌────────────────────────────────────────────────────────────────┐"
    echo "│ 🔔 ÚLTIMOS ALERTAS                                             │"
    echo "├────────────────────────────────────────────────────────────────┤"
    
    if [ $alertas -gt 0 ]; then
        grep "Alerta gerado" "$LOG_FILE" | tail -3 | while read -r line; do
            echo "│ $(echo "$line" | cut -c1-62) │"
        done
    else
        echo "│ Aguardando primeiro alerta...                                 │"
    fi
    
    echo "└────────────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "┌────────────────────────────────────────────────────────────────┐"
    echo "│ 📊 STREAM DE LOGS                                              │"
    echo "├────────────────────────────────────────────────────────────────┤"
    
    tail -5 "$LOG_FILE" 2>/dev/null | while read -r line; do
        echo "│ $(echo "$line" | cut -c1-62) │"
    done
    
    echo "└────────────────────────────────────────────────────────────────┘"
    
    sleep 3
done
