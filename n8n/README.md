# FidelinvestigatorAI - Workflow n8n

## Descrizione

Workflow n8n completo per analisi investigativa OSINT. Converte report HTML da piattaforme OSINT in relazioni investigative professionali.

## Funzionalità

| Nodo | Funzione |
|------|----------|
| **HTML Parser** | Estrae email, telefoni, social, username, breach, password |
| **Data Analyzer** | Correla dati, identifica pattern, calcola exposure |
| **Psychological Profiler** | Profila personalità (Big Five), pattern comportamentali |
| **Password Analyzer** | Analizza costruzione password, predice varianti |
| **Security Assessor** | Valuta sicurezza (Grade A-F), minacce, vulnerabilità |
| **Report Generator** | Genera report HTML professionale |

## Installazione

1. Apri n8n
2. Vai su **Settings > Import Workflow**
3. Carica `FidelinvestigatorAI_workflow.json`
4. Attiva il webhook

## Utilizzo

### Via Webhook (POST)

```bash
curl -X POST https://your-n8n-instance/webhook/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "html_content": "<html>...report OSINT...</html>",
    "logo_path": "https://example.com/logo.png"
  }'
```

### Via HTTP Request Node

Collega un nodo HTTP Request o Form Trigger al workflow.

### Input

```json
{
  "html_content": "<html>...contenuto report OSINT...</html>",
  "logo_path": "https://url-del-tuo-logo.png"  // opzionale
}
```

### Output

```json
{
  "success": true,
  "summary": {
    "target": "Mario Rossi",
    "investigation_date": "02/12/2024 16:30:00",
    "data_points": {
      "emails": 3,
      "phones": 1,
      "social_profiles": 5,
      "usernames": 4,
      "breaches": 2,
      "passwords": 1
    },
    "security": {
      "grade": "C",
      "score": 65,
      "privacy_score": 45,
      "exposure_level": "MODERATO"
    }
  },
  "html_report": "<html>...report completo...</html>",
  "extracted_data": {...},
  "analysis_report": {...},
  "psychological_profile": {...},
  "password_profile": {...},
  "security_report": {...}
}
```

## Struttura Report HTML

Il report generato include:

1. **Intestazione** - Logo, titolo, data/ora
2. **Cap. 1: Introduzione** - OSINT e metodologia
3. **Cap. 2: Scheda Soggetto** - Dati anagrafici, contatti, social
4. **Cap. 3: Analisi Dati** - Correlazioni, breach, pattern
5. **Cap. 4: Profilo Psicologico** - Personalità, comportamento
6. **Cap. 5: Sicurezza Digitale** - Password, vulnerabilità
7. **Cap. 6: Valutazione** - Footprint, rischi, raccomandazioni
8. **Cap. 7: Conclusioni** - Sintesi e avvertenze

## Conversione in PDF

### Opzione 1: wkhtmltopdf (locale)

```bash
wkhtmltopdf --page-size A4 \
  --margin-top 20mm \
  --margin-bottom 20mm \
  --margin-left 20mm \
  --margin-right 20mm \
  report.html report.pdf
```

### Opzione 2: Nodo Execute Command in n8n

Aggiungi dopo il Report Generator:

```javascript
// Salva HTML su file temporaneo
const fs = require('fs');
const htmlContent = $input.first().json.html_report;
fs.writeFileSync('/tmp/report.html', htmlContent);

// Converti con wkhtmltopdf (deve essere installato)
const { execSync } = require('child_process');
execSync('wkhtmltopdf /tmp/report.html /tmp/report.pdf');

// Leggi PDF come base64
const pdfBuffer = fs.readFileSync('/tmp/report.pdf');
return { json: { pdf_base64: pdfBuffer.toString('base64') } };
```

### Opzione 3: API esterne

- **DocRaptor**: https://docraptor.com
- **PDFShift**: https://pdfshift.io
- **HTML2PDF.app**: https://html2pdf.app

## Workflow Completi Disponibili

1. `FidelinvestigatorAI_workflow.json` - Workflow principale
2. `FidelinvestigatorAI_with_pdf.json` - Con conversione PDF via API

## Personalizzazione

### Aggiungere nuovi pattern social

Nel nodo **HTML Parser**, modifica l'oggetto `socialPlatforms`:

```javascript
const socialPlatforms = {
  // ... esistenti ...
  'nuova_piattaforma': ['dominio1.com', 'dominio2.com']
};
```

### Modificare soglie di rischio

Nel nodo **Security Assessor**, modifica l'oggetto `thresholds`:

```javascript
const thresholds = {
  emails: { safe: 1, warning: 3, danger: 5 },
  // ... modifica secondo necessità
};
```

### Personalizzare report HTML

Nel nodo **Report Generator**, modifica il template HTML nella variabile `htmlReport`.

## Requisiti

- n8n v1.0+
- Node.js (per Code nodes)
- Per PDF: wkhtmltopdf o API esterna

## Note di Sicurezza

- Il workflow processa dati sensibili - usare HTTPS
- Non loggare dati personali
- Rispettare normative privacy (GDPR)
- Uso esclusivo per scopi legittimi

---

**FidelinvestigatorAI** - Agente Investigativo OSINT
