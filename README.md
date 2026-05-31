# 🏥 DocStribe · Patient Intelligence Dashboard

> **CXO-level patient analytics powered by Claude AI** — built as a hiring assignment for Docstribe.  
> A single-file, zero-build React application that transforms a raw Excel patient dataset into a fully interactive intelligence dashboard with an embedded Claude Sonnet AI chatbot and auto-generated executive briefing.

---

## 🔗 Live Demo

**[https://docstribe-rev-dashboard.vercel.app](https://docstribe-rev-dashboard.vercel.app)**

> Upload `patients_anonymized.xlsx` and optionally add your Anthropic API key to unlock all AI features.

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **UI Framework** | React 18 (CDN + Babel Standalone — no build step) |
| **Styling** | Tailwind CSS (CDN) + custom glassmorphism CSS |
| **Excel Parsing** | SheetJS (`xlsx.full.min.js`) — in-browser, no server needed |
| **Charts** | Chart.js 4 — doughnut, bar, horizontal bar, line/area |
| **AI Chatbot** | Claude Sonnet (`claude-sonnet-4-5`) via Anthropic Messages API |
| **CEO Briefing** | Claude Sonnet — auto-generated from dynamic Excel context |
| **Fonts** | Inter · Space Grotesk (Google Fonts) |
| **Deployment** | Vercel (static) / Python `http.server` (local) |

**Architecture:** Entirely self-contained `index.html` — no npm, no bundler, no backend. All data is processed client-side in the browser.

---

## ✨ Features

### 📊 Dynamic Excel Upload
- Drag-and-drop or file-picker upload of `.xlsx` files
- All 4 sheets parsed simultaneously: **Patients**, **Visits**, **Visit Actions**, **Call History**
- Cross-sheet patient index built in-memory for instant queries
- **Zero hardcoded values** — every metric is computed dynamically from the uploaded file

### 🎯 Risk Stratification
- Patient cohort categorised into **Critical / High / Medium / Rising** risk levels
- Risk scores from the `Clinical Summary` JSON field (nested inside Patients sheet)
- Doughnut chart with live patient counts and percentages

### 🏥 IP Admission Potential
- Flags patients with `ip_potential_flag = true` from clinical intelligence JSON
- Admission rate computed dynamically across the cohort
- Cross-referenced with urgency actions and care gaps

### 💰 Revenue Analytics
- Total revenue potential aggregated from **Visit Actions** sheet (`Revenue Potential` column)
- Breakdown by action type (Medication, Lab Test, Radiology, Follow-Up, Referral…)
- Status breakdown: completed / scheduled / pending — all dynamically computed
- Displayed in Indian Rupee format (₹ Cr / L / K)

### 📈 Visit Trends by Department
- Top 10 departments by visit volume (horizontal bar chart)
- Monthly visit trend line chart across the full date range
- Average visits per month computed dynamically

### 📞 Call History Analytics
- Connection rate, connected vs. not-connected counts
- Call reason breakdown (Visited, Follow-Up, Couldn't Reach, Booking…)
- Monthly call volume trend chart
- All labels mapped from raw enum values in Call History sheet

### 🧠 AI Executive Intelligence Briefing *(requires Anthropic API key)*
- **Auto-generated on data load** when an API key is set
- Claude Sonnet analyses all 4 sheets and produces a structured CEO briefing covering:
  - Executive Summary
  - Critical Risk Alerts (with exact patient counts)
  - Revenue Opportunity (in ₹)
  - Patient Engagement status
  - IP Admission Intelligence
  - 3 Immediate Action Items
- Regenerate button for fresh analysis
- Full markdown rendering (headings, bullets, bold metrics)

### 🤖 Natural Language AI Chatbot *(Claude Sonnet or rule-based fallback)*
- Embedded slide-in chat panel (bottom-right floating button)
- **With API key:** Claude Sonnet answers using dynamically built JSON context from all 4 sheets
- **Without API key:** Falls back to built-in rule-based query engine (no degradation in patient filtering)
- Example queries supported:
  - *"Show me all critical patients"*
  - *"High-risk patients with no follow-up scheduled"*
  - *"Show diabetic patients referred to cardiology"*
  - *"Patients with missed calls or no call response"*
  - *"What is the total revenue potential?"*
  - *"IP admission candidates"*
  - *"Female patients over 60"*
  - *"Patients with multiple chronic diseases"*
- Each response returns: narrative summary · stat chips · filtered patient mini-table with pagination

### 👤 Patient Demographics
- Gender distribution (doughnut)
- Age group segmentation: 0–18 / 19–35 / 36–50 / 51–65 / 65+ (bar chart)

### 🗃️ Full Patient Table
- All patients with risk level, risk score bar, IP flag, care gaps, follow-up department, workflow status
- Search by name or department
- Filter by risk category (All / Rising / Medium / High / Critical)
- Paginated (12 per page)

---

## 🚀 Setup Instructions

### Option 1 — Local Python Server (recommended)

```bash
# Clone the repository
git clone https://github.com/NikhilM150/docstribe_rev_dashboard.git
cd docstribe_rev_dashboard

# Start a local HTTP server
python -m http.server 8080

# Open in browser
# http://localhost:8080
```

### Option 2 — Direct File Open

```bash
# Simply open index.html in any modern browser
# (Chrome / Edge recommended for full FileReader API support)
open index.html        # macOS
start index.html       # Windows
```

### Enabling AI Features

1. Open the dashboard and upload `patients_anonymized.xlsx`
2. Click the **🤖** button (bottom-right) to open the AI chat panel
3. Click **⚙** (settings icon) in the chat panel header
4. Paste your Anthropic API key (`sk-ant-...`) and press **Save**
5. The CEO briefing will auto-generate immediately
6. All chat queries will now be answered by **Claude Sonnet**

> **Get an API key:** [console.anthropic.com](https://console.anthropic.com)  
> The key is stored in `sessionStorage` only — it is cleared when you close the browser tab and is never transmitted anywhere except directly to `api.anthropic.com`.

---

## 📋 Assumptions

- **Sheet names must be exactly:** `Patients`, `Visits`, `Visit Actions`, `Call History` (case-sensitive)
- The `Clinical Summary` column in the **Patients** sheet must contain valid JSON strings with nested keys: `risk_stratification`, `ip_potential`, `care_gaps_present`, `next_follow_up`, `chronic_flag`, `operational_snapshot`
- Patient IDs must be consistent across all 4 sheets for cross-sheet joins to work correctly
- The **Visit Actions** sheet must have a `Revenue Potential` column with numeric values
- The **Call History** sheet must have `Call Status` values in the format: `connected`, `not_connected`, `resolved`
- All data provided (`patients_anonymized.xlsx`) is **synthetic and anonymized** — no real patient information is used

---

## ⚠️ Known Limitations

- **API key required** for Claude AI chatbot responses and CEO briefing generation
- Without an API key the dashboard remains fully functional with the built-in **rule-based query engine** for all patient filtering and chat queries
- The Anthropic API is called directly from the browser using the `anthropic-dangerous-direct-browser-access: true` header — suitable for internal/demo tools but not recommended for production deployments with shared API keys
- Claude context is capped at **12 filtered patients per query** to stay within reasonable token limits; the patient table still shows all matching results
- No persistent storage — data and API key are cleared on browser close (by design, for privacy)
- Large Excel files (>10 MB) may have a brief parsing delay on lower-end devices

---

## 🔒 Data Privacy

| What | Where it goes |
|---|---|
| Excel file contents | **Processed entirely in your browser** — never uploaded to any server |
| Patient names & demographics | **Never sent externally** — stays in browser memory only |
| Claude API queries | Only a **compact, anonymized JSON summary** of cohort statistics + up to 12 filtered patient records (name, age, risk level, department) is sent to `api.anthropic.com` |
| Anthropic API key | Stored in **`sessionStorage`** only — cleared on tab close, never logged or transmitted elsewhere |
| Dashboard analytics | No telemetry, no tracking, no cookies |

---

## 📁 Project Structure

```
docstribe_rev_dashboard/
├── index.html                  # Complete self-contained application
├── patients_anonymized.xlsx    # Sample dataset (4 sheets, 200 patients)
└── README.md                   # This file
```

---

## 🔗 GitHub Repository

**[https://github.com/NikhilM150/docstribe_rev_dashboard](https://github.com/NikhilM150/docstribe_rev_dashboard)**

---

## 📄 License

Built for the **Docstribe hiring assignment**. Not for commercial redistribution.

---

<div align="center">
  <sub>Built with React · Tailwind CSS · SheetJS · Chart.js · Claude Sonnet AI &nbsp;|&nbsp; All patient data processed locally in-browser</sub>
</div>
