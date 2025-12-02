#!/usr/bin/env python3
"""
FidelinvestigatorAI - Esempio di Utilizzo
==========================================

Questo script dimostra come utilizzare FidelinvestigatorAI
per analizzare un report OSINT e generare un report investigativo PDF.
"""

import os
import sys

# Aggiungi path del modulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fidelinvestigator import FidelinvestigatorAI


def main():
    """Esempio di utilizzo base"""

    print("=" * 60)
    print("  FidelinvestigatorAI - Esempio di Utilizzo")
    print("=" * 60)

    # Verifica argomenti
    if len(sys.argv) < 2:
        print("""
Utilizzo:
    python example_usage.py <file_html> [--logo <path_logo>]

Esempio:
    python example_usage.py report_osint.html
    python example_usage.py report_osint.html --logo logo.png
        """)
        return

    html_file = sys.argv[1]
    logo_path = None

    # Cerca parametro logo
    if "--logo" in sys.argv:
        logo_idx = sys.argv.index("--logo")
        if logo_idx + 1 < len(sys.argv):
            logo_path = sys.argv[logo_idx + 1]

    # Verifica file esiste
    if not os.path.exists(html_file):
        print(f"[ERRORE] File non trovato: {html_file}")
        return

    # Inizializza l'agente
    agent = FidelinvestigatorAI(
        output_dir="./reports",
        logo_path=logo_path,
        verbose=True
    )

    # Esegui investigazione
    try:
        result = agent.investigate_from_file(html_file)

        print("\n" + "=" * 60)
        print("  INVESTIGAZIONE COMPLETATA CON SUCCESSO!")
        print("=" * 60)

        print(f"""
    Target:              {result.target_name}
    Report PDF:          {result.pdf_report_path}
    Security Grade:      {result.summary['security']['grade']}
    Exposure Level:      {result.summary['security']['exposure_level']}
        """)

    except Exception as e:
        print(f"\n[ERRORE] {str(e)}")
        raise


def demo_with_sample_data():
    """Demo con dati di esempio"""

    # HTML di esempio (simulazione report OSINT)
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>OSINT Report - Mario Rossi</title></head>
    <body>
        <div class="profile-info">
            <h1 class="name">Mario Rossi</h1>
            <table>
                <tr><td>Nome Completo</td><td>Mario Rossi</td></tr>
                <tr><td>Data di Nascita</td><td>15/03/1985</td></tr>
                <tr><td>Professione</td><td>Software Developer</td></tr>
                <tr><td>Nazionalità</td><td>Italiana</td></tr>
            </table>
        </div>

        <div class="contact-info">
            <h2>Contatti</h2>
            <p>Email: mario.rossi@gmail.com</p>
            <p>Email: m.rossi@outlook.com</p>
            <p>Telefono: +39 333 1234567</p>
        </div>

        <div class="social-media">
            <h2>Social Media</h2>
            <a href="https://twitter.com/mariorossi">Twitter: @mariorossi</a>
            <a href="https://www.linkedin.com/in/mariorossi">LinkedIn: mariorossi</a>
            <a href="https://github.com/mariorossi">GitHub: mariorossi</a>
            <a href="https://www.instagram.com/mario_rossi85">Instagram: mario_rossi85</a>
            <a href="https://www.facebook.com/mario.rossi.85">Facebook</a>
        </div>

        <div class="usernames">
            <h2>Username noti</h2>
            <ul>
                <li>mariorossi</li>
                <li>mario_rossi85</li>
                <li>mrossi</li>
                <li>mario.rossi</li>
            </ul>
        </div>

        <div class="breach-data">
            <h2>Data Breach</h2>
            <table>
                <tr><th>Breach</th><th>Data</th><th>Dati Esposti</th><th>Password</th></tr>
                <tr><td>LinkedIn 2021</td><td>2021-04-06</td><td>email, password</td><td>MarioR85!</td></tr>
                <tr><td>Adobe 2013</td><td>2013-10-04</td><td>email, password hash</td><td></td></tr>
                <tr><td>Collection #1</td><td>2019-01-17</td><td>email, password</td><td>rossi1985</td></tr>
            </table>
        </div>

        <div class="location">
            <h2>Località</h2>
            <p>Location: Roma, Italia</p>
            <p>Lives in: Milano</p>
        </div>
    </body>
    </html>
    """

    print("=" * 60)
    print("  FidelinvestigatorAI - Demo con Dati di Esempio")
    print("=" * 60)

    # Inizializza l'agente
    agent = FidelinvestigatorAI(
        output_dir="./reports",
        verbose=True
    )

    # Esegui investigazione
    result = agent.investigate(sample_html, "Demo_Report.pdf")

    print("\n[OK] Demo completata!")
    print(f"Report generato: {result.pdf_report_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_with_sample_data()
    else:
        main()
