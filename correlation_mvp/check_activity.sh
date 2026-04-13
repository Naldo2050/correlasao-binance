#!/bin/bash
# Verifica se o sistema está REALMENTE funcionando

cd "$(dirname "$0")"

echo "════════════════════════════════════════════════════════════════"
echo "  VERIFICAÇÃO DE ATIVIDADE - CORR-WATCH"
echo "════════════════════════════════════════════════════════════════"

LOG_FILE="logs/corr_watch.log"

# 1. Sistema rodando?
if systemctl is-active --quiet corr-watch; then
    echo "✅ Serviço: RODANDO"
else
    echo "❌ Serviço: PARADO"
    exit 1
fi

# 2. Logs sendo gerados?
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Arquivo de log não existe!"
    exit 1
fi

log_size=$(stat -c%s "$LOG_FILE")
echo "✅ Log existe: $(numfmt --to=iec $log_size)"

# 3. Logs RECENTES (últimos 60 segundos)
echo ""
echo "Atividade nos últimos 60 segundos:"

recent_logs=$(awk -v date="$(date -d '60 seconds ago' '+%Y-%m-%d %H:%M:%S')" \
  '$0 > date' "$LOG_FILE" 2>/dev/null | wc -l)

if [ $recent_logs -gt 0 ]; then
    echo "✅ $recent_logs novas linhas de log (sistema ATIVO)"
else
    echo "⚠️  Nenhum log novo nos últimos 60s (pode estar em cooldown)"
fi

# 4. Tipos de atividade
echo ""
echo "Tipos de atividade detectados:"

activity_types=(
    "Analisando:Análises de pares"
    "Correlação:Cálculos de correlação"
    "Cache hit:Hits de cache"
    "Cache miss:Misses de cache"
    "Alerta gerado:Alertas gerados"
    "Divergência:Divergências detectadas"
)

for activity in "${activity_types[@]}"; do
    pattern="${activity%%:*}"
    label="${activity##*:}"
    count=$(grep -c "$pattern" "$LOG_FILE" 2>/dev/null || echo "0")
    
    if [ $count -gt 0 ]; then
        echo "  ✅ $label: $count"
    else
        echo "  ⚪ $label: 0"
    fi
done

# 5. Última atividade
echo ""
echo "Última linha de log:"
tail -1 "$LOG_FILE" | cut -c1-100

# 6. Tempo desde última atividade
last_timestamp=$(tail -1 "$LOG_FILE" | cut -d' ' -f1-2)
echo ""
echo "Timestamp da última entrada: $last_timestamp"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "CONCLUSÃO: Sistema está $([ $recent_logs -gt 0 ] && echo 'ATIVO ✅' || echo 'EM STANDBY ⏸️')"
echo "════════════════════════════════════════════════════════════════"
