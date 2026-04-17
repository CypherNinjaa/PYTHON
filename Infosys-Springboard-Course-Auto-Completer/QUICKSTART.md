# 🎉 Infosys Springboard Course Auto-Completer - Ready to Use!

## What's Been Built

Your comprehensive course completion system is now ready! Here's what you have:

### Core Components

1. **config.py** - Configuration management
   - Loads from .env file automatically
   - Interactive CLI prompts for token, course ID(s), and options
   - Supports environment variables and user input

2. **api_client.py** - Robust API client with:
   - Retry logic with exponential backoff
   - Rate limiting (0.5 seconds between requests)
   - Comprehensive error handling
   - Support for multiple endpoints
   - Token validation

3. **content_analyzer.py** - Intelligent content analysis
   - Recursively parses course hierarchy
   - Categorizes content by type (videos, PDFs, quizzes, discussions, etc.)
   - Generates detailed inventory
   - Tracks all content types

4. **content_completer.py** - Flexible completion strategies
   - Separate completer classes for each content type
   - VideoCompleter, AudioCompleter, DocumentCompleter, QuizCompleter, DiscussionCompleter
   - GenericCompleter for unknown types
   - Graceful error handling

5. **progress_tracker.py** - Progress tracking and reporting
   - Real-time statistics
   - Success rate calculation
   - Detailed failure reports
   - Duration tracking

6. **utils.py** - Helper functions
   - Colorful terminal output
   - Progress bars
   - Formatted tables and reports
   - Logging setup

7. **course_completer.py** - Main orchestrator
   - Coordinates all components
   - Step-by-step workflow
   - User confirmations
   - Final reporting

## 🚀 Quick Start

### Option 1: Interactive Mode (Recommended)

```bash
python course_completer.py
```

Then provide:

- Your Bearer Token (from browser localStorage)
- Course ID(s) or URL(s) (single or comma-separated)
- Optional settings

### Option 2: Using .env File

1. Create `.env` file:

   ```
   INFOSYS_TOKEN=your_token_here
   INFOSYS_COURSE_IDS=lex_auth_xxxxx_shared,lex_auth_yyyyy_shared
   # optional alternative input
   INFOSYS_TARGET_URLS=https://infyspringboard.onwingspan.com/web/en/app/toc/lex_auth_012734003600908288382_shared/overview
   AUTO_CONFIRM=false
   DRY_RUN=false
   ```

2. Run:
   ```bash
   python course_completer.py
   ```

## 📋 Getting Your Credentials

### Bearer Token

1. Open Infosys Springboard and log in
2. Press F12 to open Developer Tools
3. Go to Application → Local Storage → https://infyspringboard.onwingspan.com
4. Look for key starting with `kc` (e.g., `kc-infyspringboard`)
5. Copy the `token` field value (long JWT string)

### Course ID

From the course URL:

```
https://infyspringboard.onwingspan.com/web/en/app/toc/[COURSE_ID]/overview
```

Copy the `[COURSE_ID]` part.

For viewer URLs, use this relationship:

- `/viewer/hands-on/<content_id>` = practice-problem content item
- `collectionId=<parent_course_id>` = parent course ID used by this tool
- `pathId=<node1>,<node2>,...` = child hierarchy path in the course

## ✨ Features

- ✅ **All Content Types**: Videos, PDFs, documents, quizzes, assessments, discussions
- ✅ **Smart Analysis**: Categorizes and inventories all content
- ✅ **Safe**: Always prompts before taking action
- ✅ **Reliable**: Retry logic, rate limiting, error recovery
- ✅ **Fast**: Processes entire courses in seconds
- ✅ **Detailed Logging**: All operations logged to `course_completer.log`
- ✅ **Dry-Run Mode**: Test without making actual changes
- ✅ **Progress Tracking**: Real-time progress with detailed reports

## 🎯 How It Works

1. **Authentication** - Validates your token with Infosys
2. **Content Discovery** - Fetches entire course hierarchy
3. **Analysis** - Categorizes all content by type
4. **Summary** - Shows what will be completed
5. **Confirmation** - Asks for your approval
6. **Execution** - Marks all items as complete
7. **Reporting** - Shows final results and any errors

## 📊 Supported Content Types

| Type        | Support                            |
| ----------- | ---------------------------------- |
| Videos      | ✅ Full support                    |
| Audio       | ✅ Full support                    |
| PDFs        | ✅ Full support                    |
| Documents   | ✅ Full support                    |
| Text        | ✅ Full support                    |
| Images      | ✅ Full support                    |
| Quizzes     | ✅ Mark as complete (not answered) |
| Assessments | ✅ Mark as complete (not answered) |
| Discussions | ✅ Mark as participated            |
| Sections    | ⊘ Skipped (containers)             |

## ⚠️ Important Notes

1. **Token Expiration**: Tokens expire periodically. If you see authentication errors, get a fresh token
2. **Rate Limiting**: Tool automatically waits 0.5 seconds between requests
3. **Safe for Quizzes**: Quizzes are marked complete but not answered
4. **Dry Run**: Use DRY_RUN=true to test without changes
5. **Logging**: Check `course_completer.log` for troubleshooting

## 🧪 Testing

### Test with dry run first:

```
When prompted: Would you like dry run mode? (y/n, default: n): y
```

This will show you what would be done without actually making changes.

### Then run normally:

```
When prompted: Auto-confirm completion? (y/n, default: n): y
```

## 📁 Project Files

```
.
├── course_completer.py          # Main script
├── config.py                     # Configuration management
├── api_client.py                 # API client
├── content_analyzer.py           # Content analysis
├── content_completer.py          # Completion strategies
├── progress_tracker.py           # Progress tracking
├── utils.py                      # Utilities
├── requirements.txt              # Dependencies
├── .env.example                  # Example .env
└── README.md                     # Full documentation
```

## 🆘 Troubleshooting

**Token not working?**

- Get a fresh token from browser localStorage
- Make sure it's a complete JWT token (starts with `eyJ`)

**Course ID not found?**

- Check the URL format: `/toc/[COURSE_ID]/overview`
- Copy the exact ID between `/toc/` and `/overview`

**Connection errors?**

- Check internet connection
- Infosys servers might be down
- Try again in a few moments

**Logs not helpful?**

- Run with verbose mode (automatically enabled)
- Check `course_completer.log` for detailed errors
- Share logs when asking for help

## 📝 Log File

All operations are logged to `course_completer.log` including:

- Authentication attempts
- API requests and responses
- Content analysis details
- Completion results
- Any errors or warnings

## ✅ Next Steps

1. Get a fresh Bearer token from your browser
2. Run: `python course_completer.py`
3. Follow the interactive prompts
4. Review the content summary
5. Confirm the action
6. Watch the progress bar
7. Check the final report

## 📞 Need Help?

1. Read the full README.md for detailed documentation
2. Check the troubleshooting section
3. Review the log file for error details
4. Make sure your token is fresh and valid
5. Verify the course ID is correct

---

**Ready to complete your courses? Run it now:**

```bash
python course_completer.py
```

🚀 **Happy learning!**
