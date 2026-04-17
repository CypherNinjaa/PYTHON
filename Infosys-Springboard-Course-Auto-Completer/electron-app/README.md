# Desktop App (Electron)

This folder contains a desktop UI for the Python completion engine.

## Features

- Uses all existing backend features already in the Python app.
- Lets user choose any .env file path.
- Runs course mode and playlist mode.
- Supports course IDs, TOC URLs, and viewer URLs.
- Streams live output logs in the desktop app.
- Includes quick completion mode (single course ID, instant run).
- Stop button to terminate a running job.

## Prerequisites

- Python with project dependencies installed in parent folder.
- Node.js 18+.

## Install and Run

1. Open terminal in this folder.
2. Run npm install.
3. Run npm start.

## How It Works

- Electron spawns the Python script in parent directory.
- It sets NON_INTERACTIVE=true so there are no terminal prompts.
- It passes INFOSYS_ENV_FILE for selected .env file path.
- Form inputs are sent as environment variable overrides per run.

## Quick Completion

1. Enter one course ID in Quick Completion section.
2. Click Quick Complete Now.
3. App runs with:
   - TARGET_TYPE=course
   - AUTO_CONFIRM=true
   - DRY_RUN=false

## Notes

- If token is missing in selected .env, add it in Token override field.
- For playlist mode, playlist ID or playlist URL is required.
- For course mode, at least one course ID/URL is required.
