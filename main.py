import json
import os
import random
import smtplib
import ssl
import sys
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
TOPICS_FILE = BASE_DIR / "topics.json"
LOG_FILE = BASE_DIR / "posts-log.json"
MAX_WORDS = 120


PROMPT_TEMPLATE = """You are writing a short LinkedIn post for a personal brand account.

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
"""


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_topics() -> list[str]:
    try:
        with TOPICS_FILE.open("r", encoding="utf-8") as file:
            topics = json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Could not find {TOPICS_FILE.name}.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{TOPICS_FILE.name} contains invalid JSON.") from exc

    if not isinstance(topics, list) or not all(isinstance(item, str) for item in topics):
        raise RuntimeError(f"{TOPICS_FILE.name} must be a JSON array of strings.")

    clean_topics = [topic.strip() for topic in topics if topic.strip()]
    if not clean_topics:
        raise RuntimeError(f"{TOPICS_FILE.name} must contain at least one topic.")

    return clean_topics


def trim_to_word_limit(text: str, max_words: int = MAX_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).rstrip(".,;:") + "."


def generate_post(topic: str) -> str:
    client = OpenAI(api_key=require_env("OPENAI_API_KEY"))
    prompt = PROMPT_TEMPLATE.format(topic=topic)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write concise, thoughtful LinkedIn posts for personal brand accounts.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=220,
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("OpenAI returned an empty post.")

    return trim_to_word_limit(content)


def send_email(topic: str, post: str) -> str:
    smtp_host = require_env("SMTP_HOST")
    smtp_port = int(require_env("SMTP_PORT"))
    smtp_user = require_env("SMTP_USER")
    smtp_pass = require_env("SMTP_PASS")
    to_email = require_env("TO_EMAIL")

    today = datetime.now().strftime("%Y-%m-%d")
    message = EmailMessage()
    message["Subject"] = f"LinkedIn Short Post - {today}"
    message["From"] = smtp_user
    message["To"] = to_email
    message.set_content(
        f"""Today's topic:
{topic}

LinkedIn short post:
{post}

Please review before publishing.
"""
    )

    context = ssl.create_default_context()
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(message)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.send_message(message)

    return "sent"


def append_log(entry: dict) -> None:
    if LOG_FILE.exists():
        try:
            with LOG_FILE.open("r", encoding="utf-8") as file:
                logs = json.load(file)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    if not isinstance(logs, list):
        logs = []

    logs.append(entry)
    with LOG_FILE.open("w", encoding="utf-8") as file:
        json.dump(logs, file, ensure_ascii=False, indent=2)
        file.write("\n")


def main() -> int:
    timestamp = datetime.now().isoformat(timespec="seconds")
    topic = None
    post = None

    try:
        topics = load_topics()
        topic = random.choice(topics)
        print(f"Selected topic: {topic}")

        post = generate_post(topic)
        print(f"Generated post with {len(post.split())} words.")

        send_status = send_email(topic, post)
        print("Email sent successfully.")
        append_log(
            {
                "datetime": timestamp,
                "topic": topic,
                "content": post,
                "send_status": send_status,
            }
        )
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        append_log(
            {
                "datetime": timestamp,
                "topic": topic,
                "content": post,
                "send_status": f"failed: {exc}",
            }
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

