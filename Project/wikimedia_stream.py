import json
import csv
from datetime import datetime

import requests  # install if needed: pip install requests

# Tracked entities (can be adapted as needed)
ENTITIES = [
    "Bob vs. Society",
    "Lucio Anneo Seneca",
    "Our First Day",
    "Comedy film",
    "Drama film",
]

TARGET_WIKI = "enwiki"  # English Wikipedia

EVENTS_URL = "https://stream.wikimedia.org/v2/stream/recentchange"

EVENTS_FILE = "data/wiki_events.csv"
ALERTS_FILE = "data/wiki_alerts.csv"

# Alert parameters
TARGET_USER = "ExampleUser"  # target user for alerts (example)
SIZE_THRESHOLD = 5000        # alert if |Δsize| >= 5000 bytes


def init_csv_files():
    """Create / reset the output CSV files with headers."""
    event_headers = [
        "timestamp",
        "wiki",
        "title",
        "entity_match",
        "user",
        "type",
        "comment",
        "old_len",
        "new_len",
        "size_diff",
    ]
    alert_headers = [
        "timestamp",
        "wiki",
        "title",
        "entity_match",
        "user",
        "type",
        "comment",
        "reason",
        "old_len",
        "new_len",
        "size_diff",
    ]

    # Events file
    with open(EVENTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(event_headers)

    # Alerts file
    with open(ALERTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(alert_headers)


def match_entity(title):
    """Return the name of the tracked entity matching this title, or None."""
    if not title:
        return None
    for ent in ENTITIES:
        if title.lower() == ent.lower():
            return ent
    return None


def stream_events():
    """Read the Wikimedia stream and log events related to our entities."""
    session = requests.Session()
    with session.get(EVENTS_URL, stream=True) as resp:
        print("Connected to the Wikimedia stream…")
        for line in resp.iter_lines():
            if not line:
                continue

            # Useful messages start with "data: "
            if not line.startswith(b"data: "):
                continue

            try:
                data = json.loads(line[6:])
            except json.JSONDecodeError:
                continue

            # Filter by wiki
            if data.get("wiki") != TARGET_WIKI:
                continue

            title = data.get("title")
            entity_match = match_entity(title)
            if not entity_match:
                continue  # not one of the 5 tracked entities

            # Main fields
            ts = data.get("timestamp")
            ts_str = datetime.utcfromtimestamp(ts).isoformat() if ts else ""

            user = data.get("user")
            rc_type = data.get("type")  # edit, new, log, etc.
            comment = data.get("comment", "")

            old_len = data.get("old_len") or 0
            new_len = data.get("length") or 0
            size_diff = new_len - old_len

            # Write to events file
            with open(EVENTS_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    ts_str,
                    data.get("wiki"),
                    title,
                    entity_match,
                    user,
                    rc_type,
                    comment,
                    old_len,
                    new_len,
                    size_diff,
                ])

            # Alerts handling
            alerts = []

            if user == TARGET_USER:
                alerts.append(f"Edit by target user {TARGET_USER}")

            if abs(size_diff) >= SIZE_THRESHOLD:
                alerts.append(
                    f"Large edit (|Δ| >= {SIZE_THRESHOLD} bytes)"
                )

            # If there is at least one alert, also write to ALERTS_FILE
            if alerts:
                reason = " ; ".join(alerts)
                with open(ALERTS_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        ts_str,
                        data.get("wiki"),
                        title,
                        entity_match,
                        user,
                        rc_type,
                        comment,
                        reason,
                        old_len,
                        new_len,
                        size_diff,
                    ])

                print(f"[ALERT] {ts_str} — {title} — {reason}")


if __name__ == "__main__":
    init_csv_files()
    try:
        stream_events()
    except KeyboardInterrupt:
        print("Streaming stopped by user.")
