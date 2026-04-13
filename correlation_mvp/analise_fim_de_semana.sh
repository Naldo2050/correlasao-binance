#!/bin/bash
# Análise de Fim de Semana - CORR-WATCH

cd "$(dirname "$0")"
LOG_FILE="logs/corr_watch.log"

echo "═══ ANÁLISE DE FIM DE SEMANA ═══"
echo "Data: $(date)"
echo ""

# 1. Atividade Crypto vs Forex
echo "Atividade por par (últimas 2 horas):"
tail -n 500 "$LOG_FILE" | grep "Analisando" | awk '{print $NF}' | sort | uniq -c | sort -rn
echo ""

# 2. Status dos Thresholds
python3 ajuste_thresholds.py

# 3. Verificar se há logs de "Mercado Forex fechado"
forex_closed_hits=$(grep -c "Mercado Forex fechado" "$LOG_FILE" 2>/dev/null | awk '{s+=$1} END {print s+0}')
echo "Gatilhos de mercado fechado: $forex_closed_hits"

echo ""
echo "═══ FIM DA ANÁLISE ═══"
