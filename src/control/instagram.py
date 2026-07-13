import time
from typing import Optional
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class InstagramController:
    def __init__(self, url: str) -> None:
        self.url = url
        self.driver: Optional[webdriver.Chrome] = None

    def open(self) -> None:
        options = Options()
        options.add_argument("--start-maximized")
        
      
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
       
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Chrome(options=options)
        

        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
        except Exception:
            pass  
        
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
        
        self.driver.switch_to.window(self.driver.current_window_handle)

    def _click_first(self, selectors: list) -> bool:
        """Try each selector until one clicks successfully."""
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = self.driver.find_element("xpath", selector)
                else:
                    element = self.driver.find_element("css selector", selector)
                if element.is_displayed():
                    element.click()
                    return True
            except:
                continue
        return False

    def scroll(self, direction: Optional[str] = "down") -> None:
        self.focus()
        
        if direction == "up":
            print(f"SCROLLING TO PREVIOUS REEL (MANDATORY)!")
            scroll_direction = "up"
            
            methods_tried = 0
            
        
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ARROW_UP).perform()
                print("Sent ARROW_UP key")
                time.sleep(0.2)
              
                actions.send_keys(Keys.ARROW_UP).perform()
                print("Sent ARROW_UP key (second time for reliability)")
                time.sleep(0.3)
                methods_tried += 1
            except Exception as e:
                print(f"Arrow key error: {e}")
            
          
            try:
                self.driver.execute_script("""
                    // Scroll up immediately and multiple times for reliability
                    window.scrollBy({
                        top: -window.innerHeight,
                        behavior: 'auto'
                    });
                    // Also try Page Up key
                    window.scrollBy(0, -window.innerHeight);
                """)
                print("Used JavaScript scroll up (multiple attempts)")
                time.sleep(0.2)
                methods_tried += 1
            except Exception as e:
                print(f"JavaScript scroll error: {e}")
            

            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.PAGE_UP).perform()
                print("Sent PAGE_UP key")
                time.sleep(0.3)
                methods_tried += 1
            except Exception as e:
                print(f"Page Up key error: {e}")
            
    
            try:
                self.driver.execute_script("""
                    // Simulate swipe up (swipe from bottom to top)
                    var startY = window.innerHeight * 0.8;
                    var endY = window.innerHeight * 0.2;
                    
                    // Create mouse events to simulate swipe
                    var startEvent = new MouseEvent('mousedown', {
                        bubbles: true,
                        cancelable: true,
                        clientX: window.innerWidth / 2,
                        clientY: startY
                    });
                    var moveEvent = new MouseEvent('mousemove', {
                        bubbles: true,
                        cancelable: true,
                        clientX: window.innerWidth / 2,
                        clientY: endY
                    });
                    var endEvent = new MouseEvent('mouseup', {
                        bubbles: true,
                        cancelable: true,
                        clientX: window.innerWidth / 2,
                        clientY: endY
                    });
                    
                    var target = document.elementFromPoint(window.innerWidth / 2, startY);
                    if (target) {
                        target.dispatchEvent(startEvent);
                        setTimeout(() => {
                            target.dispatchEvent(moveEvent);
                            setTimeout(() => {
                                target.dispatchEvent(endEvent);
                            }, 50);
                        }, 50);
                    }
                """)
                print("Used touch swipe up simulation")
                time.sleep(0.4)
                methods_tried += 1
            except Exception as e:
                print(f"Touch simulation error: {e}")
            
            print(f"Previous reel scroll executed with {methods_tried} methods - should be playing now!")
            
        else:
            print(f"SCROLLING TO NEXT REEL!")
            scroll_direction = "down"
            success = False
            
            # Method 1: Arrow keys (works best for Instagram Reels)
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ARROW_DOWN).perform()
                print("Sent ARROW_DOWN key")
                time.sleep(0.3)
                success = True
            except Exception as e:
                print(f"Arrow key error: {e}")
            
            # Method 2: Space key (alternative for Instagram)
            if not success:
                try:
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.SPACE).perform()
                    print("Sent SPACE key")
                    time.sleep(0.3)
                    success = True
                except Exception as e:
                    print(f"Space key error: {e}")
            
            # Method 3: JavaScript scroll (fallback)
            if not success:
                try:
                    self.driver.execute_script("""
                        // Scroll by viewport height for Instagram Reels
                        window.scrollBy({
                            top: window.innerHeight,
                            behavior: 'smooth'
                        });
                    """)
                    print("Used JavaScript smooth scroll down")
                    time.sleep(0.5)
                    success = True
                except Exception as e:
                    print(f"JavaScript scroll error: {e}")
            
            if success:
                print(f"Scroll {scroll_direction} command sent successfully!")
            else:
                print(f"All scroll {scroll_direction} methods failed!")

    def like(self) -> None:
        self.focus()
        print("LIKING POST!")
        
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Method 1: Try to find and click the heart/like button directly
            try:
                # Look for various like button selectors
                like_selectors = [
                    "svg[aria-label='Like']",
                    "svg[aria-label*='Like']", 
                    "[data-testid='like-button']",
                    "button[aria-label='Like']",
                    "button[aria-label*='Like']"
                ]
                
                for selector in like_selectors:
                    try:
                        like_button = self.driver.find_element("css selector", selector)
                        if like_button and like_button.is_displayed():
                            like_button.click()
                            print(f"Clicked like button with selector: {selector}")
                            return
                    except:
                        continue
            except Exception as e:
                print(f"Like button search error: {e}")
            
            # Method 2: Double-click on video area
            try:
                video = self.driver.find_element("tag name", "video")
                if video:
                    actions = ActionChains(self.driver)
                    actions.move_to_element(video).double_click().perform()
                    print("Double-clicked on video element")
                    return
            except Exception as e:
                print(f"Video double-click error: {e}")
            
            # Method 3: Double-click at center of screen
            try:
                size = self.driver.get_window_size()
                center_x = size['width'] // 2
                center_y = size['height'] // 2
                
                actions = ActionChains(self.driver)
                actions.move_by_offset(center_x, center_y).double_click().perform()
                print("Double-clicked at center of screen")
                return
            except Exception as e:
                print(f"Center double-click error: {e}")
                
        except Exception as e:
            print(f"Like error: {e}")
            # EMERGENCY FALLBACK: JavaScript double-click
            try:
                self.driver.execute_script("""
                    // Try to find and click like button first
                    var likeButton = document.querySelector('svg[aria-label*="Like"]') || 
                                   document.querySelector('[data-testid="like-button"]');
                    if (likeButton) {
                        likeButton.click();
                        console.log('Clicked like button via JS');
                    } else {
                        // Fallback to double-click
                        var event = new MouseEvent('dblclick', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: window.innerWidth / 2,
                            clientY: window.innerHeight / 2
                        });
                        document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2).dispatchEvent(event);
                        console.log('Double-click via JS');
                    }
                """)
                print("Used emergency JavaScript like")
            except Exception as e2:
                print(f"Emergency like failed: {e2}")

    def unlike(self) -> None:
        self.focus()
        print("UNLIKING POST (FAST)!")
        
        # Use multiple methods simultaneously for fast, reliable unliking
        methods_tried = 0
        
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            # Method 1: JavaScript - Fastest method, try first
            try:
                self.driver.execute_script("""
                    // Try multiple selectors for unlike button
                    var unlikeButton = document.querySelector('svg[aria-label*="Unlike"]') || 
                                     document.querySelector('[aria-label*="Unlike"]') ||
                                     document.querySelector('[data-testid="unlike-button"]') ||
                                     document.querySelector('svg[fill="rgb(255, 48, 64)"]') ||
                                     document.querySelector('svg[fill="#ff3040"]');
                    
                    if (unlikeButton) {
                        unlikeButton.click();
                        console.log('Clicked unlike button via JS');
                        return true;
                    }
                    
                    // Try like button if it's filled (already liked)
                    var likeButtons = document.querySelectorAll('svg[aria-label*="Like"]');
                    for (var i = 0; i < likeButtons.length; i++) {
                        var btn = likeButtons[i];
                        var pathEl = btn.querySelector('path');
                        var fill = btn.getAttribute('fill') || (pathEl ? pathEl.getAttribute('fill') : '') || '';
                        if (fill.includes('255') || fill.includes('ff3040') || fill.includes('#f00')) {
                            btn.click();
                            console.log('Clicked filled like button to unlike via JS');
                            return true;
                        }
                    }
                    
                    // Last resort: find any red/filled heart and click
                    var allSvgs = document.querySelectorAll('svg');
                    for (var i = 0; i < allSvgs.length; i++) {
                        var svg = allSvgs[i];
                        try {
                            var style = window.getComputedStyle(svg);
                            var pathEl = svg.querySelector('path');
                            var fill = svg.getAttribute('fill') || (pathEl ? pathEl.getAttribute('fill') : '') || '';
                            if ((fill.includes('255') || fill.includes('ff3040') || (style.color && style.color.includes('rgb(255')))) {
                                svg.click();
                                console.log('Clicked red SVG element via JS');
                                return true;
                            }
                        } catch(e) {
                            continue;
                        }
                    }
                    return false;
                """)
                print("Used JavaScript unlike (fast method)")
                time.sleep(0.1)
                methods_tried += 1
            except Exception as e:
                print(f"JavaScript unlike error: {e}")
            
            # Method 2: Try to find and click the unlike button directly (Selenium)
            try:
                unlike_selectors = [
                    "svg[aria-label='Unlike']",
                    "svg[aria-label*='Unlike']", 
                    "[aria-label*='Unlike']",
                    "[data-testid='unlike-button']",
                    "button[aria-label='Unlike']",
                    "button[aria-label*='Unlike']",
                    "svg[fill='rgb(255, 48, 64)']",
                    "svg[fill='#ff3040']"
                ]
                
                for selector in unlike_selectors:
                    try:
                        elements = self.driver.find_elements("css selector", selector)
                        for element in elements:
                            if element.is_displayed():
                                element.click()
                                print(f"Clicked unlike button with selector: {selector}")
                                time.sleep(0.1)
                                methods_tried += 1
                                return
                    except:
                        continue
            except Exception as e:
                print(f"Unlike button search error: {e}")
            
            # Method 3: Try like button if already liked (toggles)
            try:
                like_selectors = [
                    "svg[aria-label='Like']",
                    "svg[aria-label*='Like']", 
                    "[data-testid='like-button']",
                    "button[aria-label='Like']",
                    "button[aria-label*='Like']"
                ]
                
                for selector in like_selectors:
                    try:
                        elements = self.driver.find_elements("css selector", selector)
                        for element in elements:
                            if element.is_displayed():
                                # Check if filled/liked
                                try:
                                    fill_attr = element.get_attribute('fill')
                                    inner_html = element.get_attribute('outerHTML')
                                    if fill_attr and ('255' in fill_attr or 'ff3040' in fill_attr) or 'rgb(255' in inner_html:
                                        element.click()
                                        print(f"Clicked filled like button to unlike: {selector}")
                                        time.sleep(0.1)
                                        methods_tried += 1
                                        return
                                except:
                                    # Try clicking anyway (might toggle)
                                    element.click()
                                    print(f"Clicked like button (toggle): {selector}")
                                    time.sleep(0.1)
                                    methods_tried += 1
                                    return
                    except:
                        continue
            except Exception as e:
                print(f"Like button toggle error: {e}")
            
            # Method 4: Double-click on video area (toggles like/unlike)
            try:
                videos = self.driver.find_elements("tag name", "video")
                for video in videos:
                    if video.is_displayed():
                        actions = ActionChains(self.driver)
                        actions.move_to_element(video).double_click().perform()
                        print("Double-clicked on video element to toggle unlike")
                        time.sleep(0.1)
                        methods_tried += 1
                        return
            except Exception as e:
                print(f"Video double-click error: {e}")
                
        except Exception as e:
            print(f"Unlike error: {e}")
        
        if methods_tried > 0:
            print(f"Unlike executed with {methods_tried} method(s) - should be unliked now!")
        else:
            print("WARNING: Unlike methods failed - trying emergency fallback")
            # Final emergency fallback
            try:
                self.driver.execute_script("""
                    // Emergency: click on center of screen where like button usually is
                    var event = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        clientX: window.innerWidth / 2,
                        clientY: window.innerHeight / 2
                    });
                    document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2).dispatchEvent(event);
                """)
                print("Used emergency center click")
            except Exception as e2:
                print(f"Emergency unlike failed: {e2}")

    def save(self) -> None:
        self.focus()
        print("SAVING REEL!")
        time.sleep(0.1)  # Small delay for stability
        
        # Try ALL methods aggressively - don't skip any buttons
        methods_tried = 0
        
        # Method 1: JavaScript - Find ANY button with save/bookmark in aria-label and CLICK IT
        try:
            result = self.driver.execute_script("""
                // AGGRESSIVE: Find and click ANY save/bookmark button, regardless of state
                var clicked = false;
                
                // Try all buttons with save/bookmark in aria-label
                var allButtons = document.querySelectorAll('button, [role="button"], a, div[role="button"]');
                for (var i = 0; i < allButtons.length; i++) {
                    var btn = allButtons[i];
                    var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                    if (ariaLabel.includes('save') || ariaLabel.includes('bookmark')) {
                        var rect = btn.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            btn.click();
                            console.log('Clicked save button: ' + ariaLabel);
                            clicked = true;
                            break;
                        }
                    }
                }
                
                if (!clicked) {
                    // Try SVG elements with save/bookmark
                    var svgs = document.querySelectorAll('svg');
                    for (var i = 0; i < svgs.length; i++) {
                        var svg = svgs[i];
                        var ariaLabel = (svg.getAttribute('aria-label') || '').toLowerCase();
                        if (ariaLabel.includes('save') || ariaLabel.includes('bookmark')) {
                            var parent = svg.closest('button') || svg.closest('[role="button"]') || svg.parentElement;
                            if (parent) {
                                parent.click();
                                console.log('Clicked save via SVG parent');
                                clicked = true;
                                break;
                            } else {
                                svg.click();
                                console.log('Clicked save SVG directly');
                                clicked = true;
                                break;
                            }
                        }
                    }
                }
                
                if (!clicked) {
                    // Position-based: Click 2nd button on right side (save is usually 2nd after like)
                    var rightButtons = Array.from(document.querySelectorAll('button')).filter(function(btn) {
                        var rect = btn.getBoundingClientRect();
                        return rect.width > 0 && rect.height > 0 && 
                               rect.right > window.innerWidth * 0.75 &&
                               rect.top < window.innerHeight * 0.4;
                    }).sort(function(a, b) {
                        return a.getBoundingClientRect().top - b.getBoundingClientRect().top;
                    });
                    
                    if (rightButtons.length >= 2) {
                        rightButtons[1].click();
                        console.log('Clicked 2nd button on right (save position)');
                        clicked = true;
                    }
                }
                
                return clicked;
            """)
            
            if result:
                print("✓ Save clicked via JavaScript")
                methods_tried += 1
                time.sleep(0.15)
                return
        except Exception as e:
            print(f"JS save error: {e}")
        
        # Method 2: Selenium - Try ALL possible selectors
        save_selectors = [
            "button[aria-label*='Save']",
            "button[aria-label*='save']", 
            "button[aria-label*='Bookmark']",
            "button[aria-label*='bookmark']",
            "[aria-label*='Save']",
            "[aria-label*='save']",
            "[aria-label*='Bookmark']",
            "[aria-label*='bookmark']",
            "svg[aria-label*='Save']",
            "svg[aria-label*='save']",
            "svg[aria-label*='Bookmark']",
            "svg[aria-label*='bookmark']",
        ]
        
        for selector in save_selectors:
            try:
                elements = self.driver.find_elements("css selector", selector)
                for element in elements:
                    try:
                        if element.is_displayed():
                            # Find parent button if element is SVG
                            click_target = element
                            if element.tag_name.lower() == 'svg':
                                try:
                                    parent = element.find_element("xpath", "./ancestor::button[1]")
                                    click_target = parent
                                except:
                                    pass
                            
                            click_target.click()
                            print(f"✓ Clicked save: {selector}")
                            methods_tried += 1
                            time.sleep(0.15)
                            return
                    except:
                        continue
            except:
                continue
        
        # Method 3: Position-based click (save button is usually at ~85% width, 25% height)
        try:
            size = self.driver.get_window_size()
            save_x = int(size['width'] * 0.85)
            save_y = int(size['height'] * 0.25)
            
            self.driver.execute_script(f"""
                var element = document.elementFromPoint({save_x}, {save_y});
                if (element) {{
                    var btn = element.closest('button') || element.closest('[role="button"]') || element;
                    btn.click();
                    console.log('Position click at ({save_x}, {save_y})');
                }}
            """)
            print("✓ Position-based save click")
            methods_tried += 1
            time.sleep(0.15)
            return
        except Exception as e:
            print(f"Position click error: {e}")
        
        print(f"✗ Save failed after {methods_tried} methods")

    def unsave(self) -> None:
        self.focus()
        print("UNSAVING REEL!")
        time.sleep(0.1)
        
        # SIMPLE STRATEGY: Just click ANY save button - Instagram toggles it!
        # No need to check if filled - just click it and it will unsave if already saved
        
        # Method 1: JavaScript - Find and click ANY save/bookmark button immediately
        try:
            result = self.driver.execute_script("""
                // Find ANY button with save/bookmark/unsave and CLICK IT IMMEDIATELY
                var allButtons = document.querySelectorAll('button, [role="button"], a, div[role="button"]');
                
                for (var i = 0; i < allButtons.length; i++) {
                    var btn = allButtons[i];
                    var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                    if (ariaLabel.includes('save') || ariaLabel.includes('bookmark') || ariaLabel.includes('unsave')) {
                        var rect = btn.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && rect.top >= 0) {
                            btn.click();
                            console.log('CLICKED SAVE BUTTON: ' + ariaLabel);
                            return true;
                        }
                    }
                }
                
                // Try SVG elements
                var svgs = document.querySelectorAll('svg');
                for (var i = 0; i < svgs.length; i++) {
                    var svg = svgs[i];
                    var ariaLabel = (svg.getAttribute('aria-label') || '').toLowerCase();
                    if (ariaLabel.includes('save') || ariaLabel.includes('bookmark') || ariaLabel.includes('unsave')) {
                        var parent = svg.closest('button') || svg.closest('[role="button"]') || svg.parentElement;
                        if (parent) {
                            parent.click();
                            console.log('CLICKED SAVE VIA SVG: ' + ariaLabel);
                            return true;
                        }
                    }
                }
                
                // Position-based: Click 2nd button on right (save button position)
                var rightButtons = Array.from(document.querySelectorAll('button')).filter(function(btn) {
                    var rect = btn.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0 && 
                           rect.right > window.innerWidth * 0.75 &&
                           rect.top < window.innerHeight * 0.4 &&
                           rect.top >= 0;
                }).sort(function(a, b) {
                    return a.getBoundingClientRect().top - b.getBoundingClientRect().top;
                });
                
                if (rightButtons.length >= 2) {
                    rightButtons[1].click();
                    console.log('CLICKED 2ND BUTTON (POSITION)');
                    return true;
                }
                
                return false;
            """)
            
            if result:
                print("✓ Unsave clicked via JavaScript")
                time.sleep(0.2)
                return
        except Exception as e:
            print(f"JS unsave error: {e}")
        
        # Method 2: Selenium - Try ALL selectors and click FIRST one found
        unsave_selectors = [
            "button[aria-label*='Unsave']",
            "button[aria-label*='unsave']",
            "button[aria-label*='Save']",
            "button[aria-label*='save']",
            "button[aria-label*='Bookmark']",
            "button[aria-label*='bookmark']",
            "[aria-label*='Unsave']",
            "[aria-label*='unsave']",
            "[aria-label*='Save']",
            "[aria-label*='save']",
            "[aria-label*='Bookmark']",
            "[aria-label*='bookmark']",
            "svg[aria-label*='Save']",
            "svg[aria-label*='save']",
            "svg[aria-label*='Unsave']",
            "svg[aria-label*='unsave']",
        ]
        
        for selector in unsave_selectors:
            try:
                elements = self.driver.find_elements("css selector", selector)
                for element in elements:
                    try:
                        if element.is_displayed():
                            # If it's an SVG, find parent button
                            click_target = element
                            if element.tag_name.lower() == 'svg':
                                try:
                                    parent = element.find_element("xpath", "./ancestor::button[1]")
                                    click_target = parent
                                except:
                                    pass
                            
                            click_target.click()
                            print(f"✓ Clicked unsave: {selector}")
                            time.sleep(0.2)
                            return
                    except Exception as e:
                        print(f"Click error with {selector}: {e}")
                        continue
            except:
                continue
        
        # Method 3: Position-based click (MANDATORY FALLBACK)
        try:
            size = self.driver.get_window_size()
            save_x = int(size['width'] * 0.85)
            save_y = int(size['height'] * 0.25)
            
            # Try multiple positions around save button area
            positions = [
                (save_x, save_y),
                (save_x - 20, save_y),
                (save_x + 20, save_y),
                (save_x, save_y - 20),
                (save_x, save_y + 20),
            ]
            
            for pos_x, pos_y in positions:
                try:
                    self.driver.execute_script(f"""
                        var element = document.elementFromPoint({pos_x}, {pos_y});
                        if (element) {{
                            var btn = element.closest('button') || element.closest('[role="button"]') || element;
                            if (btn && btn.click) {{
                                btn.click();
                                console.log('Position click at ({pos_x}, {pos_y})');
                                return true;
                            }}
                        }}
                        return false;
                    """)
                    print(f"✓ Position click at ({pos_x}, {pos_y})")
                    time.sleep(0.2)
                    return
                except:
                    continue
        except Exception as e:
            print(f"Position click error: {e}")
        
        print("✗ UNSAVE FAILED - tried all methods")

    def share(self, friend_name: str) -> None:
        """Fast and reliable share function - optimized for speed."""
        self.focus()
        if not friend_name:
            print("SHARE: No recipient provided")
            return

        friend_name = friend_name.strip()
        print(f"📤 SHARING TO: '{friend_name}'")

        try:
            # Step 1: Click Share button (FAST - JavaScript)
            share_clicked = self.driver.execute_script("""
            const allEls = Array.from(document.querySelectorAll('button, svg, [role="button"]'));
            for (const el of allEls) {
                if (el.offsetParent === null) continue;
                const label = (el.getAttribute('aria-label') || '').toLowerCase();
                if (label.includes('share') || label.includes('send')) {
                    const clickTarget = el.closest('button') || el.parentElement || el;
                    if (clickTarget && typeof clickTarget.click === 'function') {
                        clickTarget.click();
                        return true;
                    } else if (el.dispatchEvent) {
                        const clickEvent = new MouseEvent('click', {bubbles: true, cancelable: true});
                        el.dispatchEvent(clickEvent);
                        return true;
                    }
                }
            }
            return false;
        """)
            
            if not share_clicked:
                # Fallback: Selenium
                share_clicked = self._click_first([
                    "button[aria-label*='Share']",
                    "svg[aria-label*='Share']",
                ])
            
            if not share_clicked:
                print("✗ Could not open share dialog")
                return
            
            time.sleep(0.3)  # Minimal wait
            
            # Step 2: Find search box and type (FAST)
            search_box = None
            for selector in ["input[placeholder*='Search']", "input[aria-label*='Search']", "input[type='text']"]:
                try:
                    search_box = self.driver.find_element("css selector", selector)
                    if search_box.is_displayed():
                        break
                except:
                    continue
            
            if not search_box:
                print("✗ Could not find search box")
                return
            
            # Type friend name
            search_box.clear()
            search_box.send_keys(friend_name)
            print(f"   Typed '{friend_name}', waiting for suggestions...")
            time.sleep(0.8)  # Wait longer for suggestions to load
            
            # Step 3: Click friend - PRIORITIZE FOLLOWED ACCOUNTS ONLY
            friend_name_lower = friend_name.lower()
            friend_name_escaped = friend_name_lower.replace("'", "\\'").replace('"', '\\"')
            
            print(f"   Searching for '{friend_name}' in your following list...")
            
            # Try multiple times with different selectors - PRIORITIZE FOLLOWED ACCOUNTS
            friend_clicked = False
            for attempt in range(3):
                friend_clicked = self.driver.execute_script(f"""
                    const name = '{friend_name_escaped}';
                    const nameWords = name.split(' ');
                    
                    // Get all clickable user items
                    const allItems = Array.from(document.querySelectorAll(
                        'div[role="button"], div[class*="user" i], div[class*="User"], div[class*="contact" i], a[role="button"]'
                    ));
                    
                    // Priority 1: Exact username match in followed accounts (first 20 items are usually followed)
                    let bestMatch = null;
                    let bestScore = 0;
                    
                    for (let i = 0; i < allItems.length; i++) {{
                        const item = allItems[i];
                        if (item.offsetParent === null) continue;
                        
                        const fullText = (item.textContent || item.innerText || '').toLowerCase();
                        const itemText = fullText.trim();
                        
                        if (itemText.length === 0 || itemText.length > 150) continue;
                        
                        // Check if this is a followed account (usually in first section)
                        const isInFirstSection = i < 20;
                        const hasFollowingIndicator = fullText.includes('following') || 
                                                      fullText.includes('follows you') ||
                                                      item.querySelector('[class*="following" i]') !== null;
                        
                        // Calculate match score
                        let score = 0;
                        let isExactMatch = false;
                        
                        // Exact username match (highest priority)
                        if (itemText === name || itemText.startsWith(name + ' ') || itemText.endsWith(' ' + name)) {{
                            score = 100;
                            isExactMatch = true;
                        }}
                        // Contains full name
                        else if (itemText.includes(name)) {{
                            score = 50;
                        }}
                        // Contains all words from name
                        else if (nameWords.length > 1 && nameWords.every(word => itemText.includes(word))) {{
                            score = 30;
                        }}
                        // Contains first word
                        else if (nameWords.length > 0 && itemText.includes(nameWords[0])) {{
                            score = 10;
                        }}
                        
                        // Boost score if it's a followed account
                        if (isInFirstSection || hasFollowingIndicator) {{
                            score += 50;
                        }}
                        
                        // Penalize if it's clearly not a friend (has "Follow" button, is in suggested section)
                        if (fullText.includes('follow') && !hasFollowingIndicator && i > 20) {{
                            score -= 30;
                        }}
                        
                        if (score > bestScore) {{
                            bestScore = score;
                            bestMatch = item;
                        }}
                    }}
                    
                    // Only click if:
                    // 1. Exact match (score >= 100) - always allow
                    // 2. Partial match (50+) + followed account indicator (score >= 80)
                    // This ensures we only select accounts that are either exact matches or clearly followed accounts
                    const isExactMatch = bestScore >= 100;
                    const isFollowedMatch = bestScore >= 80 && bestScore < 100;
                    
                    if (bestMatch && (isExactMatch || isFollowedMatch)) {{
                        try {{
                            const clickTarget = bestMatch.closest('button') || bestMatch.closest('[role="button"]') || bestMatch;
                            if (typeof clickTarget.click === 'function') {{
                                clickTarget.click();
                                return {{success: true, score: bestScore, isExact: bestScore >= 100}};
                            }}
                            const clickEvent = new MouseEvent('click', {{bubbles: true, cancelable: true}});
                            bestMatch.dispatchEvent(clickEvent);
                            return {{success: true, score: bestScore, isExact: bestScore >= 100}};
                        }} catch(e) {{
                            return {{success: false, error: e.message}};
                        }}
                    }}
                    
                    return {{success: false, reason: 'No suitable match found'}};
                """)
                
                # Check if result is a dict with success flag
                if isinstance(friend_clicked, dict):
                    if friend_clicked.get('success'):
                        score = friend_clicked.get('score', 0)
                        is_exact = friend_clicked.get('isExact', False)
                        if is_exact:
                            print(f"   ✓ Exact match found! Friend '{friend_name}' selected (score: {score})")
                        else:
                            print(f"   ✓ Friend '{friend_name}' selected (score: {score})")
                        friend_clicked = True
                        break
                    else:
                        friend_clicked = False
                elif friend_clicked:
                    print(f"   ✓ Friend '{friend_name}' selected!")
                    break
                time.sleep(0.2)
            
            if not friend_clicked:
                print(f"   ⚠ Friend '{friend_name}' not found in your following list.")
                print(f"   Please make sure:")
                print(f"   1. You follow this account")
                print(f"   2. The name matches exactly (case-insensitive)")
                print(f"   3. The account appears in the share suggestions")
                print(f"   Trying Enter key as last resort (may select wrong account)...")
                # Only try Enter if user explicitly wants to risk it
                # For safety, we'll skip auto-sending if friend not found
                search_box.send_keys(Keys.ENTER)
                time.sleep(0.3)
                print(f"   ⚠ WARNING: Friend not verified. Please check the selected account before sending!")
            
            # Verify friend was selected correctly
            if friend_clicked:
                print("   Verifying selected account is in your following list...")
                time.sleep(0.3)
                verification = self.driver.execute_script("""
                    // Check if selected account shows "Following" or is in first section
                    const selectedItems = Array.from(document.querySelectorAll('div[role="button"], div[class*="user" i]'));
                    for (const item of selectedItems) {
                        if (item.offsetParent === null) continue;
                        const text = (item.textContent || '').toLowerCase();
                        // Check if this item is selected (has active/selected class or is highlighted)
                        const isSelected = item.getAttribute('aria-selected') === 'true' ||
                                          item.classList.toString().toLowerCase().includes('selected') ||
                                          item.classList.toString().toLowerCase().includes('active') ||
                                          item.style.backgroundColor !== '' ||
                                          window.getComputedStyle(item).backgroundColor !== 'rgba(0, 0, 0, 0)';
                        
                        if (isSelected) {
                            // Check if it's a followed account
                            const hasFollowing = text.includes('following') || 
                                                text.includes('follows you') ||
                                                item.querySelector('[class*="following" i]') !== null;
                            return {isSelected: true, isFollowed: hasFollowing, text: text.substring(0, 50)};
                        }
                    }
                    return {isSelected: false, isFollowed: false};
                """)
                
                if isinstance(verification, dict) and verification.get('isSelected'):
                    if verification.get('isFollowed'):
                        print(f"   ✓ Verified: Selected account is in your following list")
                    else:
                        print(f"   ⚠ WARNING: Selected account may not be in your following list!")
                        print(f"   Account text: {verification.get('text', 'unknown')}")
                        print(f"   Proceeding with caution...")
            
            # Step 4: Click Send - MORE AGGRESSIVE with retries
            print("   Looking for Send button...")
            time.sleep(0.4)  # Wait for friend selection to register
            
            send_clicked = False
            for attempt in range(5):  # Try up to 5 times
                send_clicked = self.driver.execute_script("""
                    // Try multiple ways to find Send button
                    const allButtons = Array.from(document.querySelectorAll('button, [role="button"]'));
                    
                    // Method 1: Exact text match
                    let sendBtn = allButtons.find(btn => {
                        const text = (btn.textContent || '').trim().toLowerCase();
                        return text === 'send' && btn.offsetParent !== null;
                    });
                    
                    // Method 2: Aria label
                    if (!sendBtn) {
                        sendBtn = allButtons.find(btn => {
                            const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                            return label.includes('send') && btn.offsetParent !== null;
                        });
                    }
                    
                    // Method 3: Contains "Send" in text
                    if (!sendBtn) {
                        sendBtn = allButtons.find(btn => {
                            const text = (btn.textContent || '').trim().toLowerCase();
                            return text.includes('send') && btn.offsetParent !== null && text.length < 10;
                        });
                    }
                    
                    if (sendBtn) {
                        try {
                            if (typeof sendBtn.click === 'function') {
                                sendBtn.click();
                                return true;
                            } else {
                                const clickEvent = new MouseEvent('click', {bubbles: true, cancelable: true});
                                sendBtn.dispatchEvent(clickEvent);
                                return true;
                            }
                        } catch(e) {
                            return false;
                        }
                    }
                    return false;
                """)
                if send_clicked:
                    print("   ✓ Send button clicked!")
                    break
                time.sleep(0.3)
            
            if not send_clicked:
                print("   Trying Selenium fallback for Send button...")
                # Fallback: Selenium with multiple selectors
                send_selectors = [
                    "button[aria-label*='Send']",
                    "button[aria-label*='send']",
                    "//button[normalize-space()='Send']",
                    "//button[contains(text(), 'Send')]",
                    "button[type='button']",
                ]
                for selector in send_selectors:
                    try:
                        if selector.startswith("//"):
                            btn = self.driver.find_element("xpath", selector)
                        else:
                            btn = self.driver.find_element("css selector", selector)
                        if btn.is_displayed():
                            btn.click()
                            send_clicked = True
                            print(f"   ✓ Send clicked via Selenium: {selector}")
                            break
                    except:
                        continue
            
            if send_clicked:
                # Verify share succeeded by checking if dialog closed
                time.sleep(0.5)
                dialog_closed = self.driver.execute_script("""
                    // Check if share dialog is still open
                    const dialogs = Array.from(document.querySelectorAll('[role="dialog"], div[class*="modal"], div[class*="Modal"]'));
                    const hasVisibleDialog = dialogs.some(d => d.offsetParent !== null);
                    return !hasVisibleDialog;
                """)
                if dialog_closed:
                    print(f"✅ SUCCESS! Reel shared to '{friend_name}'!")
                else:
                    print(f"✅ Share sent to '{friend_name}'! (Dialog may still be visible)")
            else:
                print(f"⚠ Could not find Send button. Please check manually.")
                print(f"   Friend name typed: '{friend_name}'")
                print(f"   Try clicking Send manually if friend is selected.")
        except Exception as e:
            print(f"✗ JavaScript error: {e}")
            print("Trying fallback method...")
            self._share_fallback(friend_name)

    def _share_fallback(self, friend_name: str) -> None:
        """Fallback method using Selenium if JavaScript fails."""
        try:
            # Click share button
            share_clicked = self._click_first([
                "button[aria-label*='Share']",
                "svg[aria-label*='Share']",
            ])
            
            if not share_clicked:
                print("✗ Could not open share dialog")
                return
            
            time.sleep(0.4)
            
            # Find and type in search box
            search_box = None
            for selector in ["input[placeholder*='Search']", "input[aria-label*='Search']"]:
                try:
                    search_box = self.driver.find_element("css selector", selector)
                    if search_box.is_displayed():
                        break
                except:
                    continue
            
            if not search_box:
                print("✗ Could not find search box")
                return
            
            search_box.clear()
            search_box.send_keys(friend_name)
            time.sleep(0.6)
            
            # Click friend from suggestions
            friend_name_lower = friend_name.lower()
            friend_clicked = self.driver.execute_script(f"""
                const name = '{friend_name_lower}';
                const items = Array.from(document.querySelectorAll('div[role="button"]'));
                for (const item of items) {{
                    const text = (item.textContent || '').toLowerCase();
                    if (text.includes(name) && item.offsetParent !== null) {{
                        item.click();
                        return true;
                    }}
                }}
                return false;
            """)
            
            if not friend_clicked:
                search_box.send_keys(Keys.ENTER)
            
            time.sleep(0.3)
            
            # Click Send
            send_clicked = self._click_first([
                "button[aria-label*='Send']",
                "//button[normalize-space()='Send']",
            ])
            
            if send_clicked:
                print(f"✅ Reel shared to '{friend_name}'!")
            else:
                print(f"⚠ Share may have succeeded, but Send button not found")
        except Exception as e:
            print(f"✗ Share failed: {e}")

    def navigate(self, target: str) -> None:
        """Navigate to a specific Instagram tab/section."""
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
                    'a[aria-label*="Home" i]',
                    'svg[aria-label="Home"]',
                    'a[href*="/"]',
                ],
                "url": "https://www.instagram.com/",
            },
            "search": {
                "selectors": [
                    'a[href*="/explore"]',
                    'a[aria-label="Search"]',
                    'a[aria-label*="Search" i]',
                    'svg[aria-label="Search"]',
                ],
                "url": "https://www.instagram.com/explore/",
            },
            "explore": {
                "selectors": [
                    'a[href*="/explore"]',
                    'a[aria-label="Explore"]',
                    'a[aria-label*="Explore" i]',
                    'svg[aria-label="Explore"]',
                ],
                "url": "https://www.instagram.com/explore/",
            },
            "reels": {
                "selectors": [
                    'a[href*="/reels"]',
                    'a[aria-label="Reels"]',
                    'a[aria-label*="Reels" i]',
                    'svg[aria-label="Reels"]',
                ],
                "url": "https://www.instagram.com/reels/",
            },
            "messages": {
                "selectors": [
                    'a[href*="/direct"]',
                    'a[aria-label="Messages"]',
                    'a[aria-label*="Messages" i]',
                    'a[aria-label*="Direct" i]',
                    'svg[aria-label="Direct"]',
                ],
                "url": "https://www.instagram.com/direct/inbox/",
            },
            "notifications": {
                "selectors": [
                    'a[href*="/accounts/activity"]',
                    'a[aria-label="Notifications"]',
                    'a[aria-label*="Notifications" i]',
                    'svg[aria-label="Notifications"]',
                ],
                "url": "https://www.instagram.com/accounts/activity/",
            },
            "create": {
                "selectors": [
                    'a[aria-label="New post"]',
                    'a[aria-label*="Create" i]',
                    'a[aria-label*="New" i]',
                    'svg[aria-label*="Create" i]',
                    'button[aria-label*="Create" i]',
                ],
                "url": None,  # Create opens a modal, not a page
            },
            "profile": {
                "selectors": [
                    'a[href*="/"]',  # Profile link is usually username
                    'a[aria-label*="Profile" i]',
                    'svg[aria-label*="Profile" i]',
                ],
                "url": None,  # Profile URL is user-specific
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
                elements = self.driver.find_elements("css selector", selector)
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        clicked = True
                        print(f"✓ Clicked {target} navigation link")
                        break
                if clicked:
                    break
            except Exception:
                continue
        
        # Fallback: Navigate directly via URL (if URL is available)
        if not clicked and nav_info["url"]:
            try:
                self.driver.get(nav_info["url"])
                print(f"✓ Navigated to {target} via URL")
            except Exception as e:
                print(f"✗ Navigation failed: {e}")
        elif not clicked and not nav_info["url"]:
            # For Create and Profile, try JavaScript click
            clicked = self.driver.execute_script("""
                const target = arguments[0];
                const selectors = arguments[1];
                for (const sel of selectors) {
                    const elements = document.querySelectorAll(sel);
                    for (const el of elements) {
                        if (el.offsetParent !== null) {
                            el.click();
                            return true;
                        }
                    }
                }
                return false;
            """, target_lower, nav_info["selectors"])
            
            if clicked:
                print(f"✓ Clicked {target} via JavaScript")
            else:
                print(f"✗ Could not navigate to {target}")
        
        time.sleep(0.5)  # Wait for page to load