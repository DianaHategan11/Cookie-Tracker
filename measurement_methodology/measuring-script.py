import csv
import json
import time
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import tldextract
from selenium import webdriver
from selenium.webdriver.common.by import By

from pathlib import Path

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

DDG_TRACKER_LIST_URL = (
    "https://raw.githubusercontent.com/duckduckgo/tracker-radar/main/build-data/generated/domain_map.json"
)

PRE_CONSENT_WAIT = 20
POST_CONSENT_WAIT = 10
CONSENT_TIMEOUT = 15

REGION = "AUSTRALIA"

SITES = {
    "news": [
        "https://www.euronews.com/",
        "https://www.bbc.com/news/world/europe",
        "https://www.theguardian.com/world/europe-news",
        "https://www.lemonde.fr/en/",
        "https://www.spiegel.de/",
        "https://www.elmundo.es/",
        "https://www.politico.eu/",
        "https://www.ft.com/",
        "https://www.volkskrant.nl/",
        "https://www.nrc.nl/",
        "https://www.hotnews.ro/",
        "https://www.mediafax.ro/",
        "https://www.corriere.it/",
        "https://www.dw.com/en/top-stories/s-9097",
    ],
    "e_commerce": [
        "https://www.bol.com/",
        "https://www.coolblue.nl/",
        "https://www.zalando.com/",
        "https://www.otto.de/",
        "https://www.aboutyou.de/",
        "https://www.cdiscount.com/",
        "https://www.elcorteingles.es/",
        "https://www.unieuro.it/",
        "https://www.euronics.it/",
        "https://altex.ro/",
        "https://www.olx.ro/",
        "https://www.ikea.com/",
        "https://www.jysk.com/",
        "https://www.decathlon.nl/",
        "https://www.vinted.nl",
    ],
    "social_media": [
        "https://www.facebook.com/",
        "https://www.instagram.com/",
        "https://www.linkedin.com/",
        "https://www.reddit.com/", 
        "https://x.com/",
        "https://www.tiktok.com/",
        "https://www.pinterest.com/",
        "https://discord.com/",
        "https://www.threads.net/",
        "https://www.twitch.tv/",
        "https://www.quora.com/",
        "https://www.kick.com/",
    ],
    "government": [
        "https://www.belgium.be/en",
        "https://www.service-public.fr/",
        "https://www.gouvernement.fr/",
        "https://www.bundesregierung.de/",
        "https://www.governo.it/",
        "https://www.government.se/",
        "https://www.denmark.dk/",
        "https://valtioneuvosto.fi/en",
        "https://www.gov.ie/",
        "https://www.europarl.europa.eu/",
    ],
    "education": [
        "https://www.utwente.nl/",
        "https://www.tudelft.nl/",
        "https://utcluj.ro/",
        "https://www.kuleuven.be/",
        "https://www.sorbonne-universite.fr/",
        "https://www.ku.dk/",
        "https://www.comillas.edu/",
        "https://www.helsinki.fi/",
        "https://www.polimi.it/en/",
        "https://www.unibo.it/",
        "https://www.ucm.es/",
        "https://www.tcd.ie/",
        "https://www.ox.ac.uk/",
        "https://www.cam.ac.uk/",
    ],
}

INDIA_SITES = {
    "news": [
        "https://timesofindia.indiatimes.com/",
        "https://www.hindustantimes.com/",
    ],
    "e_commerce": [
        "https://www.flipkart.com/",
        "https://www.myntra.com/",
    ],
    "social_media": [
        "https://www.facebook.com/",
        "https://www.instagram.com/",
        "https://www.linkedin.com/",
        "https://www.reddit.com/",
    ],
    "government": [
        "https://www.passportindia.gov.in/psp",
    ],
    "education": [
        "https://iisc.ac.in/",
    ],
}

AUSTRALIA_SITES = {
    "news": [
        "https://www.smh.com.au/",
    ],
    "e_commerce": [
        "https://www.kogan.com/au/",
        "https://www.theiconic.com.au/",
    ],
    "social_media": [
        "https://www.facebook.com/",
        "https://www.instagram.com/",
        "https://www.linkedin.com/",
        "https://www.reddit.com/",
    ],
    "government": [
        "https://www.australia.gov.au/",
    ],
    "education": [
        "https://www.unimelb.edu.au/",
    ],
}

SOUTH_AFRICA_SITES = {
    "news": [
        "https://www.africanews.com/",
        "https://allafrica.com/",
    ],
    "e_commerce": [
        "https://www.jumia.com.ng/",
        "https://www.takealot.com/",
    ],
    "social_media": [
        "https://www.facebook.com/",
        "https://www.instagram.com/",
        "https://www.linkedin.com/",
        "https://www.reddit.com/",
    ],
    "government": [
        "https://www.gov.za/",
    ],
    "education": [
        "https://www.uct.ac.za/",
    ],
}

BRAZIL_SITES = {
    "news": [
        "https://www.riotimesonline.com/",
    ],
    "e_commerce": [
        "https://www.magazineluiza.com.br/",
        "https://www.americanas.com.br/",
    ],
    "social_media": [
        "https://www.facebook.com/",
        "https://www.instagram.com/",
        "https://www.linkedin.com/",
        "https://www.reddit.com/",
    ],
    "government": [
        "https://www.gov.br/",
    ],
    "education": [
        "https://www5.usp.br/",
    ],
}

US_SITES = {
    "news": [
        "https://www.cnn.com/",
        "https://www.nytimes.com/",
        "https://www.washingtonpost.com/",
        "https://www.npr.org/",
        "https://www.bloomberg.com/",
    ],
    "e_commerce": [
        "https://www.amazon.com/",
        "https://www.ebay.com/",
    ],
    "social_media": [
        "https://www.facebook.com/",
        "https://www.instagram.com/",
        "https://www.linkedin.com/",
        "https://www.reddit.com/",
    ],
    "government": [
        "https://www.usa.gov/",
        "https://www.whitehouse.gov/",
    ],
    "education": [
        "https://www.harvard.edu/",
        "https://www.mit.edu/",
        "https://www.stanford.edu/",
    ],
}

def load_ddg_tracker_domains():
    print("Fetching DuckDuckGo tracker list...")
    try:
        with urllib.request.urlopen(DDG_TRACKER_LIST_URL, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        domains = set(data.keys())
        print(f"Loaded {len(domains)} tracker domains.")
        return domains
    except Exception as exc:
        print(f"Could not load DDG tracker list ({exc}). Tracker matching disabled.")
        return set()


def registrable_domain(hostname):
    ext = tldextract.extract(hostname)
    if not ext.domain or not ext.suffix:
        return hostname
    return f"{ext.domain}.{ext.suffix}"


def domain_from_url(url):
    host = urlparse(url).hostname
    if not host:
        return None
    return registrable_domain(host)


def is_third_party(site_url, request_domain):
    site_domain = domain_from_url(site_url)
    if not site_domain or not request_domain:
        return False
    return site_domain != request_domain


def make_driver():
    profile_dir = tempfile.mkdtemp()
    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en-US")
    options.page_load_strategy = "eager"
    options.add_argument(
        f"--user-data-dir={profile_dir}"
    )
    options.add_experimental_option("prefs", {
        "intl.accept_languages": "en-US,en"
    })
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(10)
    return driver


def parse_requests_from_logs(logs, phase):
    records = []
    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]
        except (json.JSONDecodeError, KeyError):
            continue

        if message.get("method") != "Network.requestWillBeSent":
            continue

        params = message.get("params", {})
        request = params.get("request", {})
        url = request.get("url", "")
        if not url.startswith(("http://", "https://")):
            continue

        records.append({
            "phase": phase,
            "timestamp": params.get("timestamp"),
            "request_id": params.get("requestId"),
            "url": url,
            "domain": domain_from_url(url),
            "method": request.get("method"),
            "initiator_type": params.get("initiator", {}).get("type"),
            "resource_type": params.get("type"),
        })
    return records


def parse_cookies_from_logs(logs, phase):
    records = []
    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]
        except (json.JSONDecodeError, KeyError):
            continue

        if message.get("method") != "Network.responseReceivedExtraInfo":
            continue

        params = message.get("params", {})
        headers = params.get("headers", {})

        for header_name, header_value in headers.items():
            if header_name.lower() == "set-cookie":
                for raw_cookie in header_value.split("\n"):
                    raw_cookie = raw_cookie.strip()
                    if raw_cookie:
                        records.append({
                            "phase": phase,
                            "request_id": params.get("requestId"),
                            "status_code": params.get("statusCode"),
                            "raw_set_cookie": raw_cookie,
                            "cookie_name": raw_cookie.split("=")[0].strip(),
                        })
    return records

KNOWN_CONSENT_SELECTORS = [
    "#onetrust-accept-btn-handler",
    "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
    "#didomi-notice-agree-button",
    "#pg-accept-btn",
    "[data-testid='accept-all-button']",
]

ACCEPT_KEYWORDS = [
    "accept all", "accept cookies", "accept all cookies", "allow all", "allow cookies", "allow all cookies", "i accept all cookies",
    "agree", "i agree", "accept", "i accept", "allow", "i accept analytics cookies", "accept additional cookies", "accept optional cookies",
    "ok", "got it", "continue", "consent", "yes", "yes, i accept", "confirm", "consent and continue", "accept and continue", "agree & close",
    "accept", "accceptă", "accept toate", "sunt de acord", "aceptar y cerrar", "aceptar y continuar", 
    "tout accepter", "oui", "accord", "oui, je suis d'accord", "tillatt",
    "si, acconsento", "accetta", "accetta e continua", "accetta tutti i cookie", 
    "accepter", "accepteren", "alles accepteren", "alles toestaan", "alle cookies toestaan", 
    "oke", "oké", "bestätigen", "alle auswählen", "aceitar", "aceitar cookies",
]

REJECT_KEYWORDS = [
    "do not agree", "don't agree", "reject", "decline", "deny",
    "manage preferences", "preferences", "manage cookies", 
    "cookie settings", "settings",
    "customize", "customise",
]

def text_matches_accept(text):
    text = " ".join(text.lower().split())

    if any(kw in text for kw in REJECT_KEYWORDS):
        return False

    if text in ACCEPT_KEYWORDS:
        return True

    return False

def get_button_text(el):
    return (
        el.text
        or el.get_attribute("aria-label")
        or el.get_attribute("title")
        or el.get_attribute("value")
        or ""
    ).strip()

def get_shadow_hosts(driver):

    return driver.execute_script("""
        const hosts = [];

        function walk(root){

            const walker =
                document.createTreeWalker(
                    root,
                    NodeFilter.SHOW_ELEMENT
                );

            let node;

            while(node = walker.nextNode()){

                if(node.shadowRoot){
                    hosts.push(node);
                    walk(node.shadowRoot);
                }
            }
        }

        walk(document);

        return hosts;
    """)

def try_shadow_selectors(driver):
    for host in get_shadow_hosts(driver):

        for selector in KNOWN_CONSENT_SELECTORS:
            try:
                el = driver.execute_script(
                    """
                    return arguments[0]
                        .shadowRoot
                        .querySelector(arguments[1]);
                    """,
                    host,
                    selector
                )

                if el:
                    print(
                        "FOUND SELECTOR:",
                        selector
                    )

                    driver.execute_script(
                        "arguments[0].click();",
                        el
                    )
                    return True

            except Exception:
                pass

    return False

def try_shadow_text_match(driver):

    for host in get_shadow_hosts(driver):

        try:
            elements = driver.execute_script(
                """
                return Array.from(
                    arguments[0].shadowRoot.querySelectorAll(
                        'button, [role="button"]'
                    )
                );
                """,
                host
            )

        except Exception:
            continue

        for el in elements:

            try:
                text = driver.execute_script(
                    "return arguments[0].textContent;",
                    el
                )

                if text_matches_accept(text):
                    print("ACTUALLY CLICKING:", text)
                    driver.execute_script(
                        "arguments[0].click();",
                        el
                    )
                    return True

            except Exception:
                continue

    return False


def try_click_in_frame(driver):
    if try_shadow_selectors(driver):
        return True
    if try_shadow_text_match(driver):
        return True
    
    candidates = driver.find_elements(
        By.XPATH,
        "//button | //*[@role='button'] | //a[contains(@class,'consent') or contains(@class,'cookie')]",
    )

    for selector in KNOWN_CONSENT_SELECTORS:
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            if el.is_displayed():
                driver.execute_script("arguments[0].click()", el)
                print(
                    "CLICKED:",
                    selector
                )
                return True
        except:
            pass
    for el in candidates:
        try:
            text = get_button_text(el)
            if not text_matches_accept(text):
                continue
            if not el.is_displayed() or not el.is_enabled():
                continue
            print("CLICKING:", text)
            try:
                el.click()
            except:
                driver.execute_script(
                    "arguments[0].click();",
                    el
                )
            return True
        except Exception:
            continue
    return False

def click_accept_if_found(driver, timeout=CONSENT_TIMEOUT):
    end_time = time.time() + timeout
    clicked_anything = False

    while time.time() < end_time:
        driver.switch_to.default_content()

        if try_click_in_frame(driver):
            clicked_anything = True
            time.sleep(1)
            continue

        for iframe in driver.find_elements(By.TAG_NAME, "iframe"):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(iframe)

                if try_click_in_frame(driver):
                    clicked_anything = True
                    time.sleep(1)
                    break

            except Exception:
                continue

        time.sleep(0.5)

    driver.switch_to.default_content()

    if clicked_anything:
        return "clicked"

    return "not_found"


def measure_site(url, tracker_domains):
    banner_detected = False
    cmp_vendor = None
    
    print(f"  Visiting {url}")
    driver = make_driver()
    try:
        driver.get(url)
        time.sleep(PRE_CONSENT_WAIT)

        html = driver.page_source.lower()

        for cmp_name in [
            "onetrust",
            "cookiebot",
            "didomi",
            "trustarc",
            "sourcepoint",
            "usercentrics",
            "quantcast",
            "consentmanager",
        ]:
            if cmp_name in html:
                banner_detected = True
                cmp_vendor = cmp_name
                print("CMP FOUND:", cmp_name)

        pre_logs = driver.get_log("performance")
        pre_requests = parse_requests_from_logs(pre_logs, "pre_consent")
        pre_cookies = parse_cookies_from_logs(pre_logs, "pre_consent")

        consent_status = click_accept_if_found(driver)
        print(f"    Consent status: {consent_status}")

        if consent_status == "clicked":

            time.sleep(POST_CONSENT_WAIT)

            post_logs = driver.get_log("performance")
            post_requests = parse_requests_from_logs(
                post_logs,
                "post_consent"
            )
            post_cookies = parse_cookies_from_logs(
                post_logs,
                "post_consent"
            )

        else:

            post_requests = []
            post_cookies = []

        all_requests = pre_requests + post_requests
        for req in all_requests:
            req["third_party"] = is_third_party(url, req["domain"])
            req["is_tracker"] = req["domain"] in tracker_domains if req["domain"] else False

        request_lookup = {r["request_id"]: r for r in all_requests if "request_id" in r}
        all_cookies = pre_cookies + post_cookies
        for ck in all_cookies:
            req = request_lookup.get(ck.get("request_id", ""), {})
            domain = req.get("domain")
            ck["domain"] = domain
            ck["third_party"] = req.get("third_party", None)
            ck["is_tracker"] = (domain in tracker_domains) if domain else False

        return {
            "url": url,
            "region": REGION,
            "banner_detected": banner_detected,
            "cmp_vendor": cmp_vendor,
            "consent_status": consent_status,
            "requests": all_requests,
            "cookies": all_cookies,
            "error": None,
        }

    except Exception as exc:
        print(f"    Failed to measure {url}: {exc}")
        return {
            "url": url,
            "region": REGION,
            "banner_detected": banner_detected,
            "cmp_vendor": cmp_vendor,
            "consent_status": "error",
            "requests": [],
            "cookies": [],
            "error": str(exc),
        }
    finally:
        driver.quit()


def summarise(category, result):
    requests = result["requests"]
    cookies = result["cookies"]

    pre_requests = [r for r in requests if r["phase"] == "pre_consent"]
    pre_3p = [r for r in pre_requests if r["third_party"]]
    pre_trackers = [r for r in pre_requests if r["is_tracker"]]

    pre_cookies = [c for c in cookies if c["phase"] == "pre_consent"]
    pre_3p_cookies = [c for c in pre_cookies if c.get("third_party")]
    pre_tracker_cookies = [c for c in pre_cookies if c.get("is_tracker")]

    post_requests = [r for r in requests if r["phase"] == "post_consent"]
    post_3p = [r for r in post_requests if r["third_party"]]
    post_trackers = [r for r in post_requests if r["is_tracker"]]

    post_cookies = [c for c in cookies if c["phase"] == "post_consent"]
    post_3p_cookies = [c for c in post_cookies if c.get("third_party")]
    post_tracker_cookies = [c for c in post_cookies if c.get("is_tracker")]

    tracker_domain_counts = {}
    for r in pre_trackers:
        d = r["domain"] or "unknown"
        tracker_domain_counts[d] = tracker_domain_counts.get(d, 0) + 1
    top_trackers = sorted(tracker_domain_counts.items(), key=lambda x: -x[1])[:5]

    return {
        "category": category,
        "url": result["url"],
        "region": result["region"],
        "banner_detected": result["banner_detected"],
        "consent_status": result["consent_status"],
        "error": result.get("error"),
        "total_requests": len(requests),
        "pre_consent_requests": len(pre_requests),
        "pre_consent_3p_requests": len(pre_3p),
        "pre_consent_tracker_requests": len(pre_trackers),
        "total_cookies": len(cookies),
        "pre_consent_cookies": len(pre_cookies),
        "pre_consent_3p_cookies": len(pre_3p_cookies),
        "pre_consent_tracker_cookies": len(pre_tracker_cookies),
        "post_consent_requests": len(post_requests),
        "post_consent_3p_requests": len(post_3p),
        "post_consent_tracker_requests": len(post_trackers),
        "post_consent_cookies": len(post_cookies),
        "post_consent_3p_cookies": len(post_3p_cookies),
        "post_consent_tracker_cookies": len(post_tracker_cookies),
        "top_tracker_domains": "; ".join(f"{d}({n})" for d, n in top_trackers),
    }


def run_all(sites, tracker_domains):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = OUTPUT_DIR / f"raw_{REGION}_{timestamp}.json"
    summary_path = OUTPUT_DIR / f"summary_{REGION}_{timestamp}.csv"

    all_results = []
    all_summaries = []

    for category, urls in sites.items():
        print(f"\n=== Category: {category} ===")
        for url in urls:
            result = measure_site(url, tracker_domains)
            result["category"] = category
            all_results.append(result)
            all_summaries.append(summarise(category, result))

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Raw data written to {raw_path}")

    if all_summaries:
        fieldnames = list(all_summaries[0].keys())
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_summaries)
    print(f"Summary CSV written to {summary_path}")

    print("\n========== RUN SUMMARY ==========")
    for s in all_summaries:
        print(        
            f"[{s['category']:12}] {s['url']:45}"
            f"  pre-tracker-req: {s['pre_consent_tracker_requests']:3}"
            f"  pre-tracker-ck: {s['pre_consent_tracker_cookies']:3}"
            f"  consent: {s['consent_status']}"
            f"  post-tracker-req: {s['post_consent_tracker_requests']:3}"
            f"  post-tracker-ck: {s['post_consent_tracker_cookies']:3}"
        )
    print("=================================\n")

if __name__ == "__main__":
    tracker_domains = load_ddg_tracker_domains()
    run_all(AUSTRALIA_SITES, tracker_domains)