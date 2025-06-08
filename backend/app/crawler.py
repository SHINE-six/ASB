from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import subprocess
import platform
import logging
import asyncio
from app.llm_processor import parse_linkedin_profile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an event loop for async operations
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class LinkedInCrawler:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.driver = self.init_driver()

    def init_driver(self):
        """Initialize WebDriver with fallback options if Chrome fails"""
        try:
        #     # Try Chrome first
        #     return self._init_chrome_driver()
        # except WebDriverException as e:
        #     logger.warning(f"Chrome driver failed: {e}")
        # try:
        #     # Fallback to Firefox if Chrome fails
        #     logger.info("Trying Firefox as fallback...")
            return self._init_firefox_driver()
        except WebDriverException as firefox_error:
            logger.error(f"Firefox driver also failed: {firefox_error}")
            raise Exception("Could not initialize any WebDriver. Please make sure either Chrome or Firefox is installed.")

    def _init_chrome_driver(self):
        """Initialize Chrome WebDriver with proper permissions handling"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Install ChromeDriver
        driver_path = ChromeDriverManager().install()
        
        # Ensure driver is executable
        if platform.system() != "Windows":
            logger.info(f"Setting execute permissions on {driver_path}")
            os.chmod(driver_path, 0o755)
            
        # Check if Chrome is available
        self._check_chrome_installed()
            
        service = Service(driver_path)
        return webdriver.Chrome(service=service, options=options)

    def _init_firefox_driver(self):
        """Initialize Firefox WebDriver as fallback"""
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        
        # Install GeckoDriver
        driver_path = GeckoDriverManager().install()
        
        # Ensure driver is executable
        if platform.system() != "Windows":
            os.chmod(driver_path, 0o755)
            
        service = Service(driver_path)
        return webdriver.Firefox(service=service, options=options)
    
    def _check_chrome_installed(self):
        """Check if Chrome is installed on the system"""
        system = platform.system()
        try:
            if system == "Linux":
                # Check for Chrome or Chromium on Linux
                chrome_exists = subprocess.call(['which', 'google-chrome'], stdout=subprocess.PIPE) == 0 or \
                               subprocess.call(['which', 'chromium-browser'], stdout=subprocess.PIPE) == 0
                if not chrome_exists:
                    logger.warning("Chrome/Chromium not found. Please install Chrome or Chromium.")
            elif system == "Darwin":  # macOS
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                if not os.path.exists(chrome_path):
                    logger.warning(f"Chrome not found at {chrome_path}")
            # Windows check is more complex and less necessary, as Chrome is usually in PATH
        except Exception as e:
            logger.warning(f"Error checking for Chrome: {e}")

    def login(self):
        """Login to LinkedIn with more reliable selectors and better error handling"""
        try:
            logger.info("Navigating to LinkedIn login page")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for username field to be present
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(self.username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Try multiple ways to find the login button
            try:
                # First try: find by type attribute - most reliable
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except NoSuchElementException:
                try:
                    # Second try: less specific XPath
                    login_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'login')]")
                except NoSuchElementException:
                    # Final try: look for any button within the form
                    login_button = self.driver.find_element(By.CSS_SELECTOR, "form button")
            
            login_button.click()
            
            # Wait for login to complete
            logger.info("Waiting for login to complete")
            time.sleep(3)
            
            # Check if login was successful
            if "checkpoint" in self.driver.current_url or "login" in self.driver.current_url:
                logger.error("Login unsuccessful. Check credentials or verify if there's a CAPTCHA.")
                raise Exception("Login failed - still on login page or checkpoint")
                
            logger.info("Login successful")
            
        except (NoSuchElementException, TimeoutException) as e:
            logger.error(f"Login failed: {e}")
            raise Exception(f"Login failed: {e}")

    async def scrape_profile(self, url: str):
        self.driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        try:
            # Extract profile content
            profile_content = soup.get_text()
            
            # strip whitespace and newlines
            profile_content = ' '.join(profile_content.split())
            # Ensure profile content is not empty
            if not profile_content:
                raise ValueError("Profile content is empty")
            
            # Add the profile URL
            # profile_content += f"\nLinkedIn URL: {url}\n"
            
            # return profile_content
            
            # print(f"Profile content: {profile_content}")
            
            # Use the LLM to parse the profile with proper await
            data = await parse_linkedin_profile(profile_content)
            
            # add 'LinkedIn URL' to the data
            data['LinkedIn URL'] = url
            
            # add 'Updated Timestamp' to the data
            data['Updated Timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            if not data:
                raise ValueError("No data found in the profile")
            return data
        except Exception as e:
            logger.error(f"Error scraping profile {url}: {e}")
            return {"error": "Data not found for the profile", "url": url}

    def crawl_profiles(self, profiles: list[str]):
        self.login()
        results = []
        for profile in profiles:
            # Run the async function in the event loop
            data = loop.run_until_complete(self.scrape_profile(profile))
            results.append(data)
            # Add a small delay between requests to avoid rate limiting
            time.sleep(2)
        self.driver.quit()
        return results
