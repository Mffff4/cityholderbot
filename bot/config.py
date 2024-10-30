from typing import List, Dict, Tuple, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    SLEEP_TIME: List[int] = [1900, 2000]
    USE_PROXY_FROM_FILE: bool = False
    FULL_LOG_INFO: bool = False
    REF_ID: int = 228618799
    LOGGER_FORMAT: str = "{message}"

    RANDOM_DELAY: List[float] = [0.5, 3.0]
    BROWSER_THREAD_TIMEOUT: List[int] = [600, 1800]
    BROWSER_CREATION_TIMEOUT: List[int] = [120, 300]
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    PAGE_LOAD_DELAY: List[int] = [2, 4]
    CITY_BUTTON_CLICK_DELAY: List[int] = [3, 5]
    BUILD_BUTTON_CLICK_DELAY: List[int] = [2, 4]

    SCRIPT_TIMEOUT: List[int] = [600, 1800]

    BUTTON_TEXTS: Dict[str, Dict[str, str]] = {
        "city": {"ru": "Ваш город", "en": "Your City"},
        "build": {"ru": "Строительство", "en": "Construction"},
        "excellent": {"ru": "Отлично!", "en": "Excellent!"},
        "collect": {"ru": "Собрать", "en": "Collect"},
        "skip": {"ru": "Пропустить", "en": "Skip"},
        "create_city": {"ru": "Создать город", "en": "Create city"},
        "lets_start": {"ru": "Начнем", "en": "Let's start"}
    }

    SELECTORS: Dict[str, str] = {
        "close_button": "div._closeButton_1lie3_16",
        "excellent_button": "//button[contains(@class, '_button_afxdk_1') and contains(@class, '_primary_afxdk_25') and contains(@class, '_normal_afxdk_194') and (text()='Отлично!' or text()='Excellent!')]",
        "collect_button": "//button[contains(@class, '_button_afxdk_1') and (contains(text(), 'Collect') or contains(text(), 'Собрать'))]",
        "skip_button": "//button[contains(@class, '_button_afxdk_1') and (text()='Skip' or text()='Пропустить')]",
        "dice_button": "//button[contains(@class, '_diceBtn_bm9n3_93')]",
        "create_city_button": "//button[contains(@class, '_button_afxdk_1') and contains(@class, '_primary_afxdk_25') and contains(@class, '_normal_afxdk_194') and (text()='Create city' or text()='Создать город')]",
        "lets_start_button": "//button[contains(@class, '_button_afxdk_1') and contains(@class, '_primary_afxdk_25') and contains(@class, '_normal_afxdk_194') and (text()=\"Let's start\" or text()='Начнем')]",
        "energy_element": "energy",
        "coin_image_xpath": "//img[@src='/assets/coin-CWjfuPAG.png']",
        "build_button_xpath": "a._btnBuildWrapper_xw841_23[href='/city/build']"
    }

    PROXY: Optional[str] = None

    MOBILE_USER_AGENT: str = "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36"
    WINDOW_SIZE: Tuple[int, int] = (375, 812)
    HEADLESS: bool = True
    LANGUAGE: str = "ru-RU"
    SCRIPT_UPGRADE_MAX_EXECUTION_TIME: int = 180000
    SCRIPT_UPGRADE_NO_CHANGE_TIMEOUT: int = 30000
    SCRIPT_UPGRADE_SLEEP_TIMES: Dict[str, int] = {
        "click_delay": 2000,
        "post_click_delay": 1500,
        "final_delay": 1000
    }
    NETWORK_HEADERS: Dict[str, str] = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://web.telegram.org/",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://web.telegram.org"
    }
    NAVIGATION: Dict[str, float] = {
        "max_wait_time": 10,
        "check_interval": 0.5
    }

    PAGE_LOAD_TIMEOUT: int = 30
    NAVIGATION_TIMEOUT: int = 30

config = Config()
