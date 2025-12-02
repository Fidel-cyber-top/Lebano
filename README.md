# FidelinvestigatorAI

```
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
║     ─────────────────────────────────────────────────────────   ║
║     Agente Investigativo OSINT di Elite                         ║
║     Background: CIA | ROS | DIA | DCSA | DEA                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## Descrizione

**FidelinvestigatorAI** è un agente investigativo avanzato specializzato nell'analisi di report OSINT (Open Source Intelligence). L'agente analizza report HTML provenienti da piattaforme OSINT e produce relazioni investigative professionali in formato PDF.

### Caratteristiche Principali

- **Parsing Intelligente**: Estrazione automatica di dati da report HTML OSINT
- **Correlazione Dati**: Identificazione di pattern e connessioni tra le informazioni
- **Profilo Psicologico**: Analisi comportamentale basata sull'impronta digitale
- **Analisi Password**: Studio dei pattern di costruzione password e valutazione sicurezza
- **Valutazione Sicurezza**: Assessment completo della postura di sicurezza online
- **Report PDF Professionale**: Generazione di report investigativi formattati professionalmente

### Dati Analizzati

- Informazioni personali (nome, data nascita, occupazione)
- Indirizzi email e numeri di telefono
- Profili social media
- Username e alias
- Data breach e password esposte
- Geolocalizzazione
- Relazioni e connessioni

## Installazione

```bash
# Clone del repository
git clone https://github.com/your-repo/fidelinvestigator.git
cd fidelinvestigator

# Installazione dipendenze
pip install -r requirements.txt

# Oppure installazione come package
pip install -e .
```

## Utilizzo

### Da Codice Python

```python
from fidelinvestigator import FidelinvestigatorAI

# Inizializza l'agente
agent = FidelinvestigatorAI(
    output_dir="./reports",  # Directory per i report
    verbose=True             # Stampa progresso
)

# Opzionale: imposta il logo aziendale
agent.set_logo("/path/to/logo.png")

# Esegui investigazione da file HTML
result = agent.investigate_from_file("/path/to/osint_report.html")

# Oppure da stringa HTML
with open("report.html", "r") as f:
    html_content = f.read()
result = agent.investigate(html_content)

# Accedi ai risultati
print(f"Target: {result.target_name}")
print(f"Report PDF: {result.pdf_report_path}")
print(f"Security Grade: {result.security_report.security_posture.grade}")
```

### Da Linea di Comando

```bash
# Analisi base
python -m fidelinvestigator report.html

# Con nome output personalizzato
python -m fidelinvestigator report.html -o mio_report.pdf

# Con logo aziendale
python -m fidelinvestigator report.html --logo logo.png

# Modalità silenziosa
python -m fidelinvestigator report.html -q
```

### Analisi Rapida (senza PDF)

```python
from fidelinvestigator import FidelinvestigatorAI

agent = FidelinvestigatorAI()
quick_result = agent.get_quick_analysis(html_content)

print(quick_result['exposure_level'])
print(quick_result['key_findings'])
```

## Struttura del Report PDF

Il report generato segue una struttura professionale:

### Intestazione
- Logo aziendale (alto a destra)
- Titolo "REPORT INFO INVESTIGATIVO" (centrato)
- Data e ora di redazione

### Capitoli

1. **INTRODUZIONE**
   - Cos'è l'OSINT
   - Metodologia investigativa
   - Ambito e limitazioni

2. **SCHEDA SOGGETTO**
   - Dati anagrafici
   - Informazioni di contatto
   - Presenza social media
   - Username e identità digitali

3. **ANALISI E CORRELAZIONE DATI**
   - Correlazioni identificate
   - Esposizione a data breach
   - Pattern di attività
   - Findings chiave

4. **PROFILO PSICOLOGICO**
   - Tratti di personalità
   - Pattern comportamentali
   - Stile comunicativo
   - Vulnerabilità e punti di forza

5. **ANALISI SICUREZZA DIGITALE**
   - Analisi pattern password
   - Valutazione postura di sicurezza
   - Vulnerabilità identificate
   - Assessment minacce

6. **VALUTAZIONE COMPLESSIVA**
   - Digital footprint
   - Indicatori di rischio
   - Raccomandazioni operative

7. **CONCLUSIONI**
   - Sintesi investigativa
   - Considerazioni finali
   - Avvertenze

### Formattazione
- Font: Times New Roman
- Interlinea: 1.5
- Formato: A4
- Struttura gerarchica: Capitoli > Paragrafi > Sottoparagrafi

## Moduli

### html_parser.py
Parser specializzato per report HTML OSINT. Estrae:
- Dati personali
- Contatti
- Social media
- Data breach
- Password
- Geolocalizzazione

### data_analyzer.py
Analizzatore con funzionalità di:
- Correlazione email-username
- Correlazione cross-platform
- Analisi temporal
- Identificazione pattern
- Risk assessment

### psychological_profiler.py
Profiler basato su:
- Big Five personality traits
- Behavioral analysis
- Communication style
- Risk profile

### password_analyzer.py
Analizzatore password con:
- Pattern detection
- Strength assessment
- Prediction engine
- Psychological insights

### security_assessor.py
Valutatore sicurezza:
- Exposure metrics
- Vulnerability identification
- Threat assessment
- Privacy score

### report_generator.py
Generatore PDF professionale:
- Formattazione avanzata
- Tabelle e liste
- Info box
- Numerazione automatica

## Output

### InvestigationResult

```python
@dataclass
class InvestigationResult:
    target_name: str
    investigation_date: str
    extracted_data: ExtractedData
    analysis_report: AnalysisReport
    psychological_profile: PsychologicalProfile
    password_profile: PasswordProfile
    security_report: SecurityReport
    pdf_report_path: str
    summary: Dict[str, Any]
```

### Summary Example

```python
{
    'target': 'Mario Rossi',
    'date': '2024-01-15 14:30:00',
    'data_points': {
        'emails': 3,
        'phones': 1,
        'social_profiles': 5,
        'usernames': 4,
        'breaches': 2,
        'passwords': 1
    },
    'security': {
        'grade': 'C',
        'score': 65,
        'privacy_score': 45,
        'exposure_level': 'MODERATO'
    },
    'risk_indicators': 4,
    'vulnerabilities': 3
}
```

## Requisiti

- Python 3.8+
- beautifulsoup4 >= 4.12.0
- reportlab >= 4.0.0
- lxml >= 4.9.0
- Pillow >= 10.0.0 (opzionale, per logo)

## Licenza

MIT License

## Disclaimer

Questo strumento è destinato esclusivamente a:
- Investigazioni autorizzate
- Analisi di sicurezza
- Pentesting con consenso
- Scopi educativi

L'utilizzo improprio di questo strumento è responsabilità dell'utente. Rispettare sempre le leggi locali sulla privacy e la protezione dei dati.

---

**FidelinvestigatorAI** - Agente Investigativo OSINT di Elite
