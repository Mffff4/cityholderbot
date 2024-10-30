import os
import pathlib
import platform
import subprocess
import re
from typing import Optional
import undetected_chromedriver as uc
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import read_version_from_cmd, PATTERN
import shutil

from bot.config import config
from bot.logger.logger import logger

def is_docker():
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))

def get_chrome_version() -> Optional[tuple[int, str]]:
    try:
        system = platform.system()
        version_str = None
        
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version_str, _ = winreg.QueryValueEx(key, "version")
        elif system == "Linux":
            for browser in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
                try:
                    version_str = read_version_from_cmd(browser)
                    if version_str:
                        break
                except Exception:
                    continue
        elif system == "Darwin":
            try:
                process = subprocess.Popen(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                output, _ = process.communicate()
                version_str = output.decode('utf-8').replace('Google Chrome ', '').strip()
            except Exception:
                pass

        if version_str:
            match = re.search(PATTERN, version_str)
            if match and match.group(1):
                major_version = int(match.group(1))
                return major_version, version_str

    except Exception as e:
        logger.warning(f"Не удалось определить версию Chrome: {e}")
    return None

def setup_webdriver():
    if is_docker():
        logger.info("Обнаружено Docker окружение, пропускаем скачивание webdriver")
        return

    try:
        version_info = get_chrome_version()
        if version_info:
            major_version, full_version = version_info
            logger.info(f"Обнаружена версия Chrome: {full_version} (major: {major_version})")
            
            driver_path = ChromeDriverManager(version=f"{major_version}.0.0").install()
            logger.info(f"Установлен ChromeDriver по пути: {driver_path}")
            
            target_path = os.path.join("webdriver", os.path.basename(driver_path))
            os.makedirs("webdriver", exist_ok=True)
            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.copy2(driver_path, target_path)
            os.chmod(target_path, 0o755)
            
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            
            try:
                temp_driver = uc.Chrome(
                    driver_executable_path=target_path,
                    options=options,
                    version_main=major_version
                )
                temp_driver.quit()
                logger.info(f"WebDriver успешно протестирован")
            except Exception as e:
                logger.error(f"Ошибка при тестировании драйвера: {e}")
                raise
                
        else:
            logger.warning("Не удалось определить версию Chrome")
            
    except Exception as e:
        logger.error(f"Ошибка при установке WebDriver: {e}")
        logger.info("Продолжаем работу, предполагая что драйвер уже установлен в системе")

if not os.path.exists("sessions"):
    os.makedirs("sessions")

if not os.path.exists("webdriver"):
    os.makedirs("webdriver")

setup_webdriver()

class InvalidSession(Exception):
    pass
