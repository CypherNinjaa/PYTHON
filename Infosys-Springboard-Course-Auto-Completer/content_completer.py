"""
Content Completion Strategies
Implements different strategies for completing various content types.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
import logging

from api_client import APIClient
from content_analyzer import ContentType, ContentItem


class ContentCompleter(ABC):
    """Abstract base class for content completion strategies."""

    def __init__(self, api_client: APIClient, logger: Optional[logging.Logger] = None):
        """
        Initialize the completer.

        Args:
            api_client: API client instance
            logger: Optional logger
        """
        self.api_client = api_client
        self.logger = logger or logging.getLogger(__name__)

    @abstractmethod
    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """
        Complete the content item.

        Args:
            item: Content item to complete
            user_id: User ID

        Returns:
            Tuple of (success: bool, message: str)
        """
        pass

    @property
    @abstractmethod
    def supported_types(self) -> list:
        """Return list of supported content types."""
        pass


class VideoCompleter(ContentCompleter):
    """Completer for video content."""

    @property
    def supported_types(self) -> list:
        return [ContentType.VIDEO]

    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """Mark video as 100% watched."""
        try:
            success = self.api_client.mark_content_complete(
                content_id=item.identifier,
                user_id=user_id,
                duration=item.duration,
                completion_percentage=100.0
            )

            if success:
                return True, f"Marked video '{item.name}' as watched"
            else:
                return False, f"Failed to mark video '{item.name}' as watched"

        except Exception as e:
            self.logger.error(f"Error completing video {item.identifier}: {e}")
            return False, f"Error: {str(e)[:50]}"


class AudioCompleter(ContentCompleter):
    """Completer for audio content."""

    @property
    def supported_types(self) -> list:
        return [ContentType.AUDIO]

    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """Mark audio as 100% listened."""
        try:
            success = self.api_client.mark_content_complete(
                content_id=item.identifier,
                user_id=user_id,
                duration=item.duration,
                completion_percentage=100.0
            )

            if success:
                return True, f"Marked audio '{item.name}' as listened"
            else:
                return False, f"Failed to mark audio '{item.name}' as listened"

        except Exception as e:
            self.logger.error(f"Error completing audio {item.identifier}: {e}")
            return False, f"Error: {str(e)[:50]}"


class DocumentCompleter(ContentCompleter):
    """Completer for documents (PDFs, Word docs, etc.)."""

    @property
    def supported_types(self) -> list:
        return [ContentType.PDF, ContentType.DOCUMENT, ContentType.TEXT]

    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """Mark document as 100% read."""
        try:
            # Use a fixed duration for documents (assume 1 minute read time)
            duration = item.duration if item.duration > 0 else 60.0

            success = self.api_client.mark_content_complete(
                content_id=item.identifier,
                user_id=user_id,
                duration=duration,
                completion_percentage=100.0
            )

            if success:
                return True, f"Marked document '{item.name}' as read"
            else:
                return False, f"Failed to mark document '{item.name}' as read"

        except Exception as e:
            self.logger.error(f"Error completing document {item.identifier}: {e}")
            return False, f"Error: {str(e)[:50]}"


class QuizCompleter(ContentCompleter):
    """Completer for quizzes and assessments."""

    @property
    def supported_types(self) -> list:
        return [ContentType.QUIZ, ContentType.ASSESSMENT]

    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """Complete quiz/assessment by submitting it."""
        try:
            # First, try to submit the quiz with a submission endpoint
            # This handles quizzes that require special submission flow
            submit_success = self.api_client.submit_quiz(
                content_id=item.identifier,
                user_id=user_id,
                answers={}  # Submit with empty answers first
            )

            if submit_success:
                self.logger.info(f"Successfully submitted quiz {item.identifier}")
                return True, f"Marked quiz '{item.name}' as completed"

            # If quiz submission fails, try the standard progress endpoint
            # This handles assessments that use the regular completion endpoint
            standard_success = self.api_client.mark_content_complete(
                content_id=item.identifier,
                user_id=user_id,
                duration=item.duration if item.duration > 0 else 1.0,
                completion_percentage=100.0
            )

            if standard_success:
                return True, f"Marked quiz '{item.name}' as completed"

            # Both methods failed
            self.logger.warning(f"Could not mark quiz {item.identifier} with any endpoint")
            return False, f"Quiz '{item.name}' requires special handling"

        except Exception as e:
            self.logger.error(f"Error completing quiz {item.identifier}: {e}")
            return False, f"Error: {str(e)[:50]}"


class DiscussionCompleter(ContentCompleter):
    """Completer for discussions and forums."""

    @property
    def supported_types(self) -> list:
        return [ContentType.DISCUSSION]

    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """Mark discussion as 100% participated."""
        try:
            success = self.api_client.mark_content_complete(
                content_id=item.identifier,
                user_id=user_id,
                duration=item.duration if item.duration > 0 else 1.0,
                completion_percentage=100.0
            )

            if success:
                return True, f"Marked discussion '{item.name}' as participated"
            else:
                return False, f"Failed to mark discussion '{item.name}' as participated"

        except Exception as e:
            self.logger.error(f"Error completing discussion {item.identifier}: {e}")
            return False, f"Error: {str(e)[:50]}"


class ImageCompleter(ContentCompleter):
    """Completer for image content."""

    @property
    def supported_types(self) -> list:
        return [ContentType.IMAGE]

    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """Mark image as 100% viewed."""
        try:
            success = self.api_client.mark_content_complete(
                content_id=item.identifier,
                user_id=user_id,
                duration=item.duration if item.duration > 0 else 1.0,
                completion_percentage=100.0
            )

            if success:
                return True, f"Marked image '{item.name}' as viewed"
            else:
                return False, f"Failed to mark image '{item.name}' as viewed"

        except Exception as e:
            self.logger.error(f"Error completing image {item.identifier}: {e}")
            return False, f"Error: {str(e)[:50]}"


class GenericCompleter(ContentCompleter):
    """Generic completer for unknown content types."""

    @property
    def supported_types(self) -> list:
        return [ContentType.UNKNOWN]

    def complete(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """Attempt to mark unknown content as complete."""
        try:
            success = self.api_client.mark_content_complete(
                content_id=item.identifier,
                user_id=user_id,
                duration=item.duration if item.duration > 0 else 1.0,
                completion_percentage=100.0
            )

            if success:
                return True, f"Marked '{item.name}' as completed"
            else:
                return False, f"Failed to mark '{item.name}' as completed"

        except Exception as e:
            self.logger.error(f"Error completing unknown content {item.identifier}: {e}")
            return False, f"Error: {str(e)[:50]}"


class CompletionStrategy:
    """Orchestrates content completion using appropriate strategies."""

    # Map content types to completers
    COMPLETER_MAP = {
        ContentType.VIDEO: VideoCompleter,
        ContentType.AUDIO: AudioCompleter,
        ContentType.PDF: DocumentCompleter,
        ContentType.DOCUMENT: DocumentCompleter,
        ContentType.TEXT: DocumentCompleter,
        ContentType.IMAGE: ImageCompleter,
        ContentType.QUIZ: QuizCompleter,
        ContentType.ASSESSMENT: QuizCompleter,
        ContentType.DISCUSSION: DiscussionCompleter,
        ContentType.UNKNOWN: GenericCompleter,
        ContentType.SECTION: None,  # Sections are containers, skip
    }

    def __init__(self, api_client: APIClient, logger: Optional[logging.Logger] = None):
        """
        Initialize the completion strategy.

        Args:
            api_client: API client instance
            logger: Optional logger
        """
        self.api_client = api_client
        self.logger = logger or logging.getLogger(__name__)
        self.completers: dict = {}
        self._initialize_completers()

    def _initialize_completers(self):
        """Initialize all completer instances."""
        for content_type, completer_class in self.COMPLETER_MAP.items():
            if completer_class:
                self.completers[content_type] = completer_class(self.api_client, self.logger)

    def complete_item(self, item: ContentItem, user_id: str) -> Tuple[bool, str]:
        """
        Complete a content item using the appropriate strategy.

        Args:
            item: Content item to complete
            user_id: User ID

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Skip sections/containers
        if item.is_container:
            return True, f"Skipped section '{item.name}' (container)"

        # Skip unknown types if no completer available
        if item.content_type not in self.completers:
            self.logger.warning(f"No completer for {item.content_type.value}: {item.name}")
            return False, f"No completer available for {item.content_type.value}"

        completer = self.completers[item.content_type]
        return completer.complete(item, user_id)

    def get_supported_types(self) -> list:
        """Get list of all supported content types."""
        return list(self.completers.keys())
