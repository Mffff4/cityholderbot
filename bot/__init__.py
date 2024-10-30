import os
import pathlib
import shutil
import platform
import subprocess
from typing import Optional

from bot.config import config
from bot.logger.logger import logger

def is_docker():
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))

def get_chrome_version() -> Optional[str]:
    try:
        system = platform.system()
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version.split('.')[0]
        elif system == "Linux":
            for browser in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
                try:
                    output = subprocess.check_output([browser, '--version']).decode()
                    version = output.split()[1].split('.')[0] 
                    return version
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        elif system == "Darwin": 
            try:
                output = subprocess.check_output(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'])
                return output.decode().split()[2].split('.')[0]
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
    except Exception as e:
        logger.warning(f"Не удалось определить версию Chrome: {e}")
    return None

def setup_webdriver():
    if is_docker():
        logger.info("Обнаружено Docker окружение, пропускаем скачивание webdriver")
        return

    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        chrome_version = get_chrome_version()
        if chrome_version:
            logger.info(f"Обнаружена версия Chrome: {chrome_version}")
            
            pathlib.Path("webdriver").mkdir(parents=True, exist_ok=True)
            
            # Используем новый синтаксис для установки конкретной версии
            driver_manager = ChromeDriverManager()
            driver_path = driver_manager.install()
            
            target_path = f"webdriver/{os.path.basename(driver_path)}"
            shutil.copy2(driver_path, target_path)
            os.chmod(target_path, 0o755) 
            logger.info(f"WebDriver успешно установлен: {target_path}")
        else:
            logger.warning("Не удалось определить версию Chrome, попытка установки последней версии драйвера")
            driver_path = ChromeDriverManager().install()
            target_path = f"webdriver/{os.path.basename(driver_path)}"
            shutil.copy2(driver_path, target_path)
            os.chmod(target_path, 0o755)
            
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
