#!/usr/bin/env python3
"""
Test script per TheShepherdAI
"""

import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Dati di test simulati da vari tool OSINT
SAMPLE_SHERLOCK_OUTPUT = {
    "Facebook": {"exists": True, "url": "https://www.facebook.com/mario.rossi.85"},
    "Instagram": {"exists": True, "url": "https://www.instagram.com/mario_rossi_photo"},
    "Twitter": {"exists": True, "url": "https://twitter.com/mrossi85"},
    "GitHub": {"exists": True, "url": "https://github.com/mrossi-dev"},
    "LinkedIn": {"exists": False}
}

SAMPLE_HOLEHE_OUTPUT = {
    "amazon.com": {"exists": True, "email": "mario.rossi@gmail.com"},
    "spotify.com": {"exists": True, "email": "mario.rossi@gmail.com"},
    "netflix.com": {"exists": False},
    "twitter.com": {"exists": True, "email": "mario.rossi@gmail.com"},
    "instagram.com": {"exists": True, "email": "mario.rossi@gmail.com"}
}

SAMPLE_HIBP_OUTPUT = {
    "breaches": [
        {
            "Name": "LinkedIn",
            "BreachDate": "2021-06-22",
            "DataClasses": ["Email addresses", "Names", "Phone numbers"],
            "Description": "LinkedIn data breach",
            "IsVerified": True
        },
        {
            "Name": "Adobe",
            "BreachDate": "2013-10-04",
            "DataClasses": ["Email addresses", "Password hints", "Passwords"],
            "IsVerified": True
        },
        {
            "Name": "Collection1",
            "BreachDate": "2019-01-17",
            "DataClasses": ["Email addresses", "Passwords"],
            "IsVerified": True
        }
    ]
}

SAMPLE_DEHASHED_OUTPUT = {
    "entries": [
        {
            "email": "mario.rossi@gmail.com",
            "username": "mrossi85",
            "password": "Mario85!",
            "database_name": "linkedin_2021"
        },
        {
            "email": "m.rossi85@yahoo.it",
            "password": "Rossi2023",
            "database_name": "collection1"
        },
        {
            "email": "mario.rossi@gmail.com",
            "password": "milan1985",
            "database_name": "adobe_2013",
            "ip_address": "151.38.124.89"
        }
    ]
}

SAMPLE_THEHARVESTER_OUTPUT = {
    "emails": [
        "mario.rossi@azienda-esempio.it",
        "m.rossi@techcorp.it"
    ],
    "hosts": [
        {"domain": "azienda-esempio.it", "ip": "93.184.216.34"},
        {"domain": "techcorp.it"}
    ],
    "ips": ["93.184.216.34", "151.38.124.89"]
}

SAMPLE_PHONEINFOGA_OUTPUT = {
    "number": "+39 333 1234567",
    "country": "Italy",
    "carrier": "TIM",
    "line_type": "mobile",
    "social_media": {
        "WhatsApp": True,
        "Telegram": False
    }
}


def main():
    print("=" * 70)
    print("TEST THE SHEPHERD AI")
    print("=" * 70)

    # Crea directory temporanea con i file JSON
    with tempfile.TemporaryDirectory() as tmpdir:
        # Salva file JSON di test
        json_files = {
            "sherlock_output.json": SAMPLE_SHERLOCK_OUTPUT,
            "holehe_output.json": SAMPLE_HOLEHE_OUTPUT,
            "hibp_output.json": SAMPLE_HIBP_OUTPUT,
            "dehashed_output.json": SAMPLE_DEHASHED_OUTPUT,
            "theharvester_output.json": SAMPLE_THEHARVESTER_OUTPUT,
            "phoneinfoga_output.json": SAMPLE_PHONEINFOGA_OUTPUT
        }

        for filename, data in json_files.items():
            filepath = os.path.join(tmpdir, filename)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[+] Created: {filename}")

        # Crea directory output
        output_dir = os.path.join(os.path.dirname(__file__), "test_reports")
        os.makedirs(output_dir, exist_ok=True)

        print(f"\n[*] Input directory: {tmpdir}")
        print(f"[*] Output directory: {output_dir}")

        # Esegui analisi
        from theshepherd_ai import run_shepherd_analysis

        try:
            report_paths = run_shepherd_analysis(
                workflow_path=tmpdir,
                target_name="Mario Rossi",
                output_dir=output_dir
            )

            print("\n" + "=" * 70)
            print("TEST COMPLETATO CON SUCCESSO!")
            print("=" * 70)
            print("\nReport generati:")
            for fmt, path in report_paths.items():
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"  {fmt.upper():5}: {os.path.basename(path)} ({size:,} bytes)")

            return True

        except Exception as e:
            print(f"\n[!] ERRORE: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
