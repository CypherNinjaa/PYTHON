"""
API Client for Infosys Springboard
Handles all HTTP requests with retry logic, error handling, and rate limiting.
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIError(Exception):
    """Custom exception for API errors."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    pass


class APIClient:
    """HTTP client for Infosys Springboard API with retry logic and rate limiting."""

    BASE_URL = "https://infyspringboard.onwingspan.com"
    REQUEST_DELAY = 0.5  # Delay between requests in seconds
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.5  # Exponential backoff: {backoff factor} * (2 ** ({number of total retries} - 1))

    def __init__(self, token: str, logger: Optional[logging.Logger] = None):
        """
        Initialize API client.

        Args:
            token: Bearer token for authentication
            logger: Optional logger instance
        """
        self.token = token
        self.logger = logger or logging.getLogger(__name__)
        self.session = self._create_session()
        self.last_request_time = 0

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT"],
            backoff_factor=self.BACKOFF_FACTOR
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self, include_wid: Optional[str] = None, content_type: str = "application/json") -> Dict[str, str]:
        """
        Get common headers for API requests.

        Args:
            include_wid: Optional user ID to include in headers
            content_type: Content type for the request

        Returns:
            Dictionary of headers
        """
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': f'Bearer {self.token}',
            'cache-control': 'no-cache',
            'dnt': '1',
            'hostpath': 'infyspringboard.onwingspan.com',
            'langcode': 'en',
            'locale': 'en',
            'org': 'infosysheadstart',
            'pragma': 'no-cache',
            'rootorg': 'infosysheadstart',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'content-type': content_type,
        }

        if include_wid:
            headers['wid'] = include_wid

        return headers

    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    def _handle_response_error(self, response: requests.Response, action: str):
        """
        Handle API response errors.

        Args:
            response: Response object
            action: Description of the action being performed

        Raises:
            AuthenticationError: If authentication failed
            RateLimitError: If rate limit exceeded
            APIError: For other API errors
        """
        status_code = response.status_code
        try:
            error_data = response.json()
            error_msg = error_data.get('message', str(error_data))
        except:
            error_msg = response.text[:200]

        error_detail = f"{action}: {status_code} {error_msg}"

        if status_code == 401:
            self.logger.error(f"Authentication failed: {error_detail}")
            raise AuthenticationError(f"Unauthorized: Token may have expired or be invalid. {error_msg}")
        elif status_code == 403:
            self.logger.error(f"Access denied: {error_detail}")
            raise AuthenticationError(f"Access Denied: You may not have permission to this course. {error_msg}")
        elif status_code == 429:
            self.logger.error(f"Rate limit exceeded: {error_detail}")
            raise RateLimitError(f"Rate limit exceeded. Please try again later.")
        elif status_code == 404:
            self.logger.error(f"Resource not found: {error_detail}")
            raise APIError(f"Resource not found: {error_detail}")
        elif status_code >= 500:
            self.logger.error(f"Server error: {error_detail}")
            raise APIError(f"Server error: {error_msg}")
        else:
            self.logger.error(f"API error: {error_detail}")
            raise APIError(f"{error_detail}")

    def validate_user(self) -> Tuple[str, str]:
        """
        Validate the bearer token and get user information.

        Returns:
            Tuple of (user_id, user_name)

        Raises:
            AuthenticationError: If token is invalid
            APIError: For other API errors
        """
        url = f"{self.BASE_URL}/apis/protected/v8/user/validate"
        headers = self._get_headers()

        self.logger.info("Validating authentication token...")
        self._apply_rate_limit()

        try:
            response = self.session.get(url, headers=headers, timeout=10)

            if not response.ok:
                self._handle_response_error(response, "User validation")

            data = response.json()
            user_id = data.get('wid') or data.get('userId') or data.get('id')
            user_name = data.get('name') or data.get('firstName', 'Unknown User')

            if not user_id:
                raise APIError("Could not extract user ID from response")

            self.logger.info(f"Successfully authenticated as: {user_name} (ID: {user_id})")
            return user_id, user_name

        except requests.exceptions.Timeout:
            self.logger.error("Request timeout during user validation")
            raise APIError("Request timeout. Server not responding.")
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error during user validation")
            raise APIError("Connection error. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error during user validation: {e}")
            raise APIError(f"Request failed: {str(e)}")

    def get_course_hierarchy(self, course_id: str, user_id: str) -> Dict[str, Any]:
        """
        Fetch the course hierarchy/structure.

        Args:
            course_id: ID of the course
            user_id: ID of the user

        Returns:
            Course hierarchy data

        Raises:
            APIError: If course fetch fails
        """
        url = f"{self.BASE_URL}/api-gw/wn-apis/infosysheadstart/hierarchy-service/level/{course_id}/2"
        params = {'sourceFields': 'appIconLarge'}
        headers = self._get_headers(include_wid=user_id)

        self.logger.info(f"Fetching course hierarchy for course: {course_id}")
        self._apply_rate_limit()

        try:
            response = self.session.get(url, headers=headers, params=params, timeout=15)

            if not response.ok:
                self._handle_response_error(response, "Course hierarchy fetch")

            data = response.json()
            self.logger.info("Course hierarchy fetched successfully")
            return data

        except requests.exceptions.Timeout:
            self.logger.error("Request timeout during course fetch")
            raise APIError("Request timeout. Course fetch taking too long.")
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error during course fetch")
            raise APIError("Connection error during course fetch.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error during course fetch: {e}")
            raise APIError(f"Failed to fetch course: {str(e)}")

    def mark_content_complete(
        self,
        content_id: str,
        user_id: str,
        duration: float = 1.0,
        completion_percentage: float = 100.0
    ) -> bool:
        """
        Mark a content item as complete.

        Args:
            content_id: ID of the content item
            user_id: ID of the user
            duration: Duration of the content (default: 1.0)
            completion_percentage: Completion percentage (default: 100.0 for full completion)

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.BASE_URL}/api-gw/wn-apis/infosysheadstart/progress/v1/progress/calculate"
        headers = self._get_headers(include_wid=user_id)
        headers['x-wingspan-caller'] = 'wingspan'
        headers['origin'] = self.BASE_URL

        # Calculate visited progress based on completion percentage
        max_size = float(duration) if duration and duration > 0 else 1.0
        visited_progress = (max_size * completion_percentage) / 100.0

        payload = {
            "contentId": content_id,
            "visited": [visited_progress],
            "maxSize": max_size,
            "userId": user_id
        }

        self.logger.debug(f"Marking content {content_id} as complete: {completion_percentage}%")
        self._apply_rate_limit()

        try:
            response = self.session.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if not response.ok:
                self._handle_response_error(response, f"Mark content {content_id} complete")
                return False

            self.logger.debug(f"Successfully marked {content_id} as complete")
            return True

        except APIError as e:
            self.logger.warning(f"Failed to mark {content_id} complete: {e}")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Request error marking {content_id} complete: {e}")
            return False

    def get_quizzes_for_content(self, content_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to fetch quiz/assessment data for a content item.

        Args:
            content_id: ID of the content item
            user_id: ID of the user

        Returns:
            Quiz data if available, None otherwise
        """
        # Try different potential quiz endpoints
        endpoints = [
            f"{self.BASE_URL}/api-gw/wn-apis/infosysheadstart/assessment/v1/assessments/{content_id}",
            f"{self.BASE_URL}/api-gw/wn-apis/infosysheadstart/quiz/v1/quiz/{content_id}",
        ]

        headers = self._get_headers(include_wid=user_id)

        for url in endpoints:
            try:
                self._apply_rate_limit()
                response = self.session.get(url, headers=headers, timeout=5)
                if response.ok:
                    self.logger.debug(f"Found quiz data for {content_id}")
                    return response.json()
            except:
                continue

        return None

    def submit_quiz(self, content_id: str, user_id: str, answers: Optional[Dict] = None) -> bool:
        """
        Submit quiz answers or mark quiz as attempted.

        Args:
            content_id: ID of the quiz content
            user_id: ID of the user
            answers: Optional dict of quiz answers

        Returns:
            True if submission successful, False otherwise
        """
        # Try to submit to the quiz submission endpoint
        endpoints = [
            f"{self.BASE_URL}/api-gw/wn-apis/infosysheadstart/assessment/v1/submit",
            f"{self.BASE_URL}/api-gw/wn-apis/infosysheadstart/quiz/v1/submit",
        ]

        headers = self._get_headers(include_wid=user_id)
        headers['x-wingspan-caller'] = 'wingspan'
        headers['origin'] = self.BASE_URL

        payload = {
            "contentId": content_id,
            "userId": user_id,
            "answers": answers or {}
        }

        self.logger.debug(f"Submitting quiz {content_id} with payload: {payload}")
        self._apply_rate_limit()

        for url in endpoints:
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.ok:
                    self.logger.debug(f"Successfully submitted quiz {content_id}")
                    return True
                else:
                    self.logger.debug(f"Quiz submission failed at {url}: {response.status_code}")

            except requests.exceptions.RequestException as e:
                self.logger.debug(f"Request error submitting quiz to {url}: {e}")
                continue

        return False

    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.info("API session closed")
