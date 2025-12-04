from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import platform


class PanahonScraperPlaywright:
    """Playwright-based scraper - more reliable for cloud deployment"""

    def __init__(self):
        self.__panahon_url = "https://www.panahon.gov.ph/"
        self.__data = {}

    def start_scraping(self, location):
        browser = None
        context = None
        try:
            with sync_playwright() as p:
                print("🚀 Launching browser...")

                # Different args for Windows vs Linux
                launch_args = [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]

                # Only add --single-process on Linux (for Railway)
                if platform.system() != "Windows":
                    launch_args.append('--single-process')
                    print("🐧 Running on Linux/Cloud")
                else:
                    print("🪟 Running on Windows")

                browser = p.chromium.launch(
                    headless=True,
                    args=launch_args
                )

                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()

                print(f"🌐 Navigating to {self.__panahon_url}")
                page.goto(self.__panahon_url, wait_until="networkidle", timeout=60000)
                print("✅ Page loaded")

                # Click notification button
                print("🔔 Clicking notification button...")
                page.click("button.notification-button", timeout=10000)

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
                    search_input = page.locator("input[placeholder*='Search'], input[type='search']").first
                    search_input.clear()
                    search_input.fill(location)
                    search_input.press("Enter")
                    time.sleep(3)

                    # Extract content
                    content = self.__wait_and_extract_content(page)
                    self.__data[names[i]] = content
                    print(f"   Result: {'✅ Found' if content else '❌ None'}")

                print(f"\n✅ Scraping complete!")

        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            # Proper cleanup
            try:
                if context:
                    context.close()
                if browser:
                    browser.close()
                print("🔒 Browser closed")
            except:
                pass

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

            # Get popup content
            popup = page.locator(".ol-popup-content").first

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

