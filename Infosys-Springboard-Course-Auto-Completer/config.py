"""
Configuration Management for Infosys Springboard Course Completer
Handles environment variables, CLI prompts, and token validation.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from urllib.parse import parse_qs, unquote, urlparse
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
    course_id: Optional[str] = None
    course_ids: Optional[List[str]] = None
    target_type: str = "course"
    playlist_id: Optional[str] = None
    playlist_title: Optional[str] = None
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

    @staticmethod
    def _is_truthy(value: Optional[str]) -> bool:
        """Parse common truthy env values."""
        if value is None:
            return False

        return value.strip().lower() in {"1", "true", "yes", "y", "on"}

    @staticmethod
    def _extract_playlist_id(value: str) -> Optional[str]:
        """Extract playlist UUID from either playlist URL or raw UUID input."""
        if not value:
            return None

        value = value.strip()
        if not value:
            return None

        direct_match = re.fullmatch(r"[0-9a-fA-F-]{36}", value)
        if direct_match:
            return direct_match.group(0)

        url_match = re.search(r"/playlist/me/([0-9a-fA-F-]{36})", value)
        if url_match:
            return url_match.group(1)

        return None

    @staticmethod
    def _split_course_references(value: str) -> List[str]:
        """Split mixed IDs/URLs while preserving commas inside URL query values."""
        if not value:
            return []

        references: List[str] = []
        text = value.strip()
        index = 0
        length = len(text)

        while index < length:
            # Skip leading separators/whitespace.
            while index < length and text[index] in " \t\r\n,;":
                index += 1
            if index >= length:
                break

            if text.startswith("http://", index) or text.startswith("https://", index):
                start = index
                index += 1

                while index < length:
                    char = text[index]

                    if char in "\r\n;":
                        break

                    # Treat comma as URL separator only when another URL follows.
                    if char == ",":
                        lookahead = index + 1
                        while lookahead < length and text[lookahead].isspace():
                            lookahead += 1

                        if text.startswith("http://", lookahead) or text.startswith("https://", lookahead):
                            break

                    index += 1

                token = text[start:index].strip().rstrip(",")
                if token:
                    references.append(token)

                continue

            start = index
            while index < length and text[index] not in ",;\r\n":
                index += 1

            token = text[start:index].strip()
            if token:
                references.append(token)

        return references

    @staticmethod
    def _parse_course_ids(value: str) -> List[str]:
        """Parse one or many course IDs from env/input text."""
        if not value:
            return []

        raw_tokens = ConfigManager._split_course_references(value)
        ids: List[str] = []
        seen = set()

        for token in raw_tokens:
            course_id = ConfigManager._extract_course_id_from_reference(token)
            if not course_id or course_id in seen:
                continue

            seen.add(course_id)
            ids.append(course_id)

        return ids

    @staticmethod
    def _extract_course_id_from_reference(value: str) -> Optional[str]:
        """Extract parent course ID from raw ID, TOC URL, or viewer URL."""
        if not value:
            return None

        reference = unquote(value.strip())
        if not reference:
            return None

        # Course overview URL: /toc/<course_id>/overview
        toc_match = re.search(r"/toc/([^/?#]+)", reference)
        if toc_match:
            return toc_match.group(1).strip()

        # Viewer URL: parent course ID lives in query param collectionId.
        parsed = urlparse(reference)
        query = parse_qs(parsed.query)
        collection_id = (query.get("collectionId") or [None])[0]
        collection_type = (query.get("collectionType") or [None])[0]
        if collection_id and (not collection_type or collection_type.lower() == "course"):
            return collection_id.strip()

        # Fallback for copied query strings that are not full URLs.
        cid_match = re.search(r"(?:\?|&)collectionId=([^&#]+)", reference)
        ctype_match = re.search(r"(?:\?|&)collectionType=([^&#]+)", reference)
        if cid_match:
            ctype = ctype_match.group(1).strip().lower() if ctype_match else "course"
            if ctype == "course":
                return cid_match.group(1).strip()

        # Raw course ID input.
        if re.fullmatch(r"lex(?:_auth)?_[A-Za-z0-9]+_shared", reference):
            return reference

        return None

    @staticmethod
    def _merge_course_ids(values: List[str]) -> List[str]:
        """Parse and merge unique course IDs from many env/input values."""
        merged: List[str] = []
        seen = set()

        for value in values:
            for course_id in ConfigManager._parse_course_ids(value):
                if course_id in seen:
                    continue
                seen.add(course_id)
                merged.append(course_id)

        return merged

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
        course_ids = self._merge_course_ids([
            os.getenv('INFOSYS_COURSE_IDS') or os.getenv('courseids') or "",
            os.getenv('INFOSYS_COURSE_ID') or os.getenv('courseid') or "",
            os.getenv('INFOSYS_TARGET_URLS') or os.getenv('targeturls') or "",
            os.getenv('INFOSYS_TARGET_URL') or os.getenv('targeturl') or "",
        ])
        course_id = course_ids[0] if course_ids else None
        env_target_type = (os.getenv('TARGET_TYPE') or "").strip().lower()
        playlist_raw = (
            os.getenv('INFOSYS_PLAYLIST_ID')
            or os.getenv('playlistid')
            or os.getenv('INFOSYS_PLAYLIST_URL')
            or os.getenv('playlisturl')
            or ""
        )
        playlist_id = self._extract_playlist_id(playlist_raw)
        auto_confirm = self._is_truthy(os.getenv('AUTO_CONFIRM', 'false'))
        dry_run = self._is_truthy(os.getenv('DRY_RUN', 'false'))
        non_interactive = self._is_truthy(os.getenv('NON_INTERACTIVE', 'false'))

        # Non-interactive mode is intended for GUI/automation integrations.
        if non_interactive:
            if not token:
                print(f"{Colors.RED}Error: Token is required in non-interactive mode!{Colors.ENDC}")
                sys.exit(1)

            default_target = 'playlist' if (env_target_type == 'playlist' or playlist_id) else 'course'
            target_type = env_target_type if env_target_type in {'course', 'playlist'} else default_target

            if target_type == 'course' and not course_ids:
                print(f"{Colors.RED}Error: At least one valid Course ID/URL is required in non-interactive course mode!{Colors.ENDC}")
                sys.exit(1)

            if target_type == 'playlist' and not playlist_id:
                print(f"{Colors.RED}Error: Playlist ID/URL is required in non-interactive playlist mode!{Colors.ENDC}")
                sys.exit(1)

            return Config(
                token=token,
                course_id=course_id,
                course_ids=course_ids,
                target_type=target_type,
                playlist_id=playlist_id,
                auto_confirm=auto_confirm,
                dry_run=dry_run,
                log_file=os.getenv('LOG_FILE', 'course_completer.log'),
                verbose=True
            )

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

        # Determine target mode (single course vs playlist)
        default_target = 'playlist' if (env_target_type == 'playlist' or playlist_id) else 'course'

        print(f"\n{Colors.CYAN}Target Type:{Colors.ENDC}")
        print("  1) Single Course")
        print("  2) Playlist")
        default_choice = "2" if default_target == 'playlist' else "1"
        target_choice = input(
            f"{Colors.CYAN}Choose target type (1/2, default: {default_choice}): {Colors.ENDC}"
        ).strip()

        if target_choice == '2':
            target_type = 'playlist'
        elif target_choice == '1':
            target_type = 'course'
        else:
            target_type = default_target

        if target_type == 'course':
            if not course_ids:
                print(f"\n{Colors.CYAN}Enter Course ID(s) or URL(s):{Colors.ENDC}")
                print(f"{Colors.YELLOW}(Supports raw course IDs, TOC URLs, and viewer URLs){Colors.ENDC}")
                print(f"{Colors.YELLOW}(Use comma/newline/semicolon separated values for multiple targets){Colors.ENDC}")
                course_input = input(f"{Colors.CYAN}Course ID(s)/URL(s): {Colors.ENDC}").strip()
                course_ids = self._parse_course_ids(course_input)
                course_id = course_ids[0] if course_ids else None
            else:
                if len(course_ids) == 1:
                    print(f"{Colors.GREEN}✓{Colors.ENDC} Course target loaded from environment")
                else:
                    print(f"{Colors.GREEN}✓{Colors.ENDC} {len(course_ids)} course targets loaded from environment")

            if not course_ids:
                print(f"{Colors.RED}Error: At least one valid Course ID/URL is required in course mode!{Colors.ENDC}")
                sys.exit(1)
        else:
            if playlist_id:
                print(f"{Colors.GREEN}✓{Colors.ENDC} Playlist ID loaded from environment")
            else:
                print(f"\n{Colors.CYAN}Optional: Enter Playlist URL or Playlist ID{Colors.ENDC}")
                print(f"{Colors.YELLOW}(Leave blank to choose interactively from your playlists){Colors.ENDC}")
                playlist_input = input(f"{Colors.CYAN}Playlist URL/ID: {Colors.ENDC}").strip()

                if playlist_input:
                    playlist_id = self._extract_playlist_id(playlist_input)
                    if not playlist_id:
                        print(f"{Colors.RED}Error: Could not parse playlist ID from input.{Colors.ENDC}")
                        sys.exit(1)

        # Ask for options
        print(f"\n{Colors.CYAN}Options:{Colors.ENDC}")
        auto_confirm = input(f"{Colors.CYAN}Auto-confirm completion? (y/n, default: n): {Colors.ENDC}").strip().lower() == 'y'
        dry_run = input(f"{Colors.CYAN}Dry run mode? (only show what would be done, y/n, default: n): {Colors.ENDC}").strip().lower() == 'y'

        config = Config(
            token=token,
            course_id=course_id,
            course_ids=course_ids,
            target_type=target_type,
            playlist_id=playlist_id,
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

# Course IDs (single or multiple, comma-separated)
INFOSYS_COURSE_IDS=lex_auth_xxxxxxxxxxxxxxxxxx_shared,lex_auth_yyyyyyyyyyyyyyyyyy_shared

# Optional: course URL(s). Parser extracts parent course ID automatically.
# Works with:
# - TOC URL: .../toc/<course_id>/overview
# - Viewer URL: .../viewer/...?...collectionId=<parent_course_id>&collectionType=Course
# INFOSYS_TARGET_URLS=https://infyspringboard.onwingspan.com/web/en/app/toc/lex_auth_012734003600908288382_shared/overview

# Backward-compatible single course ID
# INFOSYS_COURSE_ID=lex_auth_xxxxxxxxxxxxxxxxxx_shared

# Optional: target type (course|playlist)
TARGET_TYPE=course

# Optional: playlist ID or URL when TARGET_TYPE=playlist
# INFOSYS_PLAYLIST_ID=08281524-7cdd-430c-b327-466f2d76ad74
# INFOSYS_PLAYLIST_URL=https://infyspringboard.onwingspan.com/web/en/app/playlist/me/08281524-7cdd-430c-b327-466f2d76ad74

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

# Course IDs (REQUIRED for course mode)
# Use one ID or multiple comma-separated IDs.
# Get each from course URL: https://infyspringboard.onwingspan.com/web/en/app/toc/[COURSE_ID]/overview
INFOSYS_COURSE_IDS=lex_auth_0125409616243425281061_shared

# Optional: course URL(s). Parent course ID is auto-extracted.
# INFOSYS_TARGET_URLS=https://infyspringboard.onwingspan.com/web/en/viewer/hands-on/lex_auth_0127136112798105601178_shared?collectionId=lex_auth_012734003600908288382_shared&collectionType=Course&pathId=lex_auth_0127136535829708801223_shared,lex_auth_0127136597324103681226_shared

# Backward-compatible single course ID
# INFOSYS_COURSE_ID=lex_auth_0125409616243425281061_shared

# Target type: course or playlist (Optional, default: course)
TARGET_TYPE=course

# Playlist identifier (Optional, used when TARGET_TYPE=playlist)
# You can provide either raw UUID or full playlist URL.
INFOSYS_PLAYLIST_ID=
# INFOSYS_PLAYLIST_URL=https://infyspringboard.onwingspan.com/web/en/app/playlist/me/08281524-7cdd-430c-b327-466f2d76ad74

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
