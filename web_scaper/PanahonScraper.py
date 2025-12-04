"""
Alternative implementation using Playwright (more cloud-friendly)

Installation:
pip install playwright
playwright install chromium

Add to nixpacks.toml:
[phases.setup]
nixPkgs = ["chromium"]

[phases.install]
cmds = [
    "pip install -r requirements.txt",
    "playwright install-deps chromium"
]
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time


class PanahonScraperPlaywright:
    def __init__(self):
        self.__panahon_url = "https://www.panahon.gov.ph/"
        self.__data = {}

    def start_scraping(self, location):
        try:
            with sync_playwright() as p:
                print("🚀 Launching browser...")
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--single-process'
                    ]
                )

                page = browser.new_page()

                print(f"🌐 Navigating to {self.__panahon_url}")
                page.goto(self.__panahon_url, wait_until="domcontentloaded")
                page.wait_for_selector("body", timeout=15000)
                print("✅ Page loaded")

                # Click notification button
                print("🔔 Clicking notification button...")
                page.click("button.notification-button")

                # Wait for show button
                page.wait_for_selector("#showSelectedAlertBtn", timeout=10000)

                names = ['Rainfall', 'Thunderstorm', 'Flood', 'Tropical']

                for i in range(4):
                    print(f"\n📊 Processing {names[i]}...")

                    # Select alert type
                    page.select_option("#alertTypeSelect", index=i)

                    # Click show button
                    page.click("#showSelectedAlertBtn")
                    time.sleep(2)

                    # Search for location
                    search_input = page.locator("input[placeholder*='Search'], input[type='search']")
                    search_input.clear()
                    search_input.fill(location)
                    search_input.press("Enter")
                    time.sleep(3)

                    # Extract content
                    content = self.__wait_and_extract_content(page)
                    self.__data[names[i]] = content
                    print(f"   Result: {'✅ Found' if content else '❌ None'}")

                print(f"\n✅ Scraping complete!")
                browser.close()

        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_data(self):
        """Return scraped data or empty structure if failed"""
        if not self.__data:
            return {
                'Rainfall': None,
                'Thunderstorm': None,
                'Flood': None,
                'Tropical': None
            }
        return self.__data

    def __wait_and_extract_content(self, page, timeout=15000):
        try:
            time.sleep(2)

            # Wait for popup to be visible
            page.wait_for_selector(".ol-popup-content", state="visible", timeout=timeout)

            # Wait for content to load
            popup = page.locator(".ol-popup-content")

            # Wait until content is not "Loading..."
            max_attempts = 15
            for _ in range(max_attempts):
                content = popup.inner_text()
                if content and content.strip() and content.strip() != "Loading...":
                    return content
                time.sleep(1)

            return None

        except PlaywrightTimeout:
            print("   ⏱️ Timeout: Content didn't load")
            return None
        except Exception as e:
            print(f"   ⚠️ Error extracting content: {e}")
            return None