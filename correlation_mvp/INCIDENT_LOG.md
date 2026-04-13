# Log de Incidentes - CORR-WATCH MVP

## Incidente #001 - Desalinhamento Temporal Multi-Mercado

**Data:** 2026-04-11  
**Severidade:** 🔴 P0 (Sistema não operacional)  
**Status:** ✅ RESOLVIDO  

### Sintomas
- Serviço em crash loop contínuo
- Erro: `ValueError: array at index 0 has size 127 and the array at index 1 has size 126`
- Localização: `main.py:280` - Função `calculate_spread_zscore()`

### Causa Raiz
Desalinhamento temporal entre:
- **Mercado Crypto (24/7):** Retorna 127 candles de 1h
- **Mercado Forex (horário comercial):** Retorna 126 candles (gaps de fim de semana)

Quando `numpy.cov()` tentava correlacionar arrays de tamanhos diferentes, ocorria crash.

### Solução Implementada

```python
# Intersecção defensiva de índices
common_idx = series_a.index.intersection(series_b.index)
series_a = series_a.loc[common_idx]
series_b = series_b.loc[common_idx]
```

Aplicado em:
- `calculate_spread_zscore()`
- `test_cointegration()`

### Validação
- ✅ Sistema reiniciado sem crashes
- ✅ Primeiro alerta gerado em 16:29:04 (Score 70/100)
- ✅ Testes de regressão criados

### Lições Aprendidas
- Sempre validar tamanho de arrays antes de operações matemáticas
- Dados de diferentes mercados NUNCA são perfeitamente alinhados
- yFinance tem gaps inerentes (fins de semana, feriados)
- Necessário testes com dados de produção reais

### Prevenção Futura
- Script `test_desalinhamento.py` criado
- `health_monitor.sh` adicionado
- Logs de alinhamento em debug mode
