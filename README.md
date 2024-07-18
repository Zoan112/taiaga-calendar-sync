# Google Calendar to Taiga Sync

## Overview

This Python script synchronizes events from Google Calendar to Taiga, an open-source project management platform. It fetches events for the current day from a user's primary Google Calendar and creates corresponding tasks in a specified Taiga project and user story.

## Prerequisites

- Python 3.7 or higher
- Google Cloud project with the Calendar API enabled
- Taiga account and project
- Required Python packages: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `requests`, `zoneinfo` (for Python < 3.9)

## Setup

1. Clone the repository or download the script.

2. Install required packages:
   ```
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests zoneinfo
   ```

3. Set up Google Calendar API:
   - Create a Google Cloud project and enable the Calendar API.
   - Create credentials (OAuth 2.0 Client ID) and download the client configuration.
   - Save the downloaded file as `credentials.json` in the same directory as the script.

4. Set environment variables:
   - `TIMEZONE`: Your desired timezone (e.g., 'America/New_York')
   - `TAIGA_USERNAME`: Your Taiga username
   - `TAIGA_PASSWORD`: Your Taiga password
   - `TAIGA_PROJECT_ID`: The ID of your Taiga project
   - `TAIGA_USER_STORY_ID`: The ID of the user story where tasks will be created

## Timezone Helper

To help you find the correct timezone value for your environment, you can use the "getZoneInfo.py" helper script:

This script will print out all available timezone values. You can use any of these values for the `TIMEZONE` environment variable.

## Usage

Run the script:

```
python sync-calendar-taiga.py
```

On first run, you'll be prompted to authorize the application to access your Google Calendar. Follow the provided URL to grant permission.

## Notes

- The script uses OAuth 2.0 for Google Calendar authentication. The token is stored in `token.json` for subsequent runs.
- Ensure your Taiga credentials and project details are correctly set in the environment variables.
- The script synchronizes events for the current day only, based on the specified timezone.
