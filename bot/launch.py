import argparse
import asyncio
from itertools import cycle
from colorama import init, Fore, Style
import logging
import sys
import time

init(autoreset=True)  

from bot.bot import run_cycle
from bot.logger.logger import logger
from bot.utils.common_utils import get_session_names, get_proxies, register_sessions, get_tg_clients

async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    logger.info("Обнаружено {} сессий | {} прокси".format(len(get_session_names()), len(get_proxies())))

    action = parser.parse_args().action

    if not action:
        print_colored_ascii_art()

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Неправильный ответ! Это должно быть число")
            elif action not in ['1', '2']:
                logger.warning("Ну и для кого я выводил этот список? Там же они пронумированы")
            else:
                action = int(action)
                break

    if action == 1:
        await register_sessions()
    elif action == 2:
        cycle_count = 0
        while True:
            cycle_count += 1
            logger.info(f"Начинаю цикл {cycle_count}")
            await run_tasks()
            wait_time = 10 
            logger.info(f"Цикл {cycle_count} завершен. Все сессии обработаны.")
            logger.info(f"Ухожу в сон на {wait_time} минут перед следующим циклом...")
            
            start_time = time.time()
            end_time = start_time + wait_time * 60
            
            while time.time() < end_time:
                remaining = int(end_time - time.time())
                mins, secs = divmod(remaining, 60)
                timeformat = f"{mins:02d}:{secs:02d}"
                print(f"\rДо следующего цикла осталось: {timeformat}", end="", flush=True)
                await asyncio.sleep(1)
            
            print() 
            logger.info(f"Просыпаюсь. Начинаю цикл {cycle_count + 1}")
            logger.info("=" * 50)


async def run_tasks():
    proxies = get_proxies()
    tg_clients = await get_tg_clients()
    lock = asyncio.Lock()
    proxies_cycle = cycle(proxies) if proxies else None
    
    try:
        await run_cycle(tg_clients, [next(proxies_cycle) if proxies_cycle else None for _ in tg_clients], lock)
    except Exception as e:
        logger.error(f"Ошибка при выполнении цикла: {e}")
    finally:
        for tg_client in tg_clients:
            try:
                if tg_client.is_connected:
                    await tg_client.stop()
            except Exception as e:
                logger.warning(f"Ошибка при закрытии клиента {tg_client.name}: {e}")
    
    logger.info("Все сессии обработаны. Завершаем текущий цикл.")


def print_colored_ascii_art():
    ascii_art = [
        " .o88b. d888888b d888888b db    db db   db  .d88b.  db      d8888b. d88888b d8888b.",
        "d8P  Y8   `88'   `~~88~~' `8b  d8' 88   88 .8P  Y8. 88      88  `8D 88'     88  `8D",
        "8P         88       88     `8bd8'  88ooo88 88    88 88      88   88 88ooooo 88oobY'",
        "8b         88       88       88    88~~~88 88    88 88      88   88 88~~~~~ 88`8b  ",
        "Y8b  d8   .88.      88       88    88   88 `8b  d8' 88booo. 88  .8D 88.     88 `88.",
        " `Y88P' Y888888P    YP       YP    YP   YP  `Y88P'  Y88888P Y8888D' Y88888P 88   YD"
    ]

    divider = len(ascii_art) // 2

    for i, line in enumerate(ascii_art):
        if i < divider:
            print(Fore.WHITE + line)
        else:
            print(Fore.YELLOW + line)

    print(Style.RESET_ALL)  
    print(Fore.WHITE + "\nСделал: @mffff4 с любовью")
    print(Fore.YELLOW + "\n1. Создать новую сессию")
    print(Fore.YELLOW + "2. Запустить бота")

if __name__ == "__main__":
    print_colored_ascii_art()
