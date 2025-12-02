"""
FidelinvestigatorAI - Agente Investigativo OSINT di Elite
=========================================================

Un agente investigativo avanzato con esperienza in intelligence (CIA, ROS, DIA, DCSA, DEA)
specializzato nell'analisi di report OSINT e nella produzione di relazioni investigative professionali.

Moduli:
- html_parser: Parsing e estrazione dati da report HTML OSINT
- data_analyzer: Correlazione e analisi dei dati estratti
- psychological_profiler: Profilazione psicologica del target
- password_analyzer: Analisi pattern costruzione password
- security_assessor: Valutazione sicurezza online del target
- report_generator: Generazione report PDF professionali

Autore: FidelinvestigatorAI
Versione: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "FidelinvestigatorAI"

from .agent import FidelinvestigatorAI
from .html_parser import OSINTHTMLParser
from .data_analyzer import DataAnalyzer
from .psychological_profiler import PsychologicalProfiler
from .password_analyzer import PasswordAnalyzer
from .security_assessor import SecurityAssessor
from .report_generator import ReportGenerator

__all__ = [
    "FidelinvestigatorAI",
    "OSINTHTMLParser",
    "DataAnalyzer",
    "PsychologicalProfiler",
    "PasswordAnalyzer",
    "SecurityAssessor",
    "ReportGenerator"
]
