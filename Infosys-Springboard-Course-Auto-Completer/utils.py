"""
Utility functions for Infosys Springboard Course Completer
"""

import sys
import logging
from pathlib import Path
from typing import Optional


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Print the application banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     🚀 Infosys Springboard Course Auto-Completer (Enhanced) 🚀       ║
║                                                                      ║
║              Complete ALL Your Course Content Instantly              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}▸ {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.ENDC}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")


def print_progress_bar(
    current: int,
    total: int,
    prefix: str = '',
    suffix: str = '',
    length: int = 50,
    decimals: int = 1
):
    """
    Print a progress bar to the console.

    Args:
        current: Current progress
        total: Total items
        prefix: Prefix text
        suffix: Suffix text
        length: Length of the progress bar
        decimals: Decimal places for percentage
    """
    if total <= 0:
        percent = 0
        filled = 0
    else:
        percent = (100 * current / float(total))
        filled = int(length * current // int(total))

    bar = '█' * filled + '░' * (length - filled)

    # Color based on progress
    if percent < 30:
        color = Colors.RED
    elif percent < 70:
        color = Colors.YELLOW
    else:
        color = Colors.GREEN

    sys.stdout.write(f'\r{prefix} {color}|{bar}|{Colors.ENDC} {percent:.{decimals}f}% {suffix}')
    sys.stdout.flush()


def format_duration(seconds: float) -> str:
    """
    Format seconds into human-readable duration.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def setup_logging(log_file: Optional[str] = None, verbose: bool = True) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_file: Path to log file (if None, logs to console only)
        verbose: If True, use DEBUG level, else INFO level

    Returns:
        Configured logger instance
    """
    # Fix encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    logger = logging.getLogger('infosys-completer')
    level = logging.DEBUG if verbose else logging.INFO

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        try:
            # Create logs directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            print_success(f"Logging to file: {log_file}")
        except Exception as e:
            print_warning(f"Could not set up file logging: {e}")

    return logger


def get_content_type_from_mime(mime_type: str) -> str:
    """
    Get content type category from MIME type.

    Args:
        mime_type: MIME type string

    Returns:
        Content type category
    """
    if not mime_type:
        return "unknown"

    mime_lower = mime_type.lower()

    if mime_lower.startswith('video/'):
        return 'video'
    elif mime_lower.startswith('audio/'):
        return 'audio'
    elif mime_lower.startswith('application/pdf'):
        return 'pdf'
    elif mime_lower.startswith('application/'):
        return 'document'
    elif mime_lower.startswith('image/'):
        return 'image'
    elif mime_lower.startswith('text/'):
        return 'text'
    else:
        return 'other'


def get_icon_for_content_type(content_type: str) -> str:
    """
    Get emoji icon for content type.

    Args:
        content_type: Content type string

    Returns:
        Emoji icon
    """
    icons = {
        'video': '🎬',
        'audio': '🎵',
        'pdf': '📄',
        'document': '📃',
        'image': '🖼️',
        'text': '📝',
        'quiz': '❓',
        'assessment': '✓',
        'discussion': '💬',
        'unknown': '❓'
    }
    return icons.get(content_type, '❓')


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user to confirm an action.

    Args:
        message: Confirmation message
        default: Default choice if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    default_str = "y/N" if not default else "Y/n"
    while True:
        response = input(f"\n{Colors.BOLD}{message} ({default_str}): {Colors.ENDC}").strip().lower()
        if response == '':
            return default
        elif response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print_warning("Please enter 'y' or 'n'")


def print_table(headers: list, rows: list, max_width: int = 70):
    """
    Print a formatted table.

    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of values)
        max_width: Maximum width for text in columns
    """
    if not rows:
        print("  (No data)")
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], min(len(str(cell)), max_width))

    # Print header
    header_str = " │ ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(f"{Colors.BOLD}{header_str}{Colors.ENDC}")
    print("─" * (len(header_str) + 4))

    # Print rows
    for row in rows:
        row_str = " │ ".join(
            f"{str(cell)[:max_width]:<{w}}" if w <= max_width else f"{str(cell)[:max_width-3]}...{' '*(w-max_width+2)}"
            for cell, w in zip(row, col_widths)
        )
        print(row_str)
