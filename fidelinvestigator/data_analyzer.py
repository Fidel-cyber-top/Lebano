"""
Data Analyzer - Modulo di Analisi e Correlazione Dati
======================================================

Questo modulo analizza e correla i dati estratti dal report OSINT,
identificando pattern, connessioni e insight investigativi.
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, field


@dataclass
class CorrelationResult:
    """Risultato di una correlazione"""
    correlation_type: str
    source_data: Any
    target_data: Any
    confidence: float  # 0.0 - 1.0
    description: str
    significance: str  # low, medium, high, critical


@dataclass
class IdentityCluster:
    """Cluster di identità correlate"""
    primary_identity: str
    aliases: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ActivityPattern:
    """Pattern di attività rilevato"""
    pattern_type: str
    description: str
    frequency: str
    platforms: List[str] = field(default_factory=list)
    time_windows: List[str] = field(default_factory=list)
    significance: str = "medium"


@dataclass
class RiskIndicator:
    """Indicatore di rischio"""
    indicator_type: str
    description: str
    severity: str  # low, medium, high, critical
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AnalysisReport:
    """Report completo dell'analisi"""
    identity_clusters: List[IdentityCluster] = field(default_factory=list)
    correlations: List[CorrelationResult] = field(default_factory=list)
    activity_patterns: List[ActivityPattern] = field(default_factory=list)
    risk_indicators: List[RiskIndicator] = field(default_factory=list)
    digital_footprint_score: float = 0.0
    exposure_level: str = "unknown"
    key_findings: List[str] = field(default_factory=list)
    investigation_leads: List[str] = field(default_factory=list)


class DataAnalyzer:
    """
    Analizzatore di dati OSINT con capacità di correlazione avanzata.
    Utilizza tecniche di intelligence per identificare pattern e connessioni.
    """

    def __init__(self, extracted_data):
        """
        Inizializza l'analizzatore.

        Args:
            extracted_data: Dati estratti dal parser HTML (ExtractedData)
        """
        self.data = extracted_data
        self.report = AnalysisReport()

    def analyze(self) -> AnalysisReport:
        """
        Esegue l'analisi completa dei dati.

        Returns:
            AnalysisReport: Report completo dell'analisi
        """
        # Analisi identità
        self._analyze_identity_clusters()

        # Correlazioni
        self._correlate_emails_usernames()
        self._correlate_social_profiles()
        self._correlate_breach_data()
        self._correlate_locations()
        self._correlate_temporal_data()

        # Pattern di attività
        self._analyze_activity_patterns()

        # Indicatori di rischio
        self._assess_risk_indicators()

        # Calcola score e livello esposizione
        self._calculate_digital_footprint()

        # Genera findings e leads
        self._generate_key_findings()
        self._generate_investigation_leads()

        return self.report

    def _analyze_identity_clusters(self):
        """Analizza e raggruppa identità correlate"""
        clusters = []

        # Usa l'email principale come identità primaria
        primary_emails = self.data.contact_info.emails

        for email_info in primary_emails:
            email = email_info.get('email', '')
            username_from_email = email.split('@')[0] if '@' in email else ''

            cluster = IdentityCluster(
                primary_identity=email,
                emails=[email],
                aliases=[],
                usernames=[]
            )

            # Trova username correlati
            for username in self.data.usernames:
                similarity = self._calculate_similarity(username_from_email, username)
                if similarity > 0.5:
                    cluster.usernames.append(username)

            # Aggiungi alias dal personal info
            if self.data.personal_info.aliases:
                cluster.aliases.extend(self.data.personal_info.aliases)

            # Calcola confidence basata sui match
            matches = len(cluster.usernames) + len(cluster.aliases)
            cluster.confidence = min(1.0, 0.3 + (matches * 0.15))

            clusters.append(cluster)

        # Raggruppa cluster con overlap
        self.report.identity_clusters = self._merge_overlapping_clusters(clusters)

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcola similarità tra due stringhe (Jaccard)"""
        if not str1 or not str2:
            return 0.0

        str1 = str1.lower()
        str2 = str2.lower()

        if str1 == str2:
            return 1.0

        # Jaccard similarity
        set1 = set(str1)
        set2 = set(str2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _merge_overlapping_clusters(self, clusters: List[IdentityCluster]) -> List[IdentityCluster]:
        """Unisce cluster con identità sovrapposte"""
        if len(clusters) <= 1:
            return clusters

        merged = []
        used = set()

        for i, cluster1 in enumerate(clusters):
            if i in used:
                continue

            current = cluster1
            for j, cluster2 in enumerate(clusters[i+1:], start=i+1):
                if j in used:
                    continue

                # Verifica overlap
                overlap = (
                    set(current.emails) & set(cluster2.emails) or
                    set(current.usernames) & set(cluster2.usernames)
                )

                if overlap:
                    # Merge clusters
                    current.emails = list(set(current.emails + cluster2.emails))
                    current.usernames = list(set(current.usernames + cluster2.usernames))
                    current.aliases = list(set(current.aliases + cluster2.aliases))
                    current.confidence = max(current.confidence, cluster2.confidence)
                    used.add(j)

            merged.append(current)

        return merged

    def _correlate_emails_usernames(self):
        """Correla email e username"""
        for email_info in self.data.contact_info.emails:
            email = email_info.get('email', '')
            local_part = email.split('@')[0] if '@' in email else ''

            for username in self.data.usernames:
                similarity = self._calculate_similarity(local_part, username)

                if similarity > 0.7:
                    self.report.correlations.append(CorrelationResult(
                        correlation_type="email_username",
                        source_data=email,
                        target_data=username,
                        confidence=similarity,
                        description=f"Username '{username}' fortemente correlato all'email '{email}'",
                        significance="high" if similarity > 0.85 else "medium"
                    ))
                elif similarity > 0.5:
                    self.report.correlations.append(CorrelationResult(
                        correlation_type="email_username",
                        source_data=email,
                        target_data=username,
                        confidence=similarity,
                        description=f"Possibile correlazione tra username '{username}' e email '{email}'",
                        significance="low"
                    ))

    def _correlate_social_profiles(self):
        """Correla profili social media"""
        profiles = self.data.social_media

        # Raggruppa per username
        username_profiles = defaultdict(list)
        for profile in profiles:
            if profile.username:
                username_profiles[profile.username.lower()].append(profile)

        # Trova username usati su multiple piattaforme
        for username, profs in username_profiles.items():
            if len(profs) > 1:
                platforms = [p.platform for p in profs]
                self.report.correlations.append(CorrelationResult(
                    correlation_type="cross_platform_identity",
                    source_data=username,
                    target_data=platforms,
                    confidence=0.9,
                    description=f"Username '{username}' utilizzato su: {', '.join(platforms)}",
                    significance="high"
                ))

        # Correla con email
        for profile in profiles:
            if profile.username:
                for email_info in self.data.contact_info.emails:
                    email = email_info.get('email', '')
                    local_part = email.split('@')[0] if '@' in email else ''

                    if self._calculate_similarity(profile.username, local_part) > 0.6:
                        self.report.correlations.append(CorrelationResult(
                            correlation_type="social_email",
                            source_data=f"{profile.platform}: {profile.username}",
                            target_data=email,
                            confidence=0.75,
                            description=f"Profilo {profile.platform} correlato all'email {email}",
                            significance="medium"
                        ))

    def _correlate_breach_data(self):
        """Correla dati da breach"""
        breaches = self.data.data_breaches
        emails = [e.get('email', '') for e in self.data.contact_info.emails]

        # Verifica quali email sono coinvolte in breach
        email_breach_map = defaultdict(list)
        for breach in breaches:
            if breach.email_involved and breach.email_involved in emails:
                email_breach_map[breach.email_involved].append(breach.breach_name)

        for email, breach_names in email_breach_map.items():
            self.report.correlations.append(CorrelationResult(
                correlation_type="email_breach",
                source_data=email,
                target_data=breach_names,
                confidence=1.0,
                description=f"Email '{email}' compromessa in {len(breach_names)} breach: {', '.join(breach_names)}",
                significance="critical"
            ))

        # Analizza password esposte
        if self.data.raw_passwords:
            self.report.correlations.append(CorrelationResult(
                correlation_type="password_exposure",
                source_data="passwords",
                target_data=len(self.data.raw_passwords),
                confidence=1.0,
                description=f"{len(self.data.raw_passwords)} password esposte trovate",
                significance="critical"
            ))

    def _correlate_locations(self):
        """Correla dati di geolocalizzazione"""
        locations = self.data.locations

        if not locations:
            return

        # Raggruppa per tipo
        mentioned = [l for l in locations if l.get('type') == 'mentioned']
        coordinates = [l for l in locations if l.get('type') == 'coordinates']

        if len(mentioned) > 1:
            places = [l.get('raw', '') for l in mentioned]
            self.report.correlations.append(CorrelationResult(
                correlation_type="location_pattern",
                source_data="locations",
                target_data=places,
                confidence=0.7,
                description=f"Il target è stato associato a {len(places)} località: {', '.join(places[:5])}",
                significance="medium"
            ))

        if coordinates:
            self.report.correlations.append(CorrelationResult(
                correlation_type="gps_data",
                source_data="coordinates",
                target_data=len(coordinates),
                confidence=1.0,
                description=f"Trovate {len(coordinates)} coordinate GPS associate al target",
                significance="high"
            ))

    def _correlate_temporal_data(self):
        """Correla dati temporali"""
        timeline = self.data.timeline

        if not timeline:
            return

        # Ordina per data
        sorted_events = sorted(timeline, key=lambda x: x.get('date', ''))

        if len(sorted_events) >= 2:
            first_date = sorted_events[0].get('date', 'N/A')
            last_date = sorted_events[-1].get('date', 'N/A')

            self.report.correlations.append(CorrelationResult(
                correlation_type="temporal_range",
                source_data=first_date,
                target_data=last_date,
                confidence=0.8,
                description=f"Attività del target tracciata dal {first_date} al {last_date}",
                significance="medium"
            ))

    def _analyze_activity_patterns(self):
        """Analizza pattern di attività online"""
        # Pattern di presenza social
        platforms = [p.platform for p in self.data.social_media]
        platform_counts = Counter(platforms)

        if platforms:
            self.report.activity_patterns.append(ActivityPattern(
                pattern_type="social_presence",
                description=f"Presenza attiva su {len(set(platforms))} piattaforme social",
                frequency="regular",
                platforms=list(set(platforms)),
                significance="medium"
            ))

        # Pattern di username
        usernames = self.data.usernames
        if len(usernames) > 1:
            # Cerca pattern comuni nei username
            common_patterns = self._find_username_patterns(usernames)
            if common_patterns:
                self.report.activity_patterns.append(ActivityPattern(
                    pattern_type="username_pattern",
                    description=f"Pattern ricorrente nei username: {', '.join(common_patterns)}",
                    frequency="consistent",
                    significance="high"
                ))

        # Pattern email
        emails = [e.get('email', '') for e in self.data.contact_info.emails]
        if len(emails) > 1:
            domains = [e.split('@')[1] for e in emails if '@' in e]
            if len(set(domains)) > 1:
                self.report.activity_patterns.append(ActivityPattern(
                    pattern_type="email_diversification",
                    description=f"Utilizzo di {len(set(domains))} diversi provider email",
                    frequency="intentional",
                    significance="medium"
                ))

    def _find_username_patterns(self, usernames: List[str]) -> List[str]:
        """Trova pattern comuni nei username"""
        patterns = []

        # Trova radice comune
        if len(usernames) >= 2:
            common_prefix = self._longest_common_prefix(usernames)
            if len(common_prefix) >= 3:
                patterns.append(f"prefisso comune: {common_prefix}")

        # Cerca numeri ricorrenti
        numbers = []
        for username in usernames:
            nums = re.findall(r'\d+', username)
            numbers.extend(nums)

        number_counts = Counter(numbers)
        for num, count in number_counts.items():
            if count > 1:
                patterns.append(f"numero ricorrente: {num}")

        return patterns

    def _longest_common_prefix(self, strings: List[str]) -> str:
        """Trova il prefisso comune più lungo"""
        if not strings:
            return ""

        strings = [s.lower() for s in strings]
        shortest = min(strings, key=len)

        for i, char in enumerate(shortest):
            for string in strings:
                if string[i] != char:
                    return shortest[:i]

        return shortest

    def _assess_risk_indicators(self):
        """Valuta indicatori di rischio per la sicurezza del target"""

        # Password esposte
        if self.data.raw_passwords:
            self.report.risk_indicators.append(RiskIndicator(
                indicator_type="password_exposure",
                description=f"{len(self.data.raw_passwords)} password esposte in chiaro",
                severity="critical",
                evidence=[f"Password trovata: {p[:2]}***" for p in self.data.raw_passwords[:3]],
                recommendations=[
                    "Cambio immediato di tutte le password compromesse",
                    "Implementazione autenticazione a due fattori",
                    "Utilizzo di un password manager"
                ]
            ))

        # Data breaches
        if self.data.data_breaches:
            severity = "critical" if len(self.data.data_breaches) > 3 else "high"
            self.report.risk_indicators.append(RiskIndicator(
                indicator_type="breach_exposure",
                description=f"Coinvolgimento in {len(self.data.data_breaches)} data breach",
                severity=severity,
                evidence=[b.breach_name for b in self.data.data_breaches[:5]],
                recommendations=[
                    "Monitoraggio attivo delle credenziali",
                    "Reset di tutte le credenziali associate",
                    "Verifica accessi non autorizzati"
                ]
            ))

        # Esposizione email
        email_count = len(self.data.contact_info.emails)
        if email_count > 2:
            self.report.risk_indicators.append(RiskIndicator(
                indicator_type="email_exposure",
                description=f"{email_count} indirizzi email esposti pubblicamente",
                severity="medium",
                evidence=[e.get('email', '') for e in self.data.contact_info.emails[:3]],
                recommendations=[
                    "Riduzione della superficie di esposizione",
                    "Utilizzo di email alias",
                    "Implementazione di filtri anti-spam avanzati"
                ]
            ))

        # Social media footprint
        social_count = len(self.data.social_media)
        if social_count > 5:
            self.report.risk_indicators.append(RiskIndicator(
                indicator_type="social_overexposure",
                description=f"Presenza su {social_count} piattaforme social",
                severity="medium",
                evidence=[p.platform for p in self.data.social_media[:5]],
                recommendations=[
                    "Revisione delle impostazioni privacy",
                    "Consolidamento della presenza online",
                    "Audit delle informazioni pubblicate"
                ]
            ))

        # Informazioni personali esposte
        personal = self.data.personal_info
        exposed_fields = []
        if personal.date_of_birth:
            exposed_fields.append("data di nascita")
        if personal.full_name:
            exposed_fields.append("nome completo")
        if self.data.contact_info.phones:
            exposed_fields.append("numeri di telefono")

        if len(exposed_fields) >= 2:
            self.report.risk_indicators.append(RiskIndicator(
                indicator_type="pii_exposure",
                description=f"Dati personali sensibili esposti: {', '.join(exposed_fields)}",
                severity="high",
                evidence=exposed_fields,
                recommendations=[
                    "Rimozione dati personali da fonti pubbliche",
                    "Richiesta di diritto all'oblio dove applicabile",
                    "Monitoraggio per identity theft"
                ]
            ))

    def _calculate_digital_footprint(self):
        """Calcola il punteggio di digital footprint"""
        score = 0
        factors = []

        # Email (+10 per email, max 30)
        email_score = min(30, len(self.data.contact_info.emails) * 10)
        score += email_score
        factors.append(f"Email: {email_score}")

        # Social media (+8 per profilo, max 40)
        social_score = min(40, len(self.data.social_media) * 8)
        score += social_score
        factors.append(f"Social: {social_score}")

        # Data breaches (+15 per breach, penalità)
        breach_score = min(30, len(self.data.data_breaches) * 15)
        score += breach_score
        factors.append(f"Breaches: {breach_score}")

        # Password esposte (+20 per password)
        pwd_score = min(30, len(self.data.raw_passwords) * 20)
        score += pwd_score
        factors.append(f"Passwords: {pwd_score}")

        # Username (+5 per username)
        user_score = min(20, len(self.data.usernames) * 5)
        score += user_score
        factors.append(f"Usernames: {user_score}")

        self.report.digital_footprint_score = min(100, score)

        # Determina livello esposizione
        if score >= 80:
            self.report.exposure_level = "CRITICO"
        elif score >= 60:
            self.report.exposure_level = "ALTO"
        elif score >= 40:
            self.report.exposure_level = "MODERATO"
        elif score >= 20:
            self.report.exposure_level = "BASSO"
        else:
            self.report.exposure_level = "MINIMO"

    def _generate_key_findings(self):
        """Genera i findings chiave dell'analisi"""
        findings = []

        # Identità
        if self.data.personal_info.full_name:
            findings.append(f"Identità confermata: {self.data.personal_info.full_name}")

        # Correlazioni critiche
        critical_correlations = [c for c in self.report.correlations if c.significance == "critical"]
        if critical_correlations:
            findings.append(f"Identificate {len(critical_correlations)} correlazioni critiche")

        # Esposizione
        findings.append(f"Livello di esposizione digitale: {self.report.exposure_level}")
        findings.append(f"Digital footprint score: {self.report.digital_footprint_score}/100")

        # Breach
        if self.data.data_breaches:
            findings.append(f"Target coinvolto in {len(self.data.data_breaches)} data breach documentati")

        # Password
        if self.data.raw_passwords:
            findings.append(f"ATTENZIONE: {len(self.data.raw_passwords)} password esposte in chiaro")

        # Social
        platforms = set(p.platform for p in self.data.social_media)
        if platforms:
            findings.append(f"Presenza confermata su: {', '.join(platforms)}")

        self.report.key_findings = findings

    def _generate_investigation_leads(self):
        """Genera piste investigative da approfondire"""
        leads = []

        # Lead da username
        if self.data.usernames:
            leads.append(f"Approfondire i seguenti username su altre piattaforme: {', '.join(self.data.usernames[:5])}")

        # Lead da email
        for email_info in self.data.contact_info.emails[:3]:
            email = email_info.get('email', '')
            leads.append(f"Verificare registrazioni associate a: {email}")

        # Lead da correlazioni
        high_conf_correlations = [c for c in self.report.correlations if c.confidence > 0.8]
        for corr in high_conf_correlations[:3]:
            leads.append(f"Investigare correlazione: {corr.description}")

        # Lead da social
        for profile in self.data.social_media[:3]:
            if profile.profile_url:
                leads.append(f"Analizzare profilo {profile.platform}: {profile.username}")

        # Lead da domini
        for domain in self.data.domains[:3]:
            leads.append(f"Investigare dominio: {domain.domain}")

        self.report.investigation_leads = leads

    def get_correlation_matrix(self) -> Dict[str, List[str]]:
        """Restituisce una matrice di correlazione semplificata"""
        matrix = defaultdict(list)

        for corr in self.report.correlations:
            key = corr.correlation_type
            matrix[key].append({
                'source': str(corr.source_data),
                'target': str(corr.target_data),
                'confidence': corr.confidence,
                'significance': corr.significance
            })

        return dict(matrix)

    def get_risk_summary(self) -> Dict[str, Any]:
        """Restituisce un sommario dei rischi"""
        risks_by_severity = defaultdict(list)
        for risk in self.report.risk_indicators:
            risks_by_severity[risk.severity].append(risk.indicator_type)

        return {
            'total_risks': len(self.report.risk_indicators),
            'critical': len(risks_by_severity.get('critical', [])),
            'high': len(risks_by_severity.get('high', [])),
            'medium': len(risks_by_severity.get('medium', [])),
            'low': len(risks_by_severity.get('low', [])),
            'exposure_level': self.report.exposure_level,
            'footprint_score': self.report.digital_footprint_score
        }
