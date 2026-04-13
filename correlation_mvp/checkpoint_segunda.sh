#!/bin/bash
# Checkpoint de Segunda-feira - CORR-WATCH

cd "$(dirname "$0")"
echo "═══ CHECKPOINT SEGUNDA-FEIRA ═══"
echo "Iniciando reabertura de mercado..."

# 1. Gerar relatório da semana anterior
./relatorio_semanal.sh

# 2. Verificar se o Forex abriu (deve parar de logar "Mercado Forex fechado")
last_forex_closed=$(grep "Mercado Forex fechado" logs/corr_watch.log | tail -n 1)
echo "Última detecção de mercado fechado: $last_forex_closed"

# 3. Rodar validação completa
./validate_working.sh

echo ""
echo "O sistema deve transicionar suavemente para dados live de Forex agora."
echo "Monitorar dashboard visual para confirmar beta/z-score mudando."
echo "═══ FIM DO CHECKPOINT ═══"
