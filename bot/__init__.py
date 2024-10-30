import os
import pathlib
import platform
import subprocess
import re
from typing import Optional
import undetected_chromedriver as uc
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import shutil

from bot.config import config
from bot.logger.logger import logger

def is_docker():
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))

def get_chrome_version() -> Optional[tuple[int, str]]:
    """Возвращает (major_version: int, full_version: str)"""
    try:
        system = platform.system()
        version_str = None
        chrome_version_pattern = r'(\d+)\.(\d+)\.(\d+)\.?(\d*)'
        
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version_str, _ = winreg.QueryValueEx(key, "version")
        elif system == "Linux":
            for browser in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
                try:
                    output = subprocess.check_output([browser, '--version']).decode()
                    match = re.search(r'[\d.]+', output)
                    if match:
                        version_str = match.group(0)
                        break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        elif system == "Darwin":
            try:
                process = subprocess.Popen(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                output, _ = process.communicate()
                match = re.search(r'[\d.]+', output.decode('utf-8'))
                if match:
                    version_str = match.group(0)
            except Exception:
                pass

        if version_str:
            match = re.search(chrome_version_pattern, version_str)
            if match:
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
            
            os.makedirs("webdriver", exist_ok=True)
            
            try:
                driver_manager = ChromeDriverManager()
                driver_path = driver_manager.install()
                
                target_path = os.path.join("webdriver", os.path.basename(driver_path))
                if os.path.exists(target_path):
                    os.remove(target_path)
                shutil.copy2(driver_path, target_path)
                os.chmod(target_path, 0o755)
                
                logger.info(f"ChromeDriver успешно установлен в {target_path}")
                
                options = uc.ChromeOptions()
                options.add_argument("--headless=new")
                
                temp_driver = uc.Chrome(
                    driver_executable_path=target_path,
                    options=options,
                    version_main=major_version
                )
                temp_driver.quit()
                logger.info("ChromeDriver успешно протестирован")
                
            except Exception as e:
                logger.error(f"Ошибка при установке/тестировании ChromeDriver: {e}")
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
