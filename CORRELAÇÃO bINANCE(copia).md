## **ESTRUTURA CORRELAÇÃO COMPLETA **

## ** ARQUITETURA MACRO DO SISTEMA**

text

╔════════════════════════════════════════════════════════════════════╗

║                     CORR-WATCH SYSTEM v2.0                        ║

╠════════════════════════════════════════════════════════════════════╣

║                                                                    ║

║  CAMADA 1: INGESTÃO DE DADOS                                      ║

║  ├── APIs Primárias (Binance, CoinGecko)                         ║

║  ├── APIs Secundárias (Yahoo, Alpha Vantage)                     ║

║  ├── Dados Alternativos (Sentimento, On-chain)                   ║

║  └── Sistema de Fallback e Redundância                           ║

║                           ↓                                       ║

║  CAMADA 2: PRÉ-PROCESSAMENTO E QUALIDADE                         ║

║  ├── Detecção e Tratamento de Anomalias                          ║

║  ├── Interpolação de Dados Faltantes                             ║

║  ├── Normalização e Padronização                                 ║

║  └── Validação de Integridade                                    ║

║                           ↓                                       ║

║  CAMADA 3: MOTOR ANALÍTICO MULTI-DIMENSIONAL                     ║

║  ├── Análise de Correlação (Pearson, Spearman, Kendall)         ║

║  ├── Análise Multi-Timeframe                                     ║

║  ├── Detecção de Regime de Mercado                               ║

║  └── Análise de Microestrutura                                   ║

║                           ↓                                       ║

║  CAMADA 4: INTELIGÊNCIA ARTIFICIAL HÍBRIDA                       ║

║  ├── Modelos Supervisionados (LSTM, XGBoost)                     ║

║  ├── Modelos Não-Supervisionados (Clustering)                    ║

║  ├── Reinforcement Learning (Otimização contínua)                ║

║  └── Ensemble com Meta-Learning                                  ║

║                           ↓                                       ║

║  CAMADA 5: SISTEMA DE DECISÃO E RISCO                           ║

║  ├── Score de Confiança Multi-Critério                          ║

║  ├── Análise de Risco/Retorno                                   ║

║  ├── Sistema de Priorização                                     ║

║  └── Validação de Executabilidade                               ║

║                           ↓                                       ║

║  CAMADA 6: EXECUÇÃO E MONITORAMENTO                             ║

║  ├── Sistema de Alertas Inteligentes                            ║

║  ├── Dashboard em Tempo Real                                    ║

║  ├── Paper Trading / Simulação                                  ║

║  └── Logging e Auditoria                                        ║

║                           ↓                                       ║

║  CAMADA 7: FEEDBACK E APRENDIZADO CONTÍNUO                      ║

║  ├── Análise de Performance                                     ║

║  ├── Retreinamento Automático                                   ║

║  ├── A/B Testing de Estratégias                                 ║

║  └── Otimização Bayesiana de Hiperparâmetros                   ║

║                                                                    ║

╚════════════════════════════════════════════════════════════════════╝



### **2. COMPONENTES DETALHADOS - VERSÃO MELHORADA**

#### **2.1 SISTEMA DE QUALIDADE DE DADOS (NOVO)**

text

PIPELINE DE QUALIDADE DE DADOS

│

├── DETECÇÃO DE ANOMALIAS

│   ├── Método 1: Z-Score (valores extremos)

│   ├── Método 2: Isolation Forest (padrões anormais)

│   ├── Método 3: DBSCAN (clusters de outliers)

│   └── Método 4: Validação Cruzada entre Exchanges

│

├── TRATAMENTO DE DADOS FALTANTES

│   ├── Gaps \< 1min: Interpolação linear

│   ├── Gaps 1-5min: Interpolação spline

│   ├── Gaps \> 5min: Forward fill + flag de baixa confiança

│   └── Múltiplas fontes: Preenchimento cross-exchange

│

├── DETECÇÃO DE MANIPULAÇÃO

│   ├── Spoofing: Ordens grandes canceladas rapidamente

│   ├── Wash Trading: Volume anormal sem mudança de preço

│   ├── Pump & Dump: Spike de preço + volume seguido de crash

│   └── Stop Hunting: Movimentos direcionais para níveis-chave

│

└── SISTEMA DE CONFIANÇA DOS DADOS

    ├── Score de qualidade por fonte (0-100)

    ├── Peso dinâmico baseado em confiabilidade histórica

    ├── Fallback automático para fonte secundária

    └── Alerta quando qualidade \< limiar crítico

#### **2.2 ANÁLISE DE LIQUIDEZ E EXECUTABILIDADE (NOVO)**

text

MÓDULO DE ANÁLISE DE LIQUIDEZ

│

├── MÉTRICAS DE LIQUIDEZ POR ATIVO

│   ├── Bid-Ask Spread médio e instantâneo

│   ├── Profundidade do Order Book (2%, 5%, 10% do preço)

│   ├── Volume médio diário (30d, 60d, 90d)

│   ├── Turnover ratio (Volume/Market Cap)

│   └── Slippage estimado para diferentes tamanhos

│

├── ANÁLISE DE IMPACTO DE MERCADO

│   ├── Kyle's Lambda (impacto permanente de preço)

│   ├── Amihud Illiquidity Ratio

│   ├── Roll's Spread Estimator

│   └── VPIN (Volume-Synchronized Probability)

│

├── CUSTO DE EXECUÇÃO ESTIMADO

│   ├── Spread cost: (Ask - Bid) / 2

│   ├── Market impact: f(tamanho\_ordem, liquidez)

│   ├── Taxas de exchange: maker/taker fees

│   └── Custo total: spread + impact + fees

│

└── SCORE DE EXECUTABILIDADE

    ├── Alta (80-100): Execução imediata viável

    ├── Média (50-79): Execução em parcelas recomendada

    ├── Baixa (20-49): Aguardar melhora de liquidez

    └── Crítica (0-19): Não executável no momento

#### **2.3 SISTEMA DE CLASSIFICAÇÃO DE REGIME DE MERCADO (NOVO)**

text

IDENTIFICADOR DE REGIME DE MERCADO

│

├── REGIMES PRINCIPAIS

│   ├── BULL MARKET (Tendência de Alta)

│   │   ├── Correlações tendem a enfraquecer

│   │   ├── Ativos movem-se independentemente

│   │   └── Risk-on behavior dominante

│   │

│   ├── BEAR MARKET (Tendência de Baixa)

│   │   ├── Correlações tendem a aumentar

│   │   ├── "Tudo cai junto" - correlação → 1

│   │   └── Flight to quality ativo

│   │

│   ├── RANGING/SIDEWAYS (Lateralização)

│   │   ├── Correlações oscilam ciclicamente

│   │   ├── Mean reversion dominante

│   │   └── Ideal para pair trading

│   │

│   └── HIGH VOLATILITY REGIME (Crise/Evento)

│       ├── Correlações extremas (→ ±1)

│       ├── Quebra de padrões históricos

│       └── Necessita parâmetros especiais

│

├── INDICADORES DE REGIME

│   ├── Markov Regime-Switching Model

│   ├── Hidden Markov Model (HMM)

│   ├── Volatility regime (GARCH-based)

│   └── Trend strength indicators

│

└── AJUSTE DINÂMICO DE PARÂMETROS

    ├── Bull: Thresholds mais agressivos

    ├── Bear: Thresholds mais conservadores

    ├── Ranging: Foco em mean reversion

    └── Crisis: Modo defensivo ativado

#### **2.4 ANÁLISE DE SAZONALIDADE E CICLOS (NOVO)**

text

DETECTOR DE PADRÕES TEMPORAIS RECORRENTES

│

├── SAZONALIDADE INTRADIÁRIA

│   ├── Abertura Ásia (01:00-09:00 UTC)

│   │   └── Correlação BTC-altcoins mais forte

│   ├── Abertura Europa (07:00-15:00 UTC)

│   │   └── Aumento de volume e volatilidade

│   ├── Abertura Americas (13:00-21:00 UTC)

│   │   └── Maior liquidez, correlações mais claras

│   └── Overnight/Weekend

│       └── Baixa liquidez, correlações instáveis

│

├── SAZONALIDADE SEMANAL

│   ├── Segunda: Continuação ou reversão de sexta

│   ├── Quarta: Dados macro, volatilidade alta

│   ├── Sexta: Fechamento de posições, realização

│   └── Fim de semana: Movimentos de baixo volume

│

├── SAZONALIDADE MENSAL

│   ├── Início do mês: Rebalanceamento institucional

│   ├── Meio do mês: Vencimento de opções

│   ├── Final do mês: Window dressing

│   └── Virada do mês: "Turn of Month Effect"

│

├── CICLOS DE MERCADO

│   ├── Ciclo de 4 anos (Bitcoin halving)

│   ├── Ciclo econômico (expansão/contração)

│   ├── Ciclo de dominância (BTC → ETH → Alts)

│   └── Ciclo de sentimento (medo/ganância)

│

└── AJUSTE DE EXPECTATIVAS POR PERÍODO

    ├── Peso maior para padrões sazonais confirmados

    ├── Alertas especiais em períodos atípicos

    └── Calibração de modelos por período

#### **2.5 SISTEMA DE SENTIMENTO E DADOS ALTERNATIVOS (NOVO)**

text

ANÁLISE DE SENTIMENTO MULTI-FONTE

│

├── SENTIMENTO SOCIAL

│   ├── Twitter/X

│   │   ├── Volume de menções dos ativos

│   │   ├── Sentimento (bullish/bearish ratio)

│   │   └── Influencer activity tracking

│   ├── Reddit

│   │   ├── Subreddit activity (posts/comments)

│   │   └── Sentiment scoring

│   └── Telegram/Discord

│       └── Grupos principais monitorados

│

├── MÉTRICAS ON-CHAIN (Para Cripto)

│   ├── Exchange Flows (inflow/outflow)

│   ├── Active Addresses

│   ├── Network Value to Transactions (NVT)

│   ├── MVRV Ratio

│   └── Long/Short Ratio

│

├── ÍNDICES DE SENTIMENTO

│   ├── Fear & Greed Index

│   ├── Put/Call Ratio

│   ├── VIX (volatilidade implícita)

│   ├── Dollar Index (DXY)

│   └── Gold/Bitcoin Ratio

│

└── INTEGRAÇÃO COM CORRELAÇÃO

    ├── Sentimento extremo → correlações aumentam

    ├── Divergência social/preço → sinal de reversão

    └── Consenso alto → possível topo/fundo

#### **2.6 SISTEMA AVANÇADO DE BACKTESTING (NOVO)**

text

FRAMEWORK DE BACKTESTING ROBUSTO

│

├── SIMULAÇÃO HISTÓRICA REALISTA

│   ├── Dados tick-by-tick quando disponível

│   ├── Simulação de slippage e custos

│   ├── Limitações de liquidez incorporadas

│   └── Latência de execução simulada

│

├── VALIDAÇÃO WALK-FORWARD

│   ├── Período de treino: 70% dos dados

│   ├── Período de validação: 15% dos dados

│   ├── Período de teste: 15% dos dados

│   └── Re-otimização periódica

│

├── MÉTRICAS DE PERFORMANCE

│   ├── Accuracy da previsão de correlação

│   ├── Precision/Recall dos alertas

│   ├── Sharpe Ratio (se trading)

│   ├── Maximum Drawdown

│   ├── Win Rate e Profit Factor

│   └── Calmar Ratio

│

├── ANÁLISE DE ROBUSTEZ

│   ├── Monte Carlo simulation

│   ├── Stress testing (cenários extremos)

│   ├── Parameter sensitivity analysis

│   └── Out-of-sample testing

│

└── PREVENÇÃO DE OVERFITTING

    ├── Cross-validation temporal

    ├── Regularização (L1/L2)

    ├── Pruning de features

    └── Ensemble diversificado

#### **2.7 SISTEMA DE GESTÃO DE RISCO (NOVO)**

text

FRAMEWORK DE GESTÃO DE RISCO INTEGRADO

│

├── RISCO DE MODELO

│   ├── Confidence intervals das previsões

│   ├── Uncertainty quantification (Bayesian)

│   ├── Model decay monitoring

│   └── Fallback para regras simples

│

├── RISCO DE EXECUÇÃO

│   ├── Slippage máximo aceitável

│   ├── Tempo máximo de execução

│   ├── Partial fill handling

│   └── Order timeout protocols

│

├── RISCO DE SISTEMA

│   ├── Uptime monitoring (99.9% target)

│   ├── Latência de dados (\<100ms)

│   ├── Backup systems automáticos

│   └── Disaster recovery plan

│

├── LIMITES DE RISCO

│   ├── Máximo de alertas simultâneos: 5

│   ├── Cooldown entre sinais: 5 minutos

│   ├── Confidence mínima para alerta: 70%

│   └── Stop-loss automático de sistema

│

└── RISK DASHBOARD

    ├── VAR (Value at Risk) do sistema

    ├── Stress test results

    ├── Model performance decay curve

    └── System health metrics


### **3. FLUXO DE TRABALHO OTIMIZADO**

#### **3.1 PIPELINE DE PROCESSAMENTO EM TEMPO REAL**

text

FLUXO DE PROCESSAMENTO OTIMIZADO (Latência \< 100ms)

│

├── T+0ms: Dados chegam via WebSocket

│     ↓

├── T+5ms: Validação e limpeza inicial

│     ↓

├── T+10ms: Atualização de buffers de dados

│     ↓

├── T+20ms: Cálculo de correlações incrementais

│     ↓

├── T+30ms: Feature engineering em tempo real

│     ↓

├── T+40ms: Inferência dos modelos de IA

│     ↓

├── T+50ms: Cálculo de scores e rankings

│     ↓

├── T+60ms: Verificação de thresholds

│     ↓

├── T+70ms: Geração de alertas se necessário

│     ↓

├── T+80ms: Update do dashboard

│     ↓

├── T+90ms: Logging e persistência

│     ↓

└── T+100ms: Pronto para próximo ciclo

#### **3.2 HIERARQUIA DE TOMADA DE DECISÃO**

text

ÁRVORE DE DECISÃO PARA ALERTAS

│

├── NÍVEL 1: Filtros Básicos

│   ├── Correlação dentro do range alvo? (-0.90 ± 0.10)

│   ├── Volume suficiente? (\> média 20 períodos)

│   ├── Spread aceitável? (\< 0.5%)

│   └── Dados confiáveis? (quality score \> 80)

│         ↓ (Se todos SIM)

│

├── NÍVEL 2: Confirmação Multi-Timeframe

│   ├── Pelo menos 3 timeframes alinhados?

│   ├── Timeframe principal (5min) confirmado?

│   ├── Não há divergência major? (4h vs 5min)

│   └── Tendência de correlação consistente?

│         ↓ (Se maioria SIM)

│

├── NÍVEL 3: Validação por IA

│   ├── Confidence do modelo \> 70%?

│   ├── Ensemble agreement \> 66%?

│   ├── Sem flags de anomalia?

│   └── Pattern reconhecido no histórico?

│         ↓ (Se todos SIM)

│

├── NÍVEL 4: Análise de Contexto

│   ├── Regime de mercado apropriado?

│   ├── Sem eventos macro próximos (\< 1h)?

│   ├── Liquidez adequada para execução?

│   └── Risk/Reward favorável?

│         ↓ (Se todos SIM)

│

└── NÍVEL 5: Geração de Alerta

    ├── Calcular prioridade (1-10)

    ├── Estimar duração do sinal

    ├── Definir tamanho recomendado

    └── DISPARAR ALERTA


### **4. SISTEMA DE MONITORAMENTO E AUDITORIA**

text

DASHBOARD DE MONITORAMENTO COMPLETO

│

├── PAINEL 1: CORRELAÇÕES EM TEMPO REAL

│   ├── Matriz de correlação atualizada

│   ├── Heatmap por timeframe

│   ├── Gráfico de evolução temporal

│   └── Spread charts normalizados

│

├── PAINEL 2: SAÚDE DO SISTEMA

│   ├── Latência de dados (ms)

│   ├── CPU/Memory usage

│   ├── API calls remaining

│   ├── Error rate (last 1h)

│   └── Uptime percentage

│

├── PAINEL 3: PERFORMANCE DA IA

│   ├── Accuracy em tempo real

│   ├── Confusion matrix atualizada

│   ├── Feature importance dinâmica

│   ├── Drift detection alerts

│   └── Confidence distribution

│

├── PAINEL 4: ALERTAS E HISTÓRICO

│   ├── Alertas ativos

│   ├── Histórico 24h

│   ├── Taxa de acerto

│   ├── Falsos positivos/negativos

│   └── Time to signal distribution

│

└── PAINEL 5: ANÁLISE DE RISCO

    ├── Risk metrics em tempo real

    ├── Exposure por ativo

    ├── Stress test results

    └── System limits usage


### **5. PROTOCOLO DE MANUTENÇÃO E EVOLUÇÃO**

text

CICLO DE MELHORIA CONTÍNUA

│

├── DIÁRIO

│   ├── Verificação de logs de erro

│   ├── Análise de performance de alertas

│   ├── Ajuste fino de thresholds

│   └── Backup de dados e modelos

│

├── SEMANAL

│   ├── Retreinamento de modelos com dados novos

│   ├── Análise de falsos positivos/negativos

│   ├── Otimização de features

│   └── Review de performance vs benchmark

│

├── MENSAL

│   ├── Auditoria completa do sistema

│   ├── Atualização de regime detection

│   ├── Recalibração de risk parameters

│   └── A/B testing de novas estratégias

│

└── TRIMESTRAL

    ├── Overhaul de modelos de IA

    ├── Revisão de arquitetura

    ├── Stress testing completo

    └── Planejamento de melhorias


### **6. CONSIDERAÇÕES FINAIS E DIFERENCIAL COMPETITIVO**

text

VANTAGENS COMPETITIVAS DO SISTEMA

│

├── PRECISÃO SUPERIOR

│   ├── Multi-timeframe validation

│   ├── Ensemble de IA diversificado

│   ├── Dados alternativos integrados

│   └── Feedback loop contínuo

│

├── VELOCIDADE DE RESPOSTA

│   ├── Latência \< 100ms

│   ├── Processamento paralelo

│   ├── Cálculos incrementais

│   └── Edge computing quando possível

│

├── ROBUSTEZ E CONFIABILIDADE

│   ├── Sistema de fallback múltiplo

│   ├── Validação em múltiplas camadas

│   ├── Gestão de risco integrada

│   └── Auditoria completa de decisões

│

└── ADAPTABILIDADE

    ├── Aprendizado contínuo

    ├── Ajuste automático por regime

    ├── Detecção de novos padrões

    └── Evolução orientada por dados


## **RESUMO EXECUTIVO DAS MELHORIAS**

### ✅ **Componentes Adicionados:**

1. **Sistema robusto de qualidade de dados** com detecção de manipulação

2. **Análise profunda de liquidez** para garantir executabilidade

3. **Classificação dinâmica de regime de mercado** para ajuste adaptativo

4. **Análise de sazonalidade** em múltiplas escalas temporais

5. **Integração de sentimento e dados alternativos** para sinais antecipados

6. **Framework completo de backtesting** com prevenção de overfitting

7. **Sistema integrado de gestão de risco** em múltiplas dimensões

8. **Pipeline otimizado** com latência garantida \< 100ms

9. **Hierarquia clara de tomada de decisão** com validação em camadas

10. **Sistema de monitoramento e auditoria** completo com dashboards

### 🎯 **Resultado Final:**

O sistema agora possui todos os componentes necessários para:

- **Detectar** correlações com alta precisão

- **Antecipar** mudanças de regime com dados alternativos

- **Validar** sinais através de múltiplas camadas

- **Executar** com consciência de liquidez e custos

- **Evoluir** continuamente através de aprendizado adaptativo

- **Proteger** contra riscos de modelo, execução e sistema

Esta estrutura completa garante que o sistema não apenas identifica correlações, mas também compreende o **contexto**, valida a **executabilidade**, e mantém **robustez** mesmo em condições adversas de mercado.

  
  
Estrutura do Sistema de Monitoramento de Correlação entre Ativos


## 1. VISÃO GERAL DO SISTEMA


┌─────────────────────────────────────────────────────────────┐

│                    SISTEMA CORR-WATCH                        │

│                                                             │

│  ATIVO A ◄──── Correlação Negativa (~90%) ────► ATIVO B    │

│     │                                                       │

│     └──── Correlação Positiva ────► ATIVO C (Equilíbrio)   │

└─────────────────────────────────────────────────────────────┘


## 2. ESTRUTURA DE CAMADAS DO SISTEMA

### CAMADA 1 — COLETA DE DADOS (Data Layer)

text

FONTES DE DADOS (APIs Gratuitas)

│

├── Binance API (Principal)

│   ├── WebSocket — dados em tempo real (tick a tick)

│   ├── REST API  — dados históricos (OHLCV)

│   └── Endpoints gratuitos disponíveis:

│       ├── /api/v3/klines        → candles históricos

│       ├── /api/v3/ticker/price  → preço atual

│       ├── /api/v3/depth         → livro de ordens

│       └── /stream WebSocket     → fluxo em tempo real

│

├── APIs Complementares Gratuitas

│   ├── CoinGecko API  → dados macro e dominância

│   ├── Yahoo Finance  → ativos tradicionais (índices, forex)

│   ├── Alpha Vantage  → dados históricos alternativos

│   └── FRED API       → dados macroeconômicos (juros, inflação)

│

└── Dados Coletados por Ativo

    ├── Preço (Open, High, Low, Close)

    ├── Volume

    ├── Número de trades

    ├── Liquidações (se cripto)

    ├── Open Interest

    └── Order Book (profundidade)


### CAMADA 2 — TIMEFRAMES MONITORADOS

text

ESTRUTURA MULTI-TIMEFRAME

│

├── Microestrutura (Curto Prazo)

│   ├── 1 minuto  → correlação imediata

│   ├── 3 minutos → confirmação curta

│   └── 5 minutos → gatilho principal curto

│

├── Meso (Médio Prazo)

│   ├── 15 minutos → tendência intermediária

│   ├── 30 minutos → confirmação média

│   └── 1 hora     → estrutura dominante

│

└── Macro (Longo Prazo)

    ├── 4 horas → correlação estrutural

    ├── Diário  → correlação de fundo

    └── Semanal → correlação secular


LÓGICA DE CONFLITO ENTRE TIMEFRAMES

│

├── Exemplo Identificado:

│   ├── 5min  → Correlação POSITIVA  entre A e B

│   └── 4h    → Correlação NEGATIVA entre A e B

│

└── Diagnóstico:

    ├── Movimento de curto prazo CONTRA a tendência principal

    ├── Possível zona de reversão ou armadilha

    └── Sinal de ALERTA para divergência iminente


### CAMADA 3 — MOTOR DE CÁLCULO MATEMÁTICO

#### 3.1 Cálculo de Correlação Base

text

MÉTODO 1 — CORRELAÇÃO DE PEARSON (Padrão)

│

├── Fórmula:

│   r = Σ\[(Xi - X̄)(Yi - Ȳ)\] / √\[Σ(Xi-X̄)² × Σ(Yi-Ȳ)²\]

│

├── Interpretação no Sistema:

│   ├── r = +0.90 a +1.00 → Correlação Positiva Forte

│   ├── r = +0.50 a +0.89 → Correlação Positiva Moderada

│   ├── r = -0.50 a +0.49 → Neutro / Transição

│   ├── r = -0.89 a -0.51 → Correlação Negativa Moderada

│   └── r = -1.00 a -0.90 → Correlação Negativa Forte (ALVO)

│

└── Janelas de Cálculo (Rolling Window):

    ├── Janela curta:  20 períodos

    ├── Janela média:  50 períodos

    └── Janela longa: 100 períodos



MÉTODO 2 — CORRELAÇÃO DE SPEARMAN (Rank)

│

├── Para capturar correlações não-lineares

├── Baseada em ranking dos preços

└── Mais robusta contra outliers e manipulações



MÉTODO 3 — CORRELAÇÃO DINÂMICA (DCC-GARCH)

│

├── Captura mudanças na correlação ao longo do tempo

├── Detecta quando correlação está SE MOVENDO

└── Ideal para identificar INÍCIO de novo regime

#### 3.2 Métricas de Monitoramento Avançado

text

SPREAD ENTRE OS ATIVOS

│

├── Spread Absoluto:    S = Preço\_A - Preço\_B

├── Spread Logarítmico: S = ln(Preço\_A) - ln(Preço\_B)

├── Spread Normalizado: Z-Score do Spread

│   └── Z = (S - média\_S) / desvio\_padrão\_S

│

└── Alertas de Spread:

    ├── Z \> +2.0  → Spread muito alto   → possível reversão

    ├── Z \< -2.0  → Spread muito baixo  → possível reversão

    └── Z → 0     → Convergência ativa



BETA ROLLING (Sensibilidade entre ativos)

│

├── β = Cov(A,B) / Var(B)

├── Monitorar mudança do β ao longo do tempo

└── Quando β muda direção → sinal de mudança de correlação



COINTEGRAÇÃO (Engle-Granger / Johansen)

│

├── Verifica se os ativos compartilham tendência de longo prazo

├── Mesmo que preços se afastem, voltam a convergir

└── Base para estratégias de mean reversion


### CAMADA 4 — IDENTIFICAÇÃO DE GATILHOS

#### 4.1 Gatilhos Macroeconômicos

text

EVENTOS QUE ATIVAM CORRELAÇÃO

│

├── CATEGORIA 1 — Eventos de Risco Global

│   ├── Divulgação de dados de inflação (CPI, PCE)

│   ├── Decisões de taxa de juros (FED, BCE, BACEN)

│   ├── Dados de emprego (Non-Farm Payroll)

│   ├── PIB trimestral

│   └── Crises geopolíticas

│   

│   └── EFEITO: Ativos tendem a se correlacionar

│       fortemente (positiva ou negativamente) nesses momentos

│

├── CATEGORIA 2 — Eventos de Liquidez de Mercado

│   ├── Abertura/Fechamento de mercados (NYSE, CME)

│   ├── Vencimento de opções e futuros

│   ├── Rebalanceamento de portfólios institucionais

│   └── Chamadas de margem em cascata

│

├── CATEGORIA 3 — Eventos de Dominância (Cripto)

│   ├── Dominância do Bitcoin acima de 55%

│   ├── Movimentos bruscos do BTC (\>3% em 1h)

│   ├── Eventos de halving e seus ciclos

│   └── Liquidações em massa (\>100M USD em 1h)

│

└── CATEGORIA 4 — Eventos Técnicos de Mercado

    ├── Rompimento de suporte/resistência chave

    ├── Cruzamento de médias móveis (Golden/Death Cross)

    ├── Volume anormal detectado

    └── Divergência RSI/Preço simultânea nos ativos

#### 4.2 Gatilhos Técnicos (Detectáveis pelo Sistema)

text

SINAIS PRECURSORES DE ATIVAÇÃO DE CORRELAÇÃO

│

├── SINAL 1 — Divergência de Volume

│   ├── Ativo A: Volume crescendo

│   ├── Ativo B: Volume caindo

│   └── Indica: fluxo saindo de B e entrando em A

│

├── SINAL 2 — Compressão de Volatilidade

│   ├── ATR (Average True Range) caindo nos dois ativos

│   ├── Bandas de Bollinger contraindo simultaneamente

│   └── Indica: acúmulo antes de movimento direcional

│

├── SINAL 3 — Quebra de Padrão de Correlação

│   ├── Correlação histórica: -0.90 (negativa forte)

│   ├── Correlação atual: -0.40 (enfraquecendo)

│   └── Tendência: caminhando para 0 ou positivo

│       → ALERTA: regime de correlação mudando

│

├── SINAL 4 — Momentum Divergente

│   ├── RSI do Ativo A: subindo

│   ├── RSI do Ativo B: caindo

│   └── Confirma correlação negativa ativa

│

├── SINAL 5 — Order Flow Imbalance

│   ├── Pressão compradora em A vs vendedora em B

│   ├── Delta Volume (Buy Volume - Sell Volume)

│   └── Indica: início de movimento correlacionado

│

└── SINAL 6 — Convergência/Divergência de Médias

    ├── MACD dos dois ativos em direções opostas

    ├── Média móvel de A cruzando para cima

    ├── Média móvel de B cruzando para baixo

    └── → Confirmação de correlação negativa ativada


### CAMADA 5 — MOTOR DE INTELIGÊNCIA ARTIFICIAL

#### 5.1 Estrutura do Modelo de IA

text

PIPELINE DE MACHINE LEARNING

│

├── FASE 1 — Preparação dos Dados (Feature Engineering)

│   │

│   ├── Features de Preço:

│   │   ├── Retornos logarítmicos (1m, 5m, 15m, 1h, 4h)

│   │   ├── Posição relativa dentro do range diário

│   │   ├── Distância das médias móveis (%, não absoluto)

│   │   └── Posição do preço vs VWAP

│   │

│   ├── Features de Correlação:

│   │   ├── Correlação rolling 20, 50, 100 períodos

│   │   ├── Taxa de mudança da correlação (delta\_corr)

│   │   ├── Z-Score do spread entre os pares

│   │   └── Coeficiente Beta rolling

│   │

│   ├── Features de Volatilidade:

│   │   ├── ATR normalizado por timeframe

│   │   ├── Razão de volatilidade A/B

│   │   ├── Largura das Bandas de Bollinger

│   │   └── VIX ou índice de medo do mercado

│   │

│   ├── Features de Volume:

│   │   ├── Volume relativo (vs média 20 períodos)

│   │   ├── OBV (On Balance Volume) dos três ativos

│   │   ├── Razão de volume A/B

│   │   └── Delta de volume (compra vs venda)

│   │

│   └── Features de Mercado:

│       ├── Dominância BTC (se cripto)

│       ├── Índice DXY (dólar)

│       ├── Hora do dia e dia da semana

│       └── Distância de eventos macroeconômicos

│

│

├── FASE 2 — Definição do Target (O que a IA aprende)

│   │

│   ├── TARGET PRINCIPAL:

│   │   "Nos próximos N períodos, a correlação entre

│   │    A e B vai atingir -0.80 ou mais negativa?"

│   │   └── Saída: Probabilidade (0% a 100%)

│   │

│   ├── TARGET SECUNDÁRIO:

│   │   "Qual será a direção do movimento?"

│   │   ├── A sobe + B cai (correlação negativa ativa)

│   │   └── A cai + B sobe (correlação negativa inversa)

│   │

│   └── TARGET AUXILIAR (Ativo C):

│       "O Ativo C está confirmando equilíbrio?"

│       └── Saída: Score de equilíbrio (0 a 1)

│

│

└── FASE 3 — Modelos a Utilizar

    │

    ├── MODELO 1 — LSTM (Long Short-Term Memory)

    │   ├── Ideal para séries temporais

    │   ├── Captura dependências de longo prazo

    │   └── Aprende padrões sequenciais de correlação

    │

    ├── MODELO 2 — XGBoost / LightGBM

    │   ├── Rápido e interpretável

    │   ├── Ideal para features tabulares

    │   └── Bom para identificar importância das features

    │

    ├── MODELO 3 — Transformer (Atenção Temporal)

    │   ├── Estado da arte em séries temporais

    │   ├── Captura relações complexas entre ativos

    │   └── Detecta "quando" cada feature importa mais

    │

    └── ENSEMBLE FINAL

        ├── Combina os 3 modelos

        ├── Votação ponderada por performance

        └── Reduz falsos positivos


### CAMADA 6 — SISTEMA DE POSICIONAMENTO E CONFLITO DE TIMEFRAMES

text

ANÁLISE DE POSIÇÃO DO PREÇO POR TIMEFRAME

│

├── ESTRUTURA DE LEITURA:

│   ┌──────────────────────────────────────────────────┐

│   │ TIMEFRAME │ CORR A-B │ CORR A-C │ POSIÇÃO PREÇO  │

│   ├──────────────────────────────────────────────────│

│   │   1 min   │  +0.75   │  +0.80   │  A↑ B↑ C↑     │

│   │   5 min   │  +0.60   │  +0.70   │  A↑ B↑ C→     │

│   │  15 min   │  -0.20   │  +0.40   │  TRANSIÇÃO     │

│   │   1 hora  │  -0.75   │  +0.60   │  A↑ B↓ C→     │

│   │   4 horas │  -0.90   │  +0.85   │  A↑ B↓ C↑     │

│   └──────────────────────────────────────────────────┘

│

├── IDENTIFICAÇÃO DE CONFLITO:

│   │

│   ├── CASO 1 — Alinhamento Total

│   │   ├── Todos timeframes: correlação negativa

│   │   └── Sinal: FORTE — tendência estabelecida

│   │

│   ├── CASO 2 — Conflito Curto vs Longo

│   │   ├── 5min: correlação positiva

│   │   ├── 4h:   correlação negativa

│   │   └── Sinal: Correção temporária dentro da tendência maior

│   │

│   └── CASO 3 — Inversão em Andamento

│       ├── Timeframes curtos mudando para negativo

│       ├── Timeframes longos ainda positivos

│       └── Sinal: ALERTA — possível início de nova correlação

│

│

└── MAPA DE POSIÇÃO RELATIVA DOS PREÇOS

    │

    ├── Posição de A em relação à sua média (acima/abaixo)

    ├── Posição de B em relação à sua média (acima/abaixo)

    ├── Posição de C em relação à sua média (acima/abaixo)

    ├── Spread A-B: expandindo ou contraindo?

    └── Ativo C: funcionando como âncora de equilíbrio?


### CAMADA 7 — SISTEMA DE ALERTAS E SCORING

text

SISTEMA DE PONTUAÇÃO DE CORRELAÇÃO (Score 0-100)

│

├── COMPONENTES DO SCORE:

│   │

│   ├── Score de Correlação Atual        → peso 30%

│   │   └── Quão próximo de -0.90 está?

│   │

│   ├── Score de Velocidade de Mudança   → peso 25%

│   │   └── Correlação mudando rápido em direção ao alvo?

│   │

│   ├── Score de Confirmação de Volume   → peso 20%

│   │   └── Volume suporta o movimento?

│   │

│   ├── Score de Alinhamento Timeframes  → peso 15%

│   │   └── Quantos timeframes confirmam?

│   │

│   └── Score do Ativo C (Equilíbrio)    → peso 10%

│       └── C está em posição neutra/equilibrada?

│

│

├── NÍVEIS DE ALERTA:

│   │

│   ├── Score 0-40:   🟢 NEUTRO     → Sem correlação relevante

│   ├── Score 41-60:  🟡 ATENÇÃO    → Padrão se formando

│   ├── Score 61-80:  🟠 ALERTA     → Correlação iniciando

│   └── Score 81-100: 🔴 CRÍTICO    → Correlação ativa e forte

│

│

└── TIPOS DE NOTIFICAÇÃO:

    ├── Alerta em tempo real (WebSocket trigger)

    ├── Relatório por timeframe (a cada X minutos)

    ├── Dashboard visual de correlação

    └── Log histórico de eventos para retreinar a IA


### CAMADA 8 — LOOP DE APRENDIZADO CONTÍNUO

text

CICLO DE RETROALIMENTAÇÃO DA IA

│

├── COLETA → Dados de mercado em tempo real

│     ↓

├── CÁLCULO → Métricas e features atualizadas

│     ↓

├── PREDIÇÃO → Modelo prevê início de correlação

│     ↓

├── ALERTA → Sistema notifica o evento

│     ↓

├── OBSERVAÇÃO → O que realmente aconteceu?

│     ↓

├── AVALIAÇÃO → Predição estava correta?

│     ├── Sim → Reforça esse padrão no modelo

│     └── Não → Ajusta pesos e penaliza o padrão

│     ↓

└── RETREINAMENTO → Modelo melhora continuamente


## 3. ESTRUTURA DE PASTAS DO PROJETO

text

CORR-WATCH/

│

├── data/

│   ├── raw/           → dados brutos da API

│   ├── processed/     → dados tratados e normalizados

│   └── historical/    → base histórica para treino da IA

│

├── engines/

│   ├── collector/     → módulos de coleta de dados

│   ├── calculator/    → motor de cálculo matemático

│   ├── detector/      → identificação de padrões

│   └── alerter/       → sistema de alertas

│

├── ai/

│   ├── features/      → engenharia de features

│   ├── models/        → modelos treinados

│   ├── training/      → scripts de treino

│   └── evaluation/    → métricas de performance

│

├── dashboard/

│   ├── charts/        → visualização de correlações

│   ├── heatmaps/      → mapa de correlação por timeframe

│   └── alerts/        → painel de alertas

│

└── config/

    ├── assets.yaml    → configuração dos ativos (A, B, C)

    ├── thresholds.yaml → limites de alerta

    └── timeframes.yaml → timeframes monitorados


## 4. FLUXO COMPLETO DO SISTEMA

text

┌─────────────┐    ┌─────────────┐    ┌─────────────┐

│  BINANCE    │    │  COINGECKO  │    │  YAHOO FIN  │

│  WebSocket  │    │  REST API   │    │  REST API   │

└──────┬──────┘    └──────┬──────┘    └──────┬──────┘

       │                  │                   │

       └──────────────────┴───────────────────┘

                          │

                  ┌───────▼────────┐

                  │  DATA LAYER    │

                  │  Normalização  │

                  │  Sincronização │

                  └───────┬────────┘

                          │

                  ┌───────▼────────┐

                  │  MATH ENGINE   │

                  │  Pearson       │

                  │  Spearman      │

                  │  Z-Score       │

                  │  Beta Rolling  │

                  │  Cointegração  │

                  └───────┬────────┘

                          │

              ┌───────────┴───────────┐

              │                       │

      ┌───────▼───────┐     ┌────────▼────────┐

      │  MULTI-TIME   │     │   AI ENGINE     │

      │  FRAME LAYER  │     │   LSTM/XGBoost  │

      │  1m→Semanal   │     │   Transformer   │

      └───────┬───────┘     └────────┬────────┘

              │                       │

              └───────────┬───────────┘

                          │

                  ┌───────▼────────┐

                  │ SCORE ENGINE   │

                  │  0 a 100       │

                  │  Por par       │

                  │  Por timeframe │

                  └───────┬────────┘

                          │

                  ┌───────▼────────┐

                  │   ALERTAS      │

                  │ 🟢🟡🟠🔴      │

                  │  Dashboard     │

                  │  Notificações  │

                  └───────┬────────┘

                          │

                  ┌───────▼────────┐

                  │  FEEDBACK LOOP │

                  │  Retreinamento │

                  │  IA melhora    │

                  └────────────────┘


## 5. PRÓXIMOS PASSOS SUGERIDOS

text

FASE 1 — Fundação (Semanas 1-2)

├── Definir os 3 ativos (A, B, C) exatos

├── Configurar conexão com Binance API

├── Implementar coleta básica de dados

└── Calcular correlação simples entre os pares


FASE 2 — Motor Matemático (Semanas 3-4)

├── Implementar todas as métricas da Camada 3

├── Construir análise multi-timeframe

├── Desenvolver sistema de Score

└── Criar primeiros alertas básicos


FASE 3 — Base de Dados Histórica (Semana 5)

├── Coletar 1-2 anos de dados históricos

├── Identificar manualmente os eventos passados

├── Rotular dados para treino da IA

└── Construir pipeline de features


FASE 4 — IA (Semanas 6-8)

├── Treinar modelos com dados históricos

├── Validar performance (backtesting)

├── Implementar ensemble final

└── Conectar IA ao sistema de alertas


FASE 5 — Dashboard e Refinamento (Semana 9+)

├── Interface visual de monitoramento

├── Loop de retreinamento automático

└── Otimização contínua


**Resumo:** O sistema é viável e matematicamente sólido. A combinação de **correlação rolling + Z-Score do spread + análise multi-timeframe + detecção de gatilhos + IA supervisionada** cria uma estrutura robusta para antecipar movimentos de correlação entre os três ativos com alto grau de confiabilidade.






------------------------------------------------------------------------------------------------------------------------

# **🏛️ CORR-WATCH SYSTEM v2.0 — Arquitetura Completa Revisada**

**Sistema de Monitoramento de Correlação para Operação de Convergência/Divergência** Documento Técnico de Arquitetura | Abril 2026


## **📋 Sumário Executivo**

Este documento apresenta a **arquitetura completa e revisada** do sistema CORR-WATCH, projetado para monitorar correlações entre pares de moedas em tempo real, detectar anomalias, desvios de padrão e gerar alertas de oportunidade para operações de correlação/convergência.

\[!IMPORTANT\] **Diferença fundamental desta revisão**: Separamos claramente o que é **viável e funcional hoje** do que é **aspiracional/futuro**. Cada componente tem uma classificação de prioridade e uma indicação clara de reaproveitamento do código existente no projeto robo\_sistema.binace.api.


## **1. DIAGNÓSTICO DO PROJETO EXISTENTE**

### **1.1 Módulos Já Existentes que Serão Reaproveitados**

| Módulo Existente | Localização | Funcionalidade Reaproveitável | Status |
| - | - | - | - |
| cross\_asset\_correlations.py | market\_analysis/ | Pearson rolling, correlação BTC/ETH/DXY/NDX, cache TTL 5min | ✅ Funcional |
| regime\_detector.py | market\_analysis/ | Detecção de regime (RISK\_ON/OFF/TRANSITION), VIX, yields | ✅ Funcional |
| mean\_reversion.py | institutional/ | Z-Score, Bollinger, %B, probabilidade de reversão | ✅ Funcional |
| market\_regime\_hmm.py | institutional/ | HMM 4 estados (bull/bear/lateral/high\_vol), transições | ✅ Funcional |
| garch\_volatility.py | institutional/ | GARCH(1,1), forecast de volatilidade, regime de vol | ✅ Funcional |
| hurst\_exponent.py | institutional/ | Hurst exponent para mean reversion vs trending | ✅ Funcional |
| kalman\_filter.py | institutional/ | Filtro de Kalman para suavização e previsão | ✅ Funcional |
| fourier\_cycles.py | institutional/ | Análise de ciclos via FFT | ✅ Funcional |
| order\_flow\_imbalance.py | institutional/ | Imbalance de order flow, pressão compradora/vendedora | ✅ Funcional |
| context\_collector.py | fetchers/ | Coleta macro (VIX, DXY, SP500, Gold, yields), klines Binance | ✅ Funcional |
| hybrid\_decision.py | ml/ | Fusão ML + LLM, detecção de conflito, frozen model | ✅ Funcional |
| XGBoost pipeline | ml/ | Feature engineering, treino, inferência | ✅ Funcional |
| flow\_analyzer/ | flow\_analyzer/ | CVD, whale flow, delta volume, absorption | ✅ Funcional |
| support\_resistance/ | support\_resistance/ | S/R, pivot points, defense zones | ✅ Funcional |


### **1.2 Gaps Identificados — O Que Precisa Ser Criado**

| Componente Necessário | Prioridade | Complexidade | Existe? |
| - | - | - | - |
| **Motor de Correlação Multi-Par** (N pares em paralelo) | 🔴 CRÍTICA | Média | ❌ Não |
| **Tabela de Monitoramento em Tempo Real** | 🔴 CRÍTICA | Alta | ❌ Não |
| **Correlação de Spearman** | 🟡 ALTA | Baixa | ❌ Não |
| **DCC-GARCH** (correlação dinâmica) | 🟡 ALTA | Alta | ❌ Não |
| **Z-Score do Spread entre pares** | 🔴 CRÍTICA | Baixa | ❌ Não |
| **Cointegração (Engle-Granger)** | 🟡 ALTA | Média | ❌ Não |
| **Dashboard de Correlação (Heatmap + Gráficos)** | 🟡 ALTA | Alta | ❌ Não |
| **Sistema de Alertas de Anomalia de Correlação** | 🔴 CRÍTICA | Média | ❌ Não |
| **Paper Trading / Simulador de Pares** | 🟢 MÉDIA | Alta | ❌ Não |
| **LSTM para previsão de correlação** | 🟢 MÉDIA | Muito Alta | ❌ Não |
| **Backtesting de Estratégia de Pares** | 🟡 ALTA | Alta | ❌ Não |
| **Detector de Manipulação de Correlação** | 🟢 MÉDIA | Alta | ❌ Não |



## **2. ARQUITETURA MACRO REVISADA — VERSÃO REALISTA**

╔══════════════════════════════════════════════════════════════════════════╗  
║                        CORR-WATCH SYSTEM v2.0                          ║  
║              "Do Viável ao Excelente — Fases Incrementais"             ║  
╠══════════════════════════════════════════════════════════════════════════╣  
║                                                                        ║  
║  CAMADA 1: INGESTÃO DE DADOS  \[REAPROVEITÁVEL ~80%\]                   ║  
║  ├── Binance REST + WebSocket (já existe em context\_collector)        ║  
║  ├── yFinance (DXY, SPX, NDX, Gold, VIX) (já existe)                 ║  
║  ├── CoinGecko (dominância BTC/ETH) (já existe via MacroDataProvider)║  
║  ├── FRED API (yields, inflação) (já existe via fred\_fetcher)        ║  
║  └── \[NOVO\] Coleta Multi-Par simultânea N×M pares                    ║  
║                           ↓                                           ║  
║  CAMADA 2: PRÉ-PROCESSAMENTO  \[REAPROVEITÁVEL ~60%\]                  ║  
║  ├── Validação de dados (já existe em data\_validator)                 ║  
║  ├── Detecção de outliers via Z-Score (já existe em mean\_reversion)   ║  
║  ├── \[NOVO\] Sincronização temporal entre pares (alinhamento)         ║  
║  ├── \[NOVO\] Interpolação de gaps cross-exchange                      ║  
║  └── \[NOVO\] Score de qualidade por fonte                             ║  
║                           ↓                                           ║  
║  CAMADA 3: MOTOR ANALÍTICO DE CORRELAÇÃO  \[~90% NOVO\]                ║  
║  ├── \[NOVO\] Pearson Multi-Par Rolling (20, 50, 100 períodos)         ║  
║  ├── \[NOVO\] Spearman Rank Correlation                                ║  
║  ├── \[NOVO\] Z-Score do Spread (normalizado)                          ║  
║  ├── \[NOVO\] Beta Rolling entre pares                                 ║  
║  ├── \[NOVO\] Teste de Cointegração (Engle-Granger / ADF)             ║  
║  ├── \[PARCIAL\] Análise Multi-Timeframe (base existe)                 ║  
║  ├── \[REUSO\] Regime Detection (HMM + GARCH existem)                  ║  
║  └── \[REUSO\] Mean Reversion Score (já existe)                        ║  
║                           ↓                                           ║  
║  CAMADA 4: INTELIGÊNCIA E SCORING  \[REAPROVEITÁVEL ~40%\]             ║  
║  ├── \[REUSO\] XGBoost para classificação (pipeline existe)            ║  
║  ├── \[NOVO\] Features específicas de correlação para ML               ║  
║  ├── \[NOVO\] Score de Confiança Multi-Critério (0-100)                ║  
║  ├── \[NOVO\] Árvore de Decisão de Alertas (5 níveis)                  ║  
║  └── \[FUTURO\] LSTM para previsão de correlação                       ║  
║                           ↓                                           ║  
║  CAMADA 5: MONITORAMENTO E ALERTAS  \[~95% NOVO\]                      ║  
║  ├── \[NOVO\] Tabela de Monitoramento em Tempo Real                    ║  
║  ├── \[NOVO\] Heatmap de Correlação por Timeframe                      ║  
║  ├── \[NOVO\] Sistema de Alertas (🟢🟡🟠🔴)                            ║  
║  ├── \[NOVO\] Detector de Anomalias de Correlação                      ║  
║  └── \[NOVO\] Dashboard Web (Gráficos + Métricas)                     ║  
║                           ↓                                           ║  
║  CAMADA 6: VALIDAÇÃO E FEEDBACK  \[~80% NOVO\]                         ║  
║  ├── \[NOVO\] Backtesting de Estratégias de Pares                      ║  
║  ├── \[NOVO\] Paper Trading Simulado                                   ║  
║  ├── \[REUSO\] Logging e Auditoria (event\_bus, event\_saver)            ║  
║  └── \[NOVO\] Loop de Aprendizado (retreinamento)                      ║  
║                                                                        ║  
╚══════════════════════════════════════════════════════════════════════════╝


## **3. ESTRUTURA DE PASTAS DO PROJETO (REVISADA)**

CORR-WATCH/                          (dentro de robo\_sistema.binace.api/)  
│  
├── correlation/                     ← NOVO PACOTE PRINCIPAL  
│   ├── \_\_init\_\_.py  
│   ├── config.py                    \# Configuração de pares, timeframes, thresholds  
│   │  
│   ├── engine/                      \# Motor de Cálculo de Correlação  
│   │   ├── \_\_init\_\_.py  
│   │   ├── pearson\_engine.py        \# Pearson rolling multi-par  
│   │   ├── spearman\_engine.py       \# Spearman rank correlation  
│   │   ├── spread\_analyzer.py       \# Z-Score do spread, spread log/absoluto  
│   │   ├── beta\_rolling.py          \# Beta rolling entre pares  
│   │   ├── cointegration.py         \# Teste ADF, Engle-Granger, Johansen  
│   │   ├── dcc\_garch.py             \# Correlação Dinâmica Condicional  
│   │   └── correlation\_matrix.py    \# Matriz NxN de correlações  
│   │  
│   ├── collector/                   \# Coleta de Dados Multi-Par  
│   │   ├── \_\_init\_\_.py  
│   │   ├── pair\_data\_collector.py   \# Coleta klines N pares simultâneos  
│   │   ├── sync\_aligner.py          \# Alinhamento temporal entre séries  
│   │   └── data\_quality\_scorer.py   \# Score de qualidade por fonte  
│   │  
│   ├── detector/                    \# Detecção de Padrões e Anomalias  
│   │   ├── \_\_init\_\_.py  
│   │   ├── anomaly\_detector.py      \# Desvios do padrão de correlação  
│   │   ├── regime\_change\_detector.py \# Mudança de regime de correlação  
│   │   ├── divergence\_detector.py   \# Divergência entre preço e correlação  
│   │   ├── manipulation\_detector.py \# Detecção de manipulação (spoofing, wash)  
│   │   └── seasonality\_analyzer.py  \# Sazonalidade intradiária/semanal/mensal  
│   │  
│   ├── scoring/                     \# Sistema de Scoring e Decisão  
│   │   ├── \_\_init\_\_.py  
│   │   ├── correlation\_scorer.py    \# Score 0-100 por par  
│   │   ├── multi\_timeframe\_scorer.py \# Alinhamento entre timeframes  
│   │   ├── confidence\_calculator.py \# Score de confiança multi-critério  
│   │   └── alert\_decision\_tree.py   \# Árvore de decisão para alertas  
│   │  
│   ├── alerts/                      \# Sistema de Alertas  
│   │   ├── \_\_init\_\_.py  
│   │   ├── alert\_engine.py          \# Motor de alertas de correlação  
│   │   ├── alert\_types.py           \# Tipos de alerta (anomalia, desvio, etc.)  
│   │   ├── cooldown\_manager.py      \# Cooldown entre alertas  
│   │   └── notification\_handler.py  \# Despacho de notificações  
│   │  
│   ├── monitoring/                  \# Tabela de Monitoramento  
│   │   ├── \_\_init\_\_.py  
│   │   ├── correlation\_table.py     \# Tabela de monitoramento em tempo real  
│   │   ├── heatmap\_generator.py     \# Geração de heatmap NxN  
│   │   ├── spread\_chart.py          \# Gráficos de spread normalizado  
│   │   └── health\_dashboard.py      \# Saúde do sistema de correlação  
│   │  
│   ├── ml/                          \# Machine Learning Específico  
│   │   ├── \_\_init\_\_.py  
│   │   ├── correlation\_features.py  \# Features de correlação para ML  
│   │   ├── correlation\_predictor.py \# Predição de mudança de correlação  
│   │   └── pair\_classifier.py       \# Classificação de pares por regime  
│   │  
│   ├── backtest/                    \# Backtesting  
│   │   ├── \_\_init\_\_.py  
│   │   ├── pair\_backtester.py       \# Backtester de estratégia de pares  
│   │   ├── walk\_forward.py          \# Walk-forward validation  
│   │   └── performance\_metrics.py   \# Sharpe, Drawdown, Win Rate  
│   │  
│   └── dashboard/                   \# Dashboard Web  
│       ├── \_\_init\_\_.py  
│       ├── app.py                   \# Servidor web (FastAPI/Flask)  
│       ├── templates/               \# HTML templates  
│       └── static/                  \# CSS/JS para visualização  
│  
├── config/  
│   └── correlation\_config.yaml      \# Configuração dos pares e thresholds  
│  
└── tests/  
    └── correlation/                 \# Testes do módulo de correlação  
        ├── test\_pearson\_engine.py  
        ├── test\_spread\_analyzer.py  
        ├── test\_anomaly\_detector.py  
        ├── test\_correlation\_scorer.py  
        └── test\_pair\_backtester.py


## **4. COMPONENTES DETALHADOS**

### **4.1 MOTOR DE CORRELAÇÃO MULTI-PAR (Camada 3 — Core)**

Este é o **coração do sistema**. Calcula correlações entre N pares em múltiplos timeframes.

┌─────────────────────────────────────────────────────────────────────┐  
│                    MOTOR DE CORRELAÇÃO MULTI-PAR                     │  
│                                                                     │  
│  PARES MONITORADOS (Configurável via YAML)                         │  
│  ├── Crypto-Crypto                                                 │  
│  │   ├── BTC/USDT ↔ ETH/USDT   (corr. positiva esperada ~0.85)   │  
│  │   ├── BTC/USDT ↔ SOL/USDT   (corr. positiva moderada ~0.70)   │  
│  │   ├── BTC/USDT ↔ BNB/USDT   (corr. positiva forte ~0.80)     │  
│  │   ├── ETH/USDT ↔ SOL/USDT   (corr. positiva ~0.75)           │  
│  │   └── BTC/USDT ↔ XRP/USDT   (corr. variável ~0.50-0.70)     │  
│  │                                                                 │  
│  ├── Crypto-Macro (Correlação Inversa/Variável)                   │  
│  │   ├── BTC ↔ DXY     (inversa esperada ~-0.40 a -0.70)         │  
│  │   ├── BTC ↔ SPX/NDX (positiva esperada ~0.30 a 0.60)          │  
│  │   ├── BTC ↔ Gold     (variável, às vezes inversa)             │  
│  │   └── BTC ↔ VIX     (inversa esperada ~-0.30 a -0.50)        │  
│  │                                                                 │  
│  └── Forex (Opcional — Fase 2)                                    │  
│      ├── EUR/USD ↔ GBP/USD  (positiva forte)                     │  
│      ├── USD/JPY ↔ EUR/USD  (inversa moderada)                   │  
│      └── AUD/USD ↔ NZD/USD  (positiva muito forte)               │  
│                                                                     │  
│  MÉTRICAS CALCULADAS POR PAR                                       │  
│  ├── Correlação Pearson (rolling 20, 50, 100)                     │  
│  ├── Correlação Spearman (rolling 50)                             │  
│  ├── Z-Score do Spread                                            │  
│  ├── Beta Rolling                                                 │  
│  ├── Delta de Correlação (velocidade de mudança)                  │  
│  ├── Teste de Cointegração (p-value)                              │  
│  └── Half-Life de Mean Reversion                                  │  
│                                                                     │  
│  TIMEFRAMES                                                        │  
│  ├── 1min, 5min, 15min  → Microestrutura (scalping)              │  
│  ├── 1h, 4h             → Intraday (swing curto)                 │  
│  └── 1d, 1w             → Estrutural (posição)                   │  
└─────────────────────────────────────────────────────────────────────┘

#### **Definição Matemática dos Cálculos**

CÁLCULOS CORE DO MOTOR  
│  
├── 1. CORRELAÇÃO DE PEARSON (Rolling)  
│   │   r = Σ\[(Xi - X̄)(Yi - Ȳ)\] / √\[Σ(Xi-X̄)² × Σ(Yi-Ȳ)²\]  
│   │  
│   ├── Window 20:  Correlação de curto prazo (ruído alto, reação rápida)  
│   ├── Window 50:  Correlação de médio prazo (equilíbrio ruído/sinal)  
│   └── Window 100: Correlação de longo prazo (tendência estrutural)  
│  
├── 2. CORRELAÇÃO DE SPEARMAN (Rank-Based)  
│   │   ρ = 1 - \[6·Σ(di²)\] / \[n(n²-1)\]  
│   │  
│   └── Vantagem: Robusta contra outliers e movimentos extremos  
│       Captura relações não-lineares que Pearson perde  
│  
├── 3. Z-SCORE DO SPREAD (Normalizado)  
│   │   Spread = ln(Preço\_A) - β·ln(Preço\_B)  (log-spread cointegrado)  
│   │   Z = (Spread - μ\_spread) / σ\_spread  
│   │  
│   ├── Z \> +2.0  → Spread expandido → possível CONVERGÊNCIA (long B, short A)  
│   ├── Z \< -2.0  → Spread contraído → possível DIVERGÊNCIA (long A, short B)  
│   ├── Z → 0     → Equilíbrio → sem sinal  
│   └── |Z| \> 3.0 → ANOMALIA → investigar quebra estrutural  
│  
├── 4. BETA ROLLING  
│   │   β = Cov(R\_A, R\_B) / Var(R\_B)  
│   │  
│   └── Monitora sensibilidade entre os ativos ao longo do tempo  
│       Mudança brusca no β → sinal de mudança de regime  
│  
├── 5. COINTEGRAÇÃO (Engle-Granger)  
│   │   H0: Séries NÃO são cointegradas  
│   │   Ha: Séries SÃO cointegradas (compartilham tendência de longo prazo)  
│   │  
│   ├── Passo 1: Regressão linear → resíduos  
│   ├── Passo 2: Teste ADF nos resíduos  
│   ├── p-value \< 0.05 → Cointegradas → Pair Trading viável  
│   └── p-value \> 0.10 → Não cointegradas → Cautela com mean reversion  
│  
├── 6. HALF-LIFE DE MEAN REVERSION  
│   │   Regressão: ΔSpread\_t = θ·Spread\_\{t-1\} + ε\_t  
│   │   Half-life = -ln(2) / θ  
│   │  
│   └── Tempo estimado para spread voltar à média  
│       HL \< 10 períodos: reversion rápida (bom para scalping)  
│       HL \> 50 períodos: reversion lenta (posição)  
│  
└── 7. DELTA DE CORRELAÇÃO (Velocidade de Mudança)  
    │   ΔCorr = Corr\_t - Corr\_\{t-n\}  
    │  
    └── |ΔCorr| \> 0.20 em 5 períodos → ALERTA de mudança de regime

\[!TIP\] **Prioridade de implementação**: Comece com Pearson + Z-Score do Spread + Cointegração. Esses três juntos já formam a base funcional de qualquer sistema de pair trading profissional.


### **4.2 TABELA DE MONITORAMENTO DE CORRELAÇÃO (O Painel Principal)**

Esta é a **interface central** do sistema — uma tabela que mostra todas as correlações em tempo real com indicadores visuais de anomalia.

┌──────────────────────────────────────────────────────────────────────────────────┐  
│                    TABELA DE MONITORAMENTO DE CORRELAÇÃO                          │  
├──────────────────────────────────────────────────────────────────────────────────┤  
│                                                                                  │  
│  PAR          │ CORR    │ CORR    │ CORR   │ Z-SCORE │ COINT  │ STATUS │ SCORE  │  
│               │ 20p     │ 50p     │ 100p   │ SPREAD  │ p-val  │        │ (0-100)│  
│  ─────────────┼─────────┼─────────┼────────┼─────────┼────────┼────────┼────────│  
│  BTC↔ETH      │ 🟢 0.87 │ 🟢 0.82 │ 🟢 0.79│ 🟢-0.3  │ 0.02✅ │ NORMAL │  35    │  
│  BTC↔SOL      │ 🟡 0.65 │ 🟢 0.72 │ 🟢 0.68│ 🟡+1.8  │ 0.08⚠ │ ATENÇÃO│  58    │  
│  BTC↔DXY      │ 🔴-0.75 │ 🟠-0.62 │ 🟡-0.45│ 🟠+2.3  │ 0.04✅ │ ALERTA │  72    │  
│  BTC↔SPX      │ 🟢 0.55 │ 🟢 0.48 │ 🟢 0.42│ 🟢-0.5  │ 0.15❌ │ NORMAL │  28    │  
│  ETH↔SOL      │ 🔴 0.40 │ 🟢 0.71 │ 🟢 0.73│ 🔴-2.5  │ 0.03✅ │ CRÍTICO│  85    │  
│  BTC↔GOLD     │ 🟡 0.22 │ 🟡 0.18 │ 🟡 0.10│ 🟢+0.1  │ 0.45❌ │ NEUTRO │  15    │  
│  ─────────────┼─────────┼─────────┼────────┼─────────┼────────┼────────┼────────│  
│                                                                                  │  
│  LEGENDA DE CORES (por desvio da média histórica):                              │  
│  🟢 Dentro do padrão (±1σ da média)                                             │  
│  🟡 Atenção: desvio moderado (1-2σ)                                             │  
│  🟠 Alerta: desvio significativo (2-2.5σ)                                       │  
│  🔴 Crítico: anomalia detectada (\>2.5σ) → OPORTUNIDADE ou RISCO                │  
│                                                                                  │  
│  FILTROS: \[Timeframe: ▼ 1h\] \[Tipo: ▼ Todos\] \[Min Score: ▼ 50\]                 │  
│  ATUALIZAÇÃO: A cada 5 segundos | Último update: 12:35:19 UTC-3               │  
└──────────────────────────────────────────────────────────────────────────────────┘

#### **Lógica de Coloração e Alertas da Tabela**

SISTEMA DE COLORAÇÃO INTELIGENTE  
│  
├── CORRELAÇÃO (cor baseada em desvio do valor esperado)  
│   │  
│   ├── Para pares com correlação positiva esperada (ex: BTC↔ETH, esperada ~0.80):  
│   │   ├── 🟢 corr \> esperada - 1σ          (dentro do normal)  
│   │   ├── 🟡 corr entre esperada - 2σ e -1σ (enfraquecendo)  
│   │   ├── 🟠 corr entre esperada - 2.5σ e -2σ (anomalia moderada)  
│   │   └── 🔴 corr \< esperada - 2.5σ         (anomalia severa → oportunidade)  
│   │  
│   └── Para pares com correlação negativa esperada (ex: BTC↔DXY, esperada ~-0.50):  
│       ├── 🟢 corr \< esperada + 1σ           (normal)  
│       ├── 🟡 corr entre esperada + 1σ e +2σ (enfraquecendo)  
│       ├── 🟠 corr entre esperada + 2σ e +2.5σ  
│       └── 🔴 corr \> esperada + 2.5σ         (correlação invertendo → ALERTA)  
│  
├── Z-SCORE DO SPREAD (absoluto)  
│   ├── 🟢 |Z| \< 1.0    → Equilíbrio  
│   ├── 🟡 |Z| 1.0-2.0  → Atenção — spread expandindo  
│   ├── 🟠 |Z| 2.0-2.5  → Zona de possível reversão  
│   └── 🔴 |Z| \> 2.5    → Zona de alta probabilidade de reversão  
│  
└── COINTEGRAÇÃO  
    ├── ✅ p \< 0.05   → Cointegrados (pair trading viável)  
    ├── ⚠️ p 0.05-0.10 → Marginal (cautela)  
    └── ❌ p \> 0.10   → Não cointegrados (mean reversion arriscado)


### **4.3 SISTEMA DE SCORING (Score 0-100 por Par)**

COMPOSIÇÃO DO SCORE DE CORRELAÇÃO (0-100 por par)  
│  
├── COMPONENTE 1: Força do Desvio Atual (Peso: 30%)  
│   └── Quão longe o Z-Score do spread está do equilíbrio?  
│       ├── |Z| \> 2.5  → 100 pontos (desvio extremo)  
│       ├── |Z| \> 2.0  → 80 pontos  
│       ├── |Z| \> 1.5  → 50 pontos  
│       └── |Z| \< 1.0  → 10 pontos  
│  
├── COMPONENTE 2: Velocidade de Mudança da Correlação (Peso: 25%)  
│   └── |ΔCorr\_5p| (variação da correlação em 5 períodos)  
│       ├── |ΔCorr| \> 0.30  → 100 pontos (mudança brusca)  
│       ├── |ΔCorr| \> 0.15  → 60 pontos  
│       └── |ΔCorr| \< 0.05  → 10 pontos  
│  
├── COMPONENTE 3: Confirmação de Volume (Peso: 20%)  
│   └── Volume relativo dos dois ativos suporta o movimento?  
│       ├── Volume A↑ + Volume B↓ (com correlação negativa) → 100 pontos  
│       ├── Volume A↑ + Volume B↑ (ambos ativos)           → 60 pontos  
│       └── Volume baixo em ambos                          → 10 pontos  
│  
├── COMPONENTE 4: Alinhamento Multi-Timeframe (Peso: 15%)  
│   └── Quantos timeframes confirmam a mesma direção?  
│       ├── 4+ timeframes alinhados  → 100 pontos  
│       ├── 3 timeframes alinhados   → 70 pontos  
│       ├── 2 timeframes alinhados   → 40 pontos  
│       └── Divergência entre TFs    → 10 pontos (CONFLITO)  
│  
└── COMPONENTE 5: Regime de Mercado (Peso: 10%)  
    └── O regime atual favorece a estratégia de correlação?  
        ├── Ranging/Lateral → 100 pontos (ideal para mean reversion)  
        ├── Trending moderado → 50 pontos  
        ├── Alta volatilidade → 30 pontos (risco alto, oportunidade)  
        └── Trending forte → 10 pontos (correlações instáveis)  
  
NÍVEIS DO SCORE:  
├── 0-30:    🟢 NEUTRO     → Sem oportunidade clara  
├── 31-50:   🟡 OBSERVAÇÃO → Padrão se formando, acompanhar  
├── 51-70:   🟠 ALERTA     → Desvio significativo, preparar  
├── 71-85:   🔴 ATIVO      → Alta probabilidade de reversão  
└── 86-100:  ⚡ CRÍTICO     → Anomalia severa, ação imediata


### **4.4 SISTEMA DE ALERTAS DE CORRELAÇÃO (Camada 5)**

\[!IMPORTANT\] Alertas sem validação são lixo. Cada alerta passa por **5 níveis de filtro** antes de ser disparado.

ÁRVORE DE DECISÃO PARA ALERTAS — 5 NÍVEIS DE VALIDAÇÃO  
│  
├── NÍVEL 1: FILTROS QUANTITATIVOS BÁSICOS  
│   ├── Z-Score do spread \> threshold? (padrão: |Z| \> 2.0)  
│   ├── Correlação desviou \> 2σ da média histórica?  
│   ├── Volume do par \> 80% da média 20 períodos?  
│   └── Dados são confiáveis? (quality score \> 75)  
│         ↓ (Se TODOS sim → Nível 2)  
│  
├── NÍVEL 2: CONFIRMAÇÃO MULTI-TIMEFRAME  
│   ├── ≥ 2 timeframes confirmam o sinal?  
│   ├── Timeframe principal (selecionado) confirmado?  
│   ├── Sem divergência severa entre 1h e 4h?  
│   └── Tendência do Z-Score é consistente (crescente ou decrescente)?  
│         ↓ (Se MAIORIA sim → Nível 3)  
│  
├── NÍVEL 3: VALIDAÇÃO ESTATÍSTICA  
│   ├── Par é cointegrado? (p \< 0.10)  
│   ├── Half-life \< 100 períodos? (mean reversion plausível)  
│   ├── Hurst exponent \< 0.5? (série tem caráter mean-reverting)  
│   └── Sem quebra estrutural recente? (Chow test / CUSUM)  
│         ↓ (Se MAIORIA sim → Nível 4)  
│  
├── NÍVEL 4: ANÁLISE DE CONTEXTO  
│   ├── Regime de mercado não é "crise/evento extremo"?  
│   ├── Sem evento macro nos próximos 60 min? (CPI, FOMC, NFP)  
│   ├── Liquidez dos dois ativos é suficiente?  
│   └── Não há outro alerta ativo para o mesmo par? (cooldown 5min)  
│         ↓ (Se TODOS sim → Nível 5)  
│  
└── NÍVEL 5: GERAÇÃO DO ALERTA  
    ├── Calcular Score final (0-100)  
    ├── Determinar tipo: CONVERGÊNCIA, DIVERGÊNCIA, ANOMALIA, ou REGIME\_CHANGE  
    ├── Estimar direção: qual ativo comprar/vender (se pair trade)  
    ├── Calcular confiança final (combinação dos 4 níveis)  
    └── → DISPARAR ALERTA 🔔

#### **Tipos de Alerta**

| Tipo de Alerta | Condição | Ação Sugerida |
| - | - | - |
| **CONVERGÊNCIA** | Z-Score extremo (\>2.0) + cointegração + volume | Spread vai voltar à média → Long ativo barato, Short ativo caro |
| **DIVERGÊNCIA** | Correlação caindo rapidamente + sem cointegração | Pares se descorrelando → Sair de posição existente |
| **ANOMALIA** | Z-Score \> 3.0 ou correlação inverteu sinal | Investigar: quebra estrutural, evento, manipulação |
| **REGIME\_CHANGE** | HMM detectou mudança + ΔCorr \> 0.30 em 5p | Recalibrar thresholds, ajustar estratégia |
| **SEASON\_ALERT** | Padrão sazonal ativado (abertura NYSE, vencimento) | Preparar para volatilidade de correlação |



### **4.5 ANÁLISE DE CONFLITO MULTI-TIMEFRAME (Detalhado)**

MAPA DE CORRELAÇÃO POR TIMEFRAME — EXEMPLO REAL  
│  
│  ┌──────────────────────────────────────────────────────────────────┐  
│  │ TF     │ CORR BTC↔ETH │ CORR BTC↔DXY │ Z-SPREAD │ DIAGNÓSTICO │  
│  ├────────┼──────────────┼──────────────┼──────────┼─────────────│  
│  │ 5min   │   +0.92      │   -0.30      │  -0.5    │ NORMAL      │  
│  │ 15min  │   +0.88      │   -0.45      │  -0.8    │ NORMAL      │  
│  │ 1h     │   +0.75      │   -0.55      │  -1.4    │ ATENÇÃO     │  
│  │ 4h     │   +0.60      │   -0.70      │  -2.1    │ ALERTA      │  
│  │ 1d     │   +0.82      │   -0.50      │  -0.3    │ NORMAL      │  
│  └──────────────────────────────────────────────────────────────────┘  
│  
├── CASO 1: ALINHAMENTO (Todos TFs concordam)  
│   → Score MTF = 100 | Sinal FORTE | Alta confiança  
│  
├── CASO 2: CONFLITO CURTO vs LONGO  
│   │ Exemplo: 5min positiva, 4h negativa  
│   │ → Correção temporária dentro da tendência macro  
│   │ → Score MTF penalizado, sinal MODERADO  
│   │ → Sugestão: seguir o timeframe mais longo  
│   │  
│   └── REGRA PRÁTICA:  
│       Se TF curto ≠ TF longo → TF longo prevalece com 70% peso  
│  
├── CASO 3: INVERSÃO EM ANDAMENTO  
│   │ TFs curtos mudando de sinal, TFs longos ainda no padrão anterior  
│   │ → ALERTA de possível mudança de regime  
│   │ → Score MTF reduzido, aguardar confirmação  
│   │  
│   └── TRIGGER: Quando ≥ 3 TFs consecutivos (5m, 15m, 1h) invertem  
│       enquanto 4h e 1d mantêm → REGIME\_CHANGE iminente  
│  
└── CASO 4: SEPARAÇÃO CRYPTO vs MACRO  
    │ Correlação crypto alta mas macro enfraquecendo  
    │ → BTC descolando do macro (CRYPTO\_NATIVE regime)  
    │ → Ajustar pesos: crypto correlations \> macro correlations  
    │  
    └── INDICADOR: BTC↔ETH estável, BTC↔SPX caindo → crypto nativo


### **4.6 CLASSIFICAÇÃO DE REGIME DE MERCADO PARA CORRELAÇÃO**

\[!NOTE\] Este módulo **reusa diretamente** o market\_regime\_hmm.py e regime\_detector.py existentes no projeto, adicionando uma camada de interpretação para correlação.

REGIMES E IMPACTO NA ESTRATÉGIA DE CORRELAÇÃO  
│  
├── 🟢 REGIME LATERAL / RANGING (HMM state=2)  
│   ├── Correlações oscilam ciclicamente e de forma previsível  
│   ├── Mean reversion é DOMINANTE → Z-Score funciona muito bem  
│   ├── Cointegração tende a ser estável  
│   └── ESTRATÉGIA: Pair trading agressivo, Z-Score ±2.0  
│  
├── 🟡 REGIME BULL (HMM state=0)  
│   ├── Correlações crypto-crypto tendem a ENFRAQUECER (alts divergem)  
│   ├── Correlação BTC↔SPX tende a ser positiva  
│   ├── BTC↔DXY tende a ser negativa  
│   └── ESTRATÉGIA: Pair trading cauteloso, foco em crypto↔macro  
│  
├── 🟠 REGIME BEAR (HMM state=1)  
│   ├── "Tudo cai junto" → correlações crypto-crypto → 1.0  
│   ├── Pair trading crypto↔crypto PERDE eficácia  
│   ├── BTC↔Gold pode ficar positivo (ambos caem menos)  
│   └── ESTRATÉGIA: Reduzir exposição, foco em hedges macro  
│  
└── 🔴 REGIME HIGH VOLATILITY / CRISE (HMM state=3)  
    ├── Correlações extremas e instáveis (→ ±1 bruscamente)  
    ├── Quebras de cointegração são frequentes  
    ├── Z-Score pode dar sinais falsos (spreads muito expandidos)  
    └── ESTRATÉGIA: MODO DEFENSIVO  
        ├── Thresholds mais conservadores (Z \> 3.0)  
        ├── Tamanho de posição reduzido a 50%  
        ├── Cooldown entre alertas aumentado para 15 min  
        └── Alertas de ANOMALIA têm prioridade máxima


### **4.7 GATILHOS E SINAIS PRECURSORES**

SINAIS QUE PRECEDEM ATIVAÇÃO/DESATIVAÇÃO DE CORRELAÇÃO  
│  
├── SINAL 1: DIVERGÊNCIA DE VOLUME ENTRE PARES  
│   ├── Ativo A: Volume crescendo (+50% vs média 20p)  
│   ├── Ativo B: Volume caindo (-30% vs média 20p)  
│   └── INDICA: Fluxo saindo de B e entrando em A → correlação vai mudar  
│  
├── SINAL 2: COMPRESSÃO DE VOLATILIDADE SIMULTÂNEA  
│   ├── GARCH forecast mostra volatilidade convergindo para lr\_variance  
│   ├── Bollinger Squeeze detectado em ambos os ativos  
│   └── INDICA: Breakout iminente → correlação pode saltar/cair  
│  
├── SINAL 3: QUEBRA GRADUAL DE CORRELAÇÃO  
│   ├── Corr\_20p caindo enquanto Corr\_100p estável  
│   ├── ΔCorr\_5p \> 0.10 por 3+ períodos consecutivos  
│   └── INDICA: Mudança de regime em andamento  
│  
├── SINAL 4: MOMENTUM DIVERGENTE (RSI / MACD)  
│   ├── RSI do ativo A subindo (\> 60)  
│   ├── RSI do ativo B caindo (\< 40)  
│   └── CONFIRMA: Correlação negativa se ativando  
│  
├── SINAL 5: ORDER FLOW IMBALANCE OPOSTO  
│   ├── Delta Volume positivo em A (mais compras)  
│   ├── Delta Volume negativo em B (mais vendas)  
│   └── INDICA: Smart money posicionando em direções opostas  
│  
├── SINAL 6: EVENTO MACRO IMINENTE  
│   ├── CPI, FOMC, NFP nos próximos 60 minutos  
│   ├── Correlações tendem a se intensificar pós-evento  
│   └── INDICA: Preparar para spike de correlação  
│  
└── SINAL 7: COINTEGRAÇÃO QUEBRANDO  
    ├── p-value subindo gradualmente (0.02 → 0.05 → 0.08 → 0.15)  
    ├── Half-life do spread aumentando (10 → 25 → 60 períodos)  
    └── INDICA: Relação de longo prazo enfraquecendo → SAIR de pair trade


## **5. DEPENDÊNCIAS TÉCNICAS**

### **5.1 Bibliotecas Python Necessárias**

| Biblioteca | Versão | Uso | Já Instalada? |
| - | - | - | - |
| numpy | ≥1.24 | Cálculos numéricos, correlação | ✅ Sim |
| pandas | ≥2.0 | DataFrames, rolling windows | ✅ Sim |
| scipy | ≥1.10 | Spearman, teste ADF, estatísticas | ⚠️ Verificar |
| statsmodels | ≥0.14 | Cointegração, ADF, VECM | ❌ Instalar |
| aiohttp | ≥3.9 | Coleta assíncrona de dados | ✅ Sim |
| yfinance | ≥0.2 | Dados macro (DXY, SPX, VIX) | ✅ Sim |
| xgboost | ≥2.0 | ML para predição de correlação | ✅ Sim |
| plotly | ≥5.18 | Gráficos interativos, heatmaps | ❌ Instalar |
| fastapi | ≥0.110 | Dashboard web | ❌ Instalar |
| uvicorn | ≥0.29 | Servidor ASGI para dashboard | ❌ Instalar |
| websockets | ≥12.0 | WebSocket para dashboard RT | ✅ Sim |
| arch | ≥6.0 | DCC-GARCH (opcional, Fase 2+) | ❌ Instalar (Fase 2) |


### **5.2 APIs Externas**

| API | Uso | Custo | Rate Limit |
| - | - | - | - |
| Binance REST | Klines, ticker, depth | Gratuita | 1200 req/min |
| Binance WebSocket | Dados em tempo real | Gratuita | Ilimitado (5 streams) |
| CoinGecko | Dominância, market cap | Gratuita | 30 req/min |
| yFinance | DXY, SPX, NDX, VIX, Gold | Gratuita | ~2000/hora |
| FRED API | Yields, inflação, PIB | Gratuita (API key) | 120/min |
| Alpha Vantage | Fallback dados macro | Gratuita (5/min) | 5 req/min |



## **6. FLUXO DE PROCESSAMENTO**

PIPELINE COMPLETO — DO DADO AO ALERTA  
│  
├── T+0ms: Tick de preço chega via WebSocket (BTC, ETH, SOL, etc.)  
│     ou: Timer periódico dispara coleta REST (klines)  
│     ↓  
├── T+5ms: COLETA → pair\_data\_collector busca dados de N pares  
│     ↓  
├── T+15ms: ALINHAMENTO → sync\_aligner sincroniza timestamps entre pares  
│     ↓  
├── T+25ms: QUALIDADE → data\_quality\_scorer atribui score a cada série  
│     ↓  
├── T+50ms: CÁLCULO DE CORRELAÇÃO (rolling Pearson/Spearman)  
│     + CÁLCULO DE SPREAD (log-spread, Z-Score)  
│     + CÁLCULO DE BETA (rolling)  
│     ↓  
├── T+70ms: MULTI-TIMEFRAME → Repetir cálculo para 1min, 5min, 1h, 4h, 1d  
│     ↓  
├── T+90ms: DETECÇÃO DE ANOMALIA → anomaly\_detector verifica desvios  
│     ↓  
├── T+100ms: SCORING → correlation\_scorer calcula score 0-100 por par  
│     ↓  
├── T+110ms: ÁRVORE DE DECISÃO → alert\_decision\_tree avalia 5 níveis  
│     ↓  
├── T+120ms: Se score \> threshold → GERA ALERTA  
│     ↓  
├── T+130ms: ATUALIZA TABELA DE MONITORAMENTO  
│     ↓  
├── T+140ms: ATUALIZA DASHBOARD (WebSocket push para frontend)  
│     ↓  
└── T+150ms: LOG + PERSISTÊNCIA (para backtesting e retreinamento)  
  
PERIODICIDADE DE ATUALIZAÇÃO:  
├── Dados tick (WebSocket): contínuo  
├── Klines 1min/5min: a cada 1 minuto  
├── Klines 1h/4h: a cada 5 minutos  
├── Klines 1d: a cada 30 minutos  
├── Dados macro (yFinance, FRED): a cada 5-15 minutos (cache)  
└── Cointegração (ADF test): a cada 1 hora (computacionalmente pesado)


## **7. CONFIGURAÇÃO — correlation\_config.yaml**

\# correlation\_config.yaml  
\# Configuração central do CORR-WATCH System  
  
system:  
  name: "CORR-WATCH"  
  version: "2.0"  
  update\_interval\_seconds: 5      \# Frequência de update da tabela  
  log\_level: "INFO"  
  
\# Pares monitorados  
pairs:  
  crypto\_crypto:  
    - pair: \["BTCUSDT", "ETHUSDT"\]  
      expected\_correlation: 0.80  
      correlation\_type: "positive"  
      priority: 1  
  
    - pair: \["BTCUSDT", "SOLUSDT"\]  
      expected\_correlation: 0.65  
      correlation\_type: "positive"  
      priority: 2  
  
    - pair: \["BTCUSDT", "BNBUSDT"\]  
      expected\_correlation: 0.75  
      correlation\_type: "positive"  
      priority: 2  
  
    - pair: \["ETHUSDT", "SOLUSDT"\]  
      expected\_correlation: 0.70  
      correlation\_type: "positive"  
      priority: 3  
  
  crypto\_macro:  
    - pair: \["BTCUSDT", "DXY"\]  
      expected\_correlation: -0.50  
      correlation\_type: "negative"  
      priority: 1  
      source\_b: "yfinance"  
  
    - pair: \["BTCUSDT", "SPX"\]  
      expected\_correlation: 0.40  
      correlation\_type: "positive"  
      priority: 2  
      source\_b: "yfinance"  
  
    - pair: \["BTCUSDT", "VIX"\]  
      expected\_correlation: -0.35  
      correlation\_type: "negative"  
      priority: 3  
      source\_b: "yfinance"  
  
\# Timeframes monitorados  
timeframes:  
  primary: "1h"                   \# Timeframe principal de decisão  
  all: \["5m", "15m", "1h", "4h", "1d"\]  
  weights:  
    "5m": 0.10  
    "15m": 0.15  
    "1h": 0.30                    \# Maior peso para TF principal  
    "4h": 0.25  
    "1d": 0.20  
  
\# Janelas de cálculo  
windows:  
  short: 20  
  medium: 50  
  long: 100  
  
\# Thresholds de alerta  
thresholds:  
  z\_score\_alert: 2.0              \# Z-Score para gerar alerta  
  z\_score\_critical: 2.5           \# Z-Score para alerta crítico  
  z\_score\_anomaly: 3.0            \# Z-Score para anomalia  
  
  correlation\_deviation\_alert: 0.20     \# Desvio de corr para alerta  
  correlation\_deviation\_critical: 0.30  \# Desvio de corr para crítico  
  
  delta\_correlation\_alert: 0.15         \# ΔCorr em 5 períodos  
  delta\_correlation\_critical: 0.25  
  
  cointegration\_pvalue\_max: 0.10        \# p-value máximo para cointegração  
  halflife\_max\_periods: 100             \# Half-life máximo aceitável  
  
  min\_volume\_ratio: 0.80               \# Volume mínimo vs média 20p  
  min\_score\_for\_alert: 60              \# Score mínimo para gerar alerta  
  min\_quality\_score: 75                \# Quality score mínimo dos dados  
  
\# Alertas  
alerts:  
  cooldown\_seconds: 300            \# 5 minutos entre alertas do mesmo par  
  max\_simultaneous: 5              \# Máximo de alertas ativos simultâneos  
  notification\_channels:  
    - "console"  
    - "log"  
    - "dashboard"  
    \# - "telegram"                 \# Futuro  
  
\# Regime adjustments  
regime\_adjustments:  
  ranging:                         \# Lateral → mais agressivo  
    z\_score\_alert: 1.8  
    min\_score\_for\_alert: 50  
  
  bear:                            \# Bear → mais conservador  
    z\_score\_alert: 2.5  
    min\_score\_for\_alert: 75  
  
  high\_volatility:                 \# Crise → modo defensivo  
    z\_score\_alert: 3.0  
    min\_score\_for\_alert: 85  
    cooldown\_seconds: 900          \# 15 minutos


## **8. ROADMAP DE IMPLEMENTAÇÃO (FASEADO)**

### **FASE 1 — FUNDAÇÃO (Semanas 1-2) 🔴 CRÍTICO**

| Tarefa | Arquivos | Dependências |
| - | - | - |
| Criar pacote correlation/ com estrutura de pastas | \_\_init\_\_.py, config.py | Nenhuma |
| Implementar pair\_data\_collector.py (coleta multi-par) | collector/pair\_data\_collector.py | Reusar context\_collector.\_fetch\_klines |
| Implementar sync\_aligner.py (alinhamento temporal) | collector/sync\_aligner.py | pandas |
| Implementar pearson\_engine.py (correlação rolling) | engine/pearson\_engine.py | numpy, pandas |
| Implementar spread\_analyzer.py (Z-Score do spread) | engine/spread\_analyzer.py | numpy |
| Criar correlation\_config.yaml | config/ | Nenhuma |
| Testes unitários da Fase 1 | tests/correlation/ | pytest |


**Resultado**: Motor básico de correlação funcionando para N pares com Z-Score.


### **FASE 2 — MOTOR ANALÍTICO COMPLETO (Semanas 3-4) 🟡 ALTA**

| Tarefa | Arquivos | Dependências |
| - | - | - |
| Implementar spearman\_engine.py | engine/ | scipy.stats.spearmanr |
| Implementar beta\_rolling.py | engine/ | numpy |
| Implementar cointegration.py (ADF + Engle-Granger) | engine/ | statsmodels |
| Implementar correlation\_matrix.py (NxN) | engine/ | numpy |
| Implementar anomaly\_detector.py (desvios de correlação) | detector/ | Phase 1 |
| Implementar regime\_change\_detector.py | detector/ | Reusar market\_regime\_hmm.py |
| Integrar mean\_reversion.py e hurst\_exponent.py | Reusar institutional/ | Existentes |
| Testes unitários da Fase 2 | tests/correlation/ | pytest |


**Resultado**: Motor analítico completo com Pearson, Spearman, cointegração, Z-Score, anomalia.


### **FASE 3 — SCORING + ALERTAS (Semana 5) 🟡 ALTA**

| Tarefa | Arquivos | Dependências |
| - | - | - |
| Implementar correlation\_scorer.py (score 0-100) | scoring/ | Fase 1-2 |
| Implementar multi\_timeframe\_scorer.py | scoring/ | Fase 1-2 |
| Implementar alert\_decision\_tree.py (5 níveis) | scoring/ | Fase 1-3 |
| Implementar alert\_engine.py (motor de alertas) | alerts/ | Fase 3 |
| Implementar cooldown\_manager.py | alerts/ | Nenhuma |
| Implementar correlation\_table.py (tabela de monitoramento) | monitoring/ | Fase 1-3 |
| Testes de integração | tests/correlation/ | pytest |


**Resultado**: Sistema de scoring e alertas funcional com tabela de monitoramento no console.


### **FASE 4 — DASHBOARD VISUAL (Semanas 6-7) 🟢 MÉDIA**

| Tarefa | Arquivos | Dependências |
| - | - | - |
| Implementar heatmap\_generator.py (heatmap NxN) | monitoring/ | plotly |
| Implementar spread\_chart.py (gráficos de spread) | monitoring/ | plotly |
| Implementar app.py (servidor FastAPI + WebSocket) | dashboard/ | fastapi, uvicorn |
| Criar templates HTML com gráficos interativos | dashboard/templates/ | plotly.js |
| Implementar push de dados em tempo real via WS | dashboard/ | websockets |


**Resultado**: Dashboard web acessível no navegador com heatmap, gráficos e alertas ao vivo.


### **FASE 5 — ML + BACKTESTING (Semanas 8-10) 🟢 MÉDIA**

| Tarefa | Arquivos | Dependências |
| - | - | - |
| Implementar correlation\_features.py | ml/ | Fase 1-3 |
| Implementar correlation\_predictor.py (XGBoost) | ml/ | Reusar ml/train\_model.py |
| Implementar pair\_backtester.py | backtest/ | Fase 1-3, numpy |
| Implementar walk\_forward.py | backtest/ | numpy |
| Implementar performance\_metrics.py (Sharpe, DDmax) | backtest/ | numpy |
| Treinar primeiro modelo com dados históricos | ml/ | Dados coletados nas fases 1-4 |


**Resultado**: Backtesting funcional + primeiro modelo ML de predição de correlação.


### **FASE 6 — AVANÇADO (Semanas 11+) 🟢 FUTURO**

| Tarefa | Complexidade |
| - | - |
| DCC-GARCH para correlação dinâmica | Alta (requer arch ou implementação manual) |
| LSTM para previsão de correlação | Muito Alta (requer tensorflow/pytorch) |
| Detector de manipulação (spoofing, wash trading) | Alta |
| Paper trading integrado com Binance testnet | Média |
| Análise de sazonalidade (hora, dia, mês) | Média |
| Integração com Telegram para alertas | Baixa |
| Otimização Bayesiana de hiperparâmetros | Alta |



## **9. AVALIAÇÃO CRÍTICA — O QUE REALMENTE FUNCIONA**

\[!WARNING\] **Verdade inconveniente**: Muitos sistemas de correlação falham porque tentam ser complexos demais antes de validar a base. A seguir, uma avaliação honesta.

### **✅ O Que FUNCIONA para Operar Correlação**

| Estratégia | Eficácia Comprovada | Condições |
| - | - | - |
| **Pair Trading com Z-Score** | ⭐⭐⭐⭐⭐ Alta | Pares cointegrados, regime lateral |
| **Mean Reversion de Spread** | ⭐⭐⭐⭐ Alta | Hurst \< 0.5, half-life razoável |
| **Detecção de Anomalia por Desvio** | ⭐⭐⭐⭐ Alta | Dados de qualidade, sem manipulação |
| **Multi-Timeframe como filtro** | ⭐⭐⭐⭐ Alta | Alinhamento de ≥3 TFs |
| **Regime Detection para ajuste** | ⭐⭐⭐⭐ Alta | HMM bem calibrado |


### **⚠️ O Que Funciona COM RESSALVAS**

| Estratégia | Eficácia | Ressalva |
| - | - | - |
| **Correlação Crypto↔Macro** | ⭐⭐⭐ Média | Dados macro atrasados (1d), correlação instável |
| **XGBoost para predição** | ⭐⭐⭐ Média | Necessita \> 6 meses de dados, risco de overfitting |
| **Cointegração em crypto** | ⭐⭐⭐ Média | Cointegração pode quebrar em tendências fortes |
| **Alertas automáticos** | ⭐⭐⭐ Média | Muitos falsos positivos sem validação manual |


### **❌ O Que NÃO Recomendo na Fase Inicial**

| Estratégia | Motivo |
| - | - |
| **LSTM para correlação** | Complexidade enorme, ganho marginal vs XGBoost para este caso |
| **Reinforcement Learning** | Requer milhões de dados de treino, convergência lenta |
| **DCC-GARCH** | Computacionalmente pesado, difícil de calibrar em crypto |
| **Sentimento social** | Dados de Twitter/Reddit são ruidosos demais para correlação |
| **Transformer** | Overkill — XGBoost + regras heurísticas dão resultado melhor com menos custo |



## **10. MÉTRICAS DE MONITORAMENTO DO SISTEMA**

DASHBOARD DE SAÚDE DO CORR-WATCH  
│  
├── PAINEL 1: STATUS DOS DADOS  
│   ├── Latência por fonte (Binance, yFinance, FRED)  
│   ├── Quality score por par (0-100)  
│   ├── Gaps detectados nas últimas 24h  
│   └── Taxa de dados válidos (%)  
│  
├── PAINEL 2: CORRELAÇÕES EM TEMPO REAL  
│   ├── Heatmap NxN de correlação  
│   ├── Gráfico de evolução temporal de cada par  
│   ├── Spread chart normalizado (Z-Score)  
│   └── Tabela de monitoramento principal  
│  
├── PAINEL 3: ALERTAS  
│   ├── Alertas ativos agora  
│   ├── Histórico 24h (com taxa de acerto)  
│   ├── Falsos positivos detectados  
│   └── Tempo médio entre alertas por par  
│  
├── PAINEL 4: PERFORMANCE  
│   ├── Score médio dos alertas emitidos  
│   ├── Accuracy do detector de anomalia  
│   ├── Latência do pipeline (ms)  
│   └── Uptime do sistema (%)  
│  
└── PAINEL 5: REGIME E CONTEXTO  
    ├── Regime atual (HMM state)  
    ├── VIX, DXY, dominância BTC  
    ├── Próximos eventos macro  
    └── Sazonalidade do momento


## **11. RESUMO FINAL**

| Aspecto | Decisão |
| - | - |
| **Linguagem** | Python 3.12+ (mesmo do projeto existente) |
| **Código reaproveitado** | ~40% do projeto existente |
| **Foco principal** | Z-Score do Spread + Pearson + Cointegração |
| **IA/ML** | XGBoost primeiro, LSTM depois (se necessário) |
| **Dashboard** | FastAPI + Plotly + WebSocket (real-time) |
| **Primeira versão funcional** | ~5 semanas (Fases 1-3) |
| **Versão completa com dashboard** | ~7 semanas (Fases 1-4) |
| **Pares iniciais** | BTC↔ETH, BTC↔SOL, BTC↔DXY, BTC↔SPX |


\[!TIP\] **Recomendação**: Comece pela **Fase 1** e valide manualmente os cálculos de correlação e Z-Score antes de construir alertas automáticos. Um motor analítico correto é mais valioso que mil alertas falsos.


*Documento gerado em 10/04/2026 | CORR-WATCH System v2.0 | Revisão Profissional*























