#!/usr/bin/env python3
"""
Infosys Springboard Course Auto-Completer (Enhanced)
Comprehensive course completion system supporting all content types.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

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

            # Step 2: Resolve target courses (single course or playlist)
            print_section("Step 2: Resolving Target Courses")
            course_targets = self._resolve_course_targets()
            if not course_targets:
                return

            # Step 3: Fetch + analyze all target courses
            print_section("Step 3: Fetching and Analyzing Content")
            completable_items, aggregate = self._fetch_and_analyze_targets(course_targets)
            if not completable_items:
                return

            # Step 4: Display Summary
            print_section("Step 4: Content Summary")
            if not self._display_aggregate_summary(aggregate):
                return

            # Step 5: Get Confirmation
            if not self.config.auto_confirm:
                if not confirm_action("Proceed with completion?", default=False):
                    print_warning("Operation cancelled")
                    return

            # Step 6: Execute Completion
            print_section("Step 5: Auto-Completing Content")
            self._complete_content(completable_items)

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

    def _resolve_course_targets(self) -> List[Dict[str, str]]:
        """Resolve completion targets into a list of course IDs and names."""
        if self.config.target_type == "playlist":
            return self._resolve_playlist_targets()

        if not self.config.course_id:
            print_error("Course ID is required in single-course mode")
            return []

        return [{
            "id": self.config.course_id,
            "name": self.config.course_id,
        }]

    def _resolve_playlist_targets(self) -> List[Dict[str, str]]:
        """Resolve playlist into a list of course targets."""
        playlist_id = self.config.playlist_id
        playlist_title = self.config.playlist_title

        if not playlist_id:
            print_info("Fetching your playlists...")
            playlists = self.api_client.fetch_playlists(self.config.user_id, page=0, size=50)

            if not playlists:
                print_error("No playlists found for your account")
                return []

            rows = []
            for index, playlist in enumerate(playlists, 1):
                pid = playlist.get("playlist_id") or playlist.get("playlistId") or ""
                title = playlist.get("playlist_title") or playlist.get("playlistTitle") or pid
                visibility = playlist.get("visibility") or ""
                resource_ids = playlist.get("resource_ids") or playlist.get("resourceIds") or []
                item_count = len(resource_ids) if isinstance(resource_ids, list) else 0
                rows.append([index, title, item_count, visibility, pid])

            print_info("\nAvailable playlists:")
            print_table(["#", "Title", "Items", "Visibility", "Playlist ID"], rows, max_width=36)

            selected = None
            while selected is None:
                choice = input("\nSelect playlist by number: ").strip()
                if not choice.isdigit():
                    print_warning("Please enter a valid number")
                    continue

                choice_index = int(choice)
                if choice_index < 1 or choice_index > len(playlists):
                    print_warning(f"Please choose a number between 1 and {len(playlists)}")
                    continue

                selected = playlists[choice_index - 1]

            playlist_id = selected.get("playlist_id") or selected.get("playlistId")
            playlist_title = selected.get("playlist_title") or selected.get("playlistTitle") or playlist_id

        self.config.playlist_id = playlist_id
        self.config.playlist_title = playlist_title or playlist_id

        print_info(f"Using playlist: {self.config.playlist_title} ({self.config.playlist_id})")

        try:
            playlist_detail = self.api_client.get_playlist_detail(self.config.playlist_id, self.config.user_id)
        except APIError as e:
            print_error(f"Failed to fetch playlist details: {e}")
            return []

        targets = self.api_client.extract_course_targets_from_playlist(playlist_detail)
        if not targets:
            print_error("No course targets found in selected playlist")
            return []

        print_success(f"Playlist resolved to {len(targets)} course targets")

        preview_rows = []
        for idx, target in enumerate(targets[:20], 1):
            preview_rows.append([idx, target["name"], target["id"]])

        if preview_rows:
            print_info("\nCourses in selected playlist:")
            print_table(["#", "Course", "Course ID"], preview_rows, max_width=44)

        if len(targets) > 20:
            print_info(f"... and {len(targets) - 20} more courses")

        return targets

    def _fetch_and_analyze_targets(self, course_targets: List[Dict[str, str]]):
        """Fetch and analyze all target courses, returning completable items and aggregate stats."""
        aggregate = {
            "target_courses": len(course_targets),
            "total_items": 0,
            "completable_items": 0,
            "items_by_type": {},
            "total_duration_seconds": 0.0,
            "course_summaries": [],
            "failed_courses": [],
        }

        all_completable_items = []

        for idx, target in enumerate(course_targets, 1):
            course_id = target["id"]
            course_name = target.get("name") or course_id

            print_info(f"[{idx}/{len(course_targets)}] Fetching course: {course_name}")

            try:
                course_data = self.api_client.get_course_hierarchy(course_id, self.config.user_id)
            except APIError as e:
                print_warning(f"Skipping {course_name} due to fetch error: {e}")
                aggregate["failed_courses"].append(course_name)
                continue

            analyzer = ContentAnalyzer(self.logger)
            inventory = analyzer.analyze(course_data)
            summary = analyzer.get_summary()
            completable_items = inventory.get_completable_items()

            # Prefix item names in playlist mode to make failures easy to trace.
            if self.config.target_type == "playlist":
                for item in completable_items:
                    item.name = f"[{course_name}] {item.name}"

            all_completable_items.extend(completable_items)

            aggregate["total_items"] += summary["total_items"]
            aggregate["completable_items"] += summary["completable_items"]
            aggregate["total_duration_seconds"] += summary["total_duration_seconds"]

            for content_type, count in summary["items_by_type"].items():
                aggregate["items_by_type"][content_type] = aggregate["items_by_type"].get(content_type, 0) + count

            aggregate["course_summaries"].append([
                course_name,
                summary["completable_items"],
                summary["total_items"],
            ])

        return all_completable_items, aggregate

    def _display_aggregate_summary(self, aggregate: Dict[str, Any]) -> bool:
        """Display aggregate summary for either single course or playlist mode."""
        try:
            print_info(f"Target courses: {aggregate['target_courses']}")
            print_info(f"Courses analyzed: {len(aggregate['course_summaries'])}")
            print_info(f"Total items found: {aggregate['total_items']}")
            print_info(f"Completable items: {aggregate['completable_items']}")

            if aggregate['course_summaries'] and len(aggregate['course_summaries']) > 1:
                print_info("\nPer-course breakdown:")
                print_table(["Course", "Completable", "Total"], aggregate['course_summaries'], max_width=40)

            if aggregate['items_by_type']:
                print_info("\nBreakdown by type:")
                for content_type, count in sorted(aggregate['items_by_type'].items()):
                    icon = get_icon_for_content_type(content_type)
                    print(f"  {icon} {content_type}: {count}")

            if aggregate['total_duration_seconds'] > 0:
                formatted_duration = format_duration(aggregate['total_duration_seconds'])
                print_info(f"\nTotal content duration: {formatted_duration}")

            if aggregate['failed_courses']:
                print_warning(f"\nSkipped courses due to errors: {len(aggregate['failed_courses'])}")
                for failed in aggregate['failed_courses'][:5]:
                    print(f"  - {failed}")
                if len(aggregate['failed_courses']) > 5:
                    print(f"  ... and {len(aggregate['failed_courses']) - 5} more")

            if aggregate['completable_items'] == 0:
                print_warning("No completable items found")
                return False

            return True

        except Exception as e:
            print_error(f"Error displaying summary: {e}")
            return False

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

    def _complete_content(self, completable_items):
        """
        Complete all content items.

        Args:
            completable_items: List of content items to complete
        """
        try:
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
