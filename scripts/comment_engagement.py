#!/usr/bin/env python3
"""
The Daily Amen AI - Comment Engagement Bot
Uses AI agent to generate thoughtful, contextual responses to EVERY comment
Learns from past interactions and references Catholic Catechism (CCC)

Features:
- AI-generated unique responses (no templates)
- Memory of past conversations
- CCC references with vatican.va links
- Kind, loving, doctrinally sound responses
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

# CCC Reference Database - Key paragraphs for common topics
CCC_REFERENCES = {
    'prayer': [
        ('CCC 2559', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Prayer is the raising of one's mind and heart to God'),
        ('CCC 2607', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Jesus prays and teaches us to pray'),
        ('CCC 2742', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Pray at all times with thanksgiving'),
    ],
    'faith': [
        ('CCC 142', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'By faith, man completely submits his intellect and will to God'),
        ('CCC 161', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Faith is necessary for salvation'),
        ('CCC 166', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Faith is a personal act and also ecclesial'),
    ],
    'love': [
        ('CCC 1822', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Charity is the theological virtue by which we love God above all'),
        ('CCC 1827', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The fruits of charity are joy, peace, and mercy'),
        ('CCC 2212', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The fourth commandment illuminates relationships in society'),
    ],
    'hope': [
        ('CCC 1817', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Hope is the theological virtue by which we desire eternal life'),
        ('CCC 1820', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Christian hope unfolds from the beginning of Jesus preaching'),
    ],
    'suffering': [
        ('CCC 1501', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Illness can lead to anguish and self-absorption'),
        ('CCC 1521', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Union with the passion of Christ'),
        ('CCC 2015', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The way of perfection passes by way of the Cross'),
    ],
    'forgiveness': [
        ('CCC 2842', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'This "as" is not unique in Jesus teaching'),
        ('CCC 2844', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Christian prayer extends to the forgiveness of enemies'),
        ('CCC 982', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'There is no offense however serious that the Church cannot forgive'),
    ],
    'eucharist': [
        ('CCC 1324', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Eucharist is the source and summit of Christian life'),
        ('CCC 1374', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'In the most blessed sacrament of the Eucharist'),
        ('CCC 1413', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'By the consecration the transubstantiation is operated'),
    ],
    'mary': [
        ('CCC 963', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Virgin Mary is acknowledged as Mother of God'),
        ('CCC 969', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Mary's role in the Church is inseparable from her union with Christ'),
        ('CCC 2677', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'In prayer we unite ourselves to the heart of Mary'),
    ],
    'saints': [
        ('CCC 828', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'By canonizing some members of the faithful'),
        ('CCC 957', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Communion with the saints joins us to Christ'),
        ('CCC 956', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The intercession of the saints'),
    ],
    'scripture': [
        ('CCC 101', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Church has always venerated the divine Scriptures'),
        ('CCC 104', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'In Sacred Scripture the Church finds constant nourishment'),
        ('CCC 131', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'And such is the force and power of the Word of God'),
    ],
    'church': [
        ('CCC 748', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Church is the People of God'),
        ('CCC 763', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Church was prepared in the Old Covenant'),
        ('CCC 811', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'This is the sole Church of Christ'),
    ],
    'salvation': [
        ('CCC 161', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Faith is necessary for salvation'),
        ('CCC 1816', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Disciples of Christ must not only keep the faith'),
        ('CCC 2010', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Since the initiative belongs to God in the order of grace'),
    ],
    'mercy': [
        ('CCC 1846', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Gospel is the revelation in Jesus Christ of God's mercy'),
        ('CCC 2839', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'This mercy is not merely a word'),
        ('CCC 270', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'God's almighty power is in no way arbitrary'),
    ],
    'grace': [
        ('CCC 1996', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Grace is favor, the free and undeserved help'),
        ('CCC 2000', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Sanctifying grace is a habitual gift'),
        ('CCC 2023', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Sanctifying grace makes us pleasing to God'),
    ],
    'peace': [
        ('CCC 2304', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Respect for and development of human life require peace'),
        ('CCC 2305', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Peace is not merely the absence of war'),
        ('CCC 2437', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Love of country and responsibility for the common good'),
    ],
    'family': [
        ('CCC 2201', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Christian family is a communion of persons'),
        ('CCC 2204', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The Christian family constitutes a specific revelation'),
        ('CCC 2223', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Parents have the first responsibility for education'),
    ],
    'default': [
        ('CCC 1', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'God, infinitely perfect and blessed in himself'),
        ('CCC 27', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'The desire for God is written in the human heart'),
        ('CCC 2559', 'https://www.vatican.va/archive/ENG0015/_INDEX.HTM', 'Prayer is the raising of one's mind and heart to God'),
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

def detect_topic(comment_body):
    """Detect topic from comment to find relevant CCC references"""
    body_lower = comment_body.lower()

    topic_keywords = {
        'prayer': ['pray', 'prayer', 'praying', 'intention', 'rosary', 'novena'],
        'faith': ['faith', 'believe', 'belief', 'trust', 'doubt'],
        'love': ['love', 'charity', 'compassion', 'care'],
        'hope': ['hope', 'hopeful', 'despair', 'encouragement'],
        'suffering': ['suffer', 'pain', 'illness', 'sick', 'dying', 'grief', 'loss'],
        'forgiveness': ['forgive', 'forgiveness', 'sorry', 'repent', 'confess'],
        'eucharist': ['eucharist', 'mass', 'communion', 'host', 'sacrament'],
        'mary': ['mary', 'virgin', 'mother of god', 'rosary', 'our lady'],
        'saints': ['saint', 'saints', 'canonized', 'feast day'],
        'scripture': ['bible', 'scripture', 'verse', 'gospel', 'reading'],
        'church': ['church', 'catholic', 'pope', 'bishop', 'priest'],
        'salvation': ['salvation', 'saved', 'heaven', 'eternal life'],
        'mercy': ['mercy', 'merciful', 'compassion', 'kindness'],
        'grace': ['grace', 'blessing', 'blessed', 'gift from god'],
        'peace': ['peace', 'peaceful', 'conflict', 'war'],
        'family': ['family', 'spouse', 'children', 'parents', 'marriage'],
    }

    for topic, keywords in topic_keywords.items():
        if any(kw in body_lower for kw in keywords):
            return topic

    return 'default'

def get_ccc_reference(topic):
    """Get CCC reference for the detected topic"""
    references = CCC_REFERENCES.get(topic, CCC_REFERENCES['default'])
    return random.choice(references)

def generate_ai_response(comment_body, discussion_title, memory):
    """Generate AI-powered response with CCC integration"""

    # Detect topic and get CCC reference
    topic = detect_topic(comment_body)
    ccc_ref = get_ccc_reference(topic)

    # Build context-aware prompt
    user_prompt = f"""A reader commented on the blog post "{discussion_title}":

Comment: "{comment_body}"

Detected Topic: {topic}
CCC Reference: {ccc_ref[0]} - "{ccc_ref[2]}"
CCC Link: {ccc_ref[1]}

Write a warm, loving, doctrinally sound response that:
1. Acknowledges their specific point with genuine care
2. References the CCC teaching naturally (not forced)
3. Includes the CCC paragraph number with link: [{ccc_ref[0]}]({ccc_ref[1]})
4. Ends with a gentle question to continue conversation
5. Keep it 3-5 sentences, conversational not preachy

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

When responding:
- Acknowledge the person's specific situation
- Share relevant Church teaching with love
- Include CCC paragraph with link: [CCC 1234](https://www.vatican.va/archive/ENG0015/_INDEX.HTM)
- End with an inviting question
- Keep responses 3-5 sentences, natural and conversational

Remember: Truth spoken in love is the most powerful witness."""},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content.strip()

        # Store in memory
        memory['interactions'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'comment_preview': comment_body[:100],
            'response_preview': ai_reply[:100],
            'discussion': discussion_title,
            'topic': topic,
            'ccc_used': ccc_ref[0]
        })

        if len(memory['interactions']) > 500:
            memory['interactions'] = memory['interactions'][-500:]

        save_memory(memory)
        return ai_reply

    except Exception as e:
        print(f"AI generation failed: {e}")
        return generate_fallback_response(comment_body, discussion_title, topic, ccc_ref)

def generate_fallback_response(comment_body, discussion_title, topic, ccc_ref):
    """Fallback with CCC reference when AI unavailable"""
    comment_lower = comment_body.lower()

    if any(word in comment_lower for word in ['pray', 'prayer', 'intention']):
        return f"Thank you for sharing your prayer intention. I will keep this in my prayers today. As the Catechism reminds us, "Prayer is the raising of one's mind and heart to God" [{ccc_ref[0]}]({ccc_ref[1]}). Would you like me to include a specific Scripture reflection on this topic in a future post?"

    elif any(word in comment_lower for word in ['thank', 'appreciate', 'blessing']):
        return f"Thank you so much for your kind words! Comments like yours encourage me to continue this daily reflection ministry. The Church teaches that we should "pray at all times with thanksgiving" [{ccc_ref[0]}]({ccc_ref[1]}). How has your spiritual journey been lately?"

    elif any(word in comment_lower for word in ['question', 'wonder', 'why', 'how']):
        return f"Thank you for your thoughtful question! Faith and reason walk hand in hand in Catholic tradition. The Catechism says "The desire for God is written in the human heart" [{ccc_ref[0]}]({ccc_ref[1]}). Would you be interested in a dedicated reflection on this?"

    else:
        return f"Thank you for your thoughtful comment! Your perspective enriches our community discussion. As the Catechism teaches, "The desire for God is written in the human heart" [{ccc_ref[0]}]({ccc_ref[1]}). What other aspects would you like to explore together?"

def fetch_discussions():
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
    url = f'https://api.github.com/repos/{REPO}/discussions/{discussion_id}/comments'

    try:
        response = requests.get(url, headers=get_github_headers())
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

def post_reply(discussion_id, reply_body):
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
    if comment.get('author', {}).get('login') == 'hansen1015':
        return False
    body = comment.get('body', '')
    if len(body) < 3:
        return False
    return True

def engage_with_comments():
    print(f"Starting AI-powered comment engagement at {datetime.now()}")

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        return

    memory = load_memory()
    discussions = fetch_discussions()

    if not discussions:
        print("No discussions found")
        return

    replies_posted = 0

    for discussion in discussions[:15]:
        discussion_id = discussion.get('number')
        discussion_title = discussion.get('title', '')

        comments = fetch_comments(discussion_id)

        for comment in comments[-5:]:
            if should_reply_to_comment(comment):
                comment_body = comment.get('body', '')
                reply = generate_ai_response(comment_body, discussion_title, memory)
                time.sleep(2)

                if post_reply(discussion_id, reply):
                    replies_posted += 1
                    print(f"AI replied to comment in discussion {discussion_id}")

    save_memory(memory)
    print(f"AI Engagement complete. Posted {replies_posted} replies.")
    return replies_posted

if __name__ == '__main__':
    engage_with_comments()
