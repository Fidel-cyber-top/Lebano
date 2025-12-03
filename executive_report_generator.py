#!/usr/bin/env python3
"""
FidelinvestigatorAI - Executive Vulnerability Assessment Report Generator
==========================================================================

Genera report professionali in formato DOCX seguendo standard:
- CIA/DEA/ROS/DIA Intelligence Reporting
- Executive Vulnerability Assessment Framework
- OSINT Industry Best Practices

Autore: FidelinvestigatorAI Team
Classificazione: RISERVATO
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import re

# Auto-install dependencies
def install_deps():
    required = ['python-docx', 'Pillow']
    import subprocess
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg, '-q'])

install_deps()

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# =============================================================================
# COLOR SCHEME
# =============================================================================

class Colors:
    """Corporate color scheme"""
    HEADER_ORANGE = RGBColor(212, 168, 75)      # #D4A84B
    BACKGROUND_GRAY = RGBColor(232, 232, 232)   # #E8E8E8
    DARK_GRAY = RGBColor(64, 64, 64)            # #404040
    BLACK = RGBColor(0, 0, 0)
    WHITE = RGBColor(255, 255, 255)

    # Exposure levels
    HIGH_EXPOSURE = RGBColor(220, 53, 69)       # Red
    MEDIUM_EXPOSURE = RGBColor(255, 193, 7)     # Orange/Yellow
    LOW_EXPOSURE = RGBColor(40, 167, 69)        # Green

    # Status colors
    CRITICAL = RGBColor(139, 0, 0)              # Dark red
    WARNING = RGBColor(255, 140, 0)             # Dark orange
    INFO = RGBColor(0, 123, 255)                # Blue
    SUCCESS = RGBColor(34, 139, 34)             # Forest green


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ExecutiveProfile:
    """Profile data for a C-level executive"""
    name: str
    title: str
    exposure_level: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    age: Optional[int] = None
    start_date: Optional[str] = None
    compensation: Optional[str] = None

    # Professional info
    current_role: str = ""
    previous_roles: List[str] = field(default_factory=list)
    board_memberships: List[str] = field(default_factory=list)

    # Education
    education: List[Dict[str, str]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

    # Online presence
    email: Optional[str] = None
    online_accounts: List[Dict[str, Any]] = field(default_factory=list)
    data_breaches: List[Dict[str, Any]] = field(default_factory=list)

    # Personal info exposed
    addresses: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    family_members: List[str] = field(default_factory=list)
    vehicles: List[str] = field(default_factory=list)
    photos_found: int = 0
    websites: List[str] = field(default_factory=list)


@dataclass
class CompanyInfo:
    """Company information"""
    name: str
    description: str = ""
    sector: str = ""
    headquarters: str = ""
    locations: List[str] = field(default_factory=list)
    products_services: List[str] = field(default_factory=list)
    revenue: Optional[str] = None
    employees: Optional[str] = None
    funding: Optional[str] = None
    ticker: Optional[str] = None
    notable_clients: List[str] = field(default_factory=list)
    email_format: str = ""


@dataclass
class InvestigatorProfile:
    """Investigator credentials"""
    name: str = "FidelinvestigatorAI"
    title: str = "Senior OSINT Analyst"
    background: str = ""
    certifications: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    methodology: str = ""
    tools: List[str] = field(default_factory=list)


@dataclass
class AssessmentData:
    """Complete assessment data"""
    project_name: str
    company: CompanyInfo
    investigator: InvestigatorProfile
    executives: List[ExecutiveProfile]
    start_date: str
    end_date: str

    # Analysis results
    key_findings: List[str] = field(default_factory=list)
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, str]] = field(default_factory=list)
    risk_assessment: str = ""

    # AI Analysis
    correlation_analysis: str = ""
    psychological_profiles: Dict[str, str] = field(default_factory=dict)
    threat_assessment: str = ""


# =============================================================================
# DOCX HELPER FUNCTIONS
# =============================================================================

def set_cell_shading(cell, color: RGBColor):
    """Set background color for a table cell"""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), f'{color.red:02X}{color.green:02X}{color.blue:02X}')
    cell._tc.get_or_add_tcPr().append(shading)


def add_horizontal_line(paragraph):
    """Add a horizontal line after a paragraph"""
    p = paragraph._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'D4A84B')
    pBdr.append(bottom)
    pPr.append(pBdr)


def create_styled_paragraph(doc, text: str, style: str = None,
                           bold: bool = False, italic: bool = False,
                           font_size: int = 11, color: RGBColor = None,
                           alignment: WD_ALIGN_PARAGRAPH = None,
                           space_after: int = 12) -> Any:
    """Create a styled paragraph"""
    para = doc.add_paragraph()
    run = para.add_run(text)

    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if font_size:
        run.font.size = Pt(font_size)
    if color:
        run.font.color.rgb = color
    if alignment:
        para.alignment = alignment

    para.paragraph_format.space_after = Pt(space_after)

    return para


# =============================================================================
# EXECUTIVE VULNERABILITY ASSESSMENT REPORT GENERATOR
# =============================================================================

class ExecutiveReportGenerator:
    """Generates Executive Vulnerability Assessment reports in DOCX format"""

    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.getcwd()
        self.doc = None
        self.styles_initialized = False

    def _initialize_document(self):
        """Initialize document with custom styles"""
        self.doc = Document()

        # Set default font
        style = self.doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(11)

        # Create custom styles
        self._create_custom_styles()
        self.styles_initialized = True

    def _create_custom_styles(self):
        """Create custom document styles"""
        styles = self.doc.styles

        # Title style
        if 'ReportTitle' not in [s.name for s in styles]:
            title_style = styles.add_style('ReportTitle', WD_STYLE_TYPE.PARAGRAPH)
            title_style.font.size = Pt(28)
            title_style.font.bold = True
            title_style.font.color.rgb = Colors.DARK_GRAY
            title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_style.paragraph_format.space_after = Pt(24)

        # Section Header style
        if 'SectionHeader' not in [s.name for s in styles]:
            section_style = styles.add_style('SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
            section_style.font.size = Pt(16)
            section_style.font.bold = True
            section_style.font.color.rgb = Colors.HEADER_ORANGE
            section_style.paragraph_format.space_before = Pt(18)
            section_style.paragraph_format.space_after = Pt(12)

        # Subsection style
        if 'SubSection' not in [s.name for s in styles]:
            sub_style = styles.add_style('SubSection', WD_STYLE_TYPE.PARAGRAPH)
            sub_style.font.size = Pt(14)
            sub_style.font.bold = True
            sub_style.font.color.rgb = Colors.DARK_GRAY
            sub_style.paragraph_format.space_before = Pt(12)
            sub_style.paragraph_format.space_after = Pt(8)

    def _add_cover_page(self, data: AssessmentData):
        """Add cover page"""
        # Logo placeholder
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("[LOGO PLACEHOLDER - PIOSINT EXPERT]")
        run.font.size = Pt(14)
        run.font.color.rgb = Colors.DARK_GRAY

        # Spacing
        self.doc.add_paragraph()
        self.doc.add_paragraph()

        # Company name
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(data.company.name.upper())
        run.font.size = Pt(24)
        run.font.bold = True
        run.font.color.rgb = Colors.BLACK

        # Title
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("EXECUTIVE VULNERABILITY ASSESSMENT")
        run.font.size = Pt(32)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE

        # Subtitle
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("Intelligence-Grade OSINT Investigation Report")
        run.font.size = Pt(14)
        run.font.italic = True
        run.font.color.rgb = Colors.DARK_GRAY

        # Spacing
        self.doc.add_paragraph()
        self.doc.add_paragraph()

        # Date range
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(f"Assessment Period: {data.start_date} - {data.end_date}")
        run.font.size = Pt(12)
        run.font.color.rgb = Colors.DARK_GRAY

        # Classification
        self.doc.add_paragraph()
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("CLASSIFICAZIONE: RISERVATO")
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = Colors.CRITICAL

        # Icons placeholder
        self.doc.add_paragraph()
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("[🔒 CYBERSECURITY] [🔍 OSINT] [👤 SOCIAL ENGINEERING]")
        run.font.size = Pt(16)

        # Page break
        self.doc.add_page_break()

    def _add_table_of_contents(self, data: AssessmentData):
        """Add table of contents"""
        para = self.doc.add_paragraph()
        run = para.add_run("TABLE OF CONTENTS")
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE
        add_horizontal_line(para)

        self.doc.add_paragraph()

        # TOC entries
        toc_entries = [
            ("1.", "Executive Summary", "3"),
            ("2.", "Investigator Profile", "5"),
            ("3.", f"About {data.company.name}", "7"),
            ("4.", "Identification of C-Level Personnel", "9"),
            ("5.", "Profiling of C-Level Staff", "11"),
        ]

        # Add executive sub-entries
        for i, exec in enumerate(data.executives):
            exposure_color = self._get_exposure_label(exec.exposure_level)
            toc_entries.append((f"   5.{i+1}", f"{exec.name} ({exec.title}) - {exposure_color}", ""))

        toc_entries.extend([
            ("6.", "Analysis of Data and Information Found", ""),
            ("7.", "Final Considerations and Conclusions", ""),
        ])

        # Create TOC table
        table = self.doc.add_table(rows=len(toc_entries), cols=3)
        table.autofit = True

        for i, (num, title, page) in enumerate(toc_entries):
            row = table.rows[i]
            row.cells[0].text = num
            row.cells[1].text = title
            row.cells[2].text = page

            # Style
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.paragraph_format.space_after = Pt(6)

        self.doc.add_page_break()

    def _add_executive_summary(self, data: AssessmentData):
        """Add executive summary section"""
        # Header
        para = self.doc.add_paragraph()
        run = para.add_run("EXECUTIVE SUMMARY")
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE
        add_horizontal_line(para)

        # Project info table
        info_table = self.doc.add_table(rows=4, cols=2)
        info_table.style = 'Table Grid'

        info_data = [
            ("Project Name:", data.project_name),
            ("Date:", datetime.now().strftime("%d/%m/%Y")),
            ("Prepared By:", data.investigator.name),
            ("Reporting Period:", f"{data.start_date} - {data.end_date}")
        ]

        for i, (label, value) in enumerate(info_data):
            row = info_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[0].paragraphs[0].runs[0].bold = True
            set_cell_shading(row.cells[0], Colors.BACKGROUND_GRAY)

        self.doc.add_paragraph()

        # Background
        para = self.doc.add_paragraph()
        run = para.add_run("BACKGROUND")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = Colors.DARK_GRAY

        background_text = f"""
This Executive Vulnerability Assessment was conducted on {data.company.name} to evaluate
the digital exposure and security posture of the organization's C-level executives.
The assessment utilized advanced OSINT (Open Source Intelligence) methodologies following
CIA/DEA/ROS/DIA intelligence standards to identify potential vulnerabilities that could
be exploited by threat actors for social engineering, corporate espionage, or targeted attacks.
"""
        self.doc.add_paragraph(background_text.strip())

        # Key Findings
        para = self.doc.add_paragraph()
        run = para.add_run("KEY FINDINGS")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = Colors.DARK_GRAY

        # Create 3-column layout for findings
        findings_table = self.doc.add_table(rows=1, cols=3)
        findings_table.autofit = True

        # Column 1: Key Findings
        cell1 = findings_table.rows[0].cells[0]
        para = cell1.add_paragraph()
        run = para.add_run("Key Findings")
        run.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE

        findings = [
            "C-Level Executive Profiling completed",
            f"{len(data.executives)} executives analyzed",
            "Data vulnerabilities identified",
            "Personal information exposure documented",
            "Organizational structure mapped"
        ]
        for finding in findings:
            cell1.add_paragraph(f"• {finding}")

        # Column 2: Mitigation Strategies
        cell2 = findings_table.rows[0].cells[1]
        para = cell2.add_paragraph()
        run = para.add_run("Mitigation Strategies")
        run.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE

        mitigations = [
            "Security awareness training",
            "Digital footprint reduction",
            "Privacy settings audit",
            "Credential monitoring",
            "Executive protection protocols"
        ]
        for mit in mitigations:
            cell2.add_paragraph(f"• {mit}")

        # Column 3: Conclusions
        cell3 = findings_table.rows[0].cells[2]
        para = cell3.add_paragraph()
        run = para.add_run("Conclusions")
        run.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE

        conclusions = [
            "Immediate action required for HIGH exposure",
            "Ongoing monitoring recommended",
            "Policy updates necessary",
            "Third-party risk assessment",
            "Incident response planning"
        ]
        for conc in conclusions:
            cell3.add_paragraph(f"• {conc}")

        self.doc.add_page_break()

    def _add_investigator_profile(self, data: AssessmentData):
        """Add investigator profile section"""
        para = self.doc.add_paragraph()
        run = para.add_run("INVESTIGATOR PROFILE")
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE
        add_horizontal_line(para)

        inv = data.investigator

        # Name and title
        para = self.doc.add_paragraph()
        run = para.add_run(inv.name)
        run.font.size = Pt(16)
        run.font.bold = True

        para = self.doc.add_paragraph()
        run = para.add_run(inv.title)
        run.font.size = Pt(12)
        run.font.italic = True
        run.font.color.rgb = Colors.DARK_GRAY

        # Background
        if inv.background:
            para = self.doc.add_paragraph()
            run = para.add_run("Professional Background")
            run.font.bold = True
            run.font.size = Pt(12)
            self.doc.add_paragraph(inv.background)

        # Certifications
        if inv.certifications:
            para = self.doc.add_paragraph()
            run = para.add_run("Certifications & Qualifications")
            run.font.bold = True
            run.font.size = Pt(12)

            for cert in inv.certifications:
                self.doc.add_paragraph(f"• {cert}", style='List Bullet')

        # Objectives
        para = self.doc.add_paragraph()
        run = para.add_run("Assessment Objectives")
        run.font.bold = True
        run.font.size = Pt(12)

        objectives = inv.objectives or [
            "Identify and profile C-level executives",
            "Assess digital exposure and vulnerability levels",
            "Document data breaches and credential exposure",
            "Map organizational structure and communication patterns",
            "Provide actionable mitigation recommendations"
        ]
        for obj in objectives:
            self.doc.add_paragraph(f"• {obj}", style='List Bullet')

        # Tools
        para = self.doc.add_paragraph()
        run = para.add_run("Methodology & Tools")
        run.font.bold = True
        run.font.size = Pt(12)

        tools = inv.tools or [
            "Maltego Enterprise - Entity relationship mapping",
            "Google Dorks - Advanced search techniques",
            "Sociallinks - Social media intelligence",
            "Pipl / RocketReach - People search engines",
            "OSINT Industries - Comprehensive OSINT platform",
            "OpenCorporates / Orbis - Corporate intelligence",
            "Shodan - Internet-connected device search",
            "HaveIBeenPwned - Breach database",
            "Hunchly - Web investigation documentation"
        ]

        # Tools table
        tools_table = self.doc.add_table(rows=len(tools), cols=1)
        tools_table.style = 'Table Grid'
        for i, tool in enumerate(tools):
            row = tools_table.rows[i]
            row.cells[0].text = tool
            if i % 2 == 0:
                set_cell_shading(row.cells[0], Colors.BACKGROUND_GRAY)

        self.doc.add_page_break()

    def _add_company_info(self, data: AssessmentData):
        """Add company information section"""
        company = data.company

        para = self.doc.add_paragraph()
        run = para.add_run(f"ABOUT {company.name.upper()}")
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE
        add_horizontal_line(para)

        # Company description
        if company.description:
            self.doc.add_paragraph(company.description)

        # Company info table
        info_table = self.doc.add_table(rows=10, cols=2)
        info_table.style = 'Table Grid'

        company_data = [
            ("Sector", company.sector or "N/A"),
            ("Headquarters", company.headquarters or "N/A"),
            ("Locations", ", ".join(company.locations) if company.locations else "N/A"),
            ("Products/Services", ", ".join(company.products_services) if company.products_services else "N/A"),
            ("Revenue", company.revenue or "N/A"),
            ("Employees", company.employees or "N/A"),
            ("Funding", company.funding or "N/A"),
            ("Ticker Symbol", company.ticker or "N/A (Private)"),
            ("Notable Clients", ", ".join(company.notable_clients) if company.notable_clients else "N/A"),
            ("Email Format", company.email_format or "N/A")
        ]

        for i, (label, value) in enumerate(company_data):
            row = info_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[0].paragraphs[0].runs[0].bold = True
            set_cell_shading(row.cells[0], Colors.BACKGROUND_GRAY)

        self.doc.add_page_break()

    def _add_clevel_identification(self, data: AssessmentData):
        """Add C-level identification section"""
        para = self.doc.add_paragraph()
        run = para.add_run("IDENTIFICATION OF C-LEVEL PERSONNEL")
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE
        add_horizontal_line(para)

        # Explanation
        explanation = """
C-level executives (Chief-level officers) represent the highest-ranking positions within
an organization. These individuals typically have significant access to sensitive corporate
information and are prime targets for social engineering attacks, corporate espionage,
and targeted cyber threats. Common C-level positions include:
"""
        self.doc.add_paragraph(explanation.strip())

        roles = [
            ("CEO", "Chief Executive Officer - Overall organizational leadership"),
            ("CFO", "Chief Financial Officer - Financial strategy and operations"),
            ("CTO", "Chief Technology Officer - Technology strategy and innovation"),
            ("CIO", "Chief Information Officer - IT infrastructure and systems"),
            ("COO", "Chief Operating Officer - Day-to-day operations"),
            ("CMO", "Chief Marketing Officer - Marketing and brand strategy"),
            ("CPO", "Chief Privacy Officer - Data privacy and compliance"),
            ("CISO", "Chief Information Security Officer - Cybersecurity")
        ]

        for abbr, desc in roles:
            para = self.doc.add_paragraph()
            run = para.add_run(f"{abbr}: ")
            run.bold = True
            para.add_run(desc)

        # Org chart placeholder
        self.doc.add_paragraph()
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("[ORGANIZATIONAL CHART PLACEHOLDER]")
        run.font.size = Pt(12)
        run.font.italic = True
        run.font.color.rgb = Colors.DARK_GRAY

        # Executive table
        self.doc.add_paragraph()
        para = self.doc.add_paragraph()
        run = para.add_run("Identified Executives")
        run.font.size = Pt(14)
        run.font.bold = True

        exec_table = self.doc.add_table(rows=len(data.executives) + 1, cols=5)
        exec_table.style = 'Table Grid'

        # Headers
        headers = ["Name", "Title", "Exposure Level", "Start Date", "Email"]
        for i, header in enumerate(headers):
            cell = exec_table.rows[0].cells[i]
            cell.text = header
            cell.paragraphs[0].runs[0].bold = True
            set_cell_shading(cell, Colors.HEADER_ORANGE)
            cell.paragraphs[0].runs[0].font.color.rgb = Colors.WHITE

        # Data rows
        for i, exec in enumerate(data.executives):
            row = exec_table.rows[i + 1]
            row.cells[0].text = exec.name
            row.cells[1].text = exec.title
            row.cells[2].text = exec.exposure_level
            row.cells[3].text = exec.start_date or "N/A"
            row.cells[4].text = exec.email or "N/A"

            # Color code exposure level
            exposure_cell = row.cells[2]
            if exec.exposure_level == "HIGH":
                set_cell_shading(exposure_cell, Colors.HIGH_EXPOSURE)
                exposure_cell.paragraphs[0].runs[0].font.color.rgb = Colors.WHITE
            elif exec.exposure_level == "MEDIUM":
                set_cell_shading(exposure_cell, Colors.MEDIUM_EXPOSURE)
            else:
                set_cell_shading(exposure_cell, Colors.LOW_EXPOSURE)
                exposure_cell.paragraphs[0].runs[0].font.color.rgb = Colors.WHITE

        self.doc.add_page_break()

    def _add_executive_profile(self, exec: ExecutiveProfile, index: int):
        """Add detailed profile for a single executive"""
        # Header with exposure level
        para = self.doc.add_paragraph()
        run = para.add_run(f"5.{index + 1} {exec.name}")
        run.font.size = Pt(18)
        run.font.bold = True

        # Exposure level badge
        para = self.doc.add_paragraph()
        run = para.add_run(f"[{exec.exposure_level} EXPOSURE]")
        run.font.size = Pt(14)
        run.font.bold = True
        if exec.exposure_level == "HIGH":
            run.font.color.rgb = Colors.HIGH_EXPOSURE
        elif exec.exposure_level == "MEDIUM":
            run.font.color.rgb = Colors.MEDIUM_EXPOSURE
        else:
            run.font.color.rgb = Colors.LOW_EXPOSURE

        # Role
        para = self.doc.add_paragraph()
        run = para.add_run(exec.title)
        run.font.size = Pt(14)
        run.font.italic = True
        run.font.color.rgb = Colors.DARK_GRAY

        add_horizontal_line(para)

        # Professional Information
        para = self.doc.add_paragraph()
        run = para.add_run("Professional Information")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE

        if exec.current_role:
            self.doc.add_paragraph(f"Current Role: {exec.current_role}")

        if exec.previous_roles:
            para = self.doc.add_paragraph()
            run = para.add_run("Previous Roles:")
            run.bold = True
            for role in exec.previous_roles:
                self.doc.add_paragraph(f"• {role}", style='List Bullet')

        if exec.board_memberships:
            para = self.doc.add_paragraph()
            run = para.add_run("Board Memberships:")
            run.bold = True
            for board in exec.board_memberships:
                self.doc.add_paragraph(f"• {board}", style='List Bullet')

        # Education
        if exec.education:
            para = self.doc.add_paragraph()
            run = para.add_run("Education")
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = Colors.HEADER_ORANGE

            for edu in exec.education:
                self.doc.add_paragraph(f"• {edu.get('degree', '')} - {edu.get('institution', '')} ({edu.get('year', '')})")

        # Skills
        if exec.skills:
            para = self.doc.add_paragraph()
            run = para.add_run("Skills")
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = Colors.HEADER_ORANGE

            skills_text = ", ".join(exec.skills)
            self.doc.add_paragraph(skills_text)

        # Maltego placeholder
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("[MALTEGO GRAPH PLACEHOLDER]")
        run.font.size = Pt(12)
        run.font.italic = True
        run.font.color.rgb = Colors.DARK_GRAY

        # Online Accounts
        para = self.doc.add_paragraph()
        run = para.add_run("Online Accounts Discovered")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE

        if exec.online_accounts:
            # Create accounts table
            acc_table = self.doc.add_table(rows=len(exec.online_accounts) + 1, cols=4)
            acc_table.style = 'Table Grid'

            # Headers
            for i, header in enumerate(["Platform", "Registered", "Username/ID", "Profile URL"]):
                cell = acc_table.rows[0].cells[i]
                cell.text = header
                cell.paragraphs[0].runs[0].bold = True
                set_cell_shading(cell, Colors.BACKGROUND_GRAY)

            # Data
            for i, acc in enumerate(exec.online_accounts):
                row = acc_table.rows[i + 1]
                row.cells[0].text = acc.get('platform', 'N/A')
                row.cells[1].text = "✓" if acc.get('registered', False) else "✗"
                row.cells[2].text = acc.get('username', 'N/A')
                row.cells[3].text = acc.get('url', 'N/A')
        else:
            self.doc.add_paragraph("No significant online accounts discovered during assessment.")

        # Data Breaches
        para = self.doc.add_paragraph()
        run = para.add_run("Data Breaches (HaveIBeenPwned)")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE

        if exec.data_breaches:
            for breach in exec.data_breaches:
                # Breach box
                para = self.doc.add_paragraph()
                run = para.add_run(f"⚠ {breach.get('title', 'Unknown Breach')}")
                run.font.bold = True
                run.font.color.rgb = Colors.CRITICAL

                breach_info = f"""
Domain: {breach.get('domain', 'N/A')}
Breach Date: {breach.get('breach_date', 'N/A')}
Added: {breach.get('added_date', 'N/A')}
Pwn Count: {breach.get('pwn_count', 'N/A')}
Description: {breach.get('description', 'N/A')}
"""
                self.doc.add_paragraph(breach_info.strip())
        else:
            para = self.doc.add_paragraph()
            run = para.add_run("✓ No breaches found in HaveIBeenPwned database")
            run.font.color.rgb = Colors.SUCCESS

        # Personal Information Exposed
        if any([exec.addresses, exec.phones, exec.family_members, exec.vehicles]):
            para = self.doc.add_paragraph()
            run = para.add_run("⚠ Personal Information Exposed")
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = Colors.CRITICAL

            if exec.addresses:
                self.doc.add_paragraph(f"Addresses: {len(exec.addresses)} found")
            if exec.phones:
                self.doc.add_paragraph(f"Phone Numbers: {len(exec.phones)} found (partially redacted)")
            if exec.family_members:
                self.doc.add_paragraph(f"Family Members: {len(exec.family_members)} identified")
            if exec.vehicles:
                self.doc.add_paragraph(f"Vehicles: {len(exec.vehicles)} VINs found")
            if exec.photos_found > 0:
                self.doc.add_paragraph(f"Photos: {exec.photos_found} personal/family photos found")

        # Summary Box
        self.doc.add_paragraph()
        para = self.doc.add_paragraph()
        run = para.add_run("EXECUTIVE SUMMARY")
        run.font.size = Pt(12)
        run.font.bold = True

        summary_table = self.doc.add_table(rows=4, cols=2)
        summary_table.style = 'Table Grid'

        summary_data = [
            ("💼 Professional Roles", str(len(exec.previous_roles) + 1)),
            ("🌐 Online Presence", str(len(exec.online_accounts))),
            ("🔓 Data Breaches", str(len(exec.data_breaches))),
            ("⚠ Risk Level", exec.exposure_level)
        ]

        for i, (label, value) in enumerate(summary_data):
            row = summary_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            set_cell_shading(row.cells[0], Colors.BACKGROUND_GRAY)

        self.doc.add_page_break()

    def _add_analysis_section(self, data: AssessmentData):
        """Add analysis of data and information found"""
        para = self.doc.add_paragraph()
        run = para.add_run("ANALYSIS OF DATA AND INFORMATION FOUND")
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE
        add_horizontal_line(para)

        # Risk Assessment
        para = self.doc.add_paragraph()
        run = para.add_run("Overall Risk Assessment")
        run.font.size = Pt(14)
        run.font.bold = True

        risk_text = data.risk_assessment or """
Based on the comprehensive analysis conducted, the organization presents a MODERATE to HIGH
risk profile regarding executive digital exposure. The assessment identified multiple vectors
that could be exploited by sophisticated threat actors for social engineering, corporate
espionage, or targeted attacks against key personnel.
"""
        self.doc.add_paragraph(risk_text.strip())

        # Pattern Analysis
        if data.correlation_analysis:
            para = self.doc.add_paragraph()
            run = para.add_run("Pattern Analysis (AI-Enhanced)")
            run.font.size = Pt(14)
            run.font.bold = True

            self.doc.add_paragraph(data.correlation_analysis[:2000])

        # Recommendations
        para = self.doc.add_paragraph()
        run = para.add_run("Recommendations")
        run.font.size = Pt(14)
        run.font.bold = True

        recommendations = data.recommendations or [
            {"num": "1", "title": "Management and Training on Sensitive Information",
             "desc": "Implement regular security awareness training for all executives"},
            {"num": "2", "title": "Security in Operational Processes",
             "desc": "Review and enhance operational security procedures"},
            {"num": "3", "title": "Strong IT Leadership and Technological Innovation",
             "desc": "Invest in advanced security technologies and monitoring"},
            {"num": "4", "title": "Focus on Information Security",
             "desc": "Establish robust information security policies"},
            {"num": "5", "title": "Data Breach Management",
             "desc": "Develop incident response and breach notification procedures"},
            {"num": "6", "title": "Email and Personal Data Protection",
             "desc": "Implement email security and data protection measures"},
            {"num": "7", "title": "Executive Profiling and Monitoring",
             "desc": "Establish ongoing executive digital footprint monitoring"}
        ]

        for rec in recommendations:
            para = self.doc.add_paragraph()
            run = para.add_run(f"{rec['num']}. {rec['title']}")
            run.font.bold = True
            self.doc.add_paragraph(rec['desc'])

        self.doc.add_page_break()

    def _add_conclusions(self, data: AssessmentData):
        """Add final considerations and conclusions"""
        para = self.doc.add_paragraph()
        run = para.add_run("FINAL CONSIDERATIONS AND CONCLUSIONS")
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = Colors.HEADER_ORANGE
        add_horizontal_line(para)

        conclusion_text = f"""
This Executive Vulnerability Assessment of {data.company.name} has provided a comprehensive
analysis of the digital exposure and potential vulnerabilities associated with the organization's
C-level executives. The investigation followed rigorous OSINT methodologies aligned with
intelligence community standards (CIA/DEA/ROS/DIA frameworks).

KEY CONCLUSIONS:

1. EXPOSURE PROFILE
   The assessment identified varying levels of digital exposure among the executive team.
   Immediate attention is required for personnel classified with HIGH exposure levels.

2. BREACH HISTORY
   Multiple executives were found in known data breach databases, indicating historical
   credential exposure that may still present ongoing risks.

3. PERSONAL INFORMATION
   Significant amounts of personal and family information were discoverable through
   public sources, creating potential vectors for social engineering attacks.

4. STRATEGIC IMPORTANCE
   A multidimensional security strategy is essential, combining technical controls,
   policy enhancements, and ongoing awareness training.

RECOMMENDATIONS FOR IMMEDIATE ACTION:

• Conduct credential resets for all executives found in breach databases
• Implement executive protection awareness training
• Review and enhance privacy settings across social media platforms
• Establish ongoing digital footprint monitoring
• Develop incident response procedures specific to executive targeting

This assessment represents a point-in-time evaluation. The digital threat landscape
evolves continuously, and regular reassessment is strongly recommended.
"""
        self.doc.add_paragraph(conclusion_text.strip())

        # Signature block
        self.doc.add_paragraph()
        self.doc.add_paragraph()

        para = self.doc.add_paragraph()
        run = para.add_run("_" * 40)

        para = self.doc.add_paragraph()
        run = para.add_run(data.investigator.name)
        run.font.bold = True

        para = self.doc.add_paragraph()
        run = para.add_run(data.investigator.title)
        run.font.italic = True

        para = self.doc.add_paragraph()
        run = para.add_run(f"Date: {datetime.now().strftime('%d/%m/%Y')}")

        # Classification footer
        self.doc.add_paragraph()
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run("CLASSIFICAZIONE: RISERVATO")
        run.font.bold = True
        run.font.color.rgb = Colors.CRITICAL

    def _get_exposure_label(self, level: str) -> str:
        """Get exposure level label with indicator"""
        if level == "HIGH":
            return "🔴 HIGH EXPOSURE"
        elif level == "MEDIUM":
            return "🟡 MEDIUM EXPOSURE"
        else:
            return "🟢 LOW EXPOSURE"

    def generate(self, data: AssessmentData, output_filename: str = None) -> str:
        """Generate the complete report"""
        self._initialize_document()

        # Build report sections
        self._add_cover_page(data)
        self._add_table_of_contents(data)
        self._add_executive_summary(data)
        self._add_investigator_profile(data)
        self._add_company_info(data)
        self._add_clevel_identification(data)

        # Add individual executive profiles
        for i, exec in enumerate(data.executives):
            self._add_executive_profile(exec, i)

        self._add_analysis_section(data)
        self._add_conclusions(data)

        # Save document
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Executive_Vulnerability_Assessment_{timestamp}.docx"

        output_path = os.path.join(self.output_dir, output_filename)
        self.doc.save(output_path)

        return output_path


# =============================================================================
# INTEGRATION WITH FIDELINVESTIGATOR AI
# =============================================================================

def create_assessment_from_osint_data(
    extracted_data: Dict,
    analysis_data: Dict,
    psychological_profile: Dict,
    security_assessment: Dict,
    company_name: str = "Target Company"
) -> AssessmentData:
    """
    Create AssessmentData from FidelinvestigatorAI output
    """
    # Create company info
    company = CompanyInfo(
        name=company_name,
        description="Company analyzed through OSINT investigation",
        email_format="Identified through email pattern analysis"
    )

    # Create investigator profile
    investigator = InvestigatorProfile(
        name="FidelinvestigatorAI",
        title="Automated OSINT Intelligence System",
        background="""Advanced AI-powered OSINT investigation system integrating
        Perplexity (real-time search), OpenAI GPT-4 (correlation analysis),
        and Anthropic Claude (psychological profiling) for comprehensive
        executive vulnerability assessments.""",
        certifications=[
            "AI-Enhanced OSINT Analysis",
            "Intelligence Community Standards (ICD 203)",
            "FBI BAU Behavioral Framework Integration",
            "CIA Analytic Tradecraft Compliance"
        ],
        tools=[
            "Perplexity AI - Real-time OSINT verification",
            "OpenAI GPT-4 - Pattern recognition and correlation",
            "Anthropic Claude - Psychological profiling",
            "Custom HTML/Data parsers",
            "Breach database integration"
        ]
    )

    # Create executive profiles from extracted data
    executives = []

    # Process emails as potential executives
    emails = extracted_data.get('emails', [])
    usernames = extracted_data.get('usernames', [])
    social_profiles = extracted_data.get('social_profiles', [])
    passwords = extracted_data.get('passwords', [])
    breaches = extracted_data.get('breaches', [])

    # Determine exposure level based on data
    exposure_level = "LOW"
    if len(passwords) > 0:
        exposure_level = "HIGH"
    elif len(breaches) > 2:
        exposure_level = "HIGH"
    elif len(breaches) > 0 or len(social_profiles) > 5:
        exposure_level = "MEDIUM"

    # Create at least one executive profile
    if emails:
        for i, email in enumerate(emails[:5]):  # Max 5 executives
            exec_profile = ExecutiveProfile(
                name=f"Executive {i+1}" if not usernames else usernames[i] if i < len(usernames) else f"Executive {i+1}",
                title="C-Level Executive",
                exposure_level=exposure_level,
                email=email,
                online_accounts=[
                    {"platform": p.get('platform', 'Unknown'),
                     "registered": True,
                     "username": p.get('username', ''),
                     "url": p.get('url', '')}
                    for p in social_profiles
                ],
                data_breaches=[
                    {"title": b.get('source', 'Unknown Breach'),
                     "domain": b.get('domain', 'N/A'),
                     "breach_date": b.get('date', 'N/A'),
                     "description": "Breach detected during OSINT analysis"}
                    for b in breaches
                ]
            )
            executives.append(exec_profile)

    # If no emails, create placeholder
    if not executives:
        executives.append(ExecutiveProfile(
            name="Target Subject",
            title="Subject of Investigation",
            exposure_level=exposure_level
        ))

    # Create assessment
    assessment = AssessmentData(
        project_name=f"OSINT Investigation - {company_name}",
        company=company,
        investigator=investigator,
        executives=executives,
        start_date=datetime.now().strftime("%d/%m/%Y"),
        end_date=datetime.now().strftime("%d/%m/%Y"),
        correlation_analysis=analysis_data.get('correlation_result', ''),
        threat_assessment=security_assessment.get('risk_level', ''),
        risk_assessment=f"""
Security Grade: {security_assessment.get('security_grade', 'N/A')}
Exposure Level: {security_assessment.get('exposure_level', 'N/A')}
Security Score: {security_assessment.get('security_score', 'N/A')}/100
Vulnerabilities: {len(security_assessment.get('vulnerabilities', []))}
Active Threats: {len(security_assessment.get('threats', []))}
"""
    )

    # Add psychological profiles
    if psychological_profile:
        assessment.psychological_profiles = {
            "primary": psychological_profile.get('ai_profile', '')
        }

    return assessment


# =============================================================================
# MAIN / CLI
# =============================================================================

def main():
    """Main entry point for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Executive Vulnerability Assessment Report"
    )
    parser.add_argument(
        '-c', '--company',
        default="Target Company",
        help="Company name"
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help="Output directory"
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help="Generate demo report with sample data"
    )

    args = parser.parse_args()

    if args.demo:
        # Create demo data
        company = CompanyInfo(
            name="ACME Corporation",
            description="A leading technology company specializing in innovative solutions",
            sector="Technology",
            headquarters="New York, NY",
            employees="500-1000",
            revenue="$50M - $100M"
        )

        investigator = InvestigatorProfile(
            name="FidelinvestigatorAI",
            title="Senior OSINT Analyst",
            certifications=["CEH", "OSCP", "GIAC"],
            tools=["Maltego", "Shodan", "Perplexity AI", "OpenAI GPT-4", "Claude"]
        )

        executives = [
            ExecutiveProfile(
                name="John Smith",
                title="Chief Executive Officer",
                exposure_level="HIGH",
                email="j.smith@acme.com",
                online_accounts=[
                    {"platform": "LinkedIn", "registered": True, "username": "johnsmith", "url": "https://linkedin.com/in/johnsmith"},
                    {"platform": "Twitter", "registered": True, "username": "@jsmith", "url": "https://twitter.com/jsmith"}
                ],
                data_breaches=[
                    {"title": "LinkedIn 2021", "domain": "linkedin.com", "breach_date": "2021-06-22", "pwn_count": "700M"}
                ]
            ),
            ExecutiveProfile(
                name="Jane Doe",
                title="Chief Technology Officer",
                exposure_level="MEDIUM",
                email="j.doe@acme.com"
            )
        ]

        data = AssessmentData(
            project_name="ACME Corporation Executive Assessment",
            company=company,
            investigator=investigator,
            executives=executives,
            start_date="01/12/2024",
            end_date="03/12/2024"
        )

        generator = ExecutiveReportGenerator(output_dir=args.output or os.getcwd())
        output_path = generator.generate(data)

        print(f"[✓] Demo report generated: {output_path}")
    else:
        print("Use --demo to generate a sample report, or integrate with FidelinvestigatorAI")


if __name__ == "__main__":
    main()
