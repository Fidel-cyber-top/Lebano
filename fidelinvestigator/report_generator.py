"""
Report Generator - Generatore Report PDF Professionale
=======================================================

Questo modulo genera report investigativi professionali in formato PDF
con formattazione avanzata, struttura per capitoli e stile professionale.

Formato: Times New Roman, interlinea 1.5, struttura gerarchica
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import per generazione PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@dataclass
class ReportSection:
    """Sezione del report"""
    title: str
    content: List[Any]
    level: int = 1  # 1=capitolo, 2=paragrafo, 3=sottoparagrafo


class ReportGenerator:
    """
    Generatore di report investigativi professionali.
    Produce PDF formattati secondo standard investigativi.
    """

    def __init__(self, output_path: str = "report_investigativo.pdf"):
        """
        Inizializza il generatore.

        Args:
            output_path: Percorso del file PDF di output
        """
        self.output_path = output_path
        self.elements = []
        self.styles = self._create_styles()
        self.logo_path = None
        self.report_title = "REPORT INFO INVESTIGATIVO"
        self.chapter_counter = 0
        self.section_counter = 0
        self.subsection_counter = 0

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Crea gli stili per il documento"""
        styles = {}

        # Stile base - Times New Roman, interlinea 1.5
        base_font = 'Times-Roman'
        base_font_bold = 'Times-Bold'
        base_font_italic = 'Times-Italic'
        line_spacing = 18  # ~1.5 interlinea per font 12pt

        # Titolo principale
        styles['Title'] = ParagraphStyle(
            'Title',
            fontName=base_font_bold,
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e')
        )

        # Sottotitolo
        styles['Subtitle'] = ParagraphStyle(
            'Subtitle',
            fontName=base_font_italic,
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#4a4a4a')
        )

        # Capitolo (Heading 1)
        styles['Chapter'] = ParagraphStyle(
            'Chapter',
            fontName=base_font_bold,
            fontSize=16,
            leading=24,
            alignment=TA_LEFT,
            spaceBefore=30,
            spaceAfter=15,
            textColor=colors.HexColor('#16213e'),
            borderWidth=0,
            borderPadding=5,
            borderColor=colors.HexColor('#16213e'),
            borderRadius=None
        )

        # Paragrafo (Heading 2)
        styles['Section'] = ParagraphStyle(
            'Section',
            fontName=base_font_bold,
            fontSize=14,
            leading=20,
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#1f4068')
        )

        # Sottoparagrafo (Heading 3)
        styles['Subsection'] = ParagraphStyle(
            'Subsection',
            fontName=base_font_bold,
            fontSize=12,
            leading=18,
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#162447')
        )

        # Testo normale - Times New Roman, interlinea 1.5
        styles['Normal'] = ParagraphStyle(
            'Normal',
            fontName=base_font,
            fontSize=12,
            leading=line_spacing,  # 1.5 interlinea
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6,
            firstLineIndent=0
        )

        # Testo evidenziato
        styles['Highlight'] = ParagraphStyle(
            'Highlight',
            fontName=base_font_bold,
            fontSize=12,
            leading=line_spacing,
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=6,
            textColor=colors.HexColor('#c70039')
        )

        # Lista
        styles['ListItem'] = ParagraphStyle(
            'ListItem',
            fontName=base_font,
            fontSize=11,
            leading=16,
            alignment=TA_LEFT,
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=3
        )

        # Citazione/Box info
        styles['InfoBox'] = ParagraphStyle(
            'InfoBox',
            fontName=base_font_italic,
            fontSize=11,
            leading=15,
            alignment=TA_LEFT,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10,
            spaceAfter=10,
            backColor=colors.HexColor('#f5f5f5'),
            borderWidth=1,
            borderColor=colors.HexColor('#cccccc'),
            borderPadding=10
        )

        # Footer
        styles['Footer'] = ParagraphStyle(
            'Footer',
            fontName=base_font_italic,
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        )

        # Header data
        styles['HeaderRight'] = ParagraphStyle(
            'HeaderRight',
            fontName=base_font,
            fontSize=10,
            leading=14,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#333333')
        )

        # Tabella header
        styles['TableHeader'] = ParagraphStyle(
            'TableHeader',
            fontName=base_font_bold,
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.white
        )

        # Tabella cella
        styles['TableCell'] = ParagraphStyle(
            'TableCell',
            fontName=base_font,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT
        )

        return styles

    def set_logo(self, logo_path: str):
        """Imposta il logo per l'intestazione"""
        if os.path.exists(logo_path):
            self.logo_path = logo_path

    def _add_header(self):
        """Aggiunge l'intestazione del documento"""
        # Data e ora
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")

        # Tabella per layout intestazione
        header_data = []

        # Logo a destra (se disponibile)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=4*cm, height=2*cm)
                header_data.append(['', '', logo])
            except:
                header_data.append(['', '', ''])
        else:
            # Placeholder per logo
            header_data.append(['', '', Paragraph("[ LOGO ]", self.styles['HeaderRight'])])

        header_table = Table(header_data, colWidths=[6*cm, 6*cm, 5*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.elements.append(header_table)
        self.elements.append(Spacer(1, 1*cm))

        # Titolo centrato
        self.elements.append(Paragraph(self.report_title, self.styles['Title']))

        # Data e ora
        self.elements.append(Paragraph(
            f"Data: {date_str} - Ora: {time_str}",
            self.styles['Subtitle']
        ))

        # Linea separatrice
        self.elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#16213e'),
            spaceBefore=20,
            spaceAfter=30
        ))

    def add_chapter(self, title: str, content: str = None):
        """Aggiunge un capitolo"""
        self.chapter_counter += 1
        self.section_counter = 0
        self.subsection_counter = 0

        chapter_title = f"CAPITOLO {self.chapter_counter}: {title.upper()}"
        self.elements.append(Paragraph(chapter_title, self.styles['Chapter']))

        # Linea sotto il capitolo
        self.elements.append(HRFlowable(
            width="60%",
            thickness=1,
            color=colors.HexColor('#16213e'),
            spaceBefore=5,
            spaceAfter=15
        ))

        if content:
            self.elements.append(Paragraph(content, self.styles['Normal']))

    def add_section(self, title: str, content: str = None):
        """Aggiunge un paragrafo"""
        self.section_counter += 1
        self.subsection_counter = 0

        section_title = f"{self.chapter_counter}.{self.section_counter} {title}"
        self.elements.append(Paragraph(section_title, self.styles['Section']))

        if content:
            self.elements.append(Paragraph(content, self.styles['Normal']))

    def add_subsection(self, title: str, content: str = None):
        """Aggiunge un sottoparagrafo"""
        self.subsection_counter += 1

        subsection_title = f"{self.chapter_counter}.{self.section_counter}.{self.subsection_counter} {title}"
        self.elements.append(Paragraph(subsection_title, self.styles['Subsection']))

        if content:
            self.elements.append(Paragraph(content, self.styles['Normal']))

    def add_paragraph(self, text: str, style: str = 'Normal'):
        """Aggiunge un paragrafo di testo"""
        self.elements.append(Paragraph(text, self.styles.get(style, self.styles['Normal'])))

    def add_bullet_list(self, items: List[str]):
        """Aggiunge una lista puntata"""
        list_items = []
        for item in items:
            list_items.append(ListItem(
                Paragraph(item, self.styles['ListItem']),
                leftIndent=20,
                bulletColor=colors.HexColor('#16213e')
            ))

        self.elements.append(ListFlowable(
            list_items,
            bulletType='bullet',
            start='bulletchar',
            leftIndent=10,
            bulletFontSize=8
        ))

    def add_numbered_list(self, items: List[str]):
        """Aggiunge una lista numerata"""
        for i, item in enumerate(items, 1):
            self.elements.append(Paragraph(
                f"{i}. {item}",
                self.styles['ListItem']
            ))

    def add_table(self, headers: List[str], data: List[List[str]], title: str = None):
        """Aggiunge una tabella"""
        if title:
            self.elements.append(Paragraph(title, self.styles['Subsection']))

        # Prepara dati tabella
        table_data = [headers] + data

        # Calcola larghezze colonne
        col_width = (17*cm) / len(headers)
        col_widths = [col_width] * len(headers)

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),

            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),

            # Alternating rows
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#16213e')),
        ]))

        self.elements.append(table)
        self.elements.append(Spacer(1, 0.5*cm))

    def add_info_box(self, title: str, content: str):
        """Aggiunge un box informativo evidenziato"""
        box_content = f"<b>{title}</b><br/><br/>{content}"
        self.elements.append(Spacer(1, 0.3*cm))

        # Crea tabella per box
        box_data = [[Paragraph(box_content, self.styles['Normal'])]]
        box_table = Table(box_data, colWidths=[16*cm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#16213e')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))

        self.elements.append(box_table)
        self.elements.append(Spacer(1, 0.5*cm))

    def add_highlight(self, text: str):
        """Aggiunge testo evidenziato"""
        self.elements.append(Paragraph(text, self.styles['Highlight']))

    def add_spacer(self, height: float = 0.5):
        """Aggiunge spazio verticale"""
        self.elements.append(Spacer(1, height*cm))

    def add_page_break(self):
        """Aggiunge interruzione di pagina"""
        self.elements.append(PageBreak())

    def add_horizontal_line(self):
        """Aggiunge linea orizzontale"""
        self.elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#cccccc'),
            spaceBefore=10,
            spaceAfter=10
        ))

    def generate(self,
                 extracted_data,
                 analysis_report,
                 psychological_profile,
                 password_profile,
                 security_report) -> str:
        """
        Genera il report completo.

        Args:
            extracted_data: Dati estratti dal parser
            analysis_report: Report dell'analizzatore
            psychological_profile: Profilo psicologico
            password_profile: Profilo password
            security_report: Report di sicurezza

        Returns:
            str: Percorso del file PDF generato
        """
        # Reset elementi
        self.elements = []
        self.chapter_counter = 0

        # Aggiungi intestazione
        self._add_header()

        # CAPITOLO 1: INTRODUZIONE
        self._add_introduction()

        # CAPITOLO 2: SCHEDA SOGGETTO
        self._add_subject_profile(extracted_data)

        # CAPITOLO 3: ANALISI E CORRELAZIONE DATI
        self._add_data_analysis(extracted_data, analysis_report)

        # CAPITOLO 4: PROFILO PSICOLOGICO
        self._add_psychological_analysis(psychological_profile)

        # CAPITOLO 5: ANALISI PASSWORD E SICUREZZA
        self._add_password_security_analysis(password_profile, security_report)

        # CAPITOLO 6: VALUTAZIONE COMPLESSIVA
        self._add_overall_assessment(security_report, analysis_report)

        # CAPITOLO 7: CONCLUSIONI
        self._add_conclusions(extracted_data, analysis_report, security_report)

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

    def _add_page_number(self, canvas, doc):
        """Aggiunge numero di pagina"""
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.setFillColor(colors.HexColor('#666666'))
        page_num = f"Pagina {doc.page}"
        canvas.drawCentredString(A4[0]/2, 1*cm, page_num)

        # Footer con disclaimer
        canvas.setFont('Times-Italic', 8)
        canvas.drawCentredString(A4[0]/2, 0.7*cm, "DOCUMENTO RISERVATO - FidelinvestigatorAI")
        canvas.restoreState()

    def _add_introduction(self):
        """Aggiunge il capitolo introduttivo su OSINT"""
        self.add_chapter("INTRODUZIONE")

        self.add_section("Cos'è l'OSINT")
        self.add_paragraph(
            "L'OSINT (Open Source Intelligence) rappresenta una disciplina dell'intelligence "
            "che si occupa della raccolta, analisi e utilizzo di informazioni provenienti da "
            "fonti pubblicamente accessibili. Questa metodologia investigativa permette di "
            "costruire un quadro informativo completo su un soggetto attraverso l'aggregazione "
            "e la correlazione di dati disponibili nel dominio pubblico."
        )

        self.add_paragraph(
            "Le fonti OSINT comprendono una vasta gamma di risorse: siti web, social media, "
            "registri pubblici, pubblicazioni, forum, e qualsiasi altra informazione "
            "accessibile senza necessità di autorizzazioni speciali o tecniche di intrusione. "
            "L'efficacia dell'OSINT risiede nella capacità di trasformare frammenti di "
            "informazione apparentemente insignificanti in intelligence actionable."
        )

        self.add_section("Metodologia Investigativa")
        self.add_paragraph(
            "L'indagine OSINT presentata in questo report è stata condotta seguendo una "
            "metodologia strutturata che comprende le seguenti fasi operative:"
        )

        self.add_bullet_list([
            "<b>Raccolta dati (Collection)</b>: Acquisizione sistematica di informazioni da "
            "fonti pubbliche attraverso tecniche di web scraping, analisi dei social media, "
            "e interrogazione di archivi pubblici.",

            "<b>Elaborazione (Processing)</b>: Normalizzazione, deduplicazione e strutturazione "
            "dei dati grezzi raccolti per prepararli all'analisi.",

            "<b>Analisi (Analysis)</b>: Correlazione dei dati, identificazione di pattern, "
            "verifica dell'attendibilità delle fonti e costruzione di un quadro informativo coerente.",

            "<b>Profilazione (Profiling)</b>: Costruzione del profilo del soggetto attraverso "
            "l'integrazione di informazioni anagrafiche, comportamentali e relazionali.",

            "<b>Valutazione (Assessment)</b>: Stima del livello di esposizione digitale, "
            "identificazione di vulnerabilità e rischi associati."
        ])

        self.add_section("Ambito e Limitazioni")
        self.add_paragraph(
            "Il presente report si basa esclusivamente su informazioni pubblicamente disponibili "
            "al momento dell'indagine. Le conclusioni e le valutazioni espresse hanno carattere "
            "probabilistico e si basano sull'interpretazione professionale dei dati raccolti. "
            "L'accuratezza del profilo dipende dalla qualità e completezza delle fonti disponibili."
        )

        self.add_paragraph(
            "È importante sottolineare che questo tipo di analisi non costituisce prova legale "
            "e deve essere considerato come elemento di supporto per ulteriori approfondimenti "
            "investigativi condotti nelle sedi appropriate."
        )

        self.add_page_break()

    def _add_subject_profile(self, data):
        """Aggiunge la scheda soggetto dettagliata"""
        self.add_chapter("SCHEDA SOGGETTO")

        # Dati anagrafici
        self.add_section("Dati Anagrafici")

        personal = data.personal_info
        anagrafica_data = []

        if personal.full_name:
            anagrafica_data.append(["Nome Completo", personal.full_name])
        if personal.date_of_birth:
            anagrafica_data.append(["Data di Nascita", personal.date_of_birth])
        if personal.age:
            anagrafica_data.append(["Età", str(personal.age)])
        if personal.gender:
            anagrafica_data.append(["Genere", personal.gender])
        if personal.nationality:
            anagrafica_data.append(["Nazionalità", personal.nationality])
        if personal.occupation:
            anagrafica_data.append(["Professione", personal.occupation])
        if personal.aliases:
            anagrafica_data.append(["Alias Noti", ", ".join(personal.aliases)])

        if anagrafica_data:
            self.add_table(["Campo", "Valore"], anagrafica_data)
        else:
            self.add_paragraph(
                "Dati anagrafici non disponibili o non sufficienti per l'identificazione."
            )

        # Contatti
        self.add_section("Informazioni di Contatto")

        self.add_subsection("Indirizzi Email")
        if data.contact_info.emails:
            email_data = []
            for email_info in data.contact_info.emails:
                email = email_info.get('email', 'N/A')
                domain = email_info.get('domain', 'N/A')
                email_data.append([email, domain])
            self.add_table(["Email", "Dominio"], email_data)
        else:
            self.add_paragraph("Nessun indirizzo email identificato.")

        self.add_subsection("Numeri di Telefono")
        if data.contact_info.phones:
            phone_data = []
            for phone_info in data.contact_info.phones:
                number = phone_info.get('number', 'N/A')
                country = phone_info.get('country_code', 'N/A')
                phone_data.append([number, country])
            self.add_table(["Numero", "Paese"], phone_data)
        else:
            self.add_paragraph("Nessun numero di telefono identificato.")

        # Presenza Social Media
        self.add_section("Presenza Social Media")
        if data.social_media:
            social_data = []
            for profile in data.social_media:
                social_data.append([
                    profile.platform.capitalize(),
                    profile.username or "N/A",
                    str(profile.followers) if profile.followers else "N/D"
                ])
            self.add_table(["Piattaforma", "Username", "Followers"], social_data)

            self.add_paragraph(
                f"Il soggetto mantiene una presenza attiva su {len(data.social_media)} "
                f"piattaforme social media, indicando un livello di esposizione digitale "
                f"{'elevato' if len(data.social_media) > 5 else 'moderato' if len(data.social_media) > 2 else 'contenuto'}."
            )
        else:
            self.add_paragraph("Nessun profilo social media identificato.")

        # Username
        self.add_section("Username e Identità Digitali")
        if data.usernames:
            self.add_paragraph(
                f"Sono stati identificati {len(data.usernames)} username associati al soggetto:"
            )
            self.add_bullet_list(data.usernames[:10])

            # Analisi consistenza
            unique = len(set(u.lower() for u in data.usernames))
            if unique == 1:
                self.add_paragraph(
                    "Il soggetto utilizza un username consistente su tutte le piattaforme, "
                    "facilitando la correlazione delle identità digitali."
                )
            else:
                self.add_paragraph(
                    f"Il soggetto utilizza {unique} username diversi, suggerendo una "
                    "strategia di compartimentalizzazione dell'identità digitale."
                )
        else:
            self.add_paragraph("Nessun username aggiuntivo identificato.")

        self.add_page_break()

    def _add_data_analysis(self, data, analysis):
        """Aggiunge l'analisi e correlazione dei dati"""
        self.add_chapter("ANALISI E CORRELAZIONE DATI")

        # Correlazioni identificate
        self.add_section("Correlazioni Identificate")

        if analysis.correlations:
            critical = [c for c in analysis.correlations if c.significance == "critical"]
            high = [c for c in analysis.correlations if c.significance == "high"]
            medium = [c for c in analysis.correlations if c.significance == "medium"]

            if critical:
                self.add_subsection("Correlazioni Critiche")
                for corr in critical:
                    self.add_info_box("ATTENZIONE", corr.description)

            if high:
                self.add_subsection("Correlazioni ad Alta Significatività")
                for corr in high:
                    self.add_paragraph(f"• {corr.description} (Confidenza: {corr.confidence:.0%})")

            if medium:
                self.add_subsection("Altre Correlazioni Rilevanti")
                for corr in medium[:5]:
                    self.add_paragraph(f"• {corr.description}")
        else:
            self.add_paragraph("Non sono state identificate correlazioni significative.")

        # Data Breach
        self.add_section("Esposizione a Data Breach")

        if data.data_breaches:
            self.add_paragraph(
                f"Il soggetto risulta coinvolto in {len(data.data_breaches)} data breach documentati. "
                "Questo rappresenta un indicatore critico di esposizione delle credenziali."
            )

            breach_data = []
            for breach in data.data_breaches:
                breach_data.append([
                    breach.breach_name,
                    breach.breach_date or "N/D",
                    ", ".join(breach.data_exposed[:3]) if breach.data_exposed else "N/D"
                ])
            self.add_table(["Breach", "Data", "Dati Esposti"], breach_data)
        else:
            self.add_paragraph(
                "Non risultano coinvolgimenti in data breach noti. Questo è un indicatore positivo "
                "per la sicurezza delle credenziali del soggetto."
            )

        # Pattern di attività
        self.add_section("Pattern di Attività")

        if analysis.activity_patterns:
            for pattern in analysis.activity_patterns:
                self.add_paragraph(
                    f"<b>{pattern.pattern_type.replace('_', ' ').title()}</b>: {pattern.description}"
                )
        else:
            self.add_paragraph("Non sono stati identificati pattern di attività significativi.")

        # Key Findings
        self.add_section("Findings Chiave")
        if analysis.key_findings:
            self.add_bullet_list(analysis.key_findings)

        self.add_page_break()

    def _add_psychological_analysis(self, profile):
        """Aggiunge l'analisi psicologica"""
        self.add_chapter("PROFILO PSICOLOGICO")

        self.add_section("Premessa Metodologica")
        self.add_paragraph(
            "Il profilo psicologico presentato è stato elaborato attraverso l'analisi del "
            "comportamento digitale del soggetto, le scelte identitarie online, i pattern "
            "comunicativi e le interazioni sui social media. Questa analisi si basa su "
            "metodologie di behavioral profiling e digital psychology, fornendo indicazioni "
            "probabilistiche che devono essere validate con ulteriori elementi investigativi."
        )

        # Tratti di personalità
        self.add_section("Tratti di Personalità")

        if profile.personality_traits:
            for trait in profile.personality_traits:
                self.add_subsection(f"{trait.dimension.title()}: {trait.intensity.title()}")
                self.add_paragraph(trait.trait)
                if trait.evidence:
                    self.add_paragraph(f"<i>Evidenze: {', '.join(trait.evidence[:3])}</i>")
        else:
            self.add_paragraph("Dati insufficienti per l'analisi dei tratti di personalità.")

        # Pattern comportamentali
        self.add_section("Pattern Comportamentali")

        if profile.behavioral_patterns:
            for pattern in profile.behavioral_patterns:
                self.add_paragraph(f"<b>{pattern.description}</b>")
                self.add_paragraph(f"Implicazione psicologica: {pattern.psychological_implication}")
                self.add_spacer(0.2)
        else:
            self.add_paragraph("Non sono stati identificati pattern comportamentali significativi.")

        # Stile comunicativo
        self.add_section("Stile Comunicativo")

        if profile.communication_style:
            style = profile.communication_style
            self.add_paragraph(
                f"Il soggetto presenta uno stile comunicativo prevalentemente <b>{style.formality_level}</b> "
                f"con un livello di complessità linguistica <b>{style.language_complexity}</b> "
                f"e un tono emotivo <b>{style.emotional_tone}</b>."
            )
            if style.key_characteristics:
                self.add_paragraph("Caratteristiche distintive:")
                self.add_bullet_list(style.key_characteristics)

        # Profilo di rischio comportamentale
        self.add_section("Profilo di Rischio Comportamentale")

        if profile.risk_profile:
            rp = profile.risk_profile
            self.add_table(
                ["Indicatore", "Livello"],
                [
                    ["Consapevolezza Privacy", rp.privacy_awareness.upper()],
                    ["Security Consciousness", rp.security_consciousness.upper()],
                    ["Tolleranza al Rischio", rp.risk_tolerance.upper()],
                ]
            )

        # Vulnerabilità e punti di forza
        if profile.vulnerabilities:
            self.add_section("Vulnerabilità Identificate")
            self.add_bullet_list(profile.vulnerabilities)

        if profile.strengths:
            self.add_section("Punti di Forza")
            self.add_bullet_list(profile.strengths)

        # Summary psicologico
        self.add_section("Sintesi del Profilo")
        if profile.psychological_summary:
            self.add_paragraph(profile.psychological_summary)

        self.add_page_break()

    def _add_password_security_analysis(self, pwd_profile, security_report):
        """Aggiunge l'analisi password e sicurezza"""
        self.add_chapter("ANALISI SICUREZZA DIGITALE")

        # Analisi password
        self.add_section("Analisi Password")

        if pwd_profile.passwords_analyzed > 0:
            self.add_paragraph(
                f"Sono state analizzate {pwd_profile.passwords_analyzed} password associate al soggetto."
            )

            # Score sicurezza
            self.add_info_box(
                f"LIVELLO SICUREZZA PASSWORD: {pwd_profile.security_level}",
                f"Score: {pwd_profile.security_score:.0f}/100"
            )

            # Pattern identificati
            self.add_subsection("Pattern di Costruzione")
            if pwd_profile.construction_method:
                self.add_paragraph(pwd_profile.construction_method)

            if pwd_profile.patterns:
                critical_patterns = [p for p in pwd_profile.patterns if p.security_impact == 'critical']
                if critical_patterns:
                    self.add_paragraph("<b>Pattern critici identificati:</b>")
                    for pattern in critical_patterns:
                        self.add_paragraph(f"• {pattern.description}")

            # Elementi comuni
            if pwd_profile.common_elements:
                self.add_subsection("Elementi Ricorrenti")
                self.add_paragraph(
                    "Sono stati identificati i seguenti elementi comuni nelle password analizzate:"
                )
                self.add_bullet_list([f"'{elem}'" for elem in pwd_profile.common_elements])

            # Insight psicologici
            if pwd_profile.psychological_insights:
                self.add_subsection("Insight Comportamentali")
                for insight in pwd_profile.psychological_insights:
                    self.add_paragraph(insight)

            # Predizioni
            if pwd_profile.predictions:
                self.add_subsection("Predizioni su Possibili Password")
                self.add_paragraph(
                    "Basandosi sui pattern identificati, è possibile ipotizzare le seguenti "
                    "strutture di password per altri account del soggetto:"
                )
                for pred in pwd_profile.predictions[:3]:
                    self.add_paragraph(f"<b>{pred.prediction_type}</b>: {pred.description}")
        else:
            self.add_paragraph(
                "Non sono state trovate password esposte associate al soggetto. "
                "Questo può indicare buone pratiche di sicurezza o semplicemente "
                "l'assenza di coinvolgimento in breach con esposizione di credenziali."
            )

        # Valutazione sicurezza
        self.add_section("Valutazione Postura di Sicurezza")

        if security_report.security_posture:
            posture = security_report.security_posture

            self.add_info_box(
                f"GRADE SICUREZZA: {posture.grade}",
                f"Score complessivo: {posture.overall_score:.0f}/100"
            )

            if posture.weaknesses:
                self.add_subsection("Debolezze Critiche")
                self.add_bullet_list(posture.weaknesses)

            if posture.strengths:
                self.add_subsection("Punti di Forza")
                self.add_bullet_list(posture.strengths)

        # Vulnerabilità
        self.add_section("Vulnerabilità Identificate")

        if security_report.vulnerabilities:
            for vuln in security_report.vulnerabilities:
                severity_color = {
                    'critical': '#c70039',
                    'high': '#ff5722',
                    'medium': '#ff9800',
                    'low': '#4caf50'
                }.get(vuln.severity, '#666666')

                self.add_paragraph(
                    f"<font color='{severity_color}'><b>[{vuln.severity.upper()}]</b></font> "
                    f"{vuln.vulnerability_type}: {vuln.description}"
                )

        # Minacce
        self.add_section("Valutazione delle Minacce")

        if security_report.threat_assessments:
            threat_data = []
            for threat in security_report.threat_assessments:
                threat_data.append([
                    threat.threat_type,
                    threat.likelihood.upper(),
                    threat.impact.upper()
                ])
            self.add_table(["Minaccia", "Probabilità", "Impatto"], threat_data)

        self.add_page_break()

    def _add_overall_assessment(self, security_report, analysis):
        """Aggiunge la valutazione complessiva"""
        self.add_chapter("VALUTAZIONE COMPLESSIVA")

        self.add_section("Digital Footprint")

        footprint = security_report.digital_footprint_analysis
        if footprint:
            self.add_table(
                ["Parametro", "Valore"],
                [
                    ["Dimensione Footprint", footprint.get('size', 'N/D')],
                    ["Consistenza Identità", footprint.get('consistency', 'N/D')],
                    ["Categorie Dati Esposti", str(len(footprint.get('data_categories', [])))],
                    ["Piattaforme Attive", str(len(footprint.get('platforms', [])))],
                ]
            )

        self.add_section("Indicatori di Rischio")

        if analysis.risk_indicators:
            for risk in analysis.risk_indicators:
                self.add_paragraph(
                    f"<b>{risk.indicator_type}</b> [{risk.severity.upper()}]: {risk.description}"
                )
                if risk.recommendations:
                    self.add_paragraph("<i>Raccomandazioni:</i>")
                    self.add_bullet_list(risk.recommendations[:2])
                self.add_spacer(0.3)

        # Privacy score
        self.add_section("Valutazione Privacy")
        self.add_paragraph(
            f"Il Privacy Score del soggetto è <b>{security_report.privacy_score:.0f}/100</b>. "
            f"Questo valore indica un livello di esposizione delle informazioni personali "
            f"{'critico' if security_report.privacy_score < 30 else 'elevato' if security_report.privacy_score < 50 else 'moderato' if security_report.privacy_score < 70 else 'contenuto'}."
        )

        # Raccomandazioni prioritizzate
        self.add_section("Raccomandazioni Operative")

        if security_report.recommendations_priority:
            rec_data = []
            for rec in security_report.recommendations_priority[:6]:
                rec_data.append([
                    rec.get('priority', 'N/D'),
                    rec.get('action', 'N/D'),
                    rec.get('timeline', 'N/D')
                ])
            self.add_table(["Priorità", "Azione", "Timeline"], rec_data)

        self.add_page_break()

    def _add_conclusions(self, data, analysis, security_report):
        """Aggiunge le conclusioni"""
        self.add_chapter("CONCLUSIONI")

        self.add_section("Sintesi Investigativa")

        target_name = data.personal_info.full_name or "Il soggetto dell'indagine"

        self.add_paragraph(
            f"L'analisi OSINT condotta su <b>{target_name}</b> ha permesso di costruire un "
            "quadro informativo dettagliato che evidenzia le seguenti caratteristiche principali:"
        )

        # Conclusioni basate sui dati
        conclusions = []

        # Identità digitale
        if data.social_media:
            conclusions.append(
                f"Il soggetto mantiene una presenza digitale attiva su {len(data.social_media)} "
                f"piattaforme social media, con un livello di esposizione "
                f"{'elevato' if len(data.social_media) > 5 else 'moderato'}."
            )

        # Security
        if security_report.security_posture:
            grade = security_report.security_posture.grade
            conclusions.append(
                f"La postura di sicurezza complessiva è stata valutata con grade <b>{grade}</b>, "
                f"indicando {'criticità significative che richiedono intervento immediato' if grade in ['D', 'F'] else 'margini di miglioramento nella gestione della sicurezza digitale' if grade == 'C' else 'una gestione ragionevolmente adeguata della sicurezza'}."
            )

        # Breach
        if data.data_breaches:
            conclusions.append(
                f"Il coinvolgimento in {len(data.data_breaches)} data breach rappresenta "
                "un fattore di rischio significativo per la sicurezza delle credenziali. "
                "Si raccomanda un cambio immediato di tutte le password potenzialmente compromesse."
            )

        # Password
        if data.raw_passwords:
            conclusions.append(
                f"L'esposizione di {len(data.raw_passwords)} password in chiaro costituisce "
                "una vulnerabilità critica che richiede azione immediata."
            )

        for conclusion in conclusions:
            self.add_paragraph(conclusion)

        self.add_section("Considerazioni Finali")

        self.add_paragraph(
            "L'indagine ha permesso di delineare un profilo completo del soggetto sotto il "
            "profilo dell'identità digitale, della sicurezza e degli aspetti comportamentali. "
            "Le informazioni raccolte e le correlazioni identificate forniscono elementi "
            "utili per comprendere come il soggetto si muove nel web e quali sono le "
            "potenziali vulnerabilità della sua presenza online."
        )

        self.add_paragraph(
            "Si raccomanda di utilizzare le informazioni contenute in questo report come "
            "base per eventuali approfondimenti investigativi e di implementare le "
            "raccomandazioni di sicurezza prioritarie per ridurre l'esposizione al rischio."
        )

        self.add_section("Avvertenze")

        self.add_paragraph(
            "<i>Il presente report è stato redatto sulla base di informazioni pubblicamente "
            "disponibili e rappresenta un'analisi professionale di intelligence. Le conclusioni "
            "hanno carattere probabilistico e devono essere validate attraverso ulteriori "
            "elementi di riscontro. Il documento ha natura riservata e deve essere trattato "
            "in conformità con le normative vigenti sulla privacy e sulla protezione dei dati personali.</i>"
        )

        # Firma
        self.add_spacer(2)
        self.add_horizontal_line()
        self.add_paragraph(
            f"<b>FidelinvestigatorAI</b><br/>"
            f"Agente Investigativo OSINT<br/>"
            f"Report generato il {datetime.now().strftime('%d/%m/%Y alle ore %H:%M')}"
        )
