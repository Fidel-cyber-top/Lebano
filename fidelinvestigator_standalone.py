#!/usr/bin/env python3
"""
FidelinvestigatorAI - Script di Configurazione e Esecuzione
============================================================

Script standalone per analizzare report HTML OSINT dalla cartella locale
e generare report PDF investigativi professionali.

Configurato per: /home/kali/Scrivania/suka/FidelAI/html
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# ============================================
# CONFIGURAZIONE - MODIFICA QUESTI PERCORSI
# ============================================

CONFIG = {
    # Cartella contenente i file HTML da analizzare
    "INPUT_DIR": "/home/kali/Scrivania/suka/FidelAI/html",

    # Cartella dove salvare i report PDF generati
    "OUTPUT_DIR": "/home/kali/Scrivania/suka/FidelAI/reports",

    # Percorso del logo (opzionale - lascia None se non hai un logo)
    "LOGO_PATH": None,  # Es: "/home/kali/Scrivania/suka/FidelAI/assets/logo.png"

    # Nome dell'organizzazione per il report
    "ORGANIZATION_NAME": "FidelinvestigatorAI",

    # Mostra output dettagliato
    "VERBOSE": True,
}

# ============================================
# INSTALLAZIONE DIPENDENZE
# ============================================

def check_dependencies():
    """Verifica e installa le dipendenze necessarie"""
    required = ['beautifulsoup4', 'reportlab', 'lxml', 'Pillow']
    missing = []

    for package in required:
        try:
            __import__(package.replace('-', '_').split('4')[0])
        except ImportError:
            missing.append(package)

    if missing:
        print(f"[!] Dipendenze mancanti: {', '.join(missing)}")
        print("[*] Installazione in corso...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("[✓] Dipendenze installate!")

    return True

# Verifica dipendenze all'avvio
check_dependencies()

# Import dopo verifica dipendenze
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem, HRFlowable
)

# ============================================
# DATA CLASSES
# ============================================

@dataclass
class PersonalInfo:
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    occupation: Optional[str] = None
    education: List[str] = field(default_factory=list)
    bio: Optional[str] = None

@dataclass
class ContactInfo:
    emails: List[Dict[str, Any]] = field(default_factory=list)
    phones: List[Dict[str, Any]] = field(default_factory=list)
    addresses: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class SocialMediaProfile:
    platform: str
    username: Optional[str] = None
    profile_url: Optional[str] = None
    followers: Optional[int] = None
    bio: Optional[str] = None

@dataclass
class DataBreach:
    breach_name: str
    breach_date: Optional[str] = None
    data_exposed: List[str] = field(default_factory=list)
    password_plain: Optional[str] = None

@dataclass
class ExtractedData:
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    social_media: List[SocialMediaProfile] = field(default_factory=list)
    data_breaches: List[DataBreach] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    raw_passwords: List[str] = field(default_factory=list)
    ip_addresses: List[Dict[str, Any]] = field(default_factory=list)
    locations: List[Dict[str, Any]] = field(default_factory=list)
    domains: List[Dict[str, Any]] = field(default_factory=list)

# ============================================
# HTML PARSER
# ============================================

class HTMLParser:
    """Parser per report HTML OSINT"""

    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_PATTERN = re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}')
    URL_PATTERN = re.compile(r'https?://[^\s<>"\']+')
    USERNAME_PATTERN = re.compile(r'@([a-zA-Z0-9_]{1,30})')
    PASSWORD_PATTERN = re.compile(r'(?:password|pwd|pass|passwd)[:\s]*([^\s<>]{4,})', re.IGNORECASE)

    SOCIAL_PLATFORMS = {
        'facebook': ['facebook.com', 'fb.com'],
        'twitter': ['twitter.com', 'x.com'],
        'instagram': ['instagram.com'],
        'linkedin': ['linkedin.com'],
        'tiktok': ['tiktok.com'],
        'youtube': ['youtube.com'],
        'github': ['github.com'],
        'reddit': ['reddit.com'],
        'telegram': ['t.me', 'telegram.me'],
        'discord': ['discord.gg', 'discord.com'],
        'twitch': ['twitch.tv'],
        'spotify': ['spotify.com'],
    }

    def __init__(self):
        self.data = ExtractedData()

    def parse(self, html_content: str) -> ExtractedData:
        """Esegue il parsing completo"""
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        self._extract_personal_info(text, soup)
        self._extract_contacts(text)
        self._extract_social_media(text)
        self._extract_usernames(text)
        self._extract_breaches(text, soup)
        self._extract_passwords(text)
        self._extract_locations(text)

        return self.data

    def _extract_personal_info(self, text: str, soup):
        """Estrae informazioni personali"""
        # Nome
        name_match = re.search(r'(?:name|nome|full name)[:\s]*([^\n<]+)', text, re.I)
        if name_match:
            self.data.personal_info.full_name = name_match.group(1).strip()

        # Data nascita
        dob_match = re.search(r'(?:birth|nascita|dob|data di nascita)[:\s]*([\d\/\-\.]+)', text, re.I)
        if dob_match:
            self.data.personal_info.date_of_birth = dob_match.group(1)

        # Età
        age_match = re.search(r'(?:age|età)[:\s]*(\d+)', text, re.I)
        if age_match:
            self.data.personal_info.age = int(age_match.group(1))

        # Professione
        occ_match = re.search(r'(?:occupation|job|lavoro|professione)[:\s]*([^\n<]+)', text, re.I)
        if occ_match:
            self.data.personal_info.occupation = occ_match.group(1).strip()

        # Nazionalità
        nat_match = re.search(r'(?:nationality|nazionalità)[:\s]*([^\n<]+)', text, re.I)
        if nat_match:
            self.data.personal_info.nationality = nat_match.group(1).strip()

        # Alias
        alias_matches = re.findall(r'(?:alias|aka|known as)[:\s]*([^\n,]+)', text, re.I)
        self.data.personal_info.aliases = [a.strip() for a in alias_matches]

    def _extract_contacts(self, text: str):
        """Estrae contatti"""
        # Email
        emails = self.EMAIL_PATTERN.findall(text)
        for email in set(emails):
            self.data.contact_info.emails.append({
                'email': email.lower(),
                'domain': email.split('@')[1] if '@' in email else None
            })

        # Telefoni
        phones = self.PHONE_PATTERN.findall(text)
        for phone in set(phones):
            cleaned = re.sub(r'[^\d+]', '', phone)
            if len(cleaned) >= 8:
                self.data.contact_info.phones.append({
                    'number': phone,
                    'cleaned': cleaned
                })

    def _extract_social_media(self, text: str):
        """Estrae profili social"""
        urls = self.URL_PATTERN.findall(text)

        for url in urls:
            url_lower = url.lower()
            for platform, domains in self.SOCIAL_PLATFORMS.items():
                if any(d in url_lower for d in domains):
                    # Estrai username dall'URL
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        path_parts = parsed.path.strip('/').split('/')
                        username = path_parts[0] if path_parts else None
                    except:
                        username = None

                    profile = SocialMediaProfile(
                        platform=platform,
                        profile_url=url,
                        username=username
                    )

                    # Evita duplicati
                    if not any(p.profile_url == url for p in self.data.social_media):
                        self.data.social_media.append(profile)
                    break

    def _extract_usernames(self, text: str):
        """Estrae username"""
        usernames = self.USERNAME_PATTERN.findall(text)

        # Aggiungi anche username dai social
        for profile in self.data.social_media:
            if profile.username:
                usernames.append(profile.username)

        self.data.usernames = list(set(usernames))

    def _extract_breaches(self, text: str, soup):
        """Estrae informazioni sui breach"""
        breach_pattern = re.compile(r'([A-Za-z0-9\s]+?)\s*(?:breach|leak|hack)', re.I)
        matches = breach_pattern.findall(text)

        for match in matches:
            breach = DataBreach(breach_name=match.strip())
            self.data.data_breaches.append(breach)

        # Cerca anche nelle tabelle
        tables = soup.find_all('table')
        for table in tables:
            headers = [th.text.strip().lower() for th in table.find_all('th')]
            if any(h in ' '.join(headers) for h in ['breach', 'leak', 'password']):
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cells = row.find_all('td')
                    if cells:
                        breach = DataBreach(breach_name=cells[0].text.strip())
                        for i, cell in enumerate(cells):
                            cell_text = cell.text.strip()
                            if i < len(headers):
                                if 'password' in headers[i] and len(cell_text) < 30:
                                    breach.password_plain = cell_text
                                    if cell_text not in self.data.raw_passwords:
                                        self.data.raw_passwords.append(cell_text)
                        if breach.breach_name and not any(b.breach_name == breach.breach_name for b in self.data.data_breaches):
                            self.data.data_breaches.append(breach)

    def _extract_passwords(self, text: str):
        """Estrae password"""
        matches = self.PASSWORD_PATTERN.findall(text)
        for pwd in matches:
            if pwd not in self.data.raw_passwords:
                self.data.raw_passwords.append(pwd)

    def _extract_locations(self, text: str):
        """Estrae località"""
        patterns = [
            r'(?:location|città|city|country)[:\s]*([^\n,]+)',
            r'(?:lives in|vive a|from|da)[:\s]*([^\n,]+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.I)
            for match in matches:
                self.data.locations.append({'raw': match.strip(), 'type': 'mentioned'})

# ============================================
# DATA ANALYZER
# ============================================

class DataAnalyzer:
    """Analizzatore e correlatore di dati"""

    def __init__(self, data: ExtractedData):
        self.data = data
        self.correlations = []
        self.risk_indicators = []
        self.activity_patterns = []
        self.key_findings = []
        self.exposure_level = "SCONOSCIUTO"
        self.footprint_score = 0

    def analyze(self):
        """Esegue l'analisi completa"""
        self._correlate_data()
        self._identify_patterns()
        self._assess_risks()
        self._calculate_exposure()
        self._generate_findings()

        return self

    def _correlate_data(self):
        """Correla i dati"""
        # Email-Username
        for email_info in self.data.contact_info.emails:
            email = email_info.get('email', '')
            local_part = email.split('@')[0] if '@' in email else ''

            for username in self.data.usernames:
                similarity = self._similarity(local_part, username)
                if similarity > 0.5:
                    self.correlations.append({
                        'type': 'email_username',
                        'source': email,
                        'target': username,
                        'confidence': similarity,
                        'description': f"Username '{username}' correlato a '{email}'",
                        'significance': 'high' if similarity > 0.8 else 'medium'
                    })

        # Cross-platform
        username_platforms = defaultdict(list)
        for profile in self.data.social_media:
            if profile.username:
                username_platforms[profile.username.lower()].append(profile.platform)

        for username, platforms in username_platforms.items():
            if len(platforms) > 1:
                self.correlations.append({
                    'type': 'cross_platform',
                    'source': username,
                    'target': platforms,
                    'confidence': 0.9,
                    'description': f"Username '{username}' su: {', '.join(platforms)}",
                    'significance': 'high'
                })

        # Breach
        if self.data.data_breaches:
            self.correlations.append({
                'type': 'breach_exposure',
                'source': 'breaches',
                'target': len(self.data.data_breaches),
                'confidence': 1.0,
                'description': f"Coinvolto in {len(self.data.data_breaches)} data breach",
                'significance': 'critical' if len(self.data.data_breaches) > 2 else 'high'
            })

        # Password
        if self.data.raw_passwords:
            self.correlations.append({
                'type': 'password_exposure',
                'source': 'passwords',
                'target': len(self.data.raw_passwords),
                'confidence': 1.0,
                'description': f"{len(self.data.raw_passwords)} password esposte",
                'significance': 'critical'
            })

    def _similarity(self, s1: str, s2: str) -> float:
        """Calcola similarità Jaccard"""
        if not s1 or not s2:
            return 0
        s1, s2 = s1.lower(), s2.lower()
        if s1 == s2:
            return 1.0
        set1, set2 = set(s1), set(s2)
        return len(set1 & set2) / len(set1 | set2)

    def _identify_patterns(self):
        """Identifica pattern di attività"""
        platform_count = len(self.data.social_media)

        if platform_count >= 5:
            self.activity_patterns.append({
                'type': 'multi_platform',
                'description': f'Presenza su {platform_count} piattaforme social',
                'significance': 'medium'
            })
        elif platform_count > 0 and platform_count <= 2:
            self.activity_patterns.append({
                'type': 'selective_presence',
                'description': 'Presenza social selettiva',
                'significance': 'medium'
            })

        # Username consistency
        unique_usernames = set(u.lower() for u in self.data.usernames)
        if len(unique_usernames) == 1 and len(self.data.usernames) > 1:
            self.activity_patterns.append({
                'type': 'consistent_identity',
                'description': 'Username consistente su tutte le piattaforme',
                'significance': 'high'
            })

    def _assess_risks(self):
        """Valuta i rischi"""
        if self.data.raw_passwords:
            self.risk_indicators.append({
                'type': 'password_exposure',
                'description': f"{len(self.data.raw_passwords)} password esposte in chiaro",
                'severity': 'critical',
                'recommendations': [
                    'Cambio immediato password',
                    'Attivare 2FA',
                    'Usare password manager'
                ]
            })

        if self.data.data_breaches:
            self.risk_indicators.append({
                'type': 'breach_exposure',
                'description': f"Coinvolto in {len(self.data.data_breaches)} breach",
                'severity': 'critical' if len(self.data.data_breaches) > 3 else 'high',
                'recommendations': ['Monitoraggio credenziali', 'Reset password']
            })

        if len(self.data.contact_info.emails) > 2:
            self.risk_indicators.append({
                'type': 'email_exposure',
                'description': f"{len(self.data.contact_info.emails)} email esposte",
                'severity': 'medium',
                'recommendations': ['Usare email alias']
            })

        if len(self.data.social_media) > 5:
            self.risk_indicators.append({
                'type': 'social_overexposure',
                'description': f"Presenza su {len(self.data.social_media)} social",
                'severity': 'medium',
                'recommendations': ['Revisione privacy settings']
            })

    def _calculate_exposure(self):
        """Calcola livello esposizione"""
        score = 0
        score += min(30, len(self.data.contact_info.emails) * 10)
        score += min(40, len(self.data.social_media) * 8)
        score += min(30, len(self.data.data_breaches) * 15)
        score += min(30, len(self.data.raw_passwords) * 20)
        score += min(20, len(self.data.usernames) * 5)

        self.footprint_score = min(100, score)

        if self.footprint_score >= 80:
            self.exposure_level = "CRITICO"
        elif self.footprint_score >= 60:
            self.exposure_level = "ALTO"
        elif self.footprint_score >= 40:
            self.exposure_level = "MODERATO"
        elif self.footprint_score >= 20:
            self.exposure_level = "BASSO"
        else:
            self.exposure_level = "MINIMO"

    def _generate_findings(self):
        """Genera findings chiave"""
        if self.data.personal_info.full_name:
            self.key_findings.append(f"Identità: {self.data.personal_info.full_name}")

        self.key_findings.append(f"Esposizione: {self.exposure_level} ({self.footprint_score}/100)")

        if self.data.data_breaches:
            self.key_findings.append(f"{len(self.data.data_breaches)} data breach")

        if self.data.raw_passwords:
            self.key_findings.append(f"ATTENZIONE: {len(self.data.raw_passwords)} password esposte")

        platforms = set(p.platform for p in self.data.social_media)
        if platforms:
            self.key_findings.append(f"Social: {', '.join(platforms)}")

# ============================================
# PSYCHOLOGICAL PROFILER
# ============================================

class PsychologicalProfiler:
    """Profiler psicologico"""

    def __init__(self, data: ExtractedData):
        self.data = data
        self.behavioral_patterns = []
        self.risk_profile = {}
        self.vulnerabilities = []
        self.strengths = []
        self.summary = ""

    def profile(self):
        """Genera profilo psicologico"""
        self._analyze_behavior()
        self._assess_risk_profile()
        self._identify_vulnerabilities()
        self._generate_summary()

        return self

    def _analyze_behavior(self):
        """Analizza comportamento"""
        platform_count = len(self.data.social_media)

        if platform_count >= 5:
            self.behavioral_patterns.append({
                'type': 'multi_platform',
                'description': f'Presenza su {platform_count} piattaforme',
                'implication': 'Forte bisogno connessione sociale, possibile FOMO'
            })
        elif platform_count <= 2 and platform_count > 0:
            self.behavioral_patterns.append({
                'type': 'selective',
                'description': 'Presenza social selettiva',
                'implication': 'Approccio consapevole alla privacy'
            })

        unique_usernames = set(u.lower() for u in self.data.usernames)
        if len(unique_usernames) == 1 and len(self.data.usernames) > 1:
            self.behavioral_patterns.append({
                'type': 'consistent_identity',
                'description': 'Username consistente',
                'implication': 'Personalità coerente, brand personale'
            })

        if self.data.data_breaches and len(self.data.data_breaches) > 3:
            self.behavioral_patterns.append({
                'type': 'security_negligence',
                'description': 'Multipli breach',
                'implication': 'Sottovalutazione rischi sicurezza'
            })

    def _assess_risk_profile(self):
        """Valuta profilo rischio"""
        privacy_score = 0
        if len(self.data.contact_info.emails) <= 1:
            privacy_score += 2
        if len(self.data.social_media) <= 2:
            privacy_score += 2

        security_score = 0
        if not self.data.data_breaches:
            security_score += 2
        if self.data.raw_passwords:
            security_score -= 3

        self.risk_profile = {
            'privacy_awareness': 'high' if privacy_score >= 2 else ('moderate' if privacy_score >= 0 else 'low'),
            'security_consciousness': 'high' if security_score >= 2 else ('moderate' if security_score >= 0 else 'low'),
            'risk_tolerance': 'moderate'
        }

    def _identify_vulnerabilities(self):
        """Identifica vulnerabilità"""
        if self.data.data_breaches:
            self.vulnerabilities.append('Storico breach indica possibile riutilizzo password')

        if len(self.data.social_media) > 5:
            self.vulnerabilities.append('Presenza social estesa aumenta superficie attacco')

        unique = set(u.lower() for u in self.data.usernames)
        if len(unique) == 1 and len(self.data.usernames) > 2:
            self.vulnerabilities.append('Username consistente facilita tracking')

        # Strengths
        if self.risk_profile.get('privacy_awareness') == 'high':
            self.strengths.append('Alta consapevolezza privacy')

        if not self.data.data_breaches:
            self.strengths.append('Nessun breach noto')

    def _generate_summary(self):
        """Genera sommario"""
        name = self.data.personal_info.full_name or "Il target"
        self.summary = f"{name} presenta un profilo che emerge dall'analisi del comportamento digitale. "
        self.summary += f"Consapevolezza privacy: {self.risk_profile.get('privacy_awareness', 'unknown')}, "
        self.summary += f"security consciousness: {self.risk_profile.get('security_consciousness', 'unknown')}."

# ============================================
# PASSWORD ANALYZER
# ============================================

class PasswordAnalyzer:
    """Analizzatore password"""

    COMMON_PATTERNS = {
        'keyboard': ['qwerty', 'asdf', 'zxcv', '1qaz', '2wsx'],
        'numbers': ['123', '1234', '12345', '123456'],
        'words': ['password', 'admin', 'pass', 'secret'],
        'italian': ['ciao', 'amore', 'italia', 'roma', 'milano']
    }

    def __init__(self, data: ExtractedData):
        self.data = data
        self.patterns = []
        self.strength_assessments = []
        self.security_score = 0
        self.security_level = "SCONOSCIUTO"
        self.construction_method = ""
        self.predictions = []
        self.insights = []

    def analyze(self):
        """Analizza password"""
        passwords = list(set(self.data.raw_passwords))

        if not passwords:
            return self

        for pwd in passwords:
            self._assess_strength(pwd)
            self._identify_patterns(pwd)

        self._determine_construction()
        self._calculate_score()
        self._generate_predictions()
        self._generate_insights()

        return self

    def _assess_strength(self, pwd: str):
        """Valuta forza password"""
        length = len(pwd)
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_num = any(c.isdigit() for c in pwd)
        has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in pwd)

        charset = 0
        if has_lower: charset += 26
        if has_upper: charset += 26
        if has_num: charset += 10
        if has_special: charset += 32

        import math
        entropy = length * math.log2(charset) if charset > 0 else 0

        weaknesses = []
        if length < 8: weaknesses.append('Lunghezza < 8')
        if not has_upper: weaknesses.append('No maiuscole')
        if not has_num: weaknesses.append('No numeri')
        if not has_special: weaknesses.append('No speciali')

        score = entropy - len(weaknesses) * 5
        level = 'very_weak' if score < 20 else 'weak' if score < 35 else 'medium' if score < 50 else 'strong'

        self.strength_assessments.append({
            'password_masked': pwd[0] + '*' * (len(pwd) - 2) + pwd[-1] if len(pwd) > 2 else '***',
            'length': length,
            'entropy': round(entropy, 2),
            'level': level,
            'weaknesses': weaknesses
        })

    def _identify_patterns(self, pwd: str):
        """Identifica pattern"""
        pwd_lower = pwd.lower()

        for pattern_type, patterns in self.COMMON_PATTERNS.items():
            for pattern in patterns:
                if pattern in pwd_lower:
                    self.patterns.append({
                        'type': pattern_type,
                        'value': pattern,
                        'description': f"Pattern '{pattern}' trovato",
                        'impact': 'high'
                    })

        # Nome personale
        if self.data.personal_info.full_name:
            for part in self.data.personal_info.full_name.lower().split():
                if len(part) > 2 and part in pwd_lower:
                    self.patterns.append({
                        'type': 'personal_name',
                        'value': part,
                        'description': f"Nome '{part}' in password",
                        'impact': 'critical'
                    })

        # Date
        date_match = re.search(r'\b(19|20)\d{2}\b', pwd)
        if date_match:
            self.patterns.append({
                'type': 'date',
                'value': date_match.group(),
                'description': f"Anno {date_match.group()} in password",
                'impact': 'high'
            })

    def _determine_construction(self):
        """Determina metodo costruzione"""
        methods = []
        pattern_types = Counter(p['type'] for p in self.patterns)

        if pattern_types.get('personal_name'):
            methods.append('Usa informazioni personali')
        if pattern_types.get('date'):
            methods.append('Incorpora date')
        if pattern_types.get('keyboard'):
            methods.append('Sequenze tastiera')
        if pattern_types.get('numbers'):
            methods.append('Sequenze numeriche')

        self.construction_method = '; '.join(methods) if methods else 'Non determinabile'

    def _calculate_score(self):
        """Calcola score sicurezza"""
        if not self.strength_assessments:
            return

        avg_entropy = sum(s['entropy'] for s in self.strength_assessments) / len(self.strength_assessments)
        critical = sum(1 for p in self.patterns if p['impact'] == 'critical')
        high = sum(1 for p in self.patterns if p['impact'] == 'high')

        self.security_score = max(0, min(100, avg_entropy - critical * 15 - high * 8))

        if self.security_score < 20:
            self.security_level = "CRITICO"
        elif self.security_score < 40:
            self.security_level = "BASSO"
        elif self.security_score < 60:
            self.security_level = "MEDIO"
        elif self.security_score < 80:
            self.security_level = "BUONO"
        else:
            self.security_level = "ECCELLENTE"

    def _generate_predictions(self):
        """Genera predizioni"""
        if self.data.personal_info.full_name:
            name = self.data.personal_info.full_name.split()[0].lower()
            self.predictions.append({
                'type': 'name_based',
                'description': 'Possibile uso nome in altre password',
                'examples': [f"{name}123", f"{name.capitalize()}!", f"{name}2024"]
            })

    def _generate_insights(self):
        """Genera insight psicologici"""
        if self.strength_assessments:
            avg_len = sum(s['length'] for s in self.strength_assessments) / len(self.strength_assessments)
            if avg_len < 8:
                self.insights.append('Preferenza password corte indica priorità a comodità')

        if any(p['type'] == 'personal_name' for p in self.patterns):
            self.insights.append('Uso dati personali riflette legame emotivo')

# ============================================
# SECURITY ASSESSOR
# ============================================

class SecurityAssessor:
    """Valutatore sicurezza"""

    def __init__(self, data: ExtractedData, analysis, password_profile):
        self.data = data
        self.analysis = analysis
        self.pwd = password_profile
        self.vulnerabilities = []
        self.threats = []
        self.posture = {}
        self.privacy_score = 0
        self.recommendations = []

    def assess(self):
        """Esegue valutazione"""
        self._identify_vulnerabilities()
        self._assess_threats()
        self._calculate_posture()
        self._calculate_privacy()
        self._generate_recommendations()

        return self

    def _identify_vulnerabilities(self):
        """Identifica vulnerabilità"""
        if self.data.raw_passwords:
            self.vulnerabilities.append({
                'type': 'Credential Exposure',
                'severity': 'critical',
                'description': 'Password esposte in chiaro',
                'cvss': 9.8
            })

        if len(self.data.data_breaches) > 2:
            self.vulnerabilities.append({
                'type': 'Repeated Breach',
                'severity': 'high',
                'description': 'Multipli breach indicano riutilizzo credenziali',
                'cvss': 7.5
            })

        if len(self.data.social_media) > 7:
            self.vulnerabilities.append({
                'type': 'Social Overexposure',
                'severity': 'medium',
                'description': 'Troppi profili social',
                'cvss': 4.0
            })

        if self.pwd.security_level in ['CRITICO', 'BASSO']:
            self.vulnerabilities.append({
                'type': 'Weak Passwords',
                'severity': 'high',
                'description': 'Pattern password deboli',
                'cvss': 7.0
            })

    def _assess_threats(self):
        """Valuta minacce"""
        if self.data.raw_passwords:
            self.threats.append({
                'type': 'Credential Stuffing',
                'likelihood': 'very_high',
                'impact': 'critical',
                'description': 'Attacco con credenziali esposte'
            })

        if self.data.personal_info.full_name and len(self.data.social_media) > 3:
            self.threats.append({
                'type': 'Spear Phishing',
                'likelihood': 'high',
                'impact': 'high',
                'description': 'Phishing mirato con info personali'
            })

        if self.data.data_breaches:
            self.threats.append({
                'type': 'Account Takeover',
                'likelihood': 'high' if len(self.data.data_breaches) > 2 else 'medium',
                'impact': 'high',
                'description': 'Compromissione account'
            })

    def _calculate_posture(self):
        """Calcola postura sicurezza"""
        score = 100

        for v in self.vulnerabilities:
            if v['severity'] == 'critical':
                score -= 25
            elif v['severity'] == 'high':
                score -= 15
            else:
                score -= 8

        if not self.data.raw_passwords:
            score += 10
        if not self.data.data_breaches:
            score += 15

        score = max(0, min(100, score))

        grade = 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 50 else 'F'

        self.posture = {
            'score': round(score),
            'grade': grade,
            'weaknesses': [v['description'] for v in self.vulnerabilities[:3]],
            'immediate_actions': ['Cambio password' if self.data.raw_passwords else None, 'Attivare 2FA']
        }
        self.posture['immediate_actions'] = [a for a in self.posture['immediate_actions'] if a]

    def _calculate_privacy(self):
        """Calcola privacy score"""
        score = 100
        if self.data.personal_info.full_name:
            score -= 10
        if self.data.personal_info.date_of_birth:
            score -= 15
        score -= len(self.data.contact_info.emails) * 5
        score -= len(self.data.contact_info.phones) * 10
        score -= len(self.data.social_media) * 3

        self.privacy_score = max(0, score)

    def _generate_recommendations(self):
        """Genera raccomandazioni"""
        if self.data.raw_passwords:
            self.recommendations.append({
                'priority': 'CRITICA',
                'action': 'Cambio immediato password compromesse',
                'timeline': '24 ore'
            })

        self.recommendations.append({
            'priority': 'ALTA',
            'action': 'Attivare 2FA su tutti gli account',
            'timeline': '1 settimana'
        })

        self.recommendations.append({
            'priority': 'ALTA',
            'action': 'Usare password manager',
            'timeline': '2 settimane'
        })

        if len(self.data.social_media) > 5:
            self.recommendations.append({
                'priority': 'MEDIA',
                'action': 'Audit profili social',
                'timeline': '1 mese'
            })

# ============================================
# PDF REPORT GENERATOR
# ============================================

class PDFReportGenerator:
    """Generatore report PDF"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.elements = []
        self.styles = self._create_styles()
        self.chapter_num = 0
        self.section_num = 0

    def _create_styles(self):
        """Crea stili"""
        styles = {}

        styles['Title'] = ParagraphStyle(
            'Title', fontName='Times-Bold', fontSize=24, leading=30,
            alignment=TA_CENTER, spaceAfter=20, textColor=colors.HexColor('#16213e')
        )

        styles['Subtitle'] = ParagraphStyle(
            'Subtitle', fontName='Times-Italic', fontSize=14, leading=18,
            alignment=TA_CENTER, spaceAfter=30, textColor=colors.HexColor('#4a4a4a')
        )

        styles['Chapter'] = ParagraphStyle(
            'Chapter', fontName='Times-Bold', fontSize=16, leading=24,
            alignment=TA_LEFT, spaceBefore=30, spaceAfter=15, textColor=colors.HexColor('#16213e')
        )

        styles['Section'] = ParagraphStyle(
            'Section', fontName='Times-Bold', fontSize=14, leading=20,
            alignment=TA_LEFT, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor('#1f4068')
        )

        styles['Subsection'] = ParagraphStyle(
            'Subsection', fontName='Times-Bold', fontSize=12, leading=18,
            alignment=TA_LEFT, spaceBefore=15, spaceAfter=8, textColor=colors.HexColor('#162447')
        )

        styles['Normal'] = ParagraphStyle(
            'Normal', fontName='Times-Roman', fontSize=12, leading=18,
            alignment=TA_JUSTIFY, spaceBefore=6, spaceAfter=6
        )

        styles['ListItem'] = ParagraphStyle(
            'ListItem', fontName='Times-Roman', fontSize=11, leading=16,
            alignment=TA_LEFT, leftIndent=20, spaceBefore=3, spaceAfter=3
        )

        return styles

    def _add_header(self, logo_path=None):
        """Aggiunge intestazione"""
        now = datetime.now()

        # Logo
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=4*cm, height=2*cm)
                header_data = [['', '', logo]]
            except:
                header_data = [['', '', '']]
        else:
            header_data = [['', '', Paragraph("[LOGO]", self.styles['Normal'])]]

        header_table = Table(header_data, colWidths=[6*cm, 6*cm, 5*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        self.elements.append(header_table)
        self.elements.append(Spacer(1, 1*cm))

        # Titolo
        self.elements.append(Paragraph("REPORT INFO INVESTIGATIVO", self.styles['Title']))
        self.elements.append(Paragraph(
            f"Data: {now.strftime('%d/%m/%Y')} - Ora: {now.strftime('%H:%M:%S')}",
            self.styles['Subtitle']
        ))

        # Linea
        self.elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#16213e')))
        self.elements.append(Spacer(1, 0.5*cm))

    def add_chapter(self, title: str):
        """Aggiunge capitolo"""
        self.chapter_num += 1
        self.section_num = 0
        self.elements.append(Paragraph(f"CAPITOLO {self.chapter_num}: {title.upper()}", self.styles['Chapter']))
        self.elements.append(HRFlowable(width="60%", thickness=1, color=colors.HexColor('#16213e')))

    def add_section(self, title: str):
        """Aggiunge sezione"""
        self.section_num += 1
        self.elements.append(Paragraph(f"{self.chapter_num}.{self.section_num} {title}", self.styles['Section']))

    def add_subsection(self, title: str):
        """Aggiunge sottosezione"""
        self.elements.append(Paragraph(title, self.styles['Subsection']))

    def add_paragraph(self, text: str):
        """Aggiunge paragrafo"""
        self.elements.append(Paragraph(text, self.styles['Normal']))

    def add_list(self, items: List[str]):
        """Aggiunge lista"""
        for item in items:
            self.elements.append(Paragraph(f"• {item}", self.styles['ListItem']))

    def add_table(self, headers: List[str], data: List[List[str]]):
        """Aggiunge tabella"""
        table_data = [headers] + data
        col_width = (17*cm) / len(headers)

        table = Table(table_data, colWidths=[col_width] * len(headers))
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#16213e')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        self.elements.append(table)
        self.elements.append(Spacer(1, 0.3*cm))

    def add_info_box(self, title: str, content: str):
        """Aggiunge box info"""
        box_content = f"<b>{title}</b><br/><br/>{content}"
        box_data = [[Paragraph(box_content, self.styles['Normal'])]]
        box = Table(box_data, colWidths=[16*cm])
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#16213e')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        self.elements.append(box)
        self.elements.append(Spacer(1, 0.3*cm))

    def add_page_break(self):
        """Aggiunge interruzione pagina"""
        self.elements.append(PageBreak())

    def _add_page_number(self, canvas, doc):
        """Aggiunge numero pagina"""
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawCentredString(A4[0]/2, 1*cm, f"Pagina {doc.page}")
        canvas.setFont('Times-Italic', 8)
        canvas.drawCentredString(A4[0]/2, 0.7*cm, f"DOCUMENTO RISERVATO - {CONFIG['ORGANIZATION_NAME']}")
        canvas.restoreState()

    def generate(self, data, analysis, psych, pwd, security, logo_path=None):
        """Genera il report completo"""
        self.elements = []
        self.chapter_num = 0

        target_name = data.personal_info.full_name or "Target non identificato"

        # Header
        self._add_header(logo_path)

        # CAPITOLO 1: INTRODUZIONE
        self.add_chapter("INTRODUZIONE")

        self.add_section("Cos'è l'OSINT")
        self.add_paragraph(
            "L'OSINT (Open Source Intelligence) è una disciplina dell'intelligence che si occupa "
            "della raccolta, analisi e utilizzo di informazioni provenienti da fonti pubblicamente "
            "accessibili. Questa metodologia permette di costruire un quadro informativo completo "
            "attraverso l'aggregazione e correlazione di dati pubblici."
        )

        self.add_section("Metodologia")
        self.add_list([
            "<b>Raccolta</b>: Acquisizione dati da fonti pubbliche",
            "<b>Elaborazione</b>: Normalizzazione e strutturazione",
            "<b>Analisi</b>: Correlazione e identificazione pattern",
            "<b>Profilazione</b>: Costruzione profilo soggetto",
            "<b>Valutazione</b>: Assessment rischi e vulnerabilità"
        ])

        self.add_page_break()

        # CAPITOLO 2: SCHEDA SOGGETTO
        self.add_chapter("SCHEDA SOGGETTO")

        self.add_section("Dati Anagrafici")
        anagrafica = []
        if data.personal_info.full_name:
            anagrafica.append(["Nome", data.personal_info.full_name])
        if data.personal_info.date_of_birth:
            anagrafica.append(["Data Nascita", data.personal_info.date_of_birth])
        if data.personal_info.age:
            anagrafica.append(["Età", str(data.personal_info.age)])
        if data.personal_info.nationality:
            anagrafica.append(["Nazionalità", data.personal_info.nationality])
        if data.personal_info.occupation:
            anagrafica.append(["Professione", data.personal_info.occupation])

        if anagrafica:
            self.add_table(["Campo", "Valore"], anagrafica)
        else:
            self.add_paragraph("Dati anagrafici non disponibili.")

        self.add_section("Contatti")

        self.add_subsection("Email")
        if data.contact_info.emails:
            email_data = [[e['email'], e.get('domain', 'N/A')] for e in data.contact_info.emails]
            self.add_table(["Email", "Dominio"], email_data)
        else:
            self.add_paragraph("Nessuna email identificata.")

        self.add_subsection("Telefoni")
        if data.contact_info.phones:
            phone_data = [[p['number'], p.get('cleaned', '')] for p in data.contact_info.phones]
            self.add_table(["Numero", "Pulito"], phone_data)
        else:
            self.add_paragraph("Nessun telefono identificato.")

        self.add_section("Social Media")
        if data.social_media:
            social_data = [[p.platform, p.username or 'N/A'] for p in data.social_media]
            self.add_table(["Piattaforma", "Username"], social_data)
        else:
            self.add_paragraph("Nessun profilo social identificato.")

        self.add_section("Username")
        if data.usernames:
            self.add_list(data.usernames[:10])
        else:
            self.add_paragraph("Nessun username aggiuntivo.")

        self.add_page_break()

        # CAPITOLO 3: ANALISI DATI
        self.add_chapter("ANALISI E CORRELAZIONE DATI")

        self.add_section("Correlazioni")
        critical = [c for c in analysis.correlations if c.get('significance') == 'critical']
        high = [c for c in analysis.correlations if c.get('significance') == 'high']

        if critical:
            self.add_subsection("Correlazioni Critiche")
            for c in critical:
                self.add_info_box("ATTENZIONE", c['description'])

        if high:
            self.add_subsection("Correlazioni Significative")
            self.add_list([c['description'] for c in high])

        self.add_section("Data Breach")
        if data.data_breaches:
            self.add_paragraph(f"Coinvolto in <b>{len(data.data_breaches)}</b> data breach.")
            breach_data = [[b.breach_name, b.breach_date or 'N/D'] for b in data.data_breaches]
            self.add_table(["Breach", "Data"], breach_data)
        else:
            self.add_paragraph("Nessun breach noto.")

        self.add_section("Findings Chiave")
        self.add_list(analysis.key_findings)

        self.add_page_break()

        # CAPITOLO 4: PROFILO PSICOLOGICO
        self.add_chapter("PROFILO PSICOLOGICO")

        self.add_section("Pattern Comportamentali")
        if psych.behavioral_patterns:
            for p in psych.behavioral_patterns:
                self.add_paragraph(f"<b>{p['description']}</b>")
                self.add_paragraph(f"<i>Implicazione: {p['implication']}</i>")
        else:
            self.add_paragraph("Dati insufficienti per analisi comportamentale.")

        self.add_section("Profilo Rischio")
        risk_data = [
            ["Consapevolezza Privacy", psych.risk_profile.get('privacy_awareness', 'N/A').upper()],
            ["Security Consciousness", psych.risk_profile.get('security_consciousness', 'N/A').upper()],
        ]
        self.add_table(["Indicatore", "Livello"], risk_data)

        if psych.vulnerabilities:
            self.add_section("Vulnerabilità")
            self.add_list(psych.vulnerabilities)

        if psych.strengths:
            self.add_section("Punti di Forza")
            self.add_list(psych.strengths)

        self.add_section("Sintesi")
        self.add_paragraph(psych.summary)

        self.add_page_break()

        # CAPITOLO 5: SICUREZZA
        self.add_chapter("ANALISI SICUREZZA DIGITALE")

        self.add_section("Analisi Password")
        if pwd.strength_assessments:
            self.add_info_box(
                f"SICUREZZA PASSWORD: {pwd.security_level}",
                f"Score: {pwd.security_score}/100"
            )
            self.add_paragraph(f"<b>Metodo costruzione:</b> {pwd.construction_method}")

            if pwd.insights:
                self.add_subsection("Insight")
                self.add_list(pwd.insights)
        else:
            self.add_paragraph("Nessuna password da analizzare.")

        self.add_section("Postura di Sicurezza")
        self.add_info_box(
            f"GRADE: {security.posture['grade']}",
            f"Score: {security.posture['score']}/100"
        )

        self.add_section("Vulnerabilità")
        if security.vulnerabilities:
            for v in security.vulnerabilities:
                color = {'critical': '#c70039', 'high': '#ff5722', 'medium': '#ff9800'}.get(v['severity'], '#666')
                self.add_paragraph(f"<font color='{color}'><b>[{v['severity'].upper()}]</b></font> {v['type']}: {v['description']}")
        else:
            self.add_paragraph("Nessuna vulnerabilità critica identificata.")

        self.add_section("Minacce")
        if security.threats:
            threat_data = [[t['type'], t['likelihood'].upper(), t['impact'].upper()] for t in security.threats]
            self.add_table(["Minaccia", "Probabilità", "Impatto"], threat_data)

        self.add_page_break()

        # CAPITOLO 6: VALUTAZIONE
        self.add_chapter("VALUTAZIONE COMPLESSIVA")

        self.add_section("Digital Footprint")
        footprint_data = [
            ["Esposizione", analysis.exposure_level],
            ["Score", f"{analysis.footprint_score}/100"],
            ["Privacy Score", f"{security.privacy_score}/100"],
        ]
        self.add_table(["Metrica", "Valore"], footprint_data)

        self.add_section("Indicatori Rischio")
        if analysis.risk_indicators:
            for r in analysis.risk_indicators:
                self.add_paragraph(f"<b>{r['type']}</b> [{r['severity'].upper()}]: {r['description']}")

        self.add_section("Raccomandazioni")
        if security.recommendations:
            rec_data = [[r['priority'], r['action'], r['timeline']] for r in security.recommendations]
            self.add_table(["Priorità", "Azione", "Timeline"], rec_data)

        self.add_page_break()

        # CAPITOLO 7: CONCLUSIONI
        self.add_chapter("CONCLUSIONI")

        self.add_section("Sintesi Investigativa")
        self.add_paragraph(f"L'analisi OSINT su <b>{target_name}</b> ha evidenziato:")

        conclusions = []
        if data.social_media:
            conclusions.append(f"Presenza su {len(data.social_media)} piattaforme social")
        conclusions.append(f"Security Grade: {security.posture['grade']}")
        if data.data_breaches:
            conclusions.append(f"{len(data.data_breaches)} data breach")
        if data.raw_passwords:
            conclusions.append(f"{len(data.raw_passwords)} password esposte")

        self.add_list(conclusions)

        self.add_section("Avvertenze")
        self.add_paragraph(
            "<i>Questo report si basa su informazioni pubbliche. Le conclusioni sono "
            "probabilistiche e richiedono validazione. Documento riservato.</i>"
        )

        # Footer finale
        self.elements.append(Spacer(1, 2*cm))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        self.elements.append(Paragraph(
            f"<b>{CONFIG['ORGANIZATION_NAME']}</b><br/>"
            f"Agente Investigativo OSINT<br/>"
            f"Report generato il {datetime.now().strftime('%d/%m/%Y alle ore %H:%M')}",
            self.styles['Normal']
        ))

        # Genera PDF
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        doc.build(self.elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)

        return self.output_path

# ============================================
# MAIN INVESTIGATOR
# ============================================

class FidelinvestigatorAI:
    """Agente Investigativo OSINT"""

    def __init__(self):
        self.config = CONFIG
        self._ensure_directories()

    def _ensure_directories(self):
        """Crea directory necessarie"""
        os.makedirs(self.config['OUTPUT_DIR'], exist_ok=True)

    def _print_banner(self):
        """Stampa banner"""
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
║     Background: CIA | ROS | DIA | DCSA | DEA                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def investigate_file(self, html_path: str) -> str:
        """Investiga un file HTML"""
        if self.config['VERBOSE']:
            self._print_banner()
            print(f"\n[*] Analisi file: {html_path}")

        # Leggi HTML
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        if self.config['VERBOSE']:
            print(f"[✓] File caricato: {len(html_content)} bytes")

        # FASE 1: Parsing
        if self.config['VERBOSE']:
            print("\n[*] FASE 1: Parsing HTML...")

        parser = HTMLParser()
        data = parser.parse(html_content)

        if self.config['VERBOSE']:
            print(f"    [✓] Email: {len(data.contact_info.emails)}")
            print(f"    [✓] Social: {len(data.social_media)}")
            print(f"    [✓] Breach: {len(data.data_breaches)}")
            print(f"    [✓] Password: {len(data.raw_passwords)}")

        # FASE 2: Analisi
        if self.config['VERBOSE']:
            print("\n[*] FASE 2: Analisi dati...")

        analyzer = DataAnalyzer(data)
        analysis = analyzer.analyze()

        if self.config['VERBOSE']:
            print(f"    [✓] Correlazioni: {len(analysis.correlations)}")
            print(f"    [✓] Esposizione: {analysis.exposure_level}")

        # FASE 3: Profilo psicologico
        if self.config['VERBOSE']:
            print("\n[*] FASE 3: Profilazione psicologica...")

        profiler = PsychologicalProfiler(data)
        psych = profiler.profile()

        if self.config['VERBOSE']:
            print(f"    [✓] Pattern: {len(psych.behavioral_patterns)}")
            print(f"    [✓] Privacy: {psych.risk_profile.get('privacy_awareness', 'N/A')}")

        # FASE 4: Password
        if self.config['VERBOSE']:
            print("\n[*] FASE 4: Analisi password...")

        pwd_analyzer = PasswordAnalyzer(data)
        pwd = pwd_analyzer.analyze()

        if self.config['VERBOSE']:
            print(f"    [✓] Analizzate: {len(pwd.strength_assessments)}")
            print(f"    [✓] Sicurezza: {pwd.security_level}")

        # FASE 5: Security
        if self.config['VERBOSE']:
            print("\n[*] FASE 5: Valutazione sicurezza...")

        assessor = SecurityAssessor(data, analysis, pwd)
        security = assessor.assess()

        if self.config['VERBOSE']:
            print(f"    [✓] Grade: {security.posture['grade']}")
            print(f"    [✓] Score: {security.posture['score']}/100")

        # FASE 6: Report PDF
        if self.config['VERBOSE']:
            print("\n[*] FASE 6: Generazione PDF...")

        # Nome file output
        target_name = data.personal_info.full_name or "Target"
        safe_name = "".join(c if c.isalnum() else "_" for c in target_name)[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Report_{safe_name}_{timestamp}.pdf"
        output_path = os.path.join(self.config['OUTPUT_DIR'], output_filename)

        # Genera PDF
        generator = PDFReportGenerator(output_path)
        pdf_path = generator.generate(
            data, analysis, psych, pwd, security,
            self.config.get('LOGO_PATH')
        )

        if self.config['VERBOSE']:
            print(f"    [✓] PDF generato: {pdf_path}")

            print("\n" + "="*60)
            print("           INVESTIGAZIONE COMPLETATA")
            print("="*60)
            print(f"""
    Target:          {target_name}
    Security Grade:  {security.posture['grade']}
    Esposizione:     {analysis.exposure_level}
    Privacy Score:   {security.privacy_score}/100

    Report PDF:      {pdf_path}
            """)
            print("="*60)

        return pdf_path

    def investigate_all(self) -> List[str]:
        """Investiga tutti i file HTML nella cartella input"""
        input_dir = self.config['INPUT_DIR']

        if not os.path.exists(input_dir):
            print(f"[!] Cartella non trovata: {input_dir}")
            return []

        html_files = list(Path(input_dir).glob('*.html')) + list(Path(input_dir).glob('*.htm'))

        if not html_files:
            print(f"[!] Nessun file HTML trovato in: {input_dir}")
            return []

        if self.config['VERBOSE']:
            print(f"\n[*] Trovati {len(html_files)} file HTML da analizzare")

        reports = []
        for html_file in html_files:
            try:
                report = self.investigate_file(str(html_file))
                reports.append(report)
            except Exception as e:
                print(f"[!] Errore analizzando {html_file}: {e}")

        return reports

# ============================================
# ENTRY POINT
# ============================================

def main():
    """Entry point principale"""
    import argparse

    parser = argparse.ArgumentParser(
        description='FidelinvestigatorAI - Agente Investigativo OSINT',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('file', nargs='?', help='File HTML da analizzare (opzionale)')
    parser.add_argument('--all', action='store_true', help='Analizza tutti i file nella cartella input')
    parser.add_argument('--input-dir', help='Cartella input')
    parser.add_argument('--output-dir', help='Cartella output')
    parser.add_argument('--logo', help='Percorso logo')
    parser.add_argument('-q', '--quiet', action='store_true', help='Modalità silenziosa')

    args = parser.parse_args()

    # Aggiorna config se necessario
    if args.input_dir:
        CONFIG['INPUT_DIR'] = args.input_dir
    if args.output_dir:
        CONFIG['OUTPUT_DIR'] = args.output_dir
    if args.logo:
        CONFIG['LOGO_PATH'] = args.logo
    if args.quiet:
        CONFIG['VERBOSE'] = False

    # Inizializza agente
    agent = FidelinvestigatorAI()

    if args.file:
        # Analizza file specifico
        agent.investigate_file(args.file)
    elif args.all:
        # Analizza tutti
        agent.investigate_all()
    else:
        # Default: analizza tutti nella cartella configurata
        agent.investigate_all()

if __name__ == "__main__":
    main()
