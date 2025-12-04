#!/usr/bin/env python3
"""
Script per generare un report di esempio con dati fittizi
"""

import os
import sys

# Aggiungi il path del progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# HTML fittizio con dati di esempio
FAKE_HTML = """
<!DOCTYPE html>
<html>
<head><title>OSINT Report - Mario Rossi</title></head>
<body>
<h1>OSINT Investigation Report</h1>
<h2>Target: Mario Rossi</h2>

<h3>Contact Information</h3>
<p>Email: mario.rossi@gmail.com</p>
<p>Email: m.rossi85@yahoo.it</p>
<p>Email: mario.rossi@azienda-esempio.it</p>
<p>Phone: +39 333 1234567</p>
<p>Phone: +39 02 9876543</p>

<h3>Social Media Profiles</h3>
<ul>
    <li><a href="https://www.facebook.com/mario.rossi.85">Facebook Profile</a></li>
    <li><a href="https://www.instagram.com/mario_rossi_photo">Instagram @mario_rossi_photo</a></li>
    <li><a href="https://www.linkedin.com/in/mario-rossi-milano">LinkedIn Professional</a></li>
    <li><a href="https://twitter.com/mrossi85">Twitter @mrossi85</a></li>
    <li><a href="https://github.com/mrossi-dev">GitHub @mrossi-dev</a></li>
</ul>

<h3>Usernames Found</h3>
<p>@mario_rossi_photo</p>
<p>@mrossi85</p>
<p>@mrossi-dev</p>
<p>@mario.rossi.gamer</p>

<h3>Data Breach Information</h3>
<table border="1">
    <tr><th>Source</th><th>Date</th><th>Data Exposed</th></tr>
    <tr><td>LinkedIn Breach 2021</td><td>2021-06-22</td><td>Email, Name, Phone</td></tr>
    <tr><td>Adobe Hack</td><td>2013-10-04</td><td>Email, Password Hash</td></tr>
    <tr><td>Collection #1 Leak</td><td>2019-01-17</td><td>Email, Password</td></tr>
    <tr><td>Dropbox Breach</td><td>2012-07-01</td><td>Email, Password Hash</td></tr>
</table>

<h3>Exposed Credentials</h3>
<p>Password found: Mario85!</p>
<p>Password found: Rossi2023</p>
<p>Password found: milan1985</p>

<h3>IP Addresses</h3>
<p>Last known IP: 151.38.124.89</p>
<p>VPN detected: 185.220.101.34</p>

<h3>Locations</h3>
<p>Location: Milano, Italia</p>
<p>Location: Roma, Italia</p>
<p>City: Bergamo</p>
<p>Country: Italy</p>

<h3>Additional Information</h3>
<p>Name: Mario Rossi</p>
<p>Full Name: Mario Giuseppe Rossi</p>
<p>Age: 38</p>
<p>Occupation: Software Developer</p>
<p>Company: TechCorp S.r.l.</p>

</body>
</html>
"""

def main():
    print("=" * 70)
    print("GENERAZIONE REPORT DI ESEMPIO - FidelinvestigatorAI")
    print("=" * 70)
    print("\nQuesto script genera un report completo con dati FITTIZI")
    print("per dimostrare le funzionalità del sistema.\n")

    # Crea directory output se non esiste
    output_dir = os.path.join(os.path.dirname(__file__), "example_reports")
    os.makedirs(output_dir, exist_ok=True)

    # Salva HTML temporaneo
    html_path = os.path.join(output_dir, "fake_osint_data.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(FAKE_HTML)

    print(f"[*] HTML di esempio salvato in: {html_path}")

    # Importa il sistema
    try:
        from fidelinvestigator_ai_enhanced import FidelinvestigatorAI, Config

        # Configura (senza API keys per test base)
        config = Config()
        config.OUTPUT_DIR = output_dir
        config.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        config.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        config.PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

        # Crea agente
        agent = FidelinvestigatorAI(config)

        # Esegui investigazione
        print("\n[*] Avvio investigazione con dati fittizi...\n")
        report_path = agent.investigate(html_path, output_dir)

        print("\n" + "=" * 70)
        print("REPORT GENERATI CON SUCCESSO!")
        print("=" * 70)
        print(f"\nDirectory output: {output_dir}")
        print("\nFile generati:")
        for f in os.listdir(output_dir):
            filepath = os.path.join(output_dir, f)
            size = os.path.getsize(filepath)
            print(f"  - {f} ({size:,} bytes)")

    except ImportError as e:
        print(f"\n[!] Errore import: {e}")
        print("[!] Eseguendo generazione base senza AI...")

        # Fallback: genera solo con parser base
        generate_basic_report(html_path, output_dir)

    except Exception as e:
        print(f"\n[!] Errore durante la generazione: {e}")
        import traceback
        traceback.print_exc()


def generate_basic_report(html_path: str, output_dir: str):
    """Genera report base senza dipendenze AI"""
    from datetime import datetime

    print("\n[*] Generazione report base...")

    # Parse HTML manualmente
    with open(html_path, 'r') as f:
        html = f.read()

    import re

    # Estrai dati
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
    phones = re.findall(r'\+?[0-9]{1,3}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{4,10}', html)
    usernames = re.findall(r'@([a-zA-Z0-9_.-]{3,30})', html)

    # Crea report testuale
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"basic_report_{timestamp}.txt")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("REPORT INVESTIGATIVO OSINT - ESEMPIO\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"Target: Mario Rossi (DATI FITTIZI)\n\n")

        f.write("-" * 40 + "\n")
        f.write("EMAIL IDENTIFICATE\n")
        f.write("-" * 40 + "\n")
        for email in set(emails):
            f.write(f"  • {email}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("NUMERI DI TELEFONO\n")
        f.write("-" * 40 + "\n")
        for phone in set(phones):
            f.write(f"  • {phone}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("USERNAME\n")
        f.write("-" * 40 + "\n")
        for username in set(usernames):
            f.write(f"  • @{username}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("NOTA: Questo è un report base senza analisi AI.\n")
        f.write("Configurare le API keys per report completi.\n")
        f.write("=" * 70 + "\n")

    print(f"\n[✓] Report base generato: {report_path}")


if __name__ == "__main__":
    main()
