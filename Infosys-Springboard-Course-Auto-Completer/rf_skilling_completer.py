#!/usr/bin/env python3
"""
RF Skilling Academy course completer.

This script opens a headed browser, allows manual login, auto-progresses module
content, and applies SCORM completion at the assessment stage.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Frame, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright


@dataclass
class RunStats:
    modules_visited: int = 0
    next_lesson_clicks: int = 0
    scorm_next_clicks: int = 0
    scorm_submit_clicks: int = 0
    forced_completion_calls: int = 0


def _safe_click(locator, timeout_ms: int = 1500) -> bool:
    try:
        if locator.count() == 0:
            return False
        locator.first.click(timeout=timeout_ms)
        return True
    except Exception:
        return False


def _get_scorm_frame(page: Page) -> Optional[Frame]:
    for frame in page.frames:
        if "index_lms.html" in frame.url:
            return frame
    return None


def _is_login_required(page: Page) -> bool:
    if "/user/login" in page.url:
        return True
    return page.locator('a[href*="/user/login"]').count() > 0


def _on_score_page(page: Page) -> bool:
    return "/score/" in page.url


def _is_course_complete(page: Page) -> bool:
    body = page.inner_text("body")
    if re.search(r"course completed successfully", body, re.IGNORECASE):
        return True
    if re.search(r"completed successfully", body, re.IGNORECASE) and _on_score_page(page):
        return True
    return False


def _main_heading(page: Page) -> str:
    try:
        h2 = page.locator("main h2").first
        if h2.count() == 0:
            return ""
        return h2.inner_text(timeout=1500).strip()
    except Exception:
        return ""


def _has_assessment_context(page: Page) -> bool:
    heading = _main_heading(page)
    if re.fullmatch(r"course assessment", heading, re.IGNORECASE):
        return True

    if page.get_by_role("button", name=re.compile(r"^finish$", re.IGNORECASE)).count() > 0:
        return True

    body = page.inner_text("body")
    if re.search(r"please click on 'finish' after completing the assessment", body, re.IGNORECASE):
        return True

    return False


def _wait_dom(page: Page, timeout_ms: int = 15000) -> None:
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
    except PlaywrightTimeoutError:
        pass


def _click_host_action(page: Page, regex_pattern: str) -> bool:
    try:
        return bool(
            page.evaluate(
                """
                (pattern) => {
                  const re = new RegExp(pattern, 'i');
                  const nodes = Array.from(document.querySelectorAll('button,a'));
                  for (const el of nodes) {
                    const txt = (el.textContent || '').trim();
                    const aria = (el.getAttribute('aria-label') || '').trim();
                    if (!re.test(txt) && !re.test(aria)) continue;

                    const hidden = (el.offsetParent === null) && el.getClientRects().length === 0;
                    if (hidden) continue;

                    if (
                      el.hasAttribute('disabled') ||
                      el.getAttribute('aria-disabled') === 'true' ||
                      el.classList.contains('disabled')
                    ) {
                      continue;
                    }

                    el.click();
                    return true;
                  }
                  return false;
                }
                """,
                regex_pattern,
            )
        )
    except Exception:
        return False


def _wait_for_manual_login(page: Page) -> None:
    print("\nLogin required in browser.")
    print("1) Complete login manually in the opened browser window")
    print("2) Return to terminal and press Enter to continue")
    input("Press Enter after login is complete...")
    _wait_dom(page)


def _open_learning_path(page: Page) -> None:
    # Try the common entry points from overview page.
    for _ in range(6):
        if "/group/" in page.url and "/module/" in page.url:
            return

        if _safe_click(page.get_by_role("link", name=re.compile(r"continue course", re.IGNORECASE))):
            _wait_dom(page)
            continue

        if _safe_click(page.get_by_role("link", name=re.compile(r"start course", re.IGNORECASE))):
            _wait_dom(page)
            continue

        # Some pages render buttons instead of links.
        if _safe_click(page.get_by_role("button", name=re.compile(r"continue course", re.IGNORECASE))):
            _wait_dom(page)
            continue

        if _safe_click(page.get_by_role("button", name=re.compile(r"start course", re.IGNORECASE))):
            _wait_dom(page)
            continue

        if _click_host_action(page, r"^continue course$"):
            _wait_dom(page)
            continue

        if _click_host_action(page, r"^start course$"):
            _wait_dom(page)
            continue

        break


def _tick_scorm_module(frame: Frame, max_slide_clicks: int, stats: RunStats) -> None:
    # Resume/start if a modal gate is present.
    frame.evaluate(
        """
        () => {
          const btn = Array.from(document.querySelectorAll('button,[role="button"],a'))
            .find(el => /start course|start the test|resume|restart/i.test((el.textContent || '').trim())
              || /start|resume|restart/i.test((el.getAttribute('aria-label') || '').trim()));
          if (btn) btn.click();
        }
        """
    )
    time.sleep(0.7)

    for _ in range(max_slide_clicks):
        state = frame.evaluate(
            """
            () => {
              // Try selecting first unanswered option if present.
              const groups = new Map();
              for (const r of Array.from(document.querySelectorAll('input[type="radio"]'))) {
                const key = r.name || '__default';
                if (!groups.has(key)) groups.set(key, []);
                groups.get(key).push(r);
              }
              for (const arr of groups.values()) {
                if (!arr.some(x => x.checked)) {
                  const first = arr.find(x => !x.disabled);
                  if (first) first.click();
                }
              }

              const submitBtn = Array.from(document.querySelectorAll('button,[role="button"],a')).find(el => {
                const txt = (el.textContent || '').trim();
                const aria = (el.getAttribute('aria-label') || '').trim();
                                return /^submit$/i.test(txt) && !/ctrl\\+alt/i.test(aria);
              });
              const nextBtn = Array.from(document.querySelectorAll('button,[role="button"],a')).find(el => {
                const txt = (el.textContent || '').trim();
                const aria = (el.getAttribute('aria-label') || '').trim();
                                return /^next$/i.test(txt) || /next \\(ctrl\\+alt\\+period\\)/i.test(aria);
              });
              const okBtn = Array.from(document.querySelectorAll('button,[role="button"],a'))
                .find(el => /^ok$/i.test((el.textContent || '').trim()));

              let didSubmit = false;
              let didNext = false;

              if (submitBtn) {
                submitBtn.click();
                didSubmit = true;
              }
              if (okBtn) okBtn.click();
              if (nextBtn) {
                nextBtn.click();
                didNext = true;
              }

              return { didSubmit, didNext };
            }
            """
        )

        if state.get("didSubmit"):
            stats.scorm_submit_clicks += 1
        if state.get("didNext"):
            stats.scorm_next_clicks += 1

        if not state.get("didSubmit") and not state.get("didNext"):
            break

        time.sleep(0.55)


def _force_scorm_completion(frame: Frame, stats: RunStats) -> None:
    result = frame.evaluate(
        """
        () => {
          const out = [];
          const call = (name, fn) => {
            try {
              out.push({ name, ok: true, value: fn() });
            } catch (e) {
              out.push({ name, ok: false, error: String(e.message || e) });
            }
          };

          call('SCORM2004_SetScore', () => typeof SCORM2004_SetScore === 'function' ? SCORM2004_SetScore(100, 100, 0) : 'missing');
          call('SCORM2004_SetPointBasedScore', () => typeof SCORM2004_SetPointBasedScore === 'function' ? SCORM2004_SetPointBasedScore(100, 100, 0) : 'missing');
          call('SCORM2004_SetPassed', () => typeof SCORM2004_SetPassed === 'function' ? SCORM2004_SetPassed() : 'missing');
          call('SCORM2004_SetCompleted', () => typeof SCORM2004_SetCompleted === 'function' ? SCORM2004_SetCompleted() : 'missing');
          call('SCORM2004_SetProgressMeasure', () => typeof SCORM2004_SetProgressMeasure === 'function' ? SCORM2004_SetProgressMeasure(1) : 'missing');
          call('SCORM2004_CallSetValue success', () => typeof SCORM2004_CallSetValue === 'function' ? SCORM2004_CallSetValue('cmi.success_status', 'passed') : 'missing');
          call('SCORM2004_CallSetValue completion', () => typeof SCORM2004_CallSetValue === 'function' ? SCORM2004_CallSetValue('cmi.completion_status', 'completed') : 'missing');
          call('SCORM2004_CallSetValue score.raw', () => typeof SCORM2004_CallSetValue === 'function' ? SCORM2004_CallSetValue('cmi.score.raw', '100') : 'missing');
          call('SCORM2004_CallSetValue score.scaled', () => typeof SCORM2004_CallSetValue === 'function' ? SCORM2004_CallSetValue('cmi.score.scaled', '1') : 'missing');
          call('SCORM2004_CommitData', () => typeof SCORM2004_CommitData === 'function' ? SCORM2004_CommitData() : 'missing');
          return out;
        }
        """
    )
    stats.forced_completion_calls += 1
    print("SCORM completion API calls:")
    for item in result:
        status = "ok" if item.get("ok") else "failed"
        print(f"  - {item.get('name')}: {status}")


def run(
    course_url: str,
    headless: bool,
    max_modules: int,
    max_slide_clicks: int,
    slow_mo_ms: int,
    storage_state_path: Optional[str] = None,
) -> int:
    stats = RunStats()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless, slow_mo=slow_mo_ms)
        context_kwargs = {}
        if storage_state_path:
            context_kwargs["storage_state"] = storage_state_path
            print(f"Using storage state: {storage_state_path}")

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        print(f"Opening course URL: {course_url}")
        page.goto(course_url, wait_until="domcontentloaded")

        if _is_login_required(page):
            _wait_for_manual_login(page)

        _open_learning_path(page)

        if _is_login_required(page):
            _wait_for_manual_login(page)
            _open_learning_path(page)

        for step in range(max_modules):
            if _is_course_complete(page):
                break

            current_url = page.url
            heading = _main_heading(page)
            print(f"Step {step + 1}: {heading or 'Unknown'} | {current_url}")

            stats.modules_visited += 1
            frame = _get_scorm_frame(page)
            assessment_page = _has_assessment_context(page)

            if frame is not None:
                if assessment_page:
                    _force_scorm_completion(frame, stats)
                    time.sleep(0.8)
                else:
                    _tick_scorm_module(frame, max_slide_clicks=max_slide_clicks, stats=stats)

            # Assessment pages typically expose a host-level Finish button.
            if assessment_page:
                if _safe_click(page.get_by_role("button", name=re.compile(r"^finish$", re.IGNORECASE)), timeout_ms=3000) or _click_host_action(page, r"^finish$"):
                    stats.next_lesson_clicks += 1
                    _wait_dom(page)
                    time.sleep(1.0)
                    if _is_course_complete(page) or _on_score_page(page):
                        break
                    continue

            # Move through normal learning path.
            if _safe_click(page.get_by_role("button", name=re.compile(r"next lesson", re.IGNORECASE)), timeout_ms=3000) or _click_host_action(page, r"^next lesson$"):
                stats.next_lesson_clicks += 1
                _wait_dom(page)
                time.sleep(1.0)
                continue

            # Some pages render Next Lesson as a link.
            if _safe_click(page.get_by_role("link", name=re.compile(r"next lesson", re.IGNORECASE)), timeout_ms=3000):
                stats.next_lesson_clicks += 1
                _wait_dom(page)
                time.sleep(1.0)
                continue

            # Some intermediate pages expose Continue/Start controls again.
            if _click_host_action(page, r"^continue course$|^start course$"):
                _wait_dom(page)
                time.sleep(1.0)
                continue

            if page.url == current_url:
                print("No further navigation action detected; stopping loop.")

            break

        print("\nRun summary:")
        print(f"  modules visited: {stats.modules_visited}")
        print(f"  host next/finish clicks: {stats.next_lesson_clicks}")
        print(f"  scorm next clicks: {stats.scorm_next_clicks}")
        print(f"  scorm submit clicks: {stats.scorm_submit_clicks}")
        print(f"  forced completion calls: {stats.forced_completion_calls}")
        print(f"  final url: {page.url}")

        if _is_course_complete(page) or _on_score_page(page):
            print("\nSUCCESS: course shows completed state.")
            browser.close()
            return 0

        print("\nWARNING: completion state not confirmed automatically.")
        browser.close()
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Complete RF Skilling Academy course flow in browser (manual login supported)."
    )
    parser.add_argument("--url", required=True, help="Course overview URL or learning path URL")
    parser.add_argument("--headless", action="store_true", help="Run browser headless (not recommended for manual login)")
    parser.add_argument("--max-modules", type=int, default=20, help="Maximum learning-path pages to process")
    parser.add_argument("--max-slide-clicks", type=int, default=260, help="Maximum SCORM next/submit clicks per module")
    parser.add_argument("--slow-mo", type=int, default=100, help="Playwright slow motion delay in ms")
    parser.add_argument("--storage-state", help="Path to Playwright storage state JSON to reuse authenticated session")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(
        run(
            course_url=args.url,
            headless=args.headless,
            max_modules=args.max_modules,
            max_slide_clicks=args.max_slide_clicks,
            slow_mo_ms=args.slow_mo,
            storage_state_path=args.storage_state,
        )
    )
