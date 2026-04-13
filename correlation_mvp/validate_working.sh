#!/bin/bash
# VALIDAÇÃO RÁPIDA - CORR-WATCH

cd "$(dirname "$0")"
LOG_FILE="logs/corr_watch.log"

echo "🔍 VALIDAÇÃO RÁPIDA - 5 PONTOS"
echo "--------------------------------------------------"

# 1. Serviço ativo?
echo -n "1. Serviço rodando? "
if systemctl is-active --quiet corr-watch; then
    echo "✅ SIM"
else
    echo "❌ NÃO"
fi

# 2. Log crescendo?
if [ -f "$LOG_FILE" ]; then
    size_before=$(stat -c%s "$LOG_FILE")
    echo -n "2. Verificando crescimento do log (10s)... "
    sleep 10
    size_after=$(stat -c%s "$LOG_FILE")
    if [ "$size_after" -gt "$size_before" ]; then
        echo "✅ SIM (+$((size_after - size_before)) bytes)"
    else
        echo "⏳ ESTÁTICO (aguardando novo ciclo)"
    fi
else
    echo "2. Log crescendo? ❌ Arquivo não encontrado"
fi

# 3. Alertas gerados?
echo -n "3. Alertas gerados? "
alerts=$(grep -c "Alerta gerado" "$LOG_FILE" 2>/dev/null | awk '{s+=$1} END {print s+0}')
if [ "$alerts" -gt 0 ]; then
    echo "✅ SIM ($alerts total)"
else
    echo "⏳ AGUARDANDO"
fi

# 4. Cache funcionando?
echo -n "4. Cache funcionando? "
hits=$(grep -c "Cache hit" "$LOG_FILE" 2>/dev/null | awk '{s+=$1} END {print s+0}')
if [ "$hits" -gt 0 ]; then
    echo "✅ SIM ($hits hits)"
else
    echo "⏳ AQUECENDO"
fi

# 5. Sem crashes?
echo -n "5. Sem crashes recentes? "
errors=$(tail -n 100 "$LOG_FILE" 2>/dev/null | grep -E -c "Traceback|ValueError|Exception" | awk '{s+=$1} END {print s+0}')
if [ "$errors" -eq 0 ]; then
    echo "✅ SIM (estável)"
else
    echo "⚠️  ATENÇÃO ($errors detectados nas últimas 100 linhas)"
fi

echo "--------------------------------------------------"
