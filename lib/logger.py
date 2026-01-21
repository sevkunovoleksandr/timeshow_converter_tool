import logging, sys
from colorama import init, Fore, Style
init(autoreset=True, strip=not sys.stdout.isatty())

logger = logging.getLogger("uvicorn.error")
def log_warning(msg):
	logger.warning(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
def log_info_colored(color, msg):
	logger.info(f"{color}{msg}{Style.RESET_ALL}")
def log_info(msg):
	log_info_colored(Fore.LIGHTYELLOW_EX, msg)
def log_important(msg):
	log_info_colored(Fore.MAGENTA, msg)