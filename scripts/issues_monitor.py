#!/usr/bin/env python3
"""
Issues Monitoring Bot for Daily Catholic Reflection Blog

This script:
1. Fetches new GitHub Issues
2. Categorizes them (bug, prayer, suggestion, question, critical)
3. Auto-responds to acknowledge and thank readers
4. Logs suggestions for future content
5. Flags critical issues for human review

Runs every 6 hours to stay engaged with readers.
"""

import os
import requests
import json
from datetime import datetime, timedelta
import time

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

GITHUB_TOKEN = config.get('GITHUB_TOKEN', '')
REPO = config.get('REPO', 'hansen1015/hansen1015.github.io')

# Issue category keywords
CATEGORIES = {
    'prayer': ['pray', 'prayer', 'intention', 'intercede', 'rosary', 'novena'],
    'suggestion': ['suggest', 'topic', 'saint', 'feast', 'season', 'advent', 'lent', 'idea'],
    'bug_technical': ['bug', 'error', 'broken', 'not working', 'layout', 'mobile', 'css', 'link'],
    'bug_content': ['wrong', 'incorrect', 'theology', 'doctrine', 'scripture', 'verse', 'date'],
    'question': ['question', 'ask', 'how', 'why', 'what', 'explain'],
    'collaboration': ['partner', 'collaborate', 'sponsor', 'advertise']
}

# Critical issues that need human review
CRITICAL_KEYWORDS = ['abuse', 'heresy', 'scandal', 'legal', 'cease', 'demand', 'threat']

def get_github_headers():
    return {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

def fetch_issues(state='open', since_hours=24):
    """Fetch GitHub Issues, optionally filtered by time"""
    url = f'https://api.github.com/repos/{REPO}/issues'
    params = {
        'state': state,
        'per_page': 20,
        'since': (datetime.utcnow() - timedelta(hours=since_hours)).isoformat() + 'Z'
    }

    try:
        response = requests.get(url, headers=get_github_headers(), params=params)
        response.raise_for_status()
        # Filter out pull requests (they appear in issues endpoint)
        issues = [i for i in response.json() if 'pull_request' not in i]
        return issues
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []

def categorize_issue(title, body):
    """Categorize issue based on title and body content"""
    text = (title + ' ' + body).lower()

    # Check for critical first
    if any(kw in text for kw in CRITICAL_KEYWORDS):
        return 'critical'

    # Check each category
    scores = {}
    for category, keywords in CATEGORIES.items():
        scores[category] = sum(1 for kw in keywords if kw in text)

    if not any(scores.values()):
        return 'general'

    # Return highest scoring category
    return max(scores, key=scores.get)

def generate_response(category, issue_title, issue_body):
    """Generate an appropriate auto-response based on issue category"""

    responses = {
        'prayer': f"""🙏 **Thank you for sharing your prayer intention**.

I have received your prayer request and will keep this intention in my prayers. This blog is committed to supporting our community's spiritual life through daily reflection and prayer.

**Your intention has been logged** and may inspire future reflection topics. You are in our prayers!

*"For where two or three are gathered together in my name, there am I in the midst of them."* - Matthew 18:20

---
*This is an automated response. A human may also review your request.*""",

        'suggestion': f"""💡 **Thank you for your wonderful suggestion**!

Your idea for "{issue_title[:50]}..." has been received and logged for future content planning. Reader suggestions like yours help shape this blog's direction.

**Next steps**:
- Your suggestion is added to our content backlog
- It may be featured in an upcoming daily reflection
- You'll be notified if we create content based on your idea

*"Iron sharpens iron, and one man sharpens another."* - Proverbs 27:17

---
*This is an automated response. Our team reviews all suggestions.*""",

        'bug_technical': f"""🐛 **Thank you for reporting this technical issue**.

I've received your report about "{issue_title[:50]}..." and will investigate this promptly.

**What happens next**:
1. Issue is logged in our tracking system
2. Technical team will investigate within 24-48 hours
3. We'll update this issue when a fix is deployed

If this is urgent, please reply with additional details (browser, device, screenshots).

---
*This is an automated response. Technical issues are reviewed by our team.*""",

        'bug_content': f"""⚠️ **Thank you for bringing this content concern to our attention**.

You've raised an important point about "{issue_title[:50]}...". Content accuracy, especially regarding theology and scripture, is taken very seriously.

**This issue has been flagged for human review**.

Our team will:
1. Review the content against Church teaching
2. Consult relevant sources (Scripture, Catechism, Church documents)
3. Make corrections if needed
4. Update this issue with our findings

*"The truth will set you free."* - John 8:32

---
*⚠️ This issue requires human review. A team member will respond soon.*""",

        'question': f"""📧 **Thank you for your question**!

You've asked about "{issue_title[:50]}...". We appreciate your engagement with the content.

**Response timeline**:
- General questions: Within 24-48 hours
- Theological questions: May take longer for careful discernment
- You'll receive a notification when we respond

If your question is urgent, please consider contacting your parish priest or spiritual director.

*"Ask, and it will be given to you; seek, and you will find."* - Matthew 7:7

---
*This is an automated response. We read every question and respond personally.*""",

        'collaboration': f"""🤝 **Thank you for your interest in collaboration**!

Your message about "{issue_title[:50]}..." has been received.

**This requires human review** - partnership and collaboration decisions are made by the blog administrator.

You can expect:
- Review within 3-5 business days
- Direct contact if there's a good fit
- Prayerful consideration of all proposals

---
*⚠️ This issue requires human review. Thank you for your patience.*""",

        'critical': f"""⚠️ **This issue has been flagged for immediate human review**.

Your message has been received and escalated to the blog administrator.

**Please expect**:
- Priority review within 24 hours
- Direct response from administrator
- Appropriate action as needed

---
*⚠️ CRITICAL: This issue requires immediate human attention.*""",

        'general': f"""🙏 **Thank you for reaching out**!

Your message "{issue_title[:50]}..." has been received. We appreciate you taking the time to engage with this blog.

**What happens next**:
- Your issue is logged and will be reviewed
- We aim to respond within 48 hours
- You'll be notified when we respond

*"Rejoice with those who rejoice, weep with those who weep."* - Romans 12:15

---
*This is an automated response. Every message is read personally.*"""
    }

    return responses.get(category, responses['general'])

def post_comment(issue_number, comment_body):
    """Post a comment/reply to a GitHub Issue"""
    url = f'https://api.github.com/repos/{REPO}/issues/{issue_number}/comments'
    data = {'body': comment_body}

    try:
        response = requests.post(url, headers=get_github_headers(), json=data)
        response.raise_for_status()
        print(f"Posted comment to issue #{issue_number}")
        return True
    except Exception as e:
        print(f"Error posting comment: {e}")
        return False

def add_label(issue_number, label):
    """Add a label to an issue"""
    url = f'https://api.github.com/repos/{REPO}/issues/{issue_number}/labels'
    data = [label]

    try:
        response = requests.post(url, headers=get_github_headers(), json=data)
        response.raise_for_status()
        print(f"Added label '{label}' to issue #{issue_number}")
        return True
    except Exception as e:
        print(f"Error adding label: {e}")
        return False

def log_suggestion(issue, category):
    """Log suggestions to a tracking file"""
    log_path = os.path.join(os.path.dirname(__file__), 'suggestions_log.json')

    # Load existing log
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log = json.load(f)
    else:
        log = {'suggestions': [], 'prayer_requests': [], 'bugs': []}

    entry = {
        'issue_number': issue.get('number'),
        'title': issue.get('title'),
        'author': issue.get('user', {}).get('login'),
        'category': category,
        'created_at': issue.get('created_at'),
        'logged_at': datetime.utcnow().isoformat()
    }

    if category == 'suggestion':
        log['suggestions'].append(entry)
    elif category == 'prayer':
        log['prayer_requests'].append(entry)
    elif category.startswith('bug'):
        log['bugs'].append(entry)

    # Save log
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)

    print(f"Logged {category} to suggestions_log.json")

def should_respond(issue):
    """Determine if bot should respond to this issue"""
    # Don't respond to issues already closed
    if issue.get('state') == 'closed':
        return False

    # Don't respond to our own issues
    if issue.get('user', {}).get('login') == 'hansen1015':
        return False

    # Don't respond if we already commented
    comments_url = issue.get('comments_url', '')
    if comments_url:
        try:
            response = requests.get(comments_url, headers=get_github_headers())
            comments = response.json()
            # Check if we already responded
            for comment in comments:
                if comment.get('user', {}).get('login') == 'hansen1015':
                    if 'automated response' in comment.get('body', '').lower():
                        return False
        except:
            pass

    return True

def monitor_issues():
    """Main function to monitor and respond to issues"""
    print(f"Starting issues monitoring at {datetime.utcnow()}")

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        return

    # Fetch issues from last 24 hours (adjust as needed)
    issues = fetch_issues(state='open', since_hours=24)

    if not issues:
        print("No new issues found")
        return

    stats = {'responded': 0, 'flagged': 0, 'logged': 0}

    for issue in issues:
        issue_number = issue.get('number')
        issue_title = issue.get('title', '')
        issue_body = issue.get('body', '')

        if not should_respond(issue):
            print(f"Skipping issue #{issue_number} (already responded)")
            continue

        # Categorize
        category = categorize_issue(issue_title, issue_body)
        print(f"Issue #{issue_number}: {issue_title[:40]}... -> {category}")

        # Generate and post response
        response = generate_response(category, issue_title, issue_body)
        if post_comment(issue_number, response):
            stats['responded'] += 1

        # Add appropriate label
        label_map = {
            'prayer': 'prayer-request',
            'suggestion': 'enhancement',
            'bug_technical': 'bug',
            'bug_content': 'content-review',
            'question': 'question',
            'collaboration': 'collaboration',
            'critical': 'urgent',
            'general': 'general'
        }
        add_label(issue_number, label_map.get(category, 'general'))

        # Log suggestions and prayer requests
        if category in ['suggestion', 'prayer', 'bug_technical', 'bug_content']:
            log_suggestion(issue, category)
            stats['logged'] += 1

        # Flag critical issues (already labeled as urgent)
        if category == 'critical':
            stats['flagged'] += 1
            print(f"⚠️ CRITICAL: Issue #{issue_number} flagged for immediate review")

        # Rate limiting delay
        time.sleep(2)

    print(f"
Monitoring complete. Responded: {stats['responded']}, Logged: {stats['logged']}, Flagged: {stats['flagged']}")
    return stats

if __name__ == '__main__':
    monitor_issues()
