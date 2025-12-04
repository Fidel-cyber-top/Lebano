"""
Intelligence Report Framework - Dutch OSINT Guy Methodology
============================================================

Implementazione completa della metodologia di Nico Dekens (Dutch OSINT Guy)
per la redazione di rapporti d'intelligence professionali.

Features:
- BLUF (Bottom Line Up Front)
- ACH (Analysis of Competing Hypotheses)
- Source Evaluation con Confidence Levels CIA/NATO (ICD 203)
- Multi-source verification
- Key Judgments con livelli di confidenza
- Struttura report completa secondo standard intelligence

Author: FidelinvestigatorAI
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib


class ConfidenceLevel(Enum):
    """
    Livelli di confidenza secondo ICD 203 (Intelligence Community Directive)
    Usati da CIA, NSA, FBI e comunità intelligence NATO
    """
    HIGH = "HIGH"           # Basato su informazioni di alta qualità e/o logica solida
    MODERATE = "MODERATE"   # Informazioni credibili ma con gap o interpretazioni multiple
    LOW = "LOW"             # Informazioni frammentarie, significativa incertezza

    @property
    def description(self) -> str:
        descriptions = {
            "HIGH": "Basato su informazioni di alta qualità e/o logica solida. "
                    "Verificato da almeno 3 fonti indipendenti.",
            "MODERATE": "Informazioni credibilmente sourced ma con gap informativi "
                        "o interpretazioni multiple plausibili.",
            "LOW": "Basato su informazioni frammentarie o fonti di affidabilità incerta. "
                   "Significativa incertezza nelle conclusioni."
        }
        return descriptions.get(self.value, "")

    @property
    def percentage_range(self) -> str:
        """Range di probabilità associato al livello di confidenza"""
        ranges = {
            "HIGH": "80-95%",
            "MODERATE": "55-80%",
            "LOW": "25-55%"
        }
        return ranges.get(self.value, "")


class SourceReliability(Enum):
    """
    Scala di affidabilità delle fonti secondo standard NATO/Admiralty
    """
    A = "A"  # Completamente affidabile
    B = "B"  # Normalmente affidabile
    C = "C"  # Abbastanza affidabile
    D = "D"  # Non normalmente affidabile
    E = "E"  # Inaffidabile
    F = "F"  # Affidabilità non valutabile

    @property
    def description(self) -> str:
        descriptions = {
            "A": "Completamente affidabile - Nessun dubbio su autenticità, attendibilità o competenza",
            "B": "Normalmente affidabile - Piccoli dubbi, ma solitamente valido",
            "C": "Abbastanza affidabile - Dubbi su affidabilità ma usato in passato",
            "D": "Non normalmente affidabile - Dubbi significativi ma occasionalmente valido",
            "E": "Inaffidabile - Mancanza di affidabilità provata",
            "F": "Affidabilità non valutabile - Impossibile giudicare"
        }
        return descriptions.get(self.value, "")


class InformationAccuracy(Enum):
    """
    Scala di accuratezza delle informazioni secondo standard NATO/Admiralty
    """
    ONE = "1"    # Confermata da altre fonti
    TWO = "2"    # Probabilmente vera
    THREE = "3"  # Possibilmente vera
    FOUR = "4"   # Dubbia
    FIVE = "5"   # Improbabile
    SIX = "6"    # Non valutabile

    @property
    def description(self) -> str:
        descriptions = {
            "1": "Confermata - Verificata da fonti indipendenti",
            "2": "Probabilmente vera - Non confermata, ma logica e coerente",
            "3": "Possibilmente vera - Non confermata, ragionevolmente logica",
            "4": "Dubbia - Non confermata, possibile ma non logica",
            "5": "Improbabile - Non confermata, illogica o contraddetta",
            "6": "Non valutabile - Nessuna base per valutazione"
        }
        return descriptions.get(self.value, "")


@dataclass
class Source:
    """Rappresenta una fonte OSINT con valutazione"""
    name: str
    type: str  # social_media, public_records, news, academic, government, etc.
    url: Optional[str] = None
    reliability: SourceReliability = SourceReliability.F
    accuracy: InformationAccuracy = InformationAccuracy.SIX
    access_date: datetime = field(default_factory=datetime.now)
    archived: bool = False
    archive_url: Optional[str] = None
    notes: str = ""
    bias_assessment: str = ""
    independence: bool = True  # Se la fonte è indipendente da altre

    @property
    def rating(self) -> str:
        """Rating combinato fonte (es. B-2)"""
        return f"{self.reliability.value}-{self.accuracy.value}"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type,
            "url": self.url,
            "reliability": self.reliability.value,
            "accuracy": self.accuracy.value,
            "rating": self.rating,
            "access_date": self.access_date.isoformat(),
            "archived": self.archived,
            "archive_url": self.archive_url,
            "notes": self.notes,
            "bias_assessment": self.bias_assessment,
            "independence": self.independence
        }


@dataclass
class Hypothesis:
    """Ipotesi per ACH (Analysis of Competing Hypotheses)"""
    id: str
    description: str
    evidence_support: List[Tuple[str, str]] = field(default_factory=list)  # (evidence, relationship: +/-/N)
    evidence_against: List[str] = field(default_factory=list)
    inconsistency_score: float = 0.0
    probability: float = 0.0
    notes: str = ""

    def calculate_score(self) -> float:
        """Calcola score basato su evidenze pro/contro"""
        support = sum(1 for _, rel in self.evidence_support if rel == '+')
        neutral = sum(1 for _, rel in self.evidence_support if rel == 'N')
        against = len(self.evidence_against) + sum(1 for _, rel in self.evidence_support if rel == '-')

        total = support + neutral + against
        if total == 0:
            return 0.0

        # Score: supporto - contro, normalizzato
        self.inconsistency_score = against / total if total > 0 else 0
        self.probability = max(0, (support - against) / total) if total > 0 else 0
        return self.probability

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "evidence_support": self.evidence_support,
            "evidence_against": self.evidence_against,
            "inconsistency_score": self.inconsistency_score,
            "probability": self.probability,
            "notes": self.notes
        }


@dataclass
class KeyJudgment:
    """Key Judgment con livello di confidenza"""
    statement: str
    confidence: ConfidenceLevel
    supporting_evidence: List[str] = field(default_factory=list)
    sources: List[Source] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)
    alternative_view: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "statement": self.statement,
            "confidence": self.confidence.value,
            "confidence_range": self.confidence.percentage_range,
            "supporting_evidence": self.supporting_evidence,
            "sources": [s.to_dict() for s in self.sources],
            "caveats": self.caveats,
            "alternative_view": self.alternative_view
        }


@dataclass
class EntityOfInterest:
    """Entità di interesse nell'investigazione"""
    name: str
    entity_type: str  # person, organization, location, asset, account
    identifiers: Dict[str, str] = field(default_factory=dict)
    relationships: List[Dict] = field(default_factory=list)
    timeline_events: List[Dict] = field(default_factory=list)
    risk_level: str = "unknown"
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "entity_type": self.entity_type,
            "identifiers": self.identifiers,
            "relationships": self.relationships,
            "timeline_events": self.timeline_events,
            "risk_level": self.risk_level,
            "notes": self.notes
        }


class ACHAnalyzer:
    """
    Analysis of Competing Hypotheses (ACH)

    Tecnica analitica sviluppata dalla CIA per valutare ipotesi
    alternative minimizzando bias cognitivi.
    """

    def __init__(self):
        self.hypotheses: List[Hypothesis] = []
        self.evidence: List[Dict] = []
        self.matrix: List[List[str]] = []

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Aggiunge un'ipotesi all'analisi"""
        self.hypotheses.append(hypothesis)

    def add_evidence(self, evidence_id: str, description: str,
                     source: Optional[Source] = None,
                     credibility: str = "medium") -> None:
        """Aggiunge un'evidenza all'analisi"""
        self.evidence.append({
            "id": evidence_id,
            "description": description,
            "source": source.to_dict() if source else None,
            "credibility": credibility
        })

    def evaluate_evidence_against_hypothesis(self, evidence_id: str,
                                             hypothesis_id: str,
                                             relationship: str) -> None:
        """
        Valuta come un'evidenza si relaziona a un'ipotesi

        relationship:
        - '+' = Consistente con l'ipotesi
        - '-' = Inconsistente con l'ipotesi
        - 'N' = Neutrale/non applicabile
        """
        for h in self.hypotheses:
            if h.id == hypothesis_id:
                evidence_desc = next(
                    (e["description"] for e in self.evidence if e["id"] == evidence_id),
                    evidence_id
                )
                if relationship == '-':
                    h.evidence_against.append(evidence_desc)
                h.evidence_support.append((evidence_desc, relationship))
                break

    def build_matrix(self) -> List[List[str]]:
        """Costruisce la matrice ACH"""
        # Header: Evidence | H1 | H2 | H3 | ...
        header = ["Evidence"] + [h.id for h in self.hypotheses]
        self.matrix = [header]

        for ev in self.evidence:
            row = [ev["description"]]
            for h in self.hypotheses:
                rel = next(
                    (r for d, r in h.evidence_support if d == ev["description"]),
                    "N"
                )
                row.append(rel)
            self.matrix.append(row)

        return self.matrix

    def rank_hypotheses(self) -> List[Hypothesis]:
        """Classifica le ipotesi per probabilità"""
        for h in self.hypotheses:
            h.calculate_score()

        return sorted(self.hypotheses, key=lambda x: x.probability, reverse=True)

    def get_most_likely_hypothesis(self) -> Optional[Hypothesis]:
        """Restituisce l'ipotesi più probabile"""
        ranked = self.rank_hypotheses()
        return ranked[0] if ranked else None

    def identify_diagnostic_evidence(self) -> List[Dict]:
        """
        Identifica le evidenze diagnostiche - quelle che discriminano
        meglio tra le ipotesi
        """
        diagnostic = []

        for ev in self.evidence:
            relationships = []
            for h in self.hypotheses:
                rel = next(
                    (r for d, r in h.evidence_support if d == ev["description"]),
                    "N"
                )
                relationships.append(rel)

            # Un'evidenza è diagnostica se ha valutazioni diverse tra ipotesi
            unique_rels = set(relationships)
            if len(unique_rels) > 1 and 'N' not in unique_rels:
                diagnostic.append({
                    "evidence": ev["description"],
                    "relationships": dict(zip([h.id for h in self.hypotheses], relationships)),
                    "diagnostic_value": len(unique_rels) / len(self.hypotheses)
                })

        return sorted(diagnostic, key=lambda x: x["diagnostic_value"], reverse=True)

    def generate_report(self) -> Dict:
        """Genera report ACH completo"""
        return {
            "hypotheses": [h.to_dict() for h in self.rank_hypotheses()],
            "evidence": self.evidence,
            "matrix": self.build_matrix(),
            "diagnostic_evidence": self.identify_diagnostic_evidence(),
            "most_likely": self.get_most_likely_hypothesis().to_dict() if self.get_most_likely_hypothesis() else None,
            "analysis_notes": self._generate_analysis_notes()
        }

    def _generate_analysis_notes(self) -> str:
        """Genera note analitiche automatiche"""
        ranked = self.rank_hypotheses()
        if not ranked:
            return "Nessuna ipotesi da analizzare."

        notes = []
        most_likely = ranked[0]

        notes.append(f"L'ipotesi più probabile è '{most_likely.id}' ({most_likely.description}) "
                    f"con probabilità stimata del {most_likely.probability*100:.1f}%.")

        if len(ranked) > 1:
            second = ranked[1]
            gap = most_likely.probability - second.probability
            if gap < 0.15:
                notes.append(f"ATTENZIONE: La seconda ipotesi '{second.id}' ha probabilità simile "
                           f"({second.probability*100:.1f}%). Raccogliere ulteriori evidenze diagnostiche.")

        diagnostic = self.identify_diagnostic_evidence()
        if diagnostic:
            notes.append(f"Identificate {len(diagnostic)} evidenze diagnostiche che discriminano tra le ipotesi.")

        return " ".join(notes)


class SourceEvaluator:
    """
    Valutatore di fonti OSINT secondo standard CIA/NATO
    """

    def __init__(self):
        self.sources: List[Source] = []
        self.verification_matrix: Dict[str, List[Source]] = {}

    def add_source(self, source: Source) -> None:
        """Aggiunge una fonte alla valutazione"""
        self.sources.append(source)

    def evaluate_source(self, source: Source,
                       previous_accuracy: Optional[bool] = None,
                       corroborated: bool = False,
                       expertise_level: str = "unknown") -> Source:
        """
        Valuta automaticamente una fonte basandosi su criteri
        """
        # Valutazione affidabilità
        type_reliability = {
            "government": SourceReliability.B,
            "academic": SourceReliability.B,
            "news_major": SourceReliability.C,
            "news_local": SourceReliability.C,
            "social_media_verified": SourceReliability.C,
            "social_media": SourceReliability.D,
            "forum": SourceReliability.D,
            "anonymous": SourceReliability.E,
            "unknown": SourceReliability.F
        }

        source.reliability = type_reliability.get(source.type, SourceReliability.F)

        # Upgrade se precedentemente accurata
        if previous_accuracy:
            reliability_order = list(SourceReliability)
            current_idx = reliability_order.index(source.reliability)
            if current_idx > 0:
                source.reliability = reliability_order[current_idx - 1]

        # Valutazione accuratezza
        if corroborated:
            source.accuracy = InformationAccuracy.ONE
        elif source.reliability in [SourceReliability.A, SourceReliability.B]:
            source.accuracy = InformationAccuracy.TWO
        elif source.reliability == SourceReliability.C:
            source.accuracy = InformationAccuracy.THREE
        elif source.reliability == SourceReliability.D:
            source.accuracy = InformationAccuracy.FOUR
        else:
            source.accuracy = InformationAccuracy.SIX

        return source

    def verify_multi_source(self, claim: str, sources: List[Source]) -> Dict:
        """
        Verifica multi-source di un'affermazione
        Richiede minimo 3 fonti indipendenti per alta confidenza
        """
        independent_sources = [s for s in sources if s.independence]

        verification = {
            "claim": claim,
            "total_sources": len(sources),
            "independent_sources": len(independent_sources),
            "source_ratings": [s.rating for s in sources],
            "verification_level": "UNVERIFIED",
            "confidence": ConfidenceLevel.LOW,
            "notes": []
        }

        if len(independent_sources) >= 3:
            # Verifica qualità fonti
            high_quality = sum(1 for s in independent_sources
                             if s.reliability in [SourceReliability.A, SourceReliability.B])

            if high_quality >= 2:
                verification["verification_level"] = "VERIFIED"
                verification["confidence"] = ConfidenceLevel.HIGH
                verification["notes"].append(
                    f"Verificato da {len(independent_sources)} fonti indipendenti, "
                    f"di cui {high_quality} di alta qualità."
                )
            else:
                verification["verification_level"] = "PARTIALLY_VERIFIED"
                verification["confidence"] = ConfidenceLevel.MODERATE
                verification["notes"].append(
                    f"Corroborato da {len(independent_sources)} fonti indipendenti, "
                    "ma qualità complessiva moderata."
                )
        elif len(independent_sources) >= 2:
            verification["verification_level"] = "PARTIALLY_VERIFIED"
            verification["confidence"] = ConfidenceLevel.MODERATE
            verification["notes"].append(
                f"Solo {len(independent_sources)} fonti indipendenti. "
                "Raccomandata ulteriore verifica."
            )
        else:
            verification["notes"].append(
                "ATTENZIONE: Fonti insufficienti per verifica. "
                "Trattare come informazione non confermata."
            )

        self.verification_matrix[claim] = sources
        return verification

    def assess_bias(self, source: Source) -> Dict:
        """Valuta potenziali bias di una fonte"""
        bias_indicators = {
            "political_leaning": "unknown",
            "commercial_interest": False,
            "emotional_language": False,
            "single_perspective": False,
            "missing_context": False,
            "overall_bias_risk": "unknown"
        }

        # Bias per tipo di fonte
        high_bias_types = ["social_media", "forum", "anonymous", "opinion"]
        medium_bias_types = ["news_local", "blog", "company"]

        if source.type in high_bias_types:
            bias_indicators["overall_bias_risk"] = "high"
        elif source.type in medium_bias_types:
            bias_indicators["overall_bias_risk"] = "medium"
        else:
            bias_indicators["overall_bias_risk"] = "low"

        return bias_indicators

    def generate_source_report(self) -> Dict:
        """Genera report completo sulle fonti"""
        return {
            "total_sources": len(self.sources),
            "sources": [s.to_dict() for s in self.sources],
            "reliability_distribution": self._get_reliability_distribution(),
            "verification_summary": self._get_verification_summary(),
            "recommendations": self._get_source_recommendations()
        }

    def _get_reliability_distribution(self) -> Dict[str, int]:
        """Distribuzione affidabilità fonti"""
        dist = {}
        for s in self.sources:
            rating = s.reliability.value
            dist[rating] = dist.get(rating, 0) + 1
        return dist

    def _get_verification_summary(self) -> Dict:
        """Sommario verifiche"""
        verified = sum(1 for claims in self.verification_matrix.values()
                      if len([s for s in claims if s.independence]) >= 3)
        return {
            "total_claims": len(self.verification_matrix),
            "verified_claims": verified,
            "verification_rate": verified / len(self.verification_matrix) if self.verification_matrix else 0
        }

    def _get_source_recommendations(self) -> List[str]:
        """Raccomandazioni per migliorare source coverage"""
        recs = []

        reliable_count = sum(1 for s in self.sources
                           if s.reliability in [SourceReliability.A, SourceReliability.B])

        if reliable_count < 3:
            recs.append("Aumentare il numero di fonti di alta affidabilità (rating A o B).")

        independent_count = sum(1 for s in self.sources if s.independence)
        if independent_count < len(self.sources) * 0.7:
            recs.append("Verificare l'indipendenza delle fonti - rischio di eco chamber.")

        types = set(s.type for s in self.sources)
        if len(types) < 3:
            recs.append("Diversificare i tipi di fonte per una prospettiva più completa.")

        archived = sum(1 for s in self.sources if s.archived)
        if archived < len(self.sources) * 0.5:
            recs.append("Archiviare le fonti per preservare le evidenze (Archive.org, screenshots).")

        return recs


class BLUFGenerator:
    """
    Generatore BLUF (Bottom Line Up Front)

    Standard di comunicazione militare/intelligence per presentare
    le conclusioni chiave all'inizio del rapporto.
    """

    def __init__(self):
        self.key_judgments: List[KeyJudgment] = []
        self.scope: str = ""
        self.timeframe: str = ""
        self.classification: str = "UNCLASSIFIED"

    def add_key_judgment(self, judgment: KeyJudgment) -> None:
        """Aggiunge un key judgment"""
        self.key_judgments.append(judgment)

    def set_scope(self, scope: str) -> None:
        """Definisce lo scope dell'analisi"""
        self.scope = scope

    def set_timeframe(self, timeframe: str) -> None:
        """Definisce il periodo di analisi"""
        self.timeframe = timeframe

    def generate_bluf(self, max_judgments: int = 5) -> str:
        """
        Genera il BLUF completo
        """
        lines = []
        lines.append("=" * 60)
        lines.append("BOTTOM LINE UP FRONT (BLUF)")
        lines.append("=" * 60)
        lines.append("")

        if self.scope:
            lines.append(f"SCOPE: {self.scope}")
        if self.timeframe:
            lines.append(f"PERIODO: {self.timeframe}")
        lines.append("")

        lines.append("KEY JUDGMENTS:")
        lines.append("-" * 40)

        # Ordina per confidenza (HIGH prima)
        sorted_judgments = sorted(
            self.key_judgments,
            key=lambda x: list(ConfidenceLevel).index(x.confidence)
        )

        for i, kj in enumerate(sorted_judgments[:max_judgments], 1):
            confidence_indicator = self._get_confidence_indicator(kj.confidence)
            lines.append(f"\n{i}. [{kj.confidence.value}] {confidence_indicator}")
            lines.append(f"   {kj.statement}")

            if kj.caveats:
                lines.append(f"   CAVEATS: {'; '.join(kj.caveats)}")

            if kj.alternative_view:
                lines.append(f"   ALTERNATIVE VIEW: {kj.alternative_view}")

        lines.append("")
        lines.append("=" * 60)
        lines.append(self._generate_confidence_legend())

        return "\n".join(lines)

    def _get_confidence_indicator(self, confidence: ConfidenceLevel) -> str:
        """Indicatore visivo per livello di confidenza"""
        indicators = {
            ConfidenceLevel.HIGH: "●●●",
            ConfidenceLevel.MODERATE: "●●○",
            ConfidenceLevel.LOW: "●○○"
        }
        return indicators.get(confidence, "○○○")

    def _generate_confidence_legend(self) -> str:
        """Legenda livelli di confidenza"""
        return """CONFIDENCE LEVELS:
HIGH (●●●): 80-95% probability - Based on high-quality information
MODERATE (●●○): 55-80% probability - Credible but with gaps
LOW (●○○): 25-55% probability - Fragmentary information"""

    def generate_structured_bluf(self) -> Dict:
        """Genera BLUF in formato strutturato"""
        return {
            "scope": self.scope,
            "timeframe": self.timeframe,
            "classification": self.classification,
            "key_judgments": [kj.to_dict() for kj in self.key_judgments],
            "text": self.generate_bluf()
        }


class IntelligenceReportGenerator:
    """
    Generatore di Intelligence Report completo
    secondo la struttura Dutch OSINT Guy
    """

    def __init__(self,
                 report_title: str,
                 analyst_name: str = "FidelinvestigatorAI",
                 classification: str = "UNCLASSIFIED"):
        self.report_title = report_title
        self.analyst_name = analyst_name
        self.classification = classification
        self.report_date = datetime.now()
        self.report_id = self._generate_report_id()

        # Componenti del report
        self.bluf_generator = BLUFGenerator()
        self.ach_analyzer = ACHAnalyzer()
        self.source_evaluator = SourceEvaluator()

        # Sezioni del report
        self.introduction: str = ""
        self.methodology: str = ""
        self.findings: List[Dict] = []
        self.entities: List[EntityOfInterest] = []
        self.timeline: List[Dict] = []
        self.analysis: str = ""
        self.recommendations: List[str] = []
        self.appendices: List[Dict] = []

        # Metadata
        self.intelligence_requirements: List[str] = []
        self.dissemination_restrictions: str = ""

    def _generate_report_id(self) -> str:
        """Genera ID univoco per il report"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"{self.report_title}{timestamp}".encode()
        short_hash = hashlib.md5(hash_input).hexdigest()[:8].upper()
        return f"INT-{timestamp}-{short_hash}"

    def set_introduction(self, purpose: str, scope: str,
                        limitations: List[str] = None) -> None:
        """Imposta l'introduzione del report"""
        self.introduction = {
            "purpose": purpose,
            "scope": scope,
            "limitations": limitations or [],
            "intelligence_requirements": self.intelligence_requirements
        }
        self.bluf_generator.set_scope(scope)

    def set_methodology(self, collection_methods: List[str],
                       analysis_techniques: List[str],
                       tools_used: List[str] = None) -> None:
        """Imposta la sezione metodologia"""
        self.methodology = {
            "collection_methods": collection_methods,
            "analysis_techniques": analysis_techniques,
            "tools_used": tools_used or [],
            "intelligence_cycle_phase": self._determine_cycle_phase(),
            "ethical_considerations": self._get_ethical_considerations()
        }

    def _determine_cycle_phase(self) -> str:
        """Determina la fase del ciclo intelligence"""
        return """
        Questo report segue il ciclo intelligence CIA/NATO:
        1. PLANNING: Definizione requisiti informativi
        2. COLLECTION: Raccolta dati OSINT
        3. PROCESSING: Organizzazione e validazione dati
        4. ANALYSIS: Analisi e produzione intelligence
        5. DISSEMINATION: Distribuzione report
        """

    def _get_ethical_considerations(self) -> List[str]:
        """Considerazioni etiche standard"""
        return [
            "Tutte le informazioni sono state raccolte da fonti pubblicamente accessibili",
            "Nessuna violazione di sistemi informatici o accesso non autorizzato",
            "Rispetto della privacy secondo GDPR e normative applicabili",
            "Le informazioni sono state verificate secondo standard professionali"
        ]

    def add_finding(self, title: str, description: str,
                   evidence: List[str], sources: List[Source],
                   confidence: ConfidenceLevel,
                   category: str = "general") -> None:
        """Aggiunge un finding al report"""
        finding = {
            "id": f"F-{len(self.findings) + 1:03d}",
            "title": title,
            "description": description,
            "evidence": evidence,
            "sources": [s.to_dict() for s in sources],
            "confidence": confidence.value,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        self.findings.append(finding)

        # Aggiungi fonti al source evaluator
        for source in sources:
            self.source_evaluator.add_source(source)

    def add_entity(self, entity: EntityOfInterest) -> None:
        """Aggiunge un'entità di interesse"""
        self.entities.append(entity)

    def add_timeline_event(self, date: datetime, event: str,
                          significance: str = "medium",
                          sources: List[Source] = None) -> None:
        """Aggiunge un evento alla timeline"""
        self.timeline.append({
            "date": date.isoformat(),
            "event": event,
            "significance": significance,
            "sources": [s.to_dict() for s in (sources or [])]
        })
        # Ordina per data
        self.timeline.sort(key=lambda x: x["date"])

    def add_key_judgment(self, judgment: KeyJudgment) -> None:
        """Aggiunge un key judgment"""
        self.bluf_generator.add_key_judgment(judgment)

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Aggiunge un'ipotesi all'analisi ACH"""
        self.ach_analyzer.add_hypothesis(hypothesis)

    def add_recommendation(self, recommendation: str,
                          priority: str = "medium") -> None:
        """Aggiunge una raccomandazione"""
        self.recommendations.append({
            "text": recommendation,
            "priority": priority
        })

    def add_appendix(self, title: str, content: Any,
                    appendix_type: str = "data") -> None:
        """Aggiunge un'appendice"""
        self.appendices.append({
            "id": f"APP-{chr(65 + len(self.appendices))}",  # APP-A, APP-B, etc.
            "title": title,
            "type": appendix_type,
            "content": content
        })

    def generate_cover_page(self) -> Dict:
        """Genera la pagina di copertina"""
        return {
            "title": self.report_title,
            "classification": self.classification,
            "report_id": self.report_id,
            "date": self.report_date.strftime("%Y-%m-%d %H:%M:%S"),
            "analyst": self.analyst_name,
            "organization": "FidelinvestigatorAI OSINT Unit",
            "distribution": self.dissemination_restrictions or "Unlimited Distribution",
            "warning": self._get_classification_warning()
        }

    def _get_classification_warning(self) -> str:
        """Warning basato sulla classificazione"""
        warnings = {
            "UNCLASSIFIED": "",
            "SENSITIVE": "ATTENZIONE: Contiene informazioni sensibili. "
                        "Distribuzione limitata.",
            "CONFIDENTIAL": "CONFIDENZIALE: Distribuzione autorizzata solo "
                           "a personale autorizzato.",
            "SECRET": "SEGRETO: Vietata la distribuzione non autorizzata."
        }
        return warnings.get(self.classification, "")

    def generate_assessment(self) -> Dict:
        """Genera la sezione Assessment con Key Judgments"""
        ach_report = self.ach_analyzer.generate_report()

        return {
            "summary": self._generate_assessment_summary(),
            "key_judgments": [kj.to_dict() for kj in self.bluf_generator.key_judgments],
            "ach_analysis": ach_report,
            "alternative_hypotheses": self._get_alternative_hypotheses(),
            "confidence_assessment": self._get_overall_confidence(),
            "gaps_and_uncertainties": self._identify_gaps()
        }

    def _generate_assessment_summary(self) -> str:
        """Genera sommario dell'assessment"""
        findings_count = len(self.findings)
        high_conf = sum(1 for kj in self.bluf_generator.key_judgments
                       if kj.confidence == ConfidenceLevel.HIGH)

        return (f"L'analisi ha prodotto {findings_count} findings e "
                f"{len(self.bluf_generator.key_judgments)} key judgments, "
                f"di cui {high_conf} ad alta confidenza.")

    def _get_alternative_hypotheses(self) -> List[Dict]:
        """Estrae ipotesi alternative dall'ACH"""
        ranked = self.ach_analyzer.rank_hypotheses()
        if len(ranked) > 1:
            return [h.to_dict() for h in ranked[1:]]
        return []

    def _get_overall_confidence(self) -> Dict:
        """Calcola confidenza complessiva del report"""
        if not self.bluf_generator.key_judgments:
            return {"level": "UNDETERMINED", "explanation": "No key judgments defined"}

        confidence_scores = {
            ConfidenceLevel.HIGH: 3,
            ConfidenceLevel.MODERATE: 2,
            ConfidenceLevel.LOW: 1
        }

        avg_score = sum(confidence_scores[kj.confidence]
                       for kj in self.bluf_generator.key_judgments) / len(self.bluf_generator.key_judgments)

        if avg_score >= 2.5:
            level = ConfidenceLevel.HIGH
        elif avg_score >= 1.5:
            level = ConfidenceLevel.MODERATE
        else:
            level = ConfidenceLevel.LOW

        return {
            "level": level.value,
            "score": avg_score,
            "explanation": level.description
        }

    def _identify_gaps(self) -> List[str]:
        """Identifica gap informativi"""
        gaps = []

        # Gap da fonti
        source_report = self.source_evaluator.generate_source_report()
        gaps.extend(source_report.get("recommendations", []))

        # Gap da ACH
        diagnostic = self.ach_analyzer.identify_diagnostic_evidence()
        if not diagnostic:
            gaps.append("Mancano evidenze diagnostiche per discriminare tra le ipotesi.")

        # Gap da confidence
        low_conf_judgments = [kj for kj in self.bluf_generator.key_judgments
                            if kj.confidence == ConfidenceLevel.LOW]
        if low_conf_judgments:
            gaps.append(f"{len(low_conf_judgments)} key judgments con confidenza bassa "
                       "richiedono ulteriori verifiche.")

        return gaps

    def generate_full_report(self) -> Dict:
        """Genera il report completo in formato strutturato"""
        return {
            "cover_page": self.generate_cover_page(),
            "bluf": self.bluf_generator.generate_structured_bluf(),
            "introduction": self.introduction,
            "methodology": self.methodology,
            "findings": self.findings,
            "timeline": self.timeline,
            "entities_of_interest": [e.to_dict() for e in self.entities],
            "analysis": {
                "narrative": self.analysis,
                "ach": self.ach_analyzer.generate_report()
            },
            "assessment": self.generate_assessment(),
            "recommendations": self.recommendations,
            "source_evaluation": self.source_evaluator.generate_source_report(),
            "appendices": self.appendices,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_id": self.report_id,
                "version": "1.0",
                "framework": "Dutch OSINT Guy Methodology"
            }
        }

    def generate_text_report(self) -> str:
        """Genera il report in formato testuale"""
        lines = []

        # Cover Page
        cover = self.generate_cover_page()
        lines.append("=" * 70)
        lines.append(f"INTELLIGENCE REPORT")
        lines.append(f"Classification: {cover['classification']}")
        lines.append("=" * 70)
        lines.append(f"\nReport ID: {cover['report_id']}")
        lines.append(f"Title: {cover['title']}")
        lines.append(f"Date: {cover['date']}")
        lines.append(f"Analyst: {cover['analyst']}")
        lines.append(f"Distribution: {cover['distribution']}")
        if cover['warning']:
            lines.append(f"\n*** {cover['warning']} ***")

        # BLUF
        lines.append("\n")
        lines.append(self.bluf_generator.generate_bluf())

        # Table of Contents
        lines.append("\n" + "=" * 70)
        lines.append("TABLE OF CONTENTS")
        lines.append("=" * 70)
        lines.append("1. Introduction")
        lines.append("2. Methodology")
        lines.append("3. Findings")
        lines.append("4. Timeline")
        lines.append("5. Entities of Interest")
        lines.append("6. Analysis")
        lines.append("7. Assessment")
        lines.append("8. Recommendations")
        lines.append("9. Source Evaluation")
        lines.append("10. Appendices")

        # Introduction
        lines.append("\n" + "-" * 70)
        lines.append("1. INTRODUCTION")
        lines.append("-" * 70)
        if isinstance(self.introduction, dict):
            lines.append(f"\nPurpose: {self.introduction.get('purpose', 'N/A')}")
            lines.append(f"Scope: {self.introduction.get('scope', 'N/A')}")
            if self.introduction.get('limitations'):
                lines.append("Limitations:")
                for lim in self.introduction['limitations']:
                    lines.append(f"  - {lim}")

        # Methodology
        lines.append("\n" + "-" * 70)
        lines.append("2. METHODOLOGY")
        lines.append("-" * 70)
        if isinstance(self.methodology, dict):
            lines.append("\nCollection Methods:")
            for method in self.methodology.get('collection_methods', []):
                lines.append(f"  - {method}")
            lines.append("\nAnalysis Techniques:")
            for tech in self.methodology.get('analysis_techniques', []):
                lines.append(f"  - {tech}")

        # Findings
        lines.append("\n" + "-" * 70)
        lines.append("3. FINDINGS")
        lines.append("-" * 70)
        for finding in self.findings:
            lines.append(f"\n[{finding['id']}] {finding['title']}")
            lines.append(f"Confidence: {finding['confidence']}")
            lines.append(f"Description: {finding['description']}")
            if finding['evidence']:
                lines.append("Evidence:")
                for ev in finding['evidence']:
                    lines.append(f"  - {ev}")

        # Timeline
        lines.append("\n" + "-" * 70)
        lines.append("4. TIMELINE")
        lines.append("-" * 70)
        for event in self.timeline:
            lines.append(f"\n{event['date']}: {event['event']}")
            lines.append(f"  Significance: {event['significance']}")

        # Entities
        lines.append("\n" + "-" * 70)
        lines.append("5. ENTITIES OF INTEREST")
        lines.append("-" * 70)
        for entity in self.entities:
            lines.append(f"\n{entity.name} ({entity.entity_type})")
            lines.append(f"  Risk Level: {entity.risk_level}")
            if entity.identifiers:
                lines.append(f"  Identifiers: {entity.identifiers}")

        # Analysis (ACH)
        lines.append("\n" + "-" * 70)
        lines.append("6. ANALYSIS")
        lines.append("-" * 70)
        if self.analysis:
            lines.append(f"\n{self.analysis}")

        ach = self.ach_analyzer.generate_report()
        if ach['hypotheses']:
            lines.append("\nAnalysis of Competing Hypotheses (ACH):")
            for h in ach['hypotheses']:
                lines.append(f"\n  Hypothesis {h['id']}: {h['description']}")
                lines.append(f"    Probability: {h['probability']*100:.1f}%")

        # Assessment
        lines.append("\n" + "-" * 70)
        lines.append("7. ASSESSMENT")
        lines.append("-" * 70)
        assessment = self.generate_assessment()
        lines.append(f"\n{assessment['summary']}")
        lines.append("\nGaps and Uncertainties:")
        for gap in assessment['gaps_and_uncertainties']:
            lines.append(f"  - {gap}")

        # Recommendations
        lines.append("\n" + "-" * 70)
        lines.append("8. RECOMMENDATIONS")
        lines.append("-" * 70)
        for rec in self.recommendations:
            priority = rec['priority'].upper()
            lines.append(f"\n[{priority}] {rec['text']}")

        # Source Evaluation
        lines.append("\n" + "-" * 70)
        lines.append("9. SOURCE EVALUATION")
        lines.append("-" * 70)
        src_report = self.source_evaluator.generate_source_report()
        lines.append(f"\nTotal Sources: {src_report['total_sources']}")
        lines.append(f"Reliability Distribution: {src_report['reliability_distribution']}")

        # Appendices
        lines.append("\n" + "-" * 70)
        lines.append("10. APPENDICES")
        lines.append("-" * 70)
        for app in self.appendices:
            lines.append(f"\n{app['id']}: {app['title']}")

        # Footer
        lines.append("\n" + "=" * 70)
        lines.append(f"END OF REPORT - {self.report_id}")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Framework: Dutch OSINT Guy Methodology")
        lines.append("=" * 70)

        return "\n".join(lines)

    def export_to_json(self, filepath: str) -> None:
        """Esporta il report in formato JSON"""
        report = self.generate_full_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def export_to_text(self, filepath: str) -> None:
        """Esporta il report in formato testo"""
        report = self.generate_text_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)


# ============================================================================
# ESTIMATIVE LANGUAGE STANDARDS (ICD 203)
# ============================================================================

class EstimativeLanguage:
    """
    Standard per linguaggio estimativo secondo ICD 203
    Usato per esprimere probabilità in modo consistente
    """

    PROBABILITY_TERMS = {
        "almost_certain": {"range": (95, 100), "terms": ["almost certain", "quasi certo"]},
        "very_likely": {"range": (80, 95), "terms": ["very likely", "highly probable", "molto probabile"]},
        "likely": {"range": (55, 80), "terms": ["likely", "probable", "probabile"]},
        "roughly_even": {"range": (45, 55), "terms": ["roughly even chance", "probabilità circa pari"]},
        "unlikely": {"range": (20, 45), "terms": ["unlikely", "improbabile"]},
        "very_unlikely": {"range": (5, 20), "terms": ["very unlikely", "highly improbable", "molto improbabile"]},
        "remote": {"range": (0, 5), "terms": ["remote", "remoto"]}
    }

    @classmethod
    def get_term_for_probability(cls, probability: float) -> str:
        """Restituisce il termine appropriato per una probabilità data"""
        prob_pct = probability * 100

        for level, data in cls.PROBABILITY_TERMS.items():
            low, high = data["range"]
            if low <= prob_pct < high:
                return data["terms"][0]

        return "uncertain"

    @classmethod
    def probability_to_confidence(cls, probability: float) -> ConfidenceLevel:
        """Converte probabilità in livello di confidenza"""
        if probability >= 0.80:
            return ConfidenceLevel.HIGH
        elif probability >= 0.55:
            return ConfidenceLevel.MODERATE
        else:
            return ConfidenceLevel.LOW


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_quick_report(title: str,
                       findings: List[Dict],
                       key_judgments: List[Dict],
                       recommendations: List[str] = None) -> IntelligenceReportGenerator:
    """
    Funzione utility per creare rapidamente un report base

    Args:
        title: Titolo del report
        findings: Lista di findings come dict con keys: title, description, evidence, confidence
        key_judgments: Lista di key judgments come dict con keys: statement, confidence, evidence
        recommendations: Lista di raccomandazioni

    Returns:
        IntelligenceReportGenerator configurato
    """
    report = IntelligenceReportGenerator(title)

    # Aggiungi findings
    for f in findings:
        confidence = ConfidenceLevel[f.get('confidence', 'MODERATE').upper()]
        source = Source(
            name=f.get('source_name', 'Unknown'),
            type=f.get('source_type', 'unknown')
        )
        report.add_finding(
            title=f['title'],
            description=f['description'],
            evidence=f.get('evidence', []),
            sources=[source],
            confidence=confidence
        )

    # Aggiungi key judgments
    for kj in key_judgments:
        confidence = ConfidenceLevel[kj.get('confidence', 'MODERATE').upper()]
        judgment = KeyJudgment(
            statement=kj['statement'],
            confidence=confidence,
            supporting_evidence=kj.get('evidence', [])
        )
        report.add_key_judgment(judgment)

    # Aggiungi raccomandazioni
    for rec in (recommendations or []):
        report.add_recommendation(rec)

    return report


# ============================================================================
# ESEMPIO DI UTILIZZO
# ============================================================================

if __name__ == "__main__":
    # Esempio di utilizzo del framework

    # 1. Crea il report generator
    report = IntelligenceReportGenerator(
        report_title="Analisi OSINT Target: Mario Rossi",
        analyst_name="FidelinvestigatorAI",
        classification="SENSITIVE"
    )

    # 2. Imposta introduzione
    report.set_introduction(
        purpose="Identificare e analizzare la presenza digitale del target",
        scope="Social media, registri pubblici, data breaches",
        limitations=["Accesso limitato a fonti a pagamento", "Lingua principale: Italiano"]
    )

    # 3. Imposta metodologia
    report.set_methodology(
        collection_methods=["SOCMINT", "Public Records Search", "Data Breach Analysis"],
        analysis_techniques=["Link Analysis", "Timeline Analysis", "ACH"],
        tools_used=["OSINT Framework", "Maltego", "Shodan"]
    )

    # 4. Aggiungi fonti
    source1 = Source(
        name="LinkedIn Profile",
        type="social_media_verified",
        url="https://linkedin.com/in/example",
        reliability=SourceReliability.C,
        accuracy=InformationAccuracy.TWO,
        archived=True
    )

    source2 = Source(
        name="Camera di Commercio",
        type="government",
        reliability=SourceReliability.A,
        accuracy=InformationAccuracy.ONE
    )

    # 5. Aggiungi findings
    report.add_finding(
        title="Presenza Social Media Confermata",
        description="Target identificato su LinkedIn, Twitter e Instagram con profilo verificato",
        evidence=[
            "Profilo LinkedIn attivo dal 2015",
            "Account Twitter con 1500 followers",
            "Instagram con geolocalizzazioni multiple"
        ],
        sources=[source1],
        confidence=ConfidenceLevel.HIGH,
        category="digital_footprint"
    )

    # 6. Aggiungi ipotesi ACH
    h1 = Hypothesis(
        id="H1",
        description="Target è un professionista legittimo"
    )
    h2 = Hypothesis(
        id="H2",
        description="Target utilizza identità fittizia"
    )
    report.add_hypothesis(h1)
    report.add_hypothesis(h2)

    # 7. Aggiungi key judgments
    kj1 = KeyJudgment(
        statement="Il target mantiene una presenza digitale consistente e verificabile",
        confidence=ConfidenceLevel.HIGH,
        supporting_evidence=["Profilo LinkedIn verificato", "Email aziendale confermata"],
        caveats=["Basato su fonti pubbliche"]
    )
    report.add_key_judgment(kj1)

    # 8. Aggiungi raccomandazioni
    report.add_recommendation(
        "Verificare credenziali professionali attraverso ordini professionali",
        priority="high"
    )
    report.add_recommendation(
        "Monitorare attività social per pattern comportamentali",
        priority="medium"
    )

    # 9. Genera report
    print(report.generate_text_report())
