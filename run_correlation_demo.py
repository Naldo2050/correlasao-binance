"""
CORR-WATCH System v2.0 — Script de Validação Fases 1 e 2
==========================================================
Coleta dados reais do Binance/yFinance, calcula todo o motor
de correlações (Pearson, Spearman, Spread, Beta, Cointegração)
e detecta anomalias e mudanças de regime.

Uso:
    python run_correlation_demo.py
"""

import asyncio
import logging
import sys
import os

# Garante que o módulo correlation está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from correlation.config import CorrWatchConfig
from correlation.collector.pair_data_collector import PairDataCollector
from correlation.collector.sync_aligner import SyncAligner
from correlation.collector.data_quality_scorer import DataQualityScorer

from correlation.engine.pearson_engine import PearsonEngine
from correlation.engine.spearman_engine import SpearmanEngine
from correlation.engine.spread_analyzer import SpreadAnalyzer
from correlation.engine.beta_rolling import BetaRolling
from correlation.engine.cointegration import CointegrationTester
from correlation.engine.correlation_matrix import CorrelationMatrix

from correlation.detector.anomaly_detector import AnomalyDetector
from correlation.detector.regime_change_detector import RegimeChangeDetector

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-35s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("corr_watch.demo")


# ============================================================================
# FORMATAÇÃO DO CONSOLE
# ============================================================================

def print_header():
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    CORR-WATCH SYSTEM v2.0                      ║")
    print("║          Sistema de Monitoramento de Correlação                ║")
    print("║              ── Fases 1 & 2: Motor Completo ──                 ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

def print_quality_table(quality_reports: dict):
    print("\n┌─────────────────────────────────────────────────────────────┐")
    print("│                    QUALIDADE DOS DADOS                       │")
    print("├──────────┬────────┬──────────┬──────┬──────────┬────────────┤")
    print("│ Símbolo  │ Score  │ Nível    │ Gaps │ Outliers │ Completo   │")
    print("├──────────┼────────┼──────────┼──────┼──────────┼────────────┤")

    for symbol, report in sorted(quality_reports.items()):
        level_icon = {
            "HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🟠", "CRITICAL": "🔴",
        }.get(report.level.value, "❓")

        print(
            f"│ {symbol:<8} │ {report.score:>5.1f} │ "
            f"{level_icon} {report.level.value:<6} │ {report.gap_count:>4} │ "
            f"{report.outlier_count:>8} │ {report.completeness:>9.1%} │"
        )

    print("└──────────┴────────┴──────────┴──────┴──────────┴────────────┘")

def print_main_table(results_payload: dict, config: CorrWatchConfig):
    print("\n┌─────────────────────────────────────────────────────────────────────────────────────────────────┐")
    print("│                                  TABELA DE ANÁLISE COMPLETA                                     │")
    print("├────────────┬──────────┬──────────┬──────────┬──────────┬────────┬────────┬───────┬────────────┤")
    print("│ PAR        │ PEARSON  │ SPEARMAN │ Z-SCORE  │   ZONE   │ HL(p)  │ BETA   │ COINT │ REGIME     │")
    print("├────────────┼──────────┼──────────┼──────────┼──────────┼────────┼────────┼───────┼────────────┤")

    for pair_id in sorted(results_payload.keys()):
        data = results_payload[pair_id]
        pearson = data.get("pearson")
        spearman = data.get("spearman")
        spread = data.get("spread")
        beta = data.get("beta")
        coint = data.get("coint")
        regime = data.get("regime")

        # Pearson W50
        if pearson and 50 in pearson.current:
            color = PearsonEngine().get_color_code(pearson.current[50], 0, 0.1)
            p_str = f"{color}{pearson.current[50]:+.4f}\033[0m"
        else:
            p_str = "   N/A  "

        # Spearman W50
        if spearman and 50 in spearman.current:
            s_str = f"{spearman.current[50]:+.4f}"
            if spearman.has_nonlinearity:
                s_str = f"\033[33m{s_str}\033[0m" # Amarelo se não linear
        else:
            s_str = "   N/A  "

        # Z-Score
        if spread and spread.z_score_series is not None:
            z_color = spread.get_z_color()
            z_str = f"{z_color}{spread.z_score_current:+.2f}\033[0m"
            zone_str = spread.zone.value[:8]
            hl_str = f"{spread.half_life:.0f}" if spread.half_life and spread.half_life < 999 else "N/A"
        else:
            z_str = "   N/A  "
            zone_str = "  N/A   "
            hl_str = "N/A"

        # Beta
        b_str = f"{beta.current.get(50, 0):+.2f}" if beta and 50 in beta.current else " N/A"

        # Cointegration
        c_icon = coint.status_icon if coint else "❓"
        c_str = f"{c_icon}"

        # Regime
        r_str = regime[0].current_regime.value[:10] if regime else "STABLE    "

        # Label
        lbl = pair_id.replace("USDT", "")
        if len(lbl) > 10: lbl = lbl[:10]

        print(
            f"│ {lbl:<10} │ {p_str:<18} │ {s_str:<18} │ {z_str:<18} │ {zone_str:<8} │ {hl_str:>6} │ {b_str:>6} │   {c_str}  │ {r_str:<10} │"
        )
    print("└────────────┴──────────┴──────────┴──────────┴──────────┴────────┴────────┴───────┴────────────┘")
    print("  Legenda Cointegração: ✅ Viável | ⚠️ Marginal | ❌ Não Cointegrado | 🟡 Spearman Não-Linear")

def print_anomalies(anomalies_dict: dict):
    print("\n┌─────────────────────────────────────────────────────────────┐")
    print("│                     ANOMALIAS DETECTADAS                     │")
    print("├─────────────────────────────────────────────────────────────┤")
    total = sum(len(a) for a in anomalies_dict.values())
    if total == 0:
        print("│ ✅ Nenhuma anomalia crítica/alerta no momento.               │")
    else:
        for pair_id, anomalies in anomalies_dict.items():
            for a in anomalies:
                print(f"│ {a.severity_icon} {pair_id}: {a.description:<42} │")
    print("└─────────────────────────────────────────────────────────────┘")


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

async def run_demo():
    print_header()
    
    # 1. Configuração
    config = CorrWatchConfig()
    logger.info(f"Pares: {len(config.pairs)} | Timeframe: {config.timeframes.primary}")

    # 2. Coleta de Dados
    async with PairDataCollector(config) as collector:
        data = await collector.fetch_all_pairs(timeframe=config.timeframes.primary, limit=200)
    
    if not data:
        return

    # 3. Qualidade
    reports = DataQualityScorer().evaluate_batch(data)
    print_quality_table(reports)

    # 4. Alinhamento Global Crypto (para Matriz NxN)
    aligner = SyncAligner()
    binance_data = {k: v for k, v in data.items() if k in config.all_symbols}
    aligned_crypto = aligner.align_multiple(binance_data, method="inner")
    
    # 5. Inicializa Motores (Fase 1 e 2)
    pearson_eng = PearsonEngine(windows=config.windows.all_windows)
    spearman_eng = SpearmanEngine(windows=config.windows.all_windows)
    spread_eng = SpreadAnalyzer(z_window=config.windows.medium)
    beta_eng = BetaRolling(windows=config.windows.all_windows)
    coint_eng = CointegrationTester()
    anomaly_det = AnomalyDetector(thresholds=config.thresholds)
    regime_det = RegimeChangeDetector()

    results_payload = {}

    # Executa por par (Alinhamento par-a-par para não perder períodos)
    for pair_cfg in config.pairs:
        sym_a, sym_b = pair_cfg.symbol_a, pair_cfg.symbol_b
        pair_id = pair_cfg.pair_id
        
        if sym_a not in data or sym_b not in data:
            continue
            
        aligned_pair = aligner.align_pair(data[sym_a], data[sym_b], sym_a, sym_b, "inner")
        if aligned_pair.empty: continue
        
        col_ret_a, col_ret_b = f"returns_{sym_a}", f"returns_{sym_b}"
        col_close_a, col_close_b = f"close_{sym_a}", f"close_{sym_b}"
        
        if col_ret_a in aligned_pair.columns and col_ret_b in aligned_pair.columns:
            # Motores de Retornos
            p_res = pearson_eng.calculate(aligned_pair[col_ret_a], aligned_pair[col_ret_b], pair_id)
            s_res = spearman_eng.calculate(aligned_pair[col_ret_a], aligned_pair[col_ret_b], pair_id, p_res.current)
            b_res = beta_eng.calculate(aligned_pair[col_ret_a], aligned_pair[col_ret_b], pair_id)
            
            # Motores de Preços (Close)
            z_res = spread_eng.analyze(aligned_pair[col_close_a], aligned_pair[col_close_b], pair_id)
            c_res = coint_eng.test(aligned_pair[col_close_a], aligned_pair[col_close_b], pair_id)
            
            # Detecção
            regime = regime_det.detect(pair_id, pearson_result=p_res, beta_result=b_res, expected_correlation=pair_cfg.expected_correlation)
            
            results_payload[pair_id] = {
                "expected_correlation": pair_cfg.expected_correlation,
                "pearson": p_res,
                "spearman": s_res,
                "beta": b_res,
                "spread": z_res,
                "coint": c_res,
                "regime": regime
            }

    # 6. Deteccão Globais de Anomalias
    anomalies = anomaly_det.detect_batch(results_payload)

    # 7. Print Matriz Pearson
    matrix = CorrelationMatrix()
    matrix.update(aligned_crypto, windows=config.windows.all_windows)
    print(matrix.format_table(window=config.windows.medium))

    # 8. Tabelas Finais
    print_main_table(results_payload, config)
    print_anomalies(anomalies)

    print("\n" + "═" * 70)
    print("  ✅ FASE 2 — Testes do Motor Analítico Concluídos com Sucesso!")
    print("═" * 70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        pass
