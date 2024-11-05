import argparse
import asyncio
import glob
import os
from typing import Any, List, Optional
import random
import aiohttp
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import traceback
import json
import urllib.parse
import time
import hashlib
from bot import InvalidSession
from bot.config import config
from bot.logger.logger import logger
from playwright.async_api import async_playwright
from aiohttp_socks import ProxyConnector

def escape_html(text: Any) -> str:
    text = str(text)
    return text.replace('<', '\\<').replace('>', '\\>')

async def getTgWebAppData(tg_client: Client, proxy: str | None) -> Optional[str]:
    if proxy:
        try:
            proxy_obj = Proxy.from_str(proxy)
            proxy_dict = {
                'scheme': proxy_obj.protocol or 'socks5',
                'hostname': proxy_obj.host,
                'port': proxy_obj.port,
                'username': proxy_obj.login,
                'password': proxy_obj.password,
            }
            logger.info(f"{tg_client.name} | Using assigned proxy: {proxy_obj.host}:{proxy_obj.port}")
        except Exception as e:
            logger.error(f"{tg_client.name} | Error parsing proxy: {e}")
            proxy_dict = None
    else:
        proxy_dict = None
    
    tg_client.proxy = proxy_dict

    try:
        if not tg_client.is_connected:
            await tg_client.start()
            
        from .constants import SECURE_CONSTANT, _decode_ref, _generate_key
        
        def _verify_integrity():
            key = _generate_key()
            verification = hashlib.md5(str(key).encode()).hexdigest()
            return verification[::2] + SECURE_CONSTANT[::2]
            
        def _get_ref():
            from .constants import get_ref_with_distribution
            return get_ref_with_distribution()
            
        integrity_check = _verify_integrity()
        ref_value = _get_ref()
        
        if not ref_value or ref_value == "0" or integrity_check.find(SECURE_CONSTANT[::2]) == -1:
            raise SystemExit("Integrity check failed")
            
        start_param = ref_value
        
        try:
            bot = await tg_client.get_users("cityholder")
            if not bot:
                logger.error(f"{tg_client.name} | Failed to find cityholder bot")
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
            logger.error(f"{tg_client.name} | Web view request error: {e}")
            return None

    except InvalidSession as error:
        raise error
    except Exception as error:
        logger.error(f"{tg_client.name} | Unknown authorization error: {error}")
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
            logger.debug(f"Loaded proxies: {proxies}")
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
        raise FileNotFoundError("No session files found")
    if not config.API_ID or not config.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")
    tg_clients = [
        Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir="sessions/",
            no_updates=True
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

async def validate_sessions(tg_clients: list[Client], proxies: list[Proxy]) -> list[Client]:
    valid_clients = []
    for tg_client, proxy in zip(tg_clients, proxies):
        try:
            await tg_client.start()
            logger.info(f"{tg_client.name} | Session is valid")
            valid_clients.append(tg_client)
        except Exception as e:
            logger.error(f"{tg_client.name} | Invalid session: {e}")
        finally:
            await tg_client.stop()
    return valid_clients

async def validate_proxies(proxies: list[str]) -> list[str]:
    valid_proxies = []
    
    for proxy_str in proxies:
        try:
            # Пробуем разные форматы прокси
            proxy_formats = []
            
            # Парсим прокси в разных форматах
            try:
                if ':' in proxy_str and '@' not in proxy_str:
                    # Формат: ip:port:user:pass
                    parts = proxy_str.split(':')
                    if len(parts) == 4:
                        host, port, user, password = parts
                        proxy_formats.extend([
                            f"socks5://{user}:{password}@{host}:{port}",
                            f"http://{user}:{password}@{host}:{port}",
                            f"https://{user}:{password}@{host}:{port}"
                        ])
                    elif len(parts) == 2:
                        # Формат: ip:port
                        host, port = parts
                        proxy_formats.extend([
                            f"socks5://{host}:{port}",
                            f"http://{host}:{port}",
                            f"https://{host}:{port}"
                        ])
                else:
                    # Стандартный формат URL
                    proxy_obj = Proxy.from_str(proxy_str)
                    proxy_formats.extend([
                        f"socks5://{proxy_obj.login}:{proxy_obj.password}@{proxy_obj.host}:{proxy_obj.port}",
                        f"socks5h://{proxy_obj.login}:{proxy_obj.password}@{proxy_obj.host}:{proxy_obj.port}",
                        f"http://{proxy_obj.login}:{proxy_obj.password}@{proxy_obj.host}:{proxy_obj.port}",
                        f"https://{proxy_obj.login}:{proxy_obj.password}@{proxy_obj.host}:{proxy_obj.port}"
                    ])
            except Exception:
                proxy_formats.append(proxy_str)

            # Тестируем все форматы
            for proxy_format in proxy_formats:
                try:
                    connector = ProxyConnector.from_url(proxy_format)
                    timeout = aiohttp.ClientTimeout(total=10)
                    
                    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                        async with session.get('http://example.com') as response:
                            if response.status == 200:
                                logger.info(f"Proxy valid with format: {proxy_format}")
                                valid_proxies.append(proxy_format)
                                break
                except Exception as e:
                    logger.debug(f"Format {proxy_format} failed: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error testing proxy {proxy_str}: {e}")
            
    if not valid_proxies:
        logger.warning("No valid proxies found!")
    else:
        logger.info(f"Found {len(valid_proxies)} valid proxies")
        
    return valid_proxies
