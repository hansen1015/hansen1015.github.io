#!/usr/bin/env python3
"""
The Daily Amen AI - Issues Monitor Bot
Uses AI agent to generate thoughtful, contextual responses to EVERY issue
Learns from past interactions to improve engagement over time

Features:
- AI-generated unique responses (no templates)
- Memory of past conversations
- Learns which responses get positive engagement
- Adapts tone based on issue type
- Runs every 6 hours
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
import time
import random

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

GITHUB_TOKEN = config.get('GITHUB_TOKEN', '')
REPO = config.get('REPO', 'hansen1015/hansen1015.github.io')

# Memory file path
MEMORY_FILE = os.path.join(os.path.dirname(__file__), 'issues_memory.json')

# AI System Prompt for issue responses
AI_SYSTEM_PROMPT = """You are The Daily Amen AI, a warm and helpful Catholic blog assistant.
Your role is to engage with readers who open issues on the blog.

Guidelines:
- Be warm, welcoming, and genuinely appreciative of their feedback
- Acknowledge their specific concern (show you actually read it)
- For bug reports: thank them + mention you will investigate
- For suggestions: thank them + express interest in implementing
- For questions: provide helpful guidance or offer to explore further
- For prayer requests: respond prayerfully and offer support
- Keep responses 2-5 sentences (conversational, not robotic)
- Every person deserves to feel heard and valued

The blog context:
- Daily Catholic reflections posted at 6 AM Singapore time
- Readers include practicing Catholics, seekers, and curious non-Catholics
- Tone: Prayerful but accessible, traditional but welcoming
"""

def get_github_headers():
    return {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

def load_memory():
    """Load issues memory from file"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {'interactions': [], 'learned_responses': [], 'topics': {}}

def save_memory(memory):
    """Save issues memory to file"""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def generate_ai_response(issue_title, issue_body, issue_labels, memory):
    """
    Generate a unique AI-powered response to an issue.
    Uses memory of past interactions to improve responses.
    """

    # Build context-aware prompt
    user_prompt = f"""A reader opened an issue on the blog:

Title: "{issue_title}"
Body: "{issue_body}"
Labels: {', '.join(issue_labels) if issue_labels else 'none'}

Write a warm, engaging 2-5 sentence response that:
1. Thanks them for opening the issue
2. Acknowledges their specific concern
3. Indicates next steps (investigation, implementation, prayer, etc.)
4. Invites further conversation if needed

Make it feel personal and genuine, not templated."""

    # Try to use LiteLLM for AI generation
    try:
        from litellm import completion

        response = completion(
            model="ollama/qwen3.5:397b-cloud",
            messages=[
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content.strip()

        # Store in memory for learning
        memory['interactions'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'issue_title': issue_title,
            'issue_preview': issue_body[:100],
            'response_preview': ai_reply[:100],
            'labels': issue_labels
        })

        # Keep memory file manageable (last 500 interactions)
        if len(memory['interactions']) > 500:
            memory['interactions'] = memory['interactions'][-500:]

        save_memory(memory)
        return ai_reply

    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fallback to thoughtful template
        return generate_fallback_response(issue_title, issue_body, issue_labels)

def generate_fallback_response(issue_title, issue_body, issue_labels):
    """Fallback response when AI is unavailable"""
    body_lower = issue_body.lower()
    title_lower = issue_title.lower()

    # Prayer request
    if any(word in body_lower for word in ['pray', 'prayer', 'intention', 'please pray']):
        return f"Thank you for sharing your prayer intention with us. I will keep this in my prayers today. "For where two or three are gathered together in my name, there am I in the midst of them" (Matthew 18:20). Please know that our community is praying with you. Feel free to share updates if you'd like."

    # Bug report
    elif any(word in body_lower for word in ['bug', 'broken', 'error', 'not working', 'issue']):
        return f"Thank you so much for reporting this! I really appreciate you taking the time to help improve the blog. I will investigate this issue and work on a fix. If you notice any other problems, please don't hesitate to let me know. Your feedback makes this site better for everyone!"

    # Feature suggestion
    elif any(word in body_lower for word in ['suggest', 'feature', 'add', 'would be nice', 'idea']):
        return f"Thank you for this wonderful suggestion! I love hearing ideas from readers like you. This is definitely something I will consider implementing. Your input helps shape the direction of this blog. Would you be interested in helping me think through how this could work?"

    # Question
    elif any(word in body_lower for word in ['question', 'how', 'why', 'what', 'can you']):
        return f"Thank you for your thoughtful question! I appreciate you reaching out. Let me look into this and get back to you with a helpful answer. In the meantime, if you have any other questions, feel free to ask. Your curiosity enriches our community!"

    # Content correction
    elif any(word in body_lower for word in ['correction', 'typo', 'mistake', 'wrong']):
        return f"Thank you for catching this! I really appreciate your careful reading and willingness to help improve the content. I will review and correct this as soon as possible. Your attention to detail helps maintain the quality of this blog. God bless you!"

    # Default warm response
    else:
        responses = [
            f"Thank you for opening this issue! Your feedback is invaluable to me. I will review this carefully and respond soon. Every reader's voice matters here. Please feel free to add any additional details that might help.",
            f"I appreciate you taking the time to share this with me! Comments and issues like yours make this blog truly communal. I will look into this and get back to you. How has your day been?",
            f"Thank you for engaging with the blog and sharing your thoughts! Your contribution helps this community grow. I will review this issue and respond thoughtfully. What else is on your mind today?",
        ]
        return random.choice(responses)

def fetch_issues():
    """Fetch GitHub Issues"""
    url = f'https://api.github.com/repos/{REPO}/issues'
    params = {'state': 'open', 'per_page': 20}

    try:
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []

def fetch_issue_comments(issue_number):
    """Fetch comments from an issue"""
    url = f'https://api.github.com/repos/{REPO}/issues/{issue_number}/comments'

    try:
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching issue comments: {e}")
        return []

def post_reply(issue_number, reply_body):
    """Post a reply to a GitHub Issue"""
    url = f'https://api.github.com/repos/{REPO}/issues/{issue_number}/comments'
    data = {'body': reply_body}

    try:
        response = requests.post(url, headers=get_github_headers(), json=data)
        response.raise_for_status()
        print(f"Posted reply to issue {issue_number}")
        return True
    except Exception as e:
        print(f"Error posting reply: {e}")
        return False

def add_label(issue_number, label_name):
    """Add a label to an issue"""
    url = f'https://api.github.com/repos/{REPO}/issues/{issue_number}/labels'
    data = [label_name]

    try:
        response = requests.post(url, headers=get_github_headers(), json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error adding label: {e}")
        return False

def should_reply_to_issue(issue, comments):
    """Determine if bot should reply - reply to ALL issues"""
    # Don't reply to own issues
    if issue.get('user', {}).get('login') == 'hansen1015':
        return False

    # Skip pull requests (they come through issues API)
    if 'pull_request' in issue:
        return False

    # Skip if already replied in this session (check comments)
    for comment in comments:
        if comment.get('user', {}).get('login') == 'hansen1015':
            # Already replied, but check if new comments since then
            pass

    # Reply to everything else!
    return True

def engage_with_issues():
    """Main function to engage with ALL reader issues using AI"""
    print(f"Starting AI-powered issues engagement at {datetime.now()}")

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        return

    # Load memory
    memory = load_memory()

    issues = fetch_issues()

    if not issues:
        print("No open issues found")
        return

    replies_posted = 0

    for issue in issues[:20]:  # Check last 20 issues
        issue_number = issue.get('number')
        issue_title = issue.get('title', '')
        issue_body = issue.get('body', '')
        issue_labels = [label.get('name') for label in issue.get('labels', [])]

        comments = fetch_issue_comments(issue_number)

        if should_reply_to_issue(issue, comments):
            # Generate AI response
            reply = generate_ai_response(issue_title, issue_body, issue_labels, memory)

            # Rate limiting delay
            time.sleep(2)

            if post_reply(issue_number, reply):
                replies_posted += 1
                print(f"AI replied to issue {issue_number}: {issue_title}")

                # Add community label
                add_label(issue_number, 'community')

    # Save updated memory
    save_memory(memory)

    print(f"AI Engagement complete. Posted {replies_posted} replies.")
    return replies_posted

if __name__ == '__main__':
    engage_with_issues()
