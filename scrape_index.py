import csv
import os
import shutil
import tempfile
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from utils import (
    extract_name,
    extract_title,
    extract_location,
    extract_education,
    extract_connections,
    MISCONDUCT_SEARCH_TERMS
)

# ========= CONFIGURATION ========= #
SEARCH_QUERY = 'site:linkedin.com/in ("U.S." AND "ICE" AND "Immigration")'
CSV_FILENAME = 'ice_agents.csv'
TRAINING_FILENAME = 'training_profiles.csv'
ARTICLE_LOG = 'article_log.csv'
ARTICLE_DIR = Path("articles")
SCROLL_CHECK_TIME = 10
RESTART_ARTICLE_DRIVER_EVERY = 10  # agents

BAD_WORDS = [
    'lawyer', 'attorney', 'counsel', 'litigation', 'chief counsel',
    'assistant chief counsel', 'general attorney', 'executive deputy principal legal advisor',
    'esq', 'legal advisor', 'managing partner', 'founder', 'public affairs',
    'privacy officer', 'speechwriter', 'rights', 'lgbt'
]
GOOD_WORDS = [
    'agent', 'officer', 'director', 'supervisor', 'investigator',
    'field office', 'deportation', 'enforcement', 'compliance', 'attaché',
    'mission support', 'program manager', 'section chief', 'analyst', 'criminal'
]
URL_BAD_PARTS = ['llc', 'group', 'solutions', 'consulting', 'services']

ARTICLE_DIR.mkdir(exist_ok=True)
# ================================= #

user_data_dir = tempfile.mkdtemp()
article_user_data_dir = tempfile.mkdtemp()

def create_chrome_driver(user_data):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_argument(f"--user-data-dir={user_data}")
    return webdriver.Chrome(options=options)

driver = create_chrome_driver(user_data_dir)
article_driver = create_chrome_driver(article_user_data_dir)

def is_bad_title(title):
    return any(word in title.lower() for word in BAD_WORDS)

def is_good_title(title):
    return any(word in title.lower() for word in GOOD_WORDS)

def is_ice_experience(snippet):
    snippet = snippet.lower()
    return ("experience: u.s. immigration and customs enforcement" in snippet
            or ("ice" in snippet and "experience" in snippet))

def is_human_url(url):
    return not any(bad in url.lower() for bad in URL_BAD_PARTS)

def log_article(name, index, url, text):
    log_exists = Path(ARTICLE_LOG).exists()
    with open(ARTICLE_LOG, 'a', newline='', encoding='utf-8') as log:
        writer = csv.writer(log)
        if not log_exists:
            writer.writerow(['Name', 'Index', 'Article URL'])
        writer.writerow([name, index, url])
    safe_name = name.replace(' ', '_').replace('/', '_')
    filename = ARTICLE_DIR / f"{safe_name}_{index}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def get_misconduct_snippet(driver, name):
    snippets = []
    query = f'"{name}" ICE misconduct immigration'
    driver.get("https://www.bing.com/")
    time.sleep(1)
    try:
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        articles = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        for idx, article in enumerate(articles[:3]):
            try:
                link = article.find_element(By.CSS_SELECTOR, "h2 a")
                snippet_elem = article.find_element(By.CSS_SELECTOR, "p")
                url = link.get_attribute("href")
                snippet = snippet_elem.text.strip()
                if snippet:
                    log_article(name, idx + 1, url, snippet)
                    snippets.append(snippet)
            except:
                continue
    except Exception as e:
        print(f"⚠️ Article search failed for {name}: {e}")
    time.sleep(random.uniform(3, 5))
    return " ".join(snippets[:2])

try:
    print("🔵 Opening DuckDuckGo...")
    driver.get("https://duckduckgo.com/")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(SEARCH_QUERY)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    last_click_time = time.time()
    print("🔵 Scrolling and loading results...")

    while True:
        try:
            more = driver.find_element(By.ID, "more-results")
            if more.is_displayed():
                driver.execute_script("arguments[0].click();", more)
                last_click_time = time.time()
                time.sleep(3)
        except:
            pass

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)
        if time.time() - last_click_time > SCROLL_CHECK_TIME:
            break

    print("🔵 Collecting results...")
    article_elements = driver.find_elements(By.XPATH, "//article")

    results = []
    for a in article_elements:
        try:
            link = a.find_element(By.CSS_SELECTOR, "h2 a")
            snippet = a.find_element(By.CSS_SELECTOR, '[data-result="snippet"]').text
            url = link.get_attribute("href")
            name = link.text.strip()
            if url and "linkedin.com/in/" in url:
                results.append((url, name, snippet))
        except:
            continue

    entries = []
    seen = set()
    for i, (url, raw_name, snippet) in enumerate(results, 1):
        if url in seen:
            continue
        seen.add(url)

        if (is_bad_title(snippet) or not is_good_title(snippet)
                or not is_ice_experience(snippet) or not is_human_url(url)):
            continue

        name = extract_name(raw_name)

        # Recreate article_driver if dead or every N entries
        if i % RESTART_ARTICLE_DRIVER_EVERY == 0:
            try:
                article_driver.quit()
            except:
                pass
            article_driver = create_chrome_driver(tempfile.mkdtemp())

        try:
            article_driver.title
        except:
            print("⚠️ Article driver was lost. Restarting...")
            article_driver.quit()
            article_driver = create_chrome_driver(tempfile.mkdtemp())

        print(f"🔍 Searching for articles about: {name}")
        misconduct = get_misconduct_snippet(article_driver, name)
        final_snippet = misconduct or snippet

        entry = {
            'Number': i,
            'Name': name,
            'Title': extract_title(snippet),
            'Location': extract_location(snippet),
            'Education': extract_education(snippet),
            'Connections': extract_connections(snippet),
            'Profile URL': url,
            'Snippet': final_snippet
        }
        entries.append(entry)
        print(f"✅ [{i}] {name}: {entry['Title']} | Snippet: {final_snippet[:100]}...")

    print(f"✅ Finished scraping {len(entries)} entries. Saving...")

    with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Number', 'Name', 'Title', 'Location', 'Education', 'Connections', 'Profile URL'
        ])
        writer.writeheader()
        for e in entries:
            writer.writerow({k: e[k] for k in writer.fieldnames})

    with open(TRAINING_FILENAME, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Title', 'Snippet'])
        writer.writeheader()
        for e in entries:
            writer.writerow({k: e[k] for k in writer.fieldnames})

finally:
    driver.quit()
    try:
        article_driver.quit()
    except:
        pass
    shutil.rmtree(user_data_dir, ignore_errors=True)
    shutil.rmtree(article_user_data_dir, ignore_errors=True)