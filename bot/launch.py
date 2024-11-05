import argparse
import asyncio
from itertools import cycle
from colorama import init, Fore, Style
import time
import os
import platform
from pyrogram.errors import RPCError
import warnings
import logging

logging.getLogger('pyrogram').setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

init(autoreset=True)  

from bot.bot import run_cycle
from bot.logger.logger import logger
from bot.utils.common_utils import get_session_names, get_proxies, register_sessions, get_tg_clients, validate_sessions, validate_proxies
from bot.config import config
from bot.utils.session_proxy_manager import SessionProxyManager

def clear_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    clear_screen()
    
    logger.info("Found {} sessions | {} proxies".format(len(get_session_names()), len(get_proxies())))

    action = parser.parse_args().action

    if not action:
        print_colored_ascii_art()

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Invalid input! Must be a number")
            elif action not in ['1', '2']:
                logger.warning("Please select from the numbered options shown")
            else:
                action = int(action)
                break

    if action == 1:
        await register_sessions()
    elif action == 2:
        cycle_count = 0
        while True:
            cycle_count += 1
            logger.info(f"Starting cycle {cycle_count}")
            await run_tasks()
            wait_time = config.CYCLE_WAIT_TIME
            logger.info(f"Cycle {cycle_count} completed. All sessions processed.")
            logger.info(f"Sleeping for {wait_time} minutes before next cycle...")
            
            start_time = time.time()
            end_time = start_time + wait_time * 60
            
            while time.time() < end_time:
                remaining = int(end_time - time.time())
                mins, secs = divmod(remaining, 60)
                timeformat = f"{mins:02d}:{secs:02d}"
                print(f"\rTime until next cycle: {timeformat}", end="", flush=True)
                await asyncio.sleep(1)
            
            print() 
            logger.info(f"Waking up. Starting cycle {cycle_count + 1}")
            logger.info("=" * 50)


async def run_tasks():
    proxies = get_proxies()
    tg_clients = await get_tg_clients()
    lock = asyncio.Lock()
    
    logger.debug(f"Proxies before validation: {proxies}")

    proxies = await validate_proxies(proxies)
    
    if not proxies:
        logger.error("No valid proxies found. Exiting.")
        return

    tg_clients = await validate_sessions(tg_clients, proxies)
    
    if not tg_clients:
        logger.error("No valid sessions found. Exiting.")
        return

    proxy_manager = SessionProxyManager()
    
    assigned_proxies = []
    available_proxies = proxies.copy() if proxies else []
    
    for client in tg_clients:
        assigned_proxy = proxy_manager.get_proxy(client.name)
        if assigned_proxy:
            assigned_proxies.append(assigned_proxy)
        elif available_proxies:
            new_proxy = available_proxies.pop(0)
            proxy_manager.assign_proxy(client.name, new_proxy)
            assigned_proxies.append(new_proxy)
        else:
            assigned_proxies.append(None)
    
    try:
        for client in tg_clients:
            client.parse_mode = None
            client.no_updates = True
            if hasattr(client, '_handle_updates'):
                client._handle_updates = lambda *args, **kwargs: None
        
        await run_cycle(tg_clients, assigned_proxies, lock)
    except Exception as e:
        if not isinstance(e, (RPCError, KeyError, ValueError)):
            logger.error(f"Error during cycle execution: {e}")
    finally:
        for tg_client in tg_clients:
            try:
                if hasattr(tg_client, 'is_connected') and tg_client.is_connected:
                    try:
                        await tg_client.stop()
                    except Exception:
                        pass
            except Exception:
                pass
    
    logger.info("All sessions processed. Ending current cycle.")


def print_colored_ascii_art():
    start_text = f"""
{Fore.RED}ВНИМАНИЕ: Эта ферма не предназначена для продажи!{Style.RESET_ALL}
{Fore.RED}WARNING: This farm is not for sale!{Style.RESET_ALL}
{Fore.RED}¡ADVERTENCIA: ¡Esta granja no está a la venta!{Style.RESET_ALL}
{Fore.RED}ATTENTION: Cette ferme n'est pas à vendre!{Style.RESET_ALL}
{Fore.RED}ACHTUNG: Diese Farm ist nicht zum Verkauf bestimmt!{Style.RESET_ALL}
{Fore.RED}ATTENZIONE: Questa fattoria non è in vendita!{Style.RESET_ALL}
{Fore.RED}注意：この農場は販売用ではありません！{Style.RESET_ALL}
{Fore.RED}주의: 이 농장은 판매용이 아닙니다!{Style.RESET_ALL}
{Fore.RED}注意：此农场不用于销售！{Style.RESET_ALL}
{Fore.RED}ATENÇÃO: Esta fazenda não se destina à venda!{Style.RESET_ALL}


{Fore.CYAN}
 .o88b. d888888b d888888b db    db db   db  .d88b.  db      d8888b. d88888b d8888b.
d8P  Y8   `88'   `~~88~~' `8b  d8' 88   88 .8P  Y8. 88      88  `8D 88'     88  `8D
8P         88       88     `8bd8'  88ooo88 88    88 88      88   88 88ooooo 88oobY'
8b         88       88       88    88~~~88 88    88 88      88   88 88~~~~~ 88`8b  
Y8b  d8   .88.      88       88    88   88 `8b  d8' 88booo. 88  .8D 88.     88 `88.
 `Y88P' Y888888P    YP       YP    YP   YP  `Y88P'  Y88888P Y8888D' Y88888P 88   YD
{Style.RESET_ALL}
{Fore.YELLOW}Select action:{Style.RESET_ALL}

    {Fore.GREEN}1. Create session{Style.RESET_ALL}
    {Fore.GREEN}2. Launch clicker{Style.RESET_ALL}

{Fore.CYAN}Developed by: @Mffff4{Style.RESET_ALL}
{Fore.CYAN}Our Telegram channel: {Fore.BLUE}https://t.me/+l3roJWT9aRNkMjUy{Style.RESET_ALL}
"""
    print(start_text)

if __name__ == "__main__":
    print_colored_ascii_art()
