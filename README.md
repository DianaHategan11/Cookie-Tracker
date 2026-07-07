# Cookie-Tracker

# Measurement Methodology

A Selenium-based measurement tool for studying cookie consent behavior, third-party requests, and tracker activity across regional websites.

The script visits websites by category, records browser network activity before consent, attempts to accept cookie banners, records activity after consent, and exports both raw JSON data and summary CSV files.

## What this project measures

For each website, the tool collects:

- Cookie consent banner detection
- Detected Consent Management Platform (CMP), when identifiable
- Consent interaction status (`clicked`, `not_found`, or `error`)
- Pre-consent and post-consent network requests
- Pre-consent and post-consent `Set-Cookie` headers
- Third-party requests and cookies
- Tracker requests and cookies, matched against DuckDuckGo Tracker Radar
- Top tracker domains observed before consent

## How it works

1. Downloads the DuckDuckGo Tracker Radar domain map.
2. Opens each target site in a fresh Chrome browser profile.
3. Waits before consent to capture initial requests and cookies.
4. Searches for cookie consent buttons using:
   - Known CMP selectors
   - Button text matching
   - Shadow DOM traversal
   - Iframe traversal
5. Clicks an accept/allow button when found.
6. Captures post-consent requests and cookies.
7. Labels each request/cookie as first-party or third-party.
8. Labels tracker activity using the DuckDuckGo tracker list.
9. Writes raw and summarized results to the `results/` directory.

## Requirements

- Python 3.9+
- Google Chrome
- ChromeDriver compatible with your installed Chrome version
- Python packages:
  - `selenium`
  - `tldextract`

Install the Python dependencies with:

```bash
pip install selenium tldextract
```

Depending on your environment, you may also need to install ChromeDriver separately and make sure it is available on your `PATH`.

## Usage

Run the script from the project directory:

```bash
python measuring-script.py
```

By default, the script currently runs measurements for:

```python
AUSTRALIA_SITES
```

To measure a different region, edit the final line of `measuring-script.py`:

```python
run_all(AUSTRALIA_SITES, tracker_domains)
```

For example:

```python
run_all(US_SITES, tracker_domains)
```

Also update the `REGION` variable near the top of the script so output filenames and result metadata match the region being measured:

```python
REGION = "US"
```

## Output files

Each run creates two files in `results/`:

```text
raw_<REGION>_<TIMESTAMP>.json
summary_<REGION>_<TIMESTAMP>.csv
```

### Raw JSON

The raw JSON file contains detailed per-site records, including:

- URL
- Region
- Consent status
- Banner/CMP detection
- Full request records
- Full cookie records
- Errors, if any

### Summary CSV

The summary CSV provides one row per website with aggregate metrics such as:

- Total requests
- Pre-consent requests
- Pre-consent third-party requests
- Pre-consent tracker requests
- Total cookies
- Pre-consent cookies
- Pre-consent third-party cookies
- Pre-consent tracker cookies
- Post-consent request and cookie counts
- Top pre-consent tracker domains

## Included site categories

The script contains website lists grouped by category:

- News
- E-commerce
- Social media
- Government
- Education

It includes predefined regional lists for Europe, India, Australia, South Africa, Brazil, and the United States.

## Disclaimer

This project is intended for research and educational measurement purposes only. 

## Ethical Considerations

To minimise potential impact on websites and the network, the measurements are performed at a limited scale and frequency, to about 135 websites. Each website visit makes use of an automated browser that emulates standard browser behaviour and does not generate traffic other than visiting the target website and visiting any third-party website as requested by the website itself. Measurements are repeated only a limited number of times, primarily when collected data is incomplete or to reduce measurement errors to improve the reliability of the results.

All the selected websites are publicly accessible, and only the homepages of these websites are visited by the automated browser. As only publicly available websites are visited using normal website interactions, the collected data only includes requests and cookies set by the websites themselves, and no personal identifiable information will be included.
