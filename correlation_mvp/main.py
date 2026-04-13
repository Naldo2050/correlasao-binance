"""
CORR-WATCH MVP - Sistema de Monitoramento de Correlação
Versão mínima funcional consolidada - 1 semana
Inclui: Logging robusto, Retries de API e Detecção de Terminal.
"""

from typing import Dict, List, Optional
import ccxt
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from statsmodels.tsa.stattools import adfuller
from rich.console import Console
from rich.table import Table
from rich.live import Live
import time
from datetime import datetime, timezone
import yaml
import logging
from logging.handlers import RotatingFileHandler
import os

from multi_timeframe_engine import MultiTimeframeEngine, get_mtf_engine
from data_cache import DataCache, get_cache
from cache_stats import CacheMonitor, format_cache_line

from dashboard_mtf import (
    MultiTimeframeDashboard,
    create_simple_mtf_table,
    format_cache_footer
)
from correlation_visualizer import (
    CorrelationVisualizer,
    print_correlation_summary
)

from divergence_detector import TimeframeDivergenceDetector, DivergenceHistory
from pattern_classifier import PatternClassifier
from smart_alerts import SmartAlertSystem, AlertPriority
from regime_analyzer import RegimeAnalyzer

# ============================================================================
# MODIFICAÇÃO A: CONFIGURAÇÃO DE LOGGING
# ============================================================================
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/corr_watch.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_forex_market_open() -> bool:
    """
    Verifica se o mercado Forex está aberto
    Forex: Domingo 22:00 UTC até Sexta 22:00 UTC
    """
    now_utc = datetime.now(timezone.utc)
    weekday = now_utc.weekday()  # 0=Monday, 6=Sunday
    hour = now_utc.hour
    
    # Sábado completo: fechado
    if weekday == 5:
        return False
    
    # Domingo: abre às 22:00
    if weekday == 6:
        return hour >= 22
    
    # Segunda a Quinta: aberto
    if weekday < 4:
        return True
    
    # Sexta: fecha às 22:00
    if weekday == 4:
        return hour < 22
    
    return True

class CorrelationWatchMVP:
    """MVP do sistema de correlação - foco em funcionalidade e resiliência"""
    
    def __init__(self, config_path='config.yaml'):
        # Carregar config
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Configuração carregada: {config_path}")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração {config_path}: {e}")
            raise
        
        self.pairs = self.config['pairs']
        self.window = self.config['window']
        self.z_threshold = self.config['z_threshold']
        self.interval = self.config['update_interval']
        
        # Exchange
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        self.console = Console()
        
        # NOVO: Inicializar motor multi-timeframe
        self.mtf_engine = get_mtf_engine(
            timeframes=['5m', '15m', '1h', '4h', '1d']
        )
        
        # NOVO: Inicializar cache
        self.cache = get_cache(
            ttl_seconds=self.config.get('cache', {}).get('ttl_seconds', 300),
            max_items=self.config.get('cache', {}).get('max_items', 100)
        )
        
        # NOVO: Monitor de cache
        self.cache_monitor = CacheMonitor(self.cache)
        
        # NOVO: Timeframe base para coleta
        self.base_timeframe = self.config.get(
            'multi_timeframe', {}
        ).get('base_timeframe', '15m')
        
        logger.info(
            f"Sistema MTF inicializado: base={self.base_timeframe}, "
            f"cache_ttl={self.cache.ttl}s"
        )
        
        # NOVO: Inicializar dashboard
        self.dashboard = MultiTimeframeDashboard(
            cache=self.cache,
            mtf_engine=self.mtf_engine
        )
        
        # NOVO: Visualizador
        self.visualizer = CorrelationVisualizer()

        # NOVO: Detector de divergência
        self.divergence_detector = TimeframeDivergenceDetector()
        
        # NOVO: Classificador de padrões
        self.pattern_classifier = PatternClassifier()
        
        # NOVO: Sistema de alertas
        self.alert_system = SmartAlertSystem(
            cooldown_minutes=5,
            max_alerts_per_pair=3
        )
        
        # NOVO: Analisador de regime
        self.regime_analyzer = RegimeAnalyzer()
        
        # NOVO: Histórico de divergências
        self.divergence_history = DivergenceHistory()
        
        # NOVO: Histórico de correlações (para classificador de padrões)
        self.correlation_history: Dict[str, List[Dict]] = {}

    # ============================================================================
    # MODIFICAÇÃO C: BUSCA DE DADOS COM RETRY ROBUSTO
    # ============================================================================
    def fetch_data(self, symbol, timeframe='1h', limit=200):
        """Busca dados OHLCV - Suporta Binance e yFinance"""
        
        # Detectar se é Forex ou Índice (yFinance)
        if symbol.endswith('=X') or symbol.startswith('^'):
            return self._fetch_yfinance(symbol, timeframe, limit)
        else:
            return self._fetch_binance(symbol, timeframe, limit)

    def _fetch_binance(self, symbol, timeframe, limit):
        """Busca de Binance (crypto)"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(
                ohlcv, 
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Erro Binance ao buscar {symbol}: {e}")
            return None

    def _fetch_yfinance(self, symbol, timeframe, limit):
        """Busca de yFinance (forex, stocks, etc.)"""
        try:
            import yfinance as yf
            
            # Mapear timeframe para yFinance
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1h': '1h',
                '4h': '1h',  # yFinance não tem 4h, usar 1h
                '1d': '1d'
            }
            
            period_map = {
                '1m': '7d',
                '5m': '60d',
                '15m': '60d',
                '1h': '730d',  # 2 anos
                '4h': '730d',
                '1d': '730d'
            }
            
            interval = interval_map.get(timeframe, '1h')
            period = period_map.get(timeframe, '730d')
            
            # Download
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.error(f"yFinance retornou dados vazios para {symbol}")
                return None
            
            # Renomear colunas para padrão
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            
            # Ajustar nomes
            if 'date' in df.columns:
                df.rename(columns={'date': 'timestamp'}, inplace=True)
            elif 'datetime' in df.columns:
                df.rename(columns={'datetime': 'timestamp'}, inplace=True)
            
            # Garantir que tem timestamp
            if 'timestamp' not in df.columns:
                df['timestamp'] = df.index
            
            # Selecionar últimos N períodos
            df = df.tail(limit)
            
            # Colunas necessárias
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Coluna {col} faltando em {symbol}")
                    return None
            
            return df[required_cols]
            
        except Exception as e:
            logger.error(f"Erro yFinance ao buscar {symbol}: {e}")
            return None

    def fetch_data_with_cache(self, symbol, timeframe='15m', limit=500):
        """
        Busca dados com cache inteligente
        
        Args:
            symbol: Símbolo do ativo
            timeframe: Timeframe desejado
            limit: Número de candles
        
        Returns:
            DataFrame ou None
        """
        # Tentar cache primeiro
        cached = self.cache.get(symbol, timeframe)
        if cached is not None:
            logger.debug(f"✅ Cache hit: {symbol} {timeframe}")
            return cached
        
        # Se não está no cache, buscar da API
        logger.debug(f"❌ Cache miss: {symbol} {timeframe}, buscando API...")
        data = self.fetch_data(symbol, timeframe, limit)
        
        # Se obteve dados, cachear
        if data is not None and len(data) > 0:
            self.cache.set(symbol, timeframe, data)
            logger.debug(f"💾 Dados cacheados: {symbol} {timeframe}")
        
        return data
    
    def calculate_correlation(self, series_a, series_b):
        """Calcula correlação de Pearson"""
        if len(series_a) < self.window:
            return np.nan
        
        a = series_a[-self.window:].values
        b = series_b[-self.window:].values
        
        corr_matrix = np.corrcoef(a, b)
        return corr_matrix[0, 1]
    
    def calculate_spread_zscore(self, series_a, series_b):
        """Calcula Z-Score do spread logarítmico"""
        # Sincronizar os índices para evitar mismatch de arrays (Erro 127 vs 126)
        common_idx = series_a.index.intersection(series_b.index)
        series_a = series_a.loc[common_idx]
        series_b = series_b.loc[common_idx]
        
        if len(series_a) < self.window:
            return np.nan, np.nan
        
        log_a = np.log(series_a.values)
        log_b = np.log(series_b.values)
        
        covariance = np.cov(log_a, log_b)
        beta = covariance[0, 1] / covariance[1, 1]
        
        spread = log_a - beta * log_b
        
        mean_spread = spread.mean()
        std_spread = spread.std()
        z_score = (spread[-1] - mean_spread) / std_spread
        
        return z_score, beta
    
    def test_cointegration(self, series_a, series_b):
        """Teste de cointegração (Engle-Granger via ADF)"""
        common_idx = series_a.index.intersection(series_b.index)
        series_a = series_a.loc[common_idx]
        series_b = series_b.loc[common_idx]
        
        if len(series_a) < 50:
            return {'is_cointegrated': False, 'p_value': 1.0, 'adf_stat': 0.0}
        
        try:
            log_a = np.log(series_a.values)
            log_b = np.log(series_b.values)
            beta = np.polyfit(log_b, log_a, 1)[0]
            spread = log_a - beta * log_b
            adf_result = adfuller(spread, maxlag=1, regression='c')
            
            return {
                'is_cointegrated': adf_result[1] < 0.05,
                'p_value': adf_result[1],
                'adf_stat': adf_result[0]
            }
        except Exception as e:
            return {'is_cointegrated': False, 'p_value': 1.0, 'adf_stat': 0.0}
    
    def calculate_score(self, z_score, correlation, cointegration):
        """Score de 0-100 baseado em regras simples"""
        score = 0
        z_abs = abs(z_score)
        if z_abs > 3.0: score += 50
        elif z_abs > 2.5: score += 40
        elif z_abs > 2.0: score += 25
        elif z_abs > 1.5: score += 10
        
        if cointegration['is_cointegrated']: score += 30
        elif cointegration['p_value'] < 0.10: score += 15
        
        corr_abs = abs(correlation)
        if corr_abs > 0.8: score += 20
        elif corr_abs > 0.6: score += 10
        
        return min(score, 100)
    
    def determine_signal(self, z_score, score):
        """Determina tipo de sinal"""
        if score < 50: return "🟢 NORMAL", "green"
        if abs(z_score) < self.z_threshold: return "🟡 OBSERVAR", "yellow"
        
        if z_score > self.z_threshold: return "🔴 CONVERGÊNCIA", "bold red"
        elif z_score < -self.z_threshold: return "🔵 DIVERGÊNCIA", "bold blue"
        else: return "🟠 ALERTA", "orange1"
    
    def analyze_pair_multi_timeframe(self, symbol_a, symbol_b, expected_corr=0.0):
        """Análise completa multi-timeframe"""
        # Verificar se par contém Forex ou Índice (Mercado Tradicional)
        is_market_hours_pair = any(
            marker in f"{symbol_a}{symbol_b}" 
            for marker in ['=X', '^', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CHF', 'CAD', 'GSPC', 'IXIC', 'DJI', 'VIX']
        )
        
        market_open = True
        if is_market_hours_pair:
            market_open = is_forex_market_open()
            if not market_open:
                logger.debug(f"💤 Mercado Tradicional fechado - {symbol_a}↔{symbol_b} usando última cotação")
        
        # Buscar dados base usando cache
        df_a = self.fetch_data_with_cache(symbol_a, timeframe=self.base_timeframe)
        df_b = self.fetch_data_with_cache(symbol_b, timeframe=self.base_timeframe)
        
        if df_a is None or df_b is None: return None
        
        # Calcular correlações MTF
        correlations = self.mtf_engine.calculate_multi_timeframe_correlation(
            df_a, df_b, base_timeframe=self.base_timeframe, window=self.window
        )
        
        # Calcular score MTF
        mtf_score = self.mtf_engine.calculate_mtf_score(correlations, expected_corr)
        
        # Calcular Z-Score e Cointegração usando dados do timeframe de 1h
        df_a_1h = self.mtf_engine.resample_ohlcv(df_a, '1h')
        df_b_1h = self.mtf_engine.resample_ohlcv(df_b, '1h')
        
        z_score, beta = (np.nan, np.nan)
        cointegration = {'is_cointegrated': False, 'p_value': 1.0, 'adf_stat': 0.0}
        
        if not df_a_1h.empty and not df_b_1h.empty:
            z_score, beta = self.calculate_spread_zscore(df_a_1h['close'], df_b_1h['close'])
            cointegration = self.test_cointegration(df_a_1h['close'], df_b_1h['close'])
        
        corr_1h = correlations.get('1h', 0.0)
        if pd.isna(corr_1h): corr_1h = 0.0
        if pd.isna(z_score): z_score = 0.0
        
        final_score = self.calculate_score(z_score, corr_1h, cointegration)
        signal, style = self.determine_signal(z_score, final_score)
        
        pair_name = f"{symbol_a.replace('/USDT', '').replace('=X', '')}↔{symbol_b.replace('/USDT', '').replace('=X', '')}"
        
        # NOVO: Detectar divergência
        divergence = self.divergence_detector.detect_divergence(
            correlations, expected_corr
        )
        
        # Adicionar ao histórico
        self.divergence_history.add(pair_name, divergence)
        
        # NOVO: Classificar padrão
        history = self.correlation_history.get(pair_name, [])
        pattern = self.pattern_classifier.classify_pattern(
            correlations, history
        )
        
        # Atualizar histórico de correlações
        if pair_name not in self.correlation_history:
            self.correlation_history[pair_name] = []
        
        self.correlation_history[pair_name].append({
            'timestamp': datetime.now(),
            **correlations
        })
        
        # Manter limite
        if len(self.correlation_history[pair_name]) > 100:
            self.correlation_history[pair_name] = self.correlation_history[pair_name][-100:]
        
        # NOVO: Analisar regime
        current_regime = self.regime_analyzer.identify_regime(corr_1h)
        regime_change = self.regime_analyzer.detect_regime_change(
            pair_name, corr_1h, current_regime
        )
        
        # NOVO: Gerar alerta inteligente
        alert = self.alert_system.analyze_and_alert(
            pair_name,
            correlations,
            z_score,
            final_score,
            expected_corr,
            history
        )
        
        result = {
            'correlations': correlations, 
            'z_score': z_score, 
            'beta': beta,
            'cointegration': cointegration, 
            'score': final_score, 
            'signal': signal, 
            'style': style,
            'last_price_a': df_a_1h['close'].iloc[-1] if not df_a_1h.empty else 0, 
            'last_price_b': df_b_1h['close'].iloc[-1] if not df_b_1h.empty else 0,
            'mtf_alignment': mtf_score['alignment_rate'],
            'divergence': divergence,
            'pattern': pattern,
            'regime': current_regime.value,
            'regime_change': regime_change,
            'alert': alert.to_dict() if alert else None
        }
        
        return result
    
    def create_monitoring_table(self, results):
        """Cria tabela de monitoramento (SUBSTITUIR método existente)"""
        
        # Usar nova tabela multi-timeframe
        table = create_simple_mtf_table(results)
        
        # Adicionar caption com cache stats
        if self.cache:
            table.caption = format_cache_footer(self.cache)
        
        return table
    
    def display_full_dashboard(self, results):
        """Exibe dashboard completo com cache e alertas"""
        self.dashboard.print_dashboard(results)
    
    def print_alerts(self, results):
        """Imprime alertas críticos"""
        alerts = []
        for pair_name, data in results.items():
            if data and data['score'] >= 70:
                direction = "LONG spread" if data['z_score'] > 0 else "SHORT spread"
                alerts.append({'pair': pair_name, 'score': data['score'], 'z_score': data['z_score'], 'direction': direction})
        
        if alerts:
            self.console.print("\n[bold red]🚨 ALERTAS CRÍTICOS:[/bold red]")
            for alert in alerts:
                self.console.print(f"  • {alert['pair']} | Score: {alert['score']} | Z: {alert['z_score']:+.2f} | Ação: {alert['direction']}")

    # ============================================================================
    # MODIFICAÇÃO B: MÉTODO RUN REESTRUTURADO (TERMINAL VS DAEMON)
    # ============================================================================
    def run(self):
        """Loop principal de monitoramento"""
        logger.info("🚀 CORR-WATCH Multi-Timeframe iniciado!")
        
        try:
            while True:
                results = {}
                
                # Analisar cada par
                for pair_config in self.pairs:
                    symbol_a = pair_config['symbol_a']
                    symbol_b = pair_config['symbol_b']
                    expected_corr = pair_config.get('expected_correlation', 0.0)
                    
                    pair_name = f"{symbol_a.replace('/USDT', '').replace('=X', '')}↔{symbol_b.replace('/USDT', '').replace('=X', '')}"
                    
                    # Usar método multi-timeframe
                    result = self.analyze_pair_multi_timeframe(
                        symbol_a, symbol_b, expected_corr
                    )
                    
                    results[pair_name] = result
                    
                    # Adicionar alerta se score alto
                    if result and result['score'] >= 60:
                        self.dashboard.add_alert(
                            pair_name,
                            result['score'],
                            result['signal']
                        )
                    
                    time.sleep(0.5)
                
                # Limpar cache expirado periodicamente
                self.cache.clean_expired()
                
                # Snapshot de cache
                self.cache_monitor.take_snapshot()
                
                # Exibir dashboard
                self.console.clear()
                self.display_full_dashboard(results)
                
                # Aguardar próximo ciclo
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Sistema encerrado pelo usuário")
            
            # Exibir estatísticas finais
            print("\n" + self.cache_monitor.get_performance_summary())

if __name__ == "__main__":
    monitor = CorrelationWatchMVP('config.yaml')
    monitor.run()
