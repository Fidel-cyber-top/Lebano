"""
FidelinvestigatorAI - File di Configurazione
=============================================

Modifica questo file per configurare i percorsi sulla tua macchina.
"""

# ============================================
# CONFIGURAZIONE PERCORSI
# ============================================

# Cartella contenente i file HTML da analizzare
INPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/html"

# Cartella dove salvare i report PDF generati
OUTPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/reports"

# Percorso del logo (lascia None se non hai un logo)
# Es: "/home/kali/Scrivania/suka/FidelAI/assets/logo.png"
LOGO_PATH = None

# ============================================
# CONFIGURAZIONE REPORT
# ============================================

# Nome dell'organizzazione che appare nel report
ORGANIZATION_NAME = "FidelinvestigatorAI"

# Titolo del report
REPORT_TITLE = "REPORT INFO INVESTIGATIVO"

# ============================================
# OPZIONI
# ============================================

# Mostra output dettagliato durante l'esecuzione
VERBOSE = True

# Formato data nel report (strftime)
DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%H:%M:%S"
