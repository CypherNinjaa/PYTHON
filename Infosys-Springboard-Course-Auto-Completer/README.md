# 🚀 Infosys Springboard Course Auto-Completer (Enhanced)

A powerful Python tool that automatically completes **ALL** content in your Infosys Springboard courses - videos, documents, quizzes, assessments, discussions, and more.

> ⚠️ **Disclaimer**: Use this tool responsibly and in compliance with your organization's policies. This is intended for educational and authorized use only.

## ✨ Features

- 🎬 **Auto-Complete All Content Types**: Videos, PDFs, documents, quizzes, assessments, discussions
- 🔐 **Secure Authentication**: Uses your existing Infosys Springboard token
- 📊 **Comprehensive Analysis**: Intelligently categorizes all course content
- 📈 **Real-time Progress**: Beautiful progress tracking with detailed reporting
- ⚡ **Fast & Reliable**: Retry logic, rate limiting, and error recovery
- 🛡️ **Safe**: Always prompts before taking action; includes dry-run mode
- 📝 **Detailed Logging**: Troubleshoot issues with comprehensive logs
- 🎯 **Flexible Configuration**: CLI prompts or .env file configuration

## 📋 Requirements

- Python 3.7+
- Internet connection
- Active Infosys Springboard account
- Bearer token (see below for how to get it)

## 🛠️ Installation

1. **Clone or download this repository**

   ```bash
   git clone https://github.com/KavinMK05/Infosys-Springboard-Course-Auto-Completer.git
   cd Infosys-Springboard-Course-Auto-Completer
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. _(Optional)_ **Create .env file for configuration**
   ```bash
   cp .env.example .env
   # Edit .env and fill in your token and course ID(s)
   ```

## 🚀 Usage

### Interactive Mode (Recommended)

```bash
python course_completer.py
```

Then follow the prompts to enter:

- Your Bearer Token
- Course ID(s) or URL(s) (single or multiple, comma-separated)
- Optional settings (auto-confirm, dry-run mode)

### Using .env File

1. Copy `.env.example` to `.env`
2. Edit `.env` and add your credentials:
   ```
   INFOSYS_TOKEN=your_token_here
   INFOSYS_COURSE_IDS=your_course_id_here,another_course_id_here
   # optional alternative input
   INFOSYS_TARGET_URLS=https://infyspringboard.onwingspan.com/web/en/app/toc/lex_auth_012734003600908288382_shared/overview
   ```
3. Run: `python course_completer.py`

### Desktop App (Electron)

If you prefer a GUI instead of terminal prompts, use the Electron app in [electron-app/README.md](electron-app/README.md).

1. Open terminal in `electron-app`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start desktop app:
   ```bash
   npm start
   ```

Desktop app includes:

- Full completion mode (all existing Python features)
- .env picker
- Quick completion mode (one course ID, instant run)
- Live logs and stop control

## 🔑 How to Get Your Bearer Token

1. Open **Infosys Springboard** and log in
   - URL: https://infyspringboard.onwingspan.com

2. Open **Developer Tools**:
   - Windows/Linux: Press `F12` or `Ctrl+Shift+I`
   - Mac: Press `Cmd+Option+I`

3. Go to the **Application** tab

4. In the left sidebar, expand **Local Storage**

5. Click on `https://infyspringboard.onwingspan.com`

6. Look for the key that starts with **`kc`** (e.g., `kc-infyspringboard`)

7. Click on it and find the **`token`** field inside the JSON value

8. Copy the entire token value (it's a long JWT string starting with `eyJ...`)

9. _Important_: The token expires after some time. If you get authentication errors, get a fresh token.

## 📖 How to Get the Course ID

1. Navigate to the course you want to complete on Infosys Springboard

2. Go to the **Course Overview** page

3. Look at the URL in your browser's address bar:

   ```
   https://infyspringboard.onwingspan.com/web/en/app/toc/lex_auth_0138419214303969287290_shared/overview
   ```

4. The **Course ID** is between `/toc/` and `/overview`:
   ```
   lex_auth_0138419214303969287290_shared
   ```

### URL Pattern (Parent/Child Relationship)

The tool now auto-detects the parent course ID from both URL types:

- **TOC URL**
  - Pattern: `/toc/<parent_course_id>/overview`
  - Example parent course ID: `lex_auth_012734003600908288382_shared`

- **Viewer URL**
  - Pattern: `/viewer/hands-on/<content_id>?collectionId=<parent_course_id>&collectionType=Course&pathId=<node1>,<node2>,...`
  - `<content_id>` is the practice-problem content item
  - `collectionId` is the parent course ID used for completion
  - `pathId` is the child hierarchy path inside the course (section/subsection lineage)

So even if practice problems have different content IDs, their shared `collectionId` maps them to the same parent course.

## 📊 Example Output

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     🚀 Infosys Springboard Course Auto-Completer (Enhanced) 🚀       ║
║                                                                      ║
║              Complete ALL Your Course Content Instantly              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

══════════════════════════════════════════════════════════════════════
▸ Step 1: Authentication
══════════════════════════════════════════════════════════════════════

✓ Validating token and fetching user info...
✓ Authenticated as: John Doe

══════════════════════════════════════════════════════════════════════
▸ Step 2: Fetching Course Content
══════════════════════════════════════════════════════════════════════

ℹ Fetching course: lex_auth_0138419214303969287290_shared
✓ Course fetched successfully

══════════════════════════════════════════════════════════════════════
▸ Step 3: Analyzing Content
══════════════════════════════════════════════════════════════════════

✓ Analysis complete. Found 42 items to complete

══════════════════════════════════════════════════════════════════════
▸ Step 4: Content Summary
══════════════════════════════════════════════════════════════════════

ℹ Total items found: 50
ℹ Completable items: 42

Breakdown by type:
  🎬 video: 15
  📄 pdf: 8
  ❓ assessment: 12
  📝 text: 5
  💬 discussion: 2

ℹ Total content duration: 2.5h

══════════════════════════════════════════════════════════════════════
▸ Step 5: Auto-Completing Content
══════════════════════════════════════════════════════════════════════

Processing (42/42) |██████████████████████████████████████████████████| 100.0%

══════════════════════════════════════════════════════════════════════
▸ Completion Report
══════════════════════════════════════════════════════════════════════

Summary:
  Total processed: 40 completed, 2 failed, 0 skipped
  Success rate: 95.2%
  Duration: 2m 15s

✨ Almost done! 2 items failed to complete

Failed items (2):
  - Final Assessment: Failed to mark quiz as completed
  - Discussion Forum: Could not mark discussion as participated
```

## 🎯 Content Types Supported

| Type        | Icon | Support                              |
| ----------- | ---- | ------------------------------------ |
| Videos      | 🎬   | ✅ Full support                      |
| Audio       | 🎵   | ✅ Full support                      |
| PDFs        | 📄   | ✅ Full support                      |
| Documents   | 📃   | ✅ Full support                      |
| Text        | 📝   | ✅ Full support                      |
| Images      | 🖼️   | ✅ Full support                      |
| Quizzes     | ❓   | ✅ Marked as complete (not answered) |
| Assessments | ✓    | ✅ Marked as complete (not answered) |
| Discussions | 💬   | ✅ Marked as participated            |
| Sections    | 📚   | ⊘ Skipped (containers only)          |

## ⚙️ Configuration Options

### .env File Variables

```bash
# Required: Your Infosys Springboard Bearer Token
INFOSYS_TOKEN=eyJhbGciOiJSUzI1NiIs...

# Required for course mode: one or many course IDs
INFOSYS_COURSE_IDS=lex_auth_0125409616243425281061_shared,lex_auth_0138419214303969287290_shared

# Optional: provide URL(s) instead of IDs; parent course IDs are extracted automatically
# INFOSYS_TARGET_URLS=https://infyspringboard.onwingspan.com/web/en/app/toc/lex_auth_012734003600908288382_shared/overview
# INFOSYS_TARGET_URLS=https://infyspringboard.onwingspan.com/web/en/viewer/hands-on/lex_auth_0127136112798105601178_shared?collectionId=lex_auth_012734003600908288382_shared&collectionType=Course&pathId=lex_auth_0127136535829708801223_shared,lex_auth_0127136597324103681226_shared

# Optional legacy single-course variable (still supported)
# INFOSYS_COURSE_ID=lex_auth_0125409616243425281061_shared

# Optional: Auto-confirm without prompting (default: false)
AUTO_CONFIRM=false

# Optional: Dry run mode - show what would be done (default: false)
DRY_RUN=false

# Optional: Log file location (default: course_completer.log)
LOG_FILE=course_completer.log
```

### Command Line Usage

```bash
# Interactive mode (recommended)
python course_completer.py

# Will prompt for all required information
```

## 📝 Logging

All operations are logged to `course_completer.log` for debugging and auditing purposes. Check this file if you encounter any issues.

## 🐛 Troubleshooting

| Issue                                 | Solution                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| **Token validation failed (401/403)** | Your token has expired. Get a fresh token from the browser localStorage        |
| **Course not found (404)**            | Verify the course ID is correct. Copy it directly from the URL                 |
| **Rate limiting (429)**               | The tool automatically applies rate limiting. Wait a few minutes and try again |
| **Connection timeout**                | Check your internet connection. The API server might be down                   |
| **No completable items found**        | The course might be empty or all items are already completed                   |
| **Some items failed to complete**     | Check `course_completer.log` for specific error messages                       |

## 🏗️ Project Structure

```
infosys-course-completer/
├── course_completer.py          # Main orchestrator script
├── config.py                     # Configuration management
├── api_client.py                 # API client with retry logic
├── content_analyzer.py           # Course content analysis
├── content_completer.py          # Content completion strategies
├── progress_tracker.py           # Progress tracking
├── utils.py                      # Helper functions
├── requirements.txt              # Python dependencies
├── .env.example                  # Example configuration
└── README.md                     # This file
```

## 🔧 How It Works

1. **Authentication**: Validates your Bearer token with Infosys Springboard
2. **Content Discovery**: Recursively fetches the entire course hierarchy
3. **Content Analysis**: Categorizes items by type (videos, PDFs, quizzes, etc.)
4. **User Confirmation**: Shows a summary and asks for confirmation
5. **Auto-Completion**: Marks each item as 100% complete
6. **Progress Tracking**: Real-time progress with detailed statistics
7. **Final Report**: Shows completion summary and any errors

## ⚠️ Important Notes

- **Token Expiration**: Tokens expire periodically. If you see "Unauthorized" errors, get a fresh token
- **Rate Limiting**: The tool waits 0.5 seconds between requests to avoid rate limiting
- **Non-destructive for Quizzes**: Quizzes are marked as complete but not answered
- **Dry Run Mode**: Use `DRY_RUN=true` to test without making actual changes
- **Backup**: Consider backing up your account settings before using this tool
- **Compliance**: Ensure you have authorization from your organization before using this tool

## 📄 License

MIT License - Feel free to use and modify as needed.

## 🤝 Contributing

Found a bug or want to suggest a feature? Feel free to create an issue or pull request!

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the `course_completer.log` file
3. Ensure your token is fresh and valid
4. Make sure the course ID is correct

---

**Made with ❤️ for Infosys Springboard learners**

_Disclaimer: This tool is not officially affiliated with Infosys or OnWingspan. Use responsibly and in compliance with your organization's policies._
