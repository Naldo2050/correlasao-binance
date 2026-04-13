"""
Teste de conectividade com APIs
Execute ANTES de rodar o sistema completo
"""

import ccxt
from rich.console import Console
import sys

console = Console()

def test_binance():
    """Testa conexão com Binance"""
    console.print("\n[bold cyan]🔍 Testando Binance API...[/bold cyan]")
    
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        
        # Teste 1: Buscar ticker
        ticker = exchange.fetch_ticker('BTC/USDT')
        console.print(f"✅ Ticker BTC/USDT: ${ticker['last']:,.2f}")
        
        # Teste 2: Buscar OHLCV
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=5)
        console.print(f"✅ OHLCV obtido: {len(ohlcv)} candles")
        console.print(f"   Último preço: ${ohlcv[-1][4]:,.2f}")
        
        # Teste 3: Verificar rate limit
        console.print(f"✅ Rate Limit ativo: {exchange.enableRateLimit}")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro na Binance: {e}[/bold red]")
        return False


def test_multiple_pairs():
    """Testa múltiplos pares"""
    console.print("\n[bold cyan]🔍 Testando múltiplos pares...[/bold cyan]")
    
    pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    exchange = ccxt.binance({'enableRateLimit': True})
    
    for pair in pairs:
        try:
            ticker = exchange.fetch_ticker(pair)
            console.print(f"✅ {pair}: ${ticker['last']:,.4f}")
        except Exception as e:
            console.print(f"❌ {pair}: {e}")
            return False
    
    return True


def test_data_quality():
    """Testa qualidade dos dados históricos"""
    console.print("\n[bold cyan]🔍 Testando qualidade dos dados...[/bold cyan]")
    
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        
        # Buscar 200 candles de 1h
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=200)
        
        console.print(f"✅ Candles obtidos: {len(ohlcv)}")
        
        # Verificar gaps
        timestamps = [x[0] for x in ohlcv]
        gaps = 0
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i-1]
            expected = 3600000  # 1 hora em ms
            if diff > expected * 1.5:
                gaps += 1
        
        if gaps > 0:
            console.print(f"⚠️  Gaps detectados: {gaps} (normal se poucos)")
        else:
            console.print(f"✅ Sem gaps temporais")
        
        # Verificar volume
        volumes = [x[5] for x in ohlcv]
        avg_volume = sum(volumes) / len(volumes)
        console.print(f"✅ Volume médio: {avg_volume:,.0f} USDT")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ Erro: {e}[/bold red]")
        return False


def main():
    console.print("[bold green]" + "="*60 + "[/bold green]")
    console.print("[bold green]  TESTE DE CONECTIVIDADE - CORR-WATCH MVP[/bold green]")
    console.print("[bold green]" + "="*60 + "[/bold green]")
    
    results = []
    
    # Teste 1
    results.append(("Binance API", test_binance()))
    
    # Teste 2
    results.append(("Múltiplos Pares", test_multiple_pairs()))
    
    # Teste 3
    results.append(("Qualidade de Dados", test_data_quality()))
    
    # Resumo
    console.print("\n[bold cyan]" + "="*60 + "[/bold cyan]")
    console.print("[bold cyan]RESUMO DOS TESTES[/bold cyan]")
    console.print("[bold cyan]" + "="*60 + "[/bold cyan]")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        style = "green" if passed else "red"
        console.print(f"[{style}]{status}[/{style}] - {test_name}")
        if not passed:
            all_passed = False
    
    console.print()
    if all_passed:
        console.print("[bold green]🎉 TODOS OS TESTES PASSARAM! Sistema pronto para rodar.[/bold green]")
        return 0
    else:
        console.print("[bold red]⚠️  ALGUNS TESTES FALHARAM. Corrija antes de prosseguir.[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
