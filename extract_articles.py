
from pathlib import Path
import time

import pandas as pd
import requests
import trafilatura
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "assignments_files" / "Input.xlsx"
ARTICLES_DIR = BASE_DIR / "articles"
LOG_FILE = BASE_DIR / "output" / "extraction_log.csv"

ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


def extract_article(url):
    """Return the article title and main text from a URL."""
    response = session.get(url, timeout=30)
    response.raise_for_status()

    html = response.text

    # First try extracting the main article text.
    downloaded = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )

    # Extract the title separately.
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.get_text(" ", strip=True)
    elif soup.title:
        title = soup.title.get_text(" ", strip=True)
    else:
        title = ""

    # Fall back to common WordPress article containers.
    if not downloaded:
        article = (
            soup.find("article")
            or soup.find("div", class_="td-post-content")
            or soup.find("main")
        )

        if article:
            for unwanted in article.select(
                "script, style, nav, footer, header, aside, "
                ".sharedaddy, .related-posts, .ads"
            ):
                unwanted.decompose()

            downloaded = article.get_text(" ", strip=True)

    if not title or not downloaded:
        raise ValueError("Could not extract both title and article text")

    return title, downloaded.strip()


def main():
    df = pd.read_excel(INPUT_FILE)

    if not {"URL_ID", "URL"}.issubset(df.columns):
        raise ValueError("Input.xlsx must contain URL_ID and URL columns")

    results = []
    total = len(df)

    for index, row in df.iterrows():
        url_id = int(row["URL_ID"])
        url = str(row["URL"]).strip()
        output_file = ARTICLES_DIR / f"{url_id}.txt"

        # Keep successful downloads so a rerun can resume.
        if output_file.exists() and output_file.stat().st_size > 0:
            results.append({
                "URL_ID": url_id,
                "URL": url,
                "STATUS": "SKIPPED_EXISTING",
                "ERROR": "",
            })
            continue

        status = "FAILED"
        error = ""

        for attempt in range(2):
            try:
                title, text = extract_article(url)

                output_file.write_text(
                    f"{title}\n\n{text}\n",
                    encoding="utf-8",
                )

                status = "SUCCESS"
                print(f"[{index + 1}/{total}] Saved {url_id}.txt")
                break

            except Exception as exc:
                error = str(exc)
                if attempt == 0:
                    time.sleep(2)

        if status == "FAILED":
            print(f"[{index + 1}/{total}] FAILED {url_id}: {error}")

        results.append({
            "URL_ID": url_id,
            "URL": url,
            "STATUS": status,
            "ERROR": error,
        })

        # Avoid sending requests too quickly.
        time.sleep(0.5)

        # Save progress periodically.
        if (index + 1) % 25 == 0:
            pd.DataFrame(results).to_csv(LOG_FILE, index=False)

    pd.DataFrame(results).to_csv(LOG_FILE, index=False)

    successes = sum(
        item["STATUS"] in {"SUCCESS", "SKIPPED_EXISTING"}
        for item in results
    )
    failures = sum(item["STATUS"] == "FAILED" for item in results)

    print("\nExtraction completed.")
    print(f"Total rows processed: {total}")
    print(f"Successful or previously saved: {successes}")
    print(f"Failed: {failures}")
    print(f"Article folder: {ARTICLES_DIR}")
    print(f"Log file: {LOG_FILE}")


if __name__ == "__main__":
    main()
