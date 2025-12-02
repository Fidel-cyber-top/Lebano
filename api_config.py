#!/usr/bin/env python3
"""
FidelinvestigatorAI - Configurazione API Keys
==============================================

ISTRUZIONI:
1. Inserisci le tue API key nei campi sottostanti
2. Salva il file
3. Esegui: python3 fidelinvestigator_ai_enhanced.py

COME OTTENERE LE API KEY:

OPENAI (GPT-4):
- Vai su: https://platform.openai.com/api-keys
- Crea un nuovo API key
- Copia e incolla qui sotto

ANTHROPIC (Claude):
- Vai su: https://console.anthropic.com/
- Crea un nuovo API key
- Copia e incolla qui sotto

PERPLEXITY:
- Vai su: https://www.perplexity.ai/settings/api
- Genera un API key
- Copia e incolla qui sotto

NOTA: Puoi anche impostare le variabili d'ambiente:
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export PERPLEXITY_API_KEY="pplx-..."
"""

import os

# ============================================================================
# API KEYS - INSERISCI LE TUE CHIAVI QUI
# ============================================================================

# OpenAI GPT-4 - Per correlazione dati e analisi pattern
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Esempio: "sk-proj-xxxxxxxxxxxxxxxxxxxxx"

# Anthropic Claude - Per profilazione psicologica e redazione report
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# Esempio: "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx"

# Perplexity AI - Per verifica OSINT in tempo reale
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
# Esempio: "pplx-xxxxxxxxxxxxxxxxxxxxx"


# ============================================================================
# MODELLI AI (opzionale - modifica solo se necessario)
# ============================================================================

# OpenAI - modelli disponibili: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
OPENAI_MODEL = "gpt-4-turbo-preview"

# Anthropic - modelli disponibili: claude-3-opus-20240229, claude-3-sonnet-20240229
ANTHROPIC_MODEL = "claude-3-opus-20240229"

# Perplexity - modelli disponibili: llama-3.1-sonar-large-128k-online
PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"


# ============================================================================
# PERCORSI FILE (Kali Linux)
# ============================================================================

# Directory contenente i file HTML da analizzare
INPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/html"

# Directory dove salvare i report PDF generati
OUTPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/reports"

# Percorso logo (opzionale) - inserire percorso immagine PNG/JPG
LOGO_PATH = None
# Esempio: "/home/kali/Scrivania/suka/FidelAI/logo.png"

# Nome organizzazione per intestazione report
ORGANIZATION_NAME = "FidelinvestigatorAI"


# ============================================================================
# IMPOSTAZIONI AVANZATE
# ============================================================================

# Mostra output dettagliato durante l'esecuzione
VERBOSE = True

# Abilita analisi AI (False = solo analisi base senza AI)
AI_ENABLED = True

# Timeout richieste API in secondi
API_TIMEOUT = 60

# Numero massimo di retry per errori di rete
MAX_RETRIES = 3


# ============================================================================
# FUNZIONE DI VERIFICA
# ============================================================================

def verify_config():
    """Verifica la configurazione delle API"""
    print("=" * 50)
    print("VERIFICA CONFIGURAZIONE API")
    print("=" * 50)

    status = {
        "OpenAI": bool(OPENAI_API_KEY),
        "Anthropic": bool(ANTHROPIC_API_KEY),
        "Perplexity": bool(PERPLEXITY_API_KEY)
    }

    for provider, configured in status.items():
        symbol = "✓" if configured else "✗"
        state = "Configurato" if configured else "NON configurato"
        print(f"  {symbol} {provider}: {state}")

    print("-" * 50)

    configured_count = sum(status.values())
    if configured_count == 3:
        print("  STATO: Tutte le API configurate - Analisi COMPLETA")
        return True
    elif configured_count > 0:
        print(f"  STATO: {configured_count}/3 API configurate - Analisi PARZIALE")
        return True
    else:
        print("  STATO: Nessuna API configurata - Solo analisi BASE")
        print("\n  ATTENZIONE: Configura almeno una API per analisi avanzata")
        return False


if __name__ == "__main__":
    verify_config()

    print("\n" + "=" * 50)
    print("PERCORSI CONFIGURATI")
    print("=" * 50)
    print(f"  Input:  {INPUT_DIR}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Logo:   {LOGO_PATH or 'Non configurato'}")
