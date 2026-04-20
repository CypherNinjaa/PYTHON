"""
Content Analyzer for Course Hierarchy
Parses course structure and categorizes content by type.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class ContentType(Enum):
    """Enumeration of content types."""
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    DOCUMENT = "document"
    IMAGE = "image"
    TEXT = "text"
    QUIZ = "quiz"
    ASSESSMENT = "assessment"
    DISCUSSION = "discussion"
    SECTION = "section"
    UNKNOWN = "unknown"


@dataclass
class ContentItem:
    """Represents a single piece of content."""
    identifier: str
    name: str
    mime_type: str
    content_type: ContentType
    duration: float = 0.0
    path: str = ""  # Full path in course hierarchy
    parent_id: Optional[str] = None
    is_container: bool = False

    def __repr__(self) -> str:
        return f"ContentItem(name='{self.name}', type={self.content_type.value}, duration={self.duration})"


@dataclass
class ContentInventory:
    """Inventory of all course content."""
    total_items: int = 0
    items_by_type: Dict[ContentType, List[ContentItem]] = field(default_factory=dict)
    all_items: List[ContentItem] = field(default_factory=list)
    failed_items: List[Dict[str, Any]] = field(default_factory=list)

    def add_item(self, item: ContentItem):
        """Add a content item to the inventory."""
        if item.content_type not in self.items_by_type:
            self.items_by_type[item.content_type] = []

        self.items_by_type[item.content_type].append(item)
        self.all_items.append(item)
        self.total_items += 1

    def get_completable_items(self) -> List[ContentItem]:
        """Get all items that should be auto-completed."""
        completable_types = {
            ContentType.VIDEO,
            ContentType.AUDIO,
            ContentType.PDF,
            ContentType.DOCUMENT,
            ContentType.QUIZ,
            ContentType.ASSESSMENT,
            ContentType.DISCUSSION,
            ContentType.TEXT
        }

        return [
            item for item in self.all_items
            if item.content_type in completable_types and not item.is_container
        ]

    def get_count_by_type(self) -> Dict[str, int]:
        """Get count of items by content type."""
        return {
            ct.value: len(items)
            for ct, items in self.items_by_type.items()
            if items
        }


class ContentAnalyzer:
    """Analyzes course hierarchy and categorizes content."""

    # MIME type patterns for content classification
    MIME_TYPE_PATTERNS = {
        ContentType.VIDEO: ['video/', 'application/x-mpegurl'],
        ContentType.AUDIO: ['audio/'],
        ContentType.PDF: ['application/pdf'],
        ContentType.DOCUMENT: [
            'application/msword',
            'application/vnd.openxmlformats',
            'application/zip',
            'application/web-module'
        ],
        ContentType.IMAGE: ['image/'],
        ContentType.TEXT: ['text/'],
        ContentType.QUIZ: ['application/quiz', 'quiz'],
        ContentType.ASSESSMENT: [
            'assessment',
            'exam',
            'application/integrated-hands-on',
            'application/web-module-exercise',
            'application/iap-assessment',
            'application/rdbms'
        ],
        ContentType.DISCUSSION: ['discussion', 'forum'],
        ContentType.SECTION: ['application/vnd.ekstep.content-collection'],
    }

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the content analyzer.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.inventory = ContentInventory()

    def analyze(self, course_data: Dict[str, Any]) -> ContentInventory:
        """
        Analyze course hierarchy and build inventory.

        Args:
            course_data: Course hierarchy data from API

        Returns:
            ContentInventory with all discovered content
        """
        self.logger.info("Starting course content analysis...")
        self.inventory = ContentInventory()

        self._traverse_hierarchy(course_data, path="")

        self.logger.info(f"Analysis complete. Found {self.inventory.total_items} total items")
        self._log_inventory_summary()

        return self.inventory

    def _traverse_hierarchy(
        self,
        data: Any,
        path: str = "",
        parent_id: Optional[str] = None,
        depth: int = 0
    ):
        """
        Recursively traverse the course hierarchy.

        Args:
            data: Current node in hierarchy
            path: Current path in hierarchy
            parent_id: Parent content ID
            depth: Current depth in tree
        """
        if isinstance(data, dict):
            # Process this node
            content_id = data.get('identifier')
            content_name = data.get('name', 'Unnamed')
            mime_type = data.get('mimeType', '')
            duration = data.get('duration', 0.0)

            # Create full path
            current_path = f"{path}/{content_name}" if path else content_name

            if content_id:
                # Categorize the content
                content_type = self._categorize_mime_type(mime_type, content_name)

                # Determine if this is a container (has children)
                has_children = bool(data.get('children'))

                # Create content item
                item = ContentItem(
                    identifier=content_id,
                    name=content_name,
                    mime_type=mime_type,
                    content_type=content_type,
                    duration=float(duration) if duration else 0.0,
                    path=current_path,
                    parent_id=parent_id,
                    is_container=has_children
                )

                self.inventory.add_item(item)
                self.logger.debug(f"Found {content_type.value}: {content_name}")

            # Process children
            if 'children' in data and isinstance(data['children'], list):
                for child in data['children']:
                    self._traverse_hierarchy(
                        child,
                        path=current_path,
                        parent_id=content_id,
                        depth=depth + 1
                    )

        elif isinstance(data, list):
            # Process list items
            for item in data:
                self._traverse_hierarchy(
                    item,
                    path=path,
                    parent_id=parent_id,
                    depth=depth
                )

    def _categorize_mime_type(self, mime_type: str, name: str = "") -> ContentType:
        """
        Categorize content based on MIME type and name.

        Args:
            mime_type: MIME type string
            name: Content name for additional context

        Returns:
            ContentType classification
        """
        if not mime_type and not name:
            return ContentType.UNKNOWN

        # Check MIME type patterns
        mime_lower = (mime_type or "").lower()
        name_lower = (name or "").lower()

        for content_type, patterns in self.MIME_TYPE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in mime_lower or pattern.lower() in name_lower:
                    return content_type

        # Check name for clues
        if any(word in name_lower for word in ['quiz', 'test', 'exam']):
            return ContentType.ASSESSMENT
        elif any(word in name_lower for word in ['discussion', 'forum', 'chat']):
            return ContentType.DISCUSSION

        # Check for container-like content (no MIME type)
        if not mime_type:
            if any(word in name_lower for word in ['module', 'chapter', 'section', 'unit', 'week']):
                return ContentType.SECTION
            return ContentType.UNKNOWN

        return ContentType.UNKNOWN

    def _log_inventory_summary(self):
        """Log a summary of the inventory."""
        counts = self.inventory.get_count_by_type()

        self.logger.info("Content Inventory Summary:")
        self.logger.info(f"  Total items: {self.inventory.total_items}")

        for content_type, count in sorted(counts.items()):
            self.logger.info(f"  - {content_type}: {count}")

    def get_completable_count(self) -> int:
        """Get count of items that should be auto-completed."""
        return len(self.inventory.get_completable_items())

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the analyzed content.

        Returns:
            Dictionary with summary information
        """
        completable_items = self.inventory.get_completable_items()
        counts = self.inventory.get_count_by_type()

        total_duration = sum(item.duration for item in completable_items)

        return {
            'total_items': self.inventory.total_items,
            'completable_items': len(completable_items),
            'items_by_type': counts,
            'total_duration_seconds': total_duration,
            'items_by_type_detail': self.inventory.items_by_type
        }
