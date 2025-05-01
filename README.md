# ICEPatrol2 (Please read all of this)

**ICEPatrol2** is an OSINT data collection and profiling toolkit for identifying and flagging ICE agents and their misconduct. Inspired by ICEPatrol leaks back in 2017 or 18. It automates the process of discovering agent profiles, scraping online content, and scoring risk based on keyword analysis. Built for idenifying ICE agents but could theoretically be applied to any agency.

---

## 📌 Features

- 🔍 **Google (acutally uses bing) Dorking Automation** — Finds ICE-related LinkedIn profiles
- 🧠 **Keyword Flagging** — Highlights articles/posts with misconduct terms (e.g. "lawsuit", "misconduct", "arrested")
- 📸 **Evidence Archiving** — Saves full articles, screenshots, and profile photos
- 📊 **Role Classification** — Labels scraped individuals as `Agent`, `Lawyer`, or `Other`
- 🤖 **Selenium-Driven Scraping** — Headless browsing and article extraction
- 📝 **Log + Resume Support** — Keeps track of visited URLs to avoid duplication
- Neural Network assesses likleyhood of being either an ICE agent or Immigration Lawyer. It also looks at article titles and decides if the article is describing misconduct.

---

## 🛠️ Requirements

- Python 3.8+
- Chrome (or chromium) + chromedriver
- pip packages:
  ```bash
  pip install pandas scikit-learn joblib selenium

---

## Data
- Info is able to be accessed via this repo
- You do not need to run any of the code to see the data
- You can modify or run the code youself if you wish. 
- This isn't a huge project and I'm just one guy. Theres probably mistakes and false positives. BE CAREFUL! 
- The file example_profiles.csv is all fake data generated to use for training the neural network.
