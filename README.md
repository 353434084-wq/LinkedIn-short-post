# LinkedIn Short Post Automation

This project generates one English LinkedIn short post every day, emails it to you for review, and records the result in `posts-log.json`.

It does not publish directly to LinkedIn. You manually review and copy the post before publishing.

## Project Structure

```text
.
├── .github/workflows/daily-linkedin-post.yml
├── main.py
├── topics.json
├── posts-log.json
├── requirements.txt
└── README.md
```

## How It Works

1. GitHub Actions runs the workflow every day.
2. The workflow installs Python dependencies.
3. `main.py` randomly selects one topic from `topics.json`.
4. The script calls the OpenAI API to generate a short LinkedIn post.
5. The post is limited to 120 words.
6. The script sends the post to your email by SMTP.
7. The script appends the result to `posts-log.json`.
8. GitHub Actions commits the updated log file back to the repository.

## Create A GitHub Repository

1. Create a new repository on GitHub.
2. Add these project files to the repository.
3. Commit and push the files to the default branch.
4. Open the repository on GitHub.
5. Go to the `Actions` tab.
6. Enable GitHub Actions if GitHub asks you to confirm.

## Configure GitHub Secrets

Open your repository on GitHub, then go to:

`Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`

Create these secrets:

| Secret | Description |
| --- | --- |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SMTP_HOST` | SMTP server host, such as `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port, usually `587` or `465` |
| `SMTP_USER` | Email account used to send the message |
| `SMTP_PASS` | SMTP password or app-specific authorization code |
| `TO_EMAIL` | Email address that should receive the generated post |

Do not write these values directly in the code.

## Modify Topics

Edit `topics.json` to change the pool of topics.

The file must be a JSON array of strings:

```json
[
  "Your first topic",
  "Your second topic",
  "Your third topic"
]
```

Keep each topic clear and specific. The script randomly picks one topic each time it runs.

## Run Manually

To manually trigger the workflow:

1. Open the repository on GitHub.
2. Go to the `Actions` tab.
3. Select `Daily LinkedIn Short Post`.
4. Click `Run workflow`.
5. Confirm the branch and click `Run workflow`.

## View Logs

There are two places to check logs:

1. GitHub Actions run logs:
   Open `Actions`, select the latest workflow run, and inspect the step output.

2. `posts-log.json`:
   This file stores each generated result with:
   - datetime
   - topic
   - generated content
   - send status

If generation or email sending fails, the script writes a clear error message to the Actions log and appends a failed entry to `posts-log.json`.

## Change The Publish Time

The workflow uses cron in UTC:

```yaml
schedule:
  - cron: "30 1 * * *"
```

Beijing time is UTC+8, so:

`Beijing 09:30 = UTC 01:30`

To change the time, convert your desired Beijing time to UTC and update the cron expression in `.github/workflows/daily-linkedin-post.yml`.

Examples:

| Beijing Time | UTC Time | Cron |
| --- | --- | --- |
| 09:30 | 01:30 | `30 1 * * *` |
| 12:00 | 04:00 | `0 4 * * *` |
| 18:30 | 10:30 | `30 10 * * *` |

## SMTP Notes For Common Email Providers

### Gmail

- Use `smtp.gmail.com`.
- Use port `587` with TLS or port `465` with SSL.
- You usually need an app password, not your normal Gmail password.
- App passwords require 2-Step Verification to be enabled.

### QQ Email

- Use `smtp.qq.com`.
- Use port `587` or `465`.
- Enable SMTP service in QQ Mail settings.
- Use the generated authorization code as `SMTP_PASS`.
- Do not use your normal QQ password as the SMTP password.

### Outlook / Microsoft 365

- Use `smtp.office365.com`.
- Use port `587`.
- Use an app password if your account requires multi-factor authentication.
- Some organization accounts block SMTP auth by policy, so check your admin settings if login fails.

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="you@example.com"
export SMTP_PASS="your-smtp-password-or-authorization-code"
export TO_EMAIL="recipient@example.com"
```

Run the script:

```bash
python main.py
```

## Generated Prompt

The script uses this prompt shape:

```text
You are writing a short LinkedIn post for a personal brand account.

Topic:
{topic}

Requirements:

* Write in English.
* Maximum 120 words.
* Start with a strong hook.
* Share one clear insight.
* Keep it practical and human.
* Avoid hashtags unless necessary.
* Avoid sounding too corporate.
* No emojis unless they add value.
* End with a light reflective sentence or question.
```

