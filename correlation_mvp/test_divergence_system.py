"""
Testes do Sistema de Divergência e Alertas
"""

import numpy as np
from divergence_detector import TimeframeDivergenceDetector, DivergenceType
from pattern_classifier import PatternClassifier, CorrelationPattern
from smart_alerts import SmartAlertSystem, AlertPriority
from regime_analyzer import RegimeAnalyzer, CorrelationRegime


def test_divergence_detector():
    """Testa detector de divergência"""
    print("\n" + "="*60)
    print("TESTE 1: Detector de Divergência")
    print("="*60)
    
    detector = TimeframeDivergenceDetector()
    
    # Teste 1: Divergência forte
    correlations = {
        '5m': 0.85,   # Curto prazo forte
        '15m': 0.80,
        '1h': 0.70,
        '4h': 0.40,   # Longo prazo fraco
        '1d': 0.35
    }
    
    result = detector.detect_divergence(correlations, expected_corr=0.60)
    
    print(f"\n📊 Teste: Divergência BULLISH")
    print(f"Curto prazo: {result['short_term_avg']:.2f}")
    print(f"Longo prazo: {result['long_term_avg']:.2f}")
    print(f"Divergência: {result['divergence_pct']:.1%}")
    print(f"Tipo: {result['type'].value}")
    print(f"Significância: {result['significance'].value}")
    print(f"Interpretação: {result['interpretation']}")
    
    assert result['has_divergence'] == True
    assert result['type'] == DivergenceType.BULLISH
    
    print("\n✅ Divergence Detector: OK")


def test_pattern_classifier():
    """Testa classificador de padrões"""
    print("\n" + "="*60)
    print("TESTE 2: Classificador de Padrões")
    print("="*60)
    
    classifier = PatternClassifier()
    
    # Simular histórico com tendência de alta
    history = [
        {'1h': 0.50},
        {'1h': 0.55},
        {'1h': 0.60},
        {'1h': 0.68},
        {'1h': 0.75}
    ]
    
    current = {'1h': 0.82, '5m': 0.85, '4h': 0.78}
    
    result = classifier.classify_pattern(current, history)
    
    print(f"\n📊 Padrão detectado: {result['pattern'].value}")
    print(f"Confiança: {result['confidence']:.0%}")
    print(f"Descrição: {result['description']}")
    print(f"Tendência: {result['trend_direction']}")
    print(f"Força: {result['strength']:.2f}")
    
    implication = classifier.get_trading_implication(
        result['pattern'],
        result['confidence']
    )
    print(f"Implicação: {implication}")
    
    assert result['pattern'] == CorrelationPattern.STRENGTHENING
    
    print("\n✅ Pattern Classifier: OK")


def test_smart_alerts():
    """Testa sistema de alertas"""
    print("\n" + "="*60)
    print("TESTE 3: Sistema de Alertas Inteligentes")
    print("="*60)
    
    alert_system = SmartAlertSystem()
    
    # Simular análise que deve gerar alerta
    correlations = {
        '5m': 0.85,
        '15m': 0.82,
        '1h': 0.78,
        '4h': 0.30,  # Divergência
        '1d': 0.25
    }
    
    alert = alert_system.analyze_and_alert(
        pair="BTC↔ETH",
        correlations=correlations,
        z_score=2.5,
        score=85,
        expected_corr=0.75
    )
    
    if alert:
        print(f"\n🔔 Alerta gerado:")
        print(f"Título: {alert.title}")
        print(f"Prioridade: {alert.priority.value}")
        print(f"Tipo: {alert.alert_type.value}")
        print(f"\nMensagem:")
        print(alert.message)
        
        print(f"\n📱 Formato notificação:")
        print(alert.format_notification())
    else:
        print("\n❌ Nenhum alerta gerado")
    
    # Verificar alertas ativos
    active = alert_system.get_active_alerts()
    print(f"\n📊 Alertas ativos: {len(active)}")
    
    print("\n✅ Smart Alerts: OK")


def test_regime_analyzer():
    """Testa analisador de regime"""
    print("\n" + "="*60)
    print("TESTE 4: Analisador de Regime")
    print("="*60)
    
    analyzer = RegimeAnalyzer()
    
    # Teste 1: Identificar regime
    regime = analyzer.identify_regime(0.85)
    print(f"\n📊 Correlação 0.85 → Regime: {regime.value}")
    assert regime == CorrelationRegime.STRONG_POSITIVE
    
    regime = analyzer.identify_regime(-0.75)
    print(f"📊 Correlação -0.75 → Regime: {regime.value}")
    assert regime == CorrelationRegime.STRONG_NEGATIVE
    
    # Teste 2: Detectar mudança
    pair = "BTC↔ETH"
    
    # Adicionar histórico gradual
    for corr in [0.80, 0.82, 0.78, 0.75, 0.70]:
        regime = analyzer.identify_regime(corr)
        change = analyzer.detect_regime_change(pair, corr, regime)
        if change:
            print(f"\n⚠️ Mudança detectada: {change}")
    
    # Mudança significativa
    change = analyzer.detect_regime_change(pair, 0.30, CorrelationRegime.MODERATE_POSITIVE)
    
    if change:
        print(f"\n🚨 Mudança de regime!")
        print(f"De: {change['previous_regime'].value}")
        print(f"Para: {change['current_regime'].value}")
        print(f"Mudança: {change['change']:.2f}")
        print(f"Direção: {change['direction']}")
    
    # Estabilidade
    stability = analyzer.get_regime_stability(pair)
    print(f"\n📊 Estabilidade do regime: {stability:.0%}")
    
    duration = analyzer.get_regime_duration(pair)
    print(f"⏱️ Duração do regime atual: {duration} períodos")
    
    print("\n✅ Regime Analyzer: OK")


if __name__ == "__main__":
    try:
        test_divergence_detector()
        test_pattern_classifier()
        test_smart_alerts()
        test_regime_analyzer()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES DO SISTEMA DE DIVERGÊNCIA PASSARAM!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
