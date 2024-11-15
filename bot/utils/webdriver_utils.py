import time
import asyncio
import traceback
from typing import Optional
import random
from playwright.async_api import async_playwright
from better_proxy import Proxy
import aiohttp
from bot.config import config
from bot.logger.logger import logger, gradient_progress_bar
import math

class BrowserManager:
    def __init__(self, account_name: str, auth_url: str, proxy: Optional[str] = None):
        self.account_name = account_name
        self.auth_url = auth_url
        self.proxy = proxy or config.PROXY
        self.browser = None
        self.context = None
        self.page = None

    async def create_browser(self):
        try:
            playwright = await async_playwright().start()
            window_width, window_height = config.BROWSER_CONFIG["window_size"]
            mobile_user_agent = config.BROWSER_CONFIG["mobile_user_agent"]
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                f"--window-size={window_width},{window_height}",
                "--lang=" + config.BROWSER_CONFIG["language"],
                "--disable-extensions",
                "--disable-notifications",
                "--disable-popup-blocking",
                "--disable-software-rasterizer",
                "--disable-dev-tools",
                "--disable-logging",
                "--disable-remote-fonts",
                "--disable-background-networking",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-translate",
                "--disable-domain-reliability",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-breakpad",
                "--disable-ipc-flooding-protection",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-background-timer-throttling",
                "--disable-background-media-suspend",
                "--js-flags=--expose-gc",
                "--memory-pressure-off",
                "--disable-web-security",
                "--ignore-certificate-errors",
                "--ignore-certificate-errors-spki-list",
                "--ignore-ssl-errors",
            ]
            if config.BROWSER_CONFIG["headless"]:
                browser_args.append("--headless=new")
            launch_options = {
                "args": browser_args,
                "headless": config.BROWSER_CONFIG["headless"],
                "ignore_default_args": ["--enable-automation"],
            }
            if config.USE_PROXY_FROM_FILE and self.proxy:
                try:
                    proxy_obj = Proxy.from_str(self.proxy)
                    proxy_config = {
                        "server": f"{proxy_obj.host}:{proxy_obj.port}",
                        "username": proxy_obj.login,
                        "password": proxy_obj.password
                    }
                    launch_options["proxy"] = proxy_config
                    browser_args.extend([
                        f"--proxy-server={proxy_obj.host}:{proxy_obj.port}",
                        "--disable-web-security",
                        "--ignore-certificate-errors",
                    ])
                except Exception as e:
                    logger.warning(f"{self.account_name} | Skipping proxy configuration: {e}")
            context_params = {
                "viewport": {"width": window_width, "height": window_height},
                "user_agent": mobile_user_agent,
                "device_scale_factor": 3,
                "is_mobile": True,
                "has_touch": True,
                "ignore_https_errors": True,
                "bypass_csp": True,
                "locale": "ru-RU"
            }
            max_retries = 3
            retry_delay = 5
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    self.browser = await playwright.chromium.launch(**launch_options)
                    self.context = await self.browser.new_context(**context_params)
                    self.page = await self.context.new_page()
                    
                    await self.page.set_extra_http_headers(config.BROWSER_CONFIG["network_headers"])
                    script_timeout = random.randint(*config.SCRIPT_TIMEOUT)
                    page_load_timeout = random.randint(*config.BROWSER_CREATION_TIMEOUT)
                    self.page.set_default_timeout(page_load_timeout * 1000)
                    self.page.set_default_navigation_timeout(script_timeout * 1000)
                    
                    await self.page.evaluate("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                    """)
                    
                    try:
                        logger.info(f"{self.account_name} | Attempting to navigate to page (attempt {attempt + 1}/{max_retries})")
                        
                        for nav_attempt in range(3):  # 3 попытки для навигации
                            try:
                                response = await self.page.goto(
                                    self.auth_url,
                                    timeout=60000,
                                    wait_until="domcontentloaded",
                                    referer="https://web.telegram.org/"
                                )
                                
                                if response and response.ok:
                                    logger.info(f"{self.account_name} | Navigation successful")
                                    logger.info(f"{self.account_name} | Browser created successfully")
                                    return self.page
                                else:
                                    status = response.status if response else 'Unknown'
                                    logger.warning(f"{self.account_name} | Navigation returned status: {status}")
                                    
                                    if nav_attempt < 2:  # Если это не последняя попытка
                                        logger.info(f"{self.account_name} | Retrying navigation in 5 seconds...")
                                        await asyncio.sleep(5)
                                        continue
                                    raise Exception(f"Navigation failed with status: {status}")
                                    
                            except Exception as e:
                                error_message = str(e)
                                if "ERR_CONNECTION_CLOSED" in error_message:
                                    if nav_attempt < 2:
                                        logger.info(f"{self.account_name} | Connection closed, retrying in 5 seconds...")
                                        await asyncio.sleep(5)
                                        continue
                                
                                if nav_attempt < 2:
                                    logger.warning(f"{self.account_name} | Navigation attempt {nav_attempt + 1} failed: {e}")
                                    await asyncio.sleep(5)
                                    continue
                                raise
                                
                        raise Exception("All navigation attempts failed")
                        
                    except Exception as nav_error:
                        last_error = nav_error
                        logger.warning(f"{self.account_name} | Navigation attempt {attempt + 1} failed: {nav_error}")
                        
                        if attempt < max_retries - 1:
                            logger.info(f"{self.account_name} | Cleaning up and retrying in {retry_delay} seconds...")
                            await self._cleanup_browser_instance()
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            raise Exception(f"Navigation failed after {max_retries} attempts. Last error: {nav_error}")
                            
                except Exception as e:
                    last_error = e
                    logger.error(f"{self.account_name} | Browser creation attempt {attempt + 1} failed: {str(e)}")
                    await self._cleanup_browser_instance()
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        raise Exception(f"Browser creation failed after {max_retries} attempts. Last error: {last_error}")
                        
        except Exception as e:
            logger.error(f"{self.account_name} | Fatal error creating browser: {str(e)}")
            await self._cleanup_browser_instance()
            raise

    async def _cleanup_browser_instance(self):
        """Вспомогательный метод для очистки ресурсов браузера"""
        try:
            if hasattr(self, 'page') and self.page:
                await self.page.close()
            if hasattr(self, 'context') and self.context:
                await self.context.close()
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"{self.account_name} | Error during cleanup: {e}")

    async def close_browser(self):
        try:
            if self.page:
                try:
                    await self.page.close()
                except Exception as e:
                    logger.debug(f"{self.account_name} | Error closing page: {e}")
            if self.context:
                try:
                    await self.context.close()
                except Exception as e:
                    logger.debug(f"{self.account_name} | Error closing context: {e}")
            if self.browser:
                try:
                    await self.browser.close()
                except Exception as e:
                    logger.debug(f"{self.account_name} | Error closing browser: {e}")
        except Exception as e:
            logger.error(f"{self.account_name} | Error closing browser: {e}")

    async def upgrade_city(self):
        try:
            logger.info(f"{self.account_name} | Starting city upgrade")
            await self.page.wait_for_selector('[class^="_buildNav"]', timeout=10000)
            upgrade_result = await self.page.evaluate(f"""
            async () => {{
                const sleep = ms => new Promise(r => setTimeout(r, ms));
                const safeClick = async (element) => {{
                    if (!element) return false;
                    try {{
                        element.click();
                        return true;
                    }} catch (e) {{
                        console.error('Click failed:', e);
                        return false;
                    }}
                }};
                let missingButtons = [];
                let upgradedCount = 0;
                let noUpgradesAvailable = true;
                const startTime = Date.now();
                const maxExecutionTime = {config.SCRIPT_UPGRADE['max_execution_time']};
                const noChangeTimeout = {config.SCRIPT_UPGRADE['no_change_timeout']};
                let lastChangeTime = startTime;
                const navElement = document.querySelector('[class^="_buildNav"]');
                if (!navElement) {{
                    console.log("Navigation element not found");
                    return {{ error: "Navigation not found" }};
                }}
                let tabs = Array.from(navElement.querySelectorAll('[class^="_navItem"]'))
                    .filter(item => item.querySelector('[class^="_count"]'));
                if (!tabs.length) {{
                    console.log("No tabs found");
                    return {{ error: "No tabs found" }};
                }}
                const reorderedTabs = [
                    ...tabs.slice(1, 4),
                    tabs[0],
                    ...tabs.slice(4)
                ];
                for (let t of reorderedTabs) {{
                    if (!t) continue;
                    if (Date.now() - startTime > maxExecutionTime) {{
                        console.log("Maximum execution time exceeded");
                        break;
                    }}
                    let clickAttempts = 0;
                    const maxClickAttempts = 3;
                    while (clickAttempts < maxClickAttempts) {{
                        if (!await safeClick(t)) {{
                            console.log("Tab click failed");
                            clickAttempts++;
                            await sleep(200);
                            continue;
                        }}
                        await sleep(500);
                        if (t.classList.contains('active') || t.getAttribute('aria-selected') === 'true') {{
                            break;
                        }}
                        clickAttempts++;
                        await sleep(200);
                    }}
                    await sleep({config.SCRIPT_UPGRADE['click_delay']});
                    let items = Array.from(document.querySelectorAll('[class^="_buildPreview"]'))
                        .filter(item => item && 
                                      !item.classList.contains('disabled') && 
                                      !item.querySelector('[class^="_cooldown"]') &&
                                      !item.querySelector('button[disabled]'));
                    if (items.length > 0) {{
                        noUpgradesAvailable = false;
                    }}
                    for (let item of items) {{
                        if (!item) continue;
                        if (Date.now() - startTime > maxExecutionTime) {{
                            break;
                        }}
                        let button = item.querySelector('button');
                        if (button) {{
                            if (await safeClick(button)) {{
                                upgradedCount++;
                                lastChangeTime = Date.now();
                                await sleep({config.SCRIPT_UPGRADE['post_click_delay']});
                                let detailButton = document.querySelector('[class^="_buildDetail"] button');
                                if (detailButton) {{
                                    await safeClick(detailButton);
                                    await sleep(1000);
                                }}
                            }}
                        }} else {{
                            missingButtons.push(item.outerHTML);
                        }}
                    }}
                    await sleep({config.SCRIPT_UPGRADE['final_delay']});
                }}
                return {{
                    message: noUpgradesAvailable ? "No upgrades available" : "Upgrade completed",
                    missingButtons: missingButtons,
                    upgradedCount: upgradedCount,
                    noUpgradesAvailable: noUpgradesAvailable
                }};
            }}
            """)
            if 'error' in upgrade_result:
                logger.error(f"{self.account_name} | Upgrade error: {upgrade_result['error']}")
                return False
            logger.info(f"{self.account_name} | Upgrades completed: {upgrade_result['upgradedCount']}")
            if upgrade_result['missingButtons']:
                logger.debug(f"{self.account_name} | Missing buttons: {upgrade_result['missingButtons']}")
            return not upgrade_result['noUpgradesAvailable']
        except Exception as e:
            logger.error(f"{self.account_name} | Error upgrading city: {e}")
            logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
            return False

    async def find_and_click_build_button(self):
        try:
            build_button = await self.page.query_selector('a._btnBuildWrapper_xw841_23[href="/city/build"]')
            if build_button:
                await build_button.scroll_into_view_if_needed()
                await build_button.click()
                await asyncio.sleep(config.BUILD_BUTTON_CLICK_DELAY[0])
                initial_url = self.page.url
                try:
                    await self.page.wait_for_url(lambda url: url != initial_url, timeout=10000)
                except Exception:
                    pass
            else:
                logger.info(f"{self.account_name} | Build button not found")
        except Exception as e:
            logger.info(f"{self.account_name} | Error finding or clicking build button: {e}")

    async def navigate_city(self):
        try:
            await self.page.wait_for_selector('body', timeout=60000)
            await asyncio.sleep(random.uniform(*config.PAGE_LOAD_DELAY))
            try:
                excellent_button = await self.page.wait_for_selector(
                    "button._button_1ir11_1._primary_1ir11_25._normal_1ir11_211:text('Отлично!')", 
                    timeout=5000
                )
                if excellent_button:
                    try:
                        await self.page.evaluate("""(element) => {
                            element.click();
                            element.dispatchEvent(new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            }));
                        }""", excellent_button)
                    except Exception:
                        try:
                            await excellent_button.click(force=True)
                        except Exception:
                            box = await excellent_button.bounding_box()
                            if box:
                                await self.page.mouse.click(
                                    box["x"] + box["width"] / 2,
                                    box["y"] + box["height"] / 2
                                )
                    await asyncio.sleep(2)
            except Exception as e:
                logger.debug(f"{self.account_name} | No excellent button found: {e}")
            city_selectors = [
                "a._button_1rcrc_1._big_1rcrc_52[href='/city']",
                "div._title_1rcrc_32:text('Ваш город')",
                "//a[contains(@class, '_button_') and @href='/city']",
                "//div[contains(@class, '_title_') and text()='Ваш город']"
            ]
            for selector in city_selectors:
                try:
                    city_button = await self.page.wait_for_selector(selector, state="visible", timeout=10000)
                    if city_button:
                        logger.info(f"{self.account_name} | Found city button")
                        await city_button.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        await self.page.evaluate("""(element) => {
                            element.click();
                            element.dispatchEvent(new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            }));
                        }""", city_button)
                        await asyncio.sleep(random.uniform(*config.CITY_BUTTON_CLICK_DELAY))
                        if '/city' in self.page.url:
                            logger.info(f"{self.account_name} | Successfully navigated to city page")
                            build_button = await self.page.wait_for_selector("div._btnBuild_xw841_23", timeout=5000)
                            if build_button:
                                await build_button.click()
                                await asyncio.sleep(random.uniform(*config.BUILD_BUTTON_CLICK_DELAY))
                            break
                except Exception as e:
                    logger.debug(f"{self.account_name} | Failed with selector {selector}: {e}")
                    continue
            upgrades_available = await self.upgrade_city()
            if not upgrades_available:
                logger.info(f"{self.account_name} | No upgrades available")
                return True
            return True
        except asyncio.CancelledError:
            logger.warning(f"{self.account_name} | Navigation cancelled")
            return False
        except Exception as e:
            logger.error(f"{self.account_name} | Error navigating city: {e}")
            logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
            return False
        finally:
            try:
                logger.info(f"{self.account_name} | Session ended")
                await self.close_browser()
            except Exception as e:
                logger.error(f"{self.account_name} | Error closing browser in finally block: {e}")

    async def check_energy_and_tap_coins(self) -> int:
        try:
            energy_element = await self.page.wait_for_selector(f"#{config.SELECTORS['energy_element']}", timeout=10000)
            energy_text = await energy_element.text_content()
            current_energy = int(energy_text.split('/')[0].strip().replace(',', ''))
            taps_remaining = current_energy
            coin_selector = "div[class*='_coin_']"
            coin_element = await self.page.wait_for_selector(coin_selector, timeout=10000)
            if coin_element and taps_remaining > 0:
                box = await coin_element.bounding_box()
                if box:
                    base_x = box['x'] + box['width'] / 2
                    base_y = box['y'] + box['height'] / 2
                    with gradient_progress_bar(range(current_energy), desc=f"{self.account_name} | Taps on coins", total=current_energy) as pbar:
                        while taps_remaining > 0: 
                            num_fingers = min(random.randint(1, 5), taps_remaining) 
                            touch_points = []
                            for i in range(num_fingers):
                                angle = random.uniform(0, 2 * 3.14159)
                                radius = random.uniform(10, 50)
                                x = base_x + radius * math.cos(angle)
                                y = base_y + radius * math.sin(angle)
                                touch_points.append({"x": x, "y": y})
                            await self.page.evaluate("""
                                (points) => {
                                    const touches = points.map((p, i) => new Touch({
                                        identifier: i,
                                        target: document.elementFromPoint(p.x, p.y),
                                        clientX: p.x,
                                        clientY: p.y,
                                        radiusX: 2.5,
                                        radiusY: 2.5,
                                        rotationAngle: 10,
                                        force: 1
                                    }));
                                    const touchStartEvent = new TouchEvent('touchstart', {
                                        cancelable: true,
                                        bubbles: true,
                                        touches: touches,
                                        targetTouches: touches,
                                        changedTouches: touches
                                    });
                                    const touchEndEvent = new TouchEvent('touchend', {
                                        cancelable: true,
                                        bubbles: true,
                                        touches: [],
                                        targetTouches: [],
                                        changedTouches: touches
                                    });
                                    document.elementFromPoint(points[0].x, points[0].y).dispatchEvent(touchStartEvent);
                                    document.elementFromPoint(points[0].x, points[0].y).dispatchEvent(touchEndEvent);
                                }
                            """, touch_points)
                            taps_remaining -= num_fingers  
                            pbar.update(num_fingers)
                            await asyncio.sleep(random.uniform(0.01, 0.05))
            return current_energy
        except Exception as e:
            logger.error(f"{self.account_name} | Error checking energy and tapping coins: {e}")
            return 0

    async def get_game_stats(self):
        try:
            stats = await self.page.evaluate("""() => {
                const formatNumber = (text) => {
                    if (!text) return null;
                    return text.replace(/[^0-9]/g, '');
                };
                const stats = {};
                const levelElement = document.querySelector('div[class*="_title_14n1y_"]');
                if (levelElement) {
                    const levelText = levelElement.textContent;
                    const levelMatch = levelText.match(/(\\d+)\\s*\\/\\s*(\\d+)/);
                    if (levelMatch) {
                        stats.level = `${levelMatch[1]}/${levelMatch[2]}`;
                    }
                }
                const incomeElement = document.querySelector('#income ._info_ji1yj_18');
                if (incomeElement) {
                    const incomeText = incomeElement.textContent;
                    stats.income = formatNumber(incomeText);
                }
                const populationElement = document.querySelector('#population ._info_ji1yj_18');
                if (populationElement) {
                    const populationText = populationElement.textContent;
                    stats.population = formatNumber(populationText);
                }
                const balanceElement = document.querySelector('div[class*="_money_"]');
                if (balanceElement) {
                    const balanceText = balanceElement.textContent;
                    stats.balance = formatNumber(balanceText);
                }
                return stats;
            }""")
            if stats:
                def format_number(num_str):
                    if num_str and num_str.isdigit():
                        return "{:,}".format(int(num_str)).replace(',', ' ')
                    return 'N/A'
                print("")
                logger.info(f"{self.account_name} | Game stats:")
                logger.info("\t├── Level: " + stats.get('level', 'N/A'))
                logger.info("\t├── Income: " + format_number(stats.get('income')) + "/hour")
                logger.info("\t├── Population: " + format_number(stats.get('population')))
                logger.info("\t└─ Balance: " + format_number(stats.get('balance')))
                print("")
            return stats
        except Exception as e:
            logger.error(f"{self.account_name} | Error getting game stats: {e}")
            return None

    async def run(self) -> bool:
        max_retries = config.MAX_RETRIES
        retry_delay = config.RETRY_DELAY
        thread_timeout = random.randint(*config.BROWSER_THREAD_TIMEOUT)
        logger.info(f"{self.account_name} | Thread timeout set: {thread_timeout} seconds")
        for attempt in range(max_retries):
            try:
                await self.create_browser()
                await self.page.goto(self.auth_url)
                try:
                    logger.info(f"{self.account_name} | Waiting for page load...")
                    await self.page.wait_for_selector(
                        "div[class*='_closeButton_'], " + 
                        "button:has-text('Отлично!'), " + 
                        "button:has-text('Забрать'), " + 
                        "button:has-text('Пропустить'), " + 
                        "button[class*='_dice_'], " + 
                        "button:has-text('Создать город'), " + 
                        "button:has-text('Начнем!')",
                        timeout=10000
                    )
                    logger.info(f"{self.account_name} | Page loaded, starting button checks")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"{self.account_name} | Page load timeout: {e}")
                    continue
                check_interval = config.NAVIGATION["check_interval"]
                max_wait_time = config.NAVIGATION["max_wait_time"]
                start_time = time.time()
                buttons_to_check = [
                    ("Close button", config.SELECTORS["close_button"]),
                    ("Excellent button", config.SELECTORS["excellent_button"]),
                    ("Collect button", config.SELECTORS["collect_button"]),
                    ("Skip button", config.SELECTORS["skip_button"]),
                    ("Dice button", config.SELECTORS["dice_button"]),
                    ("Create city button", config.SELECTORS["create_city_button"]),
                    ("Let's start button", config.SELECTORS["lets_start_button"]),
                ]
                while time.time() - start_time < max_wait_time:
                    try:
                        if not self.page.is_closed():
                            for button_name, selector in buttons_to_check:
                                try:
                                    button = await self.page.wait_for_selector(selector, timeout=2000)
                                    if button:
                                        logger.info(f"{self.account_name} | Found and clicking {button_name}")
                                        await button.click()
                                        await asyncio.sleep(random.uniform(1, 2))
                                except Exception:
                                    continue
                            energy_amount = await self.check_energy_and_tap_coins()
                            if energy_amount > 0:
                                logger.info(f"{self.account_name} | Energy found: {energy_amount}")
                                break
                        else:
                            logger.warning(f"{self.account_name} | Page closed")
                            break
                        await asyncio.sleep(check_interval)
                    except Exception as e:
                        logger.error(f"{self.account_name} | Error during button checks: {e}")
                        break
                if not self.page.is_closed():
                    try:
                        await self.get_game_stats()
                    except Exception as e:
                        logger.error(f"{self.account_name} | Error getting game stats: {e}")
                    await asyncio.sleep(5)
                    navigation_completed = await self.navigate_city()
                    if navigation_completed:
                        logger.info(f"{self.account_name} | Session ended successfully")
                        return True
                    else:
                        logger.error(f"{self.account_name} | Error navigating city")
                        return False
            except asyncio.CancelledError:
                logger.warning(f"{self.account_name} | Operation was cancelled")
                return False
            except Exception as e:
                logger.error(f"{self.account_name} | Error in BrowserManager.run: {e}")
                logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
                if attempt < max_retries - 1:
                    logger.info(f"{self.account_name} | Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"{self.account_name} | Maximum number of attempts reached. Terminating.")
                    return False
            finally:
                try:
                    await self.close_browser()
                except Exception as e:
                    logger.error(f"{self.account_name} | Error closing browser in finally block: {e}")
        return False

    async def test_proxy_connection(self):
        try:
            proxy_obj = Proxy.from_str(self.proxy)
            conn = aiohttp.TCPConnector(ssl=False)
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
                try:
                    proxy_url = f"socks5://{proxy_obj.login}:{proxy_obj.password}@{proxy_obj.host}:{proxy_obj.port}"
                    async with session.get('http://example.com', proxy=proxy_url) as response:
                        if response.status == 200:
                            logger.info(f"{self.account_name} | Proxy connection test successful")
                            return True
                except Exception as e:
                    try:
                        proxy_url = f"http://{proxy_obj.login}:{proxy_obj.password}@{proxy_obj.host}:{proxy_obj.port}"
                        async with session.get('http://example.com', proxy=proxy_url) as response:
                            if response.status == 200:
                                logger.info(f"{self.account_name} | Proxy connection test successful (HTTP)")
                                self.proxy = f"http://{proxy_obj.login}:{proxy_obj.password}@{proxy_obj.host}:{proxy_obj.port}"
                                return True
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"{self.account_name} | Proxy connection test failed: {e}")
        return False

async def play_in_browser(account_name: str, auth_url: str, proxy: Optional[str] = None) -> bool:
    browser_manager = BrowserManager(account_name, auth_url, proxy)
    result = await browser_manager.run()
    if not result:
        logger.error(f"{account_name} | Error while working with browser")
    return result
