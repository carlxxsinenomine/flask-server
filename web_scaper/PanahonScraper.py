from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time


class PanahonScraper:
    def __init__(self):
        self.__panahon_url = "https://www.panahon.gov.ph/"
        self.__chrome_options = Options()
        self.__driver = None
        self.__data = {}

    def __setup_driver(self):
        """Initialize Chrome driver with proper options"""
        self.__chrome_options.add_argument("--headless=new")
        self.__chrome_options.add_argument("--window-size=1920,1080")
        self.__chrome_options.add_argument("--no-sandbox")
        self.__chrome_options.add_argument("--disable-dev-shm-usage")
        self.__chrome_options.add_argument("--disable-gpu")
        self.__chrome_options.add_argument("--disable-extensions")
        self.__chrome_options.add_argument("--disable-software-rasterizer")
        self.__chrome_options.add_argument("--disable-background-timer-throttling")
        self.__chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        self.__chrome_options.add_argument("--disable-renderer-backgrounding")
        self.__chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.__chrome_options.add_experimental_option('useAutomationExtension', False)

        try:
            # For local Windows: use regular Chrome
            # For Streamlit Cloud: use CHROMIUM
            import platform
            import os

            if platform.system() == "Windows" or os.path.exists(
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"):
                # Local development - use regular Chrome
                print("🖥️ Running on Windows - using Chrome")
                service = Service(ChromeDriverManager().install())
            else:
                # Streamlit Cloud - use Chromium
                print("☁️ Running on cloud - using Chromium")
                service = Service(
                    ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
                )

            self.__driver = webdriver.Chrome(service=service, options=self.__chrome_options)
            print("✅ Chrome driver initialized successfully")
            return True

        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            self.__driver = None
            return False

    def start_scraping(self, location):
        try:
            # Initialize driver
            if not self.__setup_driver():
                print("Failed to initialize Chrome driver")
                return

            print(f"🌐 Navigating to {self.__panahon_url}")
            self.__driver.get(self.__panahon_url)

            WebDriverWait(self.__driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Page loaded")

            # Open Notification
            print("🔔 Clicking notification button...")
            notification_button = WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.notification-button"))
            )
            notification_button.click()

            # Show button
            show_button = WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable((By.ID, "showSelectedAlertBtn"))
            )
            names = ['Rainfall', 'Thunderstorm', 'Flood', 'Tropical']

            for i in range(4):
                print(f"\n📊 Processing {names[i]}...")
                self.__select_type(index=i)
                show_button.click()
                time.sleep(2)
                self.__search_place(location)

                content = self.__wait_and_extract_content()
                self.__data[names[i]] = content
                print(f"   Result: {'✅ Found' if content else '❌ None'}")

            print(f"\n✅ Scraping complete!")

        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            # Only quit if driver was successfully initialized
            if self.__driver is not None:
                try:
                    self.__driver.quit()
                    print("🔒 Browser closed")
                except Exception as e:
                    print(f"⚠️ Error closing driver: {e}")

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

    def __wait_and_extract_content(self, timeout=15):
        try:
            # Wait for popup to be visible
            time.sleep(2)

            popup = WebDriverWait(self.__driver, timeout).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ol-popup-content"))
            )

            # Wait for content to be loaded
            def content_loaded(driver):
                try:
                    popup_element = driver.find_element(By.CLASS_NAME, "ol-popup-content")
                    text = popup_element.text.strip()
                    return len(text) > 0 and text != "Loading..."
                except:
                    return False

            WebDriverWait(self.__driver, timeout).until(content_loaded)

            content = popup.text
            return content if content else None

        except TimeoutException:
            print("   ⏱️ Timeout: Content didn't load")
            return None
        except Exception as e:
            print(f"   ⚠️ Error extracting content: {e}")
            return None

    def __search_place(self, location_name):
        try:
            search_input = WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='search']"))
            )

            search_input.clear()
            search_input.send_keys(location_name)
            search_input.send_keys(Keys.ENTER)

            time.sleep(3)
        except Exception as e:
            print(f"   ⚠️ Error searching place: {e}")

    def __select_type(self, index=None):
        try:
            select_element = self.__driver.find_element(By.ID, "alertTypeSelect")
            dropdown = Select(select_element)
            dropdown.select_by_index(index=index)
        except Exception as e:
            print(f"   ⚠️ Error selecting type: {e}")