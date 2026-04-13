#!/bin/bash
# Health Monitor - CORR-WATCH

cd "$(dirname "$0")"
LOG_FILE="logs/corr_watch.log"
ALERT_FILE="logs/health_alerts.log"

echo "════════════════════════════════════════════════════════════════"
echo "  HEALTH CHECK - $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════════"

# Helper to get count safely
get_count() {
    grep -c "$1" "$LOG_FILE" 2>/dev/null | awk '{s+=$1} END {print s+0}'
}

# 1. Verificar erros de array
array_errors=$(get_count "array.*has size.*and.*has size")
if [ "$array_errors" -gt 0 ]; then
    echo "🔴 CRÍTICO: $array_errors erros de desalinhamento detectados!"
    echo "$(date) - Array size errors: $array_errors" >> "$ALERT_FILE"
else
    echo "✅ Sem erros de desalinhamento"
fi

# 2. Verificar FutureWarnings
warnings=$(get_count "FutureWarning")
if [ "$warnings" -gt 10 ]; then
    echo "🟡 ATENÇÃO: $warnings FutureWarnings (logs poluídos)"
else
    echo "✅ Warnings sob controle ($warnings)"
fi

# 3. Verificar crashes
crashes=$(get_count "Traceback\|Exception")
if [ "$crashes" -gt 0 ]; then
    echo "🔴 CRÍTICO: $crashes crashes detectados!"
    echo "   Última exception:"
    grep -A 5 "Exception" "$LOG_FILE" | tail -n 6
else
    echo "✅ Sem crashes detectados"
fi

# 4. Taxa de alertas
alerts=$(get_count "Alerta gerado")
echo "📊 Alertas gerados: $alerts"

echo "════════════════════════════════════════════════════════════════"
