# Slack SDK Migration

This project has been migrated from using Arcade tools to the official Slack SDK for all Slack-related operations.

## Changes Made

### 1. Updated `tools/slack_tool.py`
- Replaced Arcade client with Slack SDK WebClient
- Removed Arcade authorization flow
- Updated all functions to use Slack SDK methods:
  - `slack_post_message()` - Uses `client.chat_postMessage()`
  - `slack_fetch_messages()` - Uses `client.conversations_history()`
  - `slack_get_user_profile()` - Uses `client.users_info()`
  - `slack_get_channel_info()` - Uses `client.conversations_info()`
  - Added `slack_get_channel_members()` - Uses `client.conversations_members()`

### 2. Updated API Endpoints
- Changed endpoint paths from `/api/arcade/slack/*` to `/api/slack/*`
- Updated endpoint comments to reflect Slack SDK usage

### 3. Updated `slack_agent.py`
- Removed Arcade TDK dependencies
- Converted to simple wrapper functions around Slack SDK
- Removed complex authorization decorators

### 4. Environment Variables
- **Required**: `SLACK_BOT_TOKEN` (xoxb-...)
- **Optional**: `SLACK_CHANNEL_ID` (for default channel)
- **Removed**: `ARCADE_API_KEY` and `ARCADE_USER_ID` (no longer needed)

## Setup Instructions

### 1. Get Slack Bot Token
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create a new app or select existing app
3. Go to "OAuth & Permissions"
4. Add the following bot token scopes:
   - `chat:write` - Post messages
   - `channels:history` - Read public channels
   - `groups:history` - Read private channels
   - `im:history` - Read DMs
   - `mpim:history` - Read group DMs
   - `users:read` - Read user info
   - `users.profile:read` - Read user profiles
5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 2. Update Environment Variables
```bash
# Copy env.example to .env
cp env.example .env

# Edit .env and set your Slack bot token
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=C1234567890
```

### 3. Test the Implementation
```bash
# Run the test script
python test_slack_sdk.py
```

## API Endpoints

The following endpoints are now available:

- `GET /api/slack/messages?channel_id=C123&limit=50` - Fetch messages
- `GET /api/slack/user-profile?user_id=U123` - Get user profile
- `POST /api/slack/send-message` - Send message
- `GET /api/slack/channel-users?channel_id=C123` - Get channel users

## Benefits of Slack SDK

1. **Direct Integration**: No third-party service required
2. **Better Performance**: Direct API calls to Slack
3. **More Control**: Full access to Slack API features
4. **Simpler Setup**: Only need bot token, no Arcade account
5. **Better Error Handling**: Native Slack API error responses
6. **Future-Proof**: Official SDK maintained by Slack

## Troubleshooting

### Common Issues

1. **"SLACK_BOT_TOKEN environment variable is required"**
   - Make sure you've set the `SLACK_BOT_TOKEN` in your `.env` file
   - Ensure the token starts with `xoxb-`

2. **"Slack API error: missing_scope"**
   - Add the required scopes to your Slack app
   - Reinstall the app to your workspace

3. **"Slack API error: channel_not_found"**
   - Make sure the bot is added to the channel
   - Verify the channel ID is correct

4. **"Slack API error: not_in_channel"**
   - The bot needs to be invited to the channel
   - Use `/invite @your-bot-name` in the channel

### Testing

Run the test script to verify everything works:
```bash
python test_slack_sdk.py
```

This will test all the main functions and report any issues. 