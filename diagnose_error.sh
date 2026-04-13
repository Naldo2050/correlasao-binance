#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  DIAGNÓSTICO DE ERRO - CORR-WATCH"
echo "════════════════════════════════════════════════════════════════"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd ~/corr-watch-mvp

# ============================================
# 1. Status do Serviço
# ============================================
echo -e "\n${YELLOW}[1/7] Status do Systemd${NC}"
systemctl status corr-watch --no-pager | head -15

# ============================================
# 2. Logs do Systemd (últimos erros)
# ============================================
echo -e "\n${YELLOW}[2/7] Últimos Erros do Systemd${NC}"
sudo journalctl -u corr-watch -n 30 --no-pager | grep -i "error\|exception\|traceback\|failed" || echo "Nenhum erro encontrado no systemd"

# ============================================
# 3. Arquivo de Log do Sistema
# ============================================
echo -e "\n${YELLOW}[3/7] Arquivo system.log${NC}"
if [ -f "logs/system.log" ]; then
    size=$(stat -c%s logs/system.log)
    lines=$(wc -l < logs/system.log)
    echo "Tamanho: $size bytes"
    echo "Linhas: $lines"
    
    if [ $lines -gt 0 ]; then
        echo -e "\n${GREEN}Últimas 10 linhas:${NC}"
        tail -10 logs/system.log
    else
        echo -e "${RED}❌ Arquivo vazio!${NC}"
    fi
else
    echo -e "${RED}❌ Arquivo logs/system.log não existe!${NC}"
fi

# ============================================
# 4. Arquivo de Erro
# ============================================
echo -e "\n${YELLOW}[4/7] Arquivo error.log${NC}"
if [ -f "logs/error.log" ]; then
    size=$(stat -c%s logs/error.log)
    
    if [ $size -gt 0 ]; then
        echo -e "${RED}⚠️  Erros encontrados:${NC}"
        tail -20 logs/error.log
    else
        echo -e "${GREEN}✅ Nenhum erro registrado${NC}"
    fi
else
    echo "Arquivo não existe (normal se sem erros)"
fi

# ============================================
# 5. Processos Python Rodando
# ============================================
echo -e "\n${YELLOW}[5/7] Processos Python${NC}"
ps aux | grep -i python | grep -v grep | grep -i corr || echo "Nenhum processo corr-watch encontrado"

# ============================================
# 6. Teste de Import
# ============================================
echo -e "\n${YELLOW}[6/7] Teste de Import Manual${NC}"
source venv/bin/activate

python3 << 'PYEOF'
import sys
try:
    from multi_timeframe_engine import MultiTimeframeEngine
    from data_cache import DataCache
    from divergence_detector import TimeframeDivergenceDetector
    print("✅ Todos os imports OK")
except Exception as e:
    print(f"❌ Erro no import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

# ============================================
# 7. Verificar config.yaml
# ============================================
echo -e "\n${YELLOW}[7/7] Validar config.yaml${NC}"
if [ -f "config.yaml" ]; then
    python3 << 'PYEOF'
import yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    pairs = config.get('pairs', [])
    print(f"✅ Config válido - {len(pairs)} pares configurados")
    
    for pair in pairs:
        print(f"   • {pair.get('symbol_a', 'N/A')} ↔ {pair.get('symbol_b', 'N/A')}")
        
except Exception as e:
    print(f"❌ Erro no config.yaml: {e}")
PYEOF
else
    echo -e "${RED}❌ config.yaml não encontrado!${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "DIAGNÓSTICO COMPLETO"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Próximo passo: Rodar manualmente para ver erro real"
echo ""
echo "Execute:"
echo "  sudo systemctl stop corr-watch"
echo "  cd ~/corr-watch-mvp"
echo "  source venv/bin/activate"
echo "  python3 main.py"
echo ""
