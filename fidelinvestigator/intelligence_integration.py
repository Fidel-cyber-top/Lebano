"""
Intelligence Report Integration Module
======================================

Integrazione tra FidelinvestigatorAI e il Dutch OSINT Guy Intelligence Report Framework.
Questo modulo converte i dati OSINT esistenti nel formato richiesto dal framework
di intelligence professionale.

Author: FidelinvestigatorAI
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json

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
    EstimativeLanguage
)

from .intelligence_report_docx import (
    IntelligenceReportDOCX,
    generate_intelligence_report_docx
)


class IntelligenceReportIntegration:
    """
    Integrazione tra dati OSINT e Intelligence Report Framework
    """

    def __init__(self, anthropic_api_key: str = None):
        """
        Inizializza l'integrazione

        Args:
            anthropic_api_key: API key per analisi Claude avanzata
        """
        self.anthropic_api_key = anthropic_api_key
        self.anthropic_client = None

        if anthropic_api_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
            except ImportError:
                print("[!] anthropic module not available")

    def create_intelligence_report(
        self,
        osint_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        psych_profile: Dict[str, Any],
        security_assessment: Dict[str, Any],
        subject_name: str = "Unknown Subject",
        classification: str = "SENSITIVE"
    ) -> IntelligenceReportGenerator:
        """
        Crea un Intelligence Report completo dai dati OSINT

        Args:
            osint_data: Dati estratti (emails, usernames, social_profiles, etc.)
            analysis_data: Risultati analisi (base_analysis, osint_verification, etc.)
            psych_profile: Profilo psicologico
            security_assessment: Valutazione sicurezza
            subject_name: Nome del soggetto
            classification: Classificazione del report

        Returns:
            IntelligenceReportGenerator configurato
        """
        # Crea report generator
        report = IntelligenceReportGenerator(
            report_title=f"Intelligence Assessment: {subject_name}",
            analyst_name="FidelinvestigatorAI OSINT Unit",
            classification=classification
        )

        # 1. Configura Introduction
        self._setup_introduction(report, osint_data, analysis_data)

        # 2. Configura Methodology
        self._setup_methodology(report)

        # 3. Aggiungi Sources
        sources = self._create_sources(osint_data)
        for source in sources:
            report.source_evaluator.add_source(source)

        # 4. Aggiungi Findings
        self._add_findings(report, osint_data, analysis_data, security_assessment, sources)

        # 5. Aggiungi Entities of Interest
        self._add_entities(report, osint_data, subject_name)

        # 6. Aggiungi Timeline
        self._add_timeline(report, osint_data, analysis_data)

        # 7. Configura ACH Analysis
        self._setup_ach_analysis(report, osint_data, analysis_data)

        # 8. Aggiungi Key Judgments
        self._add_key_judgments(report, analysis_data, security_assessment, psych_profile)

        # 9. Aggiungi Recommendations
        self._add_recommendations(report, security_assessment)

        # 10. Analisi narrativa (opzionale con Claude)
        if self.anthropic_client:
            narrative = self._generate_ai_analysis(osint_data, analysis_data, security_assessment)
            report.analysis = narrative

        return report

    def _setup_introduction(self, report: IntelligenceReportGenerator,
                           osint_data: Dict, analysis_data: Dict) -> None:
        """Configura la sezione Introduction"""
        base = analysis_data.get('base_analysis', {})
        data_summary = base.get('data_summary', {})

        purpose = (
            f"Condurre un'analisi approfondita della presenza digitale del target "
            f"per identificare vulnerabilità, esposizioni e rischi operativi. "
            f"L'assessment copre {data_summary.get('emails', 0)} email, "
            f"{data_summary.get('social_profiles', 0)} profili social, "
            f"e {data_summary.get('breaches', 0)} data breach identificati."
        )

        scope = (
            "L'analisi comprende: verifica identità digitale, mappatura presenza online, "
            "valutazione esposizione credenziali, analisi comportamentale, "
            "e assessment delle vulnerabilità. Le fonti utilizzate sono esclusivamente "
            "di tipo OSINT (Open Source Intelligence)."
        )

        limitations = [
            "Analisi limitata a fonti pubblicamente accessibili",
            "Possibili gap informativi per contenuti privati o protetti",
            "Verifica dipendente dalla disponibilità delle fonti al momento dell'analisi",
            "Possibili identificatori non correttamente attribuiti in caso di omonimia"
        ]

        report.set_introduction(purpose, scope, limitations)
        report.bluf_generator.set_timeframe(
            f"Analisi condotta il {datetime.now().strftime('%d/%m/%Y')}"
        )

    def _setup_methodology(self, report: IntelligenceReportGenerator) -> None:
        """Configura la sezione Methodology"""
        collection_methods = [
            "SOCMINT (Social Media Intelligence)",
            "Public Records Search",
            "Data Breach Database Analysis",
            "Digital Footprint Mapping",
            "Username/Email Correlation",
            "Behavioral Pattern Analysis"
        ]

        analysis_techniques = [
            "ACH (Analysis of Competing Hypotheses)",
            "Multi-Source Verification",
            "Link Analysis",
            "Timeline Reconstruction",
            "Behavioral Evidence Analysis",
            "Risk Quantification"
        ]

        tools_used = [
            "FidelinvestigatorAI Framework",
            "Perplexity AI (Real-time OSINT)",
            "OpenAI GPT-4 (Correlation Analysis)",
            "Anthropic Claude (Psychological Profiling)",
            "Custom HTML/Data Parsers"
        ]

        report.set_methodology(collection_methods, analysis_techniques, tools_used)

    def _create_sources(self, osint_data: Dict) -> List[Source]:
        """Crea le fonti dai dati OSINT"""
        sources = []

        # Social profiles as sources
        for profile in osint_data.get('social_profiles', []):
            platform = profile.get('platform', 'Unknown')
            source = Source(
                name=f"{platform} Profile",
                type="social_media_verified" if profile.get('verified') else "social_media",
                url=profile.get('url', ''),
                reliability=SourceReliability.C,
                accuracy=InformationAccuracy.TWO,
                independence=True,
                notes=f"Username: {profile.get('username', 'N/A')}"
            )
            sources.append(source)

        # Data breaches as sources
        for breach in osint_data.get('breaches', []):
            source = Source(
                name=f"Data Breach: {breach.get('source', 'Unknown')}",
                type="security_database",
                reliability=SourceReliability.B,
                accuracy=InformationAccuracy.ONE,
                independence=True,
                notes=f"Date: {breach.get('date', 'Unknown')}"
            )
            sources.append(source)

        # Add generic OSINT source
        sources.append(Source(
            name="Public Records Search",
            type="public_records",
            reliability=SourceReliability.B,
            accuracy=InformationAccuracy.TWO,
            independence=True
        ))

        return sources

    def _add_findings(self, report: IntelligenceReportGenerator,
                     osint_data: Dict, analysis_data: Dict,
                     security: Dict, sources: List[Source]) -> None:
        """Aggiunge i findings al report"""
        base = analysis_data.get('base_analysis', {})
        data_summary = base.get('data_summary', {})

        # Finding 1: Digital Footprint
        email_count = data_summary.get('emails', 0)
        social_count = data_summary.get('social_profiles', 0)

        if email_count > 0 or social_count > 0:
            confidence = ConfidenceLevel.HIGH if (email_count + social_count) > 3 else ConfidenceLevel.MODERATE
            report.add_finding(
                title="Presenza Digitale Confermata",
                description=(
                    f"Il target mantiene una presenza digitale attiva con "
                    f"{email_count} indirizzi email identificati e "
                    f"{social_count} profili social media confermati."
                ),
                evidence=[
                    f"{email_count} email addresses identificati",
                    f"{social_count} social media profiles trovati",
                    f"{len(osint_data.get('usernames', []))} username correlati"
                ],
                sources=sources[:3] if sources else [],
                confidence=confidence,
                category="digital_footprint"
            )

        # Finding 2: Credential Exposure
        breach_count = data_summary.get('breaches', 0)
        password_count = data_summary.get('passwords', 0)

        if breach_count > 0 or password_count > 0:
            severity = "CRITICA" if password_count > 0 else "ALTA"
            confidence = ConfidenceLevel.HIGH

            report.add_finding(
                title=f"Esposizione Credenziali - Severità {severity}",
                description=(
                    f"Identificata esposizione di credenziali in {breach_count} data breach "
                    f"con {password_count} password compromesse. "
                    f"Questo rappresenta un rischio significativo per la sicurezza degli account."
                ),
                evidence=[
                    f"Presente in {breach_count} data breach noti",
                    f"{password_count} password esposte in chiaro" if password_count > 0 else "Nessuna password in chiaro",
                    "Potenziale per credential stuffing attacks"
                ],
                sources=[s for s in sources if 'breach' in s.name.lower()][:3],
                confidence=confidence,
                category="credential_exposure"
            )

        # Finding 3: Security Vulnerabilities
        vulnerabilities = security.get('vulnerabilities', [])
        if vulnerabilities:
            critical_vulns = [v for v in vulnerabilities if v.get('severity') in ['CRITICA', 'ALTA']]

            report.add_finding(
                title="Vulnerabilità di Sicurezza Identificate",
                description=(
                    f"L'analisi ha identificato {len(vulnerabilities)} vulnerabilità, "
                    f"di cui {len(critical_vulns)} classificate come critiche o alte. "
                    f"Security Grade complessivo: {security.get('security_grade', 'N/A')}."
                ),
                evidence=[v.get('description', '') for v in vulnerabilities[:5]],
                sources=sources[:2] if sources else [],
                confidence=ConfidenceLevel.HIGH,
                category="security"
            )

        # Finding 4: Social Engineering Risk
        if social_count > 3:
            report.add_finding(
                title="Superficie di Attacco Social Engineering",
                description=(
                    f"L'ampia presenza su {social_count} piattaforme social aumenta "
                    f"significativamente la superficie di attacco per tecniche di "
                    f"social engineering e spear phishing."
                ),
                evidence=[
                    f"{social_count} profili social pubblicamente accessibili",
                    "Informazioni personali potenzialmente aggregabili",
                    "Pattern di comportamento analizzabili"
                ],
                sources=[s for s in sources if 'social' in s.type.lower()][:3],
                confidence=ConfidenceLevel.MODERATE,
                category="social_engineering"
            )

    def _add_entities(self, report: IntelligenceReportGenerator,
                     osint_data: Dict, subject_name: str) -> None:
        """Aggiunge le entità di interesse"""
        # Main target entity
        identifiers = {}
        if osint_data.get('emails'):
            identifiers['primary_email'] = osint_data['emails'][0]
        if osint_data.get('usernames'):
            identifiers['primary_username'] = osint_data['usernames'][0]

        relationships = []
        for profile in osint_data.get('social_profiles', []):
            relationships.append({
                'type': 'owns_account',
                'platform': profile.get('platform', 'Unknown'),
                'identifier': profile.get('username', 'Unknown')
            })

        target_entity = EntityOfInterest(
            name=subject_name,
            entity_type="person",
            identifiers=identifiers,
            relationships=relationships[:10],  # Limit to 10
            risk_level=self._determine_entity_risk(osint_data),
            notes="Target principale dell'investigazione OSINT"
        )
        report.add_entity(target_entity)

        # Add related accounts as entities
        for profile in osint_data.get('social_profiles', [])[:5]:
            account_entity = EntityOfInterest(
                name=f"{profile.get('platform', 'Unknown')} Account",
                entity_type="account",
                identifiers={
                    'platform': profile.get('platform', 'Unknown'),
                    'username': profile.get('username', 'Unknown'),
                    'url': profile.get('url', '')
                },
                risk_level="medium"
            )
            report.add_entity(account_entity)

    def _determine_entity_risk(self, osint_data: Dict) -> str:
        """Determina il livello di rischio dell'entità"""
        risk_score = 0

        if osint_data.get('passwords'):
            risk_score += 40
        if len(osint_data.get('breaches', [])) > 2:
            risk_score += 30
        if len(osint_data.get('social_profiles', [])) > 5:
            risk_score += 15
        if len(osint_data.get('emails', [])) > 3:
            risk_score += 15

        if risk_score >= 60:
            return "high"
        elif risk_score >= 30:
            return "medium"
        else:
            return "low"

    def _add_timeline(self, report: IntelligenceReportGenerator,
                     osint_data: Dict, analysis_data: Dict) -> None:
        """Aggiunge eventi alla timeline"""
        # Add breach events to timeline
        for breach in osint_data.get('breaches', []):
            breach_date = breach.get('date')
            if breach_date:
                try:
                    date = datetime.strptime(breach_date, '%Y-%m-%d')
                except (ValueError, TypeError):
                    try:
                        date = datetime.strptime(breach_date, '%Y')
                    except (ValueError, TypeError):
                        date = datetime.now()

                report.add_timeline_event(
                    date=date,
                    event=f"Data breach: {breach.get('source', 'Unknown')}",
                    significance="high"
                )

        # Add current analysis event
        report.add_timeline_event(
            date=datetime.now(),
            event="Analisi OSINT condotta da FidelinvestigatorAI",
            significance="medium"
        )

    def _setup_ach_analysis(self, report: IntelligenceReportGenerator,
                           osint_data: Dict, analysis_data: Dict) -> None:
        """Configura l'Analysis of Competing Hypotheses"""
        base = analysis_data.get('base_analysis', {})

        # Hypothesis 1: Target is security-conscious
        h1 = Hypothesis(
            id="H1",
            description="Il target è consapevole della sicurezza e gestisce attivamente la propria privacy online"
        )

        # Hypothesis 2: Target has poor security hygiene
        h2 = Hypothesis(
            id="H2",
            description="Il target ha una scarsa igiene digitale e non gestisce adeguatamente la propria esposizione"
        )

        # Hypothesis 3: Target is partially aware
        h3 = Hypothesis(
            id="H3",
            description="Il target ha una consapevolezza parziale e incoerente della sicurezza digitale"
        )

        # Add hypotheses
        report.add_hypothesis(h1)
        report.add_hypothesis(h2)
        report.add_hypothesis(h3)

        # Add evidence and evaluate
        ach = report.ach_analyzer

        # Evidence: Number of breaches
        breach_count = base.get('data_summary', {}).get('breaches', 0)
        ach.add_evidence("E1", f"Target presente in {breach_count} data breach")
        if breach_count > 2:
            ach.evaluate_evidence_against_hypothesis("E1", "H1", "-")
            ach.evaluate_evidence_against_hypothesis("E1", "H2", "+")
            ach.evaluate_evidence_against_hypothesis("E1", "H3", "+")
        elif breach_count > 0:
            ach.evaluate_evidence_against_hypothesis("E1", "H1", "N")
            ach.evaluate_evidence_against_hypothesis("E1", "H2", "+")
            ach.evaluate_evidence_against_hypothesis("E1", "H3", "+")
        else:
            ach.evaluate_evidence_against_hypothesis("E1", "H1", "+")
            ach.evaluate_evidence_against_hypothesis("E1", "H2", "-")
            ach.evaluate_evidence_against_hypothesis("E1", "H3", "N")

        # Evidence: Exposed passwords
        password_count = base.get('data_summary', {}).get('passwords', 0)
        ach.add_evidence("E2", f"{password_count} password esposte")
        if password_count > 0:
            ach.evaluate_evidence_against_hypothesis("E2", "H1", "-")
            ach.evaluate_evidence_against_hypothesis("E2", "H2", "+")
            ach.evaluate_evidence_against_hypothesis("E2", "H3", "N")
        else:
            ach.evaluate_evidence_against_hypothesis("E2", "H1", "+")
            ach.evaluate_evidence_against_hypothesis("E2", "H2", "-")
            ach.evaluate_evidence_against_hypothesis("E2", "H3", "N")

        # Evidence: Social profiles count
        social_count = base.get('data_summary', {}).get('social_profiles', 0)
        ach.add_evidence("E3", f"{social_count} profili social identificati")
        if social_count > 5:
            ach.evaluate_evidence_against_hypothesis("E3", "H1", "-")
            ach.evaluate_evidence_against_hypothesis("E3", "H2", "+")
            ach.evaluate_evidence_against_hypothesis("E3", "H3", "+")
        else:
            ach.evaluate_evidence_against_hypothesis("E3", "H1", "N")
            ach.evaluate_evidence_against_hypothesis("E3", "H2", "N")
            ach.evaluate_evidence_against_hypothesis("E3", "H3", "N")

    def _add_key_judgments(self, report: IntelligenceReportGenerator,
                          analysis_data: Dict, security: Dict,
                          psych_profile: Dict) -> None:
        """Aggiunge i Key Judgments"""
        base = analysis_data.get('base_analysis', {})
        exposure_level = base.get('exposure_level', 'UNKNOWN')

        # Key Judgment 1: Overall Risk Assessment
        if exposure_level in ['CRITICO', 'ALTO']:
            confidence = ConfidenceLevel.HIGH
            statement = (
                f"Il target presenta un livello di esposizione {exposure_level} "
                f"con Security Grade {security.get('security_grade', 'N/A')}. "
                f"Le credenziali compromesse e l'ampia presenza digitale "
                f"creano una superficie di attacco significativa."
            )
        elif exposure_level == 'MODERATO':
            confidence = ConfidenceLevel.MODERATE
            statement = (
                f"Il target presenta un livello di esposizione MODERATO. "
                f"Sono state identificate alcune vulnerabilità che richiedono "
                f"azioni correttive ma il rischio complessivo è gestibile."
            )
        else:
            confidence = ConfidenceLevel.LOW
            statement = (
                f"Il target presenta un livello di esposizione {exposure_level}. "
                f"La presenza digitale è limitata e le vulnerabilità identificate "
                f"sono minime."
            )

        kj1 = KeyJudgment(
            statement=statement,
            confidence=confidence,
            supporting_evidence=base.get('risk_factors', []),
            caveats=["Basato su fonti OSINT pubblicamente accessibili"]
        )
        report.add_key_judgment(kj1)

        # Key Judgment 2: Immediate Threats
        threats = security.get('threats', [])
        if threats:
            kj2 = KeyJudgment(
                statement=(
                    f"Identificate {len(threats)} minacce potenziali attive, "
                    f"inclusi: {', '.join(threats[:3])}. "
                    f"È necessaria un'azione immediata per mitigare questi rischi."
                ),
                confidence=ConfidenceLevel.HIGH,
                supporting_evidence=[f"Minaccia: {t}" for t in threats],
                caveats=["Alcune minacce potrebbero essere già state sfruttate"]
            )
            report.add_key_judgment(kj2)

        # Key Judgment 3: Behavioral Assessment
        if psych_profile.get('ai_profile'):
            kj3 = KeyJudgment(
                statement=(
                    "L'analisi comportamentale indica pattern specifici di "
                    "presenza digitale che potrebbero essere sfruttati per "
                    "social engineering mirato."
                ),
                confidence=ConfidenceLevel.MODERATE,
                supporting_evidence=["Profilo comportamentale AI disponibile"],
                caveats=["Analisi basata su dati comportamentali limitati"]
            )
            report.add_key_judgment(kj3)

    def _add_recommendations(self, report: IntelligenceReportGenerator,
                            security: Dict) -> None:
        """Aggiunge le raccomandazioni"""
        # From security assessment
        for rec in security.get('recommendations', []):
            priority = "high" if "URGENTE" in rec or "immediatamente" in rec.lower() else "medium"
            report.add_recommendation(rec, priority)

        # Standard recommendations
        standard_recs = [
            ("Implementare autenticazione multi-fattore su tutti gli account critici", "high"),
            ("Condurre reset completo delle credenziali compromesse", "high"),
            ("Attivare monitoring per attività sospette sugli account identificati", "medium"),
            ("Implementare policy di password management aziendale", "medium"),
            ("Condurre training awareness su social engineering", "low")
        ]

        for rec, priority in standard_recs:
            report.add_recommendation(rec, priority)

    def _generate_ai_analysis(self, osint_data: Dict,
                             analysis_data: Dict, security: Dict) -> str:
        """Genera analisi narrativa con Claude AI"""
        if not self.anthropic_client:
            return ""

        system_prompt = """Sei un Senior Intelligence Analyst specializzato in OSINT.
        Genera un'analisi narrativa professionale dei dati forniti seguendo gli standard
        della comunità intelligence (ICD 203). Usa linguaggio formale e preciso."""

        data_summary = json.dumps({
            'emails': len(osint_data.get('emails', [])),
            'usernames': len(osint_data.get('usernames', [])),
            'social_profiles': len(osint_data.get('social_profiles', [])),
            'breaches': len(osint_data.get('breaches', [])),
            'passwords_exposed': len(osint_data.get('passwords', [])),
            'exposure_level': analysis_data.get('base_analysis', {}).get('exposure_level', 'N/A'),
            'security_grade': security.get('security_grade', 'N/A'),
            'threats': security.get('threats', [])
        }, indent=2)

        prompt = f"""Basandoti sui seguenti dati OSINT, genera una narrativa analitica
        professionale (3-4 paragrafi) che descriva:
        1. La presenza digitale del target
        2. Le vulnerabilità identificate
        3. Le implicazioni per la sicurezza
        4. Una valutazione del rischio complessivo

        DATI:
        {data_summary}

        Scrivi in italiano formale, stile intelligence brief."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"[!] Errore generazione analisi AI: {e}")
            return ""

    def generate_full_intelligence_report(
        self,
        osint_data: Dict[str, Any],
        analysis_data: Dict[str, Any],
        psych_profile: Dict[str, Any],
        security_assessment: Dict[str, Any],
        subject_name: str,
        output_path: str,
        format: str = "docx"
    ) -> str:
        """
        Genera il report intelligence completo

        Args:
            osint_data: Dati OSINT estratti
            analysis_data: Risultati analisi
            psych_profile: Profilo psicologico
            security_assessment: Valutazione sicurezza
            subject_name: Nome del soggetto
            output_path: Percorso file output
            format: Formato output ('docx', 'json', 'txt')

        Returns:
            Percorso del file generato
        """
        # Crea report
        report = self.create_intelligence_report(
            osint_data=osint_data,
            analysis_data=analysis_data,
            psych_profile=psych_profile,
            security_assessment=security_assessment,
            subject_name=subject_name
        )

        # Genera output
        if format == "docx":
            return generate_intelligence_report_docx(report, output_path)
        elif format == "json":
            report.export_to_json(output_path)
            return output_path
        elif format == "txt":
            report.export_to_text(output_path)
            return output_path
        else:
            raise ValueError(f"Formato non supportato: {format}")


def generate_dutch_osint_report(
    osint_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
    psych_profile: Dict[str, Any],
    security_assessment: Dict[str, Any],
    subject_name: str,
    output_path: str,
    anthropic_api_key: str = None,
    format: str = "docx"
) -> str:
    """
    Funzione utility per generare report Dutch OSINT Guy style

    Args:
        osint_data: Dati estratti
        analysis_data: Analisi dati
        psych_profile: Profilo psicologico
        security_assessment: Valutazione sicurezza
        subject_name: Nome soggetto
        output_path: Percorso output
        anthropic_api_key: API key Claude (opzionale)
        format: Formato output

    Returns:
        Percorso file generato
    """
    integration = IntelligenceReportIntegration(anthropic_api_key)

    return integration.generate_full_intelligence_report(
        osint_data=osint_data,
        analysis_data=analysis_data,
        psych_profile=psych_profile,
        security_assessment=security_assessment,
        subject_name=subject_name,
        output_path=output_path,
        format=format
    )
