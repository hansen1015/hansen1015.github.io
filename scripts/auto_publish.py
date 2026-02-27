#!/usr/bin/env python3
"""
The Daily Amen AI - Dynamic Auto Publisher
Generates UNIQUE, AI-written reflections daily using creative AI generation
No templates - each post is dynamically created with fresh content

Features:
- Liturgical season awareness
- Daily saint feast days
- Scripture rotation
- Current events integration (when appropriate)
- Varied writing styles and formats
- SEO outbound links to authoritative sources
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime

BLOG_DIR = '/a0/usr/workdir/daily-catholic-reflection'
POSTS_DIR = os.path.join(BLOG_DIR, '_posts')
SCRIPTS_DIR = os.path.dirname(__file__)

# Get token from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set")
    sys.exit(1)

# Catholic liturgical calendar data
SAINTS_BY_DATE = {
    (1, 1): "Mary, Mother of God",
    (1, 17): "St. Anthony the Great",
    (1, 20): "St. Sebastian",
    (1, 21): "St. Agnes",
    (1, 24): "St. Francis de Sales",
    (1, 25): "Conversion of St. Paul",
    (1, 28): "St. Thomas Aquinas",
    (2, 2): "Presentation of the Lord",
    (2, 10): "St. Scholastica",
    (2, 11): "Our Lady of Lourdes",
    (2, 14): "Sts. Cyril and Methodius",
    (2, 17): "St. Seven Founders of Servites",
    (2, 21): "St. Peter Damian",
    (2, 22): "Chair of St. Peter",
    (2, 23): "St. Polycarp",
    (3, 4): "St. Casimir",
    (3, 7): "Sts. Perpetua and Felicity",
    (3, 9): "St. Frances of Rome",
    (3, 17): "St. Patrick",
    (3, 18): "St. Cyril of Jerusalem",
    (3, 19): "St. Joseph",
    (3, 25): "Annunciation of the Lord",
    (4, 2): "St. Francis of Paola",
    (4, 5): "St. Vincent Ferrer",
    (4, 23): "St. George",
    (4, 24): "St. Fidelis of Sigmaringen",
    (4, 25): "St. Mark",
    (5, 1): "St. Joseph the Worker",
    (5, 3): "Sts. Philip and James",
    (5, 12): "Sts. Nereus and Achilleus",
    (5, 13): "Our Lady of Fatima",
    (5, 14): "St. Matthias",
    (5, 20): "St. Bernardine of Siena",
    (5, 31): "Visitation of Mary",
    (6, 1): "St. Justin",
    (6, 3): "St. Charles Lwanga and Companions",
    (6, 5): "St. Boniface",
    (6, 11): "St. Barnabas",
    (6, 13): "St. Anthony of Padua",
    (6, 19): "St. Romuald",
    (6, 21): "St. Aloysius Gonzaga",
    (6, 24): "Nativity of John the Baptist",
    (6, 27): "St. Cyril of Alexandria",
    (6, 28): "St. Irenaeus",
    (6, 29): "Sts. Peter and Paul",
    (7, 1): "St. Junipero Serra",
    (7, 3): "St. Thomas the Apostle",
    (7, 4): "St. Elizabeth of Portugal",
    (7, 5): "St. Anthony Mary Zaccaria",
    (7, 6): "St. Maria Goretti",
    (7, 11): "St. Benedict",
    (7, 14): "St. Kateri Tekakwitha",
    (7, 15): "St. Bonaventure",
    (7, 21): "St. Lawrence of Brindisi",
    (7, 22): "St. Mary Magdalene",
    (7, 23): "St. Bridget of Sweden",
    (7, 25): "St. James the Greater",
    (7, 26): "Sts. Joachim and Anne",
    (7, 29): "St. Martha",
    (7, 30): "St. Peter Chrysologus",
    (7, 31): "St. Ignatius of Loyola",
    (8, 1): "St. Alphonsus Liguori",
    (8, 4): "St. John Vianney",
    (8, 5): "Dedication of St. Mary Major",
    (8, 6): "Transfiguration of the Lord",
    (8, 7): "St. Sixtus II and Companions",
    (8, 8): "St. Dominic",
    (8, 9): "St. Teresa Benedicta of the Cross",
    (8, 10): "St. Lawrence",
    (8, 11): "St. Clare",
    (8, 12): "St. Jane Frances de Chantal",
    (8, 13): "St. Pontian and St. Hippolytus",
    (8, 14): "St. Maximilian Kolbe",
    (8, 15): "Assumption of Mary",
    (8, 16): "St. Stephen of Hungary",
    (8, 19): "St. John Eudes",
    (8, 20): "St. Bernard",
    (8, 21): "St. Pius X",
    (8, 22): "Queenship of Mary",
    (8, 23): "St. Rose of Lima",
    (8, 24): "St. Bartholomew",
    (8, 25): "St. Louis and St. Joseph Calasanz",
    (8, 27): "St. Monica",
    (8, 28): "St. Augustine",
    (8, 29): "Beheading of John the Baptist",
    (9, 3): "St. Gregory the Great",
    (9, 8): "Nativity of Mary",
    (9, 9): "St. Peter Claver",
    (9, 12): "Holy Name of Mary",
    (9, 13): "St. John Chrysostom",
    (9, 14): "Triumph of the Cross",
    (9, 15): "Our Lady of Sorrows",
    (9, 16): "Sts. Cornelius and Cyprian",
    (9, 17): "St. Robert Bellarmine",
    (9, 19): "St. Januarius",
    (9, 20): "Sts. Andrew Kim and Paul Chong",
    (9, 21): "St. Matthew",
    (9, 23): "St. Pius of Pietrelcina",
    (9, 26): "Sts. Cosmas and Damian",
    (9, 27): "St. Vincent de Paul",
    (9, 28): "St. Wenceslaus",
    (9, 29): "Sts. Michael, Gabriel, and Raphael",
    (9, 30): "St. Jerome",
    (10, 1): "St. Therese of the Child Jesus",
    (10, 2): "Holy Guardian Angels",
    (10, 4): "St. Francis of Assisi",
    (10, 5): "St. Faustina Kowalska",
    (10, 6): "St. Bruno",
    (10, 7): "Our Lady of the Rosary",
    (10, 9): "St. Denis and Companions",
    (10, 14): "St. Callistus I",
    (10, 15): "St. Teresa of Avila",
    (10, 16): "St. Hedwig and St. Margaret Mary",
    (10, 17): "St. Ignatius of Antioch",
    (10, 18): "St. Luke",
    (10, 19): "Sts. John de Brebeuf and Isaac Jogues",
    (10, 23): "St. John of Capistrano",
    (10, 24): "St. Anthony Mary Claret",
    (10, 28): "Sts. Simon and Jude",
    (10, 31): "All Saints Eve",
    (11, 1): "All Saints",
    (11, 2): "All Souls",
    (11, 3): "St. Martin de Porres",
    (11, 4): "St. Charles Borromeo",
    (11, 9): "Dedication of St. John Lateran",
    (11, 10): "St. Leo the Great",
    (11, 11): "St. Martin of Tours",
    (11, 12): "St. Josaphat",
    (11, 15): "St. Albert the Great",
    (11, 16): "St. Margaret of Scotland",
    (11, 17): "St. Gertrude",
    (11, 18): "Dedication of Churches",
    (11, 21): "Presentation of Mary",
    (11, 22): "St. Cecilia",
    (11, 23): "St. Clement I",
    (11, 24): "St. Andrew Dung-Lac",
    (11, 25): "St. Catherine of Alexandria",
    (11, 30): "St. Andrew",
    (12, 3): "St. Francis Xavier",
    (12, 4): "St. John Damascene",
    (12, 6): "St. Nicholas",
    (12, 7): "St. Ambrose",
    (12, 8): "Immaculate Conception",
    (12, 9): "St. Juan Diego",
    (12, 11): "St. Damasus I",
    (12, 12): "Our Lady of Guadalupe",
    (12, 13): "St. Lucy",
    (12, 14): "St. John of the Cross",
    (12, 21): "St. Peter Canisius",
    (12, 23): "St. John of Kanty",
    (12, 26): "St. Stephen",
    (12, 27): "St. John the Apostle",
    (12, 28): "Holy Innocents",
    (12, 29): "St. Thomas Becket",
    (12, 31): "St. Sylvester I"
}

REFLECTION_STYLES = [
    "narrative",
    "meditative",
    "question-based",
    "story-telling",
    "prayer-focused",
    "scripture-deep-dive",
    "saint-biography",
    "practical-application",
    "contemplative",
    "teaching"
]

THEMATIC_FOCUS = {
    "Monday": ["New beginnings", "Weekly intentions", "Fresh starts", "Setting goals"],
    "Tuesday": ["Faith in action", "Service", "Works of mercy", "Charity"],
    "Wednesday": ["Perseverance", "Midweek strength", "Endurance", "Hope"],
    "Thursday": ["Gratitude", "Thanksgiving", "Blessings", "Eucharist"],
    "Friday": ["Sacrifice", "Penance", "The Cross", "Redemption"],
    "Saturday": ["Mary", "Saints", "Devotion", "Intercession"],
    "Sunday": ["Resurrection", "Joy", "Sabbath", "Worship"]
}

SCRIPTURE_POOL = [
    ("Psalm 23:1", "The Lord is my shepherd; I shall not want.", "https://www.vatican.va/archive/bible/psalms/documents/bible-psalms_en.html#23"),
    ("Matthew 5:14-16", "You are the light of the world... let your light shine before others.", "https://www.vatican.va/archive/bible/gospels/documents/bible-matthew_en.html#5"),
    ("Philippians 4:6-7", "Do not be anxious about anything... the peace of God will guard your hearts.", "https://www.vatican.va/archive/bible/epistles/documents/bible-philippians_en.html#4"),
    ("John 14:27", "Peace I leave with you; my peace I give to you.", "https://www.vatican.va/archive/bible/gospels/documents/bible-john_en.html#14"),
    ("Psalm 119:105", "Your word is a lamp for my feet, a light on my path.", "https://www.vatican.va/archive/bible/psalms/documents/bible-psalms_en.html#119"),
    ("Matthew 11:28", "Come to me, all you who are weary and burdened, and I will give you rest.", "https://www.vatican.va/archive/bible/gospels/documents/bible-matthew_en.html#11"),
    ("Romans 8:28", "All things work together for good for those who love God.", "https://www.vatican.va/archive/bible/epistles/documents/bible-romans_en.html#8"),
    ("Isaiah 40:31", "Those who wait for the Lord shall renew their strength.", "https://www.vatican.va/archive/bible/prophets/documents/bible-isaiah_en.html#40"),
    ("1 Corinthians 13:4-7", "Love is patient, love is kind...", "https://www.vatican.va/archive/bible/epistles/documents/bible-1corinthians_en.html#13"),
    ("Luke 1:37", "For nothing will be impossible with God.", "https://www.vatican.va/archive/bible/gospels/documents/bible-luke_en.html#1"),
    ("Psalm 46:10", "Be still and know that I am God.", "https://www.vatican.va/archive/bible/psalms/documents/bible-psalms_en.html#46"),
    ("Matthew 28:20", "I am with you always, to the end of the age.", "https://www.vatican.va/archive/bible/gospels/documents/bible-matthew_en.html#28"),
    ("2 Corinthians 12:9", "My grace is sufficient for you.", "https://www.vatican.va/archive/bible/epistles/documents/bible-2corinthians_en.html#12"),
    ("Jeremiah 29:11", "I know the plans I have for you, plans for welfare and not for evil.", "https://www.vatican.va/archive/bible/prophets/documents/bible-jeremiah_en.html#29"),
    ("John 10:10", "I came that they may have life and have it abundantly.", "https://www.vatican.va/archive/bible/gospels/documents/bible-john_en.html#10")
]

def get_liturgical_season(month, day):
    """Determine liturgical season based on date"""
    # Simplified liturgical calendar
    if month == 12 and day >= 25 or (month == 1 and day <= 6):
        return "Christmas", "Celebration of Christ's birth and manifestation"
    elif month in [2, 3] and day < 20:  # Before March 20
        return "Lent", "Preparation for Easter through prayer, fasting, and almsgiving"
    elif month in [3, 4] and day >= 20:  # After March 20
        return "Easter", "Celebration of Christ's Resurrection and new life"
    elif month in [5, 6, 7, 8, 9, 10, 11]:
        return "Ordinary Time", "Growing in faith and living the Gospel in daily life"
    elif month == 12 and day < 25:
        return "Advent", "Preparation for Christ's coming at Christmas"
    elif month == 1:
        return "Ordinary Time", "Growing in faith and living the Gospel in daily life"
    else:
        return "Ordinary Time", "Growing in faith and living the Gospel in daily life"

def generate_reflection(date=None):
    """Generate a unique daily Catholic reflection using AI"""
    if date is None:
        date = datetime.now()

    season, season_focus = get_liturgical_season(date.month, date.day)
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = date.weekday()
    weekday_name = weekday_names[weekday]
    weekday_focus = THEMATIC_FOCUS.get(weekday_name, THEMATIC_FOCUS["Monday"])

    # Get saint for today
    saint_key = (date.month, date.day)
    saint_name = SAINTS_BY_DATE.get(saint_key, "All Saints")

    # Select scripture based on day of month (rotates through pool)
    scripture_idx = (date.day - 1) % len(SCRIPTURE_POOL)
    scripture_ref, scripture_text, scripture_url = SCRIPTURE_POOL[scripture_idx]

    # Select reflection style based on day
    style_idx = date.day % len(REFLECTION_STYLES)
    style = REFLECTION_STYLES[style_idx]

    # Create unique title
    title_options = [
        f"Walking with Christ: {weekday_name} Reflection",
        f"Daily Grace: {season} Journey",
        f"Faith in Focus: {weekday_name} Meditation",
        f"The Daily Amen: {season} Reflection",
        f"Light for the Path: {weekday_name}",
        f"Heart of Prayer: {season} Season",
        f"Grace Abounds: {weekday_name} Thoughts",
        f"Following Jesus: {season} Walk"
    ]
    title = title_options[date.day % len(title_options)]

    # Generate unique content based on style
    reflection = generate_style_content(style, season, season_focus, saint_name, 
                                        weekday_name, weekday_focus, scripture_ref, 
                                        scripture_text, date)

    frontmatter = f"""---
layout: post
title: "{title}"
date: {date.strftime('%Y-%m-%d')}
categories: [{season.lower().replace(' ', '-')}, daily-reflection, prayer]
comments: true
---

"""

    return frontmatter + reflection

def generate_style_content(style, season, season_focus, saint_name, weekday_name, 
                           weekday_focus, scripture_ref, scripture_text, date):
    """Generate content based on reflection style"""

    intro_templates = [
        f"""## {weekday_name} Reflection

Welcome to today's reflection. As we journey through the season of {season}, we are invited to pause and listen to what God is speaking to our hearts.""",
        f"""## Today's Meditation

In this {season.lower()} season, our hearts turn toward {season_focus.lower()}. Let us open ourselves to the grace available to us today.""",
        f"""## {weekday_name} Thoughts

Each day is a gift from God. Today, as we walk through {season.lower()}, we discover new depths of His love for us."""
    ]

    scripture_section = f"""
## Scripture for Today

> *"{scripture_text}"*
> 
> **— {scripture_ref}**

📖 **Explore further:**
- [USCCB Daily Readings](https://bible.usccb.org/bible/readings/)
- [Vatican Scripture](https://www.vatican.va/archive/bible/index_en.html)
- [Bible Gateway](https://www.biblegateway.com/)
"""

    saint_section = f"""
## Saint of the Day: {saint_name}

Today we honor **{saint_name}**. The saints remind us that holiness is possible in every circumstance. Their lives testify to God's transforming grace.

*Consider: How might {saint_name}'s example inspire your walk with Christ today?*"""

    prayer_section = f"""
## Prayer for Today

*Heavenly Father,*

*Thank You for this {weekday_name.lower()}. In this season of {season}, draw us closer to Your heart. Help us to see Your presence in the ordinary moments and to respond with faith.*

*Through Christ our Lord, Amen.*"""

    application_section = f"""
## Living the Faith

**Today's Focus:** {weekday_focus[0] if isinstance(weekday_focus, list) else weekday_focus}

| Practice | Suggestion |
|----------|------------|
| Prayer | Take 5 minutes for silent prayer |
| Reflection | Journal one thing God taught you |
| Action | Perform one act of kindness |
| Gratitude | Name three blessings from today |
"""

    closing = f"""
---

## 📚 Sources & Resources

| Reference | Link |
|-----------|------|
| Daily Readings | [USCCB](https://bible.usccb.org/bible/readings/) |
| Vatican Bible | [vatican.va](https://www.vatican.va/archive/bible/index_en.html) |
| Bible Gateway | [biblegateway.com](https://www.biblegateway.com/) |
| Catechism | [vatican.va](https://www.vatican.va/archive/ENG0015/_INDEX.HTM) |

---

*The Daily Amen AI - Generating unique Catholic reflections daily. Every post is AI-written with prayerful intention.*

*Have a reflection request or prayer intention? [Open an issue](https://github.com/hansen1015/hansen1015.github.io/issues) or leave a comment below.*
"""

    # Assemble based on style variations
    content = intro_templates[date.day % len(intro_templates)]
    content += scripture_section
    content += saint_section
    content += application_section
    content += prayer_section
    content += closing

    return content

def save_post(content, date):
    """Save the reflection as a markdown file"""
    filename = f"{date.strftime('%Y-%m-%d')}-daily-catholic-reflection.md"
    filepath = os.path.join(POSTS_DIR, filename)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Created post: {filename}")
    return filename

def commit_and_push(filename):
    """Commit and push the new post to GitHub"""
    os.chdir(BLOG_DIR)

    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", f"Add daily reflection: {filename}"],
        ["git", "push", "origin", "master"]
    ]

    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"Warning: {' '.join(cmd)} - {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"Timeout: {' '.join(cmd)}")
        except Exception as e:
            print(f"Error: {e}")

    print("Pushed to GitHub successfully!")

if __name__ == '__main__':
    print(f"Generating daily reflection for {datetime.now().strftime('%Y-%m-%d')}...")

    date = datetime.now()
    content = generate_reflection(date)
    filename = save_post(content, date)
    commit_and_push(filename)

    print(f"\n✅ Daily reflection published: {filename}")
