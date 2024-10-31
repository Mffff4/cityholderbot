import asyncio
from random import randint
import traceback

from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from pyrogram import Client

from bot import InvalidSession
from bot.logger.logger import logger
from bot.utils.common_utils import getTgWebAppData, check_proxy, escape_html
from bot.utils.webdriver_utils import play_in_browser
from bot.config import config


class Bot:

    def __init__(self, tg_client: Client, lock: asyncio.Lock):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.tg_web_data = None
        self.lock = lock
        self.first_join = True

    async def run(self, proxy) -> None:
        try:
            proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
            http_client = CloudflareScraper(connector=proxy_conn)

            if proxy:
                await check_proxy(self.session_name, http_client=http_client, proxy=proxy)

            self.tg_web_data = await getTgWebAppData(
                tg_client=self.tg_client,
                proxy=proxy
            )
            while True:
                logger.debug(f"URL address {self.session_name} | {self.tg_web_data}")

                async with self.lock:
                    play_in_browser(self.session_name, self.tg_web_data, proxy)
                sleep = randint(config.SLEEP_TIME[0], config.SLEEP_TIME[1])
                await asyncio.sleep(delay=sleep)
        except Exception as e:
            logger.error(f"Unexpected error in bot {self.session_name}: {escape_html(e)}")
            raise


async def start(tg_client: Client, proxy: str | None, lock: asyncio.Lock) -> None:
    try:
        tg_client.parse_mode = None
        if hasattr(tg_client, '_handle_updates'):
            tg_client._handle_updates = lambda *args, **kwargs: None
            
        await tg_client.start()
        
        auth_url = await getTgWebAppData(tg_client, proxy)
        
        if not auth_url:
            return None

        async with lock:
            result = await play_in_browser(tg_client.name, auth_url, proxy)
        
        if result:
            logger.info(f"{tg_client.name} | Session completed successfully")
        else:
            logger.error(f"{tg_client.name} | Error during session execution")

    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid session")
    except Exception as error:
        logger.error(f"{tg_client.name} | Unknown error: {error}")
        logger.error(f"{tg_client.name} | Traceback: {traceback.format_exc()}")
    finally:
        try:
            if tg_client.is_connected:
                await tg_client.stop()
        except Exception as e:
            logger.error(f"{tg_client.name} | Error while closing client: {e}")

async def run_cycle(tg_clients, proxies, lock):
    tasks = []
    for tg_client, proxy in zip(tg_clients, proxies):
        task = asyncio.create_task(start(tg_client, proxy, lock))
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.warning("Cycle was cancelled")
    except Exception as e:
        logger.error(f"Error during cycle execution: {e}")
    finally:
        for tg_client in tg_clients:
            try:
                if tg_client.is_connected:
                    await tg_client.stop()
                    logger.info(f"{tg_client.name} | Pyrogram session closed after cycle")
            except Exception as e:
                logger.warning(f"{tg_client.name} | Error while closing Pyrogram session: {e}")
