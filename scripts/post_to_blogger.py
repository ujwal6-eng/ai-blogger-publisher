import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

# ---------- CONFIG ----------
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = os.environ.get("BLOGGER_BLOG_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ---------- LOAD TOPIC ----------
with open("topics.txt", "r", encoding="utf-8") as f:
    topic = f.readline().strip()

# ---------- LOAD PROMPT ----------
with open("prompts/blog_prompt.txt", "r", encoding="utf-8") as f:
    prompt_template = f.read()

prompt = prompt_template.replace("{{TOPIC}}", topic)

# ---------- AI CONTENT ----------
def generate_blog(prompt):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    )

    return response.json()["choices"][0]["message"]["content"]

content_html = generate_blog(prompt)

# ---------- AUTH ----------
creds = Credentials.from_authorized_user_file(
    "token.json", SCOPES
)

service = build("blogger", "v3", credentials=creds)

# ---------- POST ----------
post_body = {
    "kind": "blogger#post",
    "title": topic,
    "content": content_html,
    "labels": ["AI", "Automation", "Blogging"]
}

post = service.posts().insert(
    blogId=BLOG_ID,
    body=post_body,
    isDraft=False
).execute()

print("✅ Blog published:", post["url"])
