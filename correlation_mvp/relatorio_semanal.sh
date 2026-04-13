#!/bin/bash
# Relatório Semanal Automatizado (Rodar toda sexta-feira)

cd "$(dirname "$0")"
LOG_FILE="logs/corr_watch.log"
REPORT_DIR="relatorios"
REPORT_FILE="$REPORT_DIR/report_week_$(date +%Y_W%U).md"

mkdir -p "$REPORT_DIR"

cat > "$REPORT_FILE" << REPORT
# 📊 Relatório Semanal - CORR-WATCH MVP
**Período:** $(date -d '7 days ago' '+%Y-%m-%d') a $(date '+%Y-%m-%d')

---

## 🎯 Métricas Gerais

| Métrica | Valor |
|---------|-------|
| Total de Logs | $(wc -l < $LOG_FILE) |
| Alertas Gerados | $(grep -c "Alerta gerado" $LOG_FILE) |
| Divergências Detectadas | $(grep -c "Divergência" $LOG_FILE) |
| Crashes/Erros | $(grep -c "Exception\|ERROR" $LOG_FILE) |
| Uptime | $(systemctl show corr-watch -p ActiveEnterTimestamp --value) |

---

## 🏆 Top 5 Pares Mais Ativos

\`\`\`
$(grep -o "Analisando [A-Za-z0-9/↔=X]*" $LOG_FILE | \
  awk '{print $2}' | sort | uniq -c | sort -rn | head -5)
\`\`\`

---

## 💾 Performance de Cache

$(
hits=$(grep -c "Cache hit" $LOG_FILE)
misses=$(grep -c "Cache miss" $LOG_FILE)
total=$((hits + misses))
if [ $total -gt 0 ]; then
    hit_rate=$(awk "BEGIN {printf \"%.1f\", ($hits / $total) * 100}")
    echo "- Hit Rate: **$hit_rate%**"
    echo "- Total Requests: $total"
    echo "- Economia de API calls: ~$hits requests"
fi
)

---

## 🔔 Distribuição de Alertas por Prioridade

$(grep "Alerta gerado" $LOG_FILE | grep -o "(.*)" | sort | uniq -c | \
  awk '{print "- " $2 " " $3 ": " $1 " alertas"}')

---

## 📈 Recomendações para Próxima Semana

$(
alert_count=$(grep -c "Alerta gerado" $LOG_FILE)
if [ $alert_count -lt 10 ]; then
    echo "- ⚠️ Poucos alertas gerados - considere **reduzir thresholds**"
elif [ $alert_count -gt 100 ]; then
    echo "- ⚠️ Muitos alertas - considere **aumentar filtros**"
else
    echo "- ✅ Volume de alertas está adequado"
fi

error_count=$(grep -c "Exception\|ERROR" $LOG_FILE)
if [ $error_count -gt 0 ]; then
    echo "- 🔴 Atenção: **$error_count erros** detectados - investigar logs"
fi
)

---

**Gerado automaticamente em:** $(date '+%Y-%m-%d %H:%M:%S')
REPORT

echo "✅ Relatório gerado: $REPORT_FILE"
# cat "$REPORT_FILE"
