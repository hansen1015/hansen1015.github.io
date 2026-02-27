#!/usr/bin/env python3
"""
The Daily Amen AI - Issues Monitor Bot
Uses AI agent to generate thoughtful, doctrinally sound responses to EVERY issue
References Catholic Catechism (CCC) with vatican.va links

Features:
- AI-generated unique responses (no templates)
- Memory of past conversations
- CCC references with links
- Kind, loving, knowledgeable tone
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

# CCC Reference Database
CCC_REFERENCES = {
    'prayer': [
        ('CCC 2559', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Prayer is the raising of one's mind and heart to God'),
        ('CCC 2607', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Jesus prays and teaches us to pray'),
    ],
    'faith': [
        ('CCC 142', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'By faith, man completely submits his intellect and will to God'),
        ('CCC 161', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Faith is necessary for salvation'),
    ],
    'love': [
        ('CCC 1822', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Charity is the theological virtue by which we love God above all'),
        ('CCC 1827', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The fruits of charity are joy, peace, and mercy'),
    ],
    'suffering': [
        ('CCC 1501', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Illness can lead to anguish and self-absorption'),
        ('CCC 1521', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Union with the passion of Christ'),
    ],
    'forgiveness': [
        ('CCC 2842', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'This "as" is not unique in Jesus teaching'),
        ('CCC 982', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'There is no offense however serious that the Church cannot forgive'),
    ],
    'mercy': [
        ('CCC 1846', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Gospel is the revelation in Jesus Christ of God's mercy'),
        ('CCC 2839', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'This mercy is not merely a word'),
    ],
    'peace': [
        ('CCC 2304', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Respect for and development of human life require peace'),
        ('CCC 2305', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Peace is not merely the absence of war'),
    ],
    'community': [
        ('CCC 953', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Communion of charisms in the Church'),
        ('CCC 949', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The faithful share in the communion of the Church'),
    ],
    'truth': [
        ('CCC 2468', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Truthfulness upholds justice and charity'),
        ('CCC 2504', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The truth is a virtue that seeks authenticity'),
    ],
    'hope': [
        ('CCC 1817', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Hope is the theological virtue by which we desire eternal life'),
        ('CCC 1820', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Christian hope unfolds from the beginning of Jesus preaching'),
    ],
    'default': [
        ('CCC 1', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'God, infinitely perfect and blessed in himself'),
        ('CCC 27', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The desire for God is written in the human heart'),
    ]
}

def get_github_headers():
    return {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {'interactions': [], 'learned_responses': [], 'topics': {}}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def detect_topic(issue_title, issue_body):
    """Detect topic from issue to find relevant CCC references"""
    text = (issue_title + ' ' + issue_body).lower()

    topic_keywords = {
        'prayer': ['pray', 'prayer', 'intention', 'rosary'],
        'faith': ['faith', 'believe', 'belief', 'trust'],
        'love': ['love', 'charity', 'compassion'],
        'suffering': ['suffer', 'pain', 'illness', 'sick', 'grief', 'loss'],
        'forgiveness': ['forgive', 'forgiveness', 'sorry', 'repent'],
        'mercy': ['mercy', 'merciful', 'compassion'],
        'peace': ['peace', 'peaceful', 'conflict'],
        'community': ['community', 'together', 'share', 'help'],
        'truth': ['truth', 'honest', 'correct', 'mistake'],
        'hope': ['hope', 'hopeful', 'despair', 'encouragement'],
    }

    for topic, keywords in topic_keywords.items():
        if any(kw in text for kw in keywords):
            return topic

    return 'default'

def get_ccc_reference(topic):
    references = CCC_REFERENCES.get(topic, CCC_REFERENCES['default'])
    return random.choice(references)

def generate_ai_response(issue_title, issue_body, issue_labels, memory):
    """Generate AI-powered response with CCC integration"""

    topic = detect_topic(issue_title, issue_body)
    ccc_ref = get_ccc_reference(topic)

    user_prompt = f"""A reader opened an issue on the blog:

Title: "{issue_title}"
Body: "{issue_body}"
Labels: {', '.join(issue_labels) if issue_labels else 'none'}

Detected Topic: {topic}
CCC Reference: {ccc_ref[0]} - "{ccc_ref[2]}"
CCC Link: {ccc_ref[1]}

Write a warm, loving, doctrinally sound response that:
1. Thanks them sincerely for opening the issue
2. Acknowledges their specific concern with genuine care
3. References the CCC teaching naturally when relevant
4. Includes the CCC paragraph with link: [{ccc_ref[0]}]({ccc_ref[1]})
5. Indicates clear next steps
6. Invites further conversation
7. Keep it 3-5 sentences, conversational not robotic

Tone: Kind, loving, knowledgeable, welcoming like a wise Catholic friend.

Make it feel personal and genuine, not templated."""

    try:
        from litellm import completion

        response = completion(
            model="ollama/qwen3.5:397b-cloud",
            messages=[
                {"role": "system", "content": """You are The Daily Amen AI, a kind and loving Catholic blog assistant.

Your characteristics:
- Deeply knowledgeable in Catholic doctrine and Catechism (CCC)
- Always warm, welcoming, and genuinely caring
- Never judgmental or condemning
- References CCC with vatican.va links when appropriate
- Speaks like a wise, gentle Catholic friend
- Every person deserves to feel heard and valued

When responding to issues:
- Thank them sincerely for their feedback
- Acknowledge their specific concern
- Share relevant Church teaching with love
- Include CCC paragraph with link: [CCC 1234](https://www.vatican.va/archive/ENG0015/_INDEX.HTM)
- Indicate clear next steps
- Keep responses 3-5 sentences, natural and conversational

Remember: Truth spoken in love is the most powerful witness."""},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content.strip()

        memory['interactions'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'issue_title': issue_title,
            'issue_preview': issue_body[:100],
            'response_preview': ai_reply[:100],
            'labels': issue_labels,
            'topic': topic,
            'ccc_used': ccc_ref[0]
        })

        if len(memory['interactions']) > 500:
            memory['interactions'] = memory['interactions'][-500:]

        save_memory(memory)
        return ai_reply

    except Exception as e:
        print(f"AI generation failed: {e}")
        return generate_fallback_response(issue_title, issue_body, issue_labels, topic, ccc_ref)

def generate_fallback_response(issue_title, issue_body, issue_labels, topic, ccc_ref):
    """Fallback with CCC reference when AI unavailable"""
    body_lower = issue_body.lower()

    if any(word in body_lower for word in ['pray', 'prayer', 'intention']):
        return f"Thank you for sharing your prayer intention with us. I will keep this in my prayers today. As the Catechism reminds us, "Prayer is the raising of one's mind and heart to God" [{ccc_ref[0]}]({ccc_ref[1]}). Please know that our community is praying with you."

    elif any(word in body_lower for word in ['bug', 'broken', 'error', 'not working']):
        return f"Thank you so much for reporting this! I really appreciate you taking the time to help improve the blog. The Church teaches us to pursue truth in all things [{ccc_ref[0]}]({ccc_ref[1]}). I will investigate this issue and work on a fix. Your feedback makes this site better for everyone!"

    elif any(word in body_lower for word in ['suggest', 'feature', 'add', 'idea']):
        return f"Thank you for this wonderful suggestion! I love hearing ideas from readers like you. The Catechism speaks of the "communion of charisms" where each person contributes their gifts [{ccc_ref[0]}]({ccc_ref[1]}). This is definitely something I will consider implementing. Would you be interested in helping me think through how this could work?"

    elif any(word in body_lower for word in ['question', 'how', 'why', 'what']):
        return f"Thank you for your thoughtful question! I appreciate you reaching out. As the Catechism says, "The desire for God is written in the human heart" [{ccc_ref[0]}]({ccc_ref[1]}). Let me look into this and get back to you with a helpful answer. Your curiosity enriches our community!"

    else:
        return f"Thank you for opening this issue! Your feedback is invaluable to me. The Catechism reminds us that "The desire for God is written in the human heart" [{ccc_ref[0]}]({ccc_ref[1]}). I will review this carefully and respond soon. Every reader's voice matters here. Please feel free to add any additional details that might help."

def fetch_issues():
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
    url = f'https://api.github.com/repos/{REPO}/issues/{issue_number}/comments'

    try:
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching issue comments: {e}")
        return []

def post_reply(issue_number, reply_body):
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
    if issue.get('user', {}).get('login') == 'hansen1015':
        return False
    if 'pull_request' in issue:
        return False
    return True

def engage_with_issues():
    print(f"Starting AI-powered issues engagement at {datetime.now()}")

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        return

    memory = load_memory()
    issues = fetch_issues()

    if not issues:
        print("No open issues found")
        return

    replies_posted = 0

    for issue in issues[:20]:
        issue_number = issue.get('number')
        issue_title = issue.get('title', '')
        issue_body = issue.get('body', '')
        issue_labels = [label.get('name') for label in issue.get('labels', [])]

        comments = fetch_issue_comments(issue_number)

        if should_reply_to_issue(issue, comments):
            reply = generate_ai_response(issue_title, issue_body, issue_labels, memory)
            time.sleep(2)

            if post_reply(issue_number, reply):
                replies_posted += 1
                print(f"AI replied to issue {issue_number}: {issue_title}")
                add_label(issue_number, 'community')

    save_memory(memory)
    print(f"AI Engagement complete. Posted {replies_posted} replies.")
    return replies_posted

if __name__ == '__main__':
    engage_with_issues()
