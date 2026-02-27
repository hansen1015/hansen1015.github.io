#!/usr/bin/env python3
"""
Comment Engagement Bot for Daily Catholic Reflection Blog

This script:
1. Fetches ALL comments from GitHub Discussions (Giscus backend)
2. Generates engaging, thoughtful replies for EVERY comment
3. Posts replies back to continue the conversation

Runs every 4 hours to stay engaged with readers.
"""

import os
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

def get_github_headers():
    return {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

def fetch_discussions():
    """Fetch GitHub Discussions (Giscus backend)"""
    url = f'https://api.github.com/repos/{REPO}/discussions'
    params = {'category': GISCUS_CATEGORY, 'per_page': 10}

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

def generate_reply(comment_body, discussion_title):
    """
    Generate an engaging reply to ANY comment.

    Guidelines:
    - Warm and welcoming tone
    - Encourage further discussion
    - Acknowledge the commenter's perspective
    - Make everyone feel heard and valued
    """

    comment_lower = comment_body.lower()

    # Prayer requests
    if any(word in comment_lower for word in ['pray', 'prayer', 'intention', 'request']):
        replies = [
            f"Thank you for sharing your prayer intention. I will keep this in my prayers today. "For where two or three are gathered together in my name, there am I in the midst of them" (Matthew 18:20). Would you like me to include a specific Scripture reflection on this topic in a future post?",
            f"I appreciate you entrusting us with this prayer request. The Rosary is a powerful intercession - have you considered meditating on the Sorrowful Mysteries during this time? I would love to hear your thoughts on how prayer has sustained you.",
        ]

    # Scripture questions
    elif any(word in comment_lower for word in ['verse', 'scripture', 'bible', 'gospel', 'read']):
        replies = [
            f"What a beautiful passage to reflect on! The Scripture you mentioned has rich depth in Catholic tradition. Have you explored the Church Fathers' commentary on this verse? I would love to create a reflection exploring this further - what aspects resonate most with you?",
            f"Thank you for bringing up this Scripture! It connects beautifully with today's reflection. The Catechism references this theme in several places. Would you be interested in a deeper dive into how the saints interpreted this passage?",
        ]

    # Lent/Seasonal
    elif any(word in comment_lower for word in ['lent', 'fast', 'sacrifice', 'penance']):
        replies = [
            f"Lent is such a profound time for spiritual growth! Your reflection on fasting resonates deeply. "Man shall not live by bread alone" (Matthew 4:4). How has your Lenten journey been so far? I would love to feature reader experiences in an upcoming post.",
            f"Thank you for sharing your Lenten practice! The three pillars of prayer, fasting, and almsgiving work together beautifully. Have you found any particular spiritual reading helpful during this season?",
        ]

    # Saints
    elif any(word in comment_lower for word in ['saint', 'feast', 'patron']):
        replies = [
            f"The saints are such wonderful models of faith! The saint you mentioned has an inspiring story. Their witness reminds us that holiness is achievable in every state of life. Would you like me to write a reflection on their spiritual teachings?",
            f"What a beautiful devotion to this saint! Their intercession has touched so many lives. I would love to explore their writings or reported miracles in a future post. What aspect of their life inspires you most?",
        ]

    # Questions/Doubts
    elif any(word in comment_lower for word in ['question', 'wonder', 'confused', 'difficult', 'struggle']):
        replies = [
            f"Thank you for your honest question. Faith and reason walk hand in hand in Catholic tradition - even the saints had moments of darkness (St. John of the Cross' "Dark Night"). Would you be open to discussing this further? I may create a reflection addressing this topic.",
            f"I appreciate your vulnerability in sharing this struggle. The Church has always welcomed honest questions - look at St. Thomas the Apostle! Your question could help others too. Would you like me to explore this topic in a future reflection?",
        ]

    # Personal testimonies
    elif any(word in comment_lower for word in ['experience', 'testimony', 'happen', 'felt', 'believe']):
        replies = [
            f"Thank you for sharing your personal experience! Testimonies like yours strengthen our community's faith. "We declare to you what was from the beginning... so that our joy may be complete" (1 John 1:1, 4). Would you be willing to share more about how your faith has grown?",
            f"Your testimony is a beautiful witness to God's work in your life! Stories like yours inspire others on their journey. Have you considered how this experience might help others facing similar situations?",
        ]

    # Thanks/Appreciation
    elif any(word in comment_lower for word in ['thank', 'appreciate', 'helpful', 'blessing']):
        replies = [
            f"Thank you so much for your kind words! Comments like yours encourage me to continue this daily reflection ministry. Your support means a lot to this community. How has your spiritual journey been lately?",
            f"I'm truly grateful for your feedback! Knowing these reflections resonate with readers like you is the greatest blessing. Please feel free to share any topics you'd like to see explored in future posts.",
        ]

    # Suggestions/Feedback
    elif any(word in comment_lower for word in ['suggest', 'idea', 'feature', 'improve']):
        replies = [
            f"Thank you for this wonderful suggestion! Reader input helps shape this blog into a true community space. I'll definitely consider this for future improvements. Is there anything else you'd like to see added?",
            f"What a great idea! I love when readers take an active role in building this community. Let me think about how to implement this. Would you be interested in contributing to this feature?",
        ]

    # General engagement - for ANY other comment
    else:
        replies = [
            f"Thank you for your thoughtful comment! Your perspective enriches our community discussion. I would love to hear more about your thoughts on this topic. What other aspects would you like to explore together?",
            f"I appreciate you taking the time to share your thoughts! Comments like yours make this reflection space truly communal. How has your day been? I would love to continue this conversation.",
            f"Thank you for engaging with this reflection! Your comment shows deep consideration of the topic. Every reader's voice matters here. Would you like to discuss how this applies to daily living?",
            f"Your comment is valued! I read every single comment and learn from this community. Thank you for being part of The Daily Amen AI family. What's on your mind today?",
        ]

    return random.choice(replies)

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
    """Determine if bot should reply to this comment - REPLY TO ALL"""
    # Don't reply to own comments
    if comment.get('author', {}).get('login') == 'hansen1015':
        return False

    # Don't reply if already replied by bot (check last comment)
    body = comment.get('body', '')
    if len(body) < 2:  # Skip empty/spam
        return False

    # REPLY TO EVERYTHING - no topic filtering!
    return True

def engage_with_comments():
    """Main function to engage with ALL reader comments"""
    print(f"Starting comment engagement at {datetime.now()}")

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        return

    discussions = fetch_discussions()

    if not discussions:
        print("No discussions found")
        return

    replies_posted = 0

    for discussion in discussions[:10]:  # Check last 10 discussions
        discussion_id = discussion.get('number')
        discussion_title = discussion.get('title', '')

        comments = fetch_comments(discussion_id)

        for comment in comments[-5:]:  # Check last 5 comments per discussion
            if should_reply_to_comment(comment):
                comment_body = comment.get('body', '')
                reply = generate_reply(comment_body, discussion_title)

                # Add delay to avoid rate limiting
                time.sleep(2)

                if post_reply(discussion_id, reply):
                    replies_posted += 1
                    print(f"Replied to comment in discussion {discussion_id}")

    print(f"Engagement complete. Posted {replies_posted} replies.")
    return replies_posted

if __name__ == '__main__':
    engage_with_comments()
