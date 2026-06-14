# Follow-Back Checker 🔍

A simple Python utility to check which users you follow on GitHub who haven't followed you back.

## Features

- 🔐 Secure: Uses GitHub Personal Access Token
- ⚡ Fast: Fetches and compares followers efficiently
- 📊 Clear output: Shows users you follow who don't follow you back
- 🐍 Pure Python: Minimal dependencies

## Prerequisites

- Python 3.6+
- GitHub Personal Access Token (with `user:follow` scope)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/code-tinker-art/follow-back-checker.git
cd follow-back-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token"
   - Select scopes: `user:follow` (minimum required)
   - Copy the token

4. Set your token as an environment variable:
```bash
export GITHUB_TOKEN="your_token_here"
```

Or create a `.env` file:
```
GITHUB_TOKEN=your_token_here
```

## Usage

Run the script:
```bash
python follow_back_checker.py
```

## Example Output

```
Fetching your followers list...
Fetching your following list...

==================================================
GitHub Follow-Back Checker
==================================================

Total Followers: 42
Total Following: 58
Mutual Follows: 35

Users you follow who don't follow you back (23):
--------------------------------------------------
  • user1
  • user2
  • user3
  • user4
  • ...

==================================================
```

## How It Works

1. Fetches your complete followers list from GitHub API
2. Fetches your complete following list from GitHub API
3. Compares the two lists
4. Shows users you follow who haven't followed you back

## Security

- Never commit your token to the repository
- Always use environment variables or `.env` files
- Never share your token with anyone
- Use `.gitignore` to prevent accidental commits of `.env` files

## API Rate Limiting

GitHub API has rate limits:
- **Authenticated requests**: 5,000 per hour
- **Unauthenticated**: 60 per hour

This script uses authenticated requests and should complete well within limits.

## License

MIT License - feel free to use and modify!

## Contributing

Feel free to fork and submit pull requests for improvements!

## Troubleshooting

**"GITHUB_TOKEN environment variable not set!"**
- Make sure you've exported the token: `export GITHUB_TOKEN='your_token'`
- Or create a `.env` file with your token

**"401 Unauthorized"**
- Your token may be invalid or expired
- Generate a new token at https://github.com/settings/tokens

**"403 Forbidden"**
- Your token may not have the required scopes
- Ensure the token has `user:follow` scope
