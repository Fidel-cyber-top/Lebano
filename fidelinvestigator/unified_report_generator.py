"""
Unified Intelligence Report Generator
======================================

Genera un UNICO report intelligence professionale in multipli formati:
- DOCX (Microsoft Word)
- PDF (ReportLab)
- HTML (Web-ready)

Basato su Dutch OSINT Guy Methodology con sezione Psychological Profile integrata.

Author: FidelinvestigatorAI
Version: 2.0.0
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import os
import html as html_escape

# DOCX imports
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# PDF imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor, black, white

# Import framework components
from .intelligence_report_framework import (
    ConfidenceLevel,
    SourceReliability,
    InformationAccuracy,
    Source,
    KeyJudgment,
    EntityOfInterest,
    Hypothesis,
    ACHAnalyzer,
    EstimativeLanguage
)


@dataclass
class PsychologicalProfile:
    """Profilo psicologico completo del target"""

    # Big Five (OCEAN)
    openness: int = 50
    conscientiousness: int = 50
    extraversion: int = 50
    agreeableness: int = 50
    neuroticism: int = 50

    # Dark Triad
    narcissism: int = 0
    machiavellianism: int = 0
    psychopathy: int = 0

    # Behavioral patterns
    communication_style: str = ""
    decision_making: str = ""
    risk_tolerance: str = ""

    # Vulnerabilities
    psychological_vulnerabilities: List[str] = field(default_factory=list)
    social_engineering_susceptibility: str = "medium"

    # AI Analysis
    ai_analysis: str = ""
    behavioral_summary: str = ""

    # Threat assessment
    threat_level: str = "LOW"
    predictability_score: int = 5

    def to_dict(self) -> Dict:
        return {
            "big_five": {
                "openness": self.openness,
                "conscientiousness": self.conscientiousness,
                "extraversion": self.extraversion,
                "agreeableness": self.agreeableness,
                "neuroticism": self.neuroticism
            },
            "dark_triad": {
                "narcissism": self.narcissism,
                "machiavellianism": self.machiavellianism,
                "psychopathy": self.psychopathy
            },
            "behavioral": {
                "communication_style": self.communication_style,
                "decision_making": self.decision_making,
                "risk_tolerance": self.risk_tolerance
            },
            "vulnerabilities": self.psychological_vulnerabilities,
            "social_engineering_susceptibility": self.social_engineering_susceptibility,
            "ai_analysis": self.ai_analysis,
            "behavioral_summary": self.behavioral_summary,
            "threat_level": self.threat_level,
            "predictability_score": self.predictability_score
        }


@dataclass
class UnifiedReportData:
    """Dati unificati per il report"""

    # Metadata
    report_title: str = "Intelligence Assessment Report"
    subject_name: str = "Unknown Subject"
    analyst_name: str = "FidelinvestigatorAI"
    classification: str = "SENSITIVE"
    report_date: datetime = field(default_factory=datetime.now)

    # OSINT Data
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    social_profiles: List[Dict] = field(default_factory=list)
    data_breaches: List[Dict] = field(default_factory=list)
    passwords_exposed: int = 0
    ip_addresses: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)

    # Analysis Results
    digital_footprint_score: int = 0
    exposure_level: str = "UNKNOWN"
    security_grade: str = "N/A"
    security_score: int = 0

    # Findings
    findings: List[Dict] = field(default_factory=list)

    # Key Judgments
    key_judgments: List[Dict] = field(default_factory=list)

    # Vulnerabilities & Threats
    vulnerabilities: List[Dict] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)

    # Recommendations
    recommendations: List[Dict] = field(default_factory=list)

    # Sources
    sources: List[Dict] = field(default_factory=list)

    # Psychological Profile
    psychological_profile: PsychologicalProfile = field(default_factory=PsychologicalProfile)

    # Timeline
    timeline_events: List[Dict] = field(default_factory=list)

    # Entities
    entities: List[Dict] = field(default_factory=list)

    # ACH Analysis
    hypotheses: List[Dict] = field(default_factory=list)

    # AI Narratives
    executive_summary: str = ""
    detailed_analysis: str = ""
    conclusions: str = ""


class UnifiedReportGenerator:
    """
    Generatore di report unificato multi-formato
    """

    # Colori corporate
    COLORS = {
        'primary': '#003366',
        'secondary': '#336699',
        'accent': '#C00000',
        'success': '#008000',
        'warning': '#FF9900',
        'light': '#F0F0F0',
        'dark': '#333333',
        'high': '#008000',
        'moderate': '#FF9900',
        'low': '#C00000'
    }

    def __init__(self, data: UnifiedReportData):
        """
        Inizializza il generatore

        Args:
            data: UnifiedReportData con tutti i dati del report
        """
        self.data = data
        self.report_id = self._generate_report_id()

    def _generate_report_id(self) -> str:
        """Genera ID univoco"""
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"{self.data.subject_name}{timestamp}".encode()
        short_hash = hashlib.md5(hash_input).hexdigest()[:8].upper()
        return f"INTEL-{timestamp}-{short_hash}"

    # =========================================================================
    # GENERAZIONE HTML
    # =========================================================================

    def generate_html(self, output_path: str) -> str:
        """Genera report in formato HTML"""

        html_content = self._build_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _build_html(self) -> str:
        """Costruisce il contenuto HTML"""

        css = self._get_css_styles()

        html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_escape.escape(self.data.report_title)}</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        {self._html_cover_page()}
        {self._html_bluf_section()}
        {self._html_toc()}
        {self._html_introduction()}
        {self._html_methodology()}
        {self._html_findings()}
        {self._html_psychological_profile()}
        {self._html_timeline()}
        {self._html_entities()}
        {self._html_analysis()}
        {self._html_assessment()}
        {self._html_recommendations()}
        {self._html_sources()}
        {self._html_footer()}
    </div>
</body>
</html>"""

        return html

    def _get_css_styles(self) -> str:
        """CSS styles per HTML"""
        return """
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }

        /* Cover Page */
        .cover-page {
            background: linear-gradient(135deg, #003366 0%, #336699 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            page-break-after: always;
        }
        .cover-page h1 { font-size: 2.5em; margin-bottom: 20px; }
        .cover-page .classification {
            background: #C00000;
            display: inline-block;
            padding: 5px 20px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        .cover-page .metadata { margin-top: 40px; text-align: left; }
        .cover-page .metadata p { margin: 10px 0; opacity: 0.9; }

        /* BLUF Section */
        .bluf-section {
            background: #E6F2FF;
            border-left: 5px solid #003366;
            padding: 30px;
            margin: 20px;
            page-break-after: always;
        }
        .bluf-section h2 { color: #003366; margin-bottom: 20px; }
        .key-judgment {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #003366;
        }
        .confidence-high { border-left-color: #008000; }
        .confidence-moderate { border-left-color: #FF9900; }
        .confidence-low { border-left-color: #C00000; }
        .confidence-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }
        .badge-high { background: #008000; color: white; }
        .badge-moderate { background: #FF9900; color: white; }
        .badge-low { background: #C00000; color: white; }

        /* Sections */
        .section {
            padding: 30px 40px;
            border-bottom: 1px solid #eee;
        }
        .section h2 {
            color: #003366;
            border-bottom: 2px solid #003366;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .section h3 {
            color: #336699;
            margin: 20px 0 10px 0;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background: #003366;
            color: white;
        }
        tr:nth-child(even) { background: #f9f9f9; }

        /* Findings */
        .finding {
            background: #f9f9f9;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #003366;
        }
        .finding-title {
            font-weight: bold;
            color: #003366;
            font-size: 1.1em;
        }

        /* Psychological Profile */
        .psych-profile {
            background: #FFF8E6;
            padding: 30px;
            margin: 20px 0;
            border-radius: 10px;
        }
        .big-five-chart {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
        }
        .trait-bar {
            flex: 1;
            min-width: 150px;
            background: #eee;
            border-radius: 5px;
            overflow: hidden;
        }
        .trait-bar .label {
            padding: 5px 10px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .trait-bar .bar {
            height: 20px;
            background: linear-gradient(90deg, #003366, #336699);
            transition: width 0.5s;
        }
        .trait-bar .value {
            text-align: right;
            padding: 5px 10px;
            font-size: 0.8em;
        }

        /* Dark Triad */
        .dark-triad {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }
        .dark-triad-item {
            flex: 1;
            text-align: center;
            padding: 15px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .dark-triad-item .score {
            font-size: 2em;
            font-weight: bold;
        }
        .score-low { color: #008000; }
        .score-medium { color: #FF9900; }
        .score-high { color: #C00000; }

        /* Recommendations */
        .recommendation {
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            display: flex;
            align-items: center;
        }
        .rec-high { background: #FFE6E6; border-left: 4px solid #C00000; }
        .rec-medium { background: #FFF3E6; border-left: 4px solid #FF9900; }
        .rec-low { background: #E6FFE6; border-left: 4px solid #008000; }
        .rec-priority {
            font-weight: bold;
            margin-right: 15px;
            min-width: 80px;
        }

        /* Footer */
        .footer {
            background: #003366;
            color: white;
            padding: 30px;
            text-align: center;
        }

        /* Print styles */
        @media print {
            .container { box-shadow: none; }
            .section { page-break-inside: avoid; }
        }
        """

    def _html_cover_page(self) -> str:
        """Genera cover page HTML"""
        return f"""
        <div class="cover-page">
            <div class="classification">// {self.data.classification} //</div>
            <h1>INTELLIGENCE REPORT</h1>
            <h2>{html_escape.escape(self.data.report_title)}</h2>
            <p style="font-size: 1.2em; margin-top: 30px;">Subject: {html_escape.escape(self.data.subject_name)}</p>
            <div class="metadata">
                <p><strong>Report ID:</strong> {self.report_id}</p>
                <p><strong>Date:</strong> {self.data.report_date.strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Analyst:</strong> {html_escape.escape(self.data.analyst_name)}</p>
                <p><strong>Framework:</strong> Dutch OSINT Guy Methodology</p>
            </div>
        </div>
        """

    def _html_bluf_section(self) -> str:
        """Genera BLUF section HTML"""
        judgments_html = ""
        for kj in self.data.key_judgments:
            conf = kj.get('confidence', 'MODERATE')
            conf_class = f"confidence-{conf.lower()}"
            badge_class = f"badge-{conf.lower()}"

            judgments_html += f"""
            <div class="key-judgment {conf_class}">
                <span class="confidence-badge {badge_class}">{conf}</span>
                {html_escape.escape(kj.get('statement', ''))}
            </div>
            """

        return f"""
        <div class="bluf-section">
            <h2>BOTTOM LINE UP FRONT (BLUF)</h2>
            <p><strong>Security Grade:</strong> {self.data.security_grade} |
               <strong>Risk Level:</strong> {self.data.exposure_level} |
               <strong>Digital Footprint:</strong> {self.data.digital_footprint_score}/100</p>

            <h3>Key Judgments</h3>
            {judgments_html if judgments_html else '<p>No key judgments defined.</p>'}
        </div>
        """

    def _html_toc(self) -> str:
        """Genera Table of Contents HTML"""
        return """
        <div class="section">
            <h2>Table of Contents</h2>
            <ol style="padding-left: 30px;">
                <li>Introduction</li>
                <li>Methodology</li>
                <li>Findings</li>
                <li>Psychological Profile</li>
                <li>Timeline</li>
                <li>Entities of Interest</li>
                <li>Analysis</li>
                <li>Assessment</li>
                <li>Recommendations</li>
                <li>Source Evaluation</li>
            </ol>
        </div>
        """

    def _html_introduction(self) -> str:
        """Genera Introduction HTML"""
        return f"""
        <div class="section">
            <h2>1. Introduction</h2>

            <h3>Purpose</h3>
            <p>Condurre un'analisi approfondita della presenza digitale del target per identificare
            vulnerabilità, esposizioni e rischi operativi. L'assessment copre {len(self.data.emails)} email,
            {len(self.data.social_profiles)} profili social, e {len(self.data.data_breaches)} data breach identificati.</p>

            <h3>Scope</h3>
            <p>L'analisi comprende: verifica identità digitale, mappatura presenza online,
            valutazione esposizione credenziali, analisi comportamentale/psicologica,
            e assessment delle vulnerabilità.</p>

            <h3>Subject Overview</h3>
            <table>
                <tr><th>Attribute</th><th>Value</th></tr>
                <tr><td>Subject</td><td>{html_escape.escape(self.data.subject_name)}</td></tr>
                <tr><td>Emails Identified</td><td>{len(self.data.emails)}</td></tr>
                <tr><td>Social Profiles</td><td>{len(self.data.social_profiles)}</td></tr>
                <tr><td>Data Breaches</td><td>{len(self.data.data_breaches)}</td></tr>
                <tr><td>Passwords Exposed</td><td>{self.data.passwords_exposed}</td></tr>
            </table>
        </div>
        """

    def _html_methodology(self) -> str:
        """Genera Methodology HTML"""
        return """
        <div class="section">
            <h2>2. Methodology</h2>

            <h3>Collection Methods</h3>
            <ul>
                <li>SOCMINT (Social Media Intelligence)</li>
                <li>Public Records Search</li>
                <li>Data Breach Database Analysis</li>
                <li>Digital Footprint Mapping</li>
                <li>Behavioral Pattern Analysis</li>
            </ul>

            <h3>Analysis Techniques</h3>
            <ul>
                <li>ACH (Analysis of Competing Hypotheses)</li>
                <li>Multi-Source Verification</li>
                <li>Link Analysis</li>
                <li>Psychological Profiling (Big Five, Dark Triad)</li>
                <li>Risk Quantification</li>
            </ul>

            <h3>Intelligence Cycle (CIA/NATO)</h3>
            <ol>
                <li><strong>PLANNING:</strong> Definizione requisiti informativi</li>
                <li><strong>COLLECTION:</strong> Raccolta dati OSINT</li>
                <li><strong>PROCESSING:</strong> Organizzazione e validazione</li>
                <li><strong>ANALYSIS:</strong> Analisi e produzione intelligence</li>
                <li><strong>DISSEMINATION:</strong> Distribuzione report</li>
            </ol>
        </div>
        """

    def _html_findings(self) -> str:
        """Genera Findings HTML"""
        findings_html = ""
        for i, finding in enumerate(self.data.findings, 1):
            conf = finding.get('confidence', 'MODERATE')
            findings_html += f"""
            <div class="finding">
                <div class="finding-title">[F-{i:03d}] {html_escape.escape(finding.get('title', ''))}</div>
                <p><strong>Confidence:</strong> {conf} | <strong>Category:</strong> {finding.get('category', 'general')}</p>
                <p>{html_escape.escape(finding.get('description', ''))}</p>
            </div>
            """

        return f"""
        <div class="section">
            <h2>3. Findings</h2>
            {findings_html if findings_html else '<p>No findings recorded.</p>'}

            <h3>Identified Data</h3>
            <table>
                <tr><th>Type</th><th>Data</th></tr>
                <tr><td>Emails</td><td>{', '.join(self.data.emails[:5]) if self.data.emails else 'None'}</td></tr>
                <tr><td>Usernames</td><td>{', '.join(self.data.usernames[:5]) if self.data.usernames else 'None'}</td></tr>
                <tr><td>Locations</td><td>{', '.join(self.data.locations[:3]) if self.data.locations else 'None'}</td></tr>
            </table>
        </div>
        """

    def _html_psychological_profile(self) -> str:
        """Genera Psychological Profile HTML"""
        pp = self.data.psychological_profile

        # Big Five bars
        big_five_html = ""
        traits = [
            ("Openness", pp.openness),
            ("Conscientiousness", pp.conscientiousness),
            ("Extraversion", pp.extraversion),
            ("Agreeableness", pp.agreeableness),
            ("Neuroticism", pp.neuroticism)
        ]
        for trait, value in traits:
            big_five_html += f"""
            <div class="trait-bar">
                <div class="label">{trait}</div>
                <div class="bar" style="width: {value}%;"></div>
                <div class="value">{value}/100</div>
            </div>
            """

        # Dark Triad
        def get_score_class(score):
            if score < 30: return "score-low"
            elif score < 60: return "score-medium"
            else: return "score-high"

        dark_triad_html = f"""
        <div class="dark-triad">
            <div class="dark-triad-item">
                <div class="score {get_score_class(pp.narcissism)}">{pp.narcissism}</div>
                <div>Narcissism</div>
            </div>
            <div class="dark-triad-item">
                <div class="score {get_score_class(pp.machiavellianism)}">{pp.machiavellianism}</div>
                <div>Machiavellianism</div>
            </div>
            <div class="dark-triad-item">
                <div class="score {get_score_class(pp.psychopathy)}">{pp.psychopathy}</div>
                <div>Psychopathy</div>
            </div>
        </div>
        """

        # Vulnerabilities
        vulns_html = ""
        for vuln in pp.psychological_vulnerabilities:
            vulns_html += f"<li>{html_escape.escape(vuln)}</li>"

        return f"""
        <div class="section">
            <h2>4. Psychological Profile</h2>

            <div class="psych-profile">
                <h3>Big Five Personality Model (OCEAN)</h3>
                <p>Valutazione dei tratti di personalità basata su indicatori comportamentali digitali.</p>
                <div class="big-five-chart">
                    {big_five_html}
                </div>

                <h3>Dark Triad Screening</h3>
                <p>Valutazione preliminare dei tratti Dark Triad (subclinici). Score &lt;30 = Basso, 30-60 = Medio, &gt;60 = Elevato.</p>
                {dark_triad_html}

                <h3>Behavioral Assessment</h3>
                <table>
                    <tr><td><strong>Communication Style</strong></td><td>{pp.communication_style or 'Non determinato'}</td></tr>
                    <tr><td><strong>Decision Making</strong></td><td>{pp.decision_making or 'Non determinato'}</td></tr>
                    <tr><td><strong>Risk Tolerance</strong></td><td>{pp.risk_tolerance or 'Non determinato'}</td></tr>
                    <tr><td><strong>Threat Level</strong></td><td>{pp.threat_level}</td></tr>
                    <tr><td><strong>Predictability Score</strong></td><td>{pp.predictability_score}/10</td></tr>
                </table>

                <h3>Social Engineering Susceptibility</h3>
                <p><strong>Level:</strong> {pp.social_engineering_susceptibility.upper()}</p>

                <h3>Psychological Vulnerabilities</h3>
                <ul>{vulns_html if vulns_html else '<li>Nessuna vulnerabilità significativa identificata</li>'}</ul>

                {f'<h3>AI Behavioral Analysis</h3><p>{html_escape.escape(pp.ai_analysis)}</p>' if pp.ai_analysis else ''}
            </div>
        </div>
        """

    def _html_timeline(self) -> str:
        """Genera Timeline HTML"""
        timeline_html = ""
        for event in self.data.timeline_events:
            timeline_html += f"""
            <tr>
                <td>{event.get('date', 'N/A')}</td>
                <td>{html_escape.escape(event.get('event', ''))}</td>
                <td>{event.get('significance', 'medium').upper()}</td>
            </tr>
            """

        return f"""
        <div class="section">
            <h2>5. Timeline</h2>
            <table>
                <tr><th>Date</th><th>Event</th><th>Significance</th></tr>
                {timeline_html if timeline_html else '<tr><td colspan="3">No timeline events recorded.</td></tr>'}
            </table>
        </div>
        """

    def _html_entities(self) -> str:
        """Genera Entities HTML"""
        entities_html = ""
        for entity in self.data.entities:
            entities_html += f"""
            <tr>
                <td>{html_escape.escape(entity.get('name', ''))}</td>
                <td>{entity.get('entity_type', 'unknown')}</td>
                <td>{entity.get('risk_level', 'unknown').upper()}</td>
            </tr>
            """

        return f"""
        <div class="section">
            <h2>6. Entities of Interest</h2>
            <table>
                <tr><th>Name</th><th>Type</th><th>Risk Level</th></tr>
                {entities_html if entities_html else '<tr><td colspan="3">No entities identified.</td></tr>'}
            </table>
        </div>
        """

    def _html_analysis(self) -> str:
        """Genera Analysis HTML"""
        hypotheses_html = ""
        for h in self.data.hypotheses:
            hypotheses_html += f"""
            <tr>
                <td>{h.get('id', 'H?')}</td>
                <td>{html_escape.escape(h.get('description', ''))}</td>
                <td>{h.get('probability', 0)*100:.1f}%</td>
            </tr>
            """

        return f"""
        <div class="section">
            <h2>7. Analysis</h2>

            {f'<p>{html_escape.escape(self.data.detailed_analysis)}</p>' if self.data.detailed_analysis else ''}

            <h3>Analysis of Competing Hypotheses (ACH)</h3>
            <p>Tecnica analitica CIA per valutare ipotesi alternative minimizzando i bias cognitivi.</p>
            <table>
                <tr><th>ID</th><th>Hypothesis</th><th>Probability</th></tr>
                {hypotheses_html if hypotheses_html else '<tr><td colspan="3">No hypotheses defined.</td></tr>'}
            </table>
        </div>
        """

    def _html_assessment(self) -> str:
        """Genera Assessment HTML"""
        vulns_html = ""
        for vuln in self.data.vulnerabilities:
            vulns_html += f"""
            <tr>
                <td>{vuln.get('type', 'N/A')}</td>
                <td>{vuln.get('severity', 'N/A')}</td>
                <td>{html_escape.escape(vuln.get('description', ''))}</td>
            </tr>
            """

        threats_html = "".join(f"<li>{html_escape.escape(t)}</li>" for t in self.data.threats)

        return f"""
        <div class="section">
            <h2>8. Assessment</h2>

            <h3>Security Metrics</h3>
            <table>
                <tr><td><strong>Security Score</strong></td><td>{self.data.security_score}/100</td></tr>
                <tr><td><strong>Security Grade</strong></td><td>{self.data.security_grade}</td></tr>
                <tr><td><strong>Exposure Level</strong></td><td>{self.data.exposure_level}</td></tr>
                <tr><td><strong>Digital Footprint</strong></td><td>{self.data.digital_footprint_score}/100</td></tr>
            </table>

            <h3>Vulnerabilities</h3>
            <table>
                <tr><th>Type</th><th>Severity</th><th>Description</th></tr>
                {vulns_html if vulns_html else '<tr><td colspan="3">No vulnerabilities identified.</td></tr>'}
            </table>

            <h3>Active Threats</h3>
            <ul>{threats_html if threats_html else '<li>No active threats identified.</li>'}</ul>
        </div>
        """

    def _html_recommendations(self) -> str:
        """Genera Recommendations HTML"""
        recs_html = ""
        for rec in self.data.recommendations:
            priority = rec.get('priority', 'medium').lower()
            priority_class = f"rec-{priority}"
            recs_html += f"""
            <div class="recommendation {priority_class}">
                <span class="rec-priority">[{priority.upper()}]</span>
                <span>{html_escape.escape(rec.get('text', ''))}</span>
            </div>
            """

        return f"""
        <div class="section">
            <h2>9. Recommendations</h2>
            {recs_html if recs_html else '<p>No recommendations at this time.</p>'}
        </div>
        """

    def _html_sources(self) -> str:
        """Genera Source Evaluation HTML"""
        sources_html = ""
        for src in self.data.sources:
            sources_html += f"""
            <tr>
                <td>{html_escape.escape(src.get('name', ''))}</td>
                <td>{src.get('type', 'unknown')}</td>
                <td>{src.get('rating', 'N/A')}</td>
            </tr>
            """

        return f"""
        <div class="section">
            <h2>10. Source Evaluation</h2>
            <p>Fonti valutate secondo standard NATO/Admiralty (Reliability A-F, Accuracy 1-6).</p>
            <table>
                <tr><th>Source</th><th>Type</th><th>Rating</th></tr>
                {sources_html if sources_html else '<tr><td colspan="3">No sources documented.</td></tr>'}
            </table>
        </div>
        """

    def _html_footer(self) -> str:
        """Genera Footer HTML"""
        return f"""
        <div class="footer">
            <p><strong>END OF REPORT</strong></p>
            <p>Report ID: {self.report_id}</p>
            <p>Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p>Framework: Dutch OSINT Guy Methodology | Standard: CIA/NATO Intelligence Cycle</p>
            <p>// {self.data.classification} //</p>
        </div>
        """

    # =========================================================================
    # GENERAZIONE PDF
    # =========================================================================

    def generate_pdf(self, output_path: str) -> str:
        """Genera report in formato PDF"""

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )

        styles = self._get_pdf_styles()
        story = []

        # Build story
        story.extend(self._pdf_cover_page(styles))
        story.append(PageBreak())
        story.extend(self._pdf_bluf_section(styles))
        story.append(PageBreak())
        story.extend(self._pdf_introduction(styles))
        story.extend(self._pdf_methodology(styles))
        story.append(PageBreak())
        story.extend(self._pdf_findings(styles))
        story.append(PageBreak())
        story.extend(self._pdf_psychological_profile(styles))
        story.append(PageBreak())
        story.extend(self._pdf_assessment(styles))
        story.extend(self._pdf_recommendations(styles))
        story.append(PageBreak())
        story.extend(self._pdf_footer(styles))

        doc.build(story)
        return output_path

    def _get_pdf_styles(self):
        """Configura stili PDF"""
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name='CoverTitle',
            fontName='Helvetica-Bold',
            fontSize=28,
            alignment=TA_CENTER,
            textColor=HexColor('#003366'),
            spaceAfter=20
        ))

        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontName='Helvetica',
            fontSize=16,
            alignment=TA_CENTER,
            textColor=HexColor('#666666'),
            spaceAfter=10
        ))

        styles.add(ParagraphStyle(
            name='SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=HexColor('#003366'),
            spaceBefore=20,
            spaceAfter=10
        ))

        styles.add(ParagraphStyle(
            name='SubsectionHeader',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=HexColor('#336699'),
            spaceBefore=15,
            spaceAfter=8
        ))

        styles.add(ParagraphStyle(
            name='BodyText15',
            fontName='Helvetica',
            fontSize=10,
            alignment=TA_JUSTIFY,
            leading=14,
            spaceAfter=8
        ))

        styles.add(ParagraphStyle(
            name='BulletItem',
            fontName='Helvetica',
            fontSize=10,
            leftIndent=20,
            spaceAfter=4
        ))

        styles.add(ParagraphStyle(
            name='Classification',
            fontName='Helvetica-Bold',
            fontSize=12,
            alignment=TA_CENTER,
            textColor=HexColor('#C00000'),
            spaceAfter=20
        ))

        return styles

    def _pdf_cover_page(self, styles) -> List:
        """Genera cover page PDF"""
        elements = []

        elements.append(Paragraph(f"// {self.data.classification} //", styles['Classification']))
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("INTELLIGENCE REPORT", styles['CoverTitle']))
        elements.append(Paragraph(self.data.report_title, styles['CoverSubtitle']))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Subject: {self.data.subject_name}", styles['CoverSubtitle']))
        elements.append(Spacer(1, 50))

        # Metadata table
        meta_data = [
            ['Report ID:', self.report_id],
            ['Date:', self.data.report_date.strftime('%d/%m/%Y %H:%M')],
            ['Analyst:', self.data.analyst_name],
            ['Framework:', 'Dutch OSINT Guy Methodology'],
            ['Standard:', 'CIA/NATO Intelligence Cycle']
        ]

        meta_table = Table(meta_data, colWidths=[4*cm, 10*cm])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(meta_table)

        return elements

    def _pdf_bluf_section(self, styles) -> List:
        """Genera BLUF section PDF"""
        elements = []

        elements.append(Paragraph("BOTTOM LINE UP FRONT (BLUF)", styles['SectionHeader']))

        # Summary metrics
        summary = f"""
        <b>Security Grade:</b> {self.data.security_grade} |
        <b>Risk Level:</b> {self.data.exposure_level} |
        <b>Digital Footprint:</b> {self.data.digital_footprint_score}/100
        """
        elements.append(Paragraph(summary, styles['BodyText15']))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Key Judgments", styles['SubsectionHeader']))

        for kj in self.data.key_judgments:
            conf = kj.get('confidence', 'MODERATE')
            text = f"<b>[{conf}]</b> {kj.get('statement', '')}"
            elements.append(Paragraph(text, styles['BodyText15']))

        return elements

    def _pdf_introduction(self, styles) -> List:
        """Genera Introduction PDF"""
        elements = []

        elements.append(Paragraph("1. INTRODUCTION", styles['SectionHeader']))

        elements.append(Paragraph("Purpose", styles['SubsectionHeader']))
        purpose = f"""Condurre un'analisi approfondita della presenza digitale del target per identificare
        vulnerabilità, esposizioni e rischi operativi. L'assessment copre {len(self.data.emails)} email,
        {len(self.data.social_profiles)} profili social, e {len(self.data.data_breaches)} data breach."""
        elements.append(Paragraph(purpose, styles['BodyText15']))

        elements.append(Paragraph("Subject Overview", styles['SubsectionHeader']))

        subject_data = [
            ['Subject', self.data.subject_name],
            ['Emails', str(len(self.data.emails))],
            ['Social Profiles', str(len(self.data.social_profiles))],
            ['Data Breaches', str(len(self.data.data_breaches))],
            ['Passwords Exposed', str(self.data.passwords_exposed)]
        ]

        subject_table = Table(subject_data, colWidths=[5*cm, 9*cm])
        subject_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (0, -1), white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(subject_table)

        return elements

    def _pdf_methodology(self, styles) -> List:
        """Genera Methodology PDF"""
        elements = []

        elements.append(Paragraph("2. METHODOLOGY", styles['SectionHeader']))

        elements.append(Paragraph("Collection Methods", styles['SubsectionHeader']))
        methods = ["SOCMINT (Social Media Intelligence)", "Public Records Search",
                   "Data Breach Database Analysis", "Behavioral Pattern Analysis"]
        for m in methods:
            elements.append(Paragraph(f"• {m}", styles['BulletItem']))

        elements.append(Paragraph("Analysis Techniques", styles['SubsectionHeader']))
        techniques = ["ACH (Analysis of Competing Hypotheses)", "Multi-Source Verification",
                     "Psychological Profiling (Big Five, Dark Triad)", "Risk Quantification"]
        for t in techniques:
            elements.append(Paragraph(f"• {t}", styles['BulletItem']))

        return elements

    def _pdf_findings(self, styles) -> List:
        """Genera Findings PDF"""
        elements = []

        elements.append(Paragraph("3. FINDINGS", styles['SectionHeader']))

        for i, finding in enumerate(self.data.findings, 1):
            title = f"[F-{i:03d}] {finding.get('title', 'Untitled')}"
            elements.append(Paragraph(title, styles['SubsectionHeader']))

            conf = finding.get('confidence', 'MODERATE')
            meta = f"<b>Confidence:</b> {conf} | <b>Category:</b> {finding.get('category', 'general')}"
            elements.append(Paragraph(meta, styles['BodyText15']))
            elements.append(Paragraph(finding.get('description', ''), styles['BodyText15']))
            elements.append(Spacer(1, 10))

        if not self.data.findings:
            elements.append(Paragraph("No findings recorded.", styles['BodyText15']))

        return elements

    def _pdf_psychological_profile(self, styles) -> List:
        """Genera Psychological Profile PDF"""
        elements = []
        pp = self.data.psychological_profile

        elements.append(Paragraph("4. PSYCHOLOGICAL PROFILE", styles['SectionHeader']))

        # Big Five
        elements.append(Paragraph("Big Five Personality Model (OCEAN)", styles['SubsectionHeader']))

        big_five_data = [
            ['Trait', 'Score', 'Level'],
            ['Openness', f"{pp.openness}/100", self._score_level(pp.openness)],
            ['Conscientiousness', f"{pp.conscientiousness}/100", self._score_level(pp.conscientiousness)],
            ['Extraversion', f"{pp.extraversion}/100", self._score_level(pp.extraversion)],
            ['Agreeableness', f"{pp.agreeableness}/100", self._score_level(pp.agreeableness)],
            ['Neuroticism', f"{pp.neuroticism}/100", self._score_level(pp.neuroticism)]
        ]

        bf_table = Table(big_five_data, colWidths=[5*cm, 4*cm, 5*cm])
        bf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        elements.append(bf_table)
        elements.append(Spacer(1, 15))

        # Dark Triad
        elements.append(Paragraph("Dark Triad Screening", styles['SubsectionHeader']))

        dt_data = [
            ['Trait', 'Score', 'Assessment'],
            ['Narcissism', f"{pp.narcissism}/100", self._dt_assessment(pp.narcissism)],
            ['Machiavellianism', f"{pp.machiavellianism}/100", self._dt_assessment(pp.machiavellianism)],
            ['Psychopathy', f"{pp.psychopathy}/100", self._dt_assessment(pp.psychopathy)]
        ]

        dt_table = Table(dt_data, colWidths=[5*cm, 4*cm, 5*cm])
        dt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        elements.append(dt_table)
        elements.append(Spacer(1, 15))

        # Behavioral
        elements.append(Paragraph("Behavioral Assessment", styles['SubsectionHeader']))
        behavioral_text = f"""
        <b>Communication Style:</b> {pp.communication_style or 'Non determinato'}<br/>
        <b>Decision Making:</b> {pp.decision_making or 'Non determinato'}<br/>
        <b>Risk Tolerance:</b> {pp.risk_tolerance or 'Non determinato'}<br/>
        <b>Threat Level:</b> {pp.threat_level}<br/>
        <b>Social Engineering Susceptibility:</b> {pp.social_engineering_susceptibility.upper()}
        """
        elements.append(Paragraph(behavioral_text, styles['BodyText15']))

        # Vulnerabilities
        if pp.psychological_vulnerabilities:
            elements.append(Paragraph("Psychological Vulnerabilities", styles['SubsectionHeader']))
            for vuln in pp.psychological_vulnerabilities:
                elements.append(Paragraph(f"• {vuln}", styles['BulletItem']))

        # AI Analysis
        if pp.ai_analysis:
            elements.append(Paragraph("AI Behavioral Analysis", styles['SubsectionHeader']))
            elements.append(Paragraph(pp.ai_analysis[:1500], styles['BodyText15']))

        return elements

    def _score_level(self, score: int) -> str:
        if score >= 70: return "High"
        elif score >= 40: return "Medium"
        else: return "Low"

    def _dt_assessment(self, score: int) -> str:
        if score >= 70: return "ELEVATED - Monitor"
        elif score >= 40: return "Moderate"
        else: return "Within normal range"

    def _pdf_assessment(self, styles) -> List:
        """Genera Assessment PDF"""
        elements = []

        elements.append(Paragraph("5. ASSESSMENT", styles['SectionHeader']))

        # Security metrics
        metrics_data = [
            ['Metric', 'Value'],
            ['Security Score', f"{self.data.security_score}/100"],
            ['Security Grade', self.data.security_grade],
            ['Exposure Level', self.data.exposure_level],
            ['Digital Footprint', f"{self.data.digital_footprint_score}/100"]
        ]

        metrics_table = Table(metrics_data, colWidths=[7*cm, 7*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 15))

        # Vulnerabilities
        elements.append(Paragraph("Vulnerabilities", styles['SubsectionHeader']))
        for vuln in self.data.vulnerabilities:
            text = f"<b>[{vuln.get('severity', 'N/A')}]</b> {vuln.get('type', '')}: {vuln.get('description', '')}"
            elements.append(Paragraph(text, styles['BodyText15']))

        # Threats
        elements.append(Paragraph("Active Threats", styles['SubsectionHeader']))
        for threat in self.data.threats:
            elements.append(Paragraph(f"• {threat}", styles['BulletItem']))

        return elements

    def _pdf_recommendations(self, styles) -> List:
        """Genera Recommendations PDF"""
        elements = []

        elements.append(Paragraph("6. RECOMMENDATIONS", styles['SectionHeader']))

        for rec in self.data.recommendations:
            priority = rec.get('priority', 'medium').upper()
            text = f"<b>[{priority}]</b> {rec.get('text', '')}"
            elements.append(Paragraph(text, styles['BodyText15']))

        if not self.data.recommendations:
            elements.append(Paragraph("No recommendations at this time.", styles['BodyText15']))

        return elements

    def _pdf_footer(self, styles) -> List:
        """Genera Footer PDF"""
        elements = []

        elements.append(Spacer(1, 30))
        elements.append(Paragraph("─" * 50, styles['BodyText15']))
        elements.append(Paragraph(f"<b>END OF REPORT</b> - {self.report_id}", styles['Classification']))
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Framework: Dutch OSINT Guy Methodology",
            styles['CoverSubtitle']
        ))
        elements.append(Paragraph(f"// {self.data.classification} //", styles['Classification']))

        return elements

    # =========================================================================
    # GENERAZIONE DOCX
    # =========================================================================

    def generate_docx(self, output_path: str) -> str:
        """Genera report in formato DOCX"""

        doc = Document()
        self._setup_docx_styles(doc)

        # Build document
        self._docx_cover_page(doc)
        self._docx_bluf_section(doc)
        self._docx_introduction(doc)
        self._docx_methodology(doc)
        self._docx_findings(doc)
        self._docx_psychological_profile(doc)
        self._docx_assessment(doc)
        self._docx_recommendations(doc)
        self._docx_sources(doc)
        self._docx_footer(doc)

        doc.save(output_path)
        return output_path

    def _setup_docx_styles(self, doc):
        """Setup DOCX styles"""
        pass  # Use default styles for simplicity

    def _add_shading(self, cell, color: str):
        """Aggiunge sfondo a una cella"""
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), color)
        cell._tc.get_or_add_tcPr().append(shading)

    def _docx_cover_page(self, doc):
        """Genera cover page DOCX"""
        # Classification
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"// {self.data.classification} //")
        run.font.bold = True
        run.font.color.rgb = RGBColor(192, 0, 0)
        run.font.size = Pt(14)

        for _ in range(3):
            doc.add_paragraph()

        # Title
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("INTELLIGENCE REPORT")
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(self.data.report_title)
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(51, 102, 153)

        doc.add_paragraph()

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(f"Subject: {self.data.subject_name}").font.size = Pt(14)

        for _ in range(4):
            doc.add_paragraph()

        # Metadata
        table = doc.add_table(rows=5, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        metadata = [
            ("Report ID", self.report_id),
            ("Date", self.data.report_date.strftime('%d/%m/%Y %H:%M')),
            ("Analyst", self.data.analyst_name),
            ("Framework", "Dutch OSINT Guy Methodology"),
            ("Standard", "CIA/NATO Intelligence Cycle")
        ]

        for i, (label, value) in enumerate(metadata):
            row = table.rows[i]
            row.cells[0].text = f"{label}:"
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[1].text = value

        doc.add_page_break()

    def _docx_bluf_section(self, doc):
        """Genera BLUF section DOCX"""
        p = doc.add_paragraph()
        run = p.add_run("BOTTOM LINE UP FRONT (BLUF)")
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        doc.add_paragraph()

        # Metrics
        p = doc.add_paragraph()
        p.add_run(f"Security Grade: ").font.bold = True
        p.add_run(f"{self.data.security_grade} | ")
        p.add_run(f"Risk Level: ").font.bold = True
        p.add_run(f"{self.data.exposure_level} | ")
        p.add_run(f"Digital Footprint: ").font.bold = True
        p.add_run(f"{self.data.digital_footprint_score}/100")

        doc.add_paragraph()

        # Key Judgments
        p = doc.add_paragraph()
        run = p.add_run("Key Judgments")
        run.font.bold = True
        run.font.size = Pt(12)

        for kj in self.data.key_judgments:
            conf = kj.get('confidence', 'MODERATE')
            p = doc.add_paragraph()
            run = p.add_run(f"[{conf}] ")
            run.font.bold = True

            if conf == 'HIGH':
                run.font.color.rgb = RGBColor(0, 128, 0)
            elif conf == 'MODERATE':
                run.font.color.rgb = RGBColor(255, 153, 0)
            else:
                run.font.color.rgb = RGBColor(192, 0, 0)

            p.add_run(kj.get('statement', ''))

        doc.add_page_break()

    def _docx_introduction(self, doc):
        """Genera Introduction DOCX"""
        p = doc.add_paragraph()
        run = p.add_run("1. INTRODUCTION")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        p = doc.add_paragraph()
        run = p.add_run("Purpose")
        run.font.bold = True

        doc.add_paragraph(
            f"Condurre un'analisi approfondita della presenza digitale del target per identificare "
            f"vulnerabilità, esposizioni e rischi operativi. L'assessment copre {len(self.data.emails)} email, "
            f"{len(self.data.social_profiles)} profili social, e {len(self.data.data_breaches)} data breach."
        )

        # Subject table
        table = doc.add_table(rows=5, cols=2)
        table.style = 'Table Grid'

        subject_info = [
            ("Subject", self.data.subject_name),
            ("Emails", str(len(self.data.emails))),
            ("Social Profiles", str(len(self.data.social_profiles))),
            ("Data Breaches", str(len(self.data.data_breaches))),
            ("Passwords Exposed", str(self.data.passwords_exposed))
        ]

        for i, (label, value) in enumerate(subject_info):
            row = table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            self._add_shading(row.cells[0], 'D9E2F3')

    def _docx_methodology(self, doc):
        """Genera Methodology DOCX"""
        doc.add_paragraph()
        p = doc.add_paragraph()
        run = p.add_run("2. METHODOLOGY")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        p = doc.add_paragraph()
        run = p.add_run("Collection Methods")
        run.font.bold = True

        methods = ["SOCMINT", "Public Records Search", "Data Breach Analysis", "Behavioral Analysis"]
        for m in methods:
            doc.add_paragraph(m, style='List Bullet')

        p = doc.add_paragraph()
        run = p.add_run("Analysis Techniques")
        run.font.bold = True

        techniques = ["ACH (Analysis of Competing Hypotheses)", "Multi-Source Verification",
                     "Psychological Profiling", "Risk Quantification"]
        for t in techniques:
            doc.add_paragraph(t, style='List Bullet')

    def _docx_findings(self, doc):
        """Genera Findings DOCX"""
        doc.add_page_break()
        p = doc.add_paragraph()
        run = p.add_run("3. FINDINGS")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        for i, finding in enumerate(self.data.findings, 1):
            doc.add_paragraph()
            p = doc.add_paragraph()
            run = p.add_run(f"[F-{i:03d}] {finding.get('title', '')}")
            run.font.bold = True

            p = doc.add_paragraph()
            p.add_run(f"Confidence: {finding.get('confidence', 'MODERATE')} | ")
            p.add_run(f"Category: {finding.get('category', 'general')}")

            doc.add_paragraph(finding.get('description', ''))

    def _docx_psychological_profile(self, doc):
        """Genera Psychological Profile DOCX"""
        doc.add_page_break()
        p = doc.add_paragraph()
        run = p.add_run("4. PSYCHOLOGICAL PROFILE")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        pp = self.data.psychological_profile

        # Big Five
        p = doc.add_paragraph()
        run = p.add_run("Big Five Personality Model (OCEAN)")
        run.font.bold = True

        table = doc.add_table(rows=6, cols=3)
        table.style = 'Table Grid'

        headers = ['Trait', 'Score', 'Level']
        for i, h in enumerate(headers):
            table.rows[0].cells[i].text = h
            self._add_shading(table.rows[0].cells[i], '003366')
            table.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

        traits = [
            ('Openness', pp.openness),
            ('Conscientiousness', pp.conscientiousness),
            ('Extraversion', pp.extraversion),
            ('Agreeableness', pp.agreeableness),
            ('Neuroticism', pp.neuroticism)
        ]

        for i, (trait, score) in enumerate(traits, 1):
            table.rows[i].cells[0].text = trait
            table.rows[i].cells[1].text = f"{score}/100"
            table.rows[i].cells[2].text = self._score_level(score)

        doc.add_paragraph()

        # Dark Triad
        p = doc.add_paragraph()
        run = p.add_run("Dark Triad Screening")
        run.font.bold = True

        table = doc.add_table(rows=4, cols=3)
        table.style = 'Table Grid'

        headers = ['Trait', 'Score', 'Assessment']
        for i, h in enumerate(headers):
            table.rows[0].cells[i].text = h
            self._add_shading(table.rows[0].cells[i], '003366')
            table.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

        dt_traits = [
            ('Narcissism', pp.narcissism),
            ('Machiavellianism', pp.machiavellianism),
            ('Psychopathy', pp.psychopathy)
        ]

        for i, (trait, score) in enumerate(dt_traits, 1):
            table.rows[i].cells[0].text = trait
            table.rows[i].cells[1].text = f"{score}/100"
            table.rows[i].cells[2].text = self._dt_assessment(score)

        doc.add_paragraph()

        # Behavioral
        p = doc.add_paragraph()
        run = p.add_run("Behavioral Assessment")
        run.font.bold = True

        doc.add_paragraph(f"Communication Style: {pp.communication_style or 'Non determinato'}")
        doc.add_paragraph(f"Decision Making: {pp.decision_making or 'Non determinato'}")
        doc.add_paragraph(f"Risk Tolerance: {pp.risk_tolerance or 'Non determinato'}")
        doc.add_paragraph(f"Threat Level: {pp.threat_level}")
        doc.add_paragraph(f"Social Engineering Susceptibility: {pp.social_engineering_susceptibility.upper()}")

        # Vulnerabilities
        if pp.psychological_vulnerabilities:
            doc.add_paragraph()
            p = doc.add_paragraph()
            run = p.add_run("Psychological Vulnerabilities")
            run.font.bold = True

            for vuln in pp.psychological_vulnerabilities:
                doc.add_paragraph(vuln, style='List Bullet')

        # AI Analysis
        if pp.ai_analysis:
            doc.add_paragraph()
            p = doc.add_paragraph()
            run = p.add_run("AI Behavioral Analysis")
            run.font.bold = True
            doc.add_paragraph(pp.ai_analysis[:2000])

    def _docx_assessment(self, doc):
        """Genera Assessment DOCX"""
        doc.add_page_break()
        p = doc.add_paragraph()
        run = p.add_run("5. ASSESSMENT")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        # Metrics table
        table = doc.add_table(rows=4, cols=2)
        table.style = 'Table Grid'

        metrics = [
            ('Security Score', f"{self.data.security_score}/100"),
            ('Security Grade', self.data.security_grade),
            ('Exposure Level', self.data.exposure_level),
            ('Digital Footprint', f"{self.data.digital_footprint_score}/100")
        ]

        for i, (label, value) in enumerate(metrics):
            table.rows[i].cells[0].text = label
            table.rows[i].cells[1].text = value
            self._add_shading(table.rows[i].cells[0], 'D9E2F3')

        doc.add_paragraph()

        # Vulnerabilities
        p = doc.add_paragraph()
        run = p.add_run("Vulnerabilities")
        run.font.bold = True

        for vuln in self.data.vulnerabilities:
            p = doc.add_paragraph()
            run = p.add_run(f"[{vuln.get('severity', 'N/A')}] ")
            run.font.bold = True
            p.add_run(f"{vuln.get('type', '')}: {vuln.get('description', '')}")

        # Threats
        doc.add_paragraph()
        p = doc.add_paragraph()
        run = p.add_run("Active Threats")
        run.font.bold = True

        for threat in self.data.threats:
            doc.add_paragraph(threat, style='List Bullet')

    def _docx_recommendations(self, doc):
        """Genera Recommendations DOCX"""
        doc.add_paragraph()
        p = doc.add_paragraph()
        run = p.add_run("6. RECOMMENDATIONS")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        for rec in self.data.recommendations:
            p = doc.add_paragraph()
            priority = rec.get('priority', 'medium').upper()
            run = p.add_run(f"[{priority}] ")
            run.font.bold = True

            if priority == 'HIGH':
                run.font.color.rgb = RGBColor(192, 0, 0)
            elif priority == 'MEDIUM':
                run.font.color.rgb = RGBColor(255, 153, 0)

            p.add_run(rec.get('text', ''))

    def _docx_sources(self, doc):
        """Genera Sources DOCX"""
        doc.add_page_break()
        p = doc.add_paragraph()
        run = p.add_run("7. SOURCE EVALUATION")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)

        doc.add_paragraph("Fonti valutate secondo standard NATO/Admiralty (Reliability A-F, Accuracy 1-6).")

        if self.data.sources:
            table = doc.add_table(rows=len(self.data.sources) + 1, cols=3)
            table.style = 'Table Grid'

            headers = ['Source', 'Type', 'Rating']
            for i, h in enumerate(headers):
                table.rows[0].cells[i].text = h
                self._add_shading(table.rows[0].cells[i], '003366')
                table.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

            for i, src in enumerate(self.data.sources, 1):
                table.rows[i].cells[0].text = src.get('name', '')
                table.rows[i].cells[1].text = src.get('type', '')
                table.rows[i].cells[2].text = src.get('rating', 'N/A')

    def _docx_footer(self, doc):
        """Genera Footer DOCX"""
        doc.add_paragraph()
        doc.add_paragraph("─" * 50)

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"END OF REPORT - {self.report_id}")
        run.font.bold = True

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("Framework: Dutch OSINT Guy Methodology | Standard: CIA/NATO Intelligence Cycle")

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"// {self.data.classification} //")
        run.font.bold = True
        run.font.color.rgb = RGBColor(192, 0, 0)

    # =========================================================================
    # GENERAZIONE MULTI-FORMATO
    # =========================================================================

    def generate_all(self, output_dir: str, base_name: str = None) -> Dict[str, str]:
        """
        Genera report in tutti i formati (HTML, DOCX, PDF)

        Args:
            output_dir: Directory di output
            base_name: Nome base per i file (opzionale)

        Returns:
            Dict con i percorsi dei file generati
        """
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = base_name or f"unified_report_{timestamp}"

        paths = {}

        # HTML
        html_path = os.path.join(output_dir, f"{base}.html")
        paths['html'] = self.generate_html(html_path)
        print(f"  ✓ HTML: {html_path}")

        # DOCX
        docx_path = os.path.join(output_dir, f"{base}.docx")
        paths['docx'] = self.generate_docx(docx_path)
        print(f"  ✓ DOCX: {docx_path}")

        # PDF
        pdf_path = os.path.join(output_dir, f"{base}.pdf")
        paths['pdf'] = self.generate_pdf(pdf_path)
        print(f"  ✓ PDF:  {pdf_path}")

        return paths


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_unified_report_from_osint(
    osint_data: Dict,
    analysis_data: Dict,
    psych_profile: Dict,
    security_assessment: Dict,
    subject_name: str,
    output_dir: str,
    anthropic_api_key: str = None
) -> Dict[str, str]:
    """
    Factory function per creare report unificato da dati OSINT

    Returns:
        Dict con percorsi file generati (html, docx, pdf)
    """
    # Build psychological profile
    psych = PsychologicalProfile()

    base_metrics = psych_profile.get('base_metrics', {})
    big_five = base_metrics.get('big_five', {})

    psych.openness = big_five.get('openness', 50)
    psych.conscientiousness = big_five.get('conscientiousness', 50)
    psych.extraversion = big_five.get('extraversion', 50)
    psych.agreeableness = big_five.get('agreeableness', 50)
    psych.neuroticism = big_five.get('neuroticism', 50)

    psych.ai_analysis = psych_profile.get('ai_profile', '')

    risk_profile = base_metrics.get('risk_profile', {})
    psych.social_engineering_susceptibility = risk_profile.get('security_consciousness', 'medium').lower()

    # Determine vulnerabilities from security assessment
    psych.psychological_vulnerabilities = [
        "Potenziale suscettibilità a phishing mirato",
        "Esposizione credenziali aumenta rischio impersonation"
    ] if security_assessment.get('security_grade', 'A') in ['D', 'F'] else []

    # Build unified data
    base = analysis_data.get('base_analysis', {})

    data = UnifiedReportData(
        report_title=f"Intelligence Assessment: {subject_name}",
        subject_name=subject_name,
        emails=osint_data.get('emails', []),
        phones=osint_data.get('phones', []),
        usernames=osint_data.get('usernames', []),
        social_profiles=osint_data.get('social_profiles', []),
        data_breaches=osint_data.get('breaches', []),
        passwords_exposed=len(osint_data.get('passwords', [])),
        digital_footprint_score=base.get('digital_footprint_score', 0),
        exposure_level=base.get('exposure_level', 'UNKNOWN'),
        security_grade=security_assessment.get('security_grade', 'N/A'),
        security_score=security_assessment.get('security_score', 0),
        vulnerabilities=security_assessment.get('vulnerabilities', []),
        threats=security_assessment.get('threats', []),
        recommendations=[{'text': r, 'priority': 'high' if 'URGENTE' in r else 'medium'}
                        for r in security_assessment.get('recommendations', [])],
        psychological_profile=psych
    )

    # Add key judgments
    exposure = data.exposure_level
    data.key_judgments = [
        {
            'statement': f"Il target presenta un livello di esposizione {exposure} con Security Grade {data.security_grade}.",
            'confidence': 'HIGH' if exposure in ['CRITICO', 'ALTO'] else 'MODERATE'
        },
        {
            'statement': f"Identificate {len(data.vulnerabilities)} vulnerabilità e {len(data.threats)} minacce attive.",
            'confidence': 'HIGH'
        }
    ]

    # Add findings
    data.findings = [
        {
            'title': 'Digital Footprint Analysis',
            'description': f"Identificati {len(data.emails)} email, {len(data.social_profiles)} profili social.",
            'confidence': 'HIGH',
            'category': 'digital_footprint'
        }
    ]

    if data.passwords_exposed > 0:
        data.findings.append({
            'title': 'Credential Exposure - CRITICAL',
            'description': f"{data.passwords_exposed} password esposte in data breach.",
            'confidence': 'HIGH',
            'category': 'credential_exposure'
        })

    # Add sources
    for profile in data.social_profiles[:5]:
        data.sources.append({
            'name': f"{profile.get('platform', 'Social')} Profile",
            'type': 'social_media',
            'rating': 'C-2'
        })

    # Generate
    generator = UnifiedReportGenerator(data)
    print(f"\n[*] Generazione Report Unificato per: {subject_name}")

    return generator.generate_all(output_dir)
