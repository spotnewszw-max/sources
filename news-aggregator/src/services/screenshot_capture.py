"""
Screenshot capture service for social media posts from influencers
Captures tweets, Facebook posts, and Instagram posts from monitored accounts
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
import base64

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScreenshotCapture:
    """Captures screenshots of social media posts from influencers"""
    
    def __init__(self, storage_path: str = "screenshots"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.ocr_available = OCR_AVAILABLE
        self.selenium_available = SELENIUM_AVAILABLE
        
    async def capture_twitter_posts(self, username: str, max_posts: int = 5) -> List[Dict]:
        """
        Capture tweets from a Twitter account using web scraping
        Falls back to Twitter API if available
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available - using API fallback for Twitter")
            return await self._capture_twitter_api(username, max_posts)
        
        posts = []
        try:
            driver = self._setup_chrome_driver()
            driver.get(f"https://twitter.com/{username}")
            
            wait = WebDriverWait(driver, 10)
            # Wait for tweets to load
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//article[@data-testid='tweet']")))
            
            # Scroll to load more tweets
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 1000);")
                await asyncio.sleep(2)
            
            # Extract tweets
            tweet_elements = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            
            for i, tweet_elem in enumerate(tweet_elements[:max_posts]):
                try:
                    # Take screenshot
                    screenshot_path = await self._save_screenshot(
                        tweet_elem, 
                        f"twitter_{username}_{i}_{datetime.now().timestamp()}.png"
                    )
                    
                    # Extract text
                    text = tweet_elem.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                    
                    # Get media if present
                    media_urls = []
                    media_elements = tweet_elem.find_elements(By.XPATH, ".//img[@alt='Image']")
                    for media in media_elements:
                        src = media.get_attribute("src")
                        if src:
                            media_urls.append(src)
                    
                    # Get metadata
                    timestamp = tweet_elem.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                    
                    post_data = {
                        "platform": "twitter",
                        "username": username,
                        "type": "tweet",
                        "text": text,
                        "screenshot_path": str(screenshot_path),
                        "media_urls": media_urls,
                        "timestamp": timestamp,
                        "captured_at": datetime.now().isoformat(),
                        "extracted_text": await self._extract_text_ocr(screenshot_path) if self.ocr_available else None
                    }
                    posts.append(post_data)
                    logger.info(f"Captured tweet from @{username}: {text[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing tweet: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error capturing Twitter posts from @{username}: {e}")
        
        return posts
    
    async def capture_facebook_posts(self, page_id: str, max_posts: int = 5) -> List[Dict]:
        """
        Capture Facebook posts from a page using web scraping
        Falls back to Facebook Graph API if available
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available - using API fallback for Facebook")
            return await self._capture_facebook_api(page_id, max_posts)
        
        posts = []
        try:
            driver = self._setup_chrome_driver()
            driver.get(f"https://www.facebook.com/{page_id}")
            
            wait = WebDriverWait(driver, 10)
            # Wait for posts to load
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='post']")))
            
            # Scroll to load more posts
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 1000);")
                await asyncio.sleep(2)
            
            # Extract posts
            post_elements = driver.find_elements(By.XPATH, "//div[@data-testid='post']")
            
            for i, post_elem in enumerate(post_elements[:max_posts]):
                try:
                    # Take screenshot
                    screenshot_path = await self._save_screenshot(
                        post_elem,
                        f"facebook_{page_id}_{i}_{datetime.now().timestamp()}.png"
                    )
                    
                    # Extract text content
                    text_elements = post_elem.find_elements(By.XPATH, ".//span[@class='x193iq51']")
                    text = " ".join([elem.text for elem in text_elements])
                    
                    # Get media
                    media_urls = []
                    img_elements = post_elem.find_elements(By.TAG_NAME, "img")
                    for img in img_elements:
                        src = img.get_attribute("src")
                        if src and "facebook" in src:
                            media_urls.append(src)
                    
                    post_data = {
                        "platform": "facebook",
                        "page_id": page_id,
                        "type": "post",
                        "text": text,
                        "screenshot_path": str(screenshot_path),
                        "media_urls": media_urls,
                        "captured_at": datetime.now().isoformat(),
                        "extracted_text": await self._extract_text_ocr(screenshot_path) if self.ocr_available else None
                    }
                    posts.append(post_data)
                    logger.info(f"Captured Facebook post from {page_id}: {text[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing Facebook post: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error capturing Facebook posts from {page_id}: {e}")
        
        return posts
    
    async def capture_instagram_posts(self, username: str, max_posts: int = 5) -> List[Dict]:
        """
        Capture Instagram posts from a profile using web scraping
        Note: Instagram has strict anti-scraping measures
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available for Instagram capture")
            return []
        
        posts = []
        try:
            driver = self._setup_chrome_driver()
            driver.get(f"https://www.instagram.com/{username}/")
            
            wait = WebDriverWait(driver, 10)
            # Wait for posts grid to load
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//article//img")))
            
            # Scroll to load more posts
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 1000);")
                await asyncio.sleep(2)
            
            # Extract post links
            post_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            
            for i, link in enumerate(post_links[:max_posts]):
                try:
                    link.click()
                    await asyncio.sleep(2)
                    
                    # Take screenshot of post modal
                    screenshot_path = await self._save_screenshot(
                        driver.find_element(By.XPATH, "//article"),
                        f"instagram_{username}_{i}_{datetime.now().timestamp()}.png"
                    )
                    
                    # Extract caption if visible
                    caption_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'C4VMK')]")
                    caption = " ".join([elem.text for elem in caption_elements])
                    
                    post_data = {
                        "platform": "instagram",
                        "username": username,
                        "type": "post",
                        "text": caption,
                        "screenshot_path": str(screenshot_path),
                        "captured_at": datetime.now().isoformat(),
                        "extracted_text": await self._extract_text_ocr(screenshot_path) if self.ocr_available else None
                    }
                    posts.append(post_data)
                    logger.info(f"Captured Instagram post from @{username}")
                    
                    # Close modal
                    driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]").click()
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing Instagram post: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error capturing Instagram posts from @{username}: {e}")
        
        return posts
    
    async def _save_screenshot(self, element, filename: str) -> Path:
        """Save screenshot of a specific element"""
        screenshot_path = self.storage_path / filename
        try:
            element.screenshot(str(screenshot_path))
            return screenshot_path
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            raise
    
    async def _extract_text_ocr(self, image_path: Path) -> Optional[str]:
        """Extract text from screenshot using OCR"""
        if not self.ocr_available:
            return None
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return None
    
    def _setup_chrome_driver(self):
        """Setup Chrome WebDriver with headless option"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Try to find ChromeDriver
        try:
            driver = webdriver.Chrome(options=options)
        except Exception:
            # Fallback to default path
            driver = webdriver.Chrome(options=options)
        
        return driver
    
    async def _capture_twitter_api(self, username: str, max_posts: int = 5) -> List[Dict]:
        """Fallback: Use Twitter API v2 to get tweets with media"""
        import os
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        if not bearer_token:
            logger.warning("Twitter API token not available")
            return []
        
        posts = []
        try:
            import httpx
            headers = {"Authorization": f"Bearer {bearer_token}"}
            
            # Get user ID
            user_url = f"https://api.twitter.com/2/users/by/username/{username}"
            async with httpx.AsyncClient() as client:
                user_response = await client.get(user_url, headers=headers)
                if user_response.status_code != 200:
                    return []
                
                user_id = user_response.json()["data"]["id"]
                
                # Get tweets with media
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                params = {
                    "max_results": max_posts,
                    "tweet.fields": "created_at,author_id,public_metrics",
                    "expansions": "attachments.media_keys",
                    "media.fields": "url,preview_image_url,type",
                    "user.fields": "username"
                }
                
                tweets_response = await client.get(tweets_url, headers=headers, params=params)
                if tweets_response.status_code != 200:
                    return []
                
                data = tweets_response.json()
                for tweet in data.get("data", []):
                    posts.append({
                        "platform": "twitter",
                        "username": username,
                        "type": "tweet",
                        "text": tweet["text"],
                        "tweet_id": tweet["id"],
                        "created_at": tweet["created_at"],
                        "captured_at": datetime.now().isoformat(),
                        "public_metrics": tweet.get("public_metrics", {})
                    })
        
        except Exception as e:
            logger.error(f"Error with Twitter API: {e}")
        
        return posts
    
    async def _capture_facebook_api(self, page_id: str, max_posts: int = 5) -> List[Dict]:
        """Fallback: Use Facebook Graph API to get posts"""
        import os
        access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        
        if not access_token:
            logger.warning("Facebook API token not available")
            return []
        
        posts = []
        try:
            import httpx
            url = f"https://graph.facebook.com/{page_id}/posts"
            params = {
                "fields": "message,story,created_time,permalink_url,attachments",
                "limit": max_posts,
                "access_token": access_token
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    return []
                
                data = response.json()
                for post in data.get("data", []):
                    posts.append({
                        "platform": "facebook",
                        "page_id": page_id,
                        "type": "post",
                        "text": post.get("message") or post.get("story", ""),
                        "post_id": post["id"],
                        "created_at": post.get("created_time"),
                        "permalink": post.get("permalink_url"),
                        "captured_at": datetime.now().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"Error with Facebook API: {e}")
        
        return posts


class SocialMediaMonitor:
    """Monitor multiple influencers across platforms"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.capture = ScreenshotCapture()
        self.config = self._load_config(config_path) if config_path else {}
    
    def _load_config(self, config_path: str) -> Dict:
        """Load influencers to monitor from config"""
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config.get("social_media", {}).get("influencers", {})
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def capture_all_posts(self) -> Dict:
        """Capture posts from all configured influencers"""
        all_posts = {
            "twitter": [],
            "facebook": [],
            "instagram": []
        }
        
        # Capture Twitter posts
        twitter_influencers = self.config.get("twitter", [])
        for username in twitter_influencers:
            posts = await self.capture.capture_twitter_posts(username)
            all_posts["twitter"].extend(posts)
        
        # Capture Facebook posts
        facebook_pages = self.config.get("facebook", [])
        for page_id in facebook_pages:
            posts = await self.capture.capture_facebook_posts(page_id)
            all_posts["facebook"].extend(posts)
        
        # Capture Instagram posts
        instagram_accounts = self.config.get("instagram", [])
        for username in instagram_accounts:
            posts = await self.capture.capture_instagram_posts(username)
            all_posts["instagram"].extend(posts)
        
        return all_posts
    
    async def monitor_influencers(self, interval_minutes: int = 30):
        """Continuously monitor influencers at specified interval"""
        while True:
            logger.info("Starting influencer monitoring cycle...")
            posts = await self.capture_all_posts()
            logger.info(f"Captured {sum(len(v) for v in posts.values())} total posts")
            
            await asyncio.sleep(interval_minutes * 60)