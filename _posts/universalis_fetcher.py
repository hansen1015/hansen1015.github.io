#!/usr/bin/env python3
"""
Universalis Liturgical Data Fetcher
Fetches accurate liturgical calendar data from Universalis.com
Used by the Daily Catholic Reflection scheduled bot
"""

import xml.etree.ElementTree as ET
import requests
from datetime import datetime
import json

def fetch_universalis_liturgical_data(date=None):
    """
    Fetch liturgical data from Universalis.com atom feed
    Returns liturgical day, saint, and other info for the given date

    Source: https://universalis.com/atom3day.xml
    """
    if date is None:
        date = datetime.now()

    # Universalis 3-day atom feed
    url = "https://universalis.com/atom3day.xml"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        # Define namespaces
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }

        # Format date for matching
        target_date = date.strftime("%d %B").lower()
        target_id = date.strftime("%Y%m%d")

        for entry in root.findall('atom:entry', ns):
            title_elem = entry.find('atom:title', ns)
            id_elem = entry.find('atom:id', ns)
            summary_elem = entry.find('atom:summary', ns)

            if title_elem is not None and id_elem is not None:
                title = title_elem.text
                entry_id = id_elem.text
                summary = summary_elem.text if summary_elem is not None else ""

                # Match by date in ID (e.g., https://universalis.com/20260301/)
                if target_id in entry_id:
                    # Extract liturgical day from summary
                    liturgical_day = summary.strip() if summary else title

                    # Extract saint info from content
                    content_elem = entry.find('atom:content', ns)
                    saint_name = ""
                    saint_info = ""

                    if content_elem is not None:
                        # Find dt/dd elements for saint info
                        dt_elem = content_elem.find('.//xhtml:dt', ns)
                        dd_elem = content_elem.find('.//xhtml:dd', ns)
                        if dt_elem is not None:
                            saint_name = dt_elem.text or ""
                        if dd_elem is not None:
                            # Get first paragraph only
                            saint_info = dd_elem.text or "" if dd_elem.text else ""

                    return {
                        "date": date.strftime("%Y-%m-%d"),
                        "title": title,
                        "liturgical_day": liturgical_day,
                        "saint_name": saint_name.replace("(", "").replace(")", "").strip(),
                        "saint_info": saint_info[:200] + "..." if len(saint_info) > 200 else saint_info,
                        "universalis_url": f"https://universalis.com/{target_id}/mass.htm",
                        "source": "Universalis.com"
                    }

        return {"error": "Date not found in feed"}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Test with today's date
    today = datetime.now()
    result = fetch_universalis_liturgical_data(today)
    print(json.dumps(result, indent=2))
