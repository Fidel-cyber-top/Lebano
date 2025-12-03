#!/usr/bin/env python3
"""
FidelinvestigatorAI - Advanced OSINT Module
============================================

Modulo avanzato per:
- Ricerca profili social tramite Perplexity AI
- Estrazione e analisi foto (EXIF, geolocalizzazione)
- Sentiment Analysis dei post
- Timeline Analysis
- Network Analysis (connessioni social)

Integra: Perplexity AI, OpenAI, Anthropic Claude

Autore: FidelinvestigatorAI Team
Classificazione: RISERVATO
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import base64
from io import BytesIO

# Auto-install dependencies
def install_deps():
    required = ['requests', 'Pillow', 'openai', 'anthropic', 'geopy']
    import subprocess
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

install_deps()

import requests
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

import openai
import anthropic


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SocialProfile:
    """Detailed social media profile"""
    platform: str
    profile_id: str
    username: str
    display_name: str = ""
    profile_url: str = ""
    bio: str = ""
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    is_verified: bool = False
    is_private: bool = False
    profile_picture_url: str = ""
    created_date: str = ""
    last_active: str = ""
    location_from_profile: str = ""

    # Extracted data
    posts: List[Dict] = field(default_factory=list)
    photos: List[Dict] = field(default_factory=list)
    connections: List[Dict] = field(default_factory=list)

    # Analysis results
    sentiment_analysis: Dict = field(default_factory=dict)
    activity_patterns: Dict = field(default_factory=dict)


@dataclass
class PhotoAnalysis:
    """Photo analysis with EXIF and geolocation"""
    photo_id: str
    source_platform: str
    url: str = ""
    filename: str = ""

    # EXIF Data
    date_taken: str = ""
    time_taken: str = ""
    camera_make: str = ""
    camera_model: str = ""
    software: str = ""

    # Geolocation
    has_gps: bool = False
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    location_name: str = ""  # Reverse geocoded address
    city: str = ""
    country: str = ""

    # Analysis
    faces_detected: int = 0
    objects_detected: List[str] = field(default_factory=list)
    scene_description: str = ""
    confidence_score: float = 0.0


@dataclass
class PostAnalysis:
    """Social media post analysis"""
    post_id: str
    platform: str
    content: str
    post_date: str = ""
    post_time: str = ""
    likes: int = 0
    comments: int = 0
    shares: int = 0

    # Sentiment Analysis
    sentiment: str = ""  # POSITIVE, NEGATIVE, NEUTRAL, MIXED
    sentiment_score: float = 0.0  # -1.0 to 1.0
    emotions: Dict[str, float] = field(default_factory=dict)  # joy, anger, fear, etc.

    # Content Analysis
    topics: List[str] = field(default_factory=list)
    entities_mentioned: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)

    # Location
    location_tagged: str = ""
    geo_coordinates: Tuple[float, float] = (0.0, 0.0)


@dataclass
class NetworkConnection:
    """Social network connection"""
    name: str
    username: str = ""
    profile_url: str = ""
    relationship_type: str = ""  # friend, follower, following, family, colleague
    connection_strength: str = ""  # strong, moderate, weak
    mutual_connections: int = 0
    interaction_frequency: str = ""  # high, medium, low


@dataclass
class TimelineEvent:
    """Event in subject's timeline"""
    date: str
    time: str = ""
    event_type: str = ""  # post, photo, check-in, life_event, breach
    platform: str = ""
    description: str = ""
    location: str = ""
    coordinates: Tuple[float, float] = (0.0, 0.0)
    significance: str = ""  # high, medium, low
    source: str = ""


@dataclass
class AdvancedOSINTData:
    """Complete advanced OSINT data collection"""
    # Subject identifiers
    subject_name: str
    search_identifiers: List[str] = field(default_factory=list)  # emails, phones, usernames

    # Discovered profiles
    social_profiles: List[SocialProfile] = field(default_factory=list)

    # Photo analysis
    photos_analyzed: List[PhotoAnalysis] = field(default_factory=list)
    geolocation_map: List[Dict] = field(default_factory=list)  # [{lat, lon, date, source}]

    # Posts and sentiment
    posts_analyzed: List[PostAnalysis] = field(default_factory=list)
    overall_sentiment: Dict = field(default_factory=dict)

    # Network
    network_connections: List[NetworkConnection] = field(default_factory=list)
    network_statistics: Dict = field(default_factory=dict)

    # Timeline
    timeline: List[TimelineEvent] = field(default_factory=list)

    # AI Analysis summaries
    perplexity_osint_report: str = ""
    social_profile_analysis: str = ""
    photo_geolocation_analysis: str = ""
    sentiment_analysis_report: str = ""
    network_analysis_report: str = ""
    timeline_analysis: str = ""


# =============================================================================
# PERPLEXITY OSINT SEARCHER
# =============================================================================

class PerplexityOSINTSearcher:
    """
    Uses Perplexity AI for real-time OSINT searches on social media profiles
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY", "")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "llama-3.1-sonar-large-128k-online"

    def _query_perplexity(self, prompt: str, system_prompt: str) -> str:
        """Query Perplexity API"""
        if not self.api_key:
            return "[Perplexity API non configurata]"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Errore Perplexity: {str(e)}]"

    def search_social_profiles(self, identifier: str, identifier_type: str = "email") -> Dict:
        """
        Search for social media profiles associated with an identifier
        """
        system_prompt = """Sei un analista OSINT specializzato nella ricerca di profili social.
Il tuo compito è trovare TUTTI i profili social media associati all'identificatore fornito.

PIATTAFORME DA CERCARE:
- Facebook, Instagram, Twitter/X, LinkedIn, TikTok
- Telegram, WhatsApp (se pubblicamente indicizzato)
- YouTube, Reddit, Pinterest, Snapchat
- GitHub, GitLab, Stack Overflow
- Qualsiasi altra piattaforma rilevante

Per ogni profilo trovato, fornisci:
- URL del profilo
- Username
- Nome visualizzato
- Bio/descrizione
- Numero follower (se disponibile)
- Se il profilo è pubblico o privato
- Data ultima attività (se disponibile)

OUTPUT: JSON strutturato con tutti i profili trovati."""

        prompt = f"""
═══════════════════════════════════════════════════════════════
RICERCA PROFILI SOCIAL - OSINT INVESTIGATION
═══════════════════════════════════════════════════════════════

IDENTIFICATORE: {identifier}
TIPO: {identifier_type}

TASKINGS:
1. Cerca TUTTI i profili social associati a questo identificatore
2. Per ogni profilo trovato, raccogli tutte le informazioni pubbliche disponibili
3. Verifica la correlazione tra i profili (stesso username, foto, bio simile)
4. Identifica il profilo principale e quelli secondari

OUTPUT RICHIESTO (JSON):
{{
  "profiles_found": [
    {{
      "platform": "nome piattaforma",
      "profile_url": "URL completo",
      "username": "username",
      "display_name": "nome visualizzato",
      "bio": "bio/descrizione",
      "followers": numero,
      "following": numero,
      "posts_count": numero,
      "is_verified": true/false,
      "is_private": true/false,
      "profile_picture_url": "URL immagine profilo",
      "location": "località dal profilo",
      "last_active": "data ultima attività",
      "confidence": "HIGH/MEDIUM/LOW"
    }}
  ],
  "correlation_analysis": "analisi correlazione tra profili",
  "primary_profile": "piattaforma del profilo principale",
  "total_digital_footprint": "valutazione estensione presenza online"
}}
"""

        response = self._query_perplexity(prompt, system_prompt)

        # Parse JSON response
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw_response": response, "profiles_found": []}

    def analyze_facebook_profile(self, profile_url: str, username: str) -> Dict:
        """
        Deep analysis of a Facebook profile using Perplexity
        """
        system_prompt = """Sei un analista OSINT specializzato nell'analisi di profili Facebook.
Analizza il profilo fornito e raccogli tutte le informazioni pubblicamente disponibili.

INFORMAZIONI DA RACCOGLIERE:
1. Informazioni personali (nome, età, località, lavoro, istruzione)
2. Lista amici visibili e loro caratteristiche
3. Post pubblici recenti (ultimi 20)
4. Foto pubbliche e loro contenuto
5. Check-in e luoghi visitati
6. Gruppi pubblici di appartenenza
7. Eventi a cui ha partecipato
8. Mi piace e interessi

Per i POST analizza:
- Data e ora
- Contenuto testuale
- Reazioni (like, commenti, condivisioni)
- Persone taggate
- Località taggata

Per le FOTO analizza:
- Data di pubblicazione
- Descrizione
- Persone taggate
- Località (se presente)
- Commenti significativi

OUTPUT: JSON strutturato con analisi completa."""

        prompt = f"""
═══════════════════════════════════════════════════════════════
ANALISI PROFILO FACEBOOK - DEEP OSINT
═══════════════════════════════════════════════════════════════

PROFILO: {profile_url}
USERNAME: {username}

TASKINGS INVESTIGATIVI:

1. INFORMAZIONI PERSONALI
   - Raccogli tutti i dati biografici pubblici
   - Identifica luogo di residenza attuale e precedenti
   - Trova informazioni su lavoro e istruzione

2. ANALISI AMICI (Top 20 più interattivi)
   - Nome e profilo
   - Relazione apparente (famiglia, amico, collega)
   - Frequenza interazioni

3. ANALISI POST (Ultimi 20 pubblici)
   Per ogni post:
   - Data/ora pubblicazione
   - Contenuto (primi 500 caratteri)
   - Sentiment (POSITIVE/NEGATIVE/NEUTRAL)
   - Engagement (reactions, comments, shares)
   - Località se presente
   - Persone menzionate/taggate

4. ANALISI FOTO (Ultime 30 pubbliche)
   Per ogni foto:
   - Data pubblicazione
   - Descrizione/caption
   - Numero tag persone
   - Località se presente
   - Tipo foto (selfie, gruppo, viaggio, evento, etc.)

5. LUOGHI E CHECK-IN
   - Lista luoghi visitati
   - Frequenza visite
   - Pattern geografici

6. INTERESSI E GRUPPI
   - Pagine seguite
   - Gruppi pubblici
   - Eventi

OUTPUT JSON STRUTTURATO con tutte le informazioni raccolte.
"""

        response = self._query_perplexity(prompt, system_prompt)

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw_response": response}

    def analyze_instagram_profile(self, profile_url: str, username: str) -> Dict:
        """Deep analysis of Instagram profile"""
        system_prompt = """Sei un analista OSINT specializzato nell'analisi di profili Instagram.
Raccogli tutte le informazioni pubblicamente disponibili sul profilo."""

        prompt = f"""
ANALISI PROFILO INSTAGRAM: {profile_url} (@{username})

RACCOGLI:
1. Bio e informazioni profilo
2. Statistiche (follower, following, post)
3. Ultimi 20 post con:
   - Data, caption, hashtag
   - Engagement (like, commenti)
   - Località taggata
   - Persone taggate
4. Stories Highlights (titoli e temi)
5. Pattern di posting (frequenza, orari)
6. Hashtag più usati
7. Account più interattivi nei commenti

OUTPUT: JSON strutturato."""

        response = self._query_perplexity(prompt, system_prompt)

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw_response": response}

    def analyze_linkedin_profile(self, profile_url: str) -> Dict:
        """Deep analysis of LinkedIn profile"""
        system_prompt = """Sei un analista OSINT specializzato nell'analisi di profili LinkedIn.
Raccogli tutte le informazioni professionali pubblicamente disponibili."""

        prompt = f"""
ANALISI PROFILO LINKEDIN: {profile_url}

RACCOGLI:
1. Nome completo e headline
2. Località e settore
3. Esperienza lavorativa completa (aziende, ruoli, date)
4. Formazione (università, certificazioni)
5. Competenze e endorsement
6. Connessioni notevoli (numero e qualità)
7. Attività recente (post, articoli, commenti)
8. Gruppi di appartenenza
9. Interessi professionali
10. Raccomandazioni ricevute

OUTPUT: JSON strutturato con analisi professionale completa."""

        response = self._query_perplexity(prompt, system_prompt)

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw_response": response}

    def analyze_telegram_account(self, identifier: str) -> Dict:
        """Search for Telegram presence"""
        system_prompt = """Sei un analista OSINT specializzato nella ricerca su Telegram.
Cerca informazioni pubbliche associate all'identificatore."""

        prompt = f"""
RICERCA TELEGRAM per: {identifier}

CERCA:
1. Account Telegram associato (se pubblico)
2. Canali pubblici gestiti
3. Gruppi pubblici di appartenenza
4. Bot creati
5. Menzioni in canali/gruppi pubblici

OUTPUT: JSON con tutte le informazioni trovate."""

        response = self._query_perplexity(prompt, system_prompt)

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw_response": response}


# =============================================================================
# PHOTO ANALYZER (EXIF & GEOLOCATION)
# =============================================================================

class PhotoAnalyzer:
    """
    Analyzes photos for EXIF data and geolocation
    """

    def __init__(self):
        if GEOPY_AVAILABLE:
            self.geolocator = Nominatim(user_agent="fidelinvestigator_osint")
        else:
            self.geolocator = None

    def extract_exif(self, image_path_or_url: str) -> Dict:
        """
        Extract EXIF data from an image
        """
        try:
            if image_path_or_url.startswith(('http://', 'https://')):
                response = requests.get(image_path_or_url, timeout=10)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(image_path_or_url)

            exif_data = {}

            if hasattr(img, '_getexif') and img._getexif():
                exif_raw = img._getexif()

                for tag_id, value in exif_raw.items():
                    tag = TAGS.get(tag_id, tag_id)

                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        exif_data["GPSInfo"] = gps_data
                    else:
                        # Convert to string if not serializable
                        try:
                            json.dumps(value)
                            exif_data[tag] = value
                        except:
                            exif_data[tag] = str(value)

            return exif_data

        except Exception as e:
            return {"error": str(e)}

    def get_gps_coordinates(self, exif_data: Dict) -> Tuple[float, float, float]:
        """
        Extract GPS coordinates from EXIF data
        Returns (latitude, longitude, altitude)
        """
        if "GPSInfo" not in exif_data:
            return (0.0, 0.0, 0.0)

        gps_info = exif_data["GPSInfo"]

        def convert_to_degrees(value):
            """Convert GPS coordinates to degrees"""
            try:
                d = float(value[0])
                m = float(value[1])
                s = float(value[2])
                return d + (m / 60.0) + (s / 3600.0)
            except:
                return 0.0

        lat = lon = alt = 0.0

        if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info:
            lat = convert_to_degrees(gps_info["GPSLatitude"])
            if gps_info["GPSLatitudeRef"] == "S":
                lat = -lat

        if "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
            lon = convert_to_degrees(gps_info["GPSLongitude"])
            if gps_info["GPSLongitudeRef"] == "W":
                lon = -lon

        if "GPSAltitude" in gps_info:
            try:
                alt = float(gps_info["GPSAltitude"])
            except:
                alt = 0.0

        return (lat, lon, alt)

    def reverse_geocode(self, lat: float, lon: float) -> Dict:
        """
        Convert coordinates to address
        """
        if not self.geolocator or lat == 0.0 or lon == 0.0:
            return {}

        try:
            location = self.geolocator.reverse(f"{lat}, {lon}", language="it")
            if location:
                address = location.raw.get("address", {})
                return {
                    "full_address": location.address,
                    "city": address.get("city") or address.get("town") or address.get("village", ""),
                    "state": address.get("state", ""),
                    "country": address.get("country", ""),
                    "postcode": address.get("postcode", ""),
                    "road": address.get("road", ""),
                    "neighbourhood": address.get("neighbourhood", "")
                }
        except GeocoderTimedOut:
            pass
        except Exception as e:
            pass

        return {}

    def analyze_photo(self, image_source: str, photo_id: str = None, platform: str = "unknown") -> PhotoAnalysis:
        """
        Complete photo analysis with EXIF and geolocation
        """
        photo_id = photo_id or hashlib.md5(image_source.encode()).hexdigest()[:12]

        analysis = PhotoAnalysis(
            photo_id=photo_id,
            source_platform=platform,
            url=image_source if image_source.startswith('http') else "",
            filename=os.path.basename(image_source) if not image_source.startswith('http') else ""
        )

        # Extract EXIF
        exif_data = self.extract_exif(image_source)

        if "error" not in exif_data:
            # Date/Time
            if "DateTimeOriginal" in exif_data:
                dt_str = str(exif_data["DateTimeOriginal"])
                try:
                    parts = dt_str.split(" ")
                    analysis.date_taken = parts[0].replace(":", "-")
                    analysis.time_taken = parts[1] if len(parts) > 1 else ""
                except:
                    pass

            # Camera info
            analysis.camera_make = str(exif_data.get("Make", ""))
            analysis.camera_model = str(exif_data.get("Model", ""))
            analysis.software = str(exif_data.get("Software", ""))

            # GPS
            lat, lon, alt = self.get_gps_coordinates(exif_data)
            if lat != 0.0 or lon != 0.0:
                analysis.has_gps = True
                analysis.latitude = lat
                analysis.longitude = lon
                analysis.altitude = alt

                # Reverse geocode
                location_info = self.reverse_geocode(lat, lon)
                if location_info:
                    analysis.location_name = location_info.get("full_address", "")
                    analysis.city = location_info.get("city", "")
                    analysis.country = location_info.get("country", "")

        return analysis


# =============================================================================
# SENTIMENT ANALYZER
# =============================================================================

class SentimentAnalyzer:
    """
    Analyzes sentiment of social media posts using AI
    """

    def __init__(self, anthropic_api_key: str = None, openai_api_key: str = None):
        self.anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_key = openai_api_key or os.getenv("OPENAI_API_KEY", "")

        self.claude_client = None
        self.openai_client = None

        if self.anthropic_key:
            self.claude_client = anthropic.Anthropic(api_key=self.anthropic_key)
        if self.openai_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_key)

    def analyze_posts_sentiment(self, posts: List[Dict]) -> Dict:
        """
        Analyze sentiment of multiple posts
        """
        if not posts:
            return {}

        # Prepare posts for analysis
        posts_text = "\n\n".join([
            f"POST {i+1} ({p.get('date', 'N/A')}):\n{p.get('content', '')[:500]}"
            for i, p in enumerate(posts[:30])  # Max 30 posts
        ])

        prompt = f"""Analizza il sentiment dei seguenti post social media.

{posts_text}

Per ogni post fornisci:
1. Sentiment: POSITIVE, NEGATIVE, NEUTRAL, MIXED
2. Score: da -1.0 (molto negativo) a +1.0 (molto positivo)
3. Emozioni rilevate: joy, sadness, anger, fear, surprise, disgust (score 0-1)
4. Topic principali
5. Tono comunicativo

Poi fornisci un'ANALISI AGGREGATA:
- Sentiment predominante generale
- Trend emotivo nel tempo
- Topic ricorrenti
- Pattern comunicativi
- Indicatori psicologici rilevanti

OUTPUT: JSON strutturato."""

        if self.claude_client:
            try:
                response = self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text

                try:
                    json_match = re.search(r'\{[\s\S]*\}', result_text)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass

                return {"raw_analysis": result_text}

            except Exception as e:
                return {"error": str(e)}

        return {"error": "No AI client available"}

    def analyze_single_post(self, content: str, date: str = "") -> PostAnalysis:
        """
        Analyze a single post
        """
        analysis = PostAnalysis(
            post_id=hashlib.md5(content.encode()).hexdigest()[:12],
            platform="unknown",
            content=content,
            post_date=date
        )

        # Extract hashtags
        analysis.hashtags = re.findall(r'#(\w+)', content)

        # Extract mentions
        analysis.mentions = re.findall(r'@(\w+)', content)

        # Extract URLs
        analysis.urls = re.findall(r'https?://\S+', content)

        # Simple sentiment (can be enhanced with AI)
        positive_words = ['felice', 'bello', 'fantastico', 'grazie', 'love', 'happy', 'great', 'amazing', 'wonderful']
        negative_words = ['triste', 'brutto', 'terribile', 'odio', 'hate', 'sad', 'terrible', 'awful', 'worst']

        content_lower = content.lower()
        pos_count = sum(1 for w in positive_words if w in content_lower)
        neg_count = sum(1 for w in negative_words if w in content_lower)

        if pos_count > neg_count:
            analysis.sentiment = "POSITIVE"
            analysis.sentiment_score = min(1.0, pos_count * 0.2)
        elif neg_count > pos_count:
            analysis.sentiment = "NEGATIVE"
            analysis.sentiment_score = max(-1.0, -neg_count * 0.2)
        else:
            analysis.sentiment = "NEUTRAL"
            analysis.sentiment_score = 0.0

        return analysis


# =============================================================================
# TIMELINE RECONSTRUCTOR
# =============================================================================

class TimelineReconstructor:
    """
    Reconstructs chronological timeline of subject's activities
    """

    def __init__(self):
        self.events: List[TimelineEvent] = []

    def add_event(self, date: str, event_type: str, description: str,
                  platform: str = "", location: str = "",
                  coordinates: Tuple[float, float] = (0.0, 0.0),
                  significance: str = "medium"):
        """Add event to timeline"""

        # Parse time if included in date
        time = ""
        if " " in date:
            parts = date.split(" ")
            date = parts[0]
            time = parts[1] if len(parts) > 1 else ""

        event = TimelineEvent(
            date=date,
            time=time,
            event_type=event_type,
            platform=platform,
            description=description,
            location=location,
            coordinates=coordinates,
            significance=significance
        )

        self.events.append(event)

    def add_posts(self, posts: List[PostAnalysis]):
        """Add posts to timeline"""
        for post in posts:
            self.add_event(
                date=post.post_date,
                event_type="post",
                description=post.content[:200],
                platform=post.platform,
                location=post.location_tagged,
                coordinates=post.geo_coordinates,
                significance="low"
            )

    def add_photos(self, photos: List[PhotoAnalysis]):
        """Add photos to timeline"""
        for photo in photos:
            if photo.date_taken:
                self.add_event(
                    date=f"{photo.date_taken} {photo.time_taken}".strip(),
                    event_type="photo",
                    description=f"Foto scattata con {photo.camera_model or 'dispositivo sconosciuto'}",
                    platform=photo.source_platform,
                    location=photo.location_name,
                    coordinates=(photo.latitude, photo.longitude),
                    significance="medium" if photo.has_gps else "low"
                )

    def add_breaches(self, breaches: List[Dict]):
        """Add data breaches to timeline"""
        for breach in breaches:
            self.add_event(
                date=breach.get("date", "Unknown"),
                event_type="breach",
                description=f"Data breach: {breach.get('source', 'Unknown')}",
                significance="high"
            )

    def get_sorted_timeline(self) -> List[TimelineEvent]:
        """Get timeline sorted by date"""
        def parse_date(event):
            try:
                return datetime.strptime(event.date, "%Y-%m-%d")
            except:
                try:
                    return datetime.strptime(event.date, "%d/%m/%Y")
                except:
                    return datetime.min

        return sorted(self.events, key=parse_date, reverse=True)

    def get_location_history(self) -> List[Dict]:
        """Extract location history from timeline"""
        locations = []
        for event in self.events:
            if event.coordinates != (0.0, 0.0) or event.location:
                locations.append({
                    "date": event.date,
                    "time": event.time,
                    "location": event.location,
                    "coordinates": event.coordinates,
                    "source": f"{event.platform} - {event.event_type}"
                })
        return locations


# =============================================================================
# NETWORK ANALYZER
# =============================================================================

class NetworkAnalyzer:
    """
    Analyzes social network connections
    """

    def __init__(self, perplexity_key: str = None, anthropic_key: str = None):
        self.perplexity = PerplexityOSINTSearcher(perplexity_key) if perplexity_key else None
        self.anthropic_key = anthropic_key

        if anthropic_key:
            self.claude = anthropic.Anthropic(api_key=anthropic_key)
        else:
            self.claude = None

    def analyze_connections(self, connections: List[Dict], subject_name: str) -> Dict:
        """
        Analyze network connections and relationships
        """
        if not self.claude:
            return {"error": "Anthropic API not configured"}

        connections_text = "\n".join([
            f"- {c.get('name', 'N/A')} (@{c.get('username', 'N/A')}): {c.get('relationship', 'unknown')}"
            for c in connections[:50]
        ])

        prompt = f"""Analizza la rete sociale di {subject_name} basandoti sulle seguenti connessioni:

{connections_text}

ANALISI RICHIESTA:

1. STRUTTURA NETWORK
   - Dimensione rete
   - Densità connessioni
   - Cluster identificabili

2. RELAZIONI CHIAVE
   - Familiari identificati
   - Partner/relazioni sentimentali
   - Colleghi di lavoro
   - Amici stretti vs conoscenti

3. INFLUENCERS NEL NETWORK
   - Persone più influenti/importanti
   - Connessioni di alto profilo
   - Opinion leaders

4. PATTERN RELAZIONALI
   - Tipo di relazioni predominanti
   - Qualità vs quantità
   - Red flags relazionali

5. IMPLICAZIONI INVESTIGATIVE
   - Leverage points
   - Possibili fonti di informazione
   - Vulnerabilità attraverso la rete

OUTPUT: JSON strutturato con analisi completa."""

        try:
            response = self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            result_text = response.content[0].text

            try:
                json_match = re.search(r'\{[\s\S]*\}', result_text)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass

            return {"raw_analysis": result_text}

        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# MAIN OSINT ORCHESTRATOR
# =============================================================================

class AdvancedOSINTOrchestrator:
    """
    Orchestrates all advanced OSINT operations
    """

    def __init__(self,
                 perplexity_key: str = None,
                 anthropic_key: str = None,
                 openai_key: str = None):

        self.perplexity_key = perplexity_key or os.getenv("PERPLEXITY_API_KEY", "")
        self.anthropic_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY", "")

        # Initialize components
        self.profile_searcher = PerplexityOSINTSearcher(self.perplexity_key)
        self.photo_analyzer = PhotoAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer(self.anthropic_key, self.openai_key)
        self.timeline = TimelineReconstructor()
        self.network_analyzer = NetworkAnalyzer(self.perplexity_key, self.anthropic_key)

    def run_complete_osint(self,
                           identifiers: List[str],
                           subject_name: str = "Target Subject") -> AdvancedOSINTData:
        """
        Run complete advanced OSINT investigation
        """

        print("=" * 60)
        print("ADVANCED OSINT INVESTIGATION")
        print("=" * 60)

        osint_data = AdvancedOSINTData(
            subject_name=subject_name,
            search_identifiers=identifiers
        )

        # 1. Search for social profiles
        print("\n[1/6] Ricerca profili social...")
        all_profiles = []
        for identifier in identifiers:
            id_type = self._detect_identifier_type(identifier)
            print(f"      Cercando: {identifier} ({id_type})")

            result = self.profile_searcher.search_social_profiles(identifier, id_type)
            profiles = result.get("profiles_found", [])
            all_profiles.extend(profiles)

            print(f"      Trovati: {len(profiles)} profili")

        # 2. Deep analyze each profile
        print("\n[2/6] Analisi approfondita profili...")
        for profile in all_profiles[:10]:  # Max 10 profiles
            platform = profile.get("platform", "").lower()
            url = profile.get("profile_url", "")
            username = profile.get("username", "")

            print(f"      Analizzando: {platform} (@{username})")

            social_profile = SocialProfile(
                platform=platform,
                profile_id=hashlib.md5(url.encode()).hexdigest()[:12],
                username=username,
                display_name=profile.get("display_name", ""),
                profile_url=url,
                bio=profile.get("bio", ""),
                followers=profile.get("followers", 0),
                following=profile.get("following", 0),
                posts_count=profile.get("posts_count", 0),
                is_verified=profile.get("is_verified", False),
                is_private=profile.get("is_private", False),
                profile_picture_url=profile.get("profile_picture_url", ""),
                location_from_profile=profile.get("location", "")
            )

            # Platform-specific deep analysis
            if "facebook" in platform and url:
                fb_data = self.profile_searcher.analyze_facebook_profile(url, username)
                social_profile.posts = fb_data.get("posts", [])
                social_profile.photos = fb_data.get("photos", [])
                social_profile.connections = fb_data.get("friends", [])

            elif "instagram" in platform and url:
                ig_data = self.profile_searcher.analyze_instagram_profile(url, username)
                social_profile.posts = ig_data.get("posts", [])
                social_profile.photos = ig_data.get("photos", [])

            elif "linkedin" in platform and url:
                li_data = self.profile_searcher.analyze_linkedin_profile(url)
                social_profile.posts = li_data.get("activity", [])
                social_profile.connections = li_data.get("connections", [])

            osint_data.social_profiles.append(social_profile)

        # 3. Analyze photos and extract geolocation
        print("\n[3/6] Analisi foto e geolocalizzazione...")
        for profile in osint_data.social_profiles:
            for photo_data in profile.photos[:20]:  # Max 20 photos per profile
                photo_url = photo_data.get("url", "")
                if photo_url:
                    print(f"      Analizzando foto da {profile.platform}...")
                    photo_analysis = self.photo_analyzer.analyze_photo(
                        photo_url,
                        platform=profile.platform
                    )
                    osint_data.photos_analyzed.append(photo_analysis)

                    if photo_analysis.has_gps:
                        osint_data.geolocation_map.append({
                            "lat": photo_analysis.latitude,
                            "lon": photo_analysis.longitude,
                            "date": photo_analysis.date_taken,
                            "location": photo_analysis.location_name,
                            "source": f"{profile.platform} photo"
                        })

        print(f"      Foto analizzate: {len(osint_data.photos_analyzed)}")
        print(f"      Con geolocalizzazione: {len(osint_data.geolocation_map)}")

        # 4. Sentiment analysis on posts
        print("\n[4/6] Sentiment Analysis dei post...")
        all_posts = []
        for profile in osint_data.social_profiles:
            for post in profile.posts:
                post_analysis = self.sentiment_analyzer.analyze_single_post(
                    post.get("content", ""),
                    post.get("date", "")
                )
                post_analysis.platform = profile.platform
                osint_data.posts_analyzed.append(post_analysis)
                all_posts.append(post)

        # Aggregate sentiment analysis
        if all_posts:
            osint_data.overall_sentiment = self.sentiment_analyzer.analyze_posts_sentiment(all_posts)

        print(f"      Post analizzati: {len(osint_data.posts_analyzed)}")

        # 5. Network analysis
        print("\n[5/6] Analisi rete sociale...")
        all_connections = []
        for profile in osint_data.social_profiles:
            for conn in profile.connections:
                network_conn = NetworkConnection(
                    name=conn.get("name", ""),
                    username=conn.get("username", ""),
                    profile_url=conn.get("url", ""),
                    relationship_type=conn.get("relationship", "unknown")
                )
                osint_data.network_connections.append(network_conn)
                all_connections.append(conn)

        if all_connections:
            osint_data.network_statistics = self.network_analyzer.analyze_connections(
                all_connections, subject_name
            )

        print(f"      Connessioni analizzate: {len(osint_data.network_connections)}")

        # 6. Build timeline
        print("\n[6/6] Costruzione timeline...")
        self.timeline.add_posts(osint_data.posts_analyzed)
        self.timeline.add_photos(osint_data.photos_analyzed)

        osint_data.timeline = self.timeline.get_sorted_timeline()

        print(f"      Eventi in timeline: {len(osint_data.timeline)}")
        print(f"      Location history: {len(self.timeline.get_location_history())} punti")

        print("\n" + "=" * 60)
        print("OSINT INVESTIGATION COMPLETATA")
        print("=" * 60)

        return osint_data

    def _detect_identifier_type(self, identifier: str) -> str:
        """Detect type of identifier"""
        if "@" in identifier and "." in identifier:
            return "email"
        elif identifier.startswith("+") or identifier.replace(" ", "").isdigit():
            return "phone"
        elif identifier.startswith("http"):
            return "url"
        else:
            return "username"


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Advanced OSINT Module")
    parser.add_argument("identifier", nargs="?", help="Email, phone, or username to investigate")
    parser.add_argument("--name", default="Target Subject", help="Subject name")
    parser.add_argument("--demo", action="store_true", help="Run demo")

    args = parser.parse_args()

    if args.demo:
        print("Demo mode - richiede API keys configurate")
        print("Imposta: PERPLEXITY_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY")

        # Demo photo analysis
        print("\n--- DEMO: Analisi EXIF foto ---")
        analyzer = PhotoAnalyzer()
        # Would need a real photo URL for demo
        print("PhotoAnalyzer inizializzato")

        # Demo sentiment
        print("\n--- DEMO: Sentiment Analysis ---")
        sentiment = SentimentAnalyzer()
        demo_post = sentiment.analyze_single_post(
            "Oggi è stata una giornata fantastica! #happy #blessed"
        )
        print(f"Sentiment: {demo_post.sentiment} (score: {demo_post.sentiment_score})")
        print(f"Hashtags: {demo_post.hashtags}")

    elif args.identifier:
        orchestrator = AdvancedOSINTOrchestrator()
        result = orchestrator.run_complete_osint(
            [args.identifier],
            args.name
        )
        print(f"\nProfili trovati: {len(result.social_profiles)}")
        print(f"Foto analizzate: {len(result.photos_analyzed)}")
        print(f"Post analizzati: {len(result.posts_analyzed)}")

    else:
        print("Uso: python advanced_osint_module.py <identifier> --name 'Nome Soggetto'")
        print("     python advanced_osint_module.py --demo")


if __name__ == "__main__":
    main()
