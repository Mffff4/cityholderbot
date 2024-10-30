import asyncio
from random import randint
import traceback

from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from pyrogram import Client
from pyrogram.errors import UserNotParticipant

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

    async def CONFIRM_TASK_EXPERIMENTAL(self):
        async with self.tg_client:
            self.user_id = (await self.tg_client.get_me()).id
            await self.tg_client.join_chat("fueljetton")
            await asyncio.sleep(5)
            if not config.CONFIRM_TASK_EXPERIMENTAL:
                return
            
            
            channels_id = [
                "coin_summer", "farmfrog", "open_gamester",
                "Coindigs", "hmlogovo", "crypto_h0me", "crypto_dr1ve",
                "icryptotea", "mem_notcoin", "crypto_jeman", "Crypto_Woolf", "fueljetton_en", "vodkatokensol",
                "Meme_AI_Mema", "tonographia"
            ]
            for channel_id in channels_id:
                try:
                    member = await self.tg_client.get_chat_member(channel_id, self.user_id)
                    if member.status not in ["member", "administrator", "creator"]:
                        await self.tg_client.join_chat(channel_id)
                        logger.info(
                            f"📜 <yellow><u>{self.tg_client.name}</u></yellow> | Начинаю подписываться на канал @{channel_id} для таска")
                        await asyncio.sleep(5)
                except UserNotParticipant:
                    await self.tg_client.join_chat(channel_id)
                    logger.info(
                        f"📜 <yellow><u>{self.tg_client.name}</u></yellow> | Начинаю подписываться на канал @{channel_id} для таска")
                    await asyncio.sleep(5)

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
                logger.debug(f"URL адрес {self.session_name} | {self.tg_web_data}")

                async with self.lock:
                    play_in_browser(self.session_name, self.tg_web_data, proxy)
                sleep = randint(config.SLEEP_TIME[0], config.SLEEP_TIME[1])
                await asyncio.sleep(delay=sleep)
        except Exception as e:
            logger.error(f"Неожиданная ошибка в боте {self.session_name}: {escape_html(e)}")
            raise


async def start(tg_client: Client, proxy: str | None, lock: asyncio.Lock) -> None:
    try:
        await tg_client.start()
        
        auth_url = await getTgWebAppData(tg_client, proxy)
        
        if not auth_url:
            return None

        async with lock:
            result = await play_in_browser(tg_client.name, auth_url, proxy)
        
        if result:
            logger.info(f"{tg_client.name} | Сессия успешно завершена")
        else:
            logger.error(f"{tg_client.name} | Ошибка при выполнении сессии")

    except InvalidSession:
        logger.error(f"{tg_client.name} | Невалидная сессия")
    except Exception as error:
        logger.error(f"{tg_client.name} | Неизвестная ошибка: {error}")
        logger.error(f"{tg_client.name} | Traceback: {traceback.format_exc()}")
    finally:
        try:
            if tg_client.is_connected:
                await tg_client.stop()
        except Exception as e:
            logger.error(f"{tg_client.name} | Ошибка при закрытии клиента: {e}")

async def run_cycle(tg_clients, proxies, lock):
    tasks = []
    for tg_client, proxy in zip(tg_clients, proxies):
        task = asyncio.create_task(start(tg_client, proxy, lock))
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.warning("Цикл был отменен")
    except Exception as e:
        logger.error(f"Ошибка во время выполнения цикла: {e}")
    finally:
        for tg_client in tg_clients:
            try:
                if tg_client.is_connected:
                    await tg_client.stop()
                    logger.info(f"{tg_client.name} | Сессия Pyrogram закрыта после цикла")
            except Exception as e:
                logger.warning(f"{tg_client.name} | Ошибка при закрытии сессии Pyrogram: {e}")
