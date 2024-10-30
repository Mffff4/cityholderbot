import time
import json
import asyncio
import traceback
from typing import Optional, List, Dict
import random
from bot.utils.common_utils import random_delay, touch_element, extract_game_stats

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException
from tqdm import tqdm

from bot.config import config
from bot.logger.logger import logger, log_game_stats, gradient_progress_bar
from colorama import Fore
import signal
import os

class BrowserManager:
    def __init__(self, account_name: str, auth_url: str, proxy: Optional[str] = None):
        self.account_name = account_name
        self.auth_url = auth_url
        self.proxy = proxy or config.PROXY
        self.driver = None

    def create_driver(self) -> uc.Chrome:
        try:
            options = uc.ChromeOptions()
            mobile_user_agent = config.MOBILE_USER_AGENT
            window_width, window_height = config.WINDOW_SIZE
            options.add_argument(f'user-agent={mobile_user_agent}')
            options.add_argument(f"--window-size={window_width},{window_height}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            if config.HEADLESS:
                options.add_argument("--headless=new")
            options.add_argument("--lang=" + config.LANGUAGE)
            options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})
            options.add_argument("--verbose")
            options.add_argument("--log-level=0")
            options.add_argument("--page-load-strategy=eager")

            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
                logger.info(f"{self.account_name} | Установлен прокси: {self.proxy}")

            if os.path.exists('/.dockerenv'):
                options.binary_location = '/usr/bin/chromium'
                try:
                    import subprocess
                    chromium_version = subprocess.check_output(['/usr/bin/chromium', '--version']).decode()
                    version_main = int(chromium_version.split()[1].split('.')[0])
                    logger.info(f"{self.account_name} | Обнаружена версия Chromium: {version_main}")
                except Exception as e:
                    logger.warning(f"{self.account_name} | Не удалось определить версию Chromium: {e}")
                    version_main = 108
                
                self.driver = uc.Chrome(
                    options=options,
                    driver_executable_path='/usr/bin/chromedriver',
                    version_main=version_main,
                    enable_cdp_events=True
                )
            else:
                self.driver = uc.Chrome(
                    options=options,
                    version_main=129,
                    enable_cdp_events=True
                )

            script_timeout = random.randint(*config.SCRIPT_TIMEOUT)
            page_load_timeout = random.randint(*config.BROWSER_CREATION_TIMEOUT)
            
            self.driver.set_page_load_timeout(page_load_timeout)
            self.driver.set_script_timeout(script_timeout)
            
            logger.info(f"{self.account_name} | Драйвер создан успешно. Таймауты: {script_timeout}с/{page_load_timeout}с")

            self.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                "width": window_width,
                "height": window_height,
                "deviceScaleFactor": 3,
                "mobile": True,
                "screenOrientation": {"type": "portraitPrimary", "angle": 0}
            })
            
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": mobile_user_agent,
                "platform": "Android",
                "acceptLanguage": config.LANGUAGE
            })
            
            self.driver.execute_cdp_cmd("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
            self.driver.execute_cdp_cmd("Emulation.setEmitTouchEventsForMouse", {"enabled": True})
            
            headers = config.NETWORK_HEADERS.copy()
            headers["User-Agent"] = mobile_user_agent
            self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})

            try:
                logger.info(f"{self.account_name} | Загрузка страницы авторизации...")
                self.driver.get(self.auth_url)
                logger.info(f"{self.account_name} | Страница авторизации загружена успешно")
            except Exception as e:
                logger.error(f"{self.account_name} | Ошибка при загрузке страницы: {e}")
                raise

            return self.driver
        except Exception as e:
            logger.error(f"{self.account_name} | Ошибка при создании драйвера: {e}")
            logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
            raise

    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"{self.account_name} | Ошибка при закрытии браузера: {e}")

    async def upgrade_city(self):
        try:
            logger.info(f"{self.account_name} | Начинаем улучшение города")
            
            upgrade_script = f"""
            const callback = arguments[arguments.length - 1];
            const sleep = ms => new Promise(r => setTimeout(r, ms));

            async function upgrade() {{
                let missingButtons = [];
                let upgradedCount = 0;
                let noUpgradesAvailable = true;
                let tabs = Array.from(document.querySelectorAll('[class^="_buildNav"] [class^="_navItem"]'))
                    .filter(item => item.querySelector('[class^="_count"]'));

                const startTime = Date.now();
                const maxExecutionTime = {config.SCRIPT_UPGRADE_MAX_EXECUTION_TIME};
                const noChangeTimeout = {config.SCRIPT_UPGRADE_NO_CHANGE_TIMEOUT};
                let lastChangeTime = startTime;

                for (let t of tabs) {{
                    if (Date.now() - startTime > maxExecutionTime) {{
                        console.log("Превышено максимальное время выполнения скрипта");
                        break;
                    }}

                    if (Date.now() - lastChangeTime > noChangeTimeout) {{
                        console.log("Нет изменений в течение 30 секунд, завершае улучшение");
                        break;
                    }}

                    t.click();
                    await sleep({config.SCRIPT_UPGRADE_SLEEP_TIMES['click_delay']});

                    let items = Array.from(document.querySelectorAll('[class^="_buildPreview"]'))
                        .filter(item => !item.classList.contains('disabled') && 
                                        !item.querySelector('[class^="_cooldown"]') &&
                                        !item.querySelector('button[disabled]'));

                    if (items.length > 0) {{
                        noUpgradesAvailable = false;
                    }}

                    for (let item of items) {{
                        if (Date.now() - startTime > maxExecutionTime) {{
                            console.log("Превышено максимальное время выполнения скрипта");
                            break;
                        }}

                        if (Date.now() - lastChangeTime > noChangeTimeout) {{
                            console.log("Нет изменений в течение 30 секунд, завершаем улучшение");
                            break;
                        }}

                        let button = item.querySelector('button');
                        if (button) {{
                            button.click();
                            upgradedCount++;
                            lastChangeTime = Date.now();
                            await sleep({config.SCRIPT_UPGRADE_SLEEP_TIMES['post_click_delay']});

                            let detailButton = document.querySelector('[class^="_buildDetail"] button');
                            if (detailButton) {{
                                detailButton.click();
                                await sleep(1000);
                            }}
                        }} else {{
                            missingButtons.push(item.outerHTML);
                        }}
                    }}

                    await sleep({config.SCRIPT_UPGRADE_SLEEP_TIMES['final_delay']});

                    // Добавляем отсчет в консоль браузера
                    const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                    const remainingTime = Math.max(0, Math.floor(maxExecutionTime / 1000 - elapsedTime));
                    console.log(`Прошло времени: ${{elapsedTime}} сек. Осталось времени: ${{remainingTime}} сек.`);
                }}

                return {{
                    message: noUpgradesAvailable ? "Нет доступных улучшений" : "Улучшение завершено",
                    missingButtons: missingButtons,
                    upgradedCount: upgradedCount,
                    noUpgradesAvailable: noUpgradesAvailable
                }};
            }}

            upgrade().then(result => callback(result)).catch(error => callback(null));
            """
            
            result = self.driver.execute_async_script(upgrade_script)
            
            if result is None:
                logger.warning(f"{self.account_name} | Скрипт улучшения города вернул None")
                return False

            logger.info(f"{self.account_name} | Выполнено улучшений: {result.get('upgradedCount', 0)}")
            if result.get('missingButtons'):
                logger.debug(f"{self.account_name} | Отсутствующие кнопки: {result.get('missingButtons')}")
            return not result.get('noUpgradesAvailable', True) 
        
        except Exception as e:
            logger.error(f"{self.account_name} | Ошибка при улучшении города: {e}")
            logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
            return False

    
    async def find_and_click_build_button(self):
        try:            
            js_code = """
            function clickBuildButton() {
                const buildButton = document.querySelector('a._btnBuildWrapper_xw841_23[href="/city/build"]');
                if (buildButton) {
                    buildButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    buildButton.click();
                    return true;
                }
                return false;
            }
            return clickBuildButton();
            """
            
            result = self.driver.execute_script(js_code)
            
            if result:
                await asyncio.sleep(config.BUILD_BUTTON_CLICK_DELAY[0])
                initial_url = self.driver.current_url
                try:
                    WebDriverWait(self.driver, 10).until(EC.url_changes(initial_url))
                    new_url = self.driver.current_url
                except TimeoutException:
                    pass
            else:
                logger.info(f"{self.account_name} | Кнопка 'Строительство' не найдена или не нажата")
            
        except Exception as e:
            logger.info(f"{self.account_name} | Незначительная ошибка при поиске или клике по кнопке 'Строительство': {e}")

    async def navigate_city(self):
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            await asyncio.sleep(random.uniform(*config.PAGE_LOAD_DELAY))
            city_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    f"//a[contains(@class, '_button_') and @href='/city']//div[contains(@class, '_title_') and "
                    f"(text()='{config.BUTTON_TEXTS['city']['ru']}' or text()='{config.BUTTON_TEXTS['city']['en']}')]"
                ))
            )
            
            touch_element(self.driver, city_button)
            
            initial_url = self.driver.current_url
            WebDriverWait(self.driver, 10).until(EC.url_changes(initial_url))
            new_url = self.driver.current_url

            await asyncio.sleep(random.uniform(*config.CITY_BUTTON_CLICK_DELAY))
            
            await self.find_and_click_build_button()
            
            upgrades_available = await self.upgrade_city()
            
            if not upgrades_available:
                logger.info(f"{self.account_name} | Нет доступных улучшений.")
                return True 
            
            return True
        except asyncio.CancelledError:
            logger.warning(f"{self.account_name} | Навигация по городу была отменена")
            return False
        except Exception as e:
            logger.error(f"{self.account_name} | Ошибка при навигации п городу: {e}")
            logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
        finally:
            logger.info(f"{self.account_name} | Завершение сессии")
            self.quit_driver()
        
        return False 

    def log_browser_logs(self):
        try:
            browser_logs = self.driver.get_log('browser')
            for log in browser_logs:
                logger.debug(f"{self.account_name} | Browser Log: {log}")
        except Exception as e:
            logger.error(f"{self.account_name} | Ошибка при получении браузерных логов: {e}")

    def log_performance_logs(self):
        try:
            performance_logs = self.driver.get_log('performance')
            for log in performance_logs:
                logger.debug(f"{self.account_name} | Performance Log: {log}")
        except Exception as e:
            logger.error(f"{self.account_name} | Ошибка при получении логов производительности: {e}")

    # def capture_websockets(self, output_file: str):
    #     def log_websocket_event(message):
    #         with open(output_file, 'a') as f:
    #             json.dump(message, f)
    #             f.write('\n')
        
    #     try:
    #         self.driver.execute_cdp_cmd("Network.enable", {})
    #         logger.warning(f"{self.account_name} | Захват WebSocket событий не реализован полностью.")
    #     except Exception as e:
    #         logger.error(f"{self.account_name} | Ошибка при захвате WebSocket событий: {e}")

    def check_energy_and_tap_coins(self) -> int:
        try:
            energy_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, config.SELECTORS["energy_element"]))
            )
            energy_text = energy_element.text
            energy_amount = int(energy_text.split('/')[0].strip().replace(',', ''))
            
            coin_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, config.SELECTORS["coin_image_xpath"]))
            )
            
            with gradient_progress_bar(range(energy_amount), desc=f"{self.account_name} | Тапы по монетам", total=energy_amount) as pbar:
                for _ in pbar:
                    touch_element(self.driver, coin_element)
                    time.sleep(random.uniform(0.005, 0.05))
            
            return energy_amount
        except Exception as e:
            logger.error(f"{self.account_name} | Ошибка при работе с энергией и монетами: {e}")
            return 0

    async def run(self) -> bool:
        max_retries = config.MAX_RETRIES
        retry_delay = config.RETRY_DELAY
        thread_timeout = random.randint(*config.BROWSER_THREAD_TIMEOUT)
        
        logger.info(f"{self.account_name} | Установлен таймаут потока: {thread_timeout} секунд")

        for attempt in range(max_retries):
            try:
                self.create_driver()                
                self.driver.get(self.auth_url)           
                initial_url = self.driver.current_url
                check_interval = config.NAVIGATION["check_interval"]
                max_wait_time = config.NAVIGATION["max_wait_time"]
                start_time = time.time()
                
                buttons_to_check = [
                    ("Кнопка закрытия", config.SELECTORS["close_button"]),
                    ("Кнопка 'Отлично!'", config.SELECTORS["excellent_button"]),
                    ("Кнопка 'Collect'/'Собрать'", config.SELECTORS["collect_button"]),
                    ("Кнопка 'Skip'", config.SELECTORS["skip_button"]),
                    ("Кнопка с кубиком", config.SELECTORS["dice_button"]),
                    ("Кнопка 'Create city'", config.SELECTORS["create_city_button"]),
                    ("Кнопка 'Let's start'", config.SELECTORS["lets_start_button"]),
                ]
                
                while time.time() - start_time < max_wait_time:
                    try:
                        current_url = self.driver.current_url
                        if current_url != initial_url:
                            
                            for button_name, selector in buttons_to_check:
                                try:
                                    by = By.XPATH if '//' in selector else By.CSS_SELECTOR
                                    button = WebDriverWait(self.driver, 1).until(
                                        EC.presence_of_element_located((by, selector))
                                    )
                                    touch_element(self.driver, button)
                                    await asyncio.sleep(random.uniform(*config.RANDOM_DELAY))
                                except TimeoutException:
                                    pass
                            
                            energy_amount = self.check_energy_and_tap_coins()
                            if energy_amount > 0:
                                break
                        await asyncio.sleep(check_interval)
                    except WebDriverException as e:
                        logger.error(f"{self.account_name} | Ошибка при работе с браузером: {e}")
                        break
                extract_game_stats(self.driver, self.account_name)
                await asyncio.sleep(5)
                try:
                    _ = self.driver.title
                except Exception:
                    logger.error(f"{self.account_name} | Браузер бы закрыт до начала навигации о городу")
                    return False
                navigation_completed = await self.navigate_city()
                
                if navigation_completed:
                    logger.info(f"{self.account_name} | Сессия завершена успешно")
                    return True
                else:
                    logger.error(f"{self.account_name} | Ошибка при навигации по городу")
                    return False
            
            except asyncio.CancelledError:
                logger.warning(f"{self.account_name} | Операция была отменена")
                return False
            except Exception as e:
                logger.error(f"{self.account_name} | Ошибка в BrowserManager.run: {e}")
                logger.error(f"{self.account_name} | Traceback: {traceback.format_exc()}")
                
                if attempt < max_retries - 1:
                    logger.info(f"{self.account_name} | Повторная попытка через {retry_delay} секунд...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"{self.account_name} | Достигнуто максимальное количество попыток. Завершение работы.")
                    return False
            
            finally:
                self.quit_driver()

        return False 


async def play_in_browser(account_name: str, auth_url: str, proxy: Optional[str] = None) -> bool:
    browser_manager = BrowserManager(account_name, auth_url, proxy)
    result = await browser_manager.run()
    
    if result:
        pass
    else:
        logger.error(f"{account_name} | Ошибка при работе с браузером")
    
    return result



