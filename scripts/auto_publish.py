#!/usr/bin/env python3
"""
Daily Catholic Reflection - Auto Publisher
Generates reflection, commits, and pushes to GitHub automatically
Uses GITHUB_TOKEN environment variable for authentication
"""

import os
import sys
import subprocess
from datetime import datetime

BLOG_DIR = '/a0/usr/workdir/daily-catholic-reflection'
POSTS_DIR = os.path.join(BLOG_DIR, '_posts')

# Get token from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set")
    sys.exit(1)

def generate_reflection(date=None):
    """Generate a daily Catholic reflection"""
    if date is None:
        date = datetime.now()

    month = date.month
    if month in [2, 3]:
        season = 'Lent'
        season_focus = 'Preparation for Easter through prayer, fasting, and almsgiving'
        themes = ['prayer', 'fasting', 'almsgiving', 'repentance', 'conversion']
    elif month in [4, 5]:
        season = 'Easter'
        season_focus = 'Celebration of Christ Resurrection and new life'
        themes = ['resurrection', 'joy', 'new life', 'hope', 'victory']
    elif month in [11, 12]:
        season = 'Advent'
        season_focus = 'Preparation for Christ coming at Christmas'
        themes = ['waiting', 'hope', 'preparation', 'coming', 'light']
    else:
        season = 'Ordinary Time'
        season_focus = 'Growing in faith and living the Gospel in daily life'
        themes = ['discipleship', 'faith', 'charity', 'service', 'kingdom']

    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday = date.weekday()
    weekday_name = weekday_names[weekday]

    weekday_themes = {
        0: 'New Beginnings and Weekly Intentions',
        1: 'Faith in Action',
        2: 'Midweek Reflection and Perseverance',
        3: 'Gratitude and Thanksgiving',
        4: 'Penance, Sacrifice, and the Cross',
        5: 'Mary, the Saints, and Devotion',
        6: 'Resurrection Joy and Sabbath Rest'
    }
    weekday_theme = weekday_themes.get(weekday, 'Daily Grace')

    reflection = f"""---
layout: post
title: "Daily Catholic Reflection - {date.strftime('%B %d, %Y')}"
date: {date.strftime('%Y-%m-%d')}
categories: [{season.lower().replace(' ', '-')}, daily-reflection, prayer]
comments: true
---

## {weekday_name}: {weekday_theme}

*"Your word is a lamp for my feet, a light on my path."* - **Psalm 119:105**

---

## Season of {season}

{season_focus}.

Today we reflect on the themes of **{', '.join(themes[:3])}** as we journey together in faith.

---

## Morning Reflection

As we begin this day, let us pause and invite the Lord into our hearts.

**Questions for Today:**

1. **Where is God calling me to grow today?**
2. **What distractions need to be surrendered?**
3. **How can I serve others as Christ served us?**

---

## Scripture Focus

> *"Create in me a clean heart, O God, and renew a right spirit within me."*  
> **— Psalm 51:10**

---

## Practical Application

| Area | Today's Focus |
|------|---------------|
| **Prayer** | Spend 5 minutes in silent prayer |
| **Fasting** | Identify one distraction to surrender |
| **Almsgiving** | Perform one act of kindness |
| **Reflection** | Return tomorrow for continued growth |

---

## Prayer for Today

*Heavenly Father,*

*Thank You for this new day. In this season of {season}, help me to embrace prayer, fasting, and almsgiving with an open heart.*

*Through Christ our Lord, Amen.*

---

*This reflection was generated with AI assistance. Published daily at 6:00 AM SGT (Singapore Time). Readers from around the world are welcome to join in prayer and reflection. Always discern in prayer and light of Church tradition.*

*"Test everything; hold fast to what is good." - 1 Thessalonians 5:21*
"""
    return reflection

def create_and_publish_post():
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f'{date_str}-daily-catholic-reflection.md'
    filepath = os.path.join(POSTS_DIR, filename)

    if os.path.exists(filepath):
        print(f"Post already exists: {filename}")
    else:
        reflection = generate_reflection(today)
        with open(filepath, 'w') as f:
            f.write(reflection)
        print(f"Created post: {filename}")

    os.chdir(BLOG_DIR)

    try:
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        result = subprocess.run(['git', 'status', '--porcelain'], check=True, capture_output=True, text=True)

        if result.stdout.strip():
            subprocess.run(['git', 'commit', '-m', f'Auto-post: Daily reflection for {date_str}'], check=True, capture_output=True)
            print(f"Committed changes")
        else:
            print("No changes to commit")

        subprocess.run(['git', 'push', 'origin', 'master'], check=True, capture_output=True)
        print(f"Pushed to GitHub")
        print(f"Daily reflection published!")

    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        return False

    return True

if __name__ == '__main__':
    success = create_and_publish_post()
    sys.exit(0 if success else 1)
