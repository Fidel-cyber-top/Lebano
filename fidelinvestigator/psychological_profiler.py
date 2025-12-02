"""
Psychological Profiler - Modulo di Profilazione Psicologica
============================================================

Questo modulo crea un profilo psicologico del target basandosi
sull'analisi del comportamento online, pattern linguistici,
scelte di username, interessi e attività sui social media.

Metodologia basata su tecniche di behavioral analysis e
intelligence psychology utilizzate in ambito investigativo.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import Counter
from datetime import datetime


@dataclass
class PersonalityTrait:
    """Tratto di personalità identificato"""
    trait: str
    dimension: str  # openness, conscientiousness, extraversion, agreeableness, neuroticism
    intensity: str  # low, medium, high
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class BehavioralPattern:
    """Pattern comportamentale"""
    pattern_type: str
    description: str
    frequency: str
    psychological_implication: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class InterestProfile:
    """Profilo degli interessi"""
    category: str
    topics: List[str] = field(default_factory=list)
    intensity: str = "medium"
    platforms: List[str] = field(default_factory=list)


@dataclass
class CommunicationStyle:
    """Stile comunicativo"""
    formality_level: str  # formal, informal, mixed
    language_complexity: str  # simple, moderate, complex
    emotional_tone: str  # positive, neutral, negative, mixed
    key_characteristics: List[str] = field(default_factory=list)


@dataclass
class RiskProfile:
    """Profilo di rischio comportamentale"""
    risk_tolerance: str  # low, moderate, high
    privacy_awareness: str  # low, moderate, high
    security_consciousness: str  # low, moderate, high
    impulsivity_indicators: List[str] = field(default_factory=list)


@dataclass
class PsychologicalProfile:
    """Profilo psicologico completo del target"""
    personality_traits: List[PersonalityTrait] = field(default_factory=list)
    behavioral_patterns: List[BehavioralPattern] = field(default_factory=list)
    interests: List[InterestProfile] = field(default_factory=list)
    communication_style: Optional[CommunicationStyle] = None
    risk_profile: Optional[RiskProfile] = None
    digital_persona: str = ""
    psychological_summary: str = ""
    vulnerabilities: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)


class PsychologicalProfiler:
    """
    Profiler psicologico basato su tecniche di intelligence analysis.
    Analizza il comportamento digitale per costruire un profilo psicologico.
    """

    # Mapping tra indicatori e tratti di personalità (Big Five)
    PERSONALITY_INDICATORS = {
        'openness': {
            'high': ['creatività', 'arte', 'musica', 'filosofia', 'viaggi', 'culture diverse',
                     'innovazione', 'curiosità', 'sperimentazione', 'nuovo', 'learning'],
            'low': ['tradizione', 'routine', 'convenzionale', 'pratico', 'concreto']
        },
        'conscientiousness': {
            'high': ['organizzato', 'pianificazione', 'obiettivi', 'disciplina', 'lavoro',
                     'carriera', 'responsabilità', 'puntuale', 'professionale'],
            'low': ['spontaneo', 'flessibile', 'procrastinare', 'disordine', 'last minute']
        },
        'extraversion': {
            'high': ['feste', 'eventi', 'amici', 'socializzare', 'gruppo', 'pubblico',
                     'networking', 'community', 'follower', 'influencer'],
            'low': ['solitario', 'privato', 'riservato', 'introspettivo', 'silenzio']
        },
        'agreeableness': {
            'high': ['aiutare', 'volontariato', 'collaborazione', 'supporto', 'team',
                     'empatia', 'gentile', 'cooperativo', 'armonia'],
            'low': ['competizione', 'sfida', 'critica', 'conflitto', 'dibattito', 'polemica']
        },
        'neuroticism': {
            'high': ['stress', 'ansia', 'preoccupazione', 'paura', 'rabbia', 'frustrazione',
                     'depressione', 'nervoso', 'tensione'],
            'low': ['calmo', 'sereno', 'equilibrato', 'stabile', 'tranquillo', 'rilassato']
        }
    }

    # Pattern username e implicazioni psicologiche
    USERNAME_PATTERNS = {
        r'\d{4}$': {'type': 'year', 'implication': 'Anno significativo (nascita, evento importante)'},
        r'\d{2}$': {'type': 'number', 'implication': 'Età o anno abbreviato'},
        r'_+': {'type': 'separator', 'implication': 'Preferenza per struttura e ordine'},
        r'[xX]{2,}': {'type': 'filler', 'implication': 'Username desiderato non disponibile'},
        r'(real|official|the)': {'type': 'authenticity', 'implication': 'Desiderio di distinzione/autenticità'},
        r'(pro|expert|master)': {'type': 'expertise', 'implication': 'Auto-percezione di competenza'},
        r'(dark|shadow|ghost|phantom)': {'type': 'mystery', 'implication': 'Attrazione per mistero/anonimato'},
        r'(king|queen|lord|boss)': {'type': 'power', 'implication': 'Desiderio di potere/status'},
        r'(love|heart|angel)': {'type': 'romantic', 'implication': 'Orientamento emotivo/romantico'},
        r'(wolf|lion|dragon|tiger)': {'type': 'animal', 'implication': 'Identificazione con attributi animali'},
        r'(ninja|samurai|warrior)': {'type': 'warrior', 'implication': 'Mentalità combattiva/disciplinata'},
        r'(gamer|player|noob)': {'type': 'gaming', 'implication': 'Forte identificazione con gaming culture'},
        r'(crypto|bitcoin|eth)': {'type': 'crypto', 'implication': 'Interesse per tecnologia/finanza'},
        r'(hacker|cyber|tech)': {'type': 'tech', 'implication': 'Identità tecnologica'},
    }

    def __init__(self, extracted_data, analysis_report=None):
        """
        Inizializza il profiler.

        Args:
            extracted_data: Dati estratti dal parser
            analysis_report: Report dell'analizzatore dati (opzionale)
        """
        self.data = extracted_data
        self.analysis = analysis_report
        self.profile = PsychologicalProfile()

    def generate_profile(self) -> PsychologicalProfile:
        """
        Genera il profilo psicologico completo.

        Returns:
            PsychologicalProfile: Profilo psicologico del target
        """
        # Analisi personalità
        self._analyze_personality_traits()

        # Pattern comportamentali
        self._analyze_behavioral_patterns()

        # Interessi
        self._analyze_interests()

        # Stile comunicativo
        self._analyze_communication_style()

        # Profilo di rischio
        self._analyze_risk_profile()

        # Analisi username
        self._analyze_usernames()

        # Digital persona
        self._construct_digital_persona()

        # Vulnerabilità e punti di forza
        self._identify_vulnerabilities()
        self._identify_strengths()

        # Predizioni comportamentali
        self._generate_predictions()

        # Summary finale
        self._generate_psychological_summary()

        return self.profile

    def _analyze_personality_traits(self):
        """Analizza i tratti di personalità (Big Five)"""

        # Raccogli tutto il testo disponibile per l'analisi
        text_corpus = self._build_text_corpus()

        for dimension, indicators in self.PERSONALITY_INDICATORS.items():
            high_matches = []
            low_matches = []

            # Cerca indicatori
            for indicator in indicators['high']:
                if indicator.lower() in text_corpus.lower():
                    high_matches.append(indicator)

            for indicator in indicators['low']:
                if indicator.lower() in text_corpus.lower():
                    low_matches.append(indicator)

            # Determina intensità
            if len(high_matches) > len(low_matches) + 2:
                intensity = 'high'
                evidence = high_matches
                confidence = min(0.9, 0.3 + len(high_matches) * 0.1)
            elif len(low_matches) > len(high_matches) + 2:
                intensity = 'low'
                evidence = low_matches
                confidence = min(0.9, 0.3 + len(low_matches) * 0.1)
            else:
                intensity = 'medium'
                evidence = high_matches + low_matches
                confidence = 0.5

            if evidence:
                self.profile.personality_traits.append(PersonalityTrait(
                    trait=self._get_trait_description(dimension, intensity),
                    dimension=dimension,
                    intensity=intensity,
                    evidence=evidence[:5],
                    confidence=confidence
                ))

    def _get_trait_description(self, dimension: str, intensity: str) -> str:
        """Ottiene descrizione del tratto"""
        descriptions = {
            'openness': {
                'high': 'Curioso, creativo, aperto a nuove esperienze',
                'medium': 'Equilibrio tra tradizione e innovazione',
                'low': 'Pragmatico, preferisce la stabilità e le convenzioni'
            },
            'conscientiousness': {
                'high': 'Organizzato, disciplinato, orientato agli obiettivi',
                'medium': 'Moderatamente strutturato',
                'low': 'Flessibile, spontaneo, adattabile'
            },
            'extraversion': {
                'high': 'Socievole, energico, cerca stimoli esterni',
                'medium': 'Ambivertito, selettivo nelle interazioni',
                'low': 'Riservato, preferisce solitudine e riflessione'
            },
            'agreeableness': {
                'high': 'Cooperativo, empatico, orientato all\'armonia',
                'medium': 'Bilanciato tra cooperazione e assertività',
                'low': 'Competitivo, critico, assertivo'
            },
            'neuroticism': {
                'high': 'Sensibile allo stress, emotivamente reattivo',
                'medium': 'Moderata stabilità emotiva',
                'low': 'Emotivamente stabile, resiliente'
            }
        }
        return descriptions.get(dimension, {}).get(intensity, 'Non determinabile')

    def _build_text_corpus(self) -> str:
        """Costruisce corpus testuale per analisi"""
        texts = []

        # Bio e descrizioni personali
        if self.data.personal_info.bio:
            texts.append(self.data.personal_info.bio)

        # Bio dai social
        for profile in self.data.social_media:
            if profile.bio:
                texts.append(profile.bio)

        # Username
        texts.extend(self.data.usernames)

        # Interessi derivati
        if self.data.personal_info.education:
            texts.extend(self.data.personal_info.education)

        if self.data.personal_info.occupation:
            texts.append(self.data.personal_info.occupation)

        return ' '.join(texts)

    def _analyze_behavioral_patterns(self):
        """Analizza pattern comportamentali"""

        # Pattern: Presenza multi-piattaforma
        platforms = [p.platform for p in self.data.social_media]
        if len(platforms) >= 5:
            self.profile.behavioral_patterns.append(BehavioralPattern(
                pattern_type="multi_platform_presence",
                description="Presenza attiva su numerose piattaforme social",
                frequency="persistente",
                psychological_implication="Forte bisogno di connessione sociale e validazione esterna. "
                                         "Possibile FOMO (fear of missing out) o necessità professionale.",
                evidence=[f"Attivo su {len(platforms)} piattaforme: {', '.join(set(platforms))}"]
            ))
        elif len(platforms) <= 2 and len(platforms) > 0:
            self.profile.behavioral_patterns.append(BehavioralPattern(
                pattern_type="selective_presence",
                description="Presenza selettiva sui social media",
                frequency="misurata",
                psychological_implication="Approccio consapevole alla privacy o preferenza per interazioni mirate.",
                evidence=[f"Limitato a {len(platforms)} piattaforme"]
            ))

        # Pattern: Consistenza username
        usernames = self.data.usernames
        if len(usernames) >= 2:
            unique_usernames = set(u.lower() for u in usernames)
            if len(unique_usernames) == 1:
                self.profile.behavioral_patterns.append(BehavioralPattern(
                    pattern_type="consistent_identity",
                    description="Username coerente su tutte le piattaforme",
                    frequency="costante",
                    psychological_implication="Personalità coerente, desiderio di brand personale riconoscibile. "
                                             "Indica trasparenza o strategia deliberata di personal branding.",
                    evidence=[f"Username consistente: {list(unique_usernames)[0]}"]
                ))
            else:
                self.profile.behavioral_patterns.append(BehavioralPattern(
                    pattern_type="fragmented_identity",
                    description="Utilizzo di username diversi",
                    frequency="variabile",
                    psychological_implication="Possibile compartimentalizzazione della vita digitale, "
                                             "o evoluzione dell'identità online nel tempo.",
                    evidence=[f"Username variabili: {', '.join(list(unique_usernames)[:3])}"]
                ))

        # Pattern: Esposizione a breach
        if self.data.data_breaches:
            if len(self.data.data_breaches) > 3:
                self.profile.behavioral_patterns.append(BehavioralPattern(
                    pattern_type="security_negligence",
                    description="Esposizione ripetuta a data breach",
                    frequency="ricorrente",
                    psychological_implication="Possibile sottovalutazione dei rischi di sicurezza, "
                                             "comportamento routinario senza aggiornamento credenziali.",
                    evidence=[f"Coinvolto in {len(self.data.data_breaches)} breach"]
                ))

        # Pattern: Uso email
        emails = self.data.contact_info.emails
        if len(emails) > 3:
            self.profile.behavioral_patterns.append(BehavioralPattern(
                pattern_type="email_proliferation",
                description="Utilizzo di molteplici indirizzi email",
                frequency="esteso",
                psychological_implication="Compartimentalizzazione, separazione tra vita personale/professionale, "
                                         "o tentativi di anonimizzazione.",
                evidence=[f"{len(emails)} email associate"]
            ))

    def _analyze_interests(self):
        """Analizza interessi basati sui dati raccolti"""

        # Interessi da piattaforme social
        platform_interests = {
            'linkedin': ('Professionale', ['carriera', 'networking', 'business']),
            'github': ('Tecnologia', ['programmazione', 'open source', 'sviluppo']),
            'instagram': ('Visual/Lifestyle', ['fotografia', 'estetica', 'lifestyle']),
            'twitter': ('News/Opinioni', ['attualità', 'dibattito', 'informazione']),
            'tiktok': ('Intrattenimento', ['video brevi', 'trend', 'creatività']),
            'youtube': ('Contenuti Video', ['apprendimento', 'intrattenimento', 'how-to']),
            'reddit': ('Community/Discussioni', ['nicchie specifiche', 'dibattito', 'anonimato']),
            'twitch': ('Gaming/Streaming', ['gaming', 'community live', 'intrattenimento']),
            'pinterest': ('Creatività/Ispirazione', ['design', 'progetti', 'ispirazione visiva']),
            'spotify': ('Musica', ['ascolto musicale', 'playlist', 'scoperta musicale']),
        }

        platforms_found = set(p.platform.lower() for p in self.data.social_media)

        for platform, (category, topics) in platform_interests.items():
            if platform in platforms_found:
                self.profile.interests.append(InterestProfile(
                    category=category,
                    topics=topics,
                    intensity='medium',
                    platforms=[platform]
                ))

        # Interessi da bio/occupazione
        if self.data.personal_info.occupation:
            self.profile.interests.append(InterestProfile(
                category='Professionale',
                topics=[self.data.personal_info.occupation],
                intensity='high',
                platforms=[]
            ))

    def _analyze_communication_style(self):
        """Analizza lo stile comunicativo"""

        text_corpus = self._build_text_corpus()

        # Analizza formalità
        formal_indicators = ['professionista', 'professionale', 'mr.', 'mrs.', 'dr.', 'ing.']
        informal_indicators = ['lol', 'haha', 'xd', '!!!', 'ciao', 'hey']

        formal_count = sum(1 for i in formal_indicators if i.lower() in text_corpus.lower())
        informal_count = sum(1 for i in informal_indicators if i.lower() in text_corpus.lower())

        if formal_count > informal_count:
            formality = 'formal'
        elif informal_count > formal_count:
            formality = 'informal'
        else:
            formality = 'mixed'

        # Caratteristiche chiave
        characteristics = []
        if any(emoji in text_corpus for emoji in ['😀', '😊', '❤️', '👍', '🔥']):
            characteristics.append('Uso di emoji')
        if '...' in text_corpus:
            characteristics.append('Uso di ellissi (riflessivo)')
        if '!' in text_corpus:
            characteristics.append('Uso di esclamativi (espressivo)')

        self.profile.communication_style = CommunicationStyle(
            formality_level=formality,
            language_complexity='moderate',
            emotional_tone='neutral',
            key_characteristics=characteristics if characteristics else ['Stile neutro']
        )

    def _analyze_risk_profile(self):
        """Analizza il profilo di rischio comportamentale"""

        # Valuta privacy awareness
        privacy_score = 0
        privacy_indicators = []

        # Meno email = più privacy aware
        if len(self.data.contact_info.emails) <= 1:
            privacy_score += 2
            privacy_indicators.append('Esposizione email limitata')
        elif len(self.data.contact_info.emails) > 3:
            privacy_score -= 1
            privacy_indicators.append('Molteplici email esposte')

        # Meno social = più privacy aware
        if len(self.data.social_media) <= 2:
            privacy_score += 2
            privacy_indicators.append('Presenza social contenuta')
        elif len(self.data.social_media) > 5:
            privacy_score -= 1
            privacy_indicators.append('Ampia presenza social')

        # Valuta security consciousness
        security_score = 0
        security_indicators = []

        # Breach indicano bassa security
        if not self.data.data_breaches:
            security_score += 2
            security_indicators.append('Nessun breach noto')
        elif len(self.data.data_breaches) > 2:
            security_score -= 2
            security_indicators.append('Molteplici breach')

        # Password esposte
        if self.data.raw_passwords:
            security_score -= 3
            security_indicators.append('Password compromesse')

        # Determina livelli
        privacy_awareness = 'high' if privacy_score >= 2 else ('moderate' if privacy_score >= 0 else 'low')
        security_consciousness = 'high' if security_score >= 2 else ('moderate' if security_score >= 0 else 'low')

        self.profile.risk_profile = RiskProfile(
            risk_tolerance='moderate',
            privacy_awareness=privacy_awareness,
            security_consciousness=security_consciousness,
            impulsivity_indicators=privacy_indicators + security_indicators
        )

    def _analyze_usernames(self):
        """Analizza i pattern nei username"""

        for username in self.data.usernames:
            for pattern, info in self.USERNAME_PATTERNS.items():
                if re.search(pattern, username, re.I):
                    self.profile.behavioral_patterns.append(BehavioralPattern(
                        pattern_type=f"username_{info['type']}",
                        description=f"Pattern '{info['type']}' rilevato in username",
                        frequency="presente",
                        psychological_implication=info['implication'],
                        evidence=[username]
                    ))

    def _construct_digital_persona(self):
        """Costruisce la digital persona del target"""

        persona_elements = []

        # Nome
        if self.data.personal_info.full_name:
            persona_elements.append(f"**Identità**: {self.data.personal_info.full_name}")

        # Occupazione
        if self.data.personal_info.occupation:
            persona_elements.append(f"**Ruolo**: {self.data.personal_info.occupation}")

        # Presenza digitale
        platforms = set(p.platform for p in self.data.social_media)
        if platforms:
            persona_elements.append(f"**Ecosistema digitale**: {', '.join(platforms)}")

        # Tratti dominanti
        high_traits = [t for t in self.profile.personality_traits if t.intensity == 'high']
        if high_traits:
            trait_desc = ', '.join(t.trait for t in high_traits[:3])
            persona_elements.append(f"**Tratti dominanti**: {trait_desc}")

        # Privacy
        if self.profile.risk_profile:
            persona_elements.append(
                f"**Consapevolezza privacy**: {self.profile.risk_profile.privacy_awareness}"
            )

        self.profile.digital_persona = '\n'.join(persona_elements)

    def _identify_vulnerabilities(self):
        """Identifica vulnerabilità psicologiche/comportamentali"""

        vulnerabilities = []

        # Vulnerabilità da breach
        if self.data.data_breaches:
            vulnerabilities.append(
                "Storico di esposizione a data breach indica possibile riutilizzo di password "
                "o scarsa attenzione alla sicurezza degli account."
            )

        # Vulnerabilità da over-sharing
        if len(self.data.social_media) > 5:
            vulnerabilities.append(
                "Presenza estesa sui social media aumenta la superficie di attacco per "
                "social engineering e phishing mirato."
            )

        # Vulnerabilità da consistenza username
        if len(set(self.data.usernames)) == 1 and len(self.data.usernames) > 2:
            vulnerabilities.append(
                "Username consistente su tutte le piattaforme facilita il tracking e "
                "la correlazione di informazioni."
            )

        # Vulnerabilità da dati personali
        personal = self.data.personal_info
        exposed_pii = []
        if personal.date_of_birth:
            exposed_pii.append('data di nascita')
        if personal.full_name:
            exposed_pii.append('nome completo')

        if len(exposed_pii) >= 2:
            vulnerabilities.append(
                f"Esposizione di PII ({', '.join(exposed_pii)}) aumenta rischio di "
                "identity theft e attacchi mirati."
            )

        self.profile.vulnerabilities = vulnerabilities

    def _identify_strengths(self):
        """Identifica punti di forza psicologici"""

        strengths = []

        # Forza da privacy awareness
        if self.profile.risk_profile and self.profile.risk_profile.privacy_awareness == 'high':
            strengths.append(
                "Alta consapevolezza della privacy indica un approccio maturo "
                "alla gestione dell'identità digitale."
            )

        # Forza da presenza selettiva
        if len(self.data.social_media) <= 2:
            strengths.append(
                "Presenza social selettiva riduce la superficie di esposizione "
                "e indica controllo sull'impronta digitale."
            )

        # Forza da assenza breach
        if not self.data.data_breaches:
            strengths.append(
                "Assenza di coinvolgimento in data breach noti suggerisce "
                "buone pratiche di sicurezza o bassa esposizione."
            )

        self.profile.strengths = strengths

    def _generate_predictions(self):
        """Genera predizioni comportamentali"""

        predictions = []

        # Predizione basata su tratti
        for trait in self.profile.personality_traits:
            if trait.dimension == 'conscientiousness' and trait.intensity == 'high':
                predictions.append(
                    "Probabile risposta positiva a comunicazioni strutturate e professionali."
                )
            elif trait.dimension == 'extraversion' and trait.intensity == 'high':
                predictions.append(
                    "Elevata probabilità di interazione con contenuti social e community."
                )

        # Predizione basata su comportamento
        if len(self.data.social_media) > 5:
            predictions.append(
                "Alta probabilità di registrazione su nuove piattaforme social emergenti."
            )

        # Predizione password
        if self.data.raw_passwords:
            predictions.append(
                "Possibile pattern riconoscibile nella costruzione delle password. "
                "Probabile riutilizzo su altri servizi."
            )

        self.profile.predictions = predictions

    def _generate_psychological_summary(self):
        """Genera il sommario psicologico finale"""

        summary_parts = []

        # Intro
        name = self.data.personal_info.full_name or "Il target"
        summary_parts.append(
            f"{name} presenta un profilo psicologico che emerge dall'analisi "
            "del comportamento digitale e delle scelte identitarie online."
        )

        # Tratti dominanti
        high_traits = [t for t in self.profile.personality_traits if t.intensity == 'high']
        if high_traits:
            traits_desc = ', '.join(t.trait.lower() for t in high_traits)
            summary_parts.append(
                f"I tratti di personalità dominanti indicano un individuo {traits_desc}."
            )

        # Comportamento digitale
        if self.profile.behavioral_patterns:
            patterns_desc = '; '.join(p.description.lower() for p in self.profile.behavioral_patterns[:3])
            summary_parts.append(
                f"Il comportamento digitale si caratterizza per: {patterns_desc}."
            )

        # Risk profile
        if self.profile.risk_profile:
            rp = self.profile.risk_profile
            summary_parts.append(
                f"Dal punto di vista della sicurezza, dimostra un livello di consapevolezza "
                f"della privacy {rp.privacy_awareness} e una security consciousness {rp.security_consciousness}."
            )

        # Vulnerabilità chiave
        if self.profile.vulnerabilities:
            summary_parts.append(
                f"Le principali vulnerabilità identificate sono: {self.profile.vulnerabilities[0]}"
            )

        # Conclusione
        summary_parts.append(
            "Questo profilo fornisce una base per comprendere le dinamiche comportamentali "
            "del target e anticipare potenziali pattern di azione."
        )

        self.profile.psychological_summary = ' '.join(summary_parts)

    def get_profile_summary(self) -> Dict[str, Any]:
        """Restituisce un sommario del profilo"""
        return {
            'personality_traits': len(self.profile.personality_traits),
            'behavioral_patterns': len(self.profile.behavioral_patterns),
            'interests': len(self.profile.interests),
            'vulnerabilities': len(self.profile.vulnerabilities),
            'strengths': len(self.profile.strengths),
            'risk_profile': {
                'privacy_awareness': self.profile.risk_profile.privacy_awareness if self.profile.risk_profile else 'unknown',
                'security_consciousness': self.profile.risk_profile.security_consciousness if self.profile.risk_profile else 'unknown'
            } if self.profile.risk_profile else None
        }
