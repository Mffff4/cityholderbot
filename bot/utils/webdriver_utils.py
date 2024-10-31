import time
import asyncio
import traceback
from typing import Optional
import random
from playwright.async_api import async_playwright
from better_proxy import Proxy

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
                "--verbose",
                "--log-level=0"
            ]

            if config.BROWSER_CONFIG["headless"]:
                browser_args.append("--headless=new")

            proxy_config = None
            proxy_config = None
            if self.proxy:
                try:
                    proxy_obj = Proxy.from_str(self.proxy)
                    proxy_config = {
                        "server": f"{proxy_obj.protocol or 'http'}://{proxy_obj.host}:{proxy_obj.port}",
                    }
                    if proxy_obj.login and proxy_obj.password:
                        proxy_config.update({
                            "username": proxy_obj.login,
                            "password": proxy_obj.password,
                        })
                    logger.info(f"{self.account_name} | Browser using proxy: {proxy_obj.host}:{proxy_obj.port}")
                except Exception as e:
                    logger.error(f"{self.account_name} | Error configuring browser proxy: {e}")
                try:
                    proxy_obj = Proxy.from_str(self.proxy)
                    proxy_config = {
                        "server": f"{proxy_obj.protocol or 'http'}://{proxy_obj.host}:{proxy_obj.port}",
                    }
                    if proxy_obj.login and proxy_obj.password:
                        proxy_config.update({
                            "username": proxy_obj.login,
                            "password": proxy_obj.password,
                        })
                    logger.info(f"{self.account_name} | Browser using proxy: {proxy_obj.host}:{proxy_obj.port}")
                except Exception as e:
                    logger.error(f"{self.account_name} | Error configuring browser proxy: {e}")

            self.browser = await playwright.chromium.launch(
                args=browser_args,
                headless=config.BROWSER_CONFIG["headless"],
                proxy=proxy_config if proxy_config else None
                headless=config.BROWSER_CONFIG["headless"],
                proxy=proxy_config if proxy_config else None
            )

            context_params = {
                "viewport": {"width": window_width, "height": window_height},
                "user_agent": mobile_user_agent,
                "device_scale_factor": 3,
                "is_mobile": True,
                "has_touch": True
            }

            self.context = await self.browser.new_context(**context_params)
            self.page = await self.context.new_page()

            await self.page.set_extra_http_headers(config.BROWSER_CONFIG["network_headers"])

            script_timeout = random.randint(*config.SCRIPT_TIMEOUT)
            page_load_timeout = random.randint(*config.BROWSER_CREATION_TIMEOUT)

            self.page.set_default_timeout(page_load_timeout * 1000)
            self.page.set_default_navigation_timeout(script_timeout * 1000)

            logger.info(f"{self.account_name} | Browser created successfully. Timeouts: {script_timeout}s/{page_load_timeout}s")

            try:
                logger.info(f"{self.account_name} | Loading auth page...")
                await self.page.goto(self.auth_url)
                logger.info(f"{self.account_name} | Auth page loaded successfully")
            except Exception as e:
                logger.error(f"{self.account_name} | Error loading page: {e}")
                raise

            return self.page

        except Exception as e:
            logger.error(f"{self.account_name} | Error creating browser: {e}")
            logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
            raise

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
            
            upgrade_result = await self.page.evaluate(f"""
            async () => {{
                const sleep = ms => new Promise(r => setTimeout(r, ms));
                let missingButtons = [];
                let upgradedCount = 0;
                let noUpgradesAvailable = true;
                
                const startTime = Date.now();
                const maxExecutionTime = {config.SCRIPT_UPGRADE['max_execution_time']};
                const noChangeTimeout = {config.SCRIPT_UPGRADE['no_change_timeout']};
                let lastChangeTime = startTime;

                let tabs = Array.from(document.querySelectorAll('[class^="_buildNav"] [class^="_navItem"]'))
                    .filter(item => item.querySelector('[class^="_count"]'));
                
                const reorderedTabs = [
                    ...tabs.slice(1, 4),
                    tabs[0],
                    ...tabs.slice(4)
                ];

                for (let t of reorderedTabs) {{
                    if (Date.now() - startTime > maxExecutionTime) {{
                        console.log("Maximum execution time exceeded");
                        break;
                    }}

                    if (Date.now() - lastChangeTime > noChangeTimeout) {{
                        console.log("No changes for 30 seconds, finishing upgrade");
                        break;
                    }}

                    let clickAttempts = 0;
                    const maxClickAttempts = 3;
                    
                    while (clickAttempts < maxClickAttempts) {{
                        t.click();
                        await sleep(500);
                        
                        if (t.classList.contains('active') || t.getAttribute('aria-selected') === 'true') {{
                            break;
                        }}
                        
                        clickAttempts++;
                        await sleep(200);
                    }}

                    await sleep({config.SCRIPT_UPGRADE['click_delay']});

                    let items = Array.from(document.querySelectorAll('[class^="_buildPreview"]'))
                        .filter(item => !item.classList.contains('disabled') && 
                                    !item.querySelector('[class^="_cooldown"]') &&
                                    !item.querySelector('button[disabled]'));

                    if (items.length > 0) {{
                        noUpgradesAvailable = false;
                    }}

                    for (let item of items) {{
                        if (Date.now() - startTime > maxExecutionTime) {{
                            break;
                        }}

                        if (Date.now() - lastChangeTime > noChangeTimeout) {{
                            break;
                        }}

                        let button = item.querySelector('button');
                        if (button) {{
                            button.click();
                            upgradedCount++;
                            lastChangeTime = Date.now();
                            await sleep({config.SCRIPT_UPGRADE['post_click_delay']});

                            let detailButton = document.querySelector('[class^="_buildDetail"] button');
                            if (detailButton) {{
                                detailButton.click();
                                await sleep(1000);
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
            await self.page.wait_for_selector('body', timeout=30000)
            await asyncio.sleep(random.uniform(*config.PAGE_LOAD_DELAY))

            # Список всех возможных кнопок для обработки
            buttons_to_handle = [
                "button._button_afxdk_1._primary_afxdk_25._normal_afxdk_194:text('Понял!')",
                "button._button_afxdk_1._primary_afxdk_25._normal_afxdk_194:text('Accepted!')",
                "button._button_afxdk_1._primary_afxdk_25._normal_afxdk_194:text('Got it!')",
                "button._button_afxdk_1:text('Собрать')",
                "button._button_afxdk_1:text('Collect')",
                "button._button_afxdk_1:text('Skip')",
                "button._button_afxdk_1:text('Пропустить')",
                "button._button_afxdk_1:text('Начнем')",
                "button._button_afxdk_1:text(\"Let's start\")",
                "button._button_afxdk_1:text('Создать город')",
                "button._button_afxdk_1:text('Create city')"
            ]

            # Функция для клика по кнопке с использованием JavaScript
            async def click_button(selector):
                try:
                    await self.page.evaluate(f"""
                        (selector) => {{
                            const button = document.querySelector(selector);
                            if (button) {{
                                button.click();
                                return true;
                            }}
                            return false;
                        }}
                    """, selector)
                    await asyncio.sleep(0.5)
                    return True
                except Exception:
                    return False

            # Обработка всех возможных кнопок
            for button_selector in buttons_to_handle:
                try:
                    button = await self.page.wait_for_selector(button_selector, timeout=2000)
                    if button:
                        for _ in range(3):  # Пробуем кликнуть до 3 раз
                            if await click_button(button_selector):
                                break
                            await asyncio.sleep(0.5)
                except Exception:
                    continue

            # Продолжаем с основной навигацией
            city_button_selector = f"//a[contains(@class, '_button_') and @href='/city']//div[contains(@class, '_title_') and (text()='{config.BUTTON_TEXTS['city']['ru']}' or text()='{config.BUTTON_TEXTS['city']['en']}')]"
            city_button = await self.page.wait_for_selector(city_button_selector, state="visible", timeout=30000)
            
            if city_button:
                await city_button.evaluate("button => button.click()")
                await asyncio.sleep(random.uniform(*config.CITY_BUTTON_CLICK_DELAY))
                
                try:
                    await self.page.wait_for_load_state('networkidle', timeout=30000)
                    await self.find_and_click_build_button()
                    upgrades_available = await self.upgrade_city()

                    if not upgrades_available:
                        logger.info(f"{self.account_name} | No upgrades available.")
                        return True

                    return True
                except Exception as e:
                    logger.error(f"{self.account_name} | Error waiting for page load: {e}")
                    return False

            return False

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
                initial_url = self.page.url
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
                            current_url = self.page.url
                            if current_url != initial_url:
                                for button_name, selector in buttons_to_check:
                                    try:
                                        button = await self.page.wait_for_selector(selector, timeout=1000)
                                        if button:
                                            await button.click()
                                            await asyncio.sleep(random.uniform(*config.RANDOM_DELAY))
                                    except Exception:
                                        continue

                                energy_amount = await self.check_energy_and_tap_coins()
                                if energy_amount > 0:
                                    break
                        else:
                            logger.warning(f"{self.account_name} | Page closed")
                            break

                        await asyncio.sleep(check_interval)
                    except Exception as e:
                        logger.error(f"{self.account_name} | Error working with browser: {e}")
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

async def play_in_browser(account_name: str, auth_url: str, proxy: Optional[str] = None) -> bool:
    browser_manager = BrowserManager(account_name, auth_url, proxy)
    result = await browser_manager.run()

    if not result:
        logger.error(f"{account_name} | Error while working with browser")

    return result



