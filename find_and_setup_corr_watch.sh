#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  LOCALIZADOR E CONFIGURADOR AUTOMÁTICO - CORR-WATCH"
echo "════════════════════════════════════════════════════════════════"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================
# LOCALIZAR PROJETO
# ============================================
echo -e "\n${YELLOW}🔍 Procurando projeto CORR-WATCH...${NC}"

# Possíveis localizações
possible_dirs=(
    "$HOME/corr-watch-mvp"
    "$HOME/correlation_mvp"
    "$HOME/robo_sistema.binace.api/correlation_mvp"
    "$HOME/Documents/Visual Studio/Correlação Binance/correlation_mvp"
)

project_dir=""

# Procurar em locais conhecidos
for dir in "${possible_dirs[@]}"; do
    if [ -d "$dir" ] && [ -f "$dir/main.py" ]; then
        project_dir="$dir"
        echo -e "${GREEN}✅ Projeto encontrado em: $dir${NC}"
        break
    fi
done

# Se não encontrou, procurar globalmente
if [ -z "$project_dir" ]; then
    echo -e "${YELLOW}Procurando em todo o sistema...${NC}"
    
    found=$(find ~ -name "multi_timeframe_engine.py" -type f 2>/dev/null | head -1)
    
    if [ -n "$found" ]; then
        project_dir=$(dirname "$found")
        echo -e "${GREEN}✅ Projeto encontrado em: $project_dir${NC}"
    else
        echo -e "${RED}❌ Projeto não encontrado!${NC}"
        echo ""
        echo "Possíveis causas:"
        echo "  1. Projeto ainda não foi criado"
        echo "  2. Está em um local diferente"
        echo ""
        echo "Criando em: ~/corr-watch-mvp"
        
        mkdir -p ~/corr-watch-mvp
        project_dir="$HOME/corr-watch-mvp"
    fi
fi

# Navegar para o diretório
cd "$project_dir" || exit 1

echo -e "${CYAN}📂 Diretório atual: $(pwd)${NC}"
echo ""

# ============================================
# VERIFICAR ESTRUTURA
# ============================================
echo -e "${YELLOW}📋 Verificando estrutura do projeto...${NC}"

files_to_check=(
    "main.py:PRINCIPAL"
    "config.yaml:CONFIGURAÇÃO"
    "multi_timeframe_engine.py:MTF ENGINE"
    "data_cache.py:CACHE"
    "dashboard_mtf.py:DASHBOARD"
    "divergence_detector.py:DIVERGÊNCIA"
    "pattern_classifier.py:PADRÕES"
    "smart_alerts.py:ALERTAS"
    "regime_analyzer.py:REGIME"
)

missing_critical=0
has_core=true

for item in "${files_to_check[@]}"; do
    file="${item%%:*}"
    label="${item##*:}"
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $label - $file"
    else
        echo -e "${RED}❌${NC} $label - $file (FALTANDO)"
        
        if [[ "$file" == "multi_timeframe_engine.py" ]] || \
           [[ "$file" == "data_cache.py" ]] || \
           [[ "$file" == "divergence_detector.py" ]]; then
            has_core=false
            missing_critical=$((missing_critical + 1))
        fi
    fi
done

echo ""

if [ "$has_core" = false ]; then
    echo -e "${RED}❌ ARQUIVOS CRÍTICOS FALTANDO!${NC}"
    echo ""
    echo "Os arquivos dos PROMPTS 1, 2 e 3 não foram encontrados."
    echo "Você precisa executar os prompts no seu agente de código primeiro."
    echo ""
    echo "Localização do projeto: $project_dir"
    echo ""
    exit 1
fi

# ============================================
# CRIAR AMBIENTE VIRTUAL SE NÃO EXISTIR
# ============================================
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
fi

# Ativar venv
source venv/bin/activate
echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"

# ============================================
# INSTALAR DEPENDÊNCIAS
# ============================================
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📦 Instalando dependências...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
fi

# ============================================
# CRIAR SCRIPTS DE TESTE
# ============================================
echo -e "\n${YELLOW}🧪 Criando scripts de teste...${NC}"

# Script 1: Diagnóstico rápido
cat > test_system_quick.py << 'PYEOF'
"""Teste Rápido do Sistema"""
import sys
from pathlib import Path

print("="*70)
print("TESTE RÁPIDO - CORR-WATCH MVP")
print("="*70)

# Verificar arquivos
print("\n📁 ARQUIVOS:")
files = [
    'multi_timeframe_engine.py',
    'data_cache.py',
    'cache_stats.py',
    'dashboard_mtf.py',
    'correlation_visualizer.py',
    'divergence_detector.py',
    'pattern_classifier.py',
    'smart_alerts.py',
    'regime_analyzer.py'
]

all_exist = True
for f in files:
    exists = Path(f).exists()
    print(f"{'✅' if exists else '❌'} {f}")
    if not exists:
        all_exist = False

# Testar imports
print("\n📦 IMPORTS:")
modules = {
    'multi_timeframe_engine': 'Motor MTF',
    'data_cache': 'Sistema de Cache',
    'dashboard_mtf': 'Dashboard',
    'divergence_detector': 'Detector de Divergência',
    'pattern_classifier': 'Classificador de Padrões',
    'smart_alerts': 'Sistema de Alertas',
    'regime_analyzer': 'Analisador de Regime'
}

all_imported = True
for module, name in modules.items():
    try:
        __import__(module)
        print(f"✅ {name}")
    except Exception as e:
        print(f"❌ {name} - {str(e)[:50]}")
        all_imported = False

# Teste funcional básico
print("\n🧪 TESTE FUNCIONAL:")
try:
    from multi_timeframe_engine import MultiTimeframeEngine
    from data_cache import DataCache
    
    # Criar instâncias
    mtf = MultiTimeframeEngine()
    cache = DataCache(ttl_seconds=60)
    
    print("✅ Motor MTF criado")
    print("✅ Cache criado")
    
    # Testar cache
    import pandas as pd
    df = pd.DataFrame({'close': [100, 101, 102]})
    cache.set('TEST', '1h', df)
    result = cache.get('TEST', '1h')
    
    if result is not None:
        print("✅ Cache funcional")
    else:
        print("❌ Cache não funcionou")
        all_imported = False
    
except Exception as e:
    print(f"❌ Erro no teste funcional: {e}")
    all_imported = False

print("\n" + "="*70)
if all_exist and all_imported:
    print("✅✅✅ SISTEMA COMPLETO E FUNCIONAL ✅✅✅")
    print("="*70)
    sys.exit(0)
else:
    print("❌ SISTEMA INCOMPLETO")
    print("="*70)
    sys.exit(1)
PYEOF

# Script 2: Verificar integração main.py
cat > check_integration.py << 'PYEOF'
"""Verifica integração do main.py"""
from pathlib import Path
import sys

print("="*70)
print("VERIFICAÇÃO DE INTEGRAÇÃO - main.py")
print("="*70)

if not Path('main.py').exists():
    print("❌ main.py não encontrado!")
    sys.exit(1)

content = Path('main.py').read_text()

checks = {
    'Import MTF Engine': 'from multi_timeframe_engine import',
    'Import Cache': 'from data_cache import',
    'Import Dashboard': 'from dashboard_mtf import',
    'Import Divergence': 'from divergence_detector import',
    'Import Alerts': 'from smart_alerts import',
    'self.mtf_engine': 'self.mtf_engine',
    'self.cache': 'self.cache',
    'self.alert_system': 'self.alert_system'
}

print("\n📋 CHECKLIST:")
passed = 0
total = len(checks)

for name, pattern in checks.items():
    found = pattern in content
    print(f"{'✅' if found else '❌'} {name}")
    if found:
        passed += 1

percentage = (passed / total) * 100

print("\n" + "="*70)
print(f"Integração: {passed}/{total} ({percentage:.0f}%)")

if percentage == 100:
    print("✅ main.py TOTALMENTE INTEGRADO")
    sys.exit(0)
elif percentage >= 50:
    print("⚠️  main.py PARCIALMENTE INTEGRADO")
    print("\nExecute: python3 auto_integrate.py")
    sys.exit(1)
else:
    print("❌ main.py NÃO INTEGRADO")
    sys.exit(1)
PYEOF

# Script 3: Auto-integração
cat > auto_integrate.py << 'PYEOF'
"""Auto-integração do main.py"""
from pathlib import Path
from datetime import datetime
import shutil

print("="*70)
print("AUTO-INTEGRAÇÃO - main.py")
print("="*70)

main_file = Path('main.py')

if not main_file.exists():
    print("❌ main.py não encontrado!")
    exit(1)

# Backup
backup = f"main.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy(main_file, backup)
print(f"✅ Backup: {backup}")

content = main_file.read_text()

# Verificar se já integrado
if 'from multi_timeframe_engine import' in content:
    print("✅ Já está integrado!")
    exit(0)

# Adicionar imports (procurar posição após 'import logging')
imports = """
# Componentes Multi-Timeframe
from multi_timeframe_engine import MultiTimeframeEngine, get_mtf_engine
from data_cache import DataCache, get_cache
from cache_stats import CacheMonitor
from dashboard_mtf import MultiTimeframeDashboard, create_simple_mtf_table
from correlation_visualizer import CorrelationVisualizer
from divergence_detector import TimeframeDivergenceDetector, DivergenceHistory
from pattern_classifier import PatternClassifier
from smart_alerts import SmartAlertSystem
from regime_analyzer import RegimeAnalyzer
"""

if 'import logging' in content:
    pos = content.find('import logging')
    end = content.find('\n', pos) + 1
    content = content[:end] + imports + content[end:]
    print("✅ Imports adicionados")

main_file.write_text(content)
print("✅ main.py atualizado")
print("\nVerifique e reinicie: sudo systemctl restart corr-watch")
PYEOF

echo -e "${GREEN}✅ Scripts criados:${NC}"
echo "   • test_system_quick.py"
echo "   • check_integration.py"
echo "   • auto_integrate.py"

# ============================================
# EXECUTAR TESTE
# ============================================
echo -e "\n${YELLOW}🚀 Executando teste do sistema...${NC}\n"

python3 test_system_quick.py
test_result=$?

echo ""

if [ $test_result -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ SISTEMA VERIFICADO COM SUCESSO!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "📂 Localização: $project_dir"
    echo ""
    echo "Próximos passos:"
    echo "  1. Verificar integração: cd $project_dir && python3 check_integration.py"
    echo "  2. Reiniciar serviço: sudo systemctl restart corr-watch"
    echo "  3. Ver logs: tail -f $project_dir/logs/system.log"
    echo ""
    
    # Criar alias útil
    echo "💡 Dica: Adicione ao ~/.bashrc:"
    echo ""
    echo "alias cw='cd $project_dir && source venv/bin/activate'"
    echo ""
else
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ⚠️  SISTEMA INCOMPLETO${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Verifique os erros acima e execute os prompts novamente."
fi

# Criar script de atalho
cat > $project_dir/quick_test.sh << 'TESTEOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 test_system_quick.py
TESTEOF

chmod +x $project_dir/quick_test.sh

echo ""
echo "Atalho criado: $project_dir/quick_test.sh"
echo ""
