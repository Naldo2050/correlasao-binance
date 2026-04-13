#!/bin/bash

# Script de Setup e Teste Automático
# CORR-WATCH MVP

set -e  # Parar se houver erro

echo "════════════════════════════════════════════════════════════════"
echo "  SETUP E TESTE AUTOMÁTICO - CORR-WATCH MVP"
echo "════════════════════════════════════════════════════════════════"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# PASSO 1: Verificar ambiente
# ============================================
echo -e "\n${YELLOW}[1/8] Verificando ambiente...${NC}"

if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar venv
source venv/bin/activate

echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"

# ============================================
# PASSO 2: Instalar dependências
# ============================================
echo -e "\n${YELLOW}[2/8] Verificando dependências...${NC}"

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
else
    echo -e "${RED}❌ requirements.txt não encontrado!${NC}"
fi

# ============================================
# PASSO 3: Verificar arquivos principais
# ============================================
echo -e "\n${YELLOW}[3/8] Verificando arquivos do sistema...${NC}"

files=(
    "main.py"
    "config.yaml"
    "multi_timeframe_engine.py"
    "data_cache.py"
    "cache_stats.py"
    "dashboard_mtf.py"
    "correlation_visualizer.py"
    "divergence_detector.py"
    "pattern_classifier.py"
    "smart_alerts.py"
    "regime_analyzer.py"
)

missing_files=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file - FALTANDO!"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo -e "\n${RED}⚠️  $missing_files arquivo(s) faltando!${NC}"
    echo "Execute os prompts novamente no seu agente de código"
    exit 1
fi

# ============================================
# PASSO 4: Criar scripts de teste
# ============================================
echo -e "\n${YELLOW}[4/8] Criando scripts de teste...${NC}"

# Criar diagnose_system.py se não existir
if [ ! -f "diagnose_system.py" ]; then
    echo "Criando diagnose_system.py..."
    cat > diagnose_system.py << 'PYEOF'
import os
import sys
from pathlib import Path

def check_file(filename):
    exists = Path(filename).exists()
    print(f"{'✅' if exists else '❌'} {filename}")
    return exists

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {e}")
        return False

print("="*60)
print("DIAGNÓSTICO RÁPIDO")
print("="*60)

core = all([
    check_file('multi_timeframe_engine.py'),
    check_file('data_cache.py'),
    check_file('cache_stats.py')
])

dashboard = all([
    check_file('dashboard_mtf.py'),
    check_file('correlation_visualizer.py')
])

divergence = all([
    check_file('divergence_detector.py'),
    check_file('pattern_classifier.py'),
    check_file('smart_alerts.py'),
    check_file('regime_analyzer.py')
])

print("\nIMPORTS:")
imports_ok = all([
    check_import('multi_timeframe_engine'),
    check_import('data_cache'),
    check_import('dashboard_mtf'),
    check_import('divergence_detector')
])

all_ok = core and dashboard and divergence and imports_ok

print("="*60)
if all_ok:
    print("✅ SISTEMA COMPLETO")
    sys.exit(0)
else:
    print("❌ SISTEMA INCOMPLETO")
    sys.exit(1)
PYEOF
fi

# Criar test_complete_system.py simplificado
if [ ! -f "test_quick.py" ]; then
    cat > test_quick.py << 'PYEOF'
import sys
print("="*60)
print("TESTE RÁPIDO DE IMPORTS")
print("="*60)

modules = [
    'multi_timeframe_engine',
    'data_cache',
    'cache_stats',
    'dashboard_mtf',
    'correlation_visualizer',
    'divergence_detector',
    'pattern_classifier',
    'smart_alerts',
    'regime_analyzer'
]

failed = []
for mod in modules:
    try:
        __import__(mod)
        print(f"✅ {mod}")
    except Exception as e:
        print(f"❌ {mod} - {e}")
        failed.append(mod)

print("="*60)
if not failed:
    print("✅ TODOS OS MÓDULOS OK")
    sys.exit(0)
else:
    print(f"❌ {len(failed)} módulos falharam")
    sys.exit(1)
PYEOF
fi

echo -e "${GREEN}✅ Scripts de teste criados${NC}"

# ============================================
# PASSO 5: Executar diagnóstico
# ============================================
echo -e "\n${YELLOW}[5/8] Executando diagnóstico...${NC}"

python3 diagnose_system.py
diag_status=$?

if [ $diag_status -ne 0 ]; then
    echo -e "${RED}❌ Diagnóstico falhou!${NC}"
    exit 1
fi

# ============================================
# PASSO 6: Teste rápido de imports
# ============================================
echo -e "\n${YELLOW}[6/8] Testando imports...${NC}"

python3 test_quick.py
test_status=$?

if [ $test_status -ne 0 ]; then
    echo -e "${RED}❌ Teste de imports falhou!${NC}"
    exit 1
fi

# ============================================
# PASSO 7: Verificar main.py
# ============================================
echo -e "\n${YELLOW}[7/8] Verificando main.py...${NC}"

if [ -f "main.py" ]; then
    # Verificar se tem os imports necessários
    if grep -q "from multi_timeframe_engine import" main.py; then
        echo -e "${GREEN}✅ main.py integrado${NC}"
    else
        echo -e "${YELLOW}⚠️  main.py não está integrado${NC}"
        echo "Execute: python3 auto_integrate_main.py"
    fi
    
    # Verificar sintaxe
    python3 -m py_compile main.py 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ main.py sem erros de sintaxe${NC}"
    else
        echo -e "${RED}❌ main.py tem erros de sintaxe${NC}"
    fi
else
    echo -e "${RED}❌ main.py não encontrado!${NC}"
fi

# ============================================
# PASSO 8: Status do serviço
# ============================================
echo -e "\n${YELLOW}[8/8] Verificando serviço...${NC}"

if systemctl is-active --quiet corr-watch; then
    echo -e "${GREEN}✅ Serviço corr-watch está rodando${NC}"
    echo -e "\nÚltimas 5 linhas do log:"
    tail -5 logs/system.log 2>/dev/null || echo "Logs não disponíveis ainda"
else
    echo -e "${YELLOW}⚠️  Serviço corr-watch não está rodando${NC}"
    echo -e "Para iniciar: ${GREEN}sudo systemctl start corr-watch${NC}"
fi

# ============================================
# RESUMO FINAL
# ============================================
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✅ SETUP COMPLETO!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Próximos passos:"
echo "  1. Verificar logs: tail -f logs/system.log"
echo "  2. Reiniciar serviço: sudo systemctl restart corr-watch"
echo "  3. Ver status: sudo systemctl status corr-watch"
echo ""
