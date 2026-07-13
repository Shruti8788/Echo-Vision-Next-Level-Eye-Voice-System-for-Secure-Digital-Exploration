import time
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class YouTubeShortsController:
    """Controller that maps gestures/voice commands to YouTube Shorts actions."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.driver: Optional[webdriver.Chrome] = None

    def open(self) -> None:
        options = Options()
        options.add_argument("--start-maximized")
        
        # Anti-detection: Make browser look like a real user
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set a real user agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Additional stealth options
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=options)
        
        # Execute script to hide webdriver property
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
        except Exception:
            pass  # CDP might not be available in all Chrome versions
        
        # Additional JavaScript to make it look more human
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            
            window.navigator.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        self.driver.get(self.url)
        time.sleep(3)

    def focus(self) -> None:
        if self.driver:
            self.driver.switch_to.window(self.driver.current_window_handle)

    def _click_first(self, selectors: List[str]) -> bool:
        """Try each CSS selector until one clicks successfully."""
        if not self.driver:
            return False

        for selector in selectors:
            try:
                element = self.driver.find_element("css selector", selector)
                if element.is_displayed():
                    element.click()
                    return True
            except Exception:
                continue
        return False

    def _click_via_script(self, script: str) -> bool:
        if not self.driver:
            return False
        try:
            return bool(self.driver.execute_script(script))
        except Exception:
            return False

    def scroll(self, direction: Optional[str] = "down") -> None:
        self.focus()
        if not self.driver:
            return

        actions = ActionChains(self.driver)
        if direction == "up":
            attempts = [
                lambda: actions.send_keys(Keys.ARROW_UP).perform(),
                lambda: actions.send_keys("k").perform(),
                lambda: actions.send_keys(Keys.PAGE_UP).perform(),
                lambda: self.driver.execute_script(
                    "window.scrollBy({top: -window.innerHeight, behavior: 'instant'});"
                ),
            ]
        else:
            attempts = [
                lambda: actions.send_keys(Keys.ARROW_DOWN).perform(),
                lambda: actions.send_keys("j").perform(),
                lambda: actions.send_keys(Keys.SPACE).perform(),
                lambda: self.driver.execute_script(
                    "window.scrollBy({top: window.innerHeight, behavior: 'instant'});"
                ),
            ]

        for attempt in attempts:
            try:
                attempt()
                time.sleep(0.1)
                break
            except Exception:
                continue

    def like(self) -> None:
        self.focus()
        if self._click_first(
            [
                "ytd-segmented-like-dislike-button-renderer button[aria-pressed='false'][aria-label*='like']",
                "button[aria-label*='Like this video'][aria-pressed='false']",
            ]
        ):
            return

        self._click_via_script(
            """
            const buttons = Array.from(document.querySelectorAll('button'));
            const target = buttons.find(btn => {
                const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                const pressed = btn.getAttribute('aria-pressed');
                return label.includes('like') && (pressed === 'false' || pressed === null);
            });
            if (target) { target.click(); return true; }
            return false;
            """
        )

    def unlike(self) -> None:
        self.focus()
        if self._click_first(
            [
                "ytd-segmented-like-dislike-button-renderer button[aria-pressed='true'][aria-label*='like']",
                "button[aria-label*='Like this video'][aria-pressed='true']",
            ]
        ):
            return

        self._click_via_script(
            """
            const buttons = Array.from(document.querySelectorAll('button'));
            const target = buttons.find(btn => {
                const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                return label.includes('like') && btn.getAttribute('aria-pressed') === 'true';
            });
            if (target) { target.click(); return true; }
            return false;
            """
        )

    def save(self) -> None:
        self.focus()
        if self._click_first(
            [
                "button[aria-label*='Save to playlist'][aria-pressed='false']",
                "button[aria-label='Save']",
            ]
        ):
            return

        self._click_via_script(
            """
            const buttons = Array.from(document.querySelectorAll('button'));
            const target = buttons.find(btn => {
                const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                const pressed = btn.getAttribute('aria-pressed');
                return label.includes('save to playlist') && (pressed === 'false' || pressed === null);
            });
            if (target) { target.click(); return true; }
            return false;
            """
        )

    def unsave(self) -> None:
        self.focus()
        if self._click_first(
            [
                "button[aria-label*='Remove from'][aria-pressed='true']",
                "button[aria-label*='Save to playlist'][aria-pressed='true']",
            ]
        ):
            return

        self._click_via_script(
            """
            const buttons = Array.from(document.querySelectorAll('button'));
            const target = buttons.find(btn => {
                const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                return label.includes('remove from') || 
                       (label.includes('save to playlist') && btn.getAttribute('aria-pressed') === 'true');
            });
            if (target) { target.click(); return true; }
            return false;
            """
        )

    def share(self, friend_name: str) -> None:
        self.focus()
        print(f"Share action not implemented for YouTube Shorts (requested: {friend_name}).")

    def navigate(self, target: str) -> None:
        """Navigate to a specific YouTube tab/section."""
        self.focus()
        if not self.driver:
            return
        
        target_lower = target.lower().strip()
        print(f"📱 Navigating to: {target}")
        
        # Map target names to selectors and URLs
        navigation_map = {
            "home": {
                "selectors": [
                    'a[href="/"]',
                    'a[aria-label="Home"]',
                    'ytd-guide-entry-renderer a[href="/"]',
                    'a[title="Home"]',
                ],
                "url": "https://www.youtube.com/",
            },
            "shorts": {
                "selectors": [
                    'a[href="/shorts"]',
                    'a[aria-label="Shorts"]',
                    'ytd-guide-entry-renderer a[href="/shorts"]',
                    'a[title="Shorts"]',
                ],
                "url": "https://www.youtube.com/shorts",
            },
            "subscriptions": {
                "selectors": [
                    'a[href="/feed/subscriptions"]',
                    'a[aria-label="Subscriptions"]',
                    'ytd-guide-entry-renderer a[href="/feed/subscriptions"]',
                ],
                "url": "https://www.youtube.com/feed/subscriptions",
            },
            "history": {
                "selectors": [
                    'a[href="/feed/history"]',
                    'a[aria-label="History"]',
                    'ytd-guide-entry-renderer a[href="/feed/history"]',
                ],
                "url": "https://www.youtube.com/feed/history",
            },
            "playlists": {
                "selectors": [
                    'a[href*="/playlist"]',
                    'a[aria-label*="Playlist"]',
                    'ytd-guide-entry-renderer a[href*="/playlist"]',
                ],
                "url": "https://www.youtube.com/playlist?list=WL",
            },
            "your videos": {
                "selectors": [
                    'a[href="/studio"]',
                    'a[aria-label*="Your videos"]',
                    'a[href*="/channel"]',
                ],
                "url": "https://studio.youtube.com/",
            },
            "your courses": {
                "selectors": [
                    'a[href*="/courses"]',
                    'a[aria-label*="Courses"]',
                ],
                "url": "https://www.youtube.com/learning",
            },
            "watch later": {
                "selectors": [
                    'a[href*="WL"]',
                    'a[aria-label*="Watch later"]',
                ],
                "url": "https://www.youtube.com/playlist?list=WL",
            },
            "liked videos": {
                "selectors": [
                    'a[href*="LL"]',
                    'a[aria-label*="Liked"]',
                ],
                "url": "https://www.youtube.com/playlist?list=LL",
            },
            "downloads": {
                "selectors": [
                    'a[href*="/offline"]',
                    'a[aria-label*="Download"]',
                ],
                "url": "https://www.youtube.com/feed/downloads",
            },
        }
        
        if target_lower not in navigation_map:
            print(f"✗ Unknown navigation target: {target}")
            return
        
        nav_info = navigation_map[target_lower]
        
        # Try clicking the navigation link first (faster)
        clicked = False
        for selector in nav_info["selectors"]:
            try:
                element = self.driver.find_element("css selector", selector)
                if element.is_displayed():
                    element.click()
                    clicked = True
                    print(f"✓ Clicked {target} navigation link")
                    break
            except Exception:
                continue
        
        # Fallback: Navigate directly via URL
        if not clicked:
            try:
                self.driver.get(nav_info["url"])
                print(f"✓ Navigated to {target} via URL")
            except Exception as e:
                print(f"✗ Navigation failed: {e}")
        
        time.sleep(0.5)  # Wait for page to load


