"""
Script de análise para recomendar ajustes de thresholds
Roda após 24-48h de operação
"""

import re
from pathlib import Path

# Ajustado para o nome do arquivo de log real
log_file = Path('logs/corr_watch.log')

if not log_file.exists():
    print(f"❌ Arquivo de log {log_file} não encontrado.")
    exit(1)

log_content = log_file.read_text(errors='replace')

# Extrair todos os scores de alertas
scores = []
for match in re.finditer(r'Score: (\d+)/100', log_content):
    scores.append(int(match.group(1)))

if not scores:
    print("❌ Nenhum alerta gerado ainda. Aguarde mais tempo.")
    exit(0)

print("═" * 70)
print("ANÁLISE DE DISTRIBUIÇÃO DE SCORES")
print("═" * 70)

# Estatísticas
avg = sum(scores) / len(scores)
min_score = min(scores)
max_score = max(scores)

print(f"\nTotal de alertas: {len(scores)}")
print(f"Score médio: {avg:.1f}")
print(f"Score mínimo: {min_score}")
print(f"Score máximo: {max_score}")

# Distribuição
print("\nDistribuição:")
ranges = {
    '0-40': sum(1 for s in scores if 0 <= s < 40),
    '40-60': sum(1 for s in scores if 40 <= s < 60),
    '60-80': sum(1 for s in scores if 60 <= s < 80),
    '80-100': sum(1 for s in scores if 80 <= s <= 100),
}

for range_name, count in ranges.items():
    pct = (count / len(scores)) * 100
    bar = '█' * int(pct / 2)
    print(f"  {range_name}: {bar} {count} ({pct:.1f}%)")

# Recomendações
print("\n" + "═" * 70)
print("RECOMENDAÇÕES:")
print("═" * 70)

if avg < 50:
    print("⚠️  Score médio muito BAIXO")
    print("   Ação: REDUZIR thresholds para gerar mais alertas")
    print("   Exemplo: min_score_for_alert: 40 (estava 60)")
elif avg > 80:
    print("⚠️  Score médio muito ALTO")
    print("   Ação: AUMENTAR thresholds para filtrar ruído")
    print("   Exemplo: min_score_for_alert: 75 (estava 60)")
else:
    print("✅ Score médio está em range ótimo (50-80)")
    print("   Nenhum ajuste necessário.")

# Análise de spam
if len(scores) > 100:
    print("\n⚠️  ALERTA DE SPAM!")
    print(f"   {len(scores)} alertas gerados (muito alto)")
    print("   Ação: Aumentar cooldown_minutes ou score mínimo")
elif len(scores) < 5:
    print("\n⏳ Poucos alertas ainda.")
    print("   Aguarde mais tempo ou reduza thresholds")

print("═" * 70)
