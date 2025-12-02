#!/usr/bin/env python3
"""
FidelinvestigatorAI - Script di Avvio Rapido
============================================

Esegui questo script per avviare l'analisi:

    python3 run_investigation.py

Oppure analizza un file specifico:

    python3 run_investigation.py /percorso/file.html
"""

import sys
import os

# Importa configurazione
try:
    from config import INPUT_DIR, OUTPUT_DIR, LOGO_PATH, ORGANIZATION_NAME, VERBOSE
except ImportError:
    # Configurazione di default se config.py non esiste
    INPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/html"
    OUTPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/reports"
    LOGO_PATH = None
    ORGANIZATION_NAME = "FidelinvestigatorAI"
    VERBOSE = True

# Aggiorna CONFIG nello script standalone
import fidelinvestigator_standalone as investigator
investigator.CONFIG['INPUT_DIR'] = INPUT_DIR
investigator.CONFIG['OUTPUT_DIR'] = OUTPUT_DIR
investigator.CONFIG['LOGO_PATH'] = LOGO_PATH
investigator.CONFIG['ORGANIZATION_NAME'] = ORGANIZATION_NAME
investigator.CONFIG['VERBOSE'] = VERBOSE

def main():
    """Avvia l'investigazione"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║        FidelinvestigatorAI - Avvio Investigazione                ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    print(f"[*] Configurazione:")
    print(f"    Input:  {INPUT_DIR}")
    print(f"    Output: {OUTPUT_DIR}")
    print(f"    Logo:   {LOGO_PATH or 'Non configurato'}")
    print()

    # Crea agente
    agent = investigator.FidelinvestigatorAI()

    if len(sys.argv) > 1:
        # File specifico passato come argomento
        html_file = sys.argv[1]
        if os.path.exists(html_file):
            print(f"[*] Analisi file: {html_file}")
            agent.investigate_file(html_file)
        else:
            print(f"[!] File non trovato: {html_file}")
            sys.exit(1)
    else:
        # Analizza tutti i file nella cartella
        print(f"[*] Analisi tutti i file in: {INPUT_DIR}")
        agent.investigate_all()

if __name__ == "__main__":
    main()
