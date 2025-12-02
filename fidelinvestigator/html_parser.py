"""
OSINT HTML Parser - Modulo di parsing per report HTML OSINT
============================================================

Questo modulo estrae e struttura i dati da report HTML generati
da piattaforme OSINT, preparandoli per l'analisi investigativa.
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from bs4 import BeautifulSoup
from urllib.parse import urlparse


@dataclass
class PersonalInfo:
    """Informazioni personali del target"""
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    bio: Optional[str] = None
    occupation: Optional[str] = None
    education: List[str] = field(default_factory=list)


@dataclass
class ContactInfo:
    """Informazioni di contatto"""
    emails: List[Dict[str, Any]] = field(default_factory=list)
    phones: List[Dict[str, Any]] = field(default_factory=list)
    addresses: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SocialMediaProfile:
    """Profilo social media"""
    platform: str
    username: Optional[str] = None
    profile_url: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    posts_count: Optional[int] = None
    verified: bool = False
    created_date: Optional[str] = None
    last_activity: Optional[str] = None
    profile_picture: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataBreach:
    """Informazioni su data breach"""
    breach_name: str
    breach_date: Optional[str] = None
    data_exposed: List[str] = field(default_factory=list)
    password_hash: Optional[str] = None
    password_plain: Optional[str] = None
    email_involved: Optional[str] = None
    source: Optional[str] = None


@dataclass
class DomainInfo:
    """Informazioni su domini"""
    domain: str
    registrant: Optional[str] = None
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiration_date: Optional[str] = None
    name_servers: List[str] = field(default_factory=list)
    status: Optional[str] = None


@dataclass
class ExtractedData:
    """Contenitore principale per tutti i dati estratti"""
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    social_media: List[SocialMediaProfile] = field(default_factory=list)
    data_breaches: List[DataBreach] = field(default_factory=list)
    domains: List[DomainInfo] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    ip_addresses: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[Dict[str, Any]] = field(default_factory=list)
    mentions: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    locations: List[Dict[str, Any]] = field(default_factory=list)
    financial_info: List[Dict[str, Any]] = field(default_factory=list)
    raw_passwords: List[str] = field(default_factory=list)
    password_patterns: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeline: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario"""
        return asdict(self)


class OSINTHTMLParser:
    """
    Parser specializzato per report HTML OSINT.
    Estrae e struttura tutti i dati rilevanti per l'analisi investigativa.
    """

    # Pattern regex per estrazione dati
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_PATTERN = re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}')
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    URL_PATTERN = re.compile(r'https?://[^\s<>"\']+')
    USERNAME_PATTERN = re.compile(r'@([a-zA-Z0-9_]{1,30})')
    DATE_PATTERN = re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b')
    PASSWORD_PATTERN = re.compile(r'(?:password|pwd|pass|passwd)[:\s]*([^\s<>]{4,})', re.IGNORECASE)
    HASH_PATTERN = re.compile(r'\b[a-fA-F0-9]{32,128}\b')

    # Mapping piattaforme social
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
        'pinterest': ['pinterest.com'],
        'snapchat': ['snapchat.com'],
        'whatsapp': ['whatsapp.com'],
        'vk': ['vk.com'],
        'tumblr': ['tumblr.com'],
        'flickr': ['flickr.com'],
        'medium': ['medium.com'],
        'spotify': ['spotify.com'],
        'twitch': ['twitch.tv'],
    }

    def __init__(self):
        self.extracted_data = ExtractedData()
        self.soup = None
        self.raw_html = None
        self.raw_text = None

    def parse(self, html_content: str) -> ExtractedData:
        """
        Esegue il parsing completo del report HTML OSINT.

        Args:
            html_content: Contenuto HTML del report OSINT

        Returns:
            ExtractedData: Oggetto contenente tutti i dati estratti
        """
        self.raw_html = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.raw_text = self.soup.get_text(separator=' ', strip=True)

        # Estrazione dati
        self._extract_personal_info()
        self._extract_contact_info()
        self._extract_social_media()
        self._extract_data_breaches()
        self._extract_domains()
        self._extract_usernames()
        self._extract_ip_addresses()
        self._extract_images()
        self._extract_locations()
        self._extract_passwords()
        self._extract_relationships()
        self._extract_timeline()
        self._extract_metadata()

        return self.extracted_data

    def parse_file(self, file_path: str) -> ExtractedData:
        """Legge e parsa un file HTML"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        return self.parse(html_content)

    def _extract_personal_info(self):
        """Estrae informazioni personali"""
        info = self.extracted_data.personal_info

        # Cerca sezioni comuni per informazioni personali
        personal_sections = self.soup.find_all(['div', 'section'],
            class_=re.compile(r'(personal|profile|info|user|target|subject)', re.I))

        # Estrae nome
        name_elements = self.soup.find_all(['h1', 'h2', 'h3', 'span', 'div'],
            class_=re.compile(r'(name|title|full-name|display-name)', re.I))
        for elem in name_elements:
            if elem.text.strip():
                info.full_name = elem.text.strip()
                break

        # Cerca in tabelle
        tables = self.soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].text.strip().lower()
                    value = cells[1].text.strip()
                    self._map_personal_field(key, value, info)

        # Cerca in definition lists
        dls = self.soup.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            for dt, dd in zip(dts, dds):
                key = dt.text.strip().lower()
                value = dd.text.strip()
                self._map_personal_field(key, value, info)

        # Cerca alias/usernames come nomi alternativi
        alias_pattern = re.compile(r'(?:alias|aka|known as|nickname)[:\s]*([^\n,]+)', re.I)
        aliases = alias_pattern.findall(self.raw_text)
        info.aliases = list(set(aliases))

    def _map_personal_field(self, key: str, value: str, info: PersonalInfo):
        """Mappa campi personali"""
        key = key.lower()
        if any(k in key for k in ['name', 'nome', 'full name']):
            if not info.full_name:
                info.full_name = value
        elif any(k in key for k in ['first name', 'nome']):
            info.first_name = value
        elif any(k in key for k in ['last name', 'cognome', 'surname']):
            info.last_name = value
        elif any(k in key for k in ['birth', 'nascita', 'dob', 'data di nascita']):
            info.date_of_birth = value
        elif any(k in key for k in ['age', 'età']):
            try:
                info.age = int(re.search(r'\d+', value).group())
            except:
                pass
        elif any(k in key for k in ['gender', 'sesso', 'sex']):
            info.gender = value
        elif any(k in key for k in ['nationality', 'nazionalità', 'citizenship']):
            info.nationality = value
        elif any(k in key for k in ['occupation', 'job', 'lavoro', 'professione']):
            info.occupation = value
        elif any(k in key for k in ['education', 'istruzione', 'school', 'university']):
            info.education.append(value)
        elif any(k in key for k in ['bio', 'about', 'description']):
            info.bio = value
        elif any(k in key for k in ['language', 'lingua']):
            info.languages.append(value)

    def _extract_contact_info(self):
        """Estrae informazioni di contatto"""
        contact = self.extracted_data.contact_info

        # Estrai email
        emails = self.EMAIL_PATTERN.findall(self.raw_text)
        for email in set(emails):
            email_info = {
                'email': email.lower(),
                'domain': email.split('@')[1] if '@' in email else None,
                'valid': self._validate_email(email)
            }
            contact.emails.append(email_info)

        # Estrai numeri di telefono
        phones = self.PHONE_PATTERN.findall(self.raw_text)
        for phone in set(phones):
            cleaned = re.sub(r'[^\d+]', '', phone)
            if len(cleaned) >= 8:
                phone_info = {
                    'number': phone,
                    'cleaned': cleaned,
                    'country_code': self._detect_country_code(cleaned)
                }
                contact.phones.append(phone_info)

        # Estrai indirizzi
        address_sections = self.soup.find_all(['div', 'span', 'p'],
            class_=re.compile(r'(address|location|indirizzo)', re.I))
        for section in address_sections:
            contact.addresses.append({
                'raw': section.text.strip(),
                'type': 'unknown'
            })

    def _validate_email(self, email: str) -> bool:
        """Valida formato email"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))

    def _detect_country_code(self, phone: str) -> Optional[str]:
        """Rileva codice paese dal numero"""
        country_codes = {
            '+39': 'IT', '+1': 'US', '+44': 'UK', '+49': 'DE',
            '+33': 'FR', '+34': 'ES', '+41': 'CH', '+43': 'AT'
        }
        for code, country in country_codes.items():
            if phone.startswith(code) or phone.startswith(code.replace('+', '')):
                return country
        return None

    def _extract_social_media(self):
        """Estrae profili social media"""
        urls = self.URL_PATTERN.findall(self.raw_text)

        for url in urls:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')

            for platform, domains in self.SOCIAL_PLATFORMS.items():
                if any(d in domain for d in domains):
                    profile = SocialMediaProfile(
                        platform=platform,
                        profile_url=url
                    )

                    # Estrai username dall'URL
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        profile.username = path_parts[0]

                    # Cerca dati aggiuntivi nel contesto
                    self._enrich_social_profile(profile, url)

                    # Evita duplicati
                    if not any(p.profile_url == url for p in self.extracted_data.social_media):
                        self.extracted_data.social_media.append(profile)

    def _enrich_social_profile(self, profile: SocialMediaProfile, url: str):
        """Arricchisce profilo social con dati dal contesto"""
        # Cerca elementi vicini all'URL per estrarre più dati
        link_elements = self.soup.find_all('a', href=url)

        for link in link_elements:
            parent = link.find_parent(['div', 'section', 'tr'])
            if parent:
                text = parent.get_text()

                # Estrai followers/following
                followers_match = re.search(r'(\d+(?:[,.\d]*)?)\s*(?:followers|seguaci)', text, re.I)
                if followers_match:
                    profile.followers = int(followers_match.group(1).replace(',', '').replace('.', ''))

                following_match = re.search(r'(\d+(?:[,.\d]*)?)\s*(?:following|seguiti)', text, re.I)
                if following_match:
                    profile.following = int(following_match.group(1).replace(',', '').replace('.', ''))

                # Estrai bio
                bio_match = re.search(r'(?:bio|description)[:\s]*([^\n]+)', text, re.I)
                if bio_match:
                    profile.bio = bio_match.group(1).strip()

    def _extract_data_breaches(self):
        """Estrae informazioni su data breach"""
        # Cerca sezioni relative a breach
        breach_sections = self.soup.find_all(['div', 'section', 'table'],
            class_=re.compile(r'(breach|leak|hack|exposed|compromise)', re.I))

        # Pattern per identificare breach
        breach_pattern = re.compile(
            r'(?P<name>[A-Za-z0-9\s]+?)[\s\-:]+(?:breach|leak|hack)',
            re.I
        )

        # Cerca nelle tabelle
        tables = self.soup.find_all('table')
        for table in tables:
            headers = [th.text.strip().lower() for th in table.find_all('th')]
            if any(h in ' '.join(headers) for h in ['breach', 'leak', 'password', 'exposed']):
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all('td')
                    if cells:
                        breach = DataBreach(breach_name=cells[0].text.strip())
                        for i, cell in enumerate(cells):
                            text = cell.text.strip()
                            if i < len(headers):
                                self._map_breach_field(headers[i], text, breach)
                        self.extracted_data.data_breaches.append(breach)

        # Estrai password e hash dal testo
        passwords = self.PASSWORD_PATTERN.findall(self.raw_text)
        self.extracted_data.raw_passwords.extend(passwords)

        hashes = self.HASH_PATTERN.findall(self.raw_text)
        for hash_val in hashes:
            hash_type = self._identify_hash_type(hash_val)
            self.extracted_data.password_patterns.append({
                'hash': hash_val,
                'type': hash_type
            })

    def _map_breach_field(self, header: str, value: str, breach: DataBreach):
        """Mappa campi breach"""
        header = header.lower()
        if 'date' in header or 'data' in header:
            breach.breach_date = value
        elif 'password' in header:
            if len(value) > 20:
                breach.password_hash = value
            else:
                breach.password_plain = value
        elif 'email' in header:
            breach.email_involved = value
        elif 'data' in header or 'exposed' in header:
            breach.data_exposed = [d.strip() for d in value.split(',')]

    def _identify_hash_type(self, hash_val: str) -> str:
        """Identifica tipo di hash"""
        length = len(hash_val)
        if length == 32:
            return 'MD5'
        elif length == 40:
            return 'SHA1'
        elif length == 64:
            return 'SHA256'
        elif length == 128:
            return 'SHA512'
        else:
            return 'Unknown'

    def _extract_domains(self):
        """Estrae informazioni sui domini"""
        domain_sections = self.soup.find_all(['div', 'section', 'table'],
            class_=re.compile(r'(domain|whois|dns)', re.I))

        # Pattern per domini
        domain_pattern = re.compile(r'\b([a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,})\b')

        domains_found = domain_pattern.findall(self.raw_text)

        # Filtra domini comuni (non interessanti)
        common_domains = {'google.com', 'facebook.com', 'twitter.com', 'github.com'}

        for domain in set(domains_found):
            if domain.lower() not in common_domains:
                domain_info = DomainInfo(domain=domain)
                self._enrich_domain_info(domain_info)
                self.extracted_data.domains.append(domain_info)

    def _enrich_domain_info(self, domain_info: DomainInfo):
        """Arricchisce info dominio dal contesto"""
        domain = domain_info.domain

        # Cerca nel testo informazioni sul dominio
        context_pattern = re.compile(
            rf'{re.escape(domain)}[^<]*?'
            r'(?:registrant|owner|created|expires|registrar)[:\s]*([^\n<]+)',
            re.I
        )

        for match in context_pattern.finditer(self.raw_text):
            context = match.group(0).lower()
            value = match.group(1).strip()

            if 'registrant' in context or 'owner' in context:
                domain_info.registrant = value
            elif 'created' in context:
                domain_info.creation_date = value
            elif 'expire' in context:
                domain_info.expiration_date = value
            elif 'registrar' in context:
                domain_info.registrar = value

    def _extract_usernames(self):
        """Estrae username"""
        # Username pattern @username
        usernames = self.USERNAME_PATTERN.findall(self.raw_text)

        # Username da tabelle/liste
        username_sections = self.soup.find_all(['span', 'div', 'td'],
            class_=re.compile(r'(username|user|handle|nick)', re.I))

        for section in username_sections:
            text = section.text.strip()
            if text and len(text) <= 30:
                usernames.append(text)

        self.extracted_data.usernames = list(set(usernames))

    def _extract_ip_addresses(self):
        """Estrae indirizzi IP"""
        ips = self.IP_PATTERN.findall(self.raw_text)

        for ip in set(ips):
            # Valida IP
            parts = ip.split('.')
            if all(0 <= int(p) <= 255 for p in parts):
                ip_info = {
                    'ip': ip,
                    'type': 'private' if self._is_private_ip(ip) else 'public'
                }
                self.extracted_data.ip_addresses.append(ip_info)

    def _is_private_ip(self, ip: str) -> bool:
        """Verifica se IP è privato"""
        parts = [int(p) for p in ip.split('.')]
        if parts[0] == 10:
            return True
        if parts[0] == 172 and 16 <= parts[1] <= 31:
            return True
        if parts[0] == 192 and parts[1] == 168:
            return True
        return False

    def _extract_images(self):
        """Estrae riferimenti a immagini"""
        images = self.soup.find_all('img')

        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')

            if src:
                self.extracted_data.images.append({
                    'url': src,
                    'alt': alt,
                    'type': 'profile' if 'profile' in src.lower() or 'avatar' in src.lower() else 'other'
                })

    def _extract_locations(self):
        """Estrae informazioni geografiche"""
        location_patterns = [
            re.compile(r'(?:location|città|city|country|paese)[:\s]*([^\n,]+)', re.I),
            re.compile(r'(?:lives in|vive a|from|da)[:\s]*([^\n,]+)', re.I),
        ]

        for pattern in location_patterns:
            matches = pattern.findall(self.raw_text)
            for match in matches:
                self.extracted_data.locations.append({
                    'raw': match.strip(),
                    'type': 'mentioned'
                })

        # Coordinate GPS se presenti
        gps_pattern = re.compile(r'[-+]?\d+\.\d+[,\s]+[-+]?\d+\.\d+')
        coords = gps_pattern.findall(self.raw_text)
        for coord in coords:
            parts = re.split(r'[,\s]+', coord)
            if len(parts) == 2:
                try:
                    lat, lon = float(parts[0]), float(parts[1])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        self.extracted_data.locations.append({
                            'lat': lat,
                            'lon': lon,
                            'type': 'coordinates'
                        })
                except:
                    pass

    def _extract_passwords(self):
        """Estrae password in chiaro"""
        # Pattern per password esposte
        password_patterns = [
            re.compile(r'password[:\s]+([^\s<>]{4,30})', re.I),
            re.compile(r'pwd[:\s]+([^\s<>]{4,30})', re.I),
            re.compile(r'pass[:\s]+([^\s<>]{4,30})', re.I),
        ]

        for pattern in password_patterns:
            matches = pattern.findall(self.raw_text)
            self.extracted_data.raw_passwords.extend(matches)

        # Rimuovi duplicati
        self.extracted_data.raw_passwords = list(set(self.extracted_data.raw_passwords))

    def _extract_relationships(self):
        """Estrae relazioni con altre persone"""
        relationship_patterns = [
            re.compile(r'(?:friend|amico|connection)[:\s]*([^\n,]+)', re.I),
            re.compile(r'(?:family|famiglia|relative|parente)[:\s]*([^\n,]+)', re.I),
            re.compile(r'(?:colleague|collega|coworker)[:\s]*([^\n,]+)', re.I),
        ]

        for pattern in relationship_patterns:
            matches = pattern.findall(self.raw_text)
            for match in matches:
                self.extracted_data.relationships.append({
                    'name': match.strip(),
                    'type': 'unknown'
                })

    def _extract_timeline(self):
        """Estrae eventi temporali per timeline"""
        dates = self.DATE_PATTERN.findall(self.raw_text)

        for date in dates:
            # Trova contesto attorno alla data
            idx = self.raw_text.find(date)
            if idx != -1:
                start = max(0, idx - 100)
                end = min(len(self.raw_text), idx + 100)
                context = self.raw_text[start:end]

                self.extracted_data.timeline.append({
                    'date': date,
                    'context': context.strip(),
                    'type': 'event'
                })

    def _extract_metadata(self):
        """Estrae metadati del report"""
        self.extracted_data.metadata = {
            'parsed_at': datetime.now().isoformat(),
            'html_length': len(self.raw_html),
            'text_length': len(self.raw_text),
            'total_emails': len(self.extracted_data.contact_info.emails),
            'total_phones': len(self.extracted_data.contact_info.phones),
            'total_social_profiles': len(self.extracted_data.social_media),
            'total_breaches': len(self.extracted_data.data_breaches),
            'total_passwords': len(self.extracted_data.raw_passwords),
            'total_usernames': len(self.extracted_data.usernames),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Restituisce un sommario dei dati estratti"""
        return {
            'target_name': self.extracted_data.personal_info.full_name,
            'emails_found': len(self.extracted_data.contact_info.emails),
            'phones_found': len(self.extracted_data.contact_info.phones),
            'social_profiles': len(self.extracted_data.social_media),
            'breaches_found': len(self.extracted_data.data_breaches),
            'passwords_exposed': len(self.extracted_data.raw_passwords),
            'usernames': len(self.extracted_data.usernames),
            'domains': len(self.extracted_data.domains),
            'locations': len(self.extracted_data.locations),
        }
