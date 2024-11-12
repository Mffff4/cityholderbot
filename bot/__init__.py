import os
import sys
import platform
from pathlib import Path
from playwright.sync_api import sync_playwright
from bot.logger.logger import logger
import glob

def is_docker():
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))

def is_browser_installed_linux():
    try:
        # Проверяем наличие установленного браузера Chromium
        browser_paths = [
            "~/.cache/ms-playwright/chromium-*/chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
        ]
        
        for path in browser_paths:
            expanded_path = os.path.expanduser(path)
            if glob.glob(expanded_path):
                return True
        return False
    except Exception:
        return False

def setup_browser():
    if is_docker():
        logger.info("Docker environment detected, skipping browser check")
        return

    try:
        import subprocess

        if platform.system() == 'Linux':
            logger.info("Linux detected, checking browser installation...")
            
            # Сначала проверяем, установлен ли уже браузер
            if is_browser_installed_linux():
                logger.info("Browser already installed, skipping installation")
                return
            
            logger.info("Browser not found, installing dependencies...")
            
            try:
                # Пытаемся установить только браузер через playwright
                subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], 
                             check=True, capture_output=True)
                logger.info("Chromium browser installed successfully")
                return
            except subprocess.CalledProcessError:
                logger.warning("Failed to install browser through playwright")
            
            # Если установка через playwright не удалась, пробуем через apt
            try:
                subprocess.run(['sudo', '-n', 'true'], check=True, capture_output=True)
                use_sudo = True
            except:
                use_sudo = False
                logger.info("No sudo access, skipping system installation")
                return

            if use_sudo:
                try:
                    # Проверяем блокировку apt
                    if os.path.exists('/var/lib/dpkg/lock-frontend'):
                        logger.warning("Package manager is locked, skipping installation")
                        return
                    
                    # Минимальный набор пакетов для работы браузера
                    minimal_packages = [
                        'chromium-browser',
                        'libnss3',
                        'libgbm1',
                        'libxshmfence1'
                    ]
                    
                    subprocess.run(['sudo', 'apt-get', 'install', '-y'] + minimal_packages, 
                                 check=True, capture_output=True)
                    logger.info("System browser installed successfully")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to install system browser: {e}")
                    logger.info("Please install browser manually:")
                    logger.info("sudo apt-get install chromium-browser")
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
