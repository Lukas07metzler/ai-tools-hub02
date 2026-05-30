# SmartAI Picks — Setup Guide
**One-time setup, ~45 minutes. After this it runs itself.**

---

## Step 1: Create GitHub Repository (5 min)

1. Go to https://github.com/new
2. Repository name: `ai-tools-hub`
3. Set to **Public** (required for free GitHub Pages)
4. Click "Create repository"

Then push this project:
```bash
cd C:\Users\Lukas\ai-tools-hub
git init
git add .
git commit -m "initial setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-tools-hub.git
git push -u origin main
```

---

## Step 2: Enable GitHub Pages (2 min)

1. Go to your repo → **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Save

Add this workflow file to enable automatic Jekyll builds:
`.github/workflows/deploy.yml` — GitHub auto-creates this when you select "GitHub Actions" source.
Or manually: https://jekyllrb.com/docs/continuous-integration/github-actions/

Your site will be live at: `https://YOUR_USERNAME.github.io/ai-tools-hub`

**Update `_config.yml`:**
- Change `url` to `https://YOUR_USERNAME.github.io`
- Change `baseurl` to `/ai-tools-hub`

---

## Step 3: Get Groq API Key (5 min — FREE)

1. Go to https://console.groq.com
2. Sign up with your Google account
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)

**Add to GitHub:**
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GROQ_API_KEY`
4. Value: paste your key
5. Save

**Free tier:** 14,400 requests/day, 6,000 tokens/min — more than enough.

---

## Step 4: Sign Up for Affiliate Programs (30 min)

Sign up for these (all free, instant or 1-3 day approval):

| Program | Commission | Signup Link |
|---------|-----------|-------------|
| Jasper AI | 30% recurring | https://www.jasper.ai/affiliates |
| Writesonic | 30% recurring | https://writesonic.com/affiliate |
| Copy.ai | 45% first payment | https://www.copy.ai/affiliate |
| Grammarly | $20/conversion | https://www.grammarly.com/affiliate |
| Surfer SEO | 25% recurring | https://surferseo.com/affiliate/ |
| Canva | Up to 80% | https://www.canva.com/affiliates/ |
| Rytr | 30% recurring | https://rytr.me/affiliate |

After approval, **replace `YOUR_AFFILIATE_ID` in `scripts/affiliate_links.json`** with your actual affiliate link for each program.

---

## Step 5: Test the Content Pipeline (5 min)

Run manually in GitHub:
1. Go to your repo → **Actions**
2. Click **"Generate Blog Post"**
3. Click **"Run workflow"** → **Run**
4. Wait ~2 minutes
5. Check `_posts/` for the new file

If it works, you'll see a new post committed automatically.

---

## Step 6: (Optional) Custom Domain

Buy a cheap domain (~€10/year) at Namecheap or Porkbun.
Add a `CNAME` file to the repo root with just your domain:
```
smartaipicks.com
```
Then configure DNS to point to GitHub Pages.

---

## What Runs Automatically After Setup

| Schedule | What Happens |
|----------|-------------|
| Mon, Wed, Fri 8am UTC | New blog post generated and published |
| Every Sunday 7am UTC | Strategy agent adds 20 new keywords |

---

## Realistic Timeline

- **Month 1-2:** Site indexed by Google, 0-10 visitors/day
- **Month 3-4:** 50-200 visitors/day, first clicks
- **Month 6:** €20-100/month if affiliate links are set up
- **Month 12+:** €100-500+/month (scales with posts + backlinks)

The more posts = the more chances to rank. By month 6 you'll have 70+ articles.

---

## Steuern (Deutschland/Österreich)

### Wann musst du es melden?

**Gute Nachricht für den Anfang:**
- Bis **ca. 256€/Jahr** aus Nebentätigkeit: sehr grauer Bereich, viele melden es nicht
- Ab **ersten nennenswerten Einnahmen** (>500€/Jahr): du solltest es korrekt angehen

### Was du tun musst (Deutschland):

1. **Gewerbe anmelden** — sobald du systematisch Geld verdienst (nicht nur einmalig)
   - Beim Gewerbeamt deiner Stadt
   - Kostet ~20-50€
   - Gewerbesteuerpflicht erst ab **24.500€ Gewinn** — darunter zahlst du keine Gewerbesteuer
   - Das Finanzamt wird automatisch informiert

2. **Kleinunternehmerregelung wählen (§19 UStG)**
   - Bis **25.000€ Jahresumsatz**: keine Umsatzsteuer nötig
   - Viel einfachere Buchhaltung
   - Empfehlenswert für den Start

3. **Einkommensteuer**
   - Grundfreibetrag 2024: **11.784€** (bis hierhin keine Einkommensteuer)
   - Affiliate-Einnahmen werden zu deinem Gesamteinkommen addiert
   - Als Schüler/Student mit wenig anderem Einkommen: langer Weg bis zur Steuerpflicht

4. **Buchhaltung**
   - Reicht: Excel-Tabelle mit Einnahmen und Ausgaben
   - Tools wie Sorted³ oder FastBill erleichtern es später

### Österreich:
- Ähnlich, aber Grenze für Kleinunternehmer: **42.000€**
- Jungunternehmer-Förderung der WKO nutzbar
- SVS-Pflichtversicherung erst ab ca. 6.453€ Jahresgewinn

### Wichtig:
**Für deine spezifische Situation (Alter, anderes Einkommen, Bundesland) wende dich an einen Steuerberater.**
Erste Beratung bei Steuerkanzleien oft kostenlos oder sehr günstig.
