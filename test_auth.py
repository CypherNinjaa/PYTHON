#!/usr/bin/env python3
"""
Quick authentication test for Infosys Springboard token
"""

import sys
import os
from pathlib import Path

# Add the Infosys module to path
sys.path.insert(0, str(Path(__file__).parent / "Infosys-Springboard-Course-Auto-Completer"))

from dotenv import load_dotenv
from api_client import APIClient, AuthenticationError, APIError
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_authentication():
    """Test if the token is valid and authentication works."""

    print("\n" + "="*60)
    print("INFOSYS SPRINGBOARD TOKEN VALIDATION TEST")
    print("="*60 + "\n")

    # Load environment variables
    if os.path.exists(".env"):
        load_dotenv(".env")
        print("[OK] Loaded .env file")
    else:
        print("[FAIL] .env file not found")
        return False

    # Get credentials
    token = os.getenv('token') or os.getenv('INFOSYS_TOKEN')
    course_id = os.getenv('courseid') or os.getenv('INFOSYS_COURSE_ID')

    if not token:
        print("[FAIL] Token not found in .env")
        return False

    if not course_id:
        print("[FAIL] Course ID not found in .env")
        return False

    print(f"[OK] Token loaded (length: {len(token)} chars)")
    print(f"[OK] Course ID: {course_id}\n")

    # Create API client and test
    try:
        print("Testing authentication...")
        api_client = APIClient(token, logger)
        user_id, user_name = api_client.validate_user()

        print(f"\n{'='*60}")
        print("[SUCCESS] AUTHENTICATION SUCCESSFUL!")
        print(f"{'='*60}")
        print(f"User: {user_name}")
        print(f"User ID: {user_id}")
        print(f"{'='*60}\n")

        api_client.close()
        return True

    except AuthenticationError as e:
        print(f"\n[FAIL] AUTHENTICATION FAILED: {e}\n")
        return False
    except APIError as e:
        print(f"\n[FAIL] API ERROR: {e}\n")
        return False
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}\n")
        return False

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
