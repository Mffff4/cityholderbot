import logging
from bot.config import config
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        levelname = record.levelname
        message = record.getMessage()
        datefmt = '%d.%m.%Y %H:%M'
        date_str = self.formatTime(record, datefmt)
        level_color = self.COLORS.get(levelname, '')
        formatted_message = f"{Fore.CYAN}{date_str}{Style.RESET_ALL} - {level_color}{levelname}{Style.RESET_ALL} - {Fore.WHITE}{message}{Style.RESET_ALL}"
        
        return formatted_message

def setup_logging():
    logger = logging.getLogger('bot')
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG if config.FULL_LOG_INFO else logging.INFO)
    handler = logging.StreamHandler()
    formatter = ColoredFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('selenium').setLevel(logging.ERROR)
    logging.getLogger('undetected_chromedriver').setLevel(logging.ERROR)

    return logger

logger = setup_logging()

def log_game_stats(account_name, stats):
    logger.info(f"{Fore.CYAN}{account_name} | Статистика игры:{Style.RESET_ALL}")
    for key, value in stats.items():
        if key in ["Доход", "Население"]:
            value = ''.join(filter(str.isdigit, value))
        logger.info(f"  {Fore.MAGENTA}{key}:{Style.RESET_ALL} {Fore.YELLOW}{value}{Style.RESET_ALL}")

def gradient_progress_bar(iterable, desc="", total=None):
    return tqdm(iterable, desc=desc, total=total, bar_format="{l_bar}{bar}", 
                colour='green')
