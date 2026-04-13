"""
CORR-WATCH System v2.0 — Orchestrator
=======================================
Ponto de integração principal do subsistema de correlação
com o `robo_sistema` / `window_processor.py`.
Garante a execução completa do pipeline para os pares configurados
e retorna o payload mastigado para a IA.
"""

import asyncio
import logging
from typing import Dict, Any, List

from correlation.config import CorrWatchConfig
from correlation.collector.pair_data_collector import PairDataCollector
from correlation.collector.sync_aligner import SyncAligner
from correlation.collector.data_quality_scorer import DataQualityScorer
from correlation.engine.pearson_engine import PearsonEngine
from correlation.engine.spearman_engine import SpearmanEngine
from correlation.engine.spread_analyzer import SpreadAnalyzer
from correlation.engine.beta_rolling import BetaRolling
from correlation.engine.cointegration import CointegrationTester
from correlation.detector.anomaly_detector import AnomalyDetector
from correlation.detector.regime_change_detector import RegimeChangeDetector
from correlation.scoring.correlation_scorer import CorrelationScorer

logger = logging.getLogger("corr_watch.orchestrator")


class CorrelationOrchestrator:
    """
    Orquestrador master do sistema de correlação.
    Pode ser instanciado uma única vez pelo bot principal
    e chamado a cada fechamento de vela (ex: a cada 1h).
    """

    def __init__(self, config_path: str = None):
        self.config = CorrWatchConfig(config_path)
        
        # Motores
        self.aligner = SyncAligner()
        self.quality_scorer = DataQualityScorer()
        self.pearson = PearsonEngine(windows=self.config.windows.all_windows)
        self.spearman = SpearmanEngine(windows=self.config.windows.all_windows)
        self.spread = SpreadAnalyzer(z_window=self.config.windows.medium)
        self.beta = BetaRolling(windows=self.config.windows.all_windows)
        self.coint = CointegrationTester()
        
        # Detectores
        self.anomaly_detector = AnomalyDetector(self.config.thresholds)
        self.regime_detector = RegimeChangeDetector()
        
        # Scorer
        self.scorer = CorrelationScorer()

    async def run_cycle(self) -> Dict[str, Any]:
        """
        Executa um ciclo completo de coleta, análise e detecção.
        
        Returns:
            Dict com os payloads de IA para cada par.
        """
        logger.info("Iniciando ciclo de análise CORR-WATCH...")
        
        # 1. Coleta
        async with PairDataCollector(self.config) as collector:
            # Usamos o timeframe primário e garantimos limit suficiente para as maiores janelas
            limit = max(self.config.windows.all_windows) + 50
            data = await collector.fetch_all_pairs(
                timeframe=self.config.timeframes.primary, 
                limit=limit
            )
            
        if not data:
            logger.error("Falha na coleta de dados (ciclo pulado)")
            return {}

        # 2. Pipeline por par
        ai_payloads = {}
        
        for pair_cfg in self.config.pairs:
            sym_a, sym_b = pair_cfg.symbol_a, pair_cfg.symbol_b
            pair_id = pair_cfg.pair_id
            
            if sym_a not in data or sym_b not in data:
                continue
                
            # Alinhamento
            aligned = self.aligner.align_pair(data[sym_a], data[sym_b], sym_a, sym_b, "inner")
            if aligned.empty:
                continue
                
            col_ret_a, col_ret_b = f"returns_{sym_a}", f"returns_{sym_b}"
            col_cl_a, col_cl_b = f"close_{sym_a}", f"close_{sym_b}"
            
            if col_ret_a in aligned.columns and col_ret_b in aligned.columns:
                # Engine Run
                p_res = self.pearson.calculate(aligned[col_ret_a], aligned[col_ret_b], pair_id)
                s_res = self.spearman.calculate(aligned[col_ret_a], aligned[col_ret_b], pair_id, p_res.current)
                b_res = self.beta.calculate(aligned[col_ret_a], aligned[col_ret_b], pair_id)
                z_res = self.spread.analyze(aligned[col_cl_a], aligned[col_cl_b], pair_id)
                c_res = self.coint.test(aligned[col_cl_a], aligned[col_cl_b], pair_id)
                
                # Detectors
                anomalies = self.anomaly_detector.detect_all(
                    pair_id=pair_id,
                    expected_correlation=pair_cfg.expected_correlation,
                    pearson_result=p_res,
                    spearman_result=s_res,
                    beta_result=b_res,
                    spread_result=z_res,
                    coint_result=c_res
                )
                
                regime_events = self.regime_detector.detect(
                    pair_id=pair_id,
                    pearson_result=p_res,
                    beta_result=b_res,
                    expected_correlation=pair_cfg.expected_correlation
                )
                current_regime = self.regime_detector.get_current_regime(pair_id)
                
                # Scorer
                score = self.scorer.evaluate(
                    pair_id, pair_cfg.expected_correlation,
                    p_res, s_res, b_res, z_res, c_res, anomalies, regime_events, current_regime
                )
                
                payload = self.scorer.build_ai_payload(
                    pair_id, score, pair_cfg.expected_correlation,
                    p_res, s_res, b_res, z_res, c_res, anomalies, current_regime
                )
                
                ai_payloads[pair_id] = payload
                
        logger.info(f"Ciclo concluído. Payloads gerados para {len(ai_payloads)} pares.")
        return ai_payloads
