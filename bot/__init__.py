import os
import sys
import platform
from pathlib import Path
from playwright.sync_api import sync_playwright
from bot.logger.logger import logger

def is_docker():
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))

def is_browser_installed():
    if platform.system() == 'Windows':
        user_home = os.path.expanduser('~')
        browser_path = Path(user_home) / 'AppData' / 'Local' / 'ms-playwright'
        if not browser_path.exists():
            return False
        
        chromium_dirs = list(browser_path.glob('chromium-*'))
        if not chromium_dirs:
            return False
            
        chrome_exe = chromium_dirs[0] / 'chrome.exe'
        return chrome_exe.exists()
    return False

def setup_browser():
    if is_docker():
        logger.info("Docker environment detected, skipping browser check")
        return

    try:
        import subprocess

        if platform.system() == 'Linux':
            logger.info("Linux detected, checking dependencies...")
            try:
                # Сначала проверяем, можем ли мы использовать sudo
                try:
                    subprocess.run(['sudo', '-n', 'true'], check=True, capture_output=True)
                    use_sudo = True
                except:
                    use_sudo = False
                    logger.info("No sudo access, trying without sudo...")

                # Список необходимых пакетов
                required_packages = [
                    'libatk1.0-0', 'libatk-bridge2.0-0', 'libcups2', 'libdbus-1-3',
                    'libdrm2', 'libgbm1', 'libasound2', 'libatspi2.0-0', 'libxcomposite1',
                    'libxdamage1', 'libxfixes3', 'libxrandr2', 'libpango-1.0-0', 'libcairo2',
                    'libnss3', 'libnspr4', 'libxss1', 'fonts-liberation', 'libappindicator3-1',
                    'libgconf-2-4', 'libgtk-3-0'
                ]

                # Пытаемся установить через playwright
                logger.info("Installing browser dependencies through playwright...")
                try:
                    subprocess.run([sys.executable, '-m', 'playwright', 'install-deps'], 
                                 check=True, capture_output=True)
                    logger.info("Playwright dependencies installed successfully")
                except subprocess.CalledProcessError:
                    logger.warning("Failed to install through playwright, continuing...")

                # Пытаемся установить через apt если есть sudo
                if use_sudo:
                    try:
                        # Проверяем, не запущен ли другой процесс apt
                        subprocess.run(['sudo', 'lsof', '/var/lib/dpkg/lock-frontend'], 
                                    check=True, capture_output=True)
                        logger.warning("Another package manager process is running, skipping apt installation")
                    except subprocess.CalledProcessError:
                        # Если процесс не запущен, пытаемся установить
                        try:
                            subprocess.run(['sudo', 'apt-get', 'update', '-y'], 
                                         check=True, capture_output=True)
                            subprocess.run(['sudo', 'apt-get', 'install', '-y'] + required_packages, 
                                         check=True, capture_output=True)
                            logger.info("System dependencies installed successfully")
                        except subprocess.CalledProcessError as e:
                            logger.warning(f"Failed to install through apt: {e}")

                # Устанавливаем браузер
                logger.info("Installing Chromium browser...")
                subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], 
                             check=True, capture_output=True)
                logger.info("Chromium browser installed successfully")

            except Exception as e:
                logger.error(f"Error during dependency installation: {e}")
                logger.info("You may need to install dependencies manually:")
                logger.info("1. Run: python -m playwright install-deps")
                logger.info("2. Run: python -m playwright install chromium")
                return

        if platform.system() == 'Windows':
            logger.info("Windows detected, checking installation...")
            
            if is_browser_installed():
                logger.info("Chromium browser already installed, skipping installation")
            else:
                logger.info("Installing dependencies...")
                
                try:
                    logger.info("Installing MS Visual C++ runtime and Playwright dependencies...")
                    subprocess.run([sys.executable, '-m', 'playwright', 'install-deps'], 
                                 check=True, 
                                 capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to install MS Visual C++ runtime: {e}")
                    logger.info("Please install Microsoft Visual C++ Redistributable manually")
                    logger.info("Download link: https://aka.ms/vs/17/release/vc_redist.x64.exe")
                    return

                try:
                    logger.info("Installing Chromium browser...")
                    subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'],
                                 check=True,
                                 capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to install Chromium: {e}")
                    logger.info("Try these steps manually:")
                    logger.info("1. Run: python -m playwright install chromium")
                    logger.info("2. If that fails, run as administrator")
                    return
        else:
            try:
                logger.info("Checking Playwright browsers...")
                subprocess.run(['playwright', 'install', 'chromium'], check=True)
                logger.info("Playwright browsers installed successfully")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install browsers automatically: {e}")
                logger.info("Try running manually: playwright install")
                return
            except FileNotFoundError:
                logger.warning("Playwright not found in system")
                logger.info("Install Playwright: pip install playwright")
                logger.info("Then install browsers: playwright install")
                return

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--headless=new"
                ]
            )
            browser.close()
            logger.info("Playwright tested successfully")
                
    except Exception as e:
        logger.error(f"Browser setup error: {e}")
        logger.info("Make sure Playwright is installed correctly")
        if platform.system() == 'Windows':
            logger.info("\nFor Windows users:")
            logger.info("1. Make sure you have Microsoft Visual C++ Redistributable installed")
            logger.info("2. Try running the command prompt as administrator")
            logger.info("3. Run: python -m playwright install chromium")

if not os.path.exists("sessions"):
    os.makedirs("sessions")

setup_browser()

class InvalidSession(Exception):
    pass
