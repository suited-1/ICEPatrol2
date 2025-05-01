# ICEPatrol2

**ICEPatrol2** is an OSINT-powered data collection and profiling toolkit for identifying and flagging ICE agents and their misconduct. It automates the process of discovering agent profiles, scraping online content, and scoring risk based on keyword analysis. Built for activist research and abolitionist efforts.

---

## 📌 Features

- 🔍 **Google Dorking Automation** — Finds ICE-related LinkedIn profiles
- 🧠 **Keyword Flagging** — Highlights articles/posts with misconduct terms (e.g. "lawsuit", "misconduct", "arrested")
- 📸 **Evidence Archiving** — Saves full articles, screenshots, and profile photos
- 📊 **Role Classification** — Labels scraped individuals as `Agent`, `Lawyer`, or `Other`
- 🤖 **Selenium-Driven Scraping** — Headless browsing and article extraction
- 📝 **Log + Resume Support** — Keeps track of visited URLs to avoid duplication

---

## 🛠️ Requirements

- Python 3.8+
- Chrome + chromedriver
- pip packages:
  ```bash
  pip install selenium beautifulsoup4 requests
