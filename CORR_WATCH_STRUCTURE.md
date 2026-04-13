# Estrutura do Sistema CORR-WATCH v2.0

Este documento detalha a árvore de diretórios e a finalidade de cada arquivo no sistema de monitoramento de correlação.

## 📂 Arquitetura de Pastas

```text
CORR-WATCH/
├── config/                          # Configurações do sistema (v2.0)
│   └── correlation_config.yaml      # Definição de pares, thresholds e janelas
│
├── correlation/                     # [v2.0] Pacote principal modular
│   ├── __init__.py
│   ├── config.py                    # Loader da configuração YAML
│   ├── orchestrator.py              # Fachada principal para integração com o bot
│   │
│   ├── alerts/                      # Subsistema de Alertas
│   │   ├── __init__.py
│   │   └── alert_manager.py         # Gestão de notificações e rate-limiting
│   │
│   ├── collector/                   # Coleta e Tratamento de Dados
│   │   ├── __init__.py
│   │   ├── data_quality_scorer.py   # Validação de integridade dos dados
│   │   ├── pair_data_collector.py   # Client Binance e yFinance (Async)
│   │   └── sync_aligner.py          # Sincronização temporal de séries
│   │
│   ├── detector/                    # Identificação de Eventos
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py      # Busca por desvios estatísticos
│   │   └── regime_change_detector.py# Identifica mudança no comportamento do par
│   │
│   ├── engine/                      # Motores Analíticos (Matemática)
│   │   ├── __init__.py
│   │   ├── beta_rolling.py          # Cálculo de Hedge Ratio rolling
│   │   ├── cointegration.py         # Testes estatísticos de Cointegração (ADF)
│   │   ├── correlation_matrix.py    # Matriz NxN de correlação global
│   │   ├── pearson_engine.py        # Motor Correlation Pearson
│   │   ├── spearman_engine.py       # Motor Rank Correlation (Non-linear)
│   │   └── spread_analyzer.py       # Análise de Z-Score e Spread
│   │
│   ├── scoring/                     # Inteligência de Pontuação
│   │   ├── __init__.py
│   │   └── correlation_scorer.py    # Geração de Score 0-100 para IA
│   │
│   ├── ml/                          # [Stub] Futuros modelos de Machine Learning
│   ├── backtest/                    # [Stub] Ferramentas de validação histórica
│   ├── dashboard/                   # [Stub] Interface visual
│   └── monitoring/                  # [Stub] Health check do sistema
│
├── correlation_mvp/                 # [MVP] Baseline e Testes Integrados
│   ├── main.py                      # Engine principal do MVP (Forex-Aware)
│   ├── multi_timeframe_engine.py    # Análise em múltiplos tempos (1m a 1d)
│   ├── dashboard_mtf.py             # UI de monitoramento em tempo real
│   ├── smart_alerts.py              # Lógica de disparos e notificações
│   ├── data_cache.py                # Sistema de cache para dados OHLCV
│   │
│   ├── scripts/                     # Utilitários de Gestão e Monitoramento [NOVO]
│   │   ├── live_dashboard.sh        # Dashboard visual em tempo real
│   │   ├── mega_dashboard.sh        # Dashboard Deluxe (ASCII/Barras)
│   │   ├── health_monitor.sh        # Auditoria de erros e integridade
│   │   ├── validate_working.sh      # Validação rápida de 5 pontos
│   │   ├── relatorio_semanal.sh     # Gerador de relatórios Markdown
│   │   ├── ajuste_thresholds.py     # IA de recomendação de configurações
│   │   ├── snapshot.sh              # Captura de estado instantâneo
│   │   ├── analise_fim_de_semana.sh # Diagnóstico de gaps Forex
│   │   └── checkpoint_segunda.sh    # Check de reabertura de mercado
│   │
│   └── tests/
│       └── test_desalinhamento.py   # Teste de regressão (TimeZone Desync)
│
├── logs/                            # Registros de execução e erros
│   └── INCIDENT_LOG.md              # Registro de bugs críticos resolvidos (P0)
│
├── tests/                           # Suite de Testes (v2.0)
│   └── correlation/                 # Testes unitários do motor core
│
├── diagnose_error.sh                # Diagnóstico remoto de falhas
├── quick_check.sh                   # Script de cheque rápido de ambiente
├── new_methods_local.py             # Protótipo: Coleta Multi-Source (Binary/YF)
├── run_correlation_demo.py          # Demo visual do Core v2.0
├── run_orchestrator_demo.py         # Auditoria de Payload AI
├── test_forex_local.py              # Validação rápida de pares Forex
└── updater_remote.py                # Utilitário de deploy para produção
```

## 📝 Descrição dos Componentes Principais

### 1. Núcleo (correlation/)
*   **config.py**: Mapeia o arquivo YAML para dataclasses Python, garantindo tipos corretos em todo o sistema.
*   **orchestrator.py**: A "unidade lógica" que o bot principal deve usar. Ele coordena o fluxo: Coleta -> Alinhamento -> Motores -> Detectores -> Scoring.

### 2. Motores Analíticos (correlation/engine/)
*   **pearson_engine.py**: O básico. Mede a relação linear entre retornos.
*   **spearman_engine.py**: Identifica relações onde os ativos se movem juntos, mesmo que não seja de forma linear (ex: exponencial).
*   **spread_analyzer.py**: Essencial para Pair Trading. Mede o quão longe o par está de sua média histórica (Z-Score).
*   **cointegration.py**: Valida matematicamente se o par tem uma tendência de longo prazo estável.

### 3. Inteligência e Alertas (correlation/detector/ & alerts/)
*   **anomaly_detector.py**: Alerta sobre picos repentinos de correlação ou quebras de cointegração.
*   **regime_change_detector.py**: Útil para saber se o mercado mudou de um estado "Stable" para um estado de "Crisis" ou "Decoupling".
*   **alert_manager.py**: Controla a frequência dos alertas para evitar ruído excessivo no Telegram/Log.

### 4. Integração AI (correlation/scoring/)
*   **correlation_scorer.py**: Transforma dados brutos (p-values, z-scores, sigmas) em um payload JSON amigável para modelos como GPT-4 ou Groq.

### 5. Baseline MVP (correlation_mvp/)
*   **main.py**: Script principal da versão MVP, agora com detecção de horário de mercado Forex.
*   **dashboard_mtf.py**: Painel real-time para múltiplos pares.
*   **scripts/**: Suite de ferramentas para "Cockpit de Produção":
    *   **mega_dashboard.sh**: Interface visual premium para monitoramento constante.
    *   **health_monitor.sh**: Focado em detectar desequilíbrios matemáticos ou crashes silenciosos.
    *   **ajuste_thresholds.py**: Analisa o histórico de logs e sugere mudanças no `config.yaml`.
    *   **relatorio_semanal.sh**: Compila métricas de performance e economia de API.

### 6. Gestão de Incidentes e Qualidade
*   **INCIDENT_LOG.md**: Documenta a resolução do Bug P0 (mismatch de arrays entre Crypto e Forex).
*   **test_desalinhamento.py**: Garante que o fix de intersecção de índices pandas nunca sofra regressão.
*   **diagnose_error.sh**: Script de auditoria profunda usado para identificar falhas remotas no Oracle.

### 7. Utilitários e Logs
*   **new_methods_local.py**: Scripts de desenvolvimento para testar novos coletores.
*   **updater_remote.py**: Facilita o deploy seguro de patches de código.
*   **logs/**: Arquivos `.log` para auditoria e debugging.

