"""
CORR-WATCH System v2.0 — Integração com Orchestrator & AI Payload
===================================================================
Demonstra a execução do orquestrador via entrada única, como seria
feito no `window_processor` do bot principal. Exibe o Payload JSON
compactado gerado para consumo de LLMs.

Uso:
    python run_orchestrator_demo.py
"""

import asyncio
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from correlation.orchestrator import CorrelationOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")

async def main():
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║          CORR-WATCH ORCHESTRATOR — GERAÇÃO DE PAYLOAD AI       ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    # Instancia o Orchestrator (Apenas 1 vez na vida útil do bot)
    orchestrator = CorrelationOrchestrator()
    
    print("⏳ Executando ciclo completo de monitoramento de correlação...")
    
    # Roda o ciclo (A cada nova vela no bot)
    ai_payloads = await orchestrator.run_cycle()
    
    print("\n✅ CICLO CONCLUÍDO. Payloads gerados:\n")
    
    # Imprime o payload JSON formatado
    print(json.dumps(ai_payloads, indent=2, ensure_ascii=False))

    print("\n" + "═" * 70)
    print("  Este payload será injetado em: build_compact_payload.py")
    print("  Para análise macro via Groq/OpenAI no bot principal.")
    print("═" * 70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
