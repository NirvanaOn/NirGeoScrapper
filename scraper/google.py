from playwright.sync_api import sync_playwright, TimeoutError
import time
import re
import random

# ================= CONFIG =================

CONFIG = {
    "DELAY_MIN": 0.6,
    "DELAY_MAX": 1.5,
    "MAX_SCROLLS": 25,
    "SCROLL_PAUSE": 1.2,
    "MAX_IMAGES": 20,          # safety cap
}

# ================= HELPERS =================

def throttle():
    """Human-like random delay"""
    time.sleep(random.uniform(
        CONFIG["DELAY_MIN"],
        CONFIG["DELAY_MAX"]
    ))


def get_text(node, selector, default="N/A"):
    try:
        loc = node.locator(selector)
        if loc.count():
            return loc.first.inner_text().strip()
    except Exception:
        pass
    return default


def get_attr(node, selector, attr, default="N/A"):
    try:
        loc = node.locator(selector)
        if loc.count():
            val = loc.first.get_attribute(attr)
            return val if val else default
    except Exception:
        pass
    return default


def extract_lat_lng(url: str):
    if not url:
        return "N/A", "N/A"
    m = re.search(r'@([-0-9.]+),([-0-9.]+)', url)
    if m:
        return m.group(1), m.group(2)
    return "N/A", "N/A"


def clean_image_url(url: str):
    """
    Normalize Google image URLs and drop junk thumbnails.
    """
    if not url:
        return None

    # drop very small thumbs
    if "w120" in url or "h120" in url:
        return None

    # prefer high-res
    url = re.sub(r"w\d+-h\d+", "w2000-h2000", url)
    return url

def parse_reviews_count(text: str) -> int:
    if not text:
        return 0

    text = text.lower().replace(",", "").strip()

    match = re.search(r'([\d.]+)\s*([km]?)', text)
    if not match:
        return 0

    number = float(match.group(1))
    suffix = match.group(2)

    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000

    return int(number)


# ================= SCRAPER =================

def scrape_google_maps(
    search_query,
    max_places=None,
    skip=0,
    automode=False
):
    seen_urls = set()
    unique_seen = 0
    scraped = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # ---------- OPEN MAPS ----------
            page.goto("https://www.google.com/maps", timeout=60000)
            page.wait_for_selector("#searchboxinput", timeout=15000)

            page.fill("#searchboxinput", search_query)
            page.keyboard.press("Enter")

            page.wait_for_selector('//a[contains(@href,"/maps/place")]', timeout=20000)

            idx = 0
            scrolls = 0

            while True:
                cards = page.locator('//a[contains(@href,"/maps/place")]')
                count = cards.count()

                # ---------- SCROLL ----------
                if idx >= count:
                    scrolls += 1
                    if scrolls >= CONFIG["MAX_SCROLLS"]:
                        print("\n[!] No more results available")
                        break

                    page.mouse.wheel(0, 6000)
                    time.sleep(CONFIG["SCROLL_PAUSE"])
                    continue

                # ---------- CLICK CARD ----------
                try:
                    cards.nth(idx).click(force=True)
                    page.wait_for_timeout(3000)
                except Exception:
                    idx += 1
                    continue

                current_url = page.url

                # ---------- DEDUP ----------
                if current_url in seen_urls:
                    idx += 1
                    continue

                seen_urls.add(current_url)
                unique_seen += 1

                # ---------- SKIP ----------
                if unique_seen <= skip:
                    print(f"[skip] {unique_seen}/{skip}", end="\r")
                    idx += 1
                    continue

                # ---------- LIMIT ----------
                if not automode and max_places and scraped >= max_places:
                    print("\n[+] Max limit reached")
                    break

                # ================= DATA EXTRACTION =================

                place_name    = get_text(page, 'h1.DUwDvf')
                category      = get_text(page, 'button[jsaction*="category"]')
                rating        = get_text(page, 'div.fontDisplayLarge')
                raw_reviews = get_text(page, 'button.GQjSyb span')
                reviews_count = parse_reviews_count(raw_reviews)

                address     = get_text(page, 'button[data-item-id="address"] .Io6YTe')
                plus_code   = get_text(page, 'button[data-item-id="oloc"] .Io6YTe')
                located_in  = get_text(page, 'button[data-item-id="locatedin"] .Io6YTe')

                phone   = get_text(page, 'button[data-item-id*="phone"] .Io6YTe')
                website = get_attr(page, 'a[data-item-id*="authority"]', 'href')

                open_status = get_text(page, 'button[data-item-id^="oh"] .Io6YTe')

                latitude, longitude = extract_lat_lng(current_url)

                # ---------- IMAGES ----------
                image_urls = set()

                imgs = page.locator('button.K4UgGe img[src]')
                for i in range(min(imgs.count(), CONFIG["MAX_IMAGES"])):
                    src = clean_image_url(imgs.nth(i).get_attribute("src"))
                    if src:
                        image_urls.add(src)

                review_imgs = page.locator('button.Tya61d[style*="background-image"]')
                for i in range(min(review_imgs.count(), CONFIG["MAX_IMAGES"])):
                    style = review_imgs.nth(i).get_attribute("style")
                    if style:
                        m = re.search(r'url\("(.*?)"\)', style)
                        if m:
                            src = clean_image_url(m.group(1))
                            if src:
                                image_urls.add(src)

                street_imgs = page.locator('img[src*="streetviewpixels"]')
                for i in range(min(street_imgs.count(), CONFIG["MAX_IMAGES"])):
                    src = clean_image_url(street_imgs.nth(i).get_attribute("src"))
                    if src:
                        image_urls.add(src)

                # ---------- STAR BREAKDOWN ----------
                star_breakdown = {}
                for star in ["5", "4", "3", "2", "1"]:
                    row = page.locator(f'tr[aria-label^="{star} stars"]')
                    star_breakdown[star] = (
                        row.get_attribute("aria-label") if row.count() else "N/A"
                    )

                # ---------- REVIEWERS ----------
                reviewers = []
                review_blocks = page.locator('div.jftiEf')
                for i in range(review_blocks.count()):
                    block = review_blocks.nth(i)
                    reviewers.append({
                        "name": get_text(block, 'div.d4r55.fontTitleMedium'),
                        "profile_url": get_attr(block, 'button.al6Kxe', 'data-href')
                    })

                # ---------- FINAL OBJECT ----------
                place = {
                    "Name": place_name,
                    "Category": category,
                    "Rating": rating,
                    "Reviews Count": reviews_count,
                    "Address": address,
                    "Plus Code": plus_code,
                    "Located In": located_in,
                    "Phone": phone,
                    "Website": website,
                    "Open Status": open_status,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Maps URL": current_url,
                    "Images": list(image_urls),
                    "Star Breakdown": star_breakdown,
                    "Reviewers": reviewers
                }

                scraped += 1
                print(
                    f"[{scraped}{'/' + str(max_places) if max_places else ''}] "
                    f"{place_name}"
                )

                yield place

                idx += 1
                throttle()

        finally:
            browser.close()
