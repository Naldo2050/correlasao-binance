#!/bin/bash
# Captura estado atual do sistema para análise

cd "$(dirname "$0")"
LOG_FILE="logs/corr_watch.log"
SNAPSHOT_FILE="snapshot_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "════════════════════════════════════════════════════════════════"
    echo "SNAPSHOT DO SISTEMA - $(date)"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    echo "=== STATUS ==="
    systemctl status corr-watch --no-pager | head -15
    echo ""
    
    echo "=== ESTATÍSTICAS ==="
    echo "Total de logs: $(wc -l < $LOG_FILE)"
    echo "Alertas gerados: $(grep -c 'Alerta gerado' $LOG_FILE)"
    echo "Divergências: $(grep -c 'Divergência' $LOG_FILE)"
    echo "Cache hits: $(grep -c 'Cache hit' $LOG_FILE)"
    echo "Cache misses: $(grep -c 'Cache miss' $LOG_FILE)"
    echo "Erros: $(grep -c 'ERROR\|Exception' $LOG_FILE)"
    echo ""
    
    echo "=== ÚLTIMOS 10 LOGS ==="
    tail -10 $LOG_FILE
    echo ""
    
    echo "=== ÚLTIMOS ALERTAS ==="
    grep "Alerta gerado" $LOG_FILE | tail -5
    echo ""
    
    echo "=== PARES MONITORADOS ==="
    grep -o "Analisando [A-Z0-9/↔=X]*" $LOG_FILE | \
        awk '{print $2}' | sort -u
    
} > "$SNAPSHOT_FILE"

echo "✅ Snapshot salvo em: $SNAPSHOT_FILE"
cat "$SNAPSHOT_FILE"
