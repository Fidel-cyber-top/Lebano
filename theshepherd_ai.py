"""
TheShepherdAI - Integration Module for TheBlackGoat Platform
=============================================================

Modulo di integrazione tra la piattaforma OSINT TheBlackGoat e il sistema
di analisi FidelinvestigatorAI. Gestisce l'input di dati JSON dal workflow
attivo e produce report intelligence unificati.

Attivazione: Bottone "TheShepherdAI" nella piattaforma

Author: FidelinvestigatorAI
Version: 1.0.0
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Import del sistema FidelinvestigatorAI
from fidelinvestigator.unified_report_generator import (
    UnifiedReportGenerator,
    UnifiedReportData,
    PsychologicalProfile,
    create_unified_report_from_osint
)

from fidelinvestigator.intelligence_report_framework import (
    ConfidenceLevel,
    SourceReliability,
    InformationAccuracy,
    Source,
    KeyJudgment
)


@dataclass
class WorkflowData:
    """
    Struttura dati per i JSON del workflow TheBlackGoat

    Supporta multiple strutture di input:
    - Output di tool OSINT (theHarvester, Sherlock, etc.)
    - Database breach (HaveIBeenPwned, DeHashed)
    - Social media scraping
    - Ricerche WHOIS/DNS
    """

    # Identificazione target
    target_name: str = ""
    target_email: str = ""
    target_username: str = ""

    # Dati raccolti
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    social_profiles: List[Dict] = field(default_factory=list)
    data_breaches: List[Dict] = field(default_factory=list)
    passwords: List[str] = field(default_factory=list)
    domains: List[Dict] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    locations: List[Dict] = field(default_factory=list)

    # Metadata workflow
    workflow_id: str = ""
    workflow_name: str = ""
    collected_at: str = ""
    tools_used: List[str] = field(default_factory=list)

    # Dati raw
    raw_data: Dict[str, Any] = field(default_factory=dict)


class TheBlackGoatParser:
    """
    Parser per i diversi formati JSON che TheBlackGoat può produrre
    """

    # Mapping dei tool OSINT comuni
    TOOL_PARSERS = {
        'theharvester': '_parse_theharvester',
        'sherlock': '_parse_sherlock',
        'holehe': '_parse_holehe',
        'maigret': '_parse_maigret',
        'socialscan': '_parse_socialscan',
        'phoneinfoga': '_parse_phoneinfoga',
        'ghunt': '_parse_ghunt',
        'hibp': '_parse_hibp',
        'dehashed': '_parse_dehashed',
        'intelx': '_parse_intelx',
        'spiderfoot': '_parse_spiderfoot',
        'maltego': '_parse_maltego',
        'recon-ng': '_parse_reconng',
        'osintgram': '_parse_osintgram',
        'twint': '_parse_twint',
        'generic': '_parse_generic'
    }

    def __init__(self):
        self.workflow_data = WorkflowData()
        self.errors = []
        self.warnings = []

    def parse_json_file(self, file_path: str) -> WorkflowData:
        """Parse un singolo file JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return self.parse_json_data(data, source_file=file_path)

        except json.JSONDecodeError as e:
            self.errors.append(f"JSON decode error in {file_path}: {e}")
            return self.workflow_data
        except Exception as e:
            self.errors.append(f"Error parsing {file_path}: {e}")
            return self.workflow_data

    def parse_json_data(self, data: Union[Dict, List],
                        source_file: str = None,
                        tool_hint: str = None) -> WorkflowData:
        """
        Parse dati JSON con auto-detection del formato

        Args:
            data: Dati JSON (dict o list)
            source_file: Path del file sorgente (per dedurre il tool)
            tool_hint: Hint esplicito sul tool utilizzato
        """
        # Determina il tool/formato
        tool = self._detect_tool(data, source_file, tool_hint)

        # Chiama il parser specifico
        parser_method = self.TOOL_PARSERS.get(tool, '_parse_generic')
        parser = getattr(self, parser_method, self._parse_generic)

        try:
            parser(data)
        except Exception as e:
            self.errors.append(f"Error in {parser_method}: {e}")
            # Fallback a parser generico
            self._parse_generic(data)

        # Salva dati raw
        self.workflow_data.raw_data[tool] = data

        return self.workflow_data

    def parse_workflow_directory(self, directory: str) -> WorkflowData:
        """
        Parse tutti i file JSON in una directory di workflow

        Args:
            directory: Path della directory con i file JSON
        """
        json_files = glob.glob(os.path.join(directory, '*.json'))

        print(f"[*] Trovati {len(json_files)} file JSON in {directory}")

        for json_file in json_files:
            print(f"    Parsing: {os.path.basename(json_file)}")
            self.parse_json_file(json_file)

        return self.workflow_data

    def _detect_tool(self, data: Union[Dict, List],
                    source_file: str = None,
                    tool_hint: str = None) -> str:
        """Auto-detect del tool OSINT dal formato dati"""

        if tool_hint:
            return tool_hint.lower()

        # Check dal nome file
        if source_file:
            filename = os.path.basename(source_file).lower()
            for tool in self.TOOL_PARSERS.keys():
                if tool in filename:
                    return tool

        # Check dalla struttura dati
        if isinstance(data, dict):
            # theHarvester
            if 'hosts' in data and 'emails' in data:
                return 'theharvester'

            # Sherlock
            if any('url' in str(v) and 'exists' in str(v) for v in data.values() if isinstance(v, dict)):
                return 'sherlock'

            # Holehe
            if any('exists' in str(v) for v in data.values() if isinstance(v, dict)):
                return 'holehe'

            # HIBP
            if 'breaches' in data or 'Breaches' in data:
                return 'hibp'

            # DeHashed
            if 'entries' in data and any('password' in str(e).lower() for e in data.get('entries', [])):
                return 'dehashed'

            # SpiderFoot
            if 'data' in data and 'meta' in data:
                return 'spiderfoot'

            # GHunt
            if 'email' in data and 'profile_pic' in data:
                return 'ghunt'

        return 'generic'

    # =========================================================================
    # PARSER SPECIFICI PER TOOL
    # =========================================================================

    def _parse_theharvester(self, data: Dict):
        """Parser per output theHarvester"""
        if 'emails' in data:
            self.workflow_data.emails.extend(data['emails'])
        if 'hosts' in data:
            for host in data['hosts']:
                if isinstance(host, dict):
                    self.workflow_data.domains.append(host)
                else:
                    self.workflow_data.domains.append({'domain': host})
        if 'ips' in data:
            self.workflow_data.ip_addresses.extend(data['ips'])

        self.workflow_data.tools_used.append('theHarvester')

    def _parse_sherlock(self, data: Dict):
        """Parser per output Sherlock"""
        for site, info in data.items():
            if isinstance(info, dict) and info.get('exists', False):
                self.workflow_data.social_profiles.append({
                    'platform': site,
                    'url': info.get('url', ''),
                    'username': self.workflow_data.target_username,
                    'exists': True
                })
                if info.get('url'):
                    # Estrai username dall'URL se non presente
                    url_parts = info['url'].rstrip('/').split('/')
                    if url_parts:
                        self.workflow_data.usernames.append(url_parts[-1])

        self.workflow_data.tools_used.append('Sherlock')

    def _parse_holehe(self, data: Dict):
        """Parser per output Holehe (email checker)"""
        for service, info in data.items():
            if isinstance(info, dict):
                if info.get('exists', False) or info.get('registered', False):
                    self.workflow_data.social_profiles.append({
                        'platform': service,
                        'email_registered': True,
                        'email': self.workflow_data.target_email
                    })

        self.workflow_data.tools_used.append('Holehe')

    def _parse_maigret(self, data: Dict):
        """Parser per output Maigret"""
        if 'results' in data:
            for result in data['results']:
                if result.get('status', '') == 'Claimed':
                    self.workflow_data.social_profiles.append({
                        'platform': result.get('site_name', ''),
                        'url': result.get('url', ''),
                        'username': result.get('username', ''),
                        'exists': True
                    })

        self.workflow_data.tools_used.append('Maigret')

    def _parse_socialscan(self, data: Dict):
        """Parser per output SocialScan"""
        if isinstance(data, list):
            for item in data:
                if item.get('available') == False:  # Account exists
                    self.workflow_data.social_profiles.append({
                        'platform': item.get('platform', ''),
                        'username': item.get('username', ''),
                        'exists': True
                    })

        self.workflow_data.tools_used.append('SocialScan')

    def _parse_phoneinfoga(self, data: Dict):
        """Parser per output PhoneInfoga"""
        if 'number' in data:
            self.workflow_data.phones.append(data['number'])

        if 'carrier' in data or 'country' in data:
            self.workflow_data.locations.append({
                'type': 'phone_location',
                'country': data.get('country', ''),
                'carrier': data.get('carrier', ''),
                'line_type': data.get('line_type', '')
            })

        if 'social_media' in data:
            for platform, info in data['social_media'].items():
                if info:
                    self.workflow_data.social_profiles.append({
                        'platform': platform,
                        'phone_linked': True
                    })

        self.workflow_data.tools_used.append('PhoneInfoga')

    def _parse_ghunt(self, data: Dict):
        """Parser per output GHunt (Google account)"""
        if 'email' in data:
            self.workflow_data.emails.append(data['email'])

        if 'name' in data:
            self.workflow_data.target_name = data['name']

        if 'profile_pic' in data:
            self.workflow_data.social_profiles.append({
                'platform': 'Google',
                'email': data.get('email', ''),
                'profile_picture': data.get('profile_pic', ''),
                'name': data.get('name', '')
            })

        if 'maps_reviews' in data:
            for review in data.get('maps_reviews', []):
                if 'location' in review:
                    self.workflow_data.locations.append({
                        'type': 'google_review',
                        'location': review['location']
                    })

        self.workflow_data.tools_used.append('GHunt')

    def _parse_hibp(self, data: Dict):
        """Parser per output HaveIBeenPwned"""
        breaches = data.get('breaches', data.get('Breaches', []))

        for breach in breaches:
            self.workflow_data.data_breaches.append({
                'source': breach.get('Name', breach.get('name', 'Unknown')),
                'date': breach.get('BreachDate', breach.get('breach_date', '')),
                'data_types': breach.get('DataClasses', breach.get('data_types', [])),
                'description': breach.get('Description', ''),
                'is_verified': breach.get('IsVerified', True)
            })

        self.workflow_data.tools_used.append('HaveIBeenPwned')

    def _parse_dehashed(self, data: Dict):
        """Parser per output DeHashed"""
        entries = data.get('entries', data.get('results', []))

        for entry in entries:
            # Email
            if entry.get('email'):
                if entry['email'] not in self.workflow_data.emails:
                    self.workflow_data.emails.append(entry['email'])

            # Username
            if entry.get('username'):
                if entry['username'] not in self.workflow_data.usernames:
                    self.workflow_data.usernames.append(entry['username'])

            # Password
            if entry.get('password'):
                self.workflow_data.passwords.append(entry['password'])

            # Breach info
            if entry.get('database_name') or entry.get('source'):
                self.workflow_data.data_breaches.append({
                    'source': entry.get('database_name', entry.get('source', '')),
                    'email': entry.get('email', ''),
                    'username': entry.get('username', ''),
                    'has_password': bool(entry.get('password'))
                })

            # IP
            if entry.get('ip_address'):
                self.workflow_data.ip_addresses.append(entry['ip_address'])

            # Phone
            if entry.get('phone'):
                self.workflow_data.phones.append(entry['phone'])

        self.workflow_data.tools_used.append('DeHashed')

    def _parse_intelx(self, data: Dict):
        """Parser per output IntelX"""
        if 'records' in data:
            for record in data['records']:
                # Estrai in base al tipo
                record_type = record.get('type', '')

                if 'email' in record_type.lower():
                    if record.get('value'):
                        self.workflow_data.emails.append(record['value'])

                elif 'password' in record_type.lower():
                    if record.get('value'):
                        self.workflow_data.passwords.append(record['value'])

                elif 'breach' in record_type.lower():
                    self.workflow_data.data_breaches.append({
                        'source': record.get('source', 'IntelX'),
                        'data': record.get('value', '')
                    })

        self.workflow_data.tools_used.append('IntelX')

    def _parse_spiderfoot(self, data: Dict):
        """Parser per output SpiderFoot"""
        if 'data' in data:
            for item in data['data']:
                item_type = item.get('type', '')
                value = item.get('data', '')

                if 'EMAIL' in item_type:
                    self.workflow_data.emails.append(value)
                elif 'PHONE' in item_type:
                    self.workflow_data.phones.append(value)
                elif 'SOCIAL' in item_type or 'ACCOUNT' in item_type:
                    self.workflow_data.social_profiles.append({
                        'platform': item.get('source', ''),
                        'url': value
                    })
                elif 'IP' in item_type:
                    self.workflow_data.ip_addresses.append(value)
                elif 'DOMAIN' in item_type:
                    self.workflow_data.domains.append({'domain': value})
                elif 'BREACH' in item_type or 'LEAK' in item_type:
                    self.workflow_data.data_breaches.append({
                        'source': item.get('source', ''),
                        'data': value
                    })

        self.workflow_data.tools_used.append('SpiderFoot')

    def _parse_maltego(self, data: Dict):
        """Parser per output Maltego (GraphML/JSON export)"""
        entities = data.get('entities', data.get('nodes', []))

        for entity in entities:
            entity_type = entity.get('type', '').lower()
            value = entity.get('value', entity.get('properties', {}).get('value', ''))

            if 'email' in entity_type:
                self.workflow_data.emails.append(value)
            elif 'phone' in entity_type:
                self.workflow_data.phones.append(value)
            elif 'person' in entity_type:
                self.workflow_data.target_name = value
            elif 'alias' in entity_type or 'username' in entity_type:
                self.workflow_data.usernames.append(value)
            elif 'domain' in entity_type or 'website' in entity_type:
                self.workflow_data.domains.append({'domain': value})
            elif 'social' in entity_type or 'profile' in entity_type:
                self.workflow_data.social_profiles.append({
                    'platform': entity.get('platform', ''),
                    'url': value
                })

        self.workflow_data.tools_used.append('Maltego')

    def _parse_reconng(self, data: Dict):
        """Parser per output Recon-ng"""
        if 'hosts' in data:
            for host in data['hosts']:
                self.workflow_data.domains.append({
                    'domain': host.get('host', ''),
                    'ip': host.get('ip_address', '')
                })

        if 'contacts' in data:
            for contact in data['contacts']:
                if contact.get('email'):
                    self.workflow_data.emails.append(contact['email'])
                if contact.get('first_name') or contact.get('last_name'):
                    name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                    if not self.workflow_data.target_name:
                        self.workflow_data.target_name = name

        if 'credentials' in data:
            for cred in data['credentials']:
                if cred.get('password'):
                    self.workflow_data.passwords.append(cred['password'])
                if cred.get('username'):
                    self.workflow_data.usernames.append(cred['username'])

        self.workflow_data.tools_used.append('Recon-ng')

    def _parse_osintgram(self, data: Dict):
        """Parser per output Osintgram (Instagram OSINT)"""
        if 'target' in data:
            self.workflow_data.target_username = data['target']

        profile = data.get('profile', {})
        if profile:
            self.workflow_data.social_profiles.append({
                'platform': 'Instagram',
                'username': profile.get('username', ''),
                'full_name': profile.get('full_name', ''),
                'bio': profile.get('biography', ''),
                'followers': profile.get('followers', 0),
                'following': profile.get('following', 0),
                'posts': profile.get('media_count', 0),
                'is_private': profile.get('is_private', False),
                'profile_pic': profile.get('profile_pic_url', '')
            })

            if profile.get('full_name'):
                self.workflow_data.target_name = profile['full_name']

        # Geolocalizzazioni dai post
        if 'locations' in data:
            for loc in data['locations']:
                self.workflow_data.locations.append({
                    'type': 'instagram_post',
                    'name': loc.get('name', ''),
                    'lat': loc.get('lat'),
                    'lng': loc.get('lng')
                })

        # Email trovate
        if 'emails' in data:
            self.workflow_data.emails.extend(data['emails'])

        self.workflow_data.tools_used.append('Osintgram')

    def _parse_twint(self, data: Dict):
        """Parser per output Twint (Twitter OSINT)"""
        if isinstance(data, list):
            # Lista di tweet
            for tweet in data:
                if tweet.get('username') and tweet['username'] not in self.workflow_data.usernames:
                    self.workflow_data.usernames.append(tweet['username'])

        elif isinstance(data, dict):
            if 'user' in data:
                user = data['user']
                self.workflow_data.social_profiles.append({
                    'platform': 'Twitter',
                    'username': user.get('username', ''),
                    'display_name': user.get('displayname', ''),
                    'bio': user.get('bio', ''),
                    'followers': user.get('followers', 0),
                    'following': user.get('following', 0),
                    'location': user.get('location', ''),
                    'joined': user.get('join_date', '')
                })

                if user.get('displayname'):
                    self.workflow_data.target_name = user['displayname']

        self.workflow_data.tools_used.append('Twint')

    def _parse_generic(self, data: Union[Dict, List]):
        """Parser generico per formati non riconosciuti"""

        def extract_from_value(value: Any, parent_key: str = ''):
            """Estrae dati ricorsivamente"""
            if isinstance(value, str):
                # Email pattern
                import re
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, value)
                for email in emails:
                    if email not in self.workflow_data.emails:
                        self.workflow_data.emails.append(email)

                # Phone pattern
                phone_pattern = r'\+?[0-9]{1,3}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{4,10}'
                phones = re.findall(phone_pattern, value)
                for phone in phones:
                    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
                    if len(cleaned) >= 8 and cleaned not in self.workflow_data.phones:
                        self.workflow_data.phones.append(phone)

                # Username pattern (@ mention)
                username_pattern = r'@([a-zA-Z0-9_]{3,30})'
                usernames = re.findall(username_pattern, value)
                for username in usernames:
                    if username not in self.workflow_data.usernames:
                        self.workflow_data.usernames.append(username)

                # URL pattern (social profiles)
                url_pattern = r'https?://(?:www\.)?(facebook|instagram|twitter|linkedin|github|tiktok)[^\s]+'
                urls = re.findall(url_pattern, value.lower())
                for platform in urls:
                    self.workflow_data.social_profiles.append({
                        'platform': platform.capitalize(),
                        'url': value
                    })

            elif isinstance(value, dict):
                for k, v in value.items():
                    extract_from_value(v, k)

            elif isinstance(value, list):
                for item in value:
                    extract_from_value(item, parent_key)

        # Estrai ricorsivamente
        extract_from_value(data)

        if 'Generic' not in self.workflow_data.tools_used:
            self.workflow_data.tools_used.append('Generic Parser')


class TheShepherdAI:
    """
    Orchestratore principale per l'analisi OSINT da TheBlackGoat

    Flusso:
    1. Riceve dati JSON dal workflow attivo
    2. Parsa e normalizza i dati
    3. Esegue analisi FidelinvestigatorAI
    4. Genera report unificato (HTML, DOCX, PDF)
    """

    def __init__(self,
                 output_dir: str = "./reports",
                 anthropic_api_key: str = None,
                 openai_api_key: str = None):
        """
        Inizializza TheShepherdAI

        Args:
            output_dir: Directory per i report generati
            anthropic_api_key: API key per Claude (analisi psicologica)
            openai_api_key: API key per GPT-4 (correlazione dati)
        """
        self.output_dir = output_dir
        self.anthropic_api_key = anthropic_api_key
        self.openai_api_key = openai_api_key

        self.parser = TheBlackGoatParser()

        os.makedirs(output_dir, exist_ok=True)

    def analyze_workflow(self,
                        workflow_path: str = None,
                        json_data: Union[Dict, List] = None,
                        json_files: List[str] = None,
                        target_name: str = None) -> Dict[str, str]:
        """
        Analizza un workflow completo e genera report

        Args:
            workflow_path: Path a directory con file JSON
            json_data: Dati JSON diretti
            json_files: Lista di file JSON da processare
            target_name: Nome del target (opzionale)

        Returns:
            Dict con percorsi dei report generati (html, docx, pdf)
        """
        print("=" * 70)
        print("THE SHEPHERD AI - OSINT Analysis Engine")
        print("Powered by FidelinvestigatorAI")
        print("=" * 70)

        # 1. Parse dei dati
        print("\n[1/5] Parsing dati OSINT...")

        if workflow_path and os.path.isdir(workflow_path):
            self.parser.parse_workflow_directory(workflow_path)
        elif json_files:
            for jf in json_files:
                self.parser.parse_json_file(jf)
        elif json_data:
            self.parser.parse_json_data(json_data)
        else:
            raise ValueError("Specificare workflow_path, json_data o json_files")

        workflow_data = self.parser.workflow_data

        # Determina nome target
        if target_name:
            workflow_data.target_name = target_name
        elif not workflow_data.target_name:
            # Prova a dedurre dal primo username o email
            if workflow_data.usernames:
                workflow_data.target_name = workflow_data.usernames[0]
            elif workflow_data.emails:
                email = workflow_data.emails[0]
                workflow_data.target_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            else:
                workflow_data.target_name = "Unknown Target"

        print(f"    Target: {workflow_data.target_name}")
        print(f"    Emails: {len(workflow_data.emails)}")
        print(f"    Phones: {len(workflow_data.phones)}")
        print(f"    Usernames: {len(workflow_data.usernames)}")
        print(f"    Social Profiles: {len(workflow_data.social_profiles)}")
        print(f"    Data Breaches: {len(workflow_data.data_breaches)}")
        print(f"    Passwords: {len(workflow_data.passwords)}")
        print(f"    Tools used: {', '.join(workflow_data.tools_used)}")

        # 2. Converti in formato OSINT standard
        print("\n[2/5] Normalizzazione dati...")
        osint_data = self._convert_to_osint_format(workflow_data)

        # 3. Esegui analisi
        print("\n[3/5] Esecuzione analisi...")
        analysis_data = self._run_analysis(osint_data)
        psych_profile = self._run_psychological_profile(osint_data, analysis_data)
        security_assessment = self._run_security_assessment(osint_data, analysis_data)

        # 4. Genera report
        print("\n[4/5] Generazione report unificato...")
        report_paths = create_unified_report_from_osint(
            osint_data=osint_data,
            analysis_data=analysis_data,
            psych_profile=psych_profile,
            security_assessment=security_assessment,
            subject_name=workflow_data.target_name,
            output_dir=self.output_dir,
            anthropic_api_key=self.anthropic_api_key
        )

        # 5. Summary
        print("\n[5/5] Completamento...")
        print("\n" + "=" * 70)
        print("ANALISI COMPLETATA - THE SHEPHERD AI")
        print("=" * 70)
        print(f"\nTarget: {workflow_data.target_name}")
        print(f"Security Grade: {security_assessment.get('security_grade', 'N/A')}")
        print(f"Risk Level: {analysis_data.get('base_analysis', {}).get('exposure_level', 'N/A')}")
        print(f"\nReport generati:")
        for fmt, path in report_paths.items():
            size = os.path.getsize(path)
            print(f"  {fmt.upper():5}: {path} ({size:,} bytes)")

        return report_paths

    def _convert_to_osint_format(self, workflow_data: WorkflowData) -> Dict[str, Any]:
        """Converte WorkflowData nel formato OSINT standard"""
        return {
            'emails': list(set(workflow_data.emails)),
            'phones': list(set(workflow_data.phones)),
            'usernames': list(set(workflow_data.usernames)),
            'social_profiles': workflow_data.social_profiles,
            'breaches': workflow_data.data_breaches,
            'passwords': workflow_data.passwords,
            'ips': workflow_data.ip_addresses,
            'domains': workflow_data.domains,
            'locations': workflow_data.locations
        }

    def _run_analysis(self, osint_data: Dict) -> Dict[str, Any]:
        """Esegue analisi base dei dati"""
        # Calcola score
        score = 0
        factors = []

        email_count = len(osint_data.get('emails', []))
        if email_count > 0:
            score += min(email_count * 10, 30)
            factors.append(f"{email_count} email esposte")

        social_count = len(osint_data.get('social_profiles', []))
        if social_count > 0:
            score += min(social_count * 8, 25)
            factors.append(f"{social_count} profili social identificati")

        breach_count = len(osint_data.get('breaches', []))
        if breach_count > 0:
            score += min(breach_count * 15, 30)
            factors.append(f"{breach_count} data breach rilevati")

        password_count = len(osint_data.get('passwords', []))
        if password_count > 0:
            score += min(password_count * 20, 40)
            factors.append(f"{password_count} password esposte - CRITICO")

        # Determina livello
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
            'base_analysis': {
                'digital_footprint_score': min(score, 100),
                'exposure_level': level,
                'risk_factors': factors,
                'data_summary': {
                    'emails': email_count,
                    'social_profiles': social_count,
                    'breaches': breach_count,
                    'passwords': password_count,
                    'usernames': len(osint_data.get('usernames', [])),
                    'ip_addresses': len(osint_data.get('ips', []))
                }
            }
        }

    def _run_psychological_profile(self, osint_data: Dict, analysis: Dict) -> Dict[str, Any]:
        """Genera profilo psicologico base"""
        base = analysis.get('base_analysis', {})

        # Big Five estimation
        big_five = {
            'openness': 50,
            'conscientiousness': 50,
            'extraversion': 50,
            'agreeableness': 50,
            'neuroticism': 50
        }

        social_count = len(osint_data.get('social_profiles', []))
        if social_count > 5:
            big_five['extraversion'] += 20
            big_five['openness'] += 10
        elif social_count < 2:
            big_five['extraversion'] -= 15

        breach_count = len(osint_data.get('breaches', []))
        if breach_count > 3:
            big_five['conscientiousness'] -= 15
            big_five['neuroticism'] += 10

        password_count = len(osint_data.get('passwords', []))
        if password_count > 0:
            big_five['conscientiousness'] -= 20

        # Normalize
        for key in big_five:
            big_five[key] = max(0, min(100, big_five[key]))

        return {
            'ai_profile': '',
            'base_metrics': {
                'big_five': big_five,
                'risk_profile': {
                    'security_consciousness': 'BASSA' if password_count > 0 else 'MEDIA'
                }
            }
        }

    def _run_security_assessment(self, osint_data: Dict, analysis: Dict) -> Dict[str, Any]:
        """Valutazione sicurezza"""
        vulnerabilities = []
        threats = []
        score = 100

        # Email exposure
        email_count = len(osint_data.get('emails', []))
        if email_count > 0:
            vulnerabilities.append({
                'type': 'EMAIL_EXPOSURE',
                'severity': 'MEDIA',
                'description': f"{email_count} indirizzi email esposti pubblicamente"
            })
            score -= email_count * 5

        # Data breaches
        breach_count = len(osint_data.get('breaches', []))
        if breach_count > 0:
            vulnerabilities.append({
                'type': 'DATA_BREACH',
                'severity': 'ALTA',
                'description': f"Presente in {breach_count} data breach noti"
            })
            score -= breach_count * 15
            threats.append('Credential Stuffing Attack')

        # Passwords
        password_count = len(osint_data.get('passwords', []))
        if password_count > 0:
            vulnerabilities.append({
                'type': 'PASSWORD_EXPOSURE',
                'severity': 'CRITICA',
                'description': f"{password_count} password esposte in chiaro"
            })
            score -= 30
            threats.extend(['Account Takeover', 'Identity Theft'])

        # Social profiles
        social_count = len(osint_data.get('social_profiles', []))
        if social_count > 5:
            vulnerabilities.append({
                'type': 'LARGE_DIGITAL_FOOTPRINT',
                'severity': 'MEDIA',
                'description': "Ampia presenza social aumenta superficie di attacco"
            })
            score -= 10
            threats.extend(['Social Engineering', 'Spear Phishing'])

        # Grade
        score = max(0, score)
        if score >= 90:
            grade = 'A'
        elif score >= 80:
            grade = 'B'
        elif score >= 70:
            grade = 'C'
        elif score >= 60:
            grade = 'D'
        else:
            grade = 'F'

        # Recommendations
        recommendations = []
        if password_count > 0:
            recommendations.append('URGENTE: Cambiare immediatamente tutte le password esposte')
            recommendations.append('Attivare autenticazione a due fattori su tutti gli account')
        if breach_count > 0:
            recommendations.append('Verificare e aggiornare credenziali account compromessi')
            recommendations.append('Monitorare attività sospette sugli account')
        if social_count > 3:
            recommendations.append('Rivedere impostazioni privacy sui profili social')
            recommendations.append('Limitare informazioni personali condivise pubblicamente')

        return {
            'security_score': score,
            'security_grade': grade,
            'vulnerabilities': vulnerabilities,
            'threats': list(set(threats)),
            'recommendations': recommendations
        }


# =============================================================================
# API / ENDPOINT FUNCTIONS
# =============================================================================

def run_shepherd_analysis(
    workflow_path: str = None,
    json_data: Union[Dict, List] = None,
    json_files: List[str] = None,
    target_name: str = None,
    output_dir: str = "./reports",
    anthropic_api_key: str = None
) -> Dict[str, str]:
    """
    Funzione principale per lanciare l'analisi TheShepherdAI

    Chiamata dal bottone "TheShepherdAI" nella piattaforma TheBlackGoat

    Args:
        workflow_path: Directory con file JSON del workflow
        json_data: Dati JSON diretti (alternativa)
        json_files: Lista file JSON (alternativa)
        target_name: Nome del target
        output_dir: Directory output report
        anthropic_api_key: API key Claude

    Returns:
        Dict con percorsi report generati
    """
    shepherd = TheShepherdAI(
        output_dir=output_dir,
        anthropic_api_key=anthropic_api_key
    )

    return shepherd.analyze_workflow(
        workflow_path=workflow_path,
        json_data=json_data,
        json_files=json_files,
        target_name=target_name
    )


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Entry point CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description='TheShepherdAI - OSINT Analysis Engine for TheBlackGoat'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Path a directory workflow o file JSON'
    )
    parser.add_argument(
        '-t', '--target',
        help='Nome del target'
    )
    parser.add_argument(
        '-o', '--output',
        default='./reports',
        help='Directory output report'
    )
    parser.add_argument(
        '--anthropic-key',
        help='Anthropic API Key per analisi avanzata'
    )

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        return

    # Determina tipo input
    if os.path.isdir(args.input):
        run_shepherd_analysis(
            workflow_path=args.input,
            target_name=args.target,
            output_dir=args.output,
            anthropic_api_key=args.anthropic_key
        )
    elif os.path.isfile(args.input) and args.input.endswith('.json'):
        run_shepherd_analysis(
            json_files=[args.input],
            target_name=args.target,
            output_dir=args.output,
            anthropic_api_key=args.anthropic_key
        )
    else:
        print(f"[!] Input non valido: {args.input}")


if __name__ == "__main__":
    main()
