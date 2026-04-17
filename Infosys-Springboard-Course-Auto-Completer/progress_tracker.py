"""
Progress Tracker for Course Completion
Tracks and reports progress during course completion.
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
import time


@dataclass
class ProgressStats:
    """Statistics for completion progress."""
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    items_by_type: Dict[str, int] = field(default_factory=dict)
    failures: List[Dict] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        processed = self.completed_items + self.failed_items
        if processed == 0:
            return 0.0
        return (self.completed_items / processed) * 100.0

    @property
    def duration_seconds(self) -> float:
        """Get total duration in seconds."""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration."""
        duration = self.duration_seconds
        minutes, seconds = divmod(int(duration), 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


class ProgressTracker:
    """Tracks completion progress and generates reports."""

    def __init__(self, total_items: int):
        """
        Initialize the progress tracker.

        Args:
            total_items: Total number of items to process
        """
        self.stats = ProgressStats(total_items=total_items)
        self.stats.start_time = time.time()

    def mark_completed(self, item_type: str):
        """Mark an item as completed."""
        self.stats.completed_items += 1
        self._update_type_count(item_type)

    def mark_failed(self, item_type: str, item_name: str, error: str):
        """Mark an item as failed."""
        self.stats.failed_items += 1
        self._update_type_count(item_type)
        self.stats.failures.append({
            'type': item_type,
            'name': item_name,
            'error': error
        })

    def mark_skipped(self, item_type: str):
        """Mark an item as skipped."""
        self.stats.skipped_items += 1

    def _update_type_count(self, item_type: str):
        """Update count for a specific item type."""
        if item_type not in self.stats.items_by_type:
            self.stats.items_by_type[item_type] = 0
        self.stats.items_by_type[item_type] += 1

    def finalize(self):
        """Finalize tracking (set end time)."""
        self.stats.end_time = time.time()

    def get_progress_percentage(self) -> float:
        """Get progress as percentage."""
        processed = self.stats.completed_items + self.stats.failed_items + self.stats.skipped_items
        if self.stats.total_items == 0:
            return 0.0
        return (processed / self.stats.total_items) * 100.0

    def get_remaining_items(self) -> int:
        """Get number of remaining items to process."""
        processed = self.stats.completed_items + self.stats.failed_items + self.stats.skipped_items
        return self.stats.total_items - processed

    def generate_report(self) -> Dict:
        """
        Generate a comprehensive report.

        Returns:
            Dictionary with report data
        """
        return {
            'summary': {
                'total_items': self.stats.total_items,
                'completed': self.stats.completed_items,
                'failed': self.stats.failed_items,
                'skipped': self.stats.skipped_items,
                'success_rate': f"{self.stats.success_rate:.1f}%",
                'duration': self.stats.duration_formatted,
            },
            'by_type': self.stats.items_by_type,
            'failures': self.stats.failures
        }
