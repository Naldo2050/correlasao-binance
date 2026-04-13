#!/bin/bash
# Dashboard Visual em Tempo Real - CORR-WATCH MVP

cd "$(dirname "$0")"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

LOG_FILE="logs/corr_watch.log"

while true; do
    clear
    
    # Header
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}         🔍 CORR-WATCH LIVE DASHBOARD 🔍${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S')${NC} | Atualiza a cada 3 segundos | Ctrl+C para sair"
    echo ""
    
    # Status do Serviço
    if systemctl is-active --quiet corr-watch; then
        uptime_raw=$(systemctl show corr-watch -p ActiveEnterTimestamp --value)
        echo -e "${GREEN}●${NC} STATUS: ${GREEN}ONLINE${NC} | Iniciado: $uptime_raw"
    else
        echo -e "${RED}●${NC} STATUS: ${RED}OFFLINE${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    echo -e "${WHITE}📊 ESTATÍSTICAS GERAIS${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    
    # Estatísticas
    total_lines=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    alertas=$(grep -c "Alerta gerado" "$LOG_FILE" 2>/dev/null || echo "0")
    divergencias=$(grep -c "Divergência detectada" "$LOG_FILE" 2>/dev/null || echo "0")
    cache_hits=$(grep -c "Cache hit" "$LOG_FILE" 2>/dev/null || echo "0")
    cache_misses=$(grep -c "Cache miss" "$LOG_FILE" 2>/dev/null || echo "0")
    erros=$(grep -c "ERROR\|Exception" "$LOG_FILE" 2>/dev/null || echo "0")
    
    # Calcular hit rate
    total_cache=$((cache_hits + cache_misses))
    if [ $total_cache -gt 0 ]; then
        hit_rate=$(awk "BEGIN {printf \"%.1f\", ($cache_hits / $total_cache) * 100}")
    else
        hit_rate="0.0"
    fi
    
    echo -e "${WHITE}Total de Logs:${NC}      $total_lines linhas"
    echo -e "${GREEN}Alertas Gerados:${NC}    $alertas"
    echo -e "${YELLOW}Divergências:${NC}       $divergencias"
    echo -e "${BLUE}Cache Hit Rate:${NC}     $hit_rate% ($cache_hits hits / $cache_misses misses)"
    
    if [ $erros -gt 0 ]; then
        echo -e "${RED}⚠️  Erros/Exceções:${NC}   $erros"
    else
        echo -e "${GREEN}✅ Erros/Exceções:${NC}   0"
    fi
    
    echo ""
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    echo -e "${WHITE}🔔 ÚLTIMOS 3 ALERTAS${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    
    if [ $alertas -gt 0 ]; then
        grep "Alerta gerado" "$LOG_FILE" | tail -3 | while IFS= read -r line; do
            timestamp=$(echo "$line" | cut -d' ' -f1-2)
            alert_text=$(echo "$line" | cut -d'-' -f4-)
            echo -e "${YELLOW}$timestamp${NC} →$alert_text"
        done
    else
        echo -e "${BLUE}Aguardando primeiro alerta...${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    echo -e "${WHITE}📈 ÚLTIMAS 5 ATIVIDADES${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    
    tail -5 "$LOG_FILE" 2>/dev/null | while IFS= read -r line; do
        # Colorir por nível
        if [[ $line == *"ERROR"* ]] || [[ $line == *"Exception"* ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ $line == *"WARNING"* ]] || [[ $line == *"Divergência"* ]]; then
            echo -e "${YELLOW}$line${NC}"
        elif [[ $line == *"Alerta gerado"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"Cache hit"* ]]; then
            echo -e "${BLUE}$line${NC}"
        else
            echo "$line"
        fi
    done | cut -c1-120
    
    echo ""
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    echo -e "${WHITE}🎯 PARES SENDO MONITORADOS${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────${NC}"
    
    # Extrair pares únicos dos últimos 50 logs
    tail -50 "$LOG_FILE" 2>/dev/null | grep -o "Analisando [A-Z0-9/↔=X]*" | \
        awk '{print $2}' | sort -u | head -10 | while read -r pair; do
        echo -e "${PURPLE}  •${NC} $pair"
    done
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    
    sleep 3
done
