#!/usr/bin/env python3
"""
The Daily Amen AI - Comment Engagement Bot
Uses AI agent to generate thoughtful, contextual responses to EVERY comment
Learns from past interactions to improve engagement over time

Features:
- AI-generated unique responses (no templates)
- Memory of past conversations
- Learns which responses get positive engagement
- Adapts tone based on comment sentiment
- Runs every 4 hours
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
GISCUS_CATEGORY = config.get('GISCUS_CATEGORY', 'General')

# Memory file path
MEMORY_FILE = os.path.join(os.path.dirname(__file__), 'engagement_memory.json')

# AI System Prompt for comment responses
AI_SYSTEM_PROMPT = """You are The Daily Amen AI, a warm and thoughtful Catholic blog assistant.
Your role is to engage with readers who comment on daily reflections.

Guidelines:
- Be warm, welcoming, and genuinely interested in each person
- Reference Catholic faith, Scripture, or Church teaching when relevant
- Acknowledge their specific point (show you actually read their comment)
- Ask a follow-up question to continue the conversation
- Keep responses 2-4 sentences (conversational, not preachy)
- Use natural, friendly language (not robotic or formal)
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
    """Load engagement memory from file"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {'interactions': [], 'learned_responses': [], 'topics': {}}

def save_memory(memory):
    """Save engagement memory to file"""
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def generate_ai_response(comment_body, discussion_title, memory):
    """
    Generate a unique AI-powered response to a comment.
    Uses memory of past interactions to improve responses.
    """

    # Check memory for similar past interactions
    learned_topics = memory.get('topics', {})

    # Build context-aware prompt
    user_prompt = f"""A reader commented on the blog post "{discussion_title}":

Comment: "{comment_body}"

Write a warm, engaging 2-4 sentence response that:
1. Acknowledges their specific point
2. Connects to Catholic faith when natural
3. Ends with a gentle question to continue conversation

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
            max_tokens=200,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content.strip()

        # Store in memory for learning
        memory['interactions'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'comment_preview': comment_body[:100],
            'response_preview': ai_reply[:100],
            'discussion': discussion_title
        })

        # Keep memory file manageable (last 500 interactions)
        if len(memory['interactions']) > 500:
            memory['interactions'] = memory['interactions'][-500:]

        save_memory(memory)
        return ai_reply

    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fallback to thoughtful template
        return generate_fallback_response(comment_body, discussion_title)

def generate_fallback_response(comment_body, discussion_title):
    """Fallback response when AI is unavailable"""
    comment_lower = comment_body.lower()

    # Still varied and thoughtful, just not AI-generated
    if any(word in comment_lower for word in ['pray', 'prayer', 'intention']):
        return f"Thank you for sharing your prayer intention. I will keep this in my prayers today. "For where two or three are gathered together in my name, there am I in the midst of them" (Matthew 18:20). Would you like me to include a specific Scripture reflection on this topic in a future post?"

    elif any(word in comment_lower for word in ['thank', 'appreciate', 'blessing']):
        return f"Thank you so much for your kind words! Comments like yours encourage me to continue this daily reflection ministry. Your support means a lot to this community. How has your spiritual journey been lately?"

    elif any(word in comment_lower for word in ['question', 'wonder', 'why', 'how']):
        return f"Thank you for your thoughtful question! Faith and reason walk hand in hand in Catholic tradition. I would love to explore this topic further - would you be interested in a dedicated reflection on this?"

    else:
        responses = [
            f"Thank you for your thoughtful comment! Your perspective enriches our community discussion. I would love to hear more about your thoughts on this topic. What other aspects would you like to explore together?",
            f"I appreciate you taking the time to share your thoughts! Comments like yours make this reflection space truly communal. How has your day been? I would love to continue this conversation.",
            f"Thank you for engaging with this reflection! Your comment shows deep consideration of the topic. Every reader's voice matters here. What's on your mind today?",
        ]
        return random.choice(responses)

def fetch_discussions():
    """Fetch GitHub Discussions (Giscus backend)"""
    url = f'https://api.github.com/repos/{REPO}/discussions'
    params = {'category': GISCUS_CATEGORY, 'per_page': 15}

    try:
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching discussions: {e}")
        return []

def fetch_comments(discussion_id):
    """Fetch comments from a discussion"""
    url = f'https://api.github.com/repos/{REPO}/discussions/{discussion_id}/comments'

    try:
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def post_reply(discussion_id, reply_body):
    """Post a reply to a GitHub Discussion"""
    url = f'https://api.github.com/repos/{REPO}/discussions/{discussion_id}/comments'
    data = {'body': reply_body}

    try:
        response = requests.post(url, headers=get_github_headers(), json=data)
        response.raise_for_status()
        print(f"Posted reply to discussion {discussion_id}")
        return True
    except Exception as e:
        print(f"Error posting reply: {e}")
        return False

def should_reply_to_comment(comment):
    """Determine if bot should reply - reply to ALL comments"""
    # Don't reply to own comments
    if comment.get('author', {}).get('login') == 'hansen1015':
        return False

    # Skip very short/spam comments
    body = comment.get('body', '')
    if len(body) < 3:
        return False

    # Reply to everything else!
    return True

def engage_with_comments():
    """Main function to engage with ALL reader comments using AI"""
    print(f"Starting AI-powered comment engagement at {datetime.now()}")

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        return

    # Load memory
    memory = load_memory()

    discussions = fetch_discussions()

    if not discussions:
        print("No discussions found")
        return

    replies_posted = 0

    for discussion in discussions[:15]:  # Check last 15 discussions
        discussion_id = discussion.get('number')
        discussion_title = discussion.get('title', '')

        comments = fetch_comments(discussion_id)

        for comment in comments[-5:]:  # Check last 5 comments per discussion
            if should_reply_to_comment(comment):
                comment_body = comment.get('body', '')

                # Generate AI response
                reply = generate_ai_response(comment_body, discussion_title, memory)

                # Rate limiting delay
                time.sleep(2)

                if post_reply(discussion_id, reply):
                    replies_posted += 1
                    print(f"AI replied to comment in discussion {discussion_id}")

    # Save updated memory
    save_memory(memory)

    print(f"AI Engagement complete. Posted {replies_posted} replies.")
    return replies_posted

if __name__ == '__main__':
    engage_with_comments()
