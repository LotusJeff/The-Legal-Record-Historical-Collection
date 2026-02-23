# PDF Monitor

Automatically checks a PDF URL daily. If the file has changed, it saves a dated copy and emails it to your mailing list via Mailjet.

---

## How It Works

1. GitHub Actions runs the script every morning at 8:00 AM UTC
2. The script downloads the PDF and computes a SHA-256 hash
3. It compares the hash to the previous day's hash (stored in `last_hash.txt`)
4. If the hash is different → saves the PDF to the `pdfs/` folder, commits it, and emails all recipients
5. If unchanged → does nothing

---

## Repository Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── pdf-monitor.yml   ← GitHub Actions workflow
├── pdfs/                     ← Downloaded PDFs saved here (auto-created)
├── check_pdf.py              ← The monitor script
├── last_hash.txt             ← Hash of the last seen PDF (auto-created)
└── README.md
```

---

## Setup Instructions

### Step 1 — Create a new GitHub repository

1. Go to https://github.com/new
2. Name it something like `pdf-monitor`
3. Make it **Private** (recommended — it will store your mailing list and PDFs)
4. Click **Create repository**

### Step 2 — Add the files to your repo

Upload these three files to the root of your repository:
- `check_pdf.py`
- `README.md`

Then create this folder path and upload the workflow file:
- `.github/workflows/pdf-monitor.yml`

**Easiest way:** Use the GitHub web UI → click "Add file" → "Create new file" → paste the contents.

For the workflow, type `.github/workflows/pdf-monitor.yml` as the filename (GitHub will create the folders automatically).

### Step 3 — Set up Mailjet

1. Sign up at https://www.mailjet.com (free tier: 200 emails/day, 6,000/month)
2. Go to **Account Settings → API Keys**
3. Note your **API Key** and **Secret Key**
4. Go to **Senders & Domains → Sender Addresses** and verify the email address you'll send FROM

### Step 4 — Configure GitHub Secrets & Variables

In your GitHub repo, go to **Settings → Secrets and variables → Actions**.

#### Secrets (sensitive — hidden after entry)

| Name | Value |
|------|-------|
| `MAILJET_API_KEY` | Your Mailjet API Key |
| `MAILJET_SECRET_KEY` | Your Mailjet Secret Key |
| `MAILING_LIST` | Comma-separated list of recipient emails, e.g. `alice@example.com,bob@example.com` |

#### Variables (non-sensitive — visible)

| Name | Value |
|------|-------|
| `PDF_URL` | `https://thelegalrecord.net/LR-CITIES.pdf` |
| `SENDER_EMAIL` | The verified email you'll send from |
| `SENDER_NAME` | Display name, e.g. `Legal Record Monitor` |

### Step 5 — Test it manually

1. Go to your repo on GitHub
2. Click the **Actions** tab
3. Click **Daily PDF Monitor** in the left sidebar
4. Click **Run workflow** → **Run workflow**
5. Watch the run — it will download the PDF, save it, and email your list (since there's no previous hash yet, it treats the first run as a change)

### Step 6 — Adjust the schedule (optional)

In `pdf-monitor.yml`, the line:
```yaml
- cron: "0 8 * * *"
```
means 8:00 AM UTC daily. Convert to your local time zone and adjust as needed. Use https://crontab.guru to build a custom schedule.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Email not received | Check Mailjet dashboard → Sent messages. Check your spam folder. Make sure sender email is verified. |
| Workflow not running | Check the Actions tab for error logs. Make sure the workflow file is in exactly `.github/workflows/`. |
| "Permission denied" on git push | Make sure the workflow has `permissions: contents: write` (already included). |
| PDF download fails | The source URL may be temporarily down. The workflow will show an error in the Actions log. |

---

## Cost

| Service | Cost |
|---------|------|
| GitHub Actions | Free (well under the 2,000 min/month free limit) |
| Mailjet | Free up to 200 emails/day, 6,000/month |
| Storage | PDFs stored in repo (~1.2MB each). GitHub's free limit is 1GB. At 1.2MB/day that's ~2.3 years of storage. |
| **Total** | **$0/month** |
