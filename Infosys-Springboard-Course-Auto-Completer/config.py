"""
Configuration Management for Infosys Springboard Course Completer
Handles environment variables, CLI prompts, and token validation.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Color codes for terminal output
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


@dataclass
class Config:
    """Configuration object holding all settings."""
    token: str
    course_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    auto_confirm: bool = False
    dry_run: bool = False
    log_file: Optional[str] = None
    verbose: bool = True


class ConfigManager:
    """Manages configuration from environment variables and user input."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            env_file: Path to .env file. If None, looks for .env in current directory.
        """
        self.env_file = env_file or ".env"
        self._load_env()

    def _load_env(self):
        """Load environment variables from .env file if it exists."""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
            print(f"{Colors.GREEN}✓{Colors.ENDC} Loaded configuration from {self.env_file}")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.ENDC} No .env file found at {self.env_file}")

    def get_config(self, skip_validation: bool = False) -> Config:
        """
        Get configuration from environment or prompt user.

        Args:
            skip_validation: If True, skip token validation

        Returns:
            Config object with all settings
        """
        # Try to get from environment first
        token = os.getenv('INFOSYS_TOKEN') or os.getenv('token')
        course_id = os.getenv('INFOSYS_COURSE_ID') or os.getenv('courseid')
        auto_confirm = os.getenv('AUTO_CONFIRM', 'false').lower() == 'true'
        dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        print(f"\n{Colors.BOLD}{Colors.CYAN}Configuration Setup{Colors.ENDC}\n")

        # Prompt for token if not in environment
        if not token:
            print(f"{Colors.CYAN}Enter your Infosys Springboard Bearer Token:{Colors.ENDC}")
            print(f"{Colors.YELLOW}(Get this from: Browser DevTools → Application → Local Storage → kc-infyspringboard){Colors.ENDC}")
            token = input(f"{Colors.CYAN}Token: {Colors.ENDC}").strip()
        else:
            print(f"{Colors.GREEN}✓{Colors.ENDC} Token loaded from environment")

        if not token:
            print(f"{Colors.RED}Error: Token is required!{Colors.ENDC}")
            sys.exit(1)

        # Prompt for course ID if not in environment
        if not course_id:
            print(f"\n{Colors.CYAN}Enter the Course ID:{Colors.ENDC}")
            print(f"{Colors.YELLOW}(Get this from course URL: /toc/[COURSE_ID]/overview){Colors.ENDC}")
            course_id = input(f"{Colors.CYAN}Course ID: {Colors.ENDC}").strip()
        else:
            print(f"{Colors.GREEN}✓{Colors.ENDC} Course ID loaded from environment")

        if not course_id:
            print(f"{Colors.RED}Error: Course ID is required!{Colors.ENDC}")
            sys.exit(1)

        # Ask for options
        print(f"\n{Colors.CYAN}Options:{Colors.ENDC}")
        auto_confirm = input(f"{Colors.CYAN}Auto-confirm completion? (y/n, default: n): {Colors.ENDC}").strip().lower() == 'y'
        dry_run = input(f"{Colors.CYAN}Dry run mode? (only show what would be done, y/n, default: n): {Colors.ENDC}").strip().lower() == 'y'

        config = Config(
            token=token,
            course_id=course_id,
            auto_confirm=auto_confirm,
            dry_run=dry_run,
            log_file=os.getenv('LOG_FILE', 'course_completer.log'),
            verbose=True
        )

        return config

    @staticmethod
    def print_env_example():
        """Print example .env file format."""
        example = """# Infosys Springboard Configuration Example
# Copy this to .env and fill in your values

# Your Infosys Springboard Bearer Token
INFOSYS_TOKEN=your_bearer_token_here

# Course ID (from course URL)
INFOSYS_COURSE_ID=lex_auth_xxxxxxxxxxxxxxxxxx_shared

# Optional: Auto-confirm without prompting (default: false)
AUTO_CONFIRM=false

# Optional: Dry run mode - show what would be done without doing it (default: false)
DRY_RUN=false

# Optional: Log file path (default: course_completer.log)
LOG_FILE=course_completer.log
"""
        print(example)


def create_example_env():
    """Create .env.example file."""
    example_content = """# Infosys Springboard Course Auto-Completer Configuration

# Your Infosys Springboard Bearer Token (REQUIRED)
# Get this from: Browser DevTools → Application → Local Storage → kc-infyspringboard → token field
INFOSYS_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik...

# Course ID (REQUIRED)
# Get this from course URL: https://infyspringboard.onwingspan.com/web/en/app/toc/[COURSE_ID]/overview
INFOSYS_COURSE_ID=lex_auth_0125409616243425281061_shared

# Auto-confirm completion without user prompt (Optional, default: false)
AUTO_CONFIRM=false

# Dry run mode - show what would be done without actually doing it (Optional, default: false)
DRY_RUN=false

# Log file location (Optional, default: course_completer.log)
LOG_FILE=course_completer.log
"""

    env_example_path = Path(".env.example")
    env_example_path.write_text(example_content)
    print(f"Created {env_example_path}")
