import os
import pathlib
import shutil
import platform

from bot.config import config
from bot.logger.logger import logger

def is_docker():
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))

def setup_webdriver():
    if is_docker():
        logger.info("Обнаружено Docker окружение, пропускаем скачивание webdriver")
        return

    if not pathlib.Path("webdriver").exists() or len(list(pathlib.Path("webdriver").iterdir())) == 0:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("Downloading webdriver. It may take some time...")
            pathlib.Path("webdriver").mkdir(parents=True, exist_ok=True)
            
            if platform.system() == 'Windows':
                webdriver_path = pathlib.Path(ChromeDriverManager().install())
                shutil.move(str(webdriver_path), f"webdriver/{webdriver_path.name}")
            else:
                chrome_path = None
                for path in ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome']:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                
                if chrome_path:
                    webdriver_path = pathlib.Path(ChromeDriverManager(chrome_type='chromium').install())
                    shutil.move(str(webdriver_path), f"webdriver/{webdriver_path.name}")
                else:
                    logger.warning("Chrome/Chromium не найден в системе")
                    
            print("Webdriver downloaded successfully")
        except Exception as e:
            logger.warning(f"Ошибка при скачивании webdriver: {e}")
            logger.info("Продолжаем работу, предполагая что драйвер уже установлен в системе")
    
if not os.path.exists("sessions"):
    os.makedirs("sessions")

if not os.path.exists("webdriver"):
    os.makedirs("webdriver")

setup_webdriver()

class InvalidSession(Exception):
    pass
