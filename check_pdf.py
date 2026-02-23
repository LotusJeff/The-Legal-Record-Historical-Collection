#!/usr/bin/env python3
"""
PDF Monitor Script
Checks if a PDF has changed since the last run.
If changed, saves it and emails it to a mailing list via Mailjet.
"""

import os
import hashlib
import requests
import json
import base64
from datetime import datetime
from pathlib import Path

# ── Configuration (all pulled from environment variables / GitHub Secrets) ──
PDF_URL        = os.environ["PDF_URL"]
MAILJET_API_KEY    = os.environ["MAILJET_API_KEY"]
MAILJET_SECRET_KEY = os.environ["MAILJET_SECRET_KEY"]
SENDER_EMAIL   = os.environ["SENDER_EMAIL"]       # must be verified in Mailjet
SENDER_NAME    = os.environ.get("SENDER_NAME", "PDF Monitor")
MAILING_LIST   = os.environ["MAILING_LIST"]       # comma-separated emails

HASH_FILE  = "last_hash.txt"
PDF_DIR    = "pdfs"

def download_pdf(url: str) -> bytes:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.content

def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_last_hash() -> str | None:
    p = Path(HASH_FILE)
    if p.exists():
        return p.read_text().strip() or None
    return None

def save_hash(hash_str: str):
    Path(HASH_FILE).write_text(hash_str)

def save_pdf(data: bytes, filename: str):
    Path(PDF_DIR).mkdir(exist_ok=True)
    Path(f"{PDF_DIR}/{filename}").write_bytes(data)
    print(f"Saved PDF: {PDF_DIR}/{filename}")

def send_email(pdf_data: bytes, filename: str):
    recipients = [
        {"Email": email.strip()}
        for email in MAILING_LIST.split(",")
        if email.strip()
    ]

    pdf_b64 = base64.b64encode(pdf_data).decode()
    today   = datetime.now().strftime("%B %d, %Y")

    payload = {
        "Messages": [
            {
                "From": {"Email": SENDER_EMAIL, "Name": SENDER_NAME},
                "To": recipients,
                "Subject": f"Updated PDF Available – {today}",
                "TextPart": (
                    f"Hello,\n\n"
                    f"The monitored PDF has been updated as of {today}.\n"
                    f"The latest version is attached.\n\n"
                    f"Source: {PDF_URL}\n\n"
                    f"— PDF Monitor"
                ),
                "HTMLPart": (
                    f"<p>Hello,</p>"
                    f"<p>The monitored PDF has been updated as of <strong>{today}</strong>.</p>"
                    f"<p>The latest version is attached to this email.</p>"
                    f"<p>Source: <a href='{PDF_URL}'>{PDF_URL}</a></p>"
                    f"<p>— PDF Monitor</p>"
                ),
                "Attachments": [
                    {
                        "ContentType": "application/pdf",
                        "Filename": filename,
                        "Base64Content": pdf_b64,
                    }
                ],
            }
        ]
    }

    resp = requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY),
        json=payload,
        timeout=60,
    )

    if resp.status_code == 200:
        data = resp.json()
        status = data["Messages"][0]["Status"]
        print(f"Email send status: {status}")
        if status != "success":
            print(f"Mailjet response: {json.dumps(data, indent=2)}")
    else:
        print(f"Mailjet error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

def main():
    print(f"[{datetime.now().isoformat()}] Checking PDF: {PDF_URL}")

    # Download
    try:
        pdf_data = download_pdf(PDF_URL)
    except Exception as e:
        print(f"ERROR: Failed to download PDF: {e}")
        raise

    current_hash = compute_hash(pdf_data)
    last_hash    = load_last_hash()

    print(f"Current hash : {current_hash}")
    print(f"Previous hash: {last_hash or 'none (first run)'}")

    if current_hash == last_hash:
        print("PDF is unchanged. Nothing to do.")
        return

    print("PDF has changed! Saving and sending email...")

    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename  = f"LR-CITIES_{timestamp}.pdf"

    save_pdf(pdf_data, filename)
    save_hash(current_hash)

    try:
        send_email(pdf_data, filename)
        print("Email sent successfully.")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        raise

if __name__ == "__main__":
    main()
