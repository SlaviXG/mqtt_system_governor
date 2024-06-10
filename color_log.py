from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Variable to control color logging
use_color = True


def enable_color_logging(enable: bool):
    global use_color
    use_color = enable


def log_info(message: str):
    if use_color:
        print(Fore.GREEN + message)
    else:
        print(message)


def log_warning(message: str):
    if use_color:
        print(Fore.YELLOW + message)
    else:
        print(message)


def log_error(message: str):
    if use_color:
        print(Fore.RED + message)
    else:
        print(message)
