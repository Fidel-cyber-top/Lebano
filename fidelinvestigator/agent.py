"""
FidelinvestigatorAI - Agente Investigativo OSINT di Elite
==========================================================

Agente investigativo con background in intelligence (CIA, ROS, DIA, DCSA, DEA)
specializzato nell'analisi di report OSINT e nella produzione di
relazioni investigative professionali.

Questo modulo orchestra tutte le componenti dell'analisi:
- Parsing HTML report OSINT
- Analisi e correlazione dati
- Profilazione psicologica
- Analisi pattern password
- Valutazione sicurezza
- Generazione report PDF professionale
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from .html_parser import OSINTHTMLParser, ExtractedData
from .data_analyzer import DataAnalyzer, AnalysisReport
from .psychological_profiler import PsychologicalProfiler, PsychologicalProfile
from .password_analyzer import PasswordAnalyzer, PasswordProfile
from .security_assessor import SecurityAssessor, SecurityReport
from .report_generator import ReportGenerator


@dataclass
class InvestigationResult:
    """Risultato completo dell'investigazione"""
    target_name: str
    investigation_date: str
    extracted_data: Optional[ExtractedData] = None
    analysis_report: Optional[AnalysisReport] = None
    psychological_profile: Optional[PsychologicalProfile] = None
    password_profile: Optional[PasswordProfile] = None
    security_report: Optional[SecurityReport] = None
    pdf_report_path: Optional[str] = None
    summary: Dict[str, Any] = field(default_factory=dict)


class FidelinvestigatorAI:
    """
    FidelinvestigatorAI - Agente Investigativo OSINT di Elite

    Un agente investigativo avanzato con esperienza in:
    - CIA (Central Intelligence Agency)
    - ROS (Raggruppamento Operativo Speciale - Carabinieri)
    - DIA (Defense Intelligence Agency)
    - DCSA (Defense Counterintelligence and Security Agency)
    - DEA (Drug Enforcement Administration)

    Specializzato in:
    - Analisi e correlazione di dati OSINT
    - Profilazione psicologica basata su comportamento digitale
    - Analisi di pattern password e valutazione sicurezza
    - Produzione di report investigativi professionali

    Esempio d'uso:
    ```python
    from fidelinvestigator import FidelinvestigatorAI

    # Inizializza l'agente
    agent = FidelinvestigatorAI()

    # Opzionale: imposta il logo
    agent.set_logo("/path/to/logo.png")

    # Esegui l'investigazione da file HTML
    result = agent.investigate_from_file("/path/to/report.html")

    # Oppure da stringa HTML
    result = agent.investigate(html_content)

    # Il report PDF è generato automaticamente
    print(f"Report generato: {result.pdf_report_path}")
    ```
    """

    AGENT_NAME = "FidelinvestigatorAI"
    AGENT_VERSION = "1.0.0"
    AGENT_DESCRIPTION = "Agente Investigativo OSINT di Elite"

    def __init__(self,
                 output_dir: str = "./reports",
                 logo_path: str = None,
                 verbose: bool = True):
        """
        Inizializza l'agente investigativo.

        Args:
            output_dir: Directory per i report generati
            logo_path: Percorso del logo da inserire nel report
            verbose: Se True, stampa informazioni durante l'esecuzione
        """
        self.output_dir = output_dir
        self.logo_path = logo_path
        self.verbose = verbose

        # Crea directory output se non esiste
        os.makedirs(output_dir, exist_ok=True)

        # Stato interno
        self._current_investigation = None

        if self.verbose:
            self._print_banner()

    def _print_banner(self):
        """Stampa banner dell'agente"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ███████╗██╗██████╗ ███████╗██╗                              ║
║     ██╔════╝██║██╔══██╗██╔════╝██║                              ║
║     █████╗  ██║██║  ██║█████╗  ██║                              ║
║     ██╔══╝  ██║██║  ██║██╔══╝  ██║                              ║
║     ██║     ██║██████╔╝███████╗███████╗                         ║
║     ╚═╝     ╚═╝╚═════╝ ╚══════╝╚══════╝                         ║
║                                                                  ║
║     INVESTIGATOR AI                                              ║
║     ─────────────────────────────────────────────────────────   ║
║     Agente Investigativo OSINT di Elite                         ║
║     Background: CIA | ROS | DIA | DCSA | DEA                    ║
║     Version: 1.0.0                                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def set_logo(self, logo_path: str):
        """
        Imposta il logo per i report.

        Args:
            logo_path: Percorso del file immagine del logo
        """
        if os.path.exists(logo_path):
            self.logo_path = logo_path
            if self.verbose:
                print(f"[+] Logo impostato: {logo_path}")
        else:
            print(f"[!] Logo non trovato: {logo_path}")

    def investigate(self, html_content: str,
                    output_filename: str = None) -> InvestigationResult:
        """
        Esegue l'investigazione completa su un report HTML OSINT.

        Args:
            html_content: Contenuto HTML del report OSINT
            output_filename: Nome file PDF output (opzionale)

        Returns:
            InvestigationResult: Risultato completo dell'investigazione
        """
        result = InvestigationResult(
            target_name="Target",
            investigation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        try:
            # FASE 1: Parsing HTML
            if self.verbose:
                print("\n[*] FASE 1: Parsing report HTML...")

            parser = OSINTHTMLParser()
            extracted_data = parser.parse(html_content)
            result.extracted_data = extracted_data

            # Aggiorna nome target
            if extracted_data.personal_info.full_name:
                result.target_name = extracted_data.personal_info.full_name

            if self.verbose:
                summary = parser.get_summary()
                print(f"    [✓] Target identificato: {result.target_name}")
                print(f"    [✓] Email trovate: {summary['emails_found']}")
                print(f"    [✓] Profili social: {summary['social_profiles']}")
                print(f"    [✓] Data breach: {summary['breaches_found']}")
                print(f"    [✓] Password esposte: {summary['passwords_exposed']}")

            # FASE 2: Analisi e correlazione dati
            if self.verbose:
                print("\n[*] FASE 2: Analisi e correlazione dati...")

            data_analyzer = DataAnalyzer(extracted_data)
            analysis_report = data_analyzer.analyze()
            result.analysis_report = analysis_report

            if self.verbose:
                print(f"    [✓] Correlazioni identificate: {len(analysis_report.correlations)}")
                print(f"    [✓] Pattern di attività: {len(analysis_report.activity_patterns)}")
                print(f"    [✓] Indicatori di rischio: {len(analysis_report.risk_indicators)}")
                print(f"    [✓] Livello esposizione: {analysis_report.exposure_level}")

            # FASE 3: Profilazione psicologica
            if self.verbose:
                print("\n[*] FASE 3: Profilazione psicologica...")

            profiler = PsychologicalProfiler(extracted_data, analysis_report)
            psychological_profile = profiler.generate_profile()
            result.psychological_profile = psychological_profile

            if self.verbose:
                summary = profiler.get_profile_summary()
                print(f"    [✓] Tratti personalità: {summary['personality_traits']}")
                print(f"    [✓] Pattern comportamentali: {summary['behavioral_patterns']}")
                print(f"    [✓] Vulnerabilità: {summary['vulnerabilities']}")

            # FASE 4: Analisi password
            if self.verbose:
                print("\n[*] FASE 4: Analisi pattern password...")

            pwd_analyzer = PasswordAnalyzer(extracted_data)
            password_profile = pwd_analyzer.analyze()
            result.password_profile = password_profile

            if self.verbose:
                summary = pwd_analyzer.get_analysis_summary()
                print(f"    [✓] Password analizzate: {summary['passwords_analyzed']}")
                print(f"    [✓] Livello sicurezza: {summary['security_level']}")
                print(f"    [✓] Pattern identificati: {summary['patterns_found']}")

            # FASE 5: Valutazione sicurezza
            if self.verbose:
                print("\n[*] FASE 5: Valutazione sicurezza online...")

            security_assessor = SecurityAssessor(extracted_data, analysis_report, password_profile)
            security_report = security_assessor.assess()
            result.security_report = security_report

            if self.verbose:
                summary = security_assessor.get_executive_summary()
                print(f"    [✓] Security Grade: {summary['security_grade']}")
                print(f"    [✓] Security Score: {summary['security_score']:.0f}/100")
                print(f"    [✓] Privacy Score: {summary['privacy_score']:.0f}/100")
                print(f"    [✓] Vulnerabilità critiche: {summary['critical_vulnerabilities']}")

            # FASE 6: Generazione report PDF
            if self.verbose:
                print("\n[*] FASE 6: Generazione report PDF professionale...")

            # Genera nome file
            if output_filename is None:
                safe_name = result.target_name.replace(' ', '_')[:30]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"Report_Investigativo_{safe_name}_{timestamp}.pdf"

            output_path = os.path.join(self.output_dir, output_filename)

            report_gen = ReportGenerator(output_path)
            if self.logo_path:
                report_gen.set_logo(self.logo_path)

            pdf_path = report_gen.generate(
                extracted_data,
                analysis_report,
                psychological_profile,
                password_profile,
                security_report
            )

            result.pdf_report_path = pdf_path

            if self.verbose:
                print(f"    [✓] Report generato: {pdf_path}")

            # Genera sommario
            result.summary = self._generate_summary(result)

            if self.verbose:
                self._print_summary(result)

            return result

        except Exception as e:
            print(f"\n[!] ERRORE durante l'investigazione: {str(e)}")
            raise

    def investigate_from_file(self, file_path: str,
                              output_filename: str = None) -> InvestigationResult:
        """
        Esegue l'investigazione da un file HTML.

        Args:
            file_path: Percorso del file HTML da analizzare
            output_filename: Nome file PDF output (opzionale)

        Returns:
            InvestigationResult: Risultato completo dell'investigazione
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato: {file_path}")

        if self.verbose:
            print(f"\n[*] Caricamento report: {file_path}")

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        if self.verbose:
            print(f"    [✓] File caricato: {len(html_content)} bytes")

        return self.investigate(html_content, output_filename)

    def _generate_summary(self, result: InvestigationResult) -> Dict[str, Any]:
        """Genera sommario dell'investigazione"""
        summary = {
            'target': result.target_name,
            'date': result.investigation_date,
            'data_points': {
                'emails': len(result.extracted_data.contact_info.emails) if result.extracted_data else 0,
                'phones': len(result.extracted_data.contact_info.phones) if result.extracted_data else 0,
                'social_profiles': len(result.extracted_data.social_media) if result.extracted_data else 0,
                'usernames': len(result.extracted_data.usernames) if result.extracted_data else 0,
                'breaches': len(result.extracted_data.data_breaches) if result.extracted_data else 0,
                'passwords': len(result.extracted_data.raw_passwords) if result.extracted_data else 0,
            },
            'security': {
                'grade': result.security_report.security_posture.grade if result.security_report and result.security_report.security_posture else 'N/A',
                'score': result.security_report.security_posture.overall_score if result.security_report and result.security_report.security_posture else 0,
                'privacy_score': result.security_report.privacy_score if result.security_report else 0,
                'exposure_level': result.analysis_report.exposure_level if result.analysis_report else 'N/A',
            },
            'risk_indicators': len(result.analysis_report.risk_indicators) if result.analysis_report else 0,
            'vulnerabilities': len(result.security_report.vulnerabilities) if result.security_report else 0,
            'pdf_report': result.pdf_report_path
        }
        return summary

    def _print_summary(self, result: InvestigationResult):
        """Stampa il sommario finale"""
        print("\n" + "="*70)
        print("                    INVESTIGAZIONE COMPLETATA")
        print("="*70)

        summary = result.summary

        print(f"""
    TARGET: {summary['target']}
    DATA: {summary['date']}

    DATI RACCOLTI:
    ├── Email identificate:      {summary['data_points']['emails']}
    ├── Numeri telefono:         {summary['data_points']['phones']}
    ├── Profili social:          {summary['data_points']['social_profiles']}
    ├── Username:                {summary['data_points']['usernames']}
    ├── Data breach:             {summary['data_points']['breaches']}
    └── Password esposte:        {summary['data_points']['passwords']}

    VALUTAZIONE SICUREZZA:
    ├── Grade:                   {summary['security']['grade']}
    ├── Security Score:          {summary['security']['score']:.0f}/100
    ├── Privacy Score:           {summary['security']['privacy_score']:.0f}/100
    └── Livello Esposizione:     {summary['security']['exposure_level']}

    INDICATORI RISCHIO:          {summary['risk_indicators']}
    VULNERABILITÀ:               {summary['vulnerabilities']}

    REPORT PDF: {summary['pdf_report']}
        """)

        print("="*70)
        print("    FidelinvestigatorAI - Investigazione Conclusa")
        print("="*70 + "\n")

    def get_quick_analysis(self, html_content: str) -> Dict[str, Any]:
        """
        Esegue un'analisi rapida senza generare il report PDF.

        Args:
            html_content: Contenuto HTML del report OSINT

        Returns:
            Dict con i risultati principali dell'analisi
        """
        parser = OSINTHTMLParser()
        extracted_data = parser.parse(html_content)

        data_analyzer = DataAnalyzer(extracted_data)
        analysis_report = data_analyzer.analyze()

        return {
            'target': extracted_data.personal_info.full_name,
            'summary': parser.get_summary(),
            'exposure_level': analysis_report.exposure_level,
            'digital_footprint_score': analysis_report.digital_footprint_score,
            'key_findings': analysis_report.key_findings,
            'risk_indicators': [r.description for r in analysis_report.risk_indicators]
        }


def main():
    """Entry point per utilizzo da linea di comando"""
    import argparse

    parser = argparse.ArgumentParser(
        description='FidelinvestigatorAI - Agente Investigativo OSINT',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python -m fidelinvestigator report.html
  python -m fidelinvestigator report.html -o output.pdf
  python -m fidelinvestigator report.html --logo logo.png
        """
    )

    parser.add_argument('input', help='File HTML del report OSINT')
    parser.add_argument('-o', '--output', help='Nome file PDF output')
    parser.add_argument('--logo', help='Percorso del logo')
    parser.add_argument('-d', '--output-dir', default='./reports', help='Directory output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Modalità silenziosa')

    args = parser.parse_args()

    # Inizializza agente
    agent = FidelinvestigatorAI(
        output_dir=args.output_dir,
        logo_path=args.logo,
        verbose=not args.quiet
    )

    # Esegui investigazione
    result = agent.investigate_from_file(args.input, args.output)

    return result


if __name__ == "__main__":
    main()
