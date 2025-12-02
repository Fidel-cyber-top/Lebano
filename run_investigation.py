#!/usr/bin/env python3
"""
FidelinvestigatorAI - Script di Avvio Rapido (Enhanced AI Edition)
===================================================================

PRIMA DI ESEGUIRE:
1. Configura le API key in api_config.py
2. Verifica i percorsi

ESECUZIONE:

    python3 run_investigation.py              # Analizza tutti i file HTML
    python3 run_investigation.py file.html    # Analizza file specifico
    python3 run_investigation.py --verify     # Verifica configurazione

"""

import sys
import os

def load_config():
    """Carica configurazione API"""
    try:
        from api_config import (
            OPENAI_API_KEY, ANTHROPIC_API_KEY, PERPLEXITY_API_KEY,
            OPENAI_MODEL, ANTHROPIC_MODEL, PERPLEXITY_MODEL,
            INPUT_DIR, OUTPUT_DIR, LOGO_PATH, ORGANIZATION_NAME,
            VERBOSE, AI_ENABLED
        )
        return {
            'OPENAI_API_KEY': OPENAI_API_KEY,
            'ANTHROPIC_API_KEY': ANTHROPIC_API_KEY,
            'PERPLEXITY_API_KEY': PERPLEXITY_API_KEY,
            'OPENAI_MODEL': OPENAI_MODEL,
            'ANTHROPIC_MODEL': ANTHROPIC_MODEL,
            'PERPLEXITY_MODEL': PERPLEXITY_MODEL,
            'INPUT_DIR': INPUT_DIR,
            'OUTPUT_DIR': OUTPUT_DIR,
            'LOGO_PATH': LOGO_PATH,
            'ORGANIZATION_NAME': ORGANIZATION_NAME,
            'VERBOSE': VERBOSE,
            'AI_ENABLED': AI_ENABLED
        }
    except ImportError:
        print("[!] File api_config.py non trovato.")
        print("    Usando configurazione di default (senza AI).\n")
        return {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
            'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY', ''),
            'OPENAI_MODEL': 'gpt-4-turbo-preview',
            'ANTHROPIC_MODEL': 'claude-3-opus-20240229',
            'PERPLEXITY_MODEL': 'llama-3.1-sonar-large-128k-online',
            'INPUT_DIR': '/home/kali/Scrivania/suka/FidelAI/html',
            'OUTPUT_DIR': '/home/kali/Scrivania/suka/FidelAI/reports',
            'LOGO_PATH': None,
            'ORGANIZATION_NAME': 'FidelinvestigatorAI',
            'VERBOSE': True,
            'AI_ENABLED': True
        }


def verify_setup():
    """Verifica configurazione completa"""
    config = load_config()

    print("""
╔══════════════════════════════════════════════════════════════════╗
║        FidelinvestigatorAI - Verifica Configurazione             ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # API Status
    print("API KEYS:")
    apis = [
        ("OpenAI (GPT-4)", config['OPENAI_API_KEY'], "Correlazione dati"),
        ("Anthropic (Claude)", config['ANTHROPIC_API_KEY'], "Profilazione psicologica"),
        ("Perplexity", config['PERPLEXITY_API_KEY'], "Verifica OSINT real-time")
    ]

    all_configured = True
    for name, key, purpose in apis:
        if key:
            print(f"  ✓ {name}: Configurato - {purpose}")
        else:
            print(f"  ✗ {name}: NON configurato - {purpose}")
            all_configured = False

    print()

    # Paths
    print("PERCORSI:")
    print(f"  Input:  {config['INPUT_DIR']}")
    if os.path.exists(config['INPUT_DIR']):
        html_files = [f for f in os.listdir(config['INPUT_DIR']) if f.endswith('.html')]
        print(f"          ✓ Trovati {len(html_files)} file HTML")
    else:
        print(f"          ✗ Directory non esistente")

    print(f"  Output: {config['OUTPUT_DIR']}")
    if os.path.exists(config['OUTPUT_DIR']):
        print(f"          ✓ Directory esistente")
    else:
        print(f"          ○ Directory verrà creata")

    print()

    # Overall status
    if all_configured:
        print("STATO: ✓ Sistema pronto per analisi COMPLETA con AI")
    else:
        print("STATO: ○ Sistema pronto per analisi PARZIALE")
        print("       Configura le API mancanti in api_config.py per analisi avanzata")

    return config


def main():
    """Avvia l'investigazione"""

    # Check for --verify flag
    if '--verify' in sys.argv:
        verify_setup()
        return

    config = load_config()

    print("""
╔══════════════════════════════════════════════════════════════════╗
║     FidelinvestigatorAI - Enhanced AI Edition                    ║
║     Sistema di Intelligence OSINT con AI Integration             ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Import enhanced module
    try:
        import fidelinvestigator_ai_enhanced as investigator
    except ImportError:
        print("[!] Modulo fidelinvestigator_ai_enhanced.py non trovato.")
        print("    Assicurati che il file sia nella stessa directory.")
        sys.exit(1)

    # Configure
    class Config:
        pass

    cfg = Config()
    for key, value in config.items():
        setattr(cfg, key, value)

    # Create agent
    agent = investigator.FidelinvestigatorAI(cfg)

    if len(sys.argv) > 1 and sys.argv[1] != '--verify':
        # Specific file
        html_file = sys.argv[1]
        if os.path.exists(html_file):
            print(f"[*] Analisi file: {html_file}")
            agent.investigate(html_file, config['OUTPUT_DIR'])
        else:
            print(f"[!] File non trovato: {html_file}")
            sys.exit(1)
    else:
        # All files in directory
        input_dir = config['INPUT_DIR']

        if not os.path.exists(input_dir):
            print(f"[!] Directory non trovata: {input_dir}")
            print("    Modifica INPUT_DIR in api_config.py")
            sys.exit(1)

        html_files = [f for f in os.listdir(input_dir) if f.endswith('.html')]

        if not html_files:
            print(f"[!] Nessun file HTML trovato in: {input_dir}")
            sys.exit(1)

        print(f"[*] Trovati {len(html_files)} file HTML da analizzare\n")

        for html_file in html_files:
            file_path = os.path.join(input_dir, html_file)
            print(f"\n{'='*60}")
            print(f"[*] Analisi: {html_file}")
            print('='*60)
            agent.investigate(file_path, config['OUTPUT_DIR'])

    print("\n" + "="*60)
    print("ANALISI COMPLETATA")
    print("="*60)
    print(f"Report salvati in: {config['OUTPUT_DIR']}")


if __name__ == "__main__":
    main()
