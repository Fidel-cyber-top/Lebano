"""
Password Analyzer - Modulo di Analisi Pattern Password
=======================================================

Questo modulo analizza le password esposte del target per identificare
pattern di costruzione, livello di sicurezza e potenziali predizioni
su altre password utilizzate.

Tecniche basate su metodologie di password intelligence e cracking analysis.
"""

import re
import string
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
from datetime import datetime


@dataclass
class PasswordPattern:
    """Pattern identificato in una password"""
    pattern_type: str
    pattern_value: str
    description: str
    frequency: int = 1
    security_impact: str = "medium"  # low, medium, high, critical


@dataclass
class PasswordStrength:
    """Valutazione forza password"""
    password_masked: str  # Prima e ultima lettera visibili
    length: int
    has_uppercase: bool
    has_lowercase: bool
    has_numbers: bool
    has_special: bool
    entropy_score: float
    strength_level: str  # very_weak, weak, medium, strong, very_strong
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class PasswordPrediction:
    """Predizione su potenziali password"""
    prediction_type: str
    description: str
    confidence: float
    examples: List[str] = field(default_factory=list)


@dataclass
class PasswordProfile:
    """Profilo completo delle password del target"""
    passwords_analyzed: int = 0
    patterns: List[PasswordPattern] = field(default_factory=list)
    strength_assessments: List[PasswordStrength] = field(default_factory=list)
    common_elements: List[str] = field(default_factory=list)
    construction_method: str = ""
    security_score: float = 0.0
    security_level: str = ""
    predictions: List[PasswordPrediction] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    psychological_insights: List[str] = field(default_factory=list)


class PasswordAnalyzer:
    """
    Analizzatore avanzato di password per investigazioni OSINT.
    Identifica pattern, valuta sicurezza e predice potenziali altre password.
    """

    # Pattern comuni nelle password
    COMMON_PATTERNS = {
        'keyboard_walk': [
            'qwerty', 'asdf', 'zxcv', 'qazwsx', '1qaz', '2wsx', '!qaz',
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
        ],
        'sequential_numbers': [
            '123', '1234', '12345', '123456', '1234567', '12345678',
            '321', '4321', '54321', '987', '654'
        ],
        'repeated_chars': [
            'aaa', 'bbb', '111', '000', 'xxx', '!!!'
        ],
        'common_words': [
            'password', 'admin', 'user', 'login', 'welcome', 'master',
            'access', 'pass', 'pwd', 'secret', 'private', 'qwerty'
        ],
        'italian_words': [
            'ciao', 'amore', 'italia', 'roma', 'milano', 'napoli',
            'casa', 'sole', 'mare', 'bella', 'bello', 'forza'
        ],
        'leet_speak': {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7'],
            'l': ['1'],
        }
    }

    # Pattern di date comuni
    DATE_PATTERNS = [
        r'\b(19|20)\d{2}\b',  # Anni
        r'\b\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\b',  # YYMMDD
        r'\b(0[1-9]|[12]\d|3[01])(0[1-9]|1[0-2])(19|20)?\d{2}\b',  # DDMMYYYY
    ]

    def __init__(self, extracted_data):
        """
        Inizializza l'analizzatore.

        Args:
            extracted_data: Dati estratti contenenti password
        """
        self.data = extracted_data
        self.profile = PasswordProfile()
        self.passwords = []

    def analyze(self) -> PasswordProfile:
        """
        Esegue l'analisi completa delle password.

        Returns:
            PasswordProfile: Profilo completo delle password
        """
        # Raccogli password
        self._collect_passwords()

        if not self.passwords:
            self.profile.passwords_analyzed = 0
            self.profile.security_level = "SCONOSCIUTO"
            self.profile.construction_method = "Nessuna password disponibile per l'analisi"
            return self.profile

        self.profile.passwords_analyzed = len(self.passwords)

        # Analizza ogni password
        for pwd in self.passwords:
            self._analyze_single_password(pwd)

        # Identifica pattern comuni
        self._identify_common_patterns()

        # Determina metodo di costruzione
        self._determine_construction_method()

        # Calcola score sicurezza complessivo
        self._calculate_security_score()

        # Genera predizioni
        self._generate_predictions()

        # Genera raccomandazioni
        self._generate_recommendations()

        # Insight psicologici
        self._generate_psychological_insights()

        return self.profile

    def _collect_passwords(self):
        """Raccoglie tutte le password disponibili"""
        self.passwords = []

        # Password in chiaro
        if self.data.raw_passwords:
            self.passwords.extend(self.data.raw_passwords)

        # Password da breach
        for breach in self.data.data_breaches:
            if breach.password_plain:
                self.passwords.append(breach.password_plain)

        # Rimuovi duplicati mantenendo ordine
        seen = set()
        unique = []
        for pwd in self.passwords:
            if pwd.lower() not in seen:
                seen.add(pwd.lower())
                unique.append(pwd)
        self.passwords = unique

    def _analyze_single_password(self, password: str):
        """Analizza una singola password"""

        # Valutazione forza
        strength = self._assess_strength(password)
        self.profile.strength_assessments.append(strength)

        # Identifica pattern
        patterns = self._identify_patterns(password)
        for pattern in patterns:
            # Cerca pattern esistente
            existing = next(
                (p for p in self.profile.patterns
                 if p.pattern_type == pattern.pattern_type and p.pattern_value == pattern.pattern_value),
                None
            )
            if existing:
                existing.frequency += 1
            else:
                self.profile.patterns.append(pattern)

    def _assess_strength(self, password: str) -> PasswordStrength:
        """Valuta la forza di una password"""

        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_num = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)

        # Calcola entropia
        charset_size = 0
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_num:
            charset_size += 10
        if has_special:
            charset_size += 32

        import math
        entropy = length * math.log2(charset_size) if charset_size > 0 else 0

        # Debolezze
        weaknesses = []
        if length < 8:
            weaknesses.append("Lunghezza insufficiente (< 8 caratteri)")
        if not has_upper:
            weaknesses.append("Mancanza di maiuscole")
        if not has_lower:
            weaknesses.append("Mancanza di minuscole")
        if not has_num:
            weaknesses.append("Mancanza di numeri")
        if not has_special:
            weaknesses.append("Mancanza di caratteri speciali")

        # Verifica pattern comuni
        pwd_lower = password.lower()
        for word in self.COMMON_PATTERNS['common_words']:
            if word in pwd_lower:
                weaknesses.append(f"Contiene parola comune: {word}")
                break

        # Determina livello
        score = entropy - (len(weaknesses) * 5)
        if score < 20:
            level = "very_weak"
        elif score < 35:
            level = "weak"
        elif score < 50:
            level = "medium"
        elif score < 65:
            level = "strong"
        else:
            level = "very_strong"

        # Maschera password
        if len(password) > 2:
            masked = password[0] + '*' * (len(password) - 2) + password[-1]
        else:
            masked = '*' * len(password)

        return PasswordStrength(
            password_masked=masked,
            length=length,
            has_uppercase=has_upper,
            has_lowercase=has_lower,
            has_numbers=has_num,
            has_special=has_special,
            entropy_score=round(entropy, 2),
            strength_level=level,
            weaknesses=weaknesses
        )

    def _identify_patterns(self, password: str) -> List[PasswordPattern]:
        """Identifica pattern in una password"""
        patterns = []
        pwd_lower = password.lower()

        # Keyboard walks
        for walk in self.COMMON_PATTERNS['keyboard_walk']:
            if walk in pwd_lower:
                patterns.append(PasswordPattern(
                    pattern_type="keyboard_walk",
                    pattern_value=walk,
                    description=f"Sequenza tastiera: {walk}",
                    security_impact="high"
                ))

        # Sequenze numeriche
        for seq in self.COMMON_PATTERNS['sequential_numbers']:
            if seq in password:
                patterns.append(PasswordPattern(
                    pattern_type="sequential_numbers",
                    pattern_value=seq,
                    description=f"Sequenza numerica: {seq}",
                    security_impact="high"
                ))

        # Caratteri ripetuti
        repeat_match = re.search(r'(.)\1{2,}', password)
        if repeat_match:
            patterns.append(PasswordPattern(
                pattern_type="repeated_chars",
                pattern_value=repeat_match.group(),
                description=f"Caratteri ripetuti: {repeat_match.group()}",
                security_impact="medium"
            ))

        # Date
        for date_pattern in self.DATE_PATTERNS:
            match = re.search(date_pattern, password)
            if match:
                patterns.append(PasswordPattern(
                    pattern_type="date",
                    pattern_value=match.group(),
                    description=f"Data identificata: {match.group()}",
                    security_impact="high"
                ))

        # Parole italiane
        for word in self.COMMON_PATTERNS['italian_words']:
            if word in pwd_lower:
                patterns.append(PasswordPattern(
                    pattern_type="italian_word",
                    pattern_value=word,
                    description=f"Parola italiana: {word}",
                    security_impact="medium"
                ))

        # Leet speak
        leet_detected = self._detect_leet_speak(password)
        if leet_detected:
            patterns.append(PasswordPattern(
                pattern_type="leet_speak",
                pattern_value=leet_detected,
                description=f"Leet speak: {leet_detected}",
                security_impact="low"
            ))

        # Nome/cognome del target
        if self.data.personal_info.full_name:
            name_parts = self.data.personal_info.full_name.lower().split()
            for part in name_parts:
                if len(part) > 2 and part in pwd_lower:
                    patterns.append(PasswordPattern(
                        pattern_type="personal_name",
                        pattern_value=part,
                        description=f"Contiene nome personale: {part}",
                        security_impact="critical"
                    ))

        # Username correlati
        for username in self.data.usernames:
            if len(username) > 2 and username.lower() in pwd_lower:
                patterns.append(PasswordPattern(
                    pattern_type="username",
                    pattern_value=username,
                    description=f"Contiene username: {username}",
                    security_impact="critical"
                ))

        return patterns

    def _detect_leet_speak(self, password: str) -> Optional[str]:
        """Rileva leet speak e decodifica"""
        leet_map = self.COMMON_PATTERNS['leet_speak']
        decoded = password.lower()

        for char, replacements in leet_map.items():
            for replacement in replacements:
                decoded = decoded.replace(replacement, char)

        # Verifica se dopo la decodifica si ottiene una parola comune
        for word_list in [self.COMMON_PATTERNS['common_words'], self.COMMON_PATTERNS['italian_words']]:
            for word in word_list:
                if word in decoded and word not in password.lower():
                    return f"{password} -> {decoded}"

        return None

    def _identify_common_patterns(self):
        """Identifica elementi comuni tra le password"""
        if len(self.passwords) < 2:
            return

        common = []

        # Trova sottostringhe comuni
        all_substrings = []
        for pwd in self.passwords:
            for i in range(len(pwd)):
                for j in range(i + 3, len(pwd) + 1):  # Minimo 3 caratteri
                    all_substrings.append(pwd[i:j].lower())

        # Conta occorrenze
        substring_counts = Counter(all_substrings)
        for substr, count in substring_counts.items():
            if count > 1 and len(substr) >= 3:
                common.append(substr)

        # Ordina per lunghezza (preferisci sottostringhe più lunghe)
        common.sort(key=len, reverse=True)

        # Rimuovi sottostringhe contenute in altre
        filtered = []
        for s in common:
            if not any(s in other and s != other for other in filtered):
                filtered.append(s)

        self.profile.common_elements = filtered[:5]

    def _determine_construction_method(self):
        """Determina il metodo di costruzione delle password"""
        methods = []

        # Analizza pattern più frequenti
        pattern_types = Counter(p.pattern_type for p in self.profile.patterns)

        if pattern_types.get('personal_name', 0) > 0:
            methods.append("Utilizza informazioni personali (nome/cognome)")

        if pattern_types.get('date', 0) > 0:
            methods.append("Incorpora date significative")

        if pattern_types.get('keyboard_walk', 0) > 0:
            methods.append("Usa sequenze tastiera")

        if pattern_types.get('sequential_numbers', 0) > 0:
            methods.append("Aggiunge sequenze numeriche")

        if pattern_types.get('leet_speak', 0) > 0:
            methods.append("Applica trasformazioni leet speak")

        if self.profile.common_elements:
            methods.append(f"Schema base comune: {self.profile.common_elements[0]}")

        # Analizza struttura
        structures = []
        for strength in self.profile.strength_assessments:
            struct = ""
            if strength.has_uppercase and strength.has_lowercase:
                struct += "Mixed-case"
            elif strength.has_uppercase:
                struct += "Uppercase"
            else:
                struct += "Lowercase"

            if strength.has_numbers:
                struct += "+Numbers"
            if strength.has_special:
                struct += "+Special"

            structures.append(struct)

        structure_counts = Counter(structures)
        most_common_struct = structure_counts.most_common(1)
        if most_common_struct:
            methods.append(f"Struttura preferita: {most_common_struct[0][0]}")

        self.profile.construction_method = "; ".join(methods) if methods else "Non determinabile"

    def _calculate_security_score(self):
        """Calcola score di sicurezza complessivo"""
        if not self.profile.strength_assessments:
            self.profile.security_score = 0
            self.profile.security_level = "SCONOSCIUTO"
            return

        # Media entropia
        avg_entropy = sum(s.entropy_score for s in self.profile.strength_assessments) / len(self.profile.strength_assessments)

        # Penalità per pattern critici
        critical_patterns = sum(1 for p in self.profile.patterns if p.security_impact == "critical")
        high_patterns = sum(1 for p in self.profile.patterns if p.security_impact == "high")

        score = avg_entropy
        score -= critical_patterns * 15
        score -= high_patterns * 8

        # Normalizza 0-100
        self.profile.security_score = max(0, min(100, score))

        # Livello
        if self.profile.security_score < 20:
            self.profile.security_level = "CRITICO"
        elif self.profile.security_score < 40:
            self.profile.security_level = "BASSO"
        elif self.profile.security_score < 60:
            self.profile.security_level = "MEDIO"
        elif self.profile.security_score < 80:
            self.profile.security_level = "BUONO"
        else:
            self.profile.security_level = "ECCELLENTE"

    def _generate_predictions(self):
        """Genera predizioni su potenziali altre password"""

        predictions = []

        # Predizione basata su elementi comuni
        if self.profile.common_elements:
            base = self.profile.common_elements[0]
            predictions.append(PasswordPrediction(
                prediction_type="base_pattern",
                description=f"Il target usa probabilmente '{base}' come base per altre password",
                confidence=0.7,
                examples=[
                    f"{base}123",
                    f"{base}2024",
                    f"{base.capitalize()}!",
                    f"{base}@123"
                ]
            ))

        # Predizione basata su nome
        if self.data.personal_info.full_name:
            name_parts = self.data.personal_info.full_name.split()
            if name_parts:
                first_name = name_parts[0].lower()
                predictions.append(PasswordPrediction(
                    prediction_type="name_based",
                    description="Possibile utilizzo del nome in altre password",
                    confidence=0.6,
                    examples=[
                        f"{first_name}123",
                        f"{first_name.capitalize()}!",
                        f"{first_name}2024",
                        f"{first_name[::-1]}"  # Reversed
                    ]
                ))

        # Predizione basata su date
        date_patterns = [p for p in self.profile.patterns if p.pattern_type == "date"]
        if date_patterns:
            date_val = date_patterns[0].pattern_value
            predictions.append(PasswordPrediction(
                prediction_type="date_based",
                description=f"Data '{date_val}' probabilmente usata in varianti",
                confidence=0.75,
                examples=[
                    f"pass{date_val}",
                    f"{date_val}!",
                    f"pwd{date_val}"
                ]
            ))

        # Predizione basata su username
        for username in self.data.usernames[:2]:
            if len(username) >= 4:
                predictions.append(PasswordPrediction(
                    prediction_type="username_based",
                    description=f"Username '{username}' potrebbe essere usato come password",
                    confidence=0.5,
                    examples=[
                        f"{username}123",
                        f"{username}!",
                        f"{username}@2024"
                    ]
                ))

        self.profile.predictions = predictions

    def _generate_recommendations(self):
        """Genera raccomandazioni per migliorare la sicurezza"""

        recommendations = [
            "Utilizzare un password manager per generare e gestire password uniche",
            "Abilitare l'autenticazione a due fattori (2FA) su tutti gli account",
        ]

        # Raccomandazioni specifiche basate sull'analisi
        if any(s.strength_level in ['very_weak', 'weak'] for s in self.profile.strength_assessments):
            recommendations.append(
                "Aumentare la lunghezza delle password a minimo 12-16 caratteri"
            )

        if any(p.pattern_type == 'personal_name' for p in self.profile.patterns):
            recommendations.append(
                "Evitare l'uso di informazioni personali nelle password"
            )

        if any(p.pattern_type == 'date' for p in self.profile.patterns):
            recommendations.append(
                "Non utilizzare date significative (nascita, anniversari) nelle password"
            )

        if self.profile.common_elements:
            recommendations.append(
                "Evitare di riutilizzare la stessa base per multiple password"
            )

        if any(p.pattern_type == 'keyboard_walk' for p in self.profile.patterns):
            recommendations.append(
                "Evitare sequenze di tasti prevedibili (qwerty, asdf)"
            )

        recommendations.append(
            "Cambiare immediatamente tutte le password compromesse"
        )
        recommendations.append(
            "Verificare regolarmente se le proprie credenziali sono state esposte in data breach"
        )

        self.profile.recommendations = recommendations

    def _generate_psychological_insights(self):
        """Genera insight psicologici basati sulle password"""

        insights = []

        # Insight da complessità
        avg_length = sum(s.length for s in self.profile.strength_assessments) / len(self.profile.strength_assessments) if self.profile.strength_assessments else 0

        if avg_length < 8:
            insights.append(
                "La preferenza per password corte suggerisce priorità alla comodità "
                "rispetto alla sicurezza, possibile sottovalutazione dei rischi cyber."
            )
        elif avg_length > 12:
            insights.append(
                "L'uso di password lunghe indica una certa consapevolezza della sicurezza "
                "e disponibilità a sacrificare comodità per protezione."
            )

        # Insight da pattern personali
        personal_patterns = [p for p in self.profile.patterns if p.pattern_type in ['personal_name', 'date']]
        if personal_patterns:
            insights.append(
                "L'incorporazione di dati personali nelle password riflette un legame "
                "emotivo con queste informazioni e una tendenza a scegliere "
                "elementi facilmente memorizzabili."
            )

        # Insight da consistenza
        if self.profile.common_elements:
            insights.append(
                "La presenza di elementi comuni suggerisce un approccio sistematico "
                "alla creazione di password, con una formula mentale ripetuta. "
                "Questo indica prevedibilità comportamentale."
            )

        # Insight da leet speak
        if any(p.pattern_type == 'leet_speak' for p in self.profile.patterns):
            insights.append(
                "L'uso di leet speak (sostituzioni come @ per 'a', 3 per 'e') "
                "indica familiarità con la cultura internet e un tentativo "
                "di aumentare la sicurezza percepita."
            )

        # Insight da breach exposure
        if self.data.data_breaches and len(self.data.data_breaches) > 1:
            insights.append(
                "Il coinvolgimento in multipli data breach senza apparente cambio "
                "di comportamento suggerisce inerzia nella gestione delle credenziali "
                "o scarsa consapevolezza delle conseguenze."
            )

        self.profile.psychological_insights = insights

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Restituisce un sommario dell'analisi"""
        return {
            'passwords_analyzed': self.profile.passwords_analyzed,
            'security_score': self.profile.security_score,
            'security_level': self.profile.security_level,
            'patterns_found': len(self.profile.patterns),
            'common_elements': self.profile.common_elements,
            'construction_method': self.profile.construction_method,
            'critical_issues': sum(1 for p in self.profile.patterns if p.security_impact == 'critical'),
            'predictions_count': len(self.profile.predictions)
        }
