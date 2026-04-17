#!/usr/bin/env python3
"""
Infosys Springboard Course Auto-Completer (Enhanced)
Comprehensive course completion system supporting all content types.
"""

import sys
import logging
from pathlib import Path

# Import our modules
from config import ConfigManager, Config
from api_client import APIClient, APIError, AuthenticationError
from content_analyzer import ContentAnalyzer
from content_completer import CompletionStrategy
from progress_tracker import ProgressTracker
from utils import (
    print_banner, print_section, print_success, print_error, print_warning,
    print_info, print_progress_bar, print_table, confirm_action, format_duration,
    get_icon_for_content_type, setup_logging, Colors
)


class CourseCompleter:
    """Main orchestrator for course completion."""

    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize the course completer.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.api_client = None
        self.analyzer = None
        self.strategy = None
        self.tracker = None

    def run(self):
        """Execute the course completion workflow."""
        try:
            print_banner()

            # Step 1: Validate Authentication
            print_section("Step 1: Authentication")
            if not self._validate_authentication():
                return

            # Step 2: Fetch Course
            print_section("Step 2: Fetching Course Content")
            course_hierarchy = self._fetch_course_hierarchy()
            if not course_hierarchy:
                return

            # Step 3: Analyze Content
            print_section("Step 3: Analyzing Content")
            inventory = self._analyze_content(course_hierarchy)
            if not inventory:
                return

            # Step 4: Display Summary
            print_section("Step 4: Content Summary")
            if not self._display_summary(inventory):
                return

            # Step 5: Get Confirmation
            if not self.config.auto_confirm:
                if not confirm_action("Proceed with completion?", default=False):
                    print_warning("Operation cancelled")
                    return

            # Step 6: Execute Completion
            print_section("Step 5: Auto-Completing Content")
            self._complete_content(inventory)

            # Step 7: Final Report
            print_section("Completion Report")
            self._display_final_report()

        except KeyboardInterrupt:
            print_warning("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            self.logger.exception("Unexpected error during execution")
            sys.exit(1)
        finally:
            self._cleanup()

    def _validate_authentication(self) -> bool:
        """
        Validate authentication and get user info.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.api_client = APIClient(self.config.token, self.logger)
            user_id, user_name = self.api_client.validate_user()

            self.config.user_id = user_id
            self.config.user_name = user_name

            print_success(f"Authenticated as: {user_name}")
            return True

        except AuthenticationError as e:
            print_error(f"Authentication failed: {e}")
            return False
        except APIError as e:
            print_error(f"API error: {e}")
            return False

    def _fetch_course_hierarchy(self) -> dict:
        """
        Fetch the course hierarchy.

        Returns:
            Course hierarchy data or None if failed
        """
        try:
            print_info(f"Fetching course: {self.config.course_id}")
            course_data = self.api_client.get_course_hierarchy(
                self.config.course_id,
                self.config.user_id
            )
            print_success("Course fetched successfully")
            return course_data

        except APIError as e:
            print_error(f"Failed to fetch course: {e}")
            return None

    def _analyze_content(self, course_hierarchy: dict) -> any:
        """
        Analyze course content.

        Args:
            course_hierarchy: Course hierarchy data

        Returns:
            Content inventory or None if failed
        """
        try:
            self.analyzer = ContentAnalyzer(self.logger)
            inventory = self.analyzer.analyze(course_hierarchy)

            completable_count = self.analyzer.get_completable_count()
            print_success(f"Analysis complete. Found {completable_count} items to complete")

            return inventory

        except Exception as e:
            print_error(f"Failed to analyze content: {e}")
            self.logger.exception("Content analysis error")
            return None

    def _display_summary(self, inventory) -> bool:
        """
        Display content summary.

        Args:
            inventory: Content inventory

        Returns:
            True to continue, False to abort
        """
        try:
            summary = self.analyzer.get_summary()

            print_info(f"Total items found: {summary['total_items']}")
            print_info(f"Completable items: {summary['completable_items']}")

            if summary['items_by_type']:
                print_info("\nBreakdown by type:")
                for content_type, count in sorted(summary['items_by_type'].items()):
                    icon = get_icon_for_content_type(content_type)
                    print(f"  {icon} {content_type}: {count}")

            if summary['total_duration_seconds'] > 0:
                formatted_duration = format_duration(summary['total_duration_seconds'])
                print_info(f"\nTotal content duration: {formatted_duration}")

            if summary['completable_items'] == 0:
                print_warning("No completable items found")
                return False

            return True

        except Exception as e:
            print_error(f"Error displaying summary: {e}")
            return False

    def _complete_content(self, inventory):
        """
        Complete all content items.

        Args:
            inventory: Content inventory
        """
        try:
            completable_items = inventory.get_completable_items()
            self.tracker = ProgressTracker(len(completable_items))
            self.strategy = CompletionStrategy(self.api_client, self.logger)

            print(f"\nProcessing {len(completable_items)} items...\n")

            for idx, item in enumerate(completable_items, 1):
                # Display progress
                progress = (idx / len(completable_items)) * 100
                print_progress_bar(
                    idx,
                    len(completable_items),
                    prefix=f"Progress ({idx}/{len(completable_items)})",
                    suffix=f"- {item.name[:40]}"
                )

                # Skip if dry run
                if self.config.dry_run:
                    self.tracker.mark_completed(item.content_type.value)
                    continue

                # Complete the item
                success, message = self.strategy.complete_item(item, self.config.user_id)

                if success:
                    self.tracker.mark_completed(item.content_type.value)
                else:
                    self.tracker.mark_failed(item.content_type.value, item.name, message)

            print()  # New line after progress bar
            self.tracker.finalize()

        except Exception as e:
            print_error(f"Error during completion: {e}")
            self.logger.exception("Content completion error")

    def _display_final_report(self):
        """Display the final completion report."""
        if not self.tracker:
            return

        report = self.tracker.generate_report()
        summary = report['summary']

        print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
        print(f"  Total processed: {summary['completed']} completed, {summary['failed']} failed, {summary['skipped']} skipped")
        print(f"  Success rate: {summary['success_rate']}")
        print(f"  Duration: {summary['duration']}")

        if self.config.dry_run:
            print_warning("\nDry run mode - no actual changes were made")

        if summary['completed'] == summary['total_items'] - summary['skipped']:
            print_success("\n✨ All items completed successfully! ✨")
        elif summary['failed'] > 0:
            print_warning(f"\n⚠ {summary['failed']} items failed to complete")

        if report['failures']:
            print_warning(f"\nFailed items ({len(report['failures'])}):")
            for failure in report['failures'][:10]:  # Show first 10
                print(f"  - {failure['name']}: {failure['error']}")

            if len(report['failures']) > 10:
                print(f"  ... and {len(report['failures']) - 10} more")

    def _cleanup(self):
        """Clean up resources."""
        if self.api_client:
            self.api_client.close()
            self.logger.info("API session closed")


def main():
    """Main entry point."""
    # Setup logging
    logger = setup_logging(verbose=True)

    # Load configuration
    config_manager = ConfigManager(env_file=".env")
    config = config_manager.get_config()

    # Create and run completer
    completer = CourseCompleter(config, logger)
    completer.run()


if __name__ == "__main__":
    main()
