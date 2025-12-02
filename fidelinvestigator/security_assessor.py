"""
Security Assessor - Modulo di Valutazione Sicurezza Online
==========================================================

Questo modulo valuta la sicurezza complessiva del target nel web,
analizzando esposizione, vulnerabilità e postura di sicurezza digitale.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExposureMetric:
    """Metrica di esposizione"""
    category: str
    value: int
    max_safe_value: int
    risk_level: str  # safe, warning, danger, critical
    description: str


@dataclass
class VulnerabilityFinding:
    """Vulnerabilità identificata"""
    vulnerability_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_assets: List[str] = field(default_factory=list)
    remediation: str = ""
    cvss_estimate: float = 0.0


@dataclass
class SecurityPosture:
    """Postura di sicurezza"""
    overall_score: float  # 0-100
    grade: str  # F, D, C, B, A
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    immediate_actions: List[str] = field(default_factory=list)


@dataclass
class ThreatAssessment:
    """Valutazione delle minacce"""
    threat_type: str
    likelihood: str  # low, medium, high, very_high
    impact: str  # low, medium, high, critical
    description: str
    indicators: List[str] = field(default_factory=list)


@dataclass
class SecurityReport:
    """Report di sicurezza completo"""
    assessment_date: str = ""
    target_identifier: str = ""
    exposure_metrics: List[ExposureMetric] = field(default_factory=list)
    vulnerabilities: List[VulnerabilityFinding] = field(default_factory=list)
    security_posture: Optional[SecurityPosture] = None
    threat_assessments: List[ThreatAssessment] = field(default_factory=list)
    digital_footprint_analysis: Dict[str, Any] = field(default_factory=dict)
    privacy_score: float = 0.0
    recommendations_priority: List[Dict[str, str]] = field(default_factory=list)


class SecurityAssessor:
    """
    Valutatore di sicurezza online del target.
    Analizza l'esposizione digitale e identifica vulnerabilità.
    """

    # Thresholds per le metriche
    THRESHOLDS = {
        'emails': {'safe': 1, 'warning': 3, 'danger': 5},
        'social_accounts': {'safe': 3, 'warning': 6, 'danger': 10},
        'breaches': {'safe': 0, 'warning': 2, 'danger': 4},
        'exposed_passwords': {'safe': 0, 'warning': 1, 'danger': 3},
        'usernames': {'safe': 2, 'warning': 5, 'danger': 8},
        'phone_numbers': {'safe': 1, 'warning': 2, 'danger': 3},
    }

    def __init__(self, extracted_data, analysis_report=None, password_profile=None):
        """
        Inizializza l'assessor.

        Args:
            extracted_data: Dati estratti dal parser
            analysis_report: Report dell'analizzatore (opzionale)
            password_profile: Profilo password (opzionale)
        """
        self.data = extracted_data
        self.analysis = analysis_report
        self.password_profile = password_profile
        self.report = SecurityReport()

    def assess(self) -> SecurityReport:
        """
        Esegue la valutazione di sicurezza completa.

        Returns:
            SecurityReport: Report di sicurezza
        """
        self.report.assessment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.report.target_identifier = self.data.personal_info.full_name or "Target non identificato"

        # Calcola metriche di esposizione
        self._calculate_exposure_metrics()

        # Identifica vulnerabilità
        self._identify_vulnerabilities()

        # Valuta minacce
        self._assess_threats()

        # Analizza digital footprint
        self._analyze_digital_footprint()

        # Calcola postura di sicurezza
        self._calculate_security_posture()

        # Calcola privacy score
        self._calculate_privacy_score()

        # Genera raccomandazioni prioritizzate
        self._generate_prioritized_recommendations()

        return self.report

    def _calculate_exposure_metrics(self):
        """Calcola metriche di esposizione"""

        metrics = []

        # Email esposte
        email_count = len(self.data.contact_info.emails)
        metrics.append(ExposureMetric(
            category="Email Esposte",
            value=email_count,
            max_safe_value=self.THRESHOLDS['emails']['safe'],
            risk_level=self._get_risk_level(email_count, self.THRESHOLDS['emails']),
            description=f"{email_count} indirizzi email trovati in fonti pubbliche"
        ))

        # Account social
        social_count = len(self.data.social_media)
        metrics.append(ExposureMetric(
            category="Profili Social Media",
            value=social_count,
            max_safe_value=self.THRESHOLDS['social_accounts']['safe'],
            risk_level=self._get_risk_level(social_count, self.THRESHOLDS['social_accounts']),
            description=f"{social_count} profili social media identificati"
        ))

        # Data breach
        breach_count = len(self.data.data_breaches)
        metrics.append(ExposureMetric(
            category="Data Breach",
            value=breach_count,
            max_safe_value=self.THRESHOLDS['breaches']['safe'],
            risk_level=self._get_risk_level(breach_count, self.THRESHOLDS['breaches']),
            description=f"Coinvolgimento in {breach_count} data breach documentati"
        ))

        # Password esposte
        pwd_count = len(self.data.raw_passwords)
        metrics.append(ExposureMetric(
            category="Password Compromesse",
            value=pwd_count,
            max_safe_value=self.THRESHOLDS['exposed_passwords']['safe'],
            risk_level='critical' if pwd_count > 0 else 'safe',
            description=f"{pwd_count} password esposte in chiaro"
        ))

        # Username
        username_count = len(self.data.usernames)
        metrics.append(ExposureMetric(
            category="Username Noti",
            value=username_count,
            max_safe_value=self.THRESHOLDS['usernames']['safe'],
            risk_level=self._get_risk_level(username_count, self.THRESHOLDS['usernames']),
            description=f"{username_count} username associati al target"
        ))

        # Telefoni
        phone_count = len(self.data.contact_info.phones)
        metrics.append(ExposureMetric(
            category="Numeri Telefono",
            value=phone_count,
            max_safe_value=self.THRESHOLDS['phone_numbers']['safe'],
            risk_level=self._get_risk_level(phone_count, self.THRESHOLDS['phone_numbers']),
            description=f"{phone_count} numeri di telefono esposti"
        ))

        self.report.exposure_metrics = metrics

    def _get_risk_level(self, value: int, thresholds: Dict) -> str:
        """Determina il livello di rischio basato sui threshold"""
        if value <= thresholds['safe']:
            return 'safe'
        elif value <= thresholds['warning']:
            return 'warning'
        elif value <= thresholds['danger']:
            return 'danger'
        else:
            return 'critical'

    def _identify_vulnerabilities(self):
        """Identifica vulnerabilità di sicurezza"""

        vulnerabilities = []

        # Vulnerabilità: Password esposte
        if self.data.raw_passwords:
            vulnerabilities.append(VulnerabilityFinding(
                vulnerability_type="Credential Exposure",
                severity="critical",
                description="Password in chiaro trovate in data breach o leak pubblici",
                affected_assets=[f"Password #{i+1}" for i in range(len(self.data.raw_passwords))],
                remediation="Cambio immediato di tutte le password compromesse e implementazione 2FA",
                cvss_estimate=9.8
            ))

        # Vulnerabilità: Email in breach multipli
        if len(self.data.data_breaches) > 2:
            vulnerabilities.append(VulnerabilityFinding(
                vulnerability_type="Repeated Breach Exposure",
                severity="high",
                description="Email coinvolta in multipli data breach, indica possibile riutilizzo credenziali",
                affected_assets=[b.breach_name for b in self.data.data_breaches],
                remediation="Audit completo delle credenziali, utilizzo password uniche per ogni servizio",
                cvss_estimate=7.5
            ))

        # Vulnerabilità: PII esposti
        pii_exposed = []
        if self.data.personal_info.date_of_birth:
            pii_exposed.append("Data di nascita")
        if self.data.personal_info.full_name:
            pii_exposed.append("Nome completo")
        if self.data.contact_info.phones:
            pii_exposed.append("Numero telefono")

        if len(pii_exposed) >= 2:
            vulnerabilities.append(VulnerabilityFinding(
                vulnerability_type="PII Exposure",
                severity="high",
                description="Informazioni personali sensibili pubblicamente accessibili",
                affected_assets=pii_exposed,
                remediation="Rimozione dati da fonti pubbliche, richiesta diritto all'oblio",
                cvss_estimate=6.5
            ))

        # Vulnerabilità: Username consistente
        if len(set(self.data.usernames)) == 1 and len(self.data.usernames) > 2:
            vulnerabilities.append(VulnerabilityFinding(
                vulnerability_type="Identity Correlation",
                severity="medium",
                description="Username identico su multiple piattaforme facilita il tracking",
                affected_assets=list(set(self.data.usernames)),
                remediation="Diversificare gli username su piattaforme diverse",
                cvss_estimate=4.3
            ))

        # Vulnerabilità: Over-sharing social
        if len(self.data.social_media) > 7:
            vulnerabilities.append(VulnerabilityFinding(
                vulnerability_type="Social Media Over-Exposure",
                severity="medium",
                description="Presenza eccessiva sui social aumenta la superficie di attacco",
                affected_assets=[p.platform for p in self.data.social_media],
                remediation="Consolidare la presenza social, rimuovere account inattivi",
                cvss_estimate=4.0
            ))

        # Vulnerabilità da password analysis
        if self.password_profile and self.password_profile.security_level in ['CRITICO', 'BASSO']:
            vulnerabilities.append(VulnerabilityFinding(
                vulnerability_type="Weak Password Practices",
                severity="high",
                description="Pattern di password deboli e prevedibili identificati",
                affected_assets=["Credenziali del target"],
                remediation="Adozione di password manager e policy di password complesse",
                cvss_estimate=7.0
            ))

        self.report.vulnerabilities = vulnerabilities

    def _assess_threats(self):
        """Valuta le minacce potenziali"""

        threats = []

        # Minaccia: Credential stuffing
        if self.data.raw_passwords and self.data.contact_info.emails:
            threats.append(ThreatAssessment(
                threat_type="Credential Stuffing Attack",
                likelihood="very_high",
                impact="critical",
                description="Con credenziali esposte, attaccanti possono tentare accesso a multipli servizi",
                indicators=[
                    "Password in chiaro disponibili",
                    "Email note",
                    "Pattern password prevedibili"
                ]
            ))

        # Minaccia: Social engineering
        if self.data.personal_info.full_name and len(self.data.social_media) > 3:
            threats.append(ThreatAssessment(
                threat_type="Social Engineering / Spear Phishing",
                likelihood="high",
                impact="high",
                description="Informazioni personali dettagliate permettono attacchi di phishing mirati",
                indicators=[
                    "Informazioni personali pubbliche",
                    "Presenza social attiva",
                    "Pattern comportamentali identificabili"
                ]
            ))

        # Minaccia: Identity theft
        pii_count = sum([
            1 if self.data.personal_info.date_of_birth else 0,
            1 if self.data.personal_info.full_name else 0,
            1 if self.data.contact_info.phones else 0,
            1 if self.data.contact_info.addresses else 0
        ])
        if pii_count >= 3:
            threats.append(ThreatAssessment(
                threat_type="Identity Theft",
                likelihood="medium",
                impact="critical",
                description="Sufficenti PII esposti per potenziale furto d'identità",
                indicators=[
                    "Dati anagrafici disponibili",
                    "Contatti personali noti",
                    "Storico digitale tracciabile"
                ]
            ))

        # Minaccia: Account takeover
        if self.data.data_breaches:
            threats.append(ThreatAssessment(
                threat_type="Account Takeover",
                likelihood="high" if len(self.data.data_breaches) > 2 else "medium",
                impact="high",
                description="Credenziali compromesse in breach possono essere usate per accesso non autorizzato",
                indicators=[
                    f"Coinvolgimento in {len(self.data.data_breaches)} breach",
                    "Possibile riutilizzo password"
                ]
            ))

        # Minaccia: Doxing
        if len(self.data.contact_info.emails) > 2 and len(self.data.social_media) > 3:
            threats.append(ThreatAssessment(
                threat_type="Doxing",
                likelihood="medium",
                impact="medium",
                description="Sufficenti informazioni pubbliche per compilare un dossier personale",
                indicators=[
                    "Multiple email pubbliche",
                    "Presenza social estesa",
                    "Correlazioni identità verificabili"
                ]
            ))

        self.report.threat_assessments = threats

    def _analyze_digital_footprint(self):
        """Analizza l'impronta digitale"""

        footprint = {
            'size': 'unknown',
            'age': 'unknown',
            'consistency': 'unknown',
            'platforms': [],
            'data_categories': []
        }

        # Dimensione footprint
        total_touchpoints = (
            len(self.data.contact_info.emails) +
            len(self.data.social_media) +
            len(self.data.usernames) +
            len(self.data.domains)
        )

        if total_touchpoints < 5:
            footprint['size'] = 'Ridotto'
        elif total_touchpoints < 15:
            footprint['size'] = 'Moderato'
        elif total_touchpoints < 30:
            footprint['size'] = 'Esteso'
        else:
            footprint['size'] = 'Molto esteso'

        # Piattaforme
        footprint['platforms'] = list(set(p.platform for p in self.data.social_media))

        # Categorie dati presenti
        categories = []
        if self.data.personal_info.full_name:
            categories.append("Dati anagrafici")
        if self.data.contact_info.emails:
            categories.append("Contatti email")
        if self.data.contact_info.phones:
            categories.append("Contatti telefonici")
        if self.data.social_media:
            categories.append("Profili social")
        if self.data.data_breaches:
            categories.append("Dati da breach")
        if self.data.raw_passwords:
            categories.append("Credenziali")
        if self.data.locations:
            categories.append("Dati di localizzazione")

        footprint['data_categories'] = categories

        # Consistenza (username uguali = alta consistenza)
        unique_usernames = len(set(u.lower() for u in self.data.usernames))
        if unique_usernames == 1 and len(self.data.usernames) > 1:
            footprint['consistency'] = 'Alta (username consistente)'
        elif unique_usernames <= 3:
            footprint['consistency'] = 'Media'
        else:
            footprint['consistency'] = 'Bassa (identità frammentate)'

        self.report.digital_footprint_analysis = footprint

    def _calculate_security_posture(self):
        """Calcola la postura di sicurezza complessiva"""

        score = 100  # Parte da 100 e sottrae penalità

        strengths = []
        weaknesses = []
        immediate_actions = []

        # Penalità per vulnerabilità
        for vuln in self.report.vulnerabilities:
            if vuln.severity == 'critical':
                score -= 25
                weaknesses.append(vuln.description)
                immediate_actions.append(vuln.remediation)
            elif vuln.severity == 'high':
                score -= 15
                weaknesses.append(vuln.description)
            elif vuln.severity == 'medium':
                score -= 8

        # Penalità per metriche
        for metric in self.report.exposure_metrics:
            if metric.risk_level == 'critical':
                score -= 15
            elif metric.risk_level == 'danger':
                score -= 10
            elif metric.risk_level == 'warning':
                score -= 5

        # Bonus per pratiche positive
        if not self.data.raw_passwords:
            score += 10
            strengths.append("Nessuna password esposta in chiaro")

        if not self.data.data_breaches:
            score += 15
            strengths.append("Nessun coinvolgimento in data breach noti")

        if len(self.data.social_media) <= 3:
            score += 5
            strengths.append("Presenza social contenuta")

        # Normalizza score
        score = max(0, min(100, score))

        # Determina grade
        if score >= 90:
            grade = 'A'
        elif score >= 80:
            grade = 'B'
        elif score >= 70:
            grade = 'C'
        elif score >= 50:
            grade = 'D'
        else:
            grade = 'F'

        self.report.security_posture = SecurityPosture(
            overall_score=score,
            grade=grade,
            strengths=strengths,
            weaknesses=weaknesses[:5],
            immediate_actions=immediate_actions[:3]
        )

    def _calculate_privacy_score(self):
        """Calcola il punteggio di privacy"""

        privacy_score = 100

        # Penalità per ogni categoria di dati esposti
        if self.data.personal_info.full_name:
            privacy_score -= 10
        if self.data.personal_info.date_of_birth:
            privacy_score -= 15
        if self.data.contact_info.emails:
            privacy_score -= len(self.data.contact_info.emails) * 5
        if self.data.contact_info.phones:
            privacy_score -= len(self.data.contact_info.phones) * 10
        if self.data.contact_info.addresses:
            privacy_score -= len(self.data.contact_info.addresses) * 15
        if self.data.social_media:
            privacy_score -= len(self.data.social_media) * 3
        if self.data.locations:
            privacy_score -= len(self.data.locations) * 5

        self.report.privacy_score = max(0, privacy_score)

    def _generate_prioritized_recommendations(self):
        """Genera raccomandazioni prioritizzate"""

        recommendations = []

        # Priorità 1: Password compromesse
        if self.data.raw_passwords:
            recommendations.append({
                'priority': 'CRITICA',
                'action': 'Cambio immediato di tutte le password compromesse',
                'timeline': 'Entro 24 ore',
                'impact': 'Previene accesso non autorizzato agli account'
            })

        # Priorità 2: 2FA
        if self.data.contact_info.emails:
            recommendations.append({
                'priority': 'ALTA',
                'action': 'Abilitare autenticazione a due fattori su tutti gli account',
                'timeline': 'Entro 1 settimana',
                'impact': 'Aggiunge layer di protezione anche con credenziali compromesse'
            })

        # Priorità 3: Password manager
        recommendations.append({
            'priority': 'ALTA',
            'action': 'Adottare un password manager (es. Bitwarden, 1Password)',
            'timeline': 'Entro 2 settimane',
            'impact': 'Elimina riutilizzo password e migliora complessità'
        })

        # Priorità 4: Audit social
        if len(self.data.social_media) > 5:
            recommendations.append({
                'priority': 'MEDIA',
                'action': 'Audit e consolidamento profili social media',
                'timeline': 'Entro 1 mese',
                'impact': 'Riduce superficie di attacco e esposizione dati'
            })

        # Priorità 5: Monitoraggio breach
        recommendations.append({
            'priority': 'MEDIA',
            'action': 'Iscriversi a servizi di monitoraggio breach (es. Have I Been Pwned)',
            'timeline': 'Entro 1 settimana',
            'impact': 'Notifica tempestiva di nuove compromissioni'
            })

        # Priorità 6: Privacy settings
        recommendations.append({
            'priority': 'MEDIA',
            'action': 'Revisione impostazioni privacy su tutti i social media',
            'timeline': 'Entro 2 settimane',
            'impact': 'Limita informazioni accessibili pubblicamente'
        })

        self.report.recommendations_priority = recommendations

    def get_executive_summary(self) -> Dict[str, Any]:
        """Restituisce un sommario esecutivo"""
        return {
            'target': self.report.target_identifier,
            'assessment_date': self.report.assessment_date,
            'security_grade': self.report.security_posture.grade if self.report.security_posture else 'N/A',
            'security_score': self.report.security_posture.overall_score if self.report.security_posture else 0,
            'privacy_score': self.report.privacy_score,
            'critical_vulnerabilities': sum(1 for v in self.report.vulnerabilities if v.severity == 'critical'),
            'high_vulnerabilities': sum(1 for v in self.report.vulnerabilities if v.severity == 'high'),
            'immediate_actions_required': len(self.report.security_posture.immediate_actions) if self.report.security_posture else 0,
            'exposure_level': self.report.digital_footprint_analysis.get('size', 'Unknown')
        }
