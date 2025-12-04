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
- intelligence_report_framework: Framework Dutch OSINT Guy per report intelligence
- intelligence_report_docx: Generatore DOCX per report intelligence
- intelligence_integration: Integrazione framework intelligence con sistema OSINT

Autore: FidelinvestigatorAI
Versione: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "FidelinvestigatorAI"

from .agent import FidelinvestigatorAI
from .html_parser import OSINTHTMLParser
from .data_analyzer import DataAnalyzer
from .psychological_profiler import PsychologicalProfiler
from .password_analyzer import PasswordAnalyzer
from .security_assessor import SecurityAssessor
from .report_generator import ReportGenerator

# Intelligence Report Framework (Dutch OSINT Guy Methodology)
from .intelligence_report_framework import (
    IntelligenceReportGenerator,
    ACHAnalyzer,
    SourceEvaluator,
    BLUFGenerator,
    ConfidenceLevel,
    SourceReliability,
    InformationAccuracy,
    Source,
    Hypothesis,
    KeyJudgment,
    EntityOfInterest,
    EstimativeLanguage,
    create_quick_report
)

from .intelligence_report_docx import (
    IntelligenceReportDOCX,
    generate_intelligence_report_docx
)

from .intelligence_integration import (
    IntelligenceReportIntegration,
    generate_dutch_osint_report
)

__all__ = [
    # Core Agent
    "FidelinvestigatorAI",
    # Parsers & Analyzers
    "OSINTHTMLParser",
    "DataAnalyzer",
    "PsychologicalProfiler",
    "PasswordAnalyzer",
    "SecurityAssessor",
    "ReportGenerator",
    # Intelligence Report Framework
    "IntelligenceReportGenerator",
    "ACHAnalyzer",
    "SourceEvaluator",
    "BLUFGenerator",
    "ConfidenceLevel",
    "SourceReliability",
    "InformationAccuracy",
    "Source",
    "Hypothesis",
    "KeyJudgment",
    "EntityOfInterest",
    "EstimativeLanguage",
    "create_quick_report",
    # DOCX Generation
    "IntelligenceReportDOCX",
    "generate_intelligence_report_docx",
    # Integration
    "IntelligenceReportIntegration",
    "generate_dutch_osint_report"
]
