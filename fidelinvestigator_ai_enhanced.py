#!/usr/bin/env python3
"""
FidelinvestigatorAI - Enhanced Edition con AI Integration
Agente Investigativo OSINT di Alto Profilo

Integrazione:
- Perplexity AI: Verifica OSINT e ricerche in tempo reale
- OpenAI GPT-4: Correlazione dati e analisi pattern avanzata
- Anthropic Claude: Profilazione psicologica e redazione report

Autore: FidelinvestigatorAI Team
"""

import os
import sys
import json
import re
import hashlib
import math
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from collections import Counter
import time

# Auto-installazione dipendenze
def install_dependencies():
    required = ['beautifulsoup4', 'reportlab', 'lxml', 'Pillow', 'openai', 'anthropic', 'requests']
    import subprocess
    for package in required:
        try:
            __import__(package.replace('-', '_').split('[')[0])
        except ImportError:
            print(f"[*] Installazione {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])

install_dependencies()

from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT, TA_LEFT
from reportlab.lib.colors import HexColor, black, grey
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import openai
import anthropic
import requests

# Import Executive Report Generator for DOCX output (Company-focused)
try:
    from executive_report_generator import (
        ExecutiveReportGenerator,
        create_assessment_from_osint_data,
        AssessmentData
    )
    DOCX_COMPANY_AVAILABLE = True
except ImportError:
    DOCX_COMPANY_AVAILABLE = False
    print("[!] executive_report_generator.py non trovato. Report DOCX aziende disabilitato.")

# Import Personal Vulnerability Report Generator (Person-focused with Claude AI)
try:
    from personal_vulnerability_report import (
        PersonalReportGenerator,
        ClaudePersonalAnalyzer,
        create_personal_assessment_from_osint,
        generate_personal_report,
        PersonalAssessmentData
    )
    DOCX_PERSONAL_AVAILABLE = True
except ImportError:
    DOCX_PERSONAL_AVAILABLE = False
    print("[!] personal_vulnerability_report.py non trovato. Report DOCX persone disabilitato.")

# Import Intelligence Report Framework (Dutch OSINT Guy Methodology)
try:
    from fidelinvestigator.intelligence_integration import (
        IntelligenceReportIntegration,
        generate_dutch_osint_report
    )
    INTELLIGENCE_REPORT_AVAILABLE = True
except ImportError:
    INTELLIGENCE_REPORT_AVAILABLE = False
    print("[!] Intelligence Report Framework non trovato. Report Intel disabilitato.")

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

class Config:
    """Configurazione centralizzata"""

    # Percorsi Kali Linux
    INPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/html"
    OUTPUT_DIR = "/home/kali/Scrivania/suka/FidelAI/reports"
    LOGO_PATH = None

    # API Keys (inserire le proprie chiavi)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

    # Modelli AI
    OPENAI_MODEL = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL = "claude-3-opus-20240229"
    PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"

    # Impostazioni
    ORGANIZATION_NAME = "FidelinvestigatorAI"
    VERBOSE = True
    AI_ENABLED = True


# ============================================================================
# CLIENT AI
# ============================================================================

class AIClients:
    """Gestione client AI centralizzata"""

    def __init__(self, config: Config):
        self.config = config
        self._openai_client = None
        self._anthropic_client = None

    @property
    def openai_client(self):
        if self._openai_client is None and self.config.OPENAI_API_KEY:
            self._openai_client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
        return self._openai_client

    @property
    def anthropic_client(self):
        if self._anthropic_client is None and self.config.ANTHROPIC_API_KEY:
            self._anthropic_client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
        return self._anthropic_client

    def query_perplexity(self, query: str, system_prompt: str = None) -> str:
        """Query Perplexity AI per ricerche OSINT in tempo reale"""
        if not self.config.PERPLEXITY_API_KEY:
            return self._fallback_analysis("perplexity", query)

        try:
            headers = {
                "Authorization": f"Bearer {self.config.PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": query})

            payload = {
                "model": self.config.PERPLEXITY_MODEL,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 4000
            }

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[!] Errore Perplexity: {e}")
            return self._fallback_analysis("perplexity", query)

    def query_openai(self, prompt: str, system_prompt: str = None) -> str:
        """Query OpenAI GPT-4 per correlazione dati"""
        if not self.openai_client:
            return self._fallback_analysis("openai", prompt)

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.openai_client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=messages,
                temperature=0.2,
                max_tokens=4000
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"[!] Errore OpenAI: {e}")
            return self._fallback_analysis("openai", prompt)

    def query_anthropic(self, prompt: str, system_prompt: str = None) -> str:
        """Query Anthropic Claude per profilazione psicologica"""
        if not self.anthropic_client:
            return self._fallback_analysis("anthropic", prompt)

        try:
            response = self.anthropic_client.messages.create(
                model=self.config.ANTHROPIC_MODEL,
                max_tokens=4000,
                system=system_prompt or "Sei un esperto analista investigativo.",
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text
        except Exception as e:
            print(f"[!] Errore Anthropic: {e}")
            return self._fallback_analysis("anthropic", prompt)

    def _fallback_analysis(self, provider: str, query: str) -> str:
        """Analisi fallback quando API non disponibile"""
        return f"[Analisi {provider} non disponibile - Configurare API key]"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PersonalInfo:
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None

@dataclass
class ContactInfo:
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)

@dataclass
class SocialMediaProfile:
    platform: str = ""
    username: str = ""
    url: str = ""
    followers: Optional[int] = None
    following: Optional[int] = None
    posts_count: Optional[int] = None
    bio: Optional[str] = None
    verified: bool = False
    created_date: Optional[str] = None
    last_activity: Optional[str] = None

@dataclass
class DataBreach:
    source: str = ""
    date: Optional[str] = None
    data_types: List[str] = field(default_factory=list)
    password_hash: Optional[str] = None
    password_plain: Optional[str] = None
    email: Optional[str] = None

@dataclass
class ExtractedData:
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    social_profiles: List[SocialMediaProfile] = field(default_factory=list)
    data_breaches: List[DataBreach] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    passwords: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    associated_domains: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# HTML PARSER
# ============================================================================

class OSINTHtmlParser:
    """Parser HTML per report OSINT"""

    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_PATTERN = re.compile(r'(?:\+?[0-9]{1,3}[-.\s]?)?(?:\([0-9]{1,4}\)[-.\s]?)?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}')
    IP_PATTERN = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    USERNAME_PATTERN = re.compile(r'@([a-zA-Z0-9_]{3,30})')

    SOCIAL_PLATFORMS = {
        'facebook.com': 'Facebook',
        'twitter.com': 'Twitter',
        'x.com': 'Twitter/X',
        'instagram.com': 'Instagram',
        'linkedin.com': 'LinkedIn',
        'tiktok.com': 'TikTok',
        'youtube.com': 'YouTube',
        'reddit.com': 'Reddit',
        'telegram': 'Telegram',
        'vk.com': 'VKontakte',
        'github.com': 'GitHub'
    }

    def parse_file(self, file_path: str) -> ExtractedData:
        """Parse un file HTML"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return self.parse_html(content)

    def parse_html(self, html_content: str) -> ExtractedData:
        """Parse contenuto HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        text_content = soup.get_text(separator=' ', strip=True)

        data = ExtractedData()

        # Estrai informazioni
        data.contact_info.emails = list(set(self.EMAIL_PATTERN.findall(text_content)))
        data.contact_info.phones = self._extract_phones(text_content)
        data.ip_addresses = list(set(self.IP_PATTERN.findall(text_content)))
        data.usernames = list(set(self.USERNAME_PATTERN.findall(text_content)))
        data.social_profiles = self._extract_social_profiles(soup, text_content)
        data.data_breaches = self._extract_breaches(soup, text_content)
        data.passwords = self._extract_passwords(soup, text_content)
        data.personal_info = self._extract_personal_info(soup, text_content)
        data.locations = self._extract_locations(text_content)

        return data

    def _extract_phones(self, text: str) -> List[str]:
        """Estrai numeri di telefono validi"""
        phones = []
        for match in self.PHONE_PATTERN.findall(text):
            cleaned = re.sub(r'[^\d+]', '', match)
            if 8 <= len(cleaned) <= 15:
                phones.append(match.strip())
        return list(set(phones))[:10]

    def _extract_social_profiles(self, soup: BeautifulSoup, text: str) -> List[SocialMediaProfile]:
        """Estrai profili social"""
        profiles = []

        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            for domain, platform in self.SOCIAL_PLATFORMS.items():
                if domain in href:
                    profiles.append(SocialMediaProfile(
                        platform=platform,
                        url=href,
                        username=self._extract_username_from_url(href)
                    ))

        return profiles

    def _extract_username_from_url(self, url: str) -> str:
        """Estrai username da URL"""
        parts = url.rstrip('/').split('/')
        if parts:
            return parts[-1]
        return ""

    def _extract_breaches(self, soup: BeautifulSoup, text: str) -> List[DataBreach]:
        """Estrai informazioni data breach"""
        breaches = []

        breach_keywords = ['breach', 'leak', 'dump', 'hack', 'compromised', 'exposed']

        for keyword in breach_keywords:
            if keyword.lower() in text.lower():
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            breach = DataBreach(
                                source=cells[0].get_text(strip=True),
                                date=cells[1].get_text(strip=True) if len(cells) > 1 else None
                            )
                            breaches.append(breach)

        return breaches

    def _extract_passwords(self, soup: BeautifulSoup, text: str) -> List[str]:
        """Estrai password esposte"""
        passwords = []

        password_patterns = [
            r'password[:\s]+([^\s<>"\']{4,30})',
            r'pass[:\s]+([^\s<>"\']{4,30})',
            r'pwd[:\s]+([^\s<>"\']{4,30})'
        ]

        for pattern in password_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            passwords.extend(matches)

        return list(set(passwords))

    def _extract_personal_info(self, soup: BeautifulSoup, text: str) -> PersonalInfo:
        """Estrai informazioni personali"""
        info = PersonalInfo()

        name_patterns = [
            r'(?:name|nome)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'(?:full name|nome completo)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info.full_name = match.group(1)
                break

        return info

    def _extract_locations(self, text: str) -> List[str]:
        """Estrai località geografiche"""
        locations = []

        location_patterns = [
            r'(?:location|località|city|città)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:country|paese)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]

        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            locations.extend(matches)

        return list(set(locations))


# ============================================================================
# AI-ENHANCED DATA ANALYZER
# ============================================================================

class AIDataAnalyzer:
    """Analizzatore dati con integrazione AI"""

    def __init__(self, ai_clients: AIClients):
        self.ai = ai_clients

    def analyze(self, data: ExtractedData) -> Dict[str, Any]:
        """Analisi completa con AI"""

        # Analisi base
        base_analysis = self._base_analysis(data)

        # Verifica OSINT con Perplexity
        print("[*] Verifica OSINT con Perplexity AI...")
        osint_verification = self._perplexity_osint_verification(data)

        # Correlazione dati con OpenAI
        print("[*] Correlazione dati con OpenAI GPT-4...")
        correlation_analysis = self._openai_correlation(data, base_analysis)

        return {
            "base_analysis": base_analysis,
            "osint_verification": osint_verification,
            "correlation_analysis": correlation_analysis,
            "digital_footprint_score": base_analysis.get("digital_footprint_score", 0),
            "exposure_level": base_analysis.get("exposure_level", "SCONOSCIUTO"),
            "ai_confidence": "ALTA" if self.ai.config.OPENAI_API_KEY else "LIMITATA"
        }

    def _base_analysis(self, data: ExtractedData) -> Dict[str, Any]:
        """Analisi base dei dati"""
        score = 0
        factors = []

        # Email exposure
        email_count = len(data.contact_info.emails)
        if email_count > 0:
            score += min(email_count * 10, 30)
            factors.append(f"{email_count} email esposte")

        # Social profiles
        social_count = len(data.social_profiles)
        if social_count > 0:
            score += min(social_count * 8, 25)
            factors.append(f"{social_count} profili social identificati")

        # Data breaches
        breach_count = len(data.data_breaches)
        if breach_count > 0:
            score += min(breach_count * 15, 30)
            factors.append(f"{breach_count} data breach rilevati")

        # Passwords
        password_count = len(data.passwords)
        if password_count > 0:
            score += min(password_count * 20, 40)
            factors.append(f"{password_count} password esposte - CRITICO")

        # Determine exposure level
        if score >= 80:
            level = "CRITICO"
        elif score >= 60:
            level = "ALTO"
        elif score >= 40:
            level = "MODERATO"
        elif score >= 20:
            level = "BASSO"
        else:
            level = "MINIMO"

        return {
            "digital_footprint_score": min(score, 100),
            "exposure_level": level,
            "risk_factors": factors,
            "data_summary": {
                "emails": email_count,
                "social_profiles": social_count,
                "breaches": breach_count,
                "passwords": password_count,
                "usernames": len(data.usernames),
                "ip_addresses": len(data.ip_addresses)
            }
        }

    def _perplexity_osint_verification(self, data: ExtractedData) -> Dict[str, Any]:
        """Verifica OSINT con Perplexity"""

        system_prompt = """CLASSIFICAZIONE: RISERVATO - INTELLIGENCE OPERATIVA

RUOLO: Sei un Senior Intelligence Analyst con 20+ anni di esperienza operativa presso:
- CIA (Directorate of Operations) - Raccolta HUMINT e analisi fonti aperte
- DIA (Defense Intelligence Agency) - Intelligence militare e geopolitica
- DEA (Intelligence Division) - Analisi reti criminali transnazionali
- ROS Carabinieri (Sezione Analisi) - Intelligence investigativa

COMPETENZE CERTIFICATE:
- OSINT (Open Source Intelligence) - Livello Avanzato NATO
- SOCMINT (Social Media Intelligence) - Certificazione IC
- Analisi fonti aperte e deep/dark web reconnaissance
- Verifica e validazione fonti multiple (Five Eyes standards)
- Threat Intelligence e indicatori di compromissione

PROTOCOLLO OPERATIVO:
1. RACCOLTA: Acquisire informazioni da fonti pubbliche verificabili
2. VALIDAZIONE: Cross-reference con database aperti e fonti multiple
3. ANALISI: Identificare pattern, connessioni e anomalie
4. CLASSIFICAZIONE: Categorizzare per rilevanza operativa

STANDARD REDAZIONALI:
- Linguaggio formale, tecnico e privo di ambiguità
- Ogni affermazione deve essere supportata da evidenze verificabili
- Indicare sempre il livello di confidenza (CONFERMATO/PROBABILE/POSSIBILE/NON VERIFICATO)
- NON formulare ipotesi non supportate dai dati
- Citare le fonti quando possibile
- Segnalare gap informativi e collection requirements

OUTPUT: Intelligence Brief strutturato in italiano, formato NATO STANAG."""

        # Prepara query
        targets = []
        if data.contact_info.emails:
            targets.append(f"Email: {', '.join(data.contact_info.emails[:3])}")
        if data.usernames:
            targets.append(f"Username: {', '.join(data.usernames[:5])}")
        if data.social_profiles:
            profiles = [f"{p.platform}: {p.username}" for p in data.social_profiles[:5]]
            targets.append(f"Social: {', '.join(profiles)}")

        if not targets:
            return {"status": "Dati insufficienti per verifica OSINT"}

        case_id = datetime.now().strftime('%Y%m%d%H%M%S')
        query = f"""═══════════════════════════════════════════════════════════════
OGGETTO: Richiesta Intelligence - Verifica OSINT Target
CLASSIFICAZIONE: RISERVATO
RIFERIMENTO OPERAZIONE: FIDEL-{case_id}
═══════════════════════════════════════════════════════════════

IDENTIFICATORI TARGET ACQUISITI:
{chr(10).join(targets)}

═══════════════════════════════════════════════════════════════
TASKINGS INTELLIGENCE:
═══════════════════════════════════════════════════════════════

1. IDENTITY VERIFICATION
   - Confermare correlazione tra identificatori acquisiti
   - Identificare alias, pseudonimi e identità alternative
   - Verificare autenticità e ownership profili social
   - Cross-reference con registri pubblici disponibili

2. DIGITAL RECONNAISSANCE
   - Mappare presenza online completa del target
   - Identificare piattaforme, servizi e community frequentate
   - Rilevare footprint su forum, board, darknet (se pubblicamente indicizzato)
   - Documentare digital assets e domini associati

3. EXPOSURE ASSESSMENT
   - Verificare presenza in data breach noti (pubblicamente documentati)
   - Identificare PII (Personally Identifiable Information) esposto
   - Valutare livello di esposizione e attack surface
   - Documentare credential leaks rilevati

4. NETWORK ANALYSIS
   - Identificare connessioni e associazioni digitali
   - Mappare rete di contatti e affiliazioni
   - Rilevare pattern di comunicazione e interazione
   - Documentare gruppi e community di appartenenza

5. THREAT INDICATORS
   - Segnalare red flags e anomalie comportamentali
   - Identificare indicatori di rischio
   - Valutare vettori di attacco probabili
   - Documentare warning signs rilevati

═══════════════════════════════════════════════════════════════
OUTPUT RICHIESTO: Intelligence Brief con sezioni numerate.
Indicare CONFIDENCE LEVEL per ogni finding.
═══════════════════════════════════════════════════════════════"""

        response = self.ai.query_perplexity(query, system_prompt)

        return {
            "verification_result": response,
            "timestamp": datetime.now().isoformat(),
            "sources_checked": "Web search in tempo reale"
        }

    def _openai_correlation(self, data: ExtractedData, base_analysis: Dict) -> Dict[str, Any]:
        """Correlazione dati avanzata con OpenAI"""

        system_prompt = """CLASSIFICAZIONE: RISERVATO - ALL-SOURCE INTELLIGENCE ANALYSIS

RUOLO: Sei un Senior Intelligence Analyst specializzato in All-Source Analysis presso:
- CIA (Directorate of Analysis) - Fusione multi-source intelligence
- DIA (Defense Intelligence Agency) - Strategic Intelligence Assessment
- FBI (Intelligence Branch) - Criminal Intelligence Analysis
- DEA (Office of National Security Intelligence) - Transnational Threat Analysis

SPECIALIZZAZIONI CERTIFICATE:
- All-Source Intelligence Fusion (IC Certification)
- Pattern Recognition e Link Analysis (i2 Analyst Notebook)
- Behavioral Analysis e Criminal Profiling
- Threat Assessment e Risk Quantification
- Timeline Reconstruction e Event Correlation
- Network Mapping e Association Matrix Analysis

METODOLOGIA ANALITICA (CIA Analytic Tradecraft Standards):
1. SOURCING: Valutare qualità, affidabilità e potenziali bias delle fonti
2. UNCERTAINTY: Quantificare e comunicare livelli di incertezza
3. ASSUMPTIONS: Identificare, esplicitare e testare assunzioni chiave
4. ALTERNATIVES: Considerare e valutare ipotesi alternative (ACH)
5. IMPLICATIONS: Valutare implicazioni operative e strategiche

FRAMEWORK ANALITICO:
- Applicare Structured Analytic Techniques (SAT)
- Implementare Analysis of Competing Hypotheses (ACH)
- Condurre Key Assumptions Check
- Applicare Devil's Advocacy quando appropriato

STANDARD REDAZIONALI IC:
- Formato: Intelligence Assessment (ICD 203 compliant)
- Linguaggio: Tecnico, preciso, inequivocabile, oggettivo
- Struttura: BLUF → Key Judgments → Evidence → Analysis → Implications
- Evidenze: Ogni conclusione deve essere tracciabile ai dati fonte
- Confidence Levels: HIGH/MODERATE/LOW con giustificazione esplicita
- Sourcing: Indicare sempre la fonte di ogni affermazione

RESTRIZIONI OPERATIVE:
- NON speculare oltre i dati disponibili
- NON omettere informazioni rilevanti per il quadro operativo
- NON minimizzare rischi o minacce identificate
- SEMPRE segnalare gap informativi e collection requirements"""

        # Prepara dati per analisi
        data_summary = f"""
DATI TARGET:

Email identificate: {', '.join(data.contact_info.emails) if data.contact_info.emails else 'Nessuna'}

Username identificati: {', '.join(data.usernames) if data.usernames else 'Nessuno'}

Profili Social:
{chr(10).join([f"- {p.platform}: {p.username} ({p.url})" for p in data.social_profiles]) if data.social_profiles else 'Nessuno'}

Data Breach:
{chr(10).join([f"- {b.source} ({b.date})" for b in data.data_breaches]) if data.data_breaches else 'Nessuno'}

Password Esposte: {len(data.passwords)} trovate
IP Addresses: {', '.join(data.ip_addresses) if data.ip_addresses else 'Nessuno'}
Località: {', '.join(data.locations) if data.locations else 'Nessuna'}

Score Impronta Digitale: {base_analysis.get('digital_footprint_score', 0)}/100
Livello Esposizione: {base_analysis.get('exposure_level', 'N/A')}
"""

        case_id = datetime.now().strftime('%Y%m%d%H%M%S')
        prompt = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           INTELLIGENCE ASSESSMENT REQUEST - ALL-SOURCE ANALYSIS              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CLASSIFICAZIONE: RISERVATO                      CASO: IA-{case_id}          ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
SEZIONE I - DATI ACQUISITI (Raw Intelligence)
═══════════════════════════════════════════════════════════════════════════════
{data_summary}

═══════════════════════════════════════════════════════════════════════════════
SEZIONE II - ANALYTIC TASKINGS
═══════════════════════════════════════════════════════════════════════════════

Condurre INTELLIGENCE ASSESSMENT completo secondo standard IC:

1. IDENTITY RESOLUTION & CORRELATION ANALYSIS
   a) Entity Resolution - Mappare tutti gli identificatori alla medesima entità
   b) Alias Detection - Identificare pseudonimi e identità alternative
   c) Cross-Platform Linkage - Correlare presenze su piattaforme diverse
   d) Confidence Assessment - Indicare livello certezza per ogni correlazione
   e) Anomaly Detection - Segnalare incongruenze o indicatori di deception

2. LINK ANALYSIS & NETWORK MAPPING
   a) Digital Network Structure - Mappare struttura relazioni online
   b) Association Typology - Classificare tipologie di relazioni identificate
   c) Centrality Metrics - Valutare ruolo e posizione nel network
   d) Hidden Connections - Identificare legami non immediatamente evidenti
   e) Communication Patterns - Analizzare pattern interazione

3. TEMPORAL ANALYSIS & TIMELINE RECONSTRUCTION
   a) Activity Timeline - Ricostruire cronologia attività digitali
   b) Behavioral Phases - Identificare fasi comportamentali distinte
   c) Exposure Events - Mappare eventi di compromissione
   d) Pattern Evolution - Analizzare evoluzione comportamenti nel tempo

4. THREAT ASSESSMENT & RISK QUANTIFICATION
   a) Vulnerability Profile - Mappare punti di esposizione critica
   b) Attack Surface Analysis - Quantificare superficie di attacco
   c) Threat Vectors - Identificare vettori attacco probabili (ranked)
   d) Risk Score - Assegnare risk score (1-10) con rationale dettagliato
   e) Threat Actor Interest - Valutare interesse potenziali attori malevoli

5. INTELLIGENCE GAPS & COLLECTION REQUIREMENTS
   a) Critical Missing Data - Dati mancanti essenziali
   b) Information Priorities - PIR (Priority Intelligence Requirements)
   c) Collection Strategies - Strategie raccolta suggerite
   d) Analytical Limitations - Limiti dell'analisi corrente

6. KEY JUDGMENTS & ACTIONABLE INTELLIGENCE
   a) Principal Findings - Evidenze principali (con confidence level)
   b) Analytical Conclusions - Conclusioni analitiche
   c) Operational Implications - Implicazioni per operazioni
   d) Investigative Recommendations - Raccomandazioni investigative prioritizzate

═══════════════════════════════════════════════════════════════════════════════
OUTPUT: Intelligence Assessment formale con Executive Summary (BLUF).
Applicare confidence levels: HIGH CONFIDENCE / MODERATE CONFIDENCE / LOW CONFIDENCE
═══════════════════════════════════════════════════════════════════════════════"""

        response = self.ai.query_openai(prompt, system_prompt)

        return {
            "correlation_result": response,
            "confidence_level": "ALTA" if self.ai.config.OPENAI_API_KEY else "LIMITATA",
            "analysis_depth": "Avanzata con GPT-4" if self.ai.config.OPENAI_API_KEY else "Base"
        }


# ============================================================================
# AI-ENHANCED PSYCHOLOGICAL PROFILER
# ============================================================================

class AIPsychologicalProfiler:
    """Profilazione psicologica avanzata con Claude"""

    def __init__(self, ai_clients: AIClients):
        self.ai = ai_clients

    def profile(self, data: ExtractedData, correlation_data: Dict) -> Dict[str, Any]:
        """Genera profilo psicologico completo con Claude"""

        print("[*] Profilazione psicologica con Anthropic Claude...")

        system_prompt = """CLASSIFICAZIONE: RISERVATO - BEHAVIORAL ANALYSIS UNIT

RUOLO: Sei un Senior Behavioral Analyst e Criminal Profiler con esperienza operativa presso:
- FBI (Behavioral Analysis Unit - BAU) - 15 anni esperienza profiling seriale
- CIA (Directorate of Operations, Psychological Profiles Division) - 10 anni
- EUROPOL (European Serious Organised Crime Centre) - 8 anni analisi comportamentale
- ROS Carabinieri (Sezione Criminalistica, Consulente Profiling) - 5 anni
- DIA (Behavioral Threat Assessment Unit) - 7 anni

CERTIFICAZIONI E QUALIFICAZIONI:
- Ph.D. Forensic Psychology - Georgetown University
- Criminal Profiling Certification - FBI National Academy, Quantico
- Behavioral Threat Assessment Professional (BTAP) - ASIS International
- Dark Triad Assessment Certification - Clinical Psychology Board
- Digital Behavioral Analysis - SANS Institute Certification
- Investigative Psychology - University of Liverpool

FRAMEWORK METODOLOGICI APPLICATI:
1. BIG FIVE PERSONALITY MODEL (OCEAN/NEO-PI-R)
   - Valutazione tratti attraverso indicatori comportamentali digitali
   - Correlazione scientifica comportamenti online-struttura personalità
   - Baseline comparison con popolazioni di riferimento

2. BEHAVIORAL EVIDENCE ANALYSIS (BEA) - Turvey Method
   - Victimology digitale e vulnerability assessment
   - Pattern comportamentali ricorrenti e signature behaviors
   - Modus operandi vs signature distinction

3. THREAT ASSESSMENT FRAMEWORK (FBI/Secret Service Model)
   - Pathway to Violence indicators
   - Grievance-based threat evaluation
   - Leakage behavior detection and analysis
   - Fixation and focus indicators

4. DARK TRIAD SCREENING PROTOCOL
   - Narcissistic indicators in self-presentation
   - Machiavellian patterns in digital interactions
   - Psychopathic callousness indicators
   - Subclinical trait assessment

PROTOCOLLO VALUTAZIONE BAU:
- Analizzare ESCLUSIVAMENTE evidenze comportamentali documentate
- Applicare differential diagnosis comportamentale
- Evitare confirmation bias attraverso ACH
- Quantificare confidence level per ogni assessment
- Documentare limitazioni metodologiche
- Considerare alternative hypothesis

STANDARD REPORT BAU:
- Linguaggio clinico-forense rigoroso
- Struttura: Assessment → Behavioral Evidence → Analysis → Conclusions
- Ogni conclusione deve citare l'evidenza comportamentale specifica
- Includere diagnostic differentials
- Fornire actionable behavioral indicators per investigatori"""

        # Prepara dati comportamentali
        behavioral_data = self._prepare_behavioral_data(data)

        case_id = datetime.now().strftime('%Y%m%d%H%M%S')
        prompt = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          BEHAVIORAL ANALYSIS UNIT - PSYCHOLOGICAL ASSESSMENT REQUEST         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CLASSIFICAZIONE: RISERVATO - PROFILING OPERATIVO                            ║
║  TIPO DOCUMENTO: Profilo Psicologico-Comportamentale                         ║
║  RIFERIMENTO CASO: BAU-{case_id}                                             ║
║  UNITÀ RICHIEDENTE: FidelinvestigatorAI - OSINT Division                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
SEZIONE A - BEHAVIORAL INDICATORS (Digital Footprint Evidence)
═══════════════════════════════════════════════════════════════════════════════

{behavioral_data}

═══════════════════════════════════════════════════════════════════════════════
SEZIONE B - CORRELATION INTELLIGENCE
═══════════════════════════════════════════════════════════════════════════════

{json.dumps(correlation_data.get('base_analysis', {}), indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════════════════════
SEZIONE C - PROFILING TASKINGS
═══════════════════════════════════════════════════════════════════════════════

Elaborare COMPREHENSIVE PSYCHOLOGICAL PROFILE secondo standard BAU:

1. PERSONALITY ASSESSMENT - BIG FIVE MODEL (OCEAN/NEO-PI-R)
   Per ciascun tratto fornire:
   ┌─────────────────────────────────────────────────────────────────────┐
   │ TRAIT          │ SCORE (0-100) │ CONFIDENCE │ BEHAVIORAL EVIDENCE  │
   ├─────────────────────────────────────────────────────────────────────┤
   │ a) OPENNESS (Apertura all'esperienza)                              │
   │ b) CONSCIENTIOUSNESS (Coscienziosità/Organizzazione)               │
   │ c) EXTRAVERSION (Estroversione/Socievolezza)                       │
   │ d) AGREEABLENESS (Amicalità/Cooperatività)                         │
   │ e) NEUROTICISM (Instabilità emotiva/Reattività)                    │
   └─────────────────────────────────────────────────────────────────────┘

   Indicatori da valutare:
   - Platform choice patterns (tipologia piattaforme frequentate)
   - Username construction patterns (struttura e significato username)
   - Exposure frequency and nature (frequenza e tipo esposizioni)
   - Digital hygiene indicators (attenzione alla sicurezza)

2. BEHAVIORAL PATTERN ANALYSIS
   a) Communication Style Profile
      - Linguistic markers e registro comunicativo
      - Assertiveness vs passivity indicators
      - Formality spectrum positioning

   b) Decision-Making Patterns
      - Risk tolerance indicators
      - Impulsivity vs deliberation markers
      - Consistency in digital choices

   c) Digital Presence Management
      - Privacy consciousness level
      - Self-presentation strategy
      - Reputation management indicators

   d) Temporal Behavioral Patterns
      - Activity timing patterns
      - Consistency vs volatility
      - Adaptation indicators

3. VULNERABILITY ASSESSMENT (Social Engineering Susceptibility)
   a) Psychological Vulnerabilities
      - Ego-based exploitation vectors
      - Authority compliance indicators
      - Social proof susceptibility
      - Scarcity/urgency response patterns

   b) Cognitive Vulnerabilities
      - Confirmation bias indicators
      - Trust calibration assessment
      - Critical thinking markers

   c) Emotional Vulnerabilities
      - Stress response patterns
      - Emotional regulation indicators
      - Trigger identification

4. DARK TRIAD SCREENING
   ┌─────────────────────────────────────────────────────────────────────┐
   │ TRAIT              │ SCORE (0-100) │ CLINICAL THRESHOLD │ EVIDENCE │
   ├─────────────────────────────────────────────────────────────────────┤
   │ a) NARCISSISM      │               │ >70 = Elevated     │          │
   │ b) MACHIAVELLIANISM│               │ >70 = Elevated     │          │
   │ c) PSYCHOPATHY     │               │ >70 = Elevated     │          │
   └─────────────────────────────────────────────────────────────────────┘
   Overall Dark Triad Risk Assessment: [LOW/MODERATE/ELEVATED/HIGH]

5. THREAT ASSESSMENT (FBI/Secret Service Framework)
   a) Threat Classification
      - Level: [MINIMAL/LOW/MODERATE/HIGH/SEVERE]
      - Confidence: [HIGH/MODERATE/LOW]

   b) Predictability Assessment
      - Behavioral predictability score (1-10)
      - Pattern stability indicators
      - Deviation likelihood

   c) Escalation Potential
      - Risk factors present
      - Protective factors present
      - Net escalation risk

   d) Key Warning Indicators
      - Red flags identificati
      - Monitoring priorities
      - Intervention triggers

6. INVESTIGATIVE IMPLICATIONS & RECOMMENDATIONS
   a) Interview/Interrogation Strategy
      - Recommended approach style
      - Rapport-building vectors
      - Potential resistance points

   b) Elicitation Vulnerabilities
      - Exploitable psychological levers
      - Recommended elicitation techniques
      - Counter-resistance strategies

   c) Monitoring Priorities
      - Key behavioral indicators to track
      - Early warning signals
      - Escalation markers

7. PROFILER CONCLUSIONS
   a) Executive Behavioral Summary (5-7 punti chiave)
   b) Confidence Assessment e Methodology Limitations
   c) Differential Diagnostic Considerations
   d) Collection Requirements for Enhanced Assessment

═══════════════════════════════════════════════════════════════════════════════
OUTPUT: BAU Psychological Profile - Formato Operativo
Applicare rigorosi standard clinico-forensi.
═══════════════════════════════════════════════════════════════════════════════"""

        response = self.ai.query_anthropic(prompt, system_prompt)

        # Estrai anche analisi base
        base_profile = self._base_psychological_analysis(data)

        return {
            "ai_profile": response,
            "base_metrics": base_profile,
            "profiler_confidence": "ALTA" if self.ai.config.ANTHROPIC_API_KEY else "LIMITATA",
            "methodology": "Analisi Claude + metriche comportamentali"
        }

    def _prepare_behavioral_data(self, data: ExtractedData) -> str:
        """Prepara dati comportamentali per analisi"""

        lines = []

        # Piattaforme social
        if data.social_profiles:
            platforms = [p.platform for p in data.social_profiles]
            lines.append(f"Piattaforme utilizzate: {', '.join(set(platforms))}")
            lines.append(f"Numero profili: {len(data.social_profiles)}")

        # Username pattern
        if data.usernames:
            lines.append(f"Username identificati: {', '.join(data.usernames)}")

            # Analizza pattern
            has_numbers = any(re.search(r'\d', u) for u in data.usernames)
            has_special = any(re.search(r'[_\-.]', u) for u in data.usernames)
            avg_length = sum(len(u) for u in data.usernames) / len(data.usernames)

            lines.append(f"Pattern username: numeri={has_numbers}, caratteri_speciali={has_special}, lunghezza_media={avg_length:.1f}")

        # Email pattern
        if data.contact_info.emails:
            lines.append(f"Email: {', '.join(data.contact_info.emails)}")

            # Analizza domini
            domains = [e.split('@')[1] for e in data.contact_info.emails if '@' in e]
            lines.append(f"Domini email: {', '.join(set(domains))}")

        # Esposizioni
        lines.append(f"Numero data breach: {len(data.data_breaches)}")
        lines.append(f"Password esposte: {len(data.passwords)}")

        # Password pattern (senza mostrare le password)
        if data.passwords:
            avg_pwd_len = sum(len(p) for p in data.passwords) / len(data.passwords)
            has_complex = any(re.search(r'[!@#$%^&*]', p) for p in data.passwords)
            lines.append(f"Pattern password: lunghezza_media={avg_pwd_len:.1f}, complessità={'alta' if has_complex else 'bassa'}")

        return '\n'.join(lines)

    def _base_psychological_analysis(self, data: ExtractedData) -> Dict[str, Any]:
        """Analisi psicologica base senza AI"""

        # Big Five estimation
        big_five = {
            "openness": 50,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50
        }

        # Adjust based on data
        social_count = len(data.social_profiles)
        if social_count > 5:
            big_five["extraversion"] += 20
            big_five["openness"] += 10
        elif social_count < 2:
            big_five["extraversion"] -= 15

        breach_count = len(data.data_breaches)
        if breach_count > 3:
            big_five["conscientiousness"] -= 15
            big_five["neuroticism"] += 10

        password_count = len(data.passwords)
        if password_count > 0:
            big_five["conscientiousness"] -= 20

        # Normalize
        for key in big_five:
            big_five[key] = max(0, min(100, big_five[key]))

        return {
            "big_five": big_five,
            "risk_profile": {
                "privacy_awareness": "BASSA" if breach_count > 2 else "MEDIA" if breach_count > 0 else "ALTA",
                "security_consciousness": "CRITICA" if password_count > 0 else "BASSA" if breach_count > 2 else "MEDIA"
            }
        }


# ============================================================================
# PASSWORD ANALYZER
# ============================================================================

class PasswordAnalyzer:
    """Analizzatore pattern password"""

    KEYBOARD_PATTERNS = [
        'qwerty', 'asdfgh', 'zxcvbn', 'qwertz', 'azerty',
        '123456', '654321', '111111', '000000', 'abcdef'
    ]

    COMMON_WORDS = [
        'password', 'admin', 'login', 'welcome', 'master',
        'letmein', 'dragon', 'monkey', 'shadow', 'sunshine'
    ]

    def analyze(self, passwords: List[str], personal_info: PersonalInfo) -> Dict[str, Any]:
        """Analizza password per pattern"""

        if not passwords:
            return {"status": "Nessuna password da analizzare"}

        analyses = []
        for pwd in passwords:
            analysis = self._analyze_single(pwd, personal_info)
            analyses.append(analysis)

        # Aggregate statistics
        avg_strength = sum(a.get('strength_score', 0) for a in analyses) / len(analyses)
        patterns_found = []
        for a in analyses:
            patterns_found.extend(a.get('patterns', []))

        return {
            "individual_analyses": analyses,
            "aggregate": {
                "total_passwords": len(passwords),
                "average_strength": round(avg_strength, 1),
                "common_patterns": list(set(patterns_found)),
                "overall_security": self._overall_security_level(avg_strength)
            },
            "recommendations": self._generate_recommendations(analyses)
        }

    def _analyze_single(self, password: str, personal_info: PersonalInfo) -> Dict[str, Any]:
        """Analizza singola password"""

        patterns = []
        score = 100

        # Length check
        length = len(password)
        if length < 8:
            score -= 30
            patterns.append("troppo_corta")
        elif length < 12:
            score -= 10

        # Complexity
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        complexity = sum([has_upper, has_lower, has_digit, has_special])
        if complexity < 2:
            score -= 25
            patterns.append("bassa_complessità")
        elif complexity < 3:
            score -= 10

        # Keyboard patterns
        pwd_lower = password.lower()
        for pattern in self.KEYBOARD_PATTERNS:
            if pattern in pwd_lower:
                score -= 20
                patterns.append(f"keyboard_pattern:{pattern}")
                break

        # Common words
        for word in self.COMMON_WORDS:
            if word in pwd_lower:
                score -= 25
                patterns.append(f"parola_comune:{word}")
                break

        # Personal info
        if personal_info.first_name and personal_info.first_name.lower() in pwd_lower:
            score -= 30
            patterns.append("contiene_nome")

        # Sequential/repeated
        if re.search(r'(.)\1{2,}', password):
            score -= 15
            patterns.append("caratteri_ripetuti")

        return {
            "password_masked": password[:2] + "*" * (len(password) - 4) + password[-2:] if len(password) > 4 else "****",
            "length": length,
            "complexity": complexity,
            "strength_score": max(0, score),
            "patterns": patterns,
            "security_level": self._security_level(max(0, score))
        }

    def _security_level(self, score: int) -> str:
        """Determina livello sicurezza"""
        if score >= 80:
            return "ECCELLENTE"
        elif score >= 60:
            return "BUONO"
        elif score >= 40:
            return "MEDIO"
        elif score >= 20:
            return "BASSO"
        else:
            return "CRITICO"

    def _overall_security_level(self, avg_score: float) -> str:
        """Livello sicurezza complessivo"""
        return self._security_level(int(avg_score))

    def _generate_recommendations(self, analyses: List[Dict]) -> List[str]:
        """Genera raccomandazioni"""
        recommendations = []

        all_patterns = []
        for a in analyses:
            all_patterns.extend(a.get('patterns', []))

        if 'troppo_corta' in all_patterns:
            recommendations.append("Utilizzare password di almeno 12 caratteri")
        if 'bassa_complessità' in all_patterns:
            recommendations.append("Includere maiuscole, numeri e caratteri speciali")
        if any('keyboard_pattern' in p for p in all_patterns):
            recommendations.append("Evitare sequenze di tastiera prevedibili")
        if any('parola_comune' in p for p in all_patterns):
            recommendations.append("Non utilizzare parole comuni o prevedibili")
        if 'contiene_nome' in all_patterns:
            recommendations.append("Non includere informazioni personali nelle password")

        return recommendations


# ============================================================================
# SECURITY ASSESSOR
# ============================================================================

class SecurityAssessor:
    """Valutazione sicurezza complessiva"""

    def assess(self, data: ExtractedData, analysis: Dict, password_analysis: Dict) -> Dict[str, Any]:
        """Valutazione sicurezza completa"""

        vulnerabilities = []
        threats = []
        score = 100

        # Email exposure
        if data.contact_info.emails:
            vulnerabilities.append({
                "type": "EMAIL_EXPOSURE",
                "severity": "MEDIA",
                "count": len(data.contact_info.emails),
                "description": f"{len(data.contact_info.emails)} indirizzi email esposti pubblicamente"
            })
            score -= len(data.contact_info.emails) * 5

        # Data breaches
        if data.data_breaches:
            vulnerabilities.append({
                "type": "DATA_BREACH",
                "severity": "ALTA",
                "count": len(data.data_breaches),
                "description": f"Presente in {len(data.data_breaches)} data breach noti"
            })
            score -= len(data.data_breaches) * 15
            threats.append("Credential Stuffing Attack")

        # Password exposure
        if data.passwords:
            vulnerabilities.append({
                "type": "PASSWORD_EXPOSURE",
                "severity": "CRITICA",
                "count": len(data.passwords),
                "description": f"{len(data.passwords)} password esposte in chiaro"
            })
            score -= 30
            threats.append("Account Takeover")
            threats.append("Identity Theft")

        # Social profiles
        if len(data.social_profiles) > 5:
            vulnerabilities.append({
                "type": "LARGE_DIGITAL_FOOTPRINT",
                "severity": "MEDIA",
                "count": len(data.social_profiles),
                "description": "Ampia presenza social aumenta superficie di attacco"
            })
            score -= 10
            threats.append("Social Engineering")
            threats.append("Spear Phishing")

        # Calculate grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return {
            "security_score": max(0, score),
            "security_grade": grade,
            "vulnerabilities": vulnerabilities,
            "threats": list(set(threats)),
            "risk_level": analysis.get('base_analysis', {}).get('exposure_level', 'SCONOSCIUTO'),
            "recommendations": self._generate_recommendations(vulnerabilities, threats)
        }

    def _generate_recommendations(self, vulnerabilities: List, threats: List) -> List[str]:
        """Genera raccomandazioni sicurezza"""
        recommendations = []

        vuln_types = [v['type'] for v in vulnerabilities]

        if 'PASSWORD_EXPOSURE' in vuln_types:
            recommendations.append("URGENTE: Cambiare immediatamente tutte le password esposte")
            recommendations.append("Attivare autenticazione a due fattori su tutti gli account")

        if 'DATA_BREACH' in vuln_types:
            recommendations.append("Verificare e aggiornare credenziali di tutti gli account compromessi")
            recommendations.append("Monitorare attività sospette sugli account")

        if 'Social Engineering' in threats:
            recommendations.append("Aumentare consapevolezza su tecniche di social engineering")
            recommendations.append("Limitare informazioni personali condivise pubblicamente")

        if 'EMAIL_EXPOSURE' in vuln_types:
            recommendations.append("Utilizzare email alias per servizi diversi")
            recommendations.append("Implementare filtri anti-phishing avanzati")

        return recommendations


# ============================================================================
# AI-ENHANCED REPORT GENERATOR
# ============================================================================

class AIReportGenerator:
    """Generatore report PDF con narrazione AI"""

    def __init__(self, ai_clients: AIClients):
        self.ai = ai_clients
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Configura stili documento"""

        # Titolo principale
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            fontName='Times-Bold',
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=HexColor('#1a1a2e')
        ))

        # Sottotitolo
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            fontName='Times-Roman',
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=HexColor('#4a4a4a')
        ))

        # Capitolo
        self.styles.add(ParagraphStyle(
            name='Chapter',
            fontName='Times-Bold',
            fontSize=16,
            spaceBefore=25,
            spaceAfter=15,
            textColor=HexColor('#1a1a2e')
        ))

        # Paragrafo
        self.styles.add(ParagraphStyle(
            name='Section',
            fontName='Times-Bold',
            fontSize=13,
            spaceBefore=15,
            spaceAfter=10,
            textColor=HexColor('#2d2d2d')
        ))

        # Corpo testo
        self.styles.add(ParagraphStyle(
            name='BodyText15',
            fontName='Times-Roman',
            fontSize=11,
            leading=16.5,  # 1.5 line spacing
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))

        # Testo evidenziato
        self.styles.add(ParagraphStyle(
            name='Highlight',
            fontName='Times-Bold',
            fontSize=11,
            leading=16.5,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            backColor=HexColor('#fff3cd')
        ))

        # Lista
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            fontName='Times-Roman',
            fontSize=11,
            leading=16.5,
            leftIndent=20,
            spaceAfter=5
        ))

    def generate(self, data: ExtractedData, analysis: Dict, psych_profile: Dict,
                 password_analysis: Dict, security_assessment: Dict,
                 output_path: str, logo_path: str = None) -> str:
        """Genera report PDF completo"""

        print("[*] Generazione narrativa report con Claude...")

        # Genera narrativa professionale con Claude
        narrative = self._generate_narrative(data, analysis, psych_profile, security_assessment)

        # Crea documento
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )

        story = []

        # Header con logo
        story.extend(self._create_header(logo_path))

        # Capitolo 1: Introduzione
        story.extend(self._chapter_introduction())

        # Capitolo 2: Executive Summary
        story.extend(self._chapter_executive_summary(analysis, security_assessment))

        # Capitolo 3: Dati Identificativi
        story.extend(self._chapter_identification(data))

        # Capitolo 4: Analisi Correlazione (AI)
        story.extend(self._chapter_correlation(analysis, narrative))

        # Capitolo 5: Profilo Psicologico (AI)
        story.extend(self._chapter_psychological(psych_profile))

        # Capitolo 6: Analisi Password
        story.extend(self._chapter_passwords(password_analysis))

        # Capitolo 7: Valutazione Sicurezza
        story.extend(self._chapter_security(security_assessment))

        # Capitolo 8: Conclusioni (AI)
        story.extend(self._chapter_conclusions(narrative, security_assessment))

        # Build PDF
        doc.build(story)

        return output_path

    def _generate_narrative(self, data: ExtractedData, analysis: Dict,
                           psych_profile: Dict, security: Dict) -> Dict[str, str]:
        """Genera narrativa professionale con Claude"""

        system_prompt = """CLASSIFICAZIONE: RISERVATO - INTELLIGENCE PRODUCT FINAL

RUOLO: Sei un Senior Intelligence Report Writer con esperienza presso:
- CIA (Directorate of Analysis) - Redazione President's Daily Brief e NIE
- DIA (Defense Intelligence Agency) - National Intelligence Estimates
- DEA (Intelligence Division) - Strategic Threat Assessments
- ROS Carabinieri - Rapporti Investigativi per Autorità Giudiziaria
- EUROPOL - Serious and Organised Crime Threat Assessments (SOCTA)

ESPERIENZA REDAZIONALE (25+ anni):
- Redazione prodotti intelligence classificati per decisori di massimo livello
- Briefing per Ministri, Comandanti, Direttori Agenzie
- Standardizzazione secondo Intelligence Community Directives (ICD 203, 206)
- Formazione analisti su IC Analytic Standards e Writing Standards
- Peer review prodotti NIE e PDB

STANDARD REDAZIONALI INTELLIGENCE COMMUNITY:
1. BLUF (Bottom Line Up Front)
   - Key judgment in apertura
   - Conclusioni prima delle evidenze

2. SOURCING TRANSPARENCY
   - Ogni affermazione attribuita a fonte specifica
   - Distinzione chiara tra fatto e valutazione analitica

3. CONFIDENCE LEVELS (ICD 203)
   - HIGH CONFIDENCE: Evidenze multiple e convergenti
   - MODERATE CONFIDENCE: Evidenze credibili ma incomplete
   - LOW CONFIDENCE: Evidenze frammentarie o contrastanti

4. ESTIMATIVE LANGUAGE (ICD 203)
   - "We assess" per giudizi analitici
   - "We judge" per valutazioni ad alta confidenza
   - Evitare ambiguità lessicali

5. ALTERNATIVE ANALYSIS
   - Considerare ipotesi alternative
   - Documentare uncertainties
   - Segnalare dissenting views

STILE LINGUISTICO MANDATORIO:
- Formale, autorevole, definitivo
- Privo di ambiguità interpretative
- Frasi concise, struttura attiva
- Terminologia tecnico-operativa
- NESSUNA speculazione non supportata
- NESSUN linguaggio emotivo o sensazionalistico
- Italiano formale, registro istituzionale

NOTA: Il documento sarà utilizzato per decisioni operative ad alto livello.
L'accuratezza, la chiarezza e l'autorevolezza sono imperativi assoluti."""

        # Prepara sommario dati
        data_summary = f"""
DATI INVESTIGAZIONE:

Email: {', '.join(data.contact_info.emails) if data.contact_info.emails else 'N/A'}
Username: {', '.join(data.usernames) if data.usernames else 'N/A'}
Profili Social: {len(data.social_profiles)}
Data Breach: {len(data.data_breaches)}
Password Esposte: {len(data.passwords)}
Score Esposizione: {analysis.get('base_analysis', {}).get('digital_footprint_score', 0)}/100
Livello Rischio: {analysis.get('base_analysis', {}).get('exposure_level', 'N/A')}
Security Grade: {security.get('security_grade', 'N/A')}
"""

        case_id = datetime.now().strftime('%Y%m%d%H%M%S')
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')

        prompt = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               INTELLIGENCE PRODUCT REQUEST - FINAL ASSESSMENT                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CLASSIFICAZIONE: RISERVATO                                                  ║
║  TIPO: Intelligence Assessment Report - Final Product                        ║
║  DATA: {date_str}                                                            ║
║  RIFERIMENTO: CASE-{case_id}                                                 ║
║  DISTRIBUZIONE: Decisori Operativi                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
SEZIONE I - CONSOLIDATED INTELLIGENCE INPUT
═══════════════════════════════════════════════════════════════════════════════
{data_summary}

═══════════════════════════════════════════════════════════════════════════════
SEZIONE II - INTELLIGENCE PRODUCT REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

Redigere FINAL INTELLIGENCE ASSESSMENT in formato JSON strutturato:

{{
  "executive_summary": "
    [BLUF - 4-5 paragrafi formali]

    SCOPE: Definizione ambito e obiettivo dell'assessment

    KEY JUDGMENTS:
    Presentare i 3-5 giudizi analitici principali, ciascuno con:
    - Statement chiaro e definitivo
    - Confidence level (HIGH/MODERATE/LOW)
    - Evidenza principale a supporto

    PRINCIPAL FINDINGS:
    - Finding 1: [descrizione] (Confidence: X)
    - Finding 2: [descrizione] (Confidence: X)
    - Finding 3: [descrizione] (Confidence: X)

    RISK ASSESSMENT:
    Valutazione sintetica del livello di rischio complessivo con rationale

    PRIORITY ACTIONS:
    Top 3 azioni raccomandate in ordine di priorità
  ",

  "detailed_analysis": "
    [5-7 paragrafi - Analisi Dettagliata secondo standard IC]

    SECTION I - SUBJECT OVERVIEW
    Presentazione formale del target investigativo, contesto operativo,
    e scope dell'investigazione condotta.

    SECTION II - DIGITAL FOOTPRINT ANALYSIS
    Analisi dettagliata della presenza digitale del soggetto:
    - Identità digitali confermate
    - Piattaforme e servizi utilizzati
    - Esposizione credenziali e dati sensibili
    - Attack surface assessment

    SECTION III - CORRELATION ANALYSIS
    Narrazione della correlazione tra data points:
    - Identity resolution findings
    - Cross-platform linkages
    - Pattern identificati
    - Anomalie e red flags

    SECTION IV - BEHAVIORAL ASSESSMENT INTEGRATION
    Sintesi del profilo comportamentale e implicazioni operative

    SECTION V - THREAT LANDSCAPE
    Minacce identificate, vettori di attacco probabili,
    e threat actors potenzialmente interessati

    SECTION VI - VULNERABILITY MATRIX
    Mappatura vulnerabilità con prioritizzazione e
    potential impact assessment
  ",

  "conclusions": "
    [4-5 paragrafi - Conclusioni Operative]

    KEY ANALYTICAL JUDGMENTS:
    Giudizi analitici finali con confidence levels espliciti
    e sourcing summary

    STRATEGIC IMPLICATIONS:
    Implicazioni di medio-lungo termine per le operazioni

    INTELLIGENCE GAPS:
    Lacune informative critiche identificate e
    Priority Intelligence Requirements (PIR)

    COLLECTION REQUIREMENTS:
    Requisiti di raccolta per completare il quadro

    OPERATIONAL RECOMMENDATIONS:
    1. [Raccomandazione prioritaria 1]
    2. [Raccomandazione prioritaria 2]
    3. [Raccomandazione prioritaria 3]

    MONITORING REQUIREMENTS:
    Indicatori chiave da monitorare e trigger per re-assessment

    DISSEMINATION NOTE:
    Note sulla distribuzione e handling del prodotto
  "
}}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT: Restituire ESCLUSIVAMENTE JSON valido.
Applicare rigorosi standard IC per redazione prodotti intelligence finali.
Linguaggio: Italiano formale istituzionale.
═══════════════════════════════════════════════════════════════════════════════"""

        response = self.ai.query_anthropic(prompt, system_prompt)

        # Parse response
        try:
            # Try to extract JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # Fallback
        return {
            "executive_summary": response[:500] if response else "Analisi AI non disponibile.",
            "correlation_narrative": "Vedere sezione dati per dettagli correlazione.",
            "conclusions": "Conclusioni basate sui dati raccolti."
        }

    def _create_header(self, logo_path: str = None) -> List:
        """Crea header documento"""
        elements = []

        # Data e ora
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y - %H:%M")

        # Tabella header
        header_data = [[
            "",
            Paragraph("REPORT INFO INVESTIGATIVO", self.styles['MainTitle']),
            ""
        ]]

        header_table = Table(header_data, colWidths=[4*cm, 9*cm, 4*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 5*mm))

        # Sottotitolo con data
        elements.append(Paragraph(f"Generato il {date_str}", self.styles['SubTitle']))
        elements.append(Paragraph("FidelinvestigatorAI - Sistema di Intelligence OSINT", self.styles['SubTitle']))

        elements.append(Spacer(1, 15*mm))

        return elements

    def _chapter_introduction(self) -> List:
        """Capitolo 1: Introduzione OSINT"""
        elements = []

        elements.append(Paragraph("CAPITOLO 1 - INTRODUZIONE", self.styles['Chapter']))

        intro_text = """
        Il presente report è stato redatto utilizzando metodologie di Open Source Intelligence (OSINT),
        ovvero tecniche di raccolta e analisi di informazioni provenienti da fonti pubblicamente accessibili.
        L'OSINT rappresenta una disciplina fondamentale nell'ambito dell'intelligence moderna, permettendo
        di costruire profili informativi dettagliati attraverso l'aggregazione e la correlazione di dati
        disponibili nel dominio pubblico.
        """
        elements.append(Paragraph(intro_text.strip(), self.styles['BodyText15']))

        methodology_text = """
        La metodologia adottata prevede l'analisi sistematica di diverse categorie di fonti:
        social network, database pubblici, registri web, e archivi di sicurezza informatica.
        I dati raccolti vengono successivamente processati attraverso algoritmi di correlazione
        e sistemi di intelligenza artificiale per identificare pattern significativi e costruire
        un quadro informativo coerente e attendibile.
        """
        elements.append(Paragraph(methodology_text.strip(), self.styles['BodyText15']))

        disclaimer_text = """
        Le informazioni contenute in questo documento derivano esclusivamente da fonti pubbliche
        e sono state elaborate nel rispetto delle normative vigenti in materia di privacy e
        protezione dei dati personali. Il report ha finalità esclusivamente informative e
        investigative nell'ambito delle attività autorizzate.
        """
        elements.append(Paragraph(disclaimer_text.strip(), self.styles['BodyText15']))

        return elements

    def _chapter_executive_summary(self, analysis: Dict, security: Dict) -> List:
        """Capitolo 2: Executive Summary"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("CAPITOLO 2 - EXECUTIVE SUMMARY", self.styles['Chapter']))

        # Metriche chiave
        base = analysis.get('base_analysis', {})

        elements.append(Paragraph("2.1 Metriche Chiave", self.styles['Section']))

        metrics = [
            f"• Digital Footprint Score: {base.get('digital_footprint_score', 0)}/100",
            f"• Livello di Esposizione: {base.get('exposure_level', 'N/A')}",
            f"• Security Grade: {security.get('security_grade', 'N/A')}",
            f"• Vulnerabilità Identificate: {len(security.get('vulnerabilities', []))}",
            f"• Minacce Attive: {len(security.get('threats', []))}"
        ]

        for metric in metrics:
            elements.append(Paragraph(metric, self.styles['BulletPoint']))

        # Risk factors
        risk_factors = base.get('risk_factors', [])
        if risk_factors:
            elements.append(Paragraph("2.2 Fattori di Rischio Principali", self.styles['Section']))
            for factor in risk_factors:
                elements.append(Paragraph(f"• {factor}", self.styles['BulletPoint']))

        return elements

    def _chapter_identification(self, data: ExtractedData) -> List:
        """Capitolo 3: Dati Identificativi"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("CAPITOLO 3 - DATI IDENTIFICATIVI", self.styles['Chapter']))

        # Email
        if data.contact_info.emails:
            elements.append(Paragraph("3.1 Indirizzi Email", self.styles['Section']))
            for email in data.contact_info.emails:
                elements.append(Paragraph(f"• {email}", self.styles['BulletPoint']))

        # Usernames
        if data.usernames:
            elements.append(Paragraph("3.2 Username Identificati", self.styles['Section']))
            for username in data.usernames:
                elements.append(Paragraph(f"• @{username}", self.styles['BulletPoint']))

        # Social profiles
        if data.social_profiles:
            elements.append(Paragraph("3.3 Profili Social Media", self.styles['Section']))
            for profile in data.social_profiles:
                elements.append(Paragraph(
                    f"• {profile.platform}: {profile.username} ({profile.url})",
                    self.styles['BulletPoint']
                ))

        # Data breaches
        if data.data_breaches:
            elements.append(Paragraph("3.4 Presenza in Data Breach", self.styles['Section']))
            for breach in data.data_breaches:
                elements.append(Paragraph(
                    f"• {breach.source} ({breach.date or 'data sconosciuta'})",
                    self.styles['BulletPoint']
                ))

        return elements

    def _chapter_correlation(self, analysis: Dict, narrative: Dict) -> List:
        """Capitolo 4: Analisi Correlazione"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("CAPITOLO 4 - ANALISI E CORRELAZIONE DATI", self.styles['Chapter']))

        # Narrativa AI
        correlation_text = narrative.get('correlation_narrative', '')
        if correlation_text:
            elements.append(Paragraph("4.1 Analisi AI Avanzata", self.styles['Section']))
            # Split into paragraphs
            paragraphs = correlation_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['BodyText15']))

        # OSINT Verification
        osint_ver = analysis.get('osint_verification', {})
        if osint_ver.get('verification_result'):
            elements.append(Paragraph("4.2 Verifica OSINT Real-Time", self.styles['Section']))
            ver_text = osint_ver['verification_result']
            # Truncate if too long
            if len(ver_text) > 2000:
                ver_text = ver_text[:2000] + "..."
            elements.append(Paragraph(ver_text, self.styles['BodyText15']))

        # Correlation analysis
        corr = analysis.get('correlation_analysis', {})
        if corr.get('correlation_result'):
            elements.append(Paragraph("4.3 Correlazione Avanzata GPT-4", self.styles['Section']))
            corr_text = corr['correlation_result']
            if len(corr_text) > 2000:
                corr_text = corr_text[:2000] + "..."
            elements.append(Paragraph(corr_text, self.styles['BodyText15']))

        return elements

    def _chapter_psychological(self, psych_profile: Dict) -> List:
        """Capitolo 5: Profilo Psicologico"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("CAPITOLO 5 - PROFILO PSICOLOGICO", self.styles['Chapter']))

        # AI Profile
        ai_profile = psych_profile.get('ai_profile', '')
        if ai_profile:
            elements.append(Paragraph("5.1 Analisi Comportamentale Claude", self.styles['Section']))
            # Truncate if needed
            if len(ai_profile) > 3000:
                ai_profile = ai_profile[:3000] + "..."

            paragraphs = ai_profile.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['BodyText15']))

        # Base metrics
        base_metrics = psych_profile.get('base_metrics', {})
        big_five = base_metrics.get('big_five', {})

        if big_five:
            elements.append(Paragraph("5.2 Metriche Big Five", self.styles['Section']))

            traits = [
                ("Openness (Apertura)", big_five.get('openness', 50)),
                ("Conscientiousness (Coscienziosità)", big_five.get('conscientiousness', 50)),
                ("Extraversion (Estroversione)", big_five.get('extraversion', 50)),
                ("Agreeableness (Amicalità)", big_five.get('agreeableness', 50)),
                ("Neuroticism (Nevroticismo)", big_five.get('neuroticism', 50))
            ]

            for trait_name, value in traits:
                elements.append(Paragraph(f"• {trait_name}: {value}/100", self.styles['BulletPoint']))

        return elements

    def _chapter_passwords(self, password_analysis: Dict) -> List:
        """Capitolo 6: Analisi Password"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("CAPITOLO 6 - ANALISI PASSWORD", self.styles['Chapter']))

        if password_analysis.get('status'):
            elements.append(Paragraph(password_analysis['status'], self.styles['BodyText15']))
            return elements

        aggregate = password_analysis.get('aggregate', {})

        elements.append(Paragraph("6.1 Statistiche Aggregate", self.styles['Section']))
        elements.append(Paragraph(f"• Password Analizzate: {aggregate.get('total_passwords', 0)}", self.styles['BulletPoint']))
        elements.append(Paragraph(f"• Strength Media: {aggregate.get('average_strength', 0)}/100", self.styles['BulletPoint']))
        elements.append(Paragraph(f"• Livello Sicurezza: {aggregate.get('overall_security', 'N/A')}", self.styles['BulletPoint']))

        patterns = aggregate.get('common_patterns', [])
        if patterns:
            elements.append(Paragraph("6.2 Pattern Identificati", self.styles['Section']))
            for pattern in patterns:
                elements.append(Paragraph(f"• {pattern}", self.styles['BulletPoint']))

        recommendations = password_analysis.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("6.3 Raccomandazioni", self.styles['Section']))
            for rec in recommendations:
                elements.append(Paragraph(f"• {rec}", self.styles['BulletPoint']))

        return elements

    def _chapter_security(self, security: Dict) -> List:
        """Capitolo 7: Valutazione Sicurezza"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("CAPITOLO 7 - VALUTAZIONE SICUREZZA", self.styles['Chapter']))

        elements.append(Paragraph("7.1 Score Complessivo", self.styles['Section']))
        elements.append(Paragraph(
            f"Security Score: {security.get('security_score', 0)}/100 (Grade: {security.get('security_grade', 'N/A')})",
            self.styles['Highlight']
        ))

        # Vulnerabilities
        vulnerabilities = security.get('vulnerabilities', [])
        if vulnerabilities:
            elements.append(Paragraph("7.2 Vulnerabilità Identificate", self.styles['Section']))
            for vuln in vulnerabilities:
                elements.append(Paragraph(
                    f"• [{vuln.get('severity', 'N/A')}] {vuln.get('type', 'N/A')}: {vuln.get('description', '')}",
                    self.styles['BulletPoint']
                ))

        # Threats
        threats = security.get('threats', [])
        if threats:
            elements.append(Paragraph("7.3 Minacce Potenziali", self.styles['Section']))
            for threat in threats:
                elements.append(Paragraph(f"• {threat}", self.styles['BulletPoint']))

        # Recommendations
        recommendations = security.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("7.4 Raccomandazioni Sicurezza", self.styles['Section']))
            for rec in recommendations:
                elements.append(Paragraph(f"• {rec}", self.styles['BulletPoint']))

        return elements

    def _chapter_conclusions(self, narrative: Dict, security: Dict) -> List:
        """Capitolo 8: Conclusioni"""
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("CAPITOLO 8 - CONCLUSIONI", self.styles['Chapter']))

        # AI-generated conclusions
        conclusions = narrative.get('conclusions', '')
        if conclusions:
            paragraphs = conclusions.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.styles['BodyText15']))

        # Final assessment
        elements.append(Paragraph("8.1 Valutazione Finale", self.styles['Section']))

        risk_level = security.get('risk_level', 'SCONOSCIUTO')
        grade = security.get('security_grade', 'N/A')

        final_text = f"""
        Sulla base dell'analisi condotta, il soggetto presenta un livello di rischio {risk_level}
        con un Security Grade di {grade}. Le evidenze raccolte attraverso le metodologie OSINT
        e l'analisi AI hanno permesso di costruire un profilo informativo completo e attendibile.
        """
        elements.append(Paragraph(final_text.strip(), self.styles['BodyText15']))

        # Signature
        elements.append(Spacer(1, 20*mm))
        elements.append(Paragraph("___" * 20, self.styles['BodyText15']))
        elements.append(Paragraph(
            f"Report generato da FidelinvestigatorAI - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            self.styles['SubTitle']
        ))

        return elements


# ============================================================================
# MAIN AGENT
# ============================================================================

class FidelinvestigatorAI:
    """Agente Investigativo OSINT con AI Enhancement"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.ai_clients = AIClients(self.config)

        self.parser = OSINTHtmlParser()
        self.analyzer = AIDataAnalyzer(self.ai_clients)
        self.profiler = AIPsychologicalProfiler(self.ai_clients)
        self.password_analyzer = PasswordAnalyzer()
        self.security_assessor = SecurityAssessor()
        self.report_generator = AIReportGenerator(self.ai_clients)

    def investigate(self, html_input: str, output_dir: str = None) -> str:
        """Esegue investigazione completa"""

        output_dir = output_dir or self.config.OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)

        print("=" * 60)
        print("FidelinvestigatorAI - Sistema di Intelligence OSINT")
        print("Enhanced Edition con AI Integration")
        print("=" * 60)

        # Check API keys
        self._check_api_keys()

        # Parse HTML
        print("\n[1/9] Parsing dati OSINT...")
        if os.path.isfile(html_input):
            data = self.parser.parse_file(html_input)
        else:
            data = self.parser.parse_html(html_input)

        print(f"      Email: {len(data.contact_info.emails)}")
        print(f"      Social: {len(data.social_profiles)}")
        print(f"      Breaches: {len(data.data_breaches)}")
        print(f"      Passwords: {len(data.passwords)}")

        # AI-Enhanced Analysis
        print("\n[2/9] Analisi e correlazione dati...")
        analysis = self.analyzer.analyze(data)

        # AI Psychological Profile
        print("\n[3/9] Profilazione psicologica...")
        psych_profile = self.profiler.profile(data, analysis)

        # Password Analysis
        print("\n[4/9] Analisi password...")
        password_analysis = self.password_analyzer.analyze(
            data.passwords,
            data.personal_info
        )

        # Security Assessment
        print("\n[5/9] Valutazione sicurezza...")
        security_assessment = self.security_assessor.assess(
            data, analysis, password_analysis
        )

        # Generate Report
        print("\n[6/9] Generazione report PDF...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"report_investigativo_{timestamp}.pdf")

        self.report_generator.generate(
            data=data,
            analysis=analysis,
            psych_profile=psych_profile,
            password_analysis=password_analysis,
            security_assessment=security_assessment,
            output_path=output_path,
            logo_path=self.config.LOGO_PATH
        )

        # Prepare extracted dict for DOCX generators
        extracted_dict = {
            'emails': list(data.contact_info.emails) if data.contact_info else [],
            'usernames': list(data.usernames),
            'phones': list(data.contact_info.phones) if data.contact_info else [],
            'ips': list(data.ip_addresses),
            'social_profiles': [asdict(p) if hasattr(p, '__dataclass_fields__') else p for p in data.social_profiles],
            'passwords': list(data.passwords),
            'breaches': [asdict(b) if hasattr(b, '__dataclass_fields__') else b for b in data.data_breaches]
        }

        # Generate DOCX Executive Report (Company-focused)
        docx_company_path = None
        if DOCX_COMPANY_AVAILABLE:
            print("\n[7/9] Generazione Executive Assessment Aziende (DOCX)...")
            docx_company_path = os.path.join(output_dir, f"executive_assessment_{timestamp}.docx")

            try:
                assessment = create_assessment_from_osint_data(
                    extracted_data=extracted_dict,
                    analysis_data=analysis,
                    psychological_profile=psych_profile,
                    security_assessment=security_assessment,
                    company_name=getattr(self.config, 'ORGANIZATION_NAME', 'Target Organization')
                )

                generator = ExecutiveReportGenerator()
                generator.generate_report(assessment, docx_company_path)

                print(f"      ✓ Report Aziende: {docx_company_path}")

            except Exception as e:
                print(f"      ✗ Errore report aziende: {e}")
                docx_company_path = None

        # Generate Personal Vulnerability Assessment (Person-focused with Claude AI)
        docx_personal_path = None
        if DOCX_PERSONAL_AVAILABLE:
            print("\n[8/9] Generazione Personal Vulnerability Assessment (Claude AI)...")
            docx_personal_path = os.path.join(output_dir, f"personal_assessment_{timestamp}.docx")

            try:
                # Determina nome soggetto da email o username
                subject_name = "Target Subject"
                if data.usernames:
                    subject_name = data.usernames[0]
                elif data.contact_info.emails:
                    email = list(data.contact_info.emails)[0]
                    subject_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()

                print(f"      Soggetto: {subject_name}")
                print(f"      Analisi con Anthropic Claude...")

                # Generate report with Claude AI analysis
                docx_personal_path = generate_personal_report(
                    osint_data=extracted_dict,
                    analysis_data=analysis,
                    psych_profile=psych_profile,
                    security_assessment=security_assessment,
                    subject_name=subject_name,
                    output_path=docx_personal_path,
                    anthropic_api_key=self.config.ANTHROPIC_API_KEY
                )

                print(f"      ✓ Report Personale (Claude): {docx_personal_path}")

            except Exception as e:
                print(f"      ✗ Errore report personale: {e}")
                import traceback
                traceback.print_exc()
                docx_personal_path = None
        else:
            print("\n[8/9] Report Personale DOCX non disponibile (modulo non installato)")

        # Generate Intelligence Report (Dutch OSINT Guy Methodology)
        intel_report_path = None
        if INTELLIGENCE_REPORT_AVAILABLE:
            print("\n[9/9] Generazione Intelligence Report (Dutch OSINT Guy Framework)...")
            intel_report_path = os.path.join(output_dir, f"intelligence_report_{timestamp}.docx")

            try:
                # Determina nome soggetto se non già determinato
                if 'subject_name' not in dir() or not subject_name:
                    subject_name = "Target Subject"
                    if data.usernames:
                        subject_name = data.usernames[0]
                    elif data.contact_info.emails:
                        email = list(data.contact_info.emails)[0]
                        subject_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()

                print(f"      Soggetto: {subject_name}")
                print(f"      Framework: Dutch OSINT Guy Methodology")
                print(f"      Standard: CIA/NATO Intelligence Cycle")

                # Generate intelligence report
                intel_report_path = generate_dutch_osint_report(
                    osint_data=extracted_dict,
                    analysis_data=analysis,
                    psych_profile=psych_profile,
                    security_assessment=security_assessment,
                    subject_name=subject_name,
                    output_path=intel_report_path,
                    anthropic_api_key=self.config.ANTHROPIC_API_KEY,
                    format="docx"
                )

                print(f"      ✓ Intelligence Report: {intel_report_path}")

            except Exception as e:
                print(f"      ✗ Errore Intelligence Report: {e}")
                import traceback
                traceback.print_exc()
                intel_report_path = None
        else:
            print("\n[9/9] Intelligence Report Framework non disponibile")

        print("\n" + "=" * 60)
        print("INVESTIGAZIONE COMPLETATA")
        print("=" * 60)
        print(f"\nReport generati:")
        print(f"  PDF:                {output_path}")
        if docx_company_path:
            print(f"  DOCX (Aziende):     {docx_company_path}")
        if docx_personal_path:
            print(f"  DOCX (Personale):   {docx_personal_path}")
        if intel_report_path:
            print(f"  DOCX (Intelligence): {intel_report_path}")
        print(f"\nSecurity Grade: {security_assessment.get('security_grade', 'N/A')}")
        print(f"Risk Level: {analysis.get('base_analysis', {}).get('exposure_level', 'N/A')}")

        return output_path

    def _check_api_keys(self):
        """Verifica configurazione API"""
        print("\n[*] Verifica API Keys:")

        if self.config.OPENAI_API_KEY:
            print("    ✓ OpenAI configurato")
        else:
            print("    ✗ OpenAI non configurato")

        if self.config.ANTHROPIC_API_KEY:
            print("    ✓ Anthropic configurato")
        else:
            print("    ✗ Anthropic non configurato")

        if self.config.PERPLEXITY_API_KEY:
            print("    ✓ Perplexity configurato")
        else:
            print("    ✗ Perplexity non configurato")

        if not any([self.config.OPENAI_API_KEY, self.config.ANTHROPIC_API_KEY, self.config.PERPLEXITY_API_KEY]):
            print("\n[!] ATTENZIONE: Nessuna API key configurata.")
            print("    L'analisi sarà limitata. Configurare le API per analisi avanzata.")


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='FidelinvestigatorAI - Agente Investigativo OSINT Enhanced'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='File HTML o directory da analizzare'
    )
    parser.add_argument(
        '-o', '--output',
        help='Directory output report',
        default=Config.OUTPUT_DIR
    )
    parser.add_argument(
        '--openai-key',
        help='OpenAI API Key',
        default=os.getenv('OPENAI_API_KEY', '')
    )
    parser.add_argument(
        '--anthropic-key',
        help='Anthropic API Key',
        default=os.getenv('ANTHROPIC_API_KEY', '')
    )
    parser.add_argument(
        '--perplexity-key',
        help='Perplexity API Key',
        default=os.getenv('PERPLEXITY_API_KEY', '')
    )

    args = parser.parse_args()

    # Configura
    config = Config()
    if args.openai_key:
        config.OPENAI_API_KEY = args.openai_key
    if args.anthropic_key:
        config.ANTHROPIC_API_KEY = args.anthropic_key
    if args.perplexity_key:
        config.PERPLEXITY_API_KEY = args.perplexity_key
    if args.output:
        config.OUTPUT_DIR = args.output

    agent = FidelinvestigatorAI(config)

    # Determina input
    input_path = args.input or config.INPUT_DIR

    if os.path.isdir(input_path):
        # Analizza tutti i file HTML nella directory
        html_files = [f for f in os.listdir(input_path) if f.endswith('.html')]
        if not html_files:
            print(f"[!] Nessun file HTML trovato in: {input_path}")
            return

        for html_file in html_files:
            file_path = os.path.join(input_path, html_file)
            print(f"\n[*] Analisi: {html_file}")
            agent.investigate(file_path, args.output)
    else:
        agent.investigate(input_path, args.output)


if __name__ == "__main__":
    main()
